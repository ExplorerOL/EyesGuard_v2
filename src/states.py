import datetime
from dataclasses import dataclass
from enum import IntEnum

from logger import logger


class StepType(IntEnum):
    """Types of programm steps"""

    off_mode = 0
    suspended_mode = 1
    work_mode = 2
    work_notified_1 = 3
    work_notified_2 = 4
    break_mode = 5
    # break_notified = 4


@dataclass
class StepData:
    """Data for step control"""

    step_type: StepType = StepType.off_mode
    step_duration_td: datetime.timedelta = datetime.timedelta(seconds=0)


class CurrentState:
    """Data about current step"""

    def __init__(self):
        self.__step_type: StepType = StepType.work_mode

        self.__step_duration_dt: datetime.timedelta = datetime.timedelta(seconds=0)
        self.__elapsed_time_dt: datetime.timedelta = datetime.timedelta(seconds=0)
        self.__suspended_mode_active: bool = False

        logger.debug(f"Init current state: {self}")

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

    @property
    def current_step_type(self) -> StepType:
        return self.__step_type

    @property
    def current_step_duration(self):
        return self.__step_duration_dt

    @property
    def current_step_elapsed_time(self):
        return self.__elapsed_time_dt

    @property
    def current_step_remaining_time(self) -> datetime.timedelta:
        return self.__step_duration_dt - self.__elapsed_time_dt

    @property
    def suspended_mode_active(self) -> bool:
        return self.__suspended_mode_active

    def set_current_step_data(
        self, step_type: StepType, step_duration: datetime.timedelta = datetime.timedelta(seconds=0)
    ):
        """Setting current step type and its duration"""
        logger.trace("CurrentState: set_current_step_data")
        self.__step_type = step_type
        self.__step_duration_dt = step_duration
        logger.debug(f"__step_type = {self.__step_type}")
        logger.debug(f"__step_duration_dt = {self.__step_duration_dt}")
        logger.debug(f"__elapsed_time_dt = {self.__elapsed_time_dt}")

    def increase_elapsed_time(self, time_delta: datetime.timedelta = datetime.timedelta(seconds=1)):
        logger.trace("CurrentState: increase_elapsed_time")
        self.__elapsed_time_dt += time_delta
        logger.debug(f"__elapsed_time_dt: {self.__elapsed_time_dt}")

    def reset_elapsed_time(self):
        self.__elapsed_time_dt = datetime.timedelta(seconds=0)
