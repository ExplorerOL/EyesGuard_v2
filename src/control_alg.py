import datetime
import time
from dataclasses import dataclass
from enum import IntEnum
from threading import Thread, Timer

from settings import Settings
from windows.break_wnd import BreakWnd


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
    step_duration_dt: int = 0


class CurrentState:
    """Data about current step"""

    def __init__(self, settings: Settings):
        self.__step_type: int = StepType.off
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

    def get_step_duration(self):
        return self.__step_duration_dt

    def get_step_elapsed_time(self):
        return self.__elapsed_time_dt

    def increase_elapsed_time(self, time_delta: datetime.timedelta = datetime.timedelta(seconds=1)):
        self.__elapsed_time_dt += time_delta

    def reset_elapsed_time(self):
        self.__elapsed_time_dt = datetime.timedelta(seconds=0)


class ControlAlg:
    """Class for time and break control"""

    def __init__(self, settings: Settings, current_state: CurrentState, break_wnd: BreakWnd):
        self.current_state = current_state
        self.break_wnd = break_wnd
        step_notified_duration_s = 5

        self.steps: list[StepData] = []

        for step_type in StepType:
            self.steps.insert(step_type, StepData())
            self.steps[step_type].step_type = step_type

        print(self.steps)
        print(type(self.steps))

        self.settings = settings
        self.user_settings = settings.get_settings()
        print(self.user_settings)
        print(StepType.work_mode)
        print(StepType.work_notified)

        self.steps[StepType.work_mode].step_duration_dt = datetime.timedelta(seconds=15)
        self.steps[StepType.work_notified].step_duration_dt = datetime.timedelta(
            seconds=step_notified_duration_s
        )
        self.steps[StepType.break_mode].step_duration_dt = datetime.timedelta(seconds=15)
        self.steps[StepType.break_notified].step_duration_dt = datetime.timedelta(
            seconds=step_notified_duration_s
        )

        print(self.steps)
        for step in self.steps:
            print(step.step_type)
            print(step.step_duration_dt)

        if self.user_settings.protection_status == "off":
            self.current_state.set_current_step(StepType.off, datetime.timedelta(seconds=0))
        else:
            self.current_state.set_current_step(
                StepType.work_mode, self.steps[StepType.break_mode].step_duration_dt
            )

        print(self.current_state)

    def start(self):
        thread_alg = Thread(target=self.main_loop)
        thread_alg.start()

    def stop(self):
        pass

    def main_loop(self):
        while True:
            if self.settings.get_settings().protection_status == "off":
                break
            for step in self.steps:
                print(f"Current step data: {step}, {step.step_type}, {step.step_duration_dt}")
                # exit from cycle if protection is off
                if self.settings.get_settings().protection_status == "off":
                    break

                if step.step_type == StepType.off:
                    continue

                self.step_actions(step, step.step_duration_dt)
                self.wait_for_step_is_ended(step)
                # skip cycle if step is off
                # print(f"Currents step: {step.step_type}")
                # print(f"Step duration: {step.step_duration_dt}")

    def wait_for_step_is_ended(self, step: StepData):
        while True:
            print(f"Currents step: {step.step_type}")
            print(f"Step duration: {self.current_state.get_step_duration()}")
            print(f"Step elapsed time: {self.current_state.get_step_elapsed_time()}")
            if self.current_state.get_step_elapsed_time() < self.current_state.get_step_duration():
                self.current_state.increase_elapsed_time()
            else:
                break

            time.sleep(1)

    def step_actions(self, next_step: StepData, duration: datetime.timedelta):
        self.current_state.reset_elapsed_time()
        self.current_state.set_current_step(step_type=next_step.step_type, step_duration=duration)
        print(f"new current step {(self.current_state.get_current_step_type())}")
        print(f"Type {type(self.current_state.get_current_step_type())}")

        if self.current_state.get_current_step_type() == StepType.break_mode:
            print("Control_alg: showing break window")
            self.break_wnd.show()
        if self.current_state.get_current_step_type() == StepType.work_mode:
            print("Control_alg: hiding break window")
            self.break_wnd.hide()
