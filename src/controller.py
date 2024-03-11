import datetime
import time
from threading import Thread

from model import EGModel
from states import StepData, StepType

# from view import EGView


class EGController:
    """Class for time and break control"""

    def __init__(self, model: EGModel):

        # self.model = None
        self.model = model
        # self.view = view
        # self.view.init_all_views(self.model)

        # self.break_wnd = view.wnd_break

        self.user_settings = self.model.settings.get_settings_copy()
        print(f"User settings: = {self.user_settings}")

        self.steps_data_list: list[StepData] = []

        for step_type in StepType:
            self.steps_data_list.insert(step_type, StepData())
            self.steps_data_list[step_type].step_type = step_type
        self.__update_alg_settings()

        print(self.steps_data_list)
        for step in self.steps_data_list:
            print(f"{step.step_type=}")
            print(step.step_duration_td)

        print(self.model.current_state)

        self.thread_alg = None

    def set_model(self, model: EGModel):
        """Assigning model to controller"""
        self.model = model

    def start(self):
        """Start controller"""
        self.__update_alg_settings()
        if self.thread_alg is None:
            self.thread_alg = Thread(target=self.main_loop)
            self.thread_alg.start()

    def stop(self):
        pass

    def main_loop(self):
        while True:
            self._do_current_step_actions()
            self._wait_for_current_step_is_ended()
            self._set_new_step_in_sequence()

    def _wait_for_current_step_is_ended(self):
        while True:
            # print info
            print(f"Currents step type: {self.model.current_state.get_current_step_type()}")
            print(f"Step duration: {self.model.current_state.get_current_step_duration()}")
            print(f"Step elapsed time: {self.model.current_state.get_step_elapsed_time()}")
            self._change_step_if_protection_mode_was_changed()

            if (
                self.model.current_state.get_step_elapsed_time()
                < self.model.current_state.get_current_step_duration()
            ):
                self.model.current_state.increase_elapsed_time()
                # self._update_time_until_break()
            else:
                break

            # actions during step is in progress
            match self.model.current_state.get_current_step_type():
                case StepType.break_mode:
                    pass
                    # self.break_wnd.set_lbl_remaining_time_text(
                    #     self.model.current_state.get_step_remaining_time()
                    # )

            # TODO - case for updating time
            # case StepType.work_notified_1:
            #     remaining_time_actual = (
            #         self.model.current_state.get_step_remaining_time()
            #         + self.steps_data_list[StepType.work_notified_2].step_duration_td
            #     )

            # case StepType.work_notified_2:
            #     remaining_time_actual = self.model.current_state.get_step_remaining_time()

            # case StepType.work_mode:
            #     remaining_time_actual = (
            #         self.model.current_state.get_step_remaining_time()
            #         + self.steps_data_list[StepType.work_notified_1].step_duration_td
            #         + self.steps_data_list[StepType.work_notified_2].step_duration_td
            #     )
            self.__update_time_until_break()
            self.__update_alg_settings()
            time.sleep(1)

    def __update_time_until_break(self):
        """Updating time until break info"""

        remaining_time_actual: datetime.timedelta = self.model.current_state.get_step_remaining_time()
        remaining_time_for_work_full = (
            self.steps_data_list[StepType.work_mode].step_duration_td
            + self.steps_data_list[StepType.work_notified_1].step_duration_td
            + self.steps_data_list[StepType.work_notified_2].step_duration_td
        )
        print(remaining_time_actual)
        match self.model.current_state.get_current_step_type():
            case StepType.off_mode:
                remaining_time_actual += self.steps_data_list[StepType.work_mode].step_duration_td
                remaining_time_for_work_full = (
                    self.steps_data_list[StepType.off_mode].step_duration_td
                    + self.steps_data_list[StepType.work_mode].step_duration_td
                    + self.steps_data_list[StepType.work_notified_1].step_duration_td
                    + self.steps_data_list[StepType.work_notified_2].step_duration_td
                )
            case StepType.work_mode:
                remaining_time_actual += (
                    self.steps_data_list[StepType.work_notified_1].step_duration_td
                    + self.steps_data_list[StepType.work_notified_2].step_duration_td
                )
            case StepType.work_notified_1:
                remaining_time_actual += self.steps_data_list[StepType.work_notified_2].step_duration_td

        print("Updating time")

        time_until_break_tooltip_string = "Time until break: " + f"{remaining_time_actual}"

        # self.view.tray_icon.title = time_until_break_tooltip_string
        # self.view.wnd_status.lbl_time_until_break.configure(text=time_until_break_tooltip_string)
        # self.view.wnd_status.pbar_time_until_break.set(
        #     1 - remaining_time_actual / remaining_time_for_work_full
        # )

    def _change_step_if_protection_mode_was_changed(self):
        if (
            self.model.settings.user_settings.protection_status == "off"
            and self.model.current_state.get_current_step_type() != StepType.off_mode
        ):
            self._set_current_step(step_type=StepType.off_mode)
            # self.view.wnd_settings.update()

        if (
            self.model.settings.user_settings.protection_status == "on"
            and self.model.current_state.get_current_step_type() == StepType.off_mode
        ):
            self._set_current_step(step_type=StepType.work_mode)
            # self.view.wnd_settings.update()

    def _do_current_step_actions(self):
        self.model.current_state.reset_elapsed_time()
        print(f"New current step {(self.model.current_state.get_current_step_type())}")
        print(f"Type {type(self.model.current_state.get_current_step_type())}")

        match self.model.current_state.get_current_step_type():
            case StepType.off_mode:
                print("Control_alg: showing off mode notification")
                # self.view.show_notification("Eyes Guard is in suspended mode!", "Attention!")

            case StepType.break_mode:
                print("Control_alg: showing break window")
                # self.break_wnd.show()

            case StepType.work_notified_1:
                if self.user_settings.notifications == "on":
                    print("Control_alg: showing working notification 1")
                    # self.view.show_notification("Break will start in 1 minute!", "Attention!")

            case StepType.work_notified_2:
                if self.user_settings.notifications == "on":
                    print("Control_alg: showing working notification 2")
                    # self.view.show_notification("Break will start in 5 seconds!", "Attention!")

            case StepType.work_mode:
                print("Control_alg: hiding break window")
                # self.break_wnd.hide()

    def __update_alg_settings(self):
        self.user_settings = self.model.settings.user_settings
        print(self.user_settings)

        #  обернуть в функцию
        # step_work_duration = datetime.timedelta(minutes=self.user_settings.work_duration)
        # if step_work_duration > self.step_notification_1_time_td + self.step_notification_2_time_td:
        #     print(
        #         f"cond 1 {step_work_duration}  {self.step_notification_1_time_td + self.step_notification_2_time_td}"
        #     )
        #     self.steps_data_list[StepType.work_mode].step_duration_td = (
        #         step_work_duration - self.step_notification_1_time_td - self.step_notification_2_time_td
        #     )
        #     self.steps_data_list[StepType.work_notified_1].step_duration_td = self.step_notification_1_time_td
        # else:
        #     self.steps_data_list[StepType.work_mode].step_duration_td = (
        #         step_work_duration - self.step_notification_2_time_td
        #     )
        #     self.steps_data_list[StepType.work_notified_1].step_duration_td = datetime.timedelta(seconds=0)
        # self.steps_data_list[StepType.break_mode].step_duration_td = datetime.timedelta(
        #     minutes=self.user_settings.break_duration
        # )

        # setting steps durations
        # setting steps durations
        self.step_off_duration_td = self.model.settings.system_settings.step_off_mode_duration
        self.step_work_duration_td = datetime.timedelta(
            minutes=self.model.settings.user_settings.work_duration
        )
        self.step_break_duration = datetime.timedelta(
            minutes=self.model.settings.user_settings.break_duration
        )
        self.step_notification_1_time_td = self.model.settings.system_settings.step_notification_1_duration
        self.step_notification_2_time_td = self.model.settings.system_settings.step_notification_2_duration
        print(f"step_work_duration_td {self.step_work_duration_td}")

        self.steps_data_list[StepType.off_mode].step_duration_td = self.step_off_duration_td
        if self.step_work_duration_td > self.step_notification_1_time_td + self.step_notification_2_time_td:
            print(
                f"cond 1 {self.step_work_duration_td}  {self.step_notification_1_time_td + self.step_notification_2_time_td}"
            )
            self.steps_data_list[StepType.work_mode].step_duration_td = (
                self.step_work_duration_td
                - self.step_notification_1_time_td
                - self.step_notification_2_time_td
            )
            # self.steps_data_list[StepType.work_notified_1].step_duration_td = self.step_notification_1_time_td
        else:
            self.steps_data_list[StepType.work_mode].step_duration_td = datetime.timedelta(seconds=0)
        self.steps_data_list[StepType.work_notified_1].step_duration_td = self.step_notification_1_time_td
        self.steps_data_list[StepType.work_notified_2].step_duration_td = self.step_notification_2_time_td
        self.steps_data_list[StepType.break_mode].step_duration_td = self.step_break_duration

        # settings autorefresh not working
        self.__update_current_state()

    def __update_current_state(self):
        current_step = self.model.current_state.get_current_step_type()
        self.model.current_state.set_current_step_data(
            step_type=current_step, step_duration=self.steps_data_list[current_step].step_duration_td
        )
        # if (
        #     self.model.current_state.get_current_step_duration
        #     != self.steps_data_list[current_step].step_duration_td
        # ):
        #     self.model.current_state.set_current_step_data(
        #         step_type=current_step, step_duration=self.steps_data_list[current_step].step_duration_td
        #     )

    def _set_new_step_in_sequence(self):
        current_step_type = self.model.current_state.get_current_step_type()

        # steps transitions
        match current_step_type:
            case StepType.off_mode:
                new_step_type = StepType.work_mode
            case StepType.work_mode:
                new_step_type = StepType.work_notified_1
            case StepType.work_notified_1:
                new_step_type = StepType.work_notified_2
            case StepType.work_notified_2:
                new_step_type = StepType.break_mode
            case StepType.break_mode:
                new_step_type = StepType.work_mode

        self._set_current_step(new_step_type)

    def _set_current_step(self, step_type: StepType) -> None:
        """settind step data in current state by step type"""

        self.model.current_state.set_current_step_data(
            step_type=step_type, step_duration=self.steps_data_list[step_type].step_duration_td
        )
