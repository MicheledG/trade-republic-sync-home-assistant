"""Set-up (service URL and API key) and options (schedule and notifications)."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    TimeSelector,
)
import voluptuous as vol

from .api import SyncApi, SyncApiError, SyncAuthError
from .const import (
    CONF_API_KEY,
    CONF_URL,
    DEFAULT_ARM_HOURS,
    DEFAULT_TIME,
    DOMAIN,
    FREQ_OFF,
    FREQUENCIES,
    MAX_ARM_HOURS,
    OPT_ARM_HOURS,
    OPT_FREQUENCY,
    OPT_MONTH_DAY,
    OPT_NOTIFY,
    OPT_TIME,
    OPT_WEEKDAYS,
    WEEKDAYS,
)


async def _check(hass: Any, url: str, key: str) -> str | None:
    try:
        await SyncApi(async_get_clientsession(hass), url, key).async_check()
    except SyncAuthError:
        return "invalid_auth"
    except SyncApiError:
        return "cannot_connect"
    return None


def _credentials_schema(url: str = "") -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_URL, default=url): TextSelector(TextSelectorConfig(type=TextSelectorType.URL)),
        vol.Required(CONF_API_KEY): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
    })


class SyncConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            url = user_input[CONF_URL].strip().rstrip("/")
            if not url.startswith("https://"):
                errors[CONF_URL] = "not_https"
            elif error := await _check(self.hass, url, user_input[CONF_API_KEY]):
                errors["base"] = error
            else:
                await self.async_set_unique_id(url)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Trade Republic Sync",
                    data={CONF_URL: url, CONF_API_KEY: user_input[CONF_API_KEY]},
                    options={OPT_FREQUENCY: FREQ_OFF, OPT_TIME: DEFAULT_TIME,
                             OPT_ARM_HOURS: DEFAULT_ARM_HOURS},
                )
        return self.async_show_form(step_id="user", data_schema=_credentials_schema(), errors=errors)

    async def async_step_reauth(self, _entry_data: dict[str, Any]) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            if error := await _check(self.hass, entry.data[CONF_URL], user_input[CONF_API_KEY]):
                errors["base"] = error
            else:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_API_KEY: user_input[CONF_API_KEY]}
                )
        schema = vol.Schema({vol.Required(CONF_API_KEY): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD))})
        return self.async_show_form(step_id="reauth_confirm", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(_entry: Any) -> SyncOptionsFlow:
        return SyncOptionsFlow()


class SyncOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        options = self.config_entry.options
        notifiers = sorted(f"notify.{name}" for name in self.hass.services.async_services_for_domain("notify"))
        notify_key = (vol.Optional(OPT_NOTIFY, description={"suggested_value": options.get(OPT_NOTIFY)})
                      if options.get(OPT_NOTIFY) else vol.Optional(OPT_NOTIFY))
        schema = vol.Schema({
            vol.Required(OPT_FREQUENCY, default=options.get(OPT_FREQUENCY, FREQ_OFF)): SelectSelector(
                SelectSelectorConfig(options=FREQUENCIES, translation_key="frequency",
                                     mode=SelectSelectorMode.DROPDOWN)),
            vol.Required(OPT_TIME, default=options.get(OPT_TIME, DEFAULT_TIME)): TimeSelector(),
            vol.Optional(OPT_WEEKDAYS, default=options.get(OPT_WEEKDAYS, [])): SelectSelector(
                SelectSelectorConfig(options=WEEKDAYS, multiple=True, translation_key="weekday")),
            vol.Optional(OPT_MONTH_DAY, default=options.get(OPT_MONTH_DAY, 1)): NumberSelector(
                NumberSelectorConfig(min=1, max=31, step=1, mode=NumberSelectorMode.BOX)),
            vol.Required(OPT_ARM_HOURS, default=options.get(OPT_ARM_HOURS, DEFAULT_ARM_HOURS)): NumberSelector(
                NumberSelectorConfig(min=1, max=MAX_ARM_HOURS, step=1, mode=NumberSelectorMode.BOX,
                                     unit_of_measurement="h")),
            notify_key: SelectSelector(SelectSelectorConfig(options=notifiers,
                                                            mode=SelectSelectorMode.DROPDOWN)),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
