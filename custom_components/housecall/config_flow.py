"""Setup and options screens for HouseCall (no YAML needed)."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.util import slugify
from homeassistant.helpers.selector import (
    BooleanSelector,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TimeSelector,
)

from .const import (
    CONF_BOARD_SERVICE,
    CONF_CHANNEL_MODE,
    CONF_CHANNELS,
    CONF_CUSTOM_PEOPLE,
    CONF_GLASS_BOARD,
    CONF_MAX_REPEATS,
    CONF_OPEN_DASHBOARD,
    CONF_MEMBERS,
    CONF_PEOPLE,
    CONF_QUIET_END,
    CONF_QUIET_START,
    CONF_REPEAT_MINUTES,
    CONF_SPEAKERS,
    CONF_TTS,
    CUSTOM_PREFIX,
    CHANNEL_MODES,
    DEFAULT_CHANNEL_MODE,
    DEFAULT_MAX_REPEATS,
    DEFAULT_QUIET_END,
    DEFAULT_QUIET_START,
    DEFAULT_REPEAT_MINUTES,
    DOMAIN,
    TEST_ALL,
    TEST_APP,
    TEST_MESSAGING,
)
from .hub import HouseCall, discover_people, list_dashboards, messaging_routes, normalize_path, notify_services


class HouseCallConfigFlow(ConfigFlow, domain=DOMAIN):
    """First-time setup: finds your people and their phones automatically."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        people = discover_people(self.hass)
        if user_input is not None:
            return self.async_create_entry(
                title="HouseCall",
                data={},
                options={
                    CONF_PEOPLE: people,
                    CONF_QUIET_START: DEFAULT_QUIET_START,
                    CONF_QUIET_END: DEFAULT_QUIET_END,
                    CONF_SPEAKERS: [],
                    CONF_REPEAT_MINUTES: DEFAULT_REPEAT_MINUTES,
                    CONF_MAX_REPEATS: DEFAULT_MAX_REPEATS,
                },
            )
        lines = []
        for pid, svcs in people.items():
            state = self.hass.states.get(pid)
            name = state.attributes.get("friendly_name", pid) if state else pid
            lines.append(f"- **{name}**: {', '.join(svcs) if svcs else 'no phone found yet'}")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={"found": "\n".join(lines) or "- No people found"},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> OptionsFlow:
        return HouseCallOptionsFlow()


