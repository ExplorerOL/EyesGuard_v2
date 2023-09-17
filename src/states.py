import datetime
from dataclasses import dataclass
from enum import IntEnum

from settings import Settings


class StepType(IntEnum):
    """Types of programm steps"""

    off = 0
    work_mode = 1
    work_notified_1 = 2
    work_notified_2 = 3
    break_mode = 4
    # break_notified = 4


@dataclass
class StepData:
    """Data for step control"""

    step_type: StepType = StepType.off
    step_duration_td: datetime.timedelta = datetime.timedelta(seconds=0)


class CurrentState:
    """Data about current step"""

    def __init__(self, settings: Settings):
        self.__step_type: StepType = StepType.off
        self.__step_duration_dt: datetime.timedelta = datetime.timedelta(seconds=0)
        self.__elapsed_time_dt: datetime.timedelta = datetime.timedelta(seconds=0)

        user_settings = settings.get_settings()
        if user_settings.protection_status == "on":
            self.__step_type = StepType.work_mode
            self.__step_duration_dt = datetime.timedelta(minutes=user_settings.work_duration)
        print(f"Init current state: {self}")

    def __self_to_dict(self) -> dict:
        # convertation object to dict
        self_dict = {
            "__step_type:": self.__step_type,
            "__step_duration_dt": self.__step_duration_dt,
            "__elapsed_time_dt": self.__elapsed_time_dt,
        }
        return self_dict

    def __repr__(self) -> dict:
        # convertation object to dict
        return self.__self_to_dict()

    def __str__(self) -> str:
        # convertation object to string
        return str(self.__self_to_dict())

    def get_current_step_type(self) -> StepType:
        return self.__step_type

    def set_current_step(self, step_type: StepType, step_duration: datetime.timedelta):
        self.__step_type = step_type
        self.__step_duration_dt = step_duration
        self.__elapsed_time_dt = datetime.timedelta(seconds=0)

    def get_step_duration(self):
        return self.__step_duration_dt

    def get_step_elapsed_time(self):
        return self.__elapsed_time_dt

    def get_step_remaining_time(self):
        return self.__step_duration_dt - self.__elapsed_time_dt

    def increase_elapsed_time(self, time_delta: datetime.timedelta = datetime.timedelta(seconds=1)):
        self.__elapsed_time_dt += time_delta

    def reset_elapsed_time(self):
        self.__elapsed_time_dt = datetime.timedelta(seconds=0)
