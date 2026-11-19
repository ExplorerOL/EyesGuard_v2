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
    model, view, _, _ = make_model(tmp_path, monkeypatch, settings={'protection_status': 'on'})

    assert model.current_state.current_step_type == StepType.work_mode
    # initial setup publishes several snapshots (init + first step actions)
    assert view.snapshots
    assert view.snapshots[-1].step_type == StepType.work_mode


def test_snapshot_contains_state_and_settings_copy(tmp_path, monkeypatch):
    model, view, _, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 25})

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
    model, view, _, _ = make_model(tmp_path, monkeypatch)

    model.set_step(new_step_type=StepType.break_mode)

    assert view.snapshots[-1].step_type == StepType.break_mode
    assert view.snapshots[-1].break_step_duration == datetime.timedelta(minutes=15)


def test_initial_step_is_off_mode_when_protection_off(tmp_path, monkeypatch):
    model, view, _, _ = make_model(tmp_path, monkeypatch, settings={'protection_status': 'off'})

    assert model.current_state.current_step_type == StepType.off_mode
    assert view.notifications == [('Eyes Guard protection is off!', 'Attention!')]


def test_steps_durations_from_settings(tmp_path, monkeypatch):
    model, _, _, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 50, 'break_duration': 20})

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
    model, _, _, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 1})

    steps = model.steps_data_list
    assert steps[StepType.work_mode].step_duration_td == datetime.timedelta(seconds=0)


def test_linear_step_sequence(tmp_path, monkeypatch):
    model, _, _, _ = make_model(tmp_path, monkeypatch)

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
    model, _, _, _ = make_model(tmp_path, monkeypatch, settings={'protection_status': 'off'})

    model.set_new_step_in_sequence()

    assert model.current_state.current_step_type == StepType.off_mode


def test_suspended_mode_returns_to_work_in_sequence(tmp_path, monkeypatch):
    model, _, _, _ = make_model(tmp_path, monkeypatch)

    model.set_step(new_step_type=StepType.suspended_mode)
    model.set_new_step_in_sequence()

    assert model.current_state.current_step_type == StepType.work_mode


def test_set_step_resets_elapsed_and_sets_duration(tmp_path, monkeypatch):
    model, _, _, _ = make_model(tmp_path, monkeypatch)
    model.current_state.increase_elapsed_time(time_delta=datetime.timedelta(seconds=30))

    model.set_step(new_step_type=StepType.break_mode)

    assert model.current_state.current_step_type == StepType.break_mode
    assert model.current_state.current_step_duration == datetime.timedelta(minutes=15)
    assert model.current_state.current_step_elapsed_time == datetime.timedelta(seconds=0)


def test_wait_for_step_ends_when_duration_elapsed(tmp_path, monkeypatch):
    """Zero-duration work step (work_duration=1) ends on the first wait iteration."""
    model, _, _, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 1})

    run_ticks_until_step_ends(model)
    model.set_new_step_in_sequence()

    assert model.current_state.current_step_type == StepType.work_notified_1


def test_wait_loop_switches_to_idle_and_back_when_activity_scripted(tmp_path, monkeypatch):
    """Inactive user switches work step to idle; returned activity exits idle.

    The tick loop cannot terminate while the user stays idle, so the monitor
    is scripted: a few inactive reads, then active. work_duration=2 makes the
    work step exactly 60 seconds, so the step ends soon after returning.
    """
    model, view, _, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 2}, inactive_reads=3)

    run_ticks_until_step_ends(model)
    idle_entered = any('iddle' in message for message, _ in view.notifications)

    assert model.current_state.current_step_type == StepType.work_mode
    assert idle_entered


def test_wait_loop_ends_work_step_by_duration(tmp_path, monkeypatch):
    """Active user: the tick loop ends only when the step duration is elapsed."""
    model, _, _, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 1})

    ended_on_first_tick = model.tick()

    assert ended_on_first_tick is True
    assert model.current_state.current_step_type == StepType.work_mode


