"""The HouseCall engine: routing, quiet hours, escalation, history."""

from __future__ import annotations

from datetime import time, timedelta
import logging
from typing import Any
from uuid import uuid4

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util, slugify

from .const import (
    ACK_PREFIX,
    CONF_BOARD_SERVICE,
    CONF_CUSTOM_PEOPLE,
    CONF_GLASS_BOARD,
    CONF_MAX_REPEATS,
    CONF_OPEN_DASHBOARD,
    CONF_PEOPLE,
    CONF_QUIET_END,
    CONF_QUIET_START,
    CONF_REPEAT_MINUTES,
    CONF_SPEAKERS,
    CONF_TTS,
    DEFAULT_MAX_REPEATS,
    DEFAULT_QUIET_END,
    DEFAULT_QUIET_START,
    DEFAULT_REPEAT_MINUTES,
    EVENT_ACKNOWLEDGED,
    EVENT_UPDATED,
    EVERYONE,
    HISTORY_LIMIT,
    PRIORITY_CRITICAL,
    PRIORITY_INFO,
    PRIORITY_NORMAL,
    SIGNAL_UPDATE,
    STARTER_DASHBOARD,
    STATUS_ACKED,
    STATUS_EXPIRED,
    STATUS_HELD,
    STATUS_SENT,
    STATUS_WAITING,
    STORAGE_KEY,
    STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)


def notify_services(hass: HomeAssistant) -> list[str]:
    """All legacy notify services, e.g. ['mobile_app_my_iphone', 'notify']."""
    return sorted(hass.services.async_services().get("notify", {}).keys())


def list_dashboards(hass: HomeAssistant) -> list[str]:
    """URL paths of the dashboards, e.g. ['dashboard-housecall'] (best effort)."""
    try:
        data = hass.data.get("lovelace")
        dashboards = getattr(data, "dashboards", None)
        if dashboards is None and isinstance(data, dict):
            dashboards = data.get("dashboards")
        return sorted(p for p in (dashboards or {}) if p)
    except Exception:  # noqa: BLE001 - internal structure may change between versions
        return []


def normalize_path(value: str | None) -> str:
    v = (value or "").strip()
    if not v:
        return ""
    if v.startswith("http://") or v.startswith("https://"):
        return v
    return v if v.startswith("/") else "/" + v


def discover_people(hass: HomeAssistant) -> dict[str, list[str]]:
    """Map each person to the phone notify services of their companion apps."""
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    available = set(notify_services(hass))
    people: dict[str, list[str]] = {}
    for state in hass.states.async_all("person"):
        found: list[str] = []
        for tracker in state.attributes.get("device_trackers", []) or []:
            entry = ent_reg.async_get(tracker)
            if not entry or entry.platform != "mobile_app" or not entry.device_id:
                continue
            device = dev_reg.async_get(entry.device_id)
            if not device:
                continue
            for name in (device.name, device.name_by_user):
                if not name:
                    continue
                svc = f"mobile_app_{slugify(name)}"
                if svc in available and svc not in found:
                    found.append(svc)
        people[state.entity_id] = found
    return people


def _parse_time(value: str | None, fallback: str) -> time:
    return dt_util.parse_time(value or fallback) or dt_util.parse_time(fallback)


