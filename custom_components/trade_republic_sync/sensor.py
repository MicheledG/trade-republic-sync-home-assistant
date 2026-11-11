"""Sensors: the run state, the last finished sync, the next scheduled one."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import RUN_STATES
from .coordinator import SyncConfigEntry
from .entity import SyncEntity
from .schedule import next_run


async def async_setup_entry(
    hass: HomeAssistant, entry: SyncConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    c = entry.runtime_data
    async_add_entities([StateSensor(c, "state"), LastSyncSensor(c, "last_sync"),
                        NextSyncSensor(c, "next_sync")])


class StateSensor(SyncEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = RUN_STATES

    @property
    def native_value(self) -> str:
        return self.coordinator.run_state


class LastSyncSensor(SyncEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.last_finished_at()

    @property
    def extra_state_attributes(self) -> dict:
        last = self.coordinator.data.get("last_finished") or {}
        summary = last.get("summary") or {}
        return {
            "outcome": last.get("state"),
            "new_records": summary.get("to_create"),
            "balance_gap": summary.get("balance_gap"),
            "problems": last.get("problems") or [],
        }


class NextSyncSensor(SyncEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        return next_run(dt_util.now(), dict(self.coordinator.config_entry.options))
