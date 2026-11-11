"""Constants for Trade Republic Sync."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "trade_republic_sync"

CONF_URL: Final = "url"
CONF_API_KEY: Final = "api_key"

OPT_FREQUENCY: Final = "frequency"
OPT_TIME: Final = "time"
OPT_WEEKDAYS: Final = "weekdays"
OPT_MONTH_DAY: Final = "month_day"
OPT_ARM_HOURS: Final = "arm_hours"
OPT_NOTIFY: Final = "notify_service"

FREQ_OFF: Final = "off"
FREQ_DAILY: Final = "daily"
FREQ_WEEKLY: Final = "weekly"
FREQ_MONTHLY: Final = "monthly"
FREQUENCIES: Final = [FREQ_OFF, FREQ_DAILY, FREQ_WEEKLY, FREQ_MONTHLY]
WEEKDAYS: Final = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

DEFAULT_TIME: Final = "09:00:00"
DEFAULT_ARM_HOURS: Final = 12
MAX_ARM_HOURS: Final = 48

# States the backend reports for a run.
STATE_ARMED: Final = "armed"
BUSY_STATES: Final = ("armed", "starting", "waiting", "claimed", "syncing")
FINAL_STATES: Final = ("ok", "error", "expired", "wrong_account", "cancelled")
RUN_STATES: Final = ["idle", *BUSY_STATES, *FINAL_STATES]

# While a run is armed nobody is looking at the phone yet: poll slowly.
POLL_ARMED: Final = timedelta(seconds=30)
POLL_ACTIVE: Final = timedelta(seconds=4)
REQUEST_TIMEOUT_SECONDS: Final = 30

NOTIFICATION_TAG: Final = "trade_republic_sync"
# Android channels: the approval must ring; progress and outcomes stay quiet.
CHANNEL_APPROVAL: Final = "Trade Republic Sync"
CHANNEL_OUTCOME: Final = "Trade Republic Sync esiti"

# Actions on the notification, answered through mobile_app_notification_action.
ACTION_SNOOZE: Final = "TRADE_REPUBLIC_SYNC_SNOOZE"
ACTION_CANCEL: Final = "TRADE_REPUBLIC_SYNC_CANCEL"
ACTION_RETRY: Final = "TRADE_REPUBLIC_SYNC_RETRY"
ACTIONS: Final = (ACTION_SNOOZE, ACTION_CANCEL, ACTION_RETRY)
SNOOZE: Final = timedelta(hours=2)

# The look of every notification on Android: the integration's own icon and colour.
NOTIFICATION_ICON: Final = "mdi:sync"
NOTIFICATION_COLOR: Final = "#00A866"
NOTIFICATION_LARGE_ICON: Final = (
    "https://raw.githubusercontent.com/MicheledG/trade-republic-sync-home-assistant/main/"
    "custom_components/trade_republic_sync/brand/icon.png"
)

# Tapping an outcome with problems opens Wallet by BudgetBakers on Android.
WALLET_APP: Final = "app://com.droid4you.application.wallet"
