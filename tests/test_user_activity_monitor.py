"""Tests for the user activity monitor idle time calculation (known issue 23)."""

import datetime

from support.user_activity_monitor import idle_time_from_ticks


def test_idle_time_small_difference():
    assert idle_time_from_ticks(tick_count=10_000, last_input_tick=3_000) == datetime.timedelta(seconds=7)


def test_idle_time_at_2_pow_31_boundary():
    """Crossing 2**31 must not turn idle time negative (signed int default)."""
    assert idle_time_from_ticks(tick_count=2**31, last_input_tick=0) == datetime.timedelta(milliseconds=2**31)


def test_idle_time_at_2_pow_32_boundary():
    assert idle_time_from_ticks(tick_count=2**32, last_input_tick=2**32 - 1_000) == datetime.timedelta(seconds=1)


def test_idle_time_wrapped_between_last_input_and_now():
    """DwTime wraps before the current tick: modulo arithmetic must give 6 seconds."""
    assert idle_time_from_ticks(tick_count=2**32 + 5_000, last_input_tick=2**32 - 1_000) == (
        datetime.timedelta(seconds=6)
    )
