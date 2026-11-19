"""Controller: time and break control, the single writer of the Model.

UI threads (Tk callbacks, tray callbacks) never mutate the Model directly:
they submit commands to the queue, and only the controller thread applies
them (known issue 11).
"""

import queue
import threading
from dataclasses import dataclass

from config.settings import UserSettingsData
from config.states import StepType
from model import Model
from support.logger import logger


@dataclass(frozen=True)
class SetStepCommand:
    """Switch the model to the given step."""

    step_type: StepType


@dataclass(frozen=True)
class ApplySettingsCommand:
    """Apply and persist new user settings."""

    user_settings: UserSettingsData


@dataclass(frozen=True)
class SuspendCommand:
    """Toggle the suspended state."""

    pass


UICommand = SetStepCommand | ApplySettingsCommand | SuspendCommand


class Controller:
    """Class for time and break control."""

    def __init__(self):
        logger.trace('Controller: object was created')
        self.model: Model
        self.thread_alg: threading.Thread | None = None
        self.__commands: queue.Queue[UICommand] = queue.Queue()
        self.__wake = threading.Event()
        self.stop_request = threading.Event()

    def set_model(self, model: Model):
        """Assigning model to controller."""
        logger.trace('Controller: set_model')
        self.model = model
        self.thread_alg = None

    def start(self):
        """Start controller in separated thread."""
        if self.thread_alg is None:
            self.thread_alg = threading.Thread(target=self.main_loop, name='Controller')
            self.thread_alg.start()

    def stop(self):
        pass

    def submit_set_step(self, step_type: StepType) -> None:
        """Queue a step switch (safe to call from UI threads)."""
        self.__submit(SetStepCommand(step_type=step_type))

    def submit_apply_settings(self, user_settings: UserSettingsData) -> None:
        """Queue applying new settings (safe to call from UI threads)."""
        self.__submit(ApplySettingsCommand(user_settings=user_settings))

    def submit_suspend(self) -> None:
        """Queue toggling the suspended state (safe to call from UI threads)."""
        self.__submit(SuspendCommand())

    def __submit(self, command: UICommand) -> None:
        logger.trace(f'Controller: __submit {type(command).__name__}')
        self.__commands.put(command)
        self.__wake.set()

    def __process_commands(self) -> None:
        """Apply all queued commands; runs in the controller thread only."""
        while True:
            try:
                command = self.__commands.get_nowait()
            except queue.Empty:
                return
            logger.trace(f'Controller: applying {type(command).__name__}')
            match command:
                case SetStepCommand(step_type=step_type):
                    self.model.set_step(step_type)
                case ApplySettingsCommand(user_settings=user_settings):
                    self.model.apply_new_user_settings(user_settings)
                case SuspendCommand():
                    self.model.switch_suspended_state()

    def main_loop(self):
        """Controller main loop in separated thread."""
        logger.trace('Controller: main_loop')
        while not self.stop_request.is_set():
            self.__process_commands()
            self.model.do_current_step_actions()
            while not self.model.tick():
                if self.stop_request.is_set():
                    return
                # pacing sleep is interruptible: a submitted command wakes the loop at once
                self.__wake.wait(timeout=self.model.settings.system_settings.TIME_TICK_S)
                self.__wake.clear()
                self.__process_commands()
            self.model.set_new_step_in_sequence()
