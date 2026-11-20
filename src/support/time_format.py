"""Formatting of time durations for UI display."""

import datetime


def format_timedelta(value: datetime.timedelta) -> str:
    """Format a timedelta as H:MM:SS with whole seconds (microseconds dropped).

    Negative values are clamped to zero: a slightly overdue step must not
    show a negative remaining time in the UI.
    """
    total_seconds = max(int(value.total_seconds()), 0)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours}:{minutes:02d}:{seconds:02d}'
