"""Tests for the Controller command queue (single-writer threading model).

The Controller thread must be the only writer of the Model: UI threads only
submit commands, and commands are applied sequentially in the controller
thread (known issue 11).
"""

import threading

from config.states import StepType
from controller import Controller


class FakeSystemSettings:
    TIME_TICK_S = 0.01


class FakeSettings:
    system_settings = FakeSystemSettings()


class FakeModel:
    """Scriptable Model stub recording calls and their thread."""

    settings = FakeSettings()

    def __init__(self, ticks_until_end: int = 1):
        self.lock = threading.Lock()
        self.ticks_until_end = ticks_until_end
        self.calls: list[tuple[str, object]] = []
        self.step_applied = threading.Event()
        self.set_step_thread: int | None = None

    def record(self, name: str, value=None):
        with self.lock:
            self.calls.append((name, value))

    # Model API used by the Controller

    def do_current_step_actions(self):
        self.record('do_current_step_actions')

    def tick(self) -> bool:
        self.record('tick')
        with self.lock:
            self.ticks_until_end -= 1
            return self.ticks_until_end < 0

    def set_new_step_in_sequence(self):
        self.record('set_new_step_in_sequence')

    def set_step(self, new_step_type: StepType):
        self.record('set_step', new_step_type)
        self.set_step_thread = threading.get_ident()
        self.step_applied.set()

    def apply_new_user_settings(self, user_settings):
        self.record('apply_new_user_settings', user_settings)

    def switch_suspended_state(self):
        self.record('switch_suspended_state')


def test_set_step_command_applied_in_controller_thread():
    model = FakeModel()
    controller = Controller()
    controller.set_model(model)
    controller.start()

    controller.submit_set_step(StepType.break_mode)
    assert model.step_applied.wait(timeout=5)

    controller.stop_request.set()
    controller.thread_alg.join(timeout=5)

    assert model.set_step_thread != threading.get_ident()
    assert ('set_step', StepType.break_mode) in model.calls


def test_commands_processed_in_fifo_order():
    model = FakeModel()
    controller = Controller()
    controller.set_model(model)
    controller.start()

    controller.submit_set_step(StepType.break_mode)
    controller.submit_suspend()
    applied_two = threading.Event()

    original_switch = model.switch_suspended_state

    def switch_recorder():
        original_switch()
        applied_two.set()

    model.switch_suspended_state = switch_recorder
    assert applied_two.wait(timeout=5)

    controller.stop_request.set()
    controller.thread_alg.join(timeout=5)

    names = [name for name, _ in model.calls if name in ('set_step', 'switch_suspended_state')]
    assert names == ['set_step', 'switch_suspended_state']


def test_manual_break_survives_background_step_end():
    """Regression for known issue 11: a queued manual break must not be lost.

    The background step ends at the same moment the user presses "Take a
    break": the sequence transition happens first, then the queued command is
    applied — the manual break wins instead of being overwritten by the
    racing background writer.
    """
    model = FakeModel(ticks_until_end=0)  # step already ended
    controller = Controller()
    controller.set_model(model)
    controller.start()

    # let the controller run one full loop (do actions -> tick -> next step)
    sequence_done = threading.Event()

    original_sequence = model.set_new_step_in_sequence

    def sequence_recorder():
        original_sequence()
        sequence_done.set()

    model.set_new_step_in_sequence = sequence_recorder
    assert sequence_done.wait(timeout=5)

    controller.submit_set_step(StepType.break_mode)
    assert model.step_applied.wait(timeout=5)

    controller.stop_request.set()
    controller.thread_alg.join(timeout=5)

    # the racing background transition happened first, then the queued manual
    # break was applied after it — the command is not lost
    first_sequence_idx = model.calls.index(('set_new_step_in_sequence', None))
    break_idx = model.calls.index(('set_step', StepType.break_mode))
    assert break_idx > first_sequence_idx
