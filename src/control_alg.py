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


@dataclass
class CurrentStep:
    """Data about current step"""

    index: int = 0
    elapsed_time_s: int = 0


class ControlAlg:
    """Class for time and break control"""

    def __init__(self, settings: Settings):
        step_notified_duration_s = 60

        self.steps: list[StepData] = []

        for step_type in StepType:
            self.steps.insert(step_type, StepData())
            self.steps[step_type].step_type = step_type

        print(self.steps)
        print(type(self.steps))

        user_settings = settings.read()
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

        self.current_step = CurrentStep()
        if user_settings.protection_status == "off":
            self.current_step.index = 0
        else:
            self.current_step.index = 1

        print(self.current_step)
