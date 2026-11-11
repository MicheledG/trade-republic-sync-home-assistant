"""The button that arms a sync now."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import UpdateFailed

from .coordinator import SyncConfigEntry
from .entity import SyncEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: SyncConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([SyncNowButton(entry.runtime_data, "sync_now")])


class SyncNowButton(SyncEntity, ButtonEntity):
    _attr_icon = "mdi:sync"

    async def async_press(self) -> None:
        try:
            await self.coordinator.async_start()
        except UpdateFailed as err:
            raise HomeAssistantError(str(err)) from err
