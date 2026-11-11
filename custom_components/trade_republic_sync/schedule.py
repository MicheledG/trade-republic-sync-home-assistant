"""When the next scheduled run is due, from the entry's options."""

from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, time, timedelta
from typing import Any

from .const import (
    DEFAULT_TIME,
    FREQ_DAILY,
    FREQ_MONTHLY,
    FREQ_OFF,
    FREQ_WEEKLY,
    OPT_FREQUENCY,
    OPT_MONTH_DAY,
    OPT_TIME,
    OPT_WEEKDAYS,
    WEEKDAYS,
)


def _due_on(day: date, options: dict[str, Any]) -> bool:
    frequency = options.get(OPT_FREQUENCY, FREQ_OFF)
    if frequency == FREQ_DAILY:
        return True
    if frequency == FREQ_WEEKLY:
        return WEEKDAYS[day.weekday()] in options.get(OPT_WEEKDAYS, [])
    if frequency == FREQ_MONTHLY:
        wanted = int(options.get(OPT_MONTH_DAY, 1))
        # Day 31 in a 30-day month means the month's last day.
        return day.day == min(wanted, monthrange(day.year, day.month)[1])
    return False


def run_time(options: dict[str, Any]) -> time:
    return time.fromisoformat(options.get(OPT_TIME, DEFAULT_TIME))


def next_run(now: datetime, options: dict[str, Any]) -> datetime | None:
    """The first due moment strictly after `now`, in `now`'s timezone."""
    if options.get(OPT_FREQUENCY, FREQ_OFF) == FREQ_OFF:
        return None
    at = run_time(options)
    for offset in range(0, 62):
        day = (now + timedelta(days=offset)).date()
        candidate = datetime.combine(day, at, tzinfo=now.tzinfo)
        if candidate > now and _due_on(day, options):
            return candidate
    return None


def due_now(now: datetime, options: dict[str, Any]) -> bool:
    """Whether a time-change tick at `now` (whole minute) is a scheduled run."""
    at = run_time(options)
    return (now.hour, now.minute) == (at.hour, at.minute) and _due_on(now.date(), options)