def test_sequence_transition_from_idle_mode_returns_to_work(tmp_path, monkeypatch):
    """Regression for known issue 8: the transitions match must be exhaustive.

    Entering set_new_step_in_sequence from iddle_mode must not raise
    UnboundLocalError and must fall back to work_mode.
    """
    model, _, _, _ = make_model(tmp_path, monkeypatch)

    model.set_step(new_step_type=StepType.iddle_mode)
    model.set_new_step_in_sequence()

    assert model.current_state.current_step_type == StepType.work_mode


def test_apply_settings_does_not_grow_steps_data_list(tmp_path, monkeypatch):
    """Regression for known issue 12: steps_data_list must be rebuilt, not appended."""
    model, _, _, _ = make_model(tmp_path, monkeypatch)
    assert len(model.steps_data_list) == len(StepType)

    for _ in range(3):
        model.apply_new_user_settings(user_settings=UserSettingsData())

    assert len(model.steps_data_list) == len(StepType)
    assert [step.step_type for step in model.steps_data_list] == list(StepType)


def volume_only_settings(volume: int) -> UserSettingsData:
    settings = UserSettingsData()
    settings.volume = volume
    return settings


def test_apply_volume_only_preserves_work_step_and_progress(tmp_path, monkeypatch):
    """Regression for known issue 13: Apply must not reset the step timer."""
    model, _, _, _ = make_model(tmp_path, monkeypatch)
    model.current_state.increase_elapsed_time(time_delta=datetime.timedelta(seconds=30))

    model.apply_new_user_settings(user_settings=volume_only_settings(volume=33))

    assert model.current_state.current_step_type == StepType.work_mode
    assert model.current_state.current_step_elapsed_time == datetime.timedelta(seconds=30)


def test_apply_volume_only_during_break_keeps_break_step(tmp_path, monkeypatch):
    model, _, _, _ = make_model(tmp_path, monkeypatch)
    model.set_step(new_step_type=StepType.break_mode)
    model.current_state.increase_elapsed_time(time_delta=datetime.timedelta(seconds=20))

    model.apply_new_user_settings(user_settings=volume_only_settings(volume=10))

    assert model.current_state.current_step_type == StepType.break_mode
    assert model.current_state.current_step_elapsed_time == datetime.timedelta(seconds=20)


def test_apply_volume_only_during_suspended_keeps_suspended_step(tmp_path, monkeypatch):
    model, _, _, _ = make_model(tmp_path, monkeypatch)
    model.set_step(new_step_type=StepType.suspended_mode)

    model.apply_new_user_settings(user_settings=volume_only_settings(volume=10))

    assert model.current_state.current_step_type == StepType.suspended_mode


def test_apply_enabling_protection_starts_work_step(tmp_path, monkeypatch):
    model, _, _, _ = make_model(tmp_path, monkeypatch, settings={'protection_status': 'off'})
    assert model.current_state.current_step_type == StepType.off_mode

    enabled = UserSettingsData()
    enabled.protection_status = 'on'
    model.apply_new_user_settings(user_settings=enabled)

    assert model.current_state.current_step_type == StepType.work_mode


def test_apply_disabling_protection_switches_to_off_step(tmp_path, monkeypatch):
    model, _, _, _ = make_model(tmp_path, monkeypatch)

    disabled = UserSettingsData()
    disabled.protection_status = 'off'
    model.apply_new_user_settings(user_settings=disabled)

    assert model.current_state.current_step_type == StepType.off_mode


def test_apply_shorter_work_duration_clamps_elapsed(tmp_path, monkeypatch):
    """Progress above the new duration must clamp: the step ends on the next tick."""
    model, _, _, _ = make_model(tmp_path, monkeypatch, settings={'work_duration': 5})
    model.current_state.increase_elapsed_time(time_delta=datetime.timedelta(seconds=240))

    shorter = UserSettingsData()
    shorter.work_duration = 1
    model.apply_new_user_settings(user_settings=shorter)

    assert model.current_state.current_step_duration == datetime.timedelta(seconds=0)
    assert model.current_state.current_step_remaining_time == datetime.timedelta(seconds=0)


def test_suspend_notification_shown_once(tmp_path, monkeypatch):
    """Regression for known issue 14: no duplicate suspend notification."""
    model, view, _, _ = make_model(tmp_path, monkeypatch)

    model.switch_suspended_state()

    suspended_notifications = sum('suspended' in message for message, _ in view.notifications)
    assert suspended_notifications == 1


