"""Sensor that feeds the dashboard card: state = alerts waiting for an answer."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_SPEAKERS, CONF_TTS, SIGNAL_UPDATE
from .hub import HouseCall


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([HouseCallSensor(entry.runtime_data, entry)])


class HouseCallSensor(SensorEntity):
    _attr_has_entity_name = False
    _attr_name = "HouseCall"
    _attr_icon = "mdi:bell-ring"
    _attr_should_poll = False
    _attr_native_unit_of_measurement = "waiting"
    _unrecorded_attributes = frozenset({"history", "people", "quiet_hours", "outputs"})

    def __init__(self, hub: HouseCall, entry: ConfigEntry) -> None:
        self.hub = hub
        self._attr_unique_id = f"{entry.entry_id}_hub"

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_UPDATE, self._refresh))
        # Presence (home/away) changes show on the card too.
        self.async_on_remove(
            self.hass.bus.async_listen("state_changed", self._maybe_person)
        )

    @callback
    def _maybe_person(self, event) -> None:
        if str(event.data.get("entity_id", "")).startswith("person."):
            self.async_write_ha_state()

    @callback
    def _refresh(self) -> None:
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        return self.hub.waiting_count()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        start, end = self.hub.quiet_window()
        opts = self.hub.opts
        return {
            "history": self.hub.history[:50],
            "people": [
                {"id": p["id"], "name": p["name"], "home": p["home"], "phones": len(p["services"]), "apps": len(p.get("routes", [])) + len(self.hub.person_builtins(p)), "custom": p["custom"]}
                for p in self.hub.people()
            ],
            "quiet_hours": {
                "start": start.strftime("%H:%M"),
                "end": end.strftime("%H:%M"),
                "active": self.hub.in_quiet_hours(),
            },
            "outputs": {
                "speaker": bool(opts.get(CONF_TTS) and opts.get(CONF_SPEAKERS)),
            },
        }
