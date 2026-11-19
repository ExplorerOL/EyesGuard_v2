"""Tests for the Model finite state machine (timings, transitions, actions).

The Model is tested without Tk and without Windows API: the activity monitor
is stubbed, the sound player is the no-op one, view calls are recorded.
"""

import datetime

from conftest import make_model, run_ticks_until_step_ends

from config.settings import UserSettingsData
from config.states import StepType

NOTIFICATION_1_DURATION = datetime.timedelta(seconds=55)
NOTIFICATION_2_DURATION = datetime.timedelta(seconds=5)
SUSPENDED_DURATION = datetime.timedelta(minutes=60)


def test_initial_step_is_work_mode_when_protection_on(tmp_path, monkeypatch):
    model, view, _ = make_model(tmp_path, monkeypatch, settings={'protection_status': 'on'})

    assert model.current_state.current_step_type == StepType.work_mode
    # initial setup publishes several snapshots (init + first step actions)
    assert view.snapshots
    assert view.snapshots[-1].step_type == StepType.work_mode


def test_snapshot_contains_state_and_settings_copy(tmp_path, monkeypatch):
    model, view, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 25})

    snapshot = view.snapshots[-1]

    assert snapshot.step_type == StepType.work_mode
    assert snapshot.step_duration == datetime.timedelta(minutes=25) - (
        NOTIFICATION_1_DURATION + NOTIFICATION_2_DURATION
    )
    assert snapshot.time_for_work_full == (datetime.timedelta(minutes=25))
    assert snapshot.break_step_duration == datetime.timedelta(minutes=15)
    assert snapshot.user_settings.work_duration == 25
    # snapshot settings are a copy: later Model changes must not mutate it
    new_settings = UserSettingsData()
    new_settings.work_duration = 50
    model.apply_new_user_settings(user_settings=new_settings)
    assert snapshot.user_settings.work_duration == 25


def test_set_step_publishes_break_snapshot(tmp_path, monkeypatch):
    model, view, _ = make_model(tmp_path, monkeypatch)

    model.set_step(new_step_type=StepType.break_mode)

    assert view.snapshots[-1].step_type == StepType.break_mode
    assert view.snapshots[-1].break_step_duration == datetime.timedelta(minutes=15)


def test_initial_step_is_off_mode_when_protection_off(tmp_path, monkeypatch):
    model, view, _ = make_model(tmp_path, monkeypatch, settings={'protection_status': 'off'})

    assert model.current_state.current_step_type == StepType.off_mode
    assert view.notifications == [('Eyes Guard protection is off!', 'Attention!')]


def test_steps_durations_from_settings(tmp_path, monkeypatch):
    model, _, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 50, 'break_duration': 20})

    steps = model.steps_data_list
    assert len(steps) == len(StepType)
    assert steps[StepType.off_mode].step_duration_td == SUSPENDED_DURATION
    assert steps[StepType.suspended_mode].step_duration_td == SUSPENDED_DURATION
    assert steps[StepType.work_mode].step_duration_td == (
        datetime.timedelta(minutes=50) - NOTIFICATION_1_DURATION - NOTIFICATION_2_DURATION
    )
    assert steps[StepType.work_notified_1].step_duration_td == NOTIFICATION_1_DURATION
    assert steps[StepType.work_notified_2].step_duration_td == NOTIFICATION_2_DURATION
    assert steps[StepType.break_mode].step_duration_td == datetime.timedelta(minutes=20)


def test_steps_durations_min_work_duration(tmp_path, monkeypatch):
    """Work duration below notifications total collapses the work step to zero."""
    model, _, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 1})

    steps = model.steps_data_list
    assert steps[StepType.work_mode].step_duration_td == datetime.timedelta(seconds=0)


def test_linear_step_sequence(tmp_path, monkeypatch):
    model, _, _ = make_model(tmp_path, monkeypatch)

    transitions = [
        (StepType.work_mode, StepType.work_notified_1),
        (StepType.work_notified_1, StepType.work_notified_2),
        (StepType.work_notified_2, StepType.break_mode),
        (StepType.break_mode, StepType.work_mode),
    ]
    for current, expected_next in transitions:
        model.set_step(new_step_type=current)
        model.set_new_step_in_sequence()
        assert model.current_state.current_step_type == expected_next


def test_off_mode_keeps_step_in_sequence(tmp_path, monkeypatch):
    model, _, _ = make_model(tmp_path, monkeypatch, settings={'protection_status': 'off'})

    model.set_new_step_in_sequence()

    assert model.current_state.current_step_type == StepType.off_mode


def test_suspended_mode_returns_to_work_in_sequence(tmp_path, monkeypatch):
    model, _, _ = make_model(tmp_path, monkeypatch)

    model.set_step(new_step_type=StepType.suspended_mode)
    model.set_new_step_in_sequence()

    assert model.current_state.current_step_type == StepType.work_mode


def test_set_step_resets_elapsed_and_sets_duration(tmp_path, monkeypatch):
    model, _, _ = make_model(tmp_path, monkeypatch)
    model.current_state.increase_elapsed_time(time_delta=datetime.timedelta(seconds=30))

    model.set_step(new_step_type=StepType.break_mode)

    assert model.current_state.current_step_type == StepType.break_mode
    assert model.current_state.current_step_duration == datetime.timedelta(minutes=15)
    assert model.current_state.current_step_elapsed_time == datetime.timedelta(seconds=0)


def test_wait_for_step_ends_when_duration_elapsed(tmp_path, monkeypatch):
    """Zero-duration work step (work_duration=1) ends on the first wait iteration."""
    model, _, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 1})

    run_ticks_until_step_ends(model)
    model.set_new_step_in_sequence()

    assert model.current_state.current_step_type == StepType.work_notified_1


def test_wait_loop_switches_to_idle_and_back_when_activity_scripted(tmp_path, monkeypatch):
    """Inactive user switches work step to idle; returned activity exits idle.

    The tick loop cannot terminate while the user stays idle, so the monitor
    is scripted: a few inactive reads, then active. work_duration=2 makes the
    work step exactly 60 seconds, so the step ends soon after returning.
    """
    model, view, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 2}, inactive_reads=3)

    run_ticks_until_step_ends(model)
    idle_entered = any('iddle' in message for message, _ in view.notifications)

    assert model.current_state.current_step_type == StepType.work_mode
    assert idle_entered


def test_wait_loop_ends_work_step_by_duration(tmp_path, monkeypatch):
    """Active user: the tick loop ends only when the step duration is elapsed."""
    model, _, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 1})

    ended_on_first_tick = model.tick()

    assert ended_on_first_tick is True
    assert model.current_state.current_step_type == StepType.work_mode