def test_startup_runs_step_actions_once_per_transition(tmp_path, monkeypatch):
    """Regression for known issue 14: the startup work sound plays exactly once.

    With work_duration=1 the work step lasts zero seconds: the controller
    starts, the initial work actions run once, then the step ends and the
    transition to work_notified_1 must not replay the work sound.
    """
    import time as time_module

    from controller import Controller

    model, _, _, sounds = make_model(tmp_path, monkeypatch, settings={'work_duration': 1})
    controller = Controller()
    controller.set_model(model=model)
    controller.start()

    deadline = time_module.monotonic() + 5
    while model.current_state.current_step_type != StepType.work_notified_1 and time_module.monotonic() < deadline:
        time_module.sleep(0.01)
    controller.stop()

    assert model.current_state.current_step_type == StepType.work_notified_1
    assert sounds.work_plays == 1


def test_idle_restores_work_notified_1_with_remaining_time(tmp_path, monkeypatch):
    """Regression for known issue 21: idle must restore the saved work step.

    Entering idle from work_notified_1 with 15 seconds left: after activity
    returns the step is work_notified_1 again (not a fresh work_mode), with
    the same remaining time.
    """
    model, _, _, _ = make_model(
        tmp_path,
        monkeypatch,
        settings={'work_duration': 2, 'reset_work_time_in_idle': 'off'},
        inactive_reads=2,
    )
    model.set_step(new_step_type=StepType.work_notified_1)
    model.current_state.increase_elapsed_time(time_delta=datetime.timedelta(seconds=40))

    model.tick()
    assert model.current_state.current_step_type == StepType.iddle_mode

    model.tick()
    # the exiting tick counts one second: 15s saved minus this tick
    assert model.current_state.current_step_type == StepType.work_notified_1
    assert model.current_state.current_step_remaining_time == datetime.timedelta(seconds=14)


def test_idle_restores_work_mode_with_remaining_time(tmp_path, monkeypatch):
    model, _, _, _ = make_model(
        tmp_path,
        monkeypatch,
        settings={'work_duration': 2, 'reset_work_time_in_idle': 'off'},
        inactive_reads=2,
    )
    # work step for work_duration=2 is exactly 60 seconds
    model.current_state.increase_elapsed_time(time_delta=datetime.timedelta(seconds=10))

    model.tick()
    assert model.current_state.current_step_type == StepType.iddle_mode

    model.tick()
    # the exiting tick counts one second: 50s saved minus this tick
    assert model.current_state.current_step_type == StepType.work_mode
    assert model.current_state.current_step_remaining_time == datetime.timedelta(seconds=49)


def test_idle_restores_work_notified_2_with_remaining_time(tmp_path, monkeypatch):
    model, _, _, _ = make_model(
        tmp_path,
        monkeypatch,
        settings={'work_duration': 2, 'reset_work_time_in_idle': 'off'},
        inactive_reads=2,
    )
    model.set_step(new_step_type=StepType.work_notified_2)
    model.current_state.increase_elapsed_time(time_delta=datetime.timedelta(seconds=2))

    model.tick()
    assert model.current_state.current_step_type == StepType.iddle_mode

    model.tick()
    # the exiting tick counts one second: 3s saved minus this tick
    assert model.current_state.current_step_type == StepType.work_notified_2
    assert model.current_state.current_step_remaining_time == datetime.timedelta(seconds=2)


def test_idle_with_reset_starts_fresh_work_step(tmp_path, monkeypatch):
    model, _, _, _ = make_model(
        tmp_path,
        monkeypatch,
        settings={'work_duration': 2, 'reset_work_time_in_idle': 'on'},
        inactive_reads=2,
    )
    model.current_state.increase_elapsed_time(time_delta=datetime.timedelta(seconds=10))

    model.tick()
    assert model.current_state.current_step_type == StepType.iddle_mode

    model.tick()
    assert model.current_state.current_step_type == StepType.work_mode
    assert model.current_state.current_step_elapsed_time == datetime.timedelta(seconds=0)
    assert model.current_state.current_step_remaining_time == datetime.timedelta(seconds=60)