class HouseCallOptionsFlow(OptionsFlow):
    """Change people, quiet hours and outputs later."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        menu = ["people", "add_person"]
        if self.config_entry.options.get(CONF_CUSTOM_PEOPLE):
            menu.append("edit_person")
        menu += ["messaging", "send_test", "quiet", "outputs"]
        return self.async_show_menu(step_id="init", menu_options=menu)

    # ------------------------------------------------------- shared helpers

    def _hub(self) -> HouseCall | None:
        hub = getattr(self.config_entry, "runtime_data", None)
        return hub if isinstance(hub, HouseCall) else None

    def _people_options(self) -> list[SelectOptionDict]:
        hub = self._hub()
        people = hub.people() if hub else []
        return [SelectOptionDict(value=p["id"], label=p["name"]) for p in people]

    # ------------------------------------------------------- messaging apps

    async def async_step_messaging(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        o = self.config_entry.options
        if user_input is not None:
            mode = user_input.get(CONF_CHANNEL_MODE, DEFAULT_CHANNEL_MODE)
            who = user_input.get("person")
            if who:
                self._pending_mode = mode
                self._editing = who
                return await self.async_step_messaging_person()
            return self._save({CONF_CHANNEL_MODE: mode})
        schema: dict[Any, Any] = {
            vol.Required(CONF_CHANNEL_MODE, default=o.get(CONF_CHANNEL_MODE, DEFAULT_CHANNEL_MODE)): SelectSelector(
                SelectSelectorConfig(options=CHANNEL_MODES, translation_key="channel_mode", mode=SelectSelectorMode.LIST)
            ),
        }
        people = self._people_options()
        if people:
            schema[vol.Optional("person")] = SelectSelector(
                SelectSelectorConfig(options=people, mode=SelectSelectorMode.DROPDOWN)
            )
        found = messaging_routes(self.hass)
        return self.async_show_form(
            step_id="messaging",
            data_schema=vol.Schema(schema),
            description_placeholders={
                "found": "\n".join(f"- {label}" for label in found.values()) or "- None yet. Add Telegram bot, Signal Messenger, ntfy, Pushover or another messaging integration first."
            },
        )

    async def async_step_messaging_person(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        pid = self._editing
        current = (self.config_entry.options.get(CONF_CHANNELS) or {}).get(pid) or {}
        found = messaging_routes(self.hass)
        if user_input is not None:
            self._routes = list(user_input.get("routes") or [])
            # Apps that are notify actions (Signal, Messenger, email...) may need an address.
            self._needs_address = [r for r in self._routes if self.hass.states.get(r) is None]
            if self._needs_address:
                return await self.async_step_messaging_addresses()
            return self._save_channels({})
        options = [SelectOptionDict(value=r, label=l) for r, l in found.items()]
        for r in current.get("routes") or []:
            if r not in found:
                options.append(SelectOptionDict(value=r, label=f"{r} (not found)"))
        return self.async_show_form(
            step_id="messaging_person",
            data_schema=vol.Schema(
                {
                    vol.Optional("routes", default=list(current.get("routes") or [])): SelectSelector(
                        SelectSelectorConfig(options=options, multiple=True, mode=SelectSelectorMode.LIST)
                    ),
                }
            ),
            description_placeholders={"name": self._person_name(pid)},
        )

    async def async_step_messaging_addresses(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        pid = self._editing
        current = (self.config_entry.options.get(CONF_CHANNELS) or {}).get(pid) or {}
        old = dict(current.get("addresses") or {})
        if user_input is not None:
            return self._save_channels({r: (user_input.get(r) or "").strip() for r in self._needs_address})
        schema = {
            vol.Optional(r, description={"suggested_value": old.get(r) or current.get("address", "")}): TextSelector()
            for r in self._needs_address
        }
        return self.async_show_form(
            step_id="messaging_addresses",
            data_schema=vol.Schema(schema),
            description_placeholders={"name": self._person_name(pid)},
        )

    def _person_name(self, pid: str) -> str:
        return next((o["label"] for o in self._people_options() if o["value"] == pid), pid)

    def _save_channels(self, addresses: dict[str, str]) -> ConfigFlowResult:
        pid = self._editing
        channels = dict(self.config_entry.options.get(CONF_CHANNELS) or {})
        addresses = {k: v for k, v in addresses.items() if v}
        if self._routes:
            channels[pid] = {"routes": self._routes, "addresses": addresses}
        else:
            channels.pop(pid, None)
        return self._save(
            {CONF_CHANNELS: channels, CONF_CHANNEL_MODE: getattr(self, "_pending_mode", DEFAULT_CHANNEL_MODE)}
        )

    # ---------------------------------------------------- send a test message

    async def async_step_send_test(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        hub = self._hub()
        people = self._people_options()
        if hub is None or not people:
            return self.async_abort(reason="nobody_to_test")
        if user_input is not None:
            results = await hub.async_test(user_input["person"], user_input.get("how", TEST_ALL))
            lines = []
            for r in results:
                if r["ok"]:
                    lines.append(f"✅ {r['channel']}: sent")
                else:
                    lines.append(f"❌ {r['channel']}: {r['error']}")
            self._test_report = "\n".join(lines)
            return await self.async_step_test_result()
        return self.async_show_form(
            step_id="send_test",
            data_schema=vol.Schema(
                {
                    vol.Required("person", default=people[0]["value"]): SelectSelector(
                        SelectSelectorConfig(options=people, mode=SelectSelectorMode.DROPDOWN)
                    ),
                    vol.Required("how", default=TEST_ALL): SelectSelector(
                        SelectSelectorConfig(options=[TEST_ALL, TEST_APP, TEST_MESSAGING], translation_key="test_how", mode=SelectSelectorMode.LIST)
                    ),
                }
            ),
        )

    async def async_step_test_result(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return await self.async_step_init()
        return self.async_show_form(
            step_id="test_result",
            data_schema=vol.Schema({}),
            description_placeholders={"report": getattr(self, "_test_report", "")},
        )

    # ------------------------------------------------ HouseCall-only people

    def _phone_selector(self) -> SelectSelector:
        options = set(notify_services(self.hass))
        for info in (self.config_entry.options.get(CONF_CUSTOM_PEOPLE) or {}).values():
            options.update(info.get("services") or [])
        return SelectSelector(
            SelectSelectorConfig(options=sorted(options), multiple=True, mode=SelectSelectorMode.DROPDOWN)
        )

    def _person_schema(self, info: dict[str, Any], with_remove: bool) -> vol.Schema:
        schema: dict[Any, Any] = {
            vol.Required("name", default=info.get("name", "")): TextSelector(),
            vol.Optional("services", default=list(info.get("services") or [])): self._phone_selector(),
            vol.Optional("presence", description={"suggested_value": info.get("presence")}): EntitySelector(
                EntitySelectorConfig(domain=["device_tracker", "binary_sensor", "input_boolean"])
            ),
        }
        if with_remove:
            schema[vol.Optional("remove", default=False)] = BooleanSelector()
        return vol.Schema(schema)

    async def async_step_add_person(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            name = (user_input.get("name") or "").strip()
            if not name:
                errors["name"] = "name_required"
            else:
                custom = dict(self.config_entry.options.get(CONF_CUSTOM_PEOPLE) or {})
                base = CUSTOM_PREFIX + (slugify(name) or "person")
                cid, n = base, 2
                while cid in custom:
                    cid, n = f"{base}_{n}", n + 1
                custom[cid] = {
                    "name": name,
                    "services": list(user_input.get("services") or []),
                    "presence": user_input.get("presence"),
                }
                return self._save({CONF_CUSTOM_PEOPLE: custom})
        return self.async_show_form(
            step_id="add_person", data_schema=self._person_schema(user_input or {}, False), errors=errors
        )

    async def async_step_edit_person(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        custom = self.config_entry.options.get(CONF_CUSTOM_PEOPLE) or {}
        if user_input is not None:
            self._editing = user_input["person"]
            return await self.async_step_edit_person_details()
        return self.async_show_form(
            step_id="edit_person",
            data_schema=vol.Schema(
                {
                    vol.Required("person"): SelectSelector(
                        SelectSelectorConfig(
                            options=[SelectOptionDict(value=cid, label=i.get("name", cid)) for cid, i in custom.items()],
                            mode=SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
        )

    async def async_step_edit_person_details(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        custom = dict(self.config_entry.options.get(CONF_CUSTOM_PEOPLE) or {})
        cid = self._editing
        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input.get("remove"):
                custom.pop(cid, None)
                return self._save({CONF_CUSTOM_PEOPLE: custom})
            name = (user_input.get("name") or "").strip()
            if not name:
                errors["name"] = "name_required"
            else:
                custom[cid] = {
                    "name": name,
                    "services": list(user_input.get("services") or []),
                    "presence": user_input.get("presence"),
                }
                return self._save({CONF_CUSTOM_PEOPLE: custom})
        return self.async_show_form(
            step_id="edit_person_details",
            data_schema=self._person_schema(user_input or custom.get(cid, {}), True),
            errors=errors,
            description_placeholders={"name": custom.get(cid, {}).get("name", "")},
        )

    def _save(self, changes: dict[str, Any]) -> ConfigFlowResult:
        return self.async_create_entry(data={**self.config_entry.options, **changes})

    async def async_step_people(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        current: dict[str, list[str]] = dict(self.config_entry.options.get(CONF_PEOPLE) or {})
        found = discover_people(self.hass)
        # Only people that still exist in Home Assistant (Settings -> People).
        person_ids = sorted(found)
        if user_input is not None:
            members = [pid for pid in user_input.get(CONF_MEMBERS, []) if pid in person_ids]
            return self._save({CONF_PEOPLE: {pid: list(user_input.get(pid, [])) for pid in members}})

        def label(pid: str) -> str:
            state = self.hass.states.get(pid)
            return state.attributes.get("friendly_name", pid) if state else pid

        members_default = [pid for pid in person_ids if pid in current] if current else person_ids
        options = set(notify_services(self.hass))
        for svcs in list(current.values()) + list(found.values()):
            options.update(svcs)
        phones = SelectSelector(
            SelectSelectorConfig(options=sorted(options), multiple=True, mode=SelectSelectorMode.DROPDOWN)
        )
        schema: dict[Any, Any] = {
            vol.Optional(CONF_MEMBERS, default=members_default): SelectSelector(
                SelectSelectorConfig(
                    options=[SelectOptionDict(value=pid, label=label(pid)) for pid in person_ids],
                    multiple=True,
                    mode=SelectSelectorMode.LIST,
                )
            )
        }
        for pid in person_ids:
            default = [s for s in current.get(pid, found.get(pid, [])) if s in options]
            schema[vol.Optional(pid, default=default)] = phones
        return self.async_show_form(
            step_id="people",
            data_schema=vol.Schema(schema),
            description_placeholders={
                "names": ", ".join(f"{label(pid)} = {pid}" for pid in person_ids) or "nobody yet"
            },
        )

    async def async_step_quiet(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self._save(user_input)
        o = self.config_entry.options
        return self.async_show_form(
            step_id="quiet",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_QUIET_START, default=o.get(CONF_QUIET_START, DEFAULT_QUIET_START)): TimeSelector(),
                    vol.Required(CONF_QUIET_END, default=o.get(CONF_QUIET_END, DEFAULT_QUIET_END)): TimeSelector(),
                }
            ),
        )

    async def async_step_outputs(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            user_input.setdefault(CONF_SPEAKERS, [])
            user_input.setdefault(CONF_TTS, None)
            user_input.setdefault(CONF_BOARD_SERVICE, "")
            user_input[CONF_OPEN_DASHBOARD] = normalize_path(user_input.get(CONF_OPEN_DASHBOARD))
            user_input[CONF_REPEAT_MINUTES] = int(user_input[CONF_REPEAT_MINUTES])
            user_input[CONF_MAX_REPEATS] = int(user_input[CONF_MAX_REPEATS])
            return self._save(user_input)
        o = self.config_entry.options
        dashboards = ["/lovelace"] + [f"/{p}" for p in list_dashboards(self.hass)]
        hub = getattr(self.config_entry, "runtime_data", None)
        current_open = hub.open_url() if isinstance(hub, HouseCall) else normalize_path(o.get(CONF_OPEN_DASHBOARD))
        return self.async_show_form(
            step_id="outputs",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_OPEN_DASHBOARD, description={"suggested_value": current_open}): SelectSelector(
                        SelectSelectorConfig(options=dashboards, custom_value=True, mode=SelectSelectorMode.DROPDOWN)
                    ),
                    vol.Optional(CONF_SPEAKERS, description={"suggested_value": o.get(CONF_SPEAKERS, [])}): EntitySelector(
                        EntitySelectorConfig(domain="media_player", multiple=True)
                    ),
                    vol.Optional(CONF_TTS, description={"suggested_value": o.get(CONF_TTS)}): EntitySelector(
                        EntitySelectorConfig(domain="tts")
                    ),
                    vol.Required(CONF_GLASS_BOARD, default=o.get(CONF_GLASS_BOARD, True)): BooleanSelector(),
                    vol.Optional(CONF_BOARD_SERVICE, description={"suggested_value": o.get(CONF_BOARD_SERVICE, "")}): TextSelector(),
                    vol.Required(CONF_REPEAT_MINUTES, default=o.get(CONF_REPEAT_MINUTES, DEFAULT_REPEAT_MINUTES)): NumberSelector(
                        NumberSelectorConfig(min=1, max=60, step=1, mode=NumberSelectorMode.BOX, unit_of_measurement="min")
                    ),
                    vol.Required(CONF_MAX_REPEATS, default=o.get(CONF_MAX_REPEATS, DEFAULT_MAX_REPEATS)): NumberSelector(
                        NumberSelectorConfig(min=0, max=20, step=1, mode=NumberSelectorMode.BOX)
                    ),
                }
            ),
        )
