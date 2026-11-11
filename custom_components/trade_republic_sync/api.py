"""Client for the sync backend's three-route API."""

from __future__ import annotations

import json
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from .const import REQUEST_TIMEOUT_SECONDS


class SyncApiError(Exception):
    """The backend could not be reached or answered unexpectedly."""


class SyncAuthError(SyncApiError):
    """The backend refused the API key."""


class SyncApi:
    """Arms runs and reads their state. The key travels only in a header."""

    def __init__(self, session: ClientSession, url: str, api_key: str) -> None:
        self._session = session
        self._url = url.rstrip("/")
        self._headers = {"X-Api-Key": api_key}
        self._timeout = ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)

    async def _request(self, method: str, path: str, **kwargs: Any) -> tuple[int, dict]:
        try:
            async with self._session.request(
                method, f"{self._url}{path}", headers=self._headers,
                timeout=self._timeout, **kwargs,
            ) as resp:
                status = resp.status
                raw = await resp.text()
        except (ClientError, TimeoutError, ValueError) as err:
            raise SyncApiError(type(err).__name__) from err
        if status == 401:
            raise SyncAuthError("unauthorised")
        try:
            body = json.loads(raw) if raw else {}
        except ValueError as err:
            raise SyncApiError("not JSON") from err
        return status, body if isinstance(body, dict) else {}

    async def async_check(self) -> None:
        """Prove URL and key work: an unknown run must be a 404, not a 401."""
        status, _ = await self._request("GET", "/runs/check")
        if status != 404:
            raise SyncApiError(f"unexpected status {status}")

    async def async_arm(self, arm_hours: float) -> dict:
        status, body = await self._request("POST", "/runs", json={"arm_hours": arm_hours})
        if status not in (200, 201) or "run_id" not in body:
            raise SyncApiError(f"unexpected status {status}")
        return body

    async def async_cancel(self, run_id: str) -> dict | None:
        """Close a run that has not started syncing; None if the backend no longer has it."""
        status, body = await self._request("DELETE", f"/runs/{run_id}")
        if status in (404, 409):
            return None
        if status != 200:
            raise SyncApiError(f"unexpected status {status}")
        return body

    async def async_run(self, run_id: str) -> dict | None:
        status, body = await self._request("GET", f"/runs/{run_id}")
        if status == 404:
            return None
        if status != 200:
            raise SyncApiError(f"unexpected status {status}")
        return body
