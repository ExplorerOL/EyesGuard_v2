import datetime
import time
from dataclasses import dataclass
from enum import IntEnum

from settings import Settings


class StepType(IntEnum):
    """Types of programm steps"""

    off = 0
    work_mode = 1
    work_notified = 2
    break_mode = 3
    break_notified = 4


@dataclass
class StepData:
    """Data for step control"""

    step_type: StepType = StepType.off
    step_duration_s: int = 0


class CurrentState:
    """Data about current step"""

    def __init__(self):
        self.__step_type: int = StepType.off
        self.__elapsed_time_s: datetime.timedelta = datetime.timedelta(seconds=0)

    def get_current_step(self) -> StepType:
        return self.__step_type

    def set_current_step(self, step_type: StepType):
        self.__step_type = step_type

    def get_elapsed_time(self):
        return self.__elapsed_time_s

    def increase_elapsed_time(self, time_delta: datetime.timedelta = datetime.timedelta(seconds=1)):
        self.__elapsed_time_s += time_delta


class ControlAlg:
    """Class for time and break control"""

    def __init__(self, settings: Settings, current_state: CurrentState):
        self.current_state = current_state
        step_notified_duration_s = 60

        self.steps: list[StepData] = []

        for step_type in StepType:
            self.steps.insert(step_type, StepData())
            self.steps[step_type].step_type = step_type

        print(self.steps)
        print(type(self.steps))

        user_settings = settings.get_settings()
        print(user_settings)
        print(StepType.work_mode)
        print(StepType.work_notified)

        self.steps[StepType.work_mode].step_duration_s = user_settings.work_duration * 60
        self.steps[StepType.work_notified].step_duration_s = step_notified_duration_s
        self.steps[StepType.break_mode].step_duration_s = user_settings.break_duration * 60
        self.steps[StepType.break_notified].step_duration_s = step_notified_duration_s

        print(self.steps)
        for step in self.steps:
            print(step.step_type)
            print(step.step_duration_s)

        if user_settings.protection_status == "off":
            self.current_state.set_current_step(StepType.off)
        else:
            self.current_state.set_current_step(StepType.work_mode)

        print(self.current_state)

    def start(self):
        self.main_loop()

    def stop(self):
        pass

    def main_loop(self):
        while True:
            for step in self.steps:
                print(f"Currents step: {step.step_type}")
                print(f"Elapsed time: {step.step_duration_s}")
                time.sleep(1000)
