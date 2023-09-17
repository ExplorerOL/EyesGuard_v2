import datetime
import time
from dataclasses import dataclass
from enum import IntEnum
from threading import Thread, Timer

from settings import Settings
from states import CurrentState, StepData, StepType
from windows.main_wnd import MainWnd


class ControlAlg:
    """Class for time and break control"""

    def __init__(self, settings: Settings, current_state: CurrentState, app: MainWnd):
        self.current_state = current_state
        self.app = app
        self.break_wnd = app.break_wnd
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
        # self.steps[StepType.break_notified].step_duration_dt = datetime.timedelta(
        #     seconds=step_notified_duration_s
        # )

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

            if self.current_state.get_current_step_type() == StepType.break_mode:
                self.break_wnd.set_lbl_remaining_time_text(self.current_state.get_step_remaining_time())
            #     self.break_wnd.pbar_break_progress.set(
            #         self.current_state.get_step_elapsed_time().seconds
            #         / self.current_state.get_step_duration().seconds
            #     )

            time.sleep(1)

    def step_actions(self, next_step: StepData, duration: datetime.timedelta):
        self.current_state.reset_elapsed_time()
        self.current_state.set_current_step(step_type=next_step.step_type, step_duration=duration)
        self.current_state.set_current_step(step_type=next_step.step_type, step_duration=duration)
        print(f"new current step {(self.current_state.get_current_step_type())}")
        print(f"Type {type(self.current_state.get_current_step_type())}")

        if self.current_state.get_current_step_type() == StepType.break_mode:
            print("Control_alg: showing break window")
            self.break_wnd.show()
        if self.current_state.get_current_step_type() == StepType.work_mode:
            print("Control_alg: hiding break window")
            self.break_wnd.hide()
        if self.current_state.get_current_step_type() == StepType.work_notified:
            print("Control_alg: showing working notification")
            self.app.show_notification("Attention!", "Break will start in 1 minute!")
            time.sleep(5)
