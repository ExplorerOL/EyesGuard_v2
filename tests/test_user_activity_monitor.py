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


def make_monitor_with_idle_script(monkeypatch, idle_seconds: list[float], timeout_seconds: int = 180):
    """UserActivityMonitor with a scripted OS idle source."""
    from support.user_activity_monitor import UserActivityMonitor

    monitor = UserActivityMonitor(activity_timeout=datetime.timedelta(seconds=timeout_seconds))
    values = list(idle_seconds)

    def fake_os_idle(self):
        if values:
            value = values.pop(0)
        else:
            value = values_fallback[0]
        return datetime.timedelta(seconds=value)

    values_fallback = [idle_seconds[-1] if idle_seconds else 0]
    monkeypatch.setattr(UserActivityMonitor, '_UserActivityMonitor__get_user_idle_time_from_os', fake_os_idle)
    return monitor


def test_set_activity_offset_when_inactive(monkeypatch):
    monitor = make_monitor_with_idle_script(monkeypatch, idle_seconds=[600, 600])

    assert monitor.is_user_active is False  # 10 min idle > 3 min timeout
    monitor.set_activity_offset()
    assert monitor._idle_time_offset == datetime.timedelta(seconds=600)


def test_reset_activity_offset_when_active(monkeypatch):
    monitor = make_monitor_with_idle_script(monkeypatch, idle_seconds=[10, 10])

    assert monitor.is_user_active is True
    monitor.reset_activity_offset()
    assert monitor._idle_time_offset == datetime.timedelta(seconds=0)


def test_offset_resets_on_new_real_input(monkeypatch):
    """Regression for known issue 22: a stale offset must not extend the next timeout.

    Long break without input (offset ~10 min) -> user returns (idle drops to
    0) -> user goes idle again for 200 s: with timeout=180 s the user must be
    considered inactive, not masked by the stale 10-minute offset.
    """
    monitor = make_monitor_with_idle_script(
        monkeypatch,
        # reads: is_user_active, set_activity_offset(is_user_active + raw read),
        # then fresh input (0 s) and the next inactivity (200 s)
        idle_seconds=[600, 600, 600, 0, 200],
        timeout_seconds=180,
    )

    assert monitor.is_user_active is False  # 600 s idle: inactive
    monitor.set_activity_offset()  # offset = 600 s
    assert monitor.is_user_active is True  # fresh input: idle 0 s -> active, offset resets

    assert monitor._idle_time_offset == datetime.timedelta(seconds=0)
    assert monitor.is_user_active is False  # 200 s idle > 180 s timeout: inactive again
