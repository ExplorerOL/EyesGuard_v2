"""Tests for CurrentState and StepData domain objects."""

import datetime

from config.states import CurrentState, StepData, StepType


def test_initial_current_state_defaults():
    current_state = CurrentState()

    assert current_state.current_step_type == StepType.work_mode
    assert current_state.current_step_duration == datetime.timedelta(seconds=0)
    assert current_state.current_step_elapsed_time == datetime.timedelta(seconds=0)
    assert current_state.current_step_remaining_time == datetime.timedelta(seconds=0)
    assert current_state.suspended_mode_active is False


def test_set_current_step_data_updates_type_and_duration():
    current_state = CurrentState()

    current_state.set_current_step_data(step_type=StepType.break_mode, step_duration=datetime.timedelta(minutes=15))

    assert current_state.current_step_type == StepType.break_mode
    assert current_state.current_step_duration == datetime.timedelta(minutes=15)
    assert current_state.current_step_remaining_time == datetime.timedelta(minutes=15)


def test_increase_elapsed_time_default_tick():
    current_state = CurrentState()
    current_state.set_current_step_data(step_type=StepType.work_mode, step_duration=datetime.timedelta(seconds=10))

    current_state.increase_elapsed_time()
    current_state.increase_elapsed_time()

    assert current_state.current_step_elapsed_time == datetime.timedelta(seconds=2)
    assert current_state.current_step_remaining_time == datetime.timedelta(seconds=8)


def test_increase_elapsed_time_custom_delta():
    current_state = CurrentState()

    current_state.increase_elapsed_time(time_delta=datetime.timedelta(seconds=30))

    assert current_state.current_step_elapsed_time == datetime.timedelta(seconds=30)


def test_reset_elapsed_time():
    current_state = CurrentState()
    current_state.increase_elapsed_time(time_delta=datetime.timedelta(seconds=30))

    current_state.reset_elapsed_time()

    assert current_state.current_step_elapsed_time == datetime.timedelta(seconds=0)


def test_step_data_defaults():
    step_data = StepData()

    assert step_data.step_type == StepType.off_mode
    assert step_data.step_duration_td == datetime.timedelta(seconds=0)


def test_step_type_is_int_enum_with_sequential_values():
    assert [step.value for step in StepType] == [0, 1, 2, 3, 4, 5, 6]
    assert StepType.break_mode == 5
