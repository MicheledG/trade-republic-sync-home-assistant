"""Trade Republic Sync: start an approved Trade Republic to Wallet sync from Home Assistant.

The backend arms a run; a notification on the phone opens the Trade Republic
app for approval; the outcome comes back as entities and a notification. Runs
start from the button or on the schedule set in the integration's options.
"""

from __future__ import annotations

from datetime import datetime

from homeassistant.const import Platform
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import UpdateFailed

from .api import SyncApi, SyncApiError, SyncAuthError
from .const import ACTIONS, CONF_API_KEY, CONF_URL
from .coordinator import SyncConfigEntry, SyncCoordinator
from .schedule import due_now

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: SyncConfigEntry) -> bool:
    api = SyncApi(async_get_clientsession(hass), entry.data[CONF_URL], entry.data[CONF_API_KEY])
    try:
        await api.async_check()
    except SyncAuthError as err:
        raise ConfigEntryAuthFailed("the API key was refused") from err
    except SyncApiError as err:
        raise ConfigEntryNotReady("the sync service is unreachable") from err

    coordinator = SyncCoordinator(hass, entry, api)
    await coordinator.async_load()
    entry.runtime_data = coordinator
    if coordinator.update_interval is not None:
        await coordinator.async_refresh()

    @callback
    def _tick(now: datetime) -> None:
        if due_now(now, dict(entry.options)):
            hass.async_create_task(_scheduled_start(coordinator))

    entry.async_on_unload(async_track_time_change(hass, _tick, second=0))

    @callback
    def _action(event: Event) -> None:
        if event.data.get("action") in ACTIONS:
            hass.async_create_task(coordinator.async_handle_action(event))

    entry.async_on_unload(hass.bus.async_listen("mobile_app_notification_action", _action))
    entry.async_on_unload(coordinator.async_shutdown_reminder)
    entry.async_on_unload(entry.add_update_listener(_reload))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _scheduled_start(coordinator: SyncCoordinator) -> None:
    try:
        await coordinator.async_start()
    except UpdateFailed:
        coordinator.logger.warning("Scheduled sync could not be armed")


async def _reload(hass: HomeAssistant, entry: SyncConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: SyncConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
