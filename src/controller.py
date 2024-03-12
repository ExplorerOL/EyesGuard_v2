import datetime
import time
from threading import Thread

from logger import logger
from model import EGModel
from states import StepData, StepType

# from view import EGView


class EGController:
    """Class for time and break control"""

    def __init__(self):
        logger.trace("Controller: object was created")

    def set_model(self, model: EGModel):
        """Assigning model to controller"""
        self.model = model
        self.thread_alg = None
        logger.trace("Controller: model was set")

    def start(self):
        """Start controller"""
        self.__update_model_settings()
        if self.thread_alg is None:
            self.thread_alg = Thread(target=self.main_loop)
            self.thread_alg.start()

    def stop(self):
        pass

    def main_loop(self):
        """Controller main loop in separated thread"""

        logger.trace("Controller: main loop started")
        while True:
            self.__do_current_step_actions()
            self.__wait_for_current_step_is_ended()
            self.__set_new_step_in_sequence()

    def __wait_for_current_step_is_ended(self):
        while True:
            # print info
            logger.info(f"Current step type: {self.model.current_state.current_step_type}")
            logger.info(f"Step duration: {self.model.current_state.current_step_duration}")
            logger.info(f"Step elapsed time: {self.model.current_state.current_step_elapsed_time}")
            # self._change_step_if_protection_mode_was_changed()
            time.sleep(1)

            # if (
            #     self.model.current_state.current_step_elapsed_time()
            #     < self.model.current_state.current_step_duration()
            # ):
            #     self.model.current_state.increase_elapsed_time()
            #     # self._update_time_until_break()
            # else:
            #     break

            # # actions during step is in progress
            # match self.model.current_state.current_step_type():
            #     case StepType.break_mode:
            #         pass
            #         # self.break_wnd.set_lbl_remaining_time_text(
            #         #     self.model.current_state.get_step_remaining_time()
            #         # )

            # # TODO - case for updating time
            # # case StepType.work_notified_1:
            # #     remaining_time_actual = (
            # #         self.model.current_state.get_step_remaining_time()
            # #         + self.steps_data_list[StepType.work_notified_2].step_duration_td
            # #     )

            # # case StepType.work_notified_2:
            # #     remaining_time_actual = self.model.current_state.get_step_remaining_time()

            # # case StepType.work_mode:
            # #     remaining_time_actual = (
            # #         self.model.current_state.get_step_remaining_time()
            # #         + self.steps_data_list[StepType.work_notified_1].step_duration_td
            # #         + self.steps_data_list[StepType.work_notified_2].step_duration_td
            # #     )
            # self.__update_time_until_break()
            # self.__update_model_settings()
            # time.sleep(1)

    def __update_time_until_break(self):
        """Updating time until break info"""

        remaining_time_actual: datetime.timedelta = self.model.current_state.get_step_remaining_time()
        remaining_time_for_work_full = (
            self.steps_data_list[StepType.work_mode].step_duration_td
            + self.steps_data_list[StepType.work_notified_1].step_duration_td
            + self.steps_data_list[StepType.work_notified_2].step_duration_td
        )
        print(remaining_time_actual)
        match self.model.current_state.current_step_type():
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

    def __change_step_if_protection_mode_was_changed(self):
        print("_change_step_if_protection_mode_was_changed")
        # if (
        #     self.model.set_model.user_settings.protection_status == "off"
        #     and self.model.current_state.current_step_type() != StepType.off_mode
        # ):
        #     self._set_current_step(step_type=StepType.off_mode)
        #     # self.view.wnd_settings.update()

        # if (
        #     self.model.set_model.user_settings.protection_status == "on"
        #     and self.model.current_state.current_step_type() == StepType.off_mode
        # ):
        #     self._set_current_step(step_type=StepType.work_mode)

    def __do_current_step_actions(self):
        print("__do_current_step_actions")
        # self.model.current_state.reset_elapsed_time()
        # print(f"New current step {(self.model.current_state.current_step_type())}")
        # print(f"Type {type(self.model.current_state.current_step_type())}")

        # match self.model.current_state.current_step_type():
        #     case StepType.off_mode:
        #         print("Control_alg: showing off mode notification")
        #         # self.view.show_notification("Eyes Guard is in suspended mode!", "Attention!")

        #     case StepType.break_mode:
        #         print("Control_alg: showing break window")
        #         # self.break_wnd.show()

        #     case StepType.work_notified_1:
        #         if self.model.set_model.user_settings.notifications == "on":
        #             print("Control_alg: showing working notification 1")
        #             # self.view.show_notification("Break will start in 1 minute!", "Attention!")

        #     case StepType.work_notified_2:
        #         if self.model.set_model.user_settings.notifications == "on":
        #             print("Control_alg: showing working notification 2")
        #             # self.view.show_notification("Break will start in 5 seconds!", "Attention!")

        #     case StepType.work_mode:
        #         print("Control_alg: hiding break window")
        #         # self.break_wnd.hide()

    def __update_model_settings(self):
        print("__update_model_settings")
        # self.model.settings.user_settings = self.model.settings.user_settings
        # self.model.(self.model)
        # print(self.model.set_model.user_settings)

        # settings autorefresh not working

        # self.__update_current_state()

    def __update_current_state(self):
        print("__update_current_state")

        # current_step = self.model.current_state.current_step_type
        # self.model.current_state.set_current_step_data(
        #     step_type=current_step, step_duration=self.steps_data_list[current_step].step_duration_td
        # )
        # if (
        #     self.model.current_state.get_current_step_duration
        #     != self.steps_data_list[current_step].step_duration_td
        # ):
        #     self.model.current_state.set_current_step_data(
        #         step_type=current_step, step_duration=self.steps_data_list[current_step].step_duration_td
        #     )

    def __set_new_step_in_sequence(self):
        print("_set_new_step_in_sequence")

        # current_step_type = self.model.current_state.current_step_type()

        # # steps transitions
        # match current_step_type:
        #     case StepType.off_mode:
        #         new_step_type = StepType.work_mode
        #     case StepType.work_mode:
        #         new_step_type = StepType.work_notified_1
        #     case StepType.work_notified_1:
        #         new_step_type = StepType.work_notified_2
        #     case StepType.work_notified_2:
        #         new_step_type = StepType.break_mode
        #     case StepType.break_mode:
        #         new_step_type = StepType.work_mode

        # self._set_current_step(new_step_type)

    def _set_current_step(self, step_type: StepType) -> None:
        """settind step data in current state by step type"""

        self.model.current_state.set_current_step_data(
            step_type=step_type, step_duration=self.steps_data_list[step_type].step_duration_td
        )
