"""Tests for UI timedelta formatting."""

import datetime

from support.time_format import format_timedelta


def test_format_timedelta_seconds_only():
    assert format_timedelta(datetime.timedelta(seconds=45)) == '0:00:45'


def test_format_timedelta_minutes_and_seconds():
    assert format_timedelta(datetime.timedelta(minutes=1, seconds=30)) == '0:01:30'


def test_format_timedelta_hours():
    assert format_timedelta(datetime.timedelta(hours=1)) == '1:00:00'


def test_format_timedelta_drops_microseconds():
    value = datetime.timedelta(seconds=45, microseconds=123456)

    assert format_timedelta(value) == '0:00:45'


def test_format_timedelta_clamps_negative_to_zero():
    assert format_timedelta(datetime.timedelta(seconds=-5)) == '0:00:00'
