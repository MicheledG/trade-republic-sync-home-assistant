"""The run lifecycle: arm, follow, notify.

A run is armed on the backend first; nothing reaches Trade Republic until the
person taps the notification. The coordinator polls slowly while a run is
armed and quickly once the login has started, and stops polling when the run
is over.
"""

from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import SyncApi, SyncApiError
from .const import (
    BUSY_STATES,
    DEFAULT_ARM_HOURS,
    DOMAIN,
    FINAL_STATES,
    NOTIFICATION_TAG,
    OPT_ARM_HOURS,
    OPT_NOTIFY,
    POLL_ACTIVE,
    POLL_ARMED,
    STATE_ARMED,
)
from .texts import text

_LOGGER = logging.getLogger(__name__)

type SyncConfigEntry = ConfigEntry[SyncCoordinator]

STORE_VERSION = 1


class SyncCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Holds the current run and the last finished one."""

    def __init__(self, hass: HomeAssistant, entry: SyncConfigEntry, api: SyncApi) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=DOMAIN, update_interval=None)
        self.api = api
        self._store: Store[dict[str, Any]] = Store(hass, STORE_VERSION, f"{DOMAIN}.{entry.entry_id}")
        self.data = {"run": None, "last_finished": None}

    async def async_load(self) -> None:
        """Resume following a run that was in progress before a restart."""
        stored = await self._store.async_load() or {}
        self.data = {"run": stored.get("run"), "last_finished": stored.get("last_finished")}
        self._set_interval()

    async def _save(self) -> None:
        await self._store.async_save(self.data)

    def _set_interval(self) -> None:
        run = self.data.get("run")
        if not run or run.get("state") not in BUSY_STATES:
            self.update_interval = None
        elif run["state"] == STATE_ARMED:
            self.update_interval = POLL_ARMED
        else:
            self.update_interval = POLL_ACTIVE

    @property
    def run_state(self) -> str:
        run = self.data.get("run")
        return run["state"] if run else "idle"

    async def async_start(self) -> None:
        """Arm a run (or pick up the one already armed) and notify the phone."""
        hours = float(self.config_entry.options.get(OPT_ARM_HOURS, DEFAULT_ARM_HOURS))
        try:
            run = await self.api.async_arm(hours)
        except SyncApiError as err:
            await self._notify(text(self.hass, "unreachable"))
            raise UpdateFailed(str(err)) from err
        self.data = {**self.data, "run": run}
        await self._save()
        self._set_interval()
        self.async_set_updated_data(self.data)
        # A run already armed comes back unchanged; its notification is sent again.
        await self._notify_approval(run)

    async def _async_update_data(self) -> dict[str, Any]:
        run = self.data.get("run")
        if not run or run.get("state") not in BUSY_STATES:
            return self.data
        try:
            fresh = await self.api.async_run(run["run_id"])
        except SyncApiError as err:
            raise UpdateFailed(str(err)) from err
        if fresh is None:  # replaced on the backend (another client armed a run)
            fresh = {**run, "state": "expired"}
        data = {**self.data, "run": fresh}
        if fresh["state"] != run["state"]:
            await self._on_transition(run, fresh)
            if fresh["state"] in FINAL_STATES:
                data["last_finished"] = fresh
        self.data = data
        await self._save()
        self._set_interval()
        return data

    async def _on_transition(self, old: dict[str, Any], new: dict[str, Any]) -> None:
        state = new["state"]
        if state == STATE_ARMED and old["state"] != STATE_ARMED:
            # The login lapsed or was rejected: the same link works again.
            await self._notify_approval(new, again=True)
        elif state == "ok":
            summary = new.get("summary") or {}
            count = int(summary.get("to_create") or 0)
            problems = len(new.get("problems") or [])
            key = "done_problems" if problems else "done"
            await self._notify(text(self.hass, key, count=count, problems=problems))
        elif state == "error":
            await self._notify(text(self.hass, "error"))
        elif state == "wrong_account":
            await self._notify(text(self.hass, "wrong_account"))
        elif state == "expired":
            await self._clear()

    async def _notify_approval(self, run: dict[str, Any], again: bool = False) -> None:
        url = run["approve_url"]
        await self._notify(
            text(self.hass, "approve_again" if again else "approve"),
            data={
                "url": url,
                "clickAction": url,
                "actions": [{"action": "URI", "title": text(self.hass, "approve_button"), "uri": url}],
            },
        )

    async def _notify(self, message: str, data: dict[str, Any] | None = None) -> None:
        service = self.config_entry.options.get(OPT_NOTIFY)
        if not service:
            return
        payload: dict[str, Any] = {
            "title": "Trade Republic",
            "message": message,
            "data": {"tag": NOTIFICATION_TAG, **(data or {})},
        }
        await self._call_notify(service, payload)

    async def _clear(self) -> None:
        service = self.config_entry.options.get(OPT_NOTIFY)
        if service:
            await self._call_notify(
                service, {"message": "clear_notification", "data": {"tag": NOTIFICATION_TAG}}
            )

    async def _call_notify(self, service: str, payload: dict[str, Any]) -> None:
        domain, _, name = service.partition(".")
        if not name:
            domain, name = "notify", service
        try:
            await self.hass.services.async_call(domain, name, payload, blocking=True)
        except Exception:  # a broken notifier must not break the sync
            _LOGGER.warning("Could not send the notification through %s", service)

    def last_finished_at(self) -> datetime | None:
        last = self.data.get("last_finished")
        when = last and last.get("finished_at")
        return dt_util.parse_datetime(when) if when else None
