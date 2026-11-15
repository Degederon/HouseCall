"""HouseCall: one place for every alert in the house."""

from __future__ import annotations

from pathlib import Path

import voluptuous as vol

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import CARD_FILENAME, CARD_URL, DOMAIN, PRIORITIES, PRIORITY_NORMAL, TEST_ALL, TEST_APP, TEST_MESSAGING, VERSION
from .hub import HouseCall

PLATFORMS = [Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SEND_SCHEMA = vol.Schema(
    {
        vol.Required("message"): cv.string,
        vol.Optional("title"): cv.string,
        vol.Optional("to"): vol.Any(cv.string, [cv.string]),
        vol.Optional("priority", default=PRIORITY_NORMAL): vol.In(PRIORITIES),
    }
)
TEST_SCHEMA = vol.Schema(
    {
        vol.Required("to"): cv.string,
        vol.Optional("how", default=TEST_ALL): vol.In([TEST_ALL, TEST_APP, TEST_MESSAGING]),
    }
)
ACK_SCHEMA = vol.Schema({vol.Required("id"): cv.string, vol.Optional("by"): cv.string})


async def _register_frontend(hass: HomeAssistant) -> None:
    """Serve the dashboard card and load it on every dashboard automatically."""
    flag = f"{DOMAIN}_frontend"
    if hass.data.get(flag):
        return
    path = Path(__file__).parent / "frontend" / CARD_FILENAME
    await hass.http.async_register_static_paths([StaticPathConfig(CARD_URL, str(path), False)])
    add_extra_js_url(hass, f"{CARD_URL}?v={VERSION}")
    hass.data[flag] = True


def _hub(hass: HomeAssistant) -> HouseCall:
    hub = hass.data.get(DOMAIN)
    if hub is None:
        raise HomeAssistantError("HouseCall is not set up")
    return hub


def _register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, "send"):
        return

    async def send(call: ServiceCall) -> ServiceResponse:
        item = await _hub(hass).async_send(
            call.data["message"],
            call.data.get("title"),
            call.data.get("to"),
            call.data.get("priority", PRIORITY_NORMAL),
        )
        return {"id": item["id"], "status": item["status"], "to": item["to_label"]}

    async def acknowledge(call: ServiceCall) -> None:
        await _hub(hass).async_acknowledge(call.data["id"], call.data.get("by"))

    async def clear_history(call: ServiceCall) -> None:
        await _hub(hass).async_clear()

    async def send_test(call: ServiceCall) -> ServiceResponse:
        hub = _hub(hass)
        pid = hub.resolve_one(call.data["to"])
        if pid is None:
            raise HomeAssistantError(f"Nobody called {call.data['to']} in HouseCall")
        results = await hub.async_test(pid, call.data.get("how", TEST_ALL))
        return {"results": results, "all_ok": all(r["ok"] for r in results)}

    hass.services.async_register(
        DOMAIN, "send", send, schema=SEND_SCHEMA, supports_response=SupportsResponse.OPTIONAL
    )
    hass.services.async_register(DOMAIN, "acknowledge", acknowledge, schema=ACK_SCHEMA)
    hass.services.async_register(DOMAIN, "clear_history", clear_history)
    hass.services.async_register(
        DOMAIN, "send_test", send_test, schema=TEST_SCHEMA, supports_response=SupportsResponse.OPTIONAL
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hub = HouseCall(hass, entry)
    await hub.async_load()
    entry.runtime_data = hub
    hass.data[DOMAIN] = hub

    await _register_frontend(hass)
    _register_services(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        await entry.runtime_data.async_stop()
        hass.data.pop(DOMAIN, None)
        for svc in ("send", "acknowledge", "clear_history", "send_test"):
            hass.services.async_remove(DOMAIN, svc)
    return ok