class HouseCall:
    """Keeps the message history and delivers messages."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.history: list[dict[str, Any]] = []
        self._store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._repeat_unsubs: dict[str, Any] = {}
        self._unsubs: list[Any] = []

    # ------------------------------------------------------------------ setup

    @property
    def opts(self) -> dict[str, Any]:
        return dict(self.entry.options)

    async def async_load(self) -> None:
        data = await self._store.async_load() or {}
        self.history = data.get("history", [])
        # Escalations don't survive a restart; mark old waiting items clearly.
        for item in self.history:
            if item.get("status") == STATUS_WAITING:
                item["status"] = STATUS_EXPIRED
        self._unsubs.append(
            self.hass.bus.async_listen("mobile_app_notification_action", self._on_action)
        )
        self._unsubs.append(
            async_track_time_interval(self.hass, self._tick, timedelta(minutes=1))
        )

    async def async_stop(self) -> None:
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        for unsub in self._repeat_unsubs.values():
            unsub()
        self._repeat_unsubs.clear()
        await self._save()

    # ----------------------------------------------------------------- people

    def people(self) -> list[dict[str, Any]]:
        result = []
        # People from Settings -> People that are ticked in HouseCall.
        for pid, services in (self.opts.get(CONF_PEOPLE) or {}).items():
            state = self.hass.states.get(pid)
            if state is None and self.hass.is_running:
                continue  # deleted from Settings -> People
            name = (
                state.attributes.get("friendly_name")
                if state
                else pid.split(".", 1)[-1].replace("_", " ").title()
            )
            result.append(
                {
                    "id": pid,
                    "name": name,
                    "services": list(services or []),
                    "home": bool(state and state.state == "home"),
                    "user_id": state.attributes.get("user_id") if state else None,
                    "custom": False,
                }
            )
        # People created only in HouseCall.
        for cid, info in (self.opts.get(CONF_CUSTOM_PEOPLE) or {}).items():
            presence = info.get("presence")
            pstate = self.hass.states.get(presence) if presence else None
            result.append(
                {
                    "id": cid,
                    "name": info.get("name") or cid.split(".", 1)[-1].title(),
                    "services": list(info.get("services") or []),
                    "home": (pstate.state in ("home", "on")) if pstate else None,
                    "user_id": None,
                    "custom": True,
                }
            )
        return result

    def _name(self, pid: str) -> str:
        for p in self.people():
            if p["id"] == pid:
                return p["name"]
        return pid

    def _resolve_to(self, to: Any) -> list[str]:
        everyone = [p["id"] for p in self.people()]
        if not to:
            return everyone
        if isinstance(to, str):
            to = [t for t in to.split(",")]
        wanted: list[str] = []
        for raw in to:
            t = str(raw).strip().lower()
            if not t:
                continue
            if t in EVERYONE:
                return everyone
            for p in self.people():
                if t in (p["id"].lower(), p["id"].split(".", 1)[-1].lower(), p["name"].lower()):
                    if p["id"] not in wanted:
                        wanted.append(p["id"])
        if not wanted:
            _LOGGER.warning("HouseCall: nobody matched %s, sending to everyone", to)
            return everyone
        return wanted

    def _to_label(self, pids: list[str]) -> str:
        if pids and len(pids) == len(self.people()) and len(pids) > 1:
            return "Everyone"
        return ", ".join(self._name(p) for p in pids) or "Everyone"

    # ------------------------------------------------------------ quiet hours

    def quiet_window(self) -> tuple[time, time]:
        return (
            _parse_time(self.opts.get(CONF_QUIET_START), DEFAULT_QUIET_START),
            _parse_time(self.opts.get(CONF_QUIET_END), DEFAULT_QUIET_END),
        )

    def in_quiet_hours(self) -> bool:
        start, end = self.quiet_window()
        now = dt_util.now().time()
        if start == end:
            return False
        if start < end:
            return start <= now < end
        return now >= start or now < end

    # ---------------------------------------------------------------- sending

    async def async_send(
        self,
        message: str,
        title: str | None = None,
        to: Any = None,
        priority: str = PRIORITY_NORMAL,
    ) -> dict[str, Any]:
        pids = self._resolve_to(to)
        item: dict[str, Any] = {
            "id": uuid4().hex[:10],
            "message": message,
            "title": title,
            "priority": priority,
            "to": pids,
            "to_label": self._to_label(pids),
            "time": dt_util.now().isoformat(),
            "status": STATUS_SENT,
            "acked_by": None,
            "via": [],
            "repeats": 0,
        }

        if priority == PRIORITY_INFO:
            await self._board(item)
        elif priority == PRIORITY_NORMAL:
            await self._board(item)
            if self.in_quiet_hours():
                item["status"] = STATUS_HELD
            else:
                await self._push(item, critical=False)
        else:
            item["status"] = STATUS_WAITING
            await self._push(item, critical=True)
            await self._speak(item)
            await self._board(item)
            self._schedule_repeat(item["id"])

        self.history.insert(0, item)
        del self.history[HISTORY_LIMIT:]
        await self._changed()
        return item

    def _add_via(self, item: dict[str, Any], what: str) -> None:
        if what not in item["via"]:
            item["via"].append(what)

    async def _call(self, domain: str, service: str, data: dict[str, Any], target: dict | None = None) -> bool:
        try:
            await self.hass.services.async_call(domain, service, data, target=target, blocking=True)
            return True
        except Exception as err:  # noqa: BLE001 - one bad device must not stop the rest
            _LOGGER.warning("HouseCall: %s.%s failed: %s", domain, service, err)
            return False

    def _services_for(self, pids: list[str]) -> list[str]:
        out: list[str] = []
        people = {p["id"]: p for p in self.people()}
        for pid in pids:
            for svc in people.get(pid, {}).get("services", []):
                if svc not in out:
                    out.append(svc)
        return out

    def open_url(self) -> str:
        """Where a tap on the notification takes you."""
        if CONF_OPEN_DASHBOARD in self.opts:
            return normalize_path(self.opts.get(CONF_OPEN_DASHBOARD))
        # Never set: use the starter dashboard if it exists.
        return f"/{STARTER_DASHBOARD}" if STARTER_DASHBOARD in list_dashboards(self.hass) else ""

    async def _push(self, item: dict[str, Any], critical: bool) -> None:
        title = item.get("title") or ("Critical alert" if critical else "Home")
        url = self.open_url()
        for svc in self._services_for(item["to"]):
            data: dict[str, Any] = {}
            if svc.startswith("mobile_app_"):
                data = {"tag": f"housecall_{item['id']}", "group": "housecall"}
                if url:
                    data["url"] = url          # iPhone
                    data["clickAction"] = url  # Android
                if critical:
                    data.update(
                        {
                            # iPhone: break through silent / Do Not Disturb
                            "push": {
                                "sound": {"name": "default", "critical": 1, "volume": 1.0},
                                "interruption-level": "critical",
                            },
                            # Android: alarm-style
                            "ttl": 0,
                            "priority": "high",
                            "channel": "alarm_stream",
                            "actions": [
                                {"action": f"{ACK_PREFIX}{item['id']}", "title": "I'm on it"}
                            ],
                        }
                    )
            payload = {"message": item["message"], "title": title}
            if data:
                payload["data"] = data
            if await self._call("notify", svc, payload):
                self._add_via(item, "phone")

    async def _speak(self, item: dict[str, Any]) -> None:
        tts = self.opts.get(CONF_TTS)
        speakers = self.opts.get(CONF_SPEAKERS) or []
        if not tts or not speakers:
            return
        if await self._call(
            "tts",
            "speak",
            {"media_player_entity_id": speakers, "message": item["message"]},
            target={"entity_id": tts},
        ):
            self._add_via(item, "speaker")

    async def _board(self, item: dict[str, Any]) -> None:
        # The HouseCall card always shows the message.
        self._add_via(item, "board")
        # Glass Message Board: post a tinted note, without its own phone notifications.
        if self.opts.get(CONF_GLASS_BOARD, True) and self.hass.services.has_service("glass_messages", "post"):
            tint = {PRIORITY_INFO: "sky", PRIORITY_NORMAL: "amber", PRIORITY_CRITICAL: "rose"}.get(item["priority"], "clear")
            single = item["to"][0] if len(item["to"]) == 1 and len(self.people()) > 1 else None
            to = single if single and single.startswith("person.") else "everyone"
            await self._call(
                "glass_messages", "post",
                {
                    "message": item["message"],
                    "to": to,
                    "sender_name": "HouseCall",
                    "tint": tint,
                    "pinned": item["priority"] == PRIORITY_CRITICAL,
                    "notify": False,
                },
            )
        # Any other action you chose under Configure.
        svc = (self.opts.get(CONF_BOARD_SERVICE) or "").strip()
        if "." not in svc:
            return
        domain, service = svc.split(".", 1)
        await self._call(domain, service, {"message": item["message"]})

    # ------------------------------------------------------------- escalation

    def _schedule_repeat(self, item_id: str) -> None:
        minutes = int(self.opts.get(CONF_REPEAT_MINUTES, DEFAULT_REPEAT_MINUTES) or DEFAULT_REPEAT_MINUTES)

        @callback
        def _fire(_now: Any) -> None:
            self._repeat_unsubs.pop(item_id, None)
            self.hass.async_create_task(self._repeat(item_id))

        self._repeat_unsubs[item_id] = async_call_later(self.hass, minutes * 60, _fire)

    async def _repeat(self, item_id: str) -> None:
        item = self._find(item_id)
        if not item or item["status"] != STATUS_WAITING:
            return
        max_repeats = int(self.opts.get(CONF_MAX_REPEATS, DEFAULT_MAX_REPEATS))
        if item["repeats"] >= max_repeats:
            item["status"] = STATUS_EXPIRED
            await self._changed()
            return
        item["repeats"] += 1
        await self._push(item, critical=True)
        await self._speak(item)
        self._schedule_repeat(item_id)
        await self._changed()

    # ---------------------------------------------------------- acknowledging

    @callback
    def _on_action(self, event: Event) -> None:
        action = str(event.data.get("action", ""))
        if not action.startswith(ACK_PREFIX):
            return
        item_id = action[len(ACK_PREFIX):]
        by = None
        user_id = event.context.user_id if event.context else None
        if user_id:
            for p in self.people():
                if p.get("user_id") == user_id:
                    by = p["name"]
                    break
        self.hass.async_create_task(self.async_acknowledge(item_id, by))

    async def async_acknowledge(self, item_id: str, by: str | None = None) -> bool:
        item = self._find(item_id)
        if not item or item["status"] == STATUS_ACKED:
            return False
        unsub = self._repeat_unsubs.pop(item_id, None)
        if unsub:
            unsub()
        item["status"] = STATUS_ACKED
        item["acked_by"] = by or "someone"
        item["acked_at"] = dt_util.now().isoformat()
        # Update the card straight away; talking to the phones can take a few seconds.
        await self._changed()
        self.hass.bus.async_fire(EVENT_ACKNOWLEDGED, {"id": item_id, "by": item["acked_by"]})
        self.hass.async_create_task(self._after_ack(item, by))
        return True

    async def _after_ack(self, item: dict[str, Any], by: str | None) -> None:
        # Clear the alert from everyone's phone, then tell the others who has it.
        for svc in self._services_for(item["to"]):
            if svc.startswith("mobile_app_"):
                await self._call(
                    "notify", svc,
                    {"message": "clear_notification", "data": {"tag": f"housecall_{item['id']}"}},
                )
        if item["priority"] == PRIORITY_CRITICAL:
            others = [p for p in item["to"] if self._name(p) != by]
            if others:
                await self._push(
                    {**item, "to": others, "message": f"{item['acked_by']} is handling it: {item['message']}",
                     "title": "Handled", "via": []},
                    critical=False,
                )

    # ------------------------------------------------------------ quiet flush

    async def _tick(self, _now: Any) -> None:
        if self.in_quiet_hours():
            return
        held = [i for i in self.history if i.get("status") == STATUS_HELD]
        if not held:
            return
        for item in reversed(held):
            await self._push(item, critical=False)
            item["status"] = STATUS_SENT
        await self._changed()

    # ------------------------------------------------------------------ misc

    def _find(self, item_id: str) -> dict[str, Any] | None:
        return next((i for i in self.history if i["id"] == item_id), None)

    async def async_clear(self) -> None:
        for unsub in self._repeat_unsubs.values():
            unsub()
        self._repeat_unsubs.clear()
        self.history.clear()
        await self._changed()

    def waiting_count(self) -> int:
        return sum(1 for i in self.history if i.get("status") == STATUS_WAITING)

    async def _save(self) -> None:
        await self._store.async_save({"history": self.history})

    async def _changed(self) -> None:
        await self._save()
        async_dispatcher_send(self.hass, SIGNAL_UPDATE)
        self.hass.bus.async_fire(EVENT_UPDATED, {"waiting": self.waiting_count()})
