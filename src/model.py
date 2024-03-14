# For preventing circular import
# https://stackoverflow.com/questions/744373/what-happens-when-using-mutual-or-circular-cyclic-imports/67673741#67673741
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view import EGView

import datetime
import time

from logger import logger
from settings import Settings, UserSettingsData
from states import CurrentState, StepData, StepType

SETTINGS_FILE = "./settings/settings.json"


class EGModel:
    def __init__(self, settings_file: str = SETTINGS_FILE):
        self.view: EGView | None = None
        self.settings = Settings(settings_file)
        self.current_state = CurrentState(self.settings)

        logger.info(f"User settings: = {self.settings.user_settings}")

        self.steps_data_list: list[StepData] = []

        for step_type in StepType:
            self.steps_data_list.insert(step_type, StepData())
            self.steps_data_list[step_type].step_type = step_type

        # setting steps durations
        self.step_off_duration_td = self.settings.system_settings.step_off_mode_duration
        self.step_work_duration_td = datetime.timedelta(minutes=self.settings.user_settings.work_duration)
        self.step_break_duration_td = datetime.timedelta(minutes=self.settings.user_settings.break_duration)
        self.step_notification_1_time_td = self.settings.system_settings.step_notification_1_duration
        self.step_notification_2_time_td = self.settings.system_settings.step_notification_2_duration
        logger.info(f"step_work_duration_td {self.step_work_duration_td}")

        self.steps_data_list[StepType.off_mode].step_duration_td = self.step_off_duration_td
        if self.step_work_duration_td > self.step_notification_1_time_td + self.step_notification_2_time_td:
            logger.info(
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
        self.steps_data_list[StepType.break_mode].step_duration_td = self.step_break_duration_td

        logger.info(self.steps_data_list)
        for step in self.steps_data_list:
            logger.info(f"{step.step_type=}")
            logger.info(step.step_duration_td)

        logger.info(self.current_state)

        logger.trace("EGModel: object was created")

    def set_view(self, view: EGView) -> None:
        """Assigning controller to view"""
        logger.trace("EGModel: set_view started")

        # import placed here for breaking circular import
        # from view import EGView

        self.view = view
        self.__init_view()

    @property
    def model(self) -> EGModel:
        logger.trace("EGModel: getting model data")
        return self

    @property
    def model_settings(self) -> Settings:
        logger.trace("EGModel: getting settings")
        return self.settings

    @model_settings.setter
    def model_settings(self, settings: Settings) -> None:
        logger.trace("EGModel: saving new settings")

    @property
    def model_user_settings(self) -> UserSettingsData:
        logger.trace("EGModel: getting user settings")
        return self.settings.user_settings

    @model_user_settings.setter
    def model_user_settings(self, user_settings: UserSettingsData) -> None:
        logger.trace("EGModel: saving new settings")
        self.settings.apply_settings_from_ui(user_settings)

    def __init_view(self):
        """View initialization with model data"""
        logger.trace("EGModel: __init_view function started")
        if self.view is not None:
            self.view.init_all_views(self.model)

    def do_current_step_actions(self):
        logger.trace("EGModel: __do_current_step_actions")
        self.model.current_state.reset_elapsed_time()
        logger.debug(f"New current step {(self.current_state.current_step_type)}")
        logger.debug(f"New step type {type(self.current_state.current_step_type)}")
        logger.debug(f"New step duration {self.current_state.current_step_duration}")
        logger.debug(f"New step remaining_time {self.current_state.current_step_remaining_time}")

        match self.model.current_state.current_step_type:
            case StepType.off_mode:
                logger.trace("EGModel: off_mode actions")
                self.view.show_notification("Eyes Guard is in suspended mode!", "Attention!")

            case StepType.break_mode:
                logger.trace("EGModel: break_mode actions")
                self.view.show_wnd_break()

            case StepType.work_notified_1:
                logger.trace("EGModel: work_notified_1 actions")
                if self.settings.user_settings.notifications == "on":
                    pass
                    # self.view.show_notification("Break will start in 1 minute!", "Attention!")

            case StepType.work_notified_2:
                logger.trace("EGModel: work_notified_2 actions")
                if self.settings.user_settings.notifications == "on":
                    self.view.show_notification("Break will start in 5 seconds!", "Attention!")

            case StepType.work_mode:
                logger.trace("EGModel: work_mode actions")
                self.view.hide_wnd_break()
                # self.break_wnd.hide()

    def wait_for_current_step_is_ended(self):
        logger.trace("EGModel: __wait_for_current_step_is_ended")
        while True:
            # print info
            logger.info(f"Current step type: {self.model.current_state.current_step_type}")
            logger.info(f"Step duration: {self.model.current_state.current_step_duration}")
            logger.info(f"Step elapsed time: {self.model.current_state.current_step_elapsed_time}")
            self.__change_step_if_protection_mode_was_changed()
            # time.sleep(1)

            if (
                self.model.current_state.current_step_elapsed_time
                < self.model.current_state.current_step_duration
            ):
                self.model.current_state.increase_elapsed_time()
                # self._update_time_until_break()
            else:
                break

            # actions during step is in progress
            match self.model.current_state.current_step_type:
                case StepType.break_mode:
                    self.view.update_wnd_break_remaining_time(self.model.current_state)
                case (
                    StepType.off_mode
                    | StepType.work_mode
                    | StepType.work_notified_1
                    | StepType.work_notified_2
                ):
                    # calculatin time to break for tooltip
                    self.__update_time_until_break()
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

            # self.__update_model_settings()
            time.sleep(1)

    def __change_step_if_protection_mode_was_changed(self):
        logger.trace("EGController: __change_step_if_protection_mode_was_changed")
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

    def __update_time_until_break(self):
        """Updating time until break info"""
        logger.trace("EGController: __update_time_until_break")

        remaining_time_actual: datetime.timedelta = self.model.current_state.current_step_remaining_time
        remaining_time_for_work_full = (
            self.model.steps_data_list[StepType.work_mode].step_duration_td
            + self.model.steps_data_list[StepType.work_notified_1].step_duration_td
            + self.model.steps_data_list[StepType.work_notified_2].step_duration_td
        )
        logger.debug(remaining_time_actual)
        match self.model.current_state.current_step_type:
            case StepType.off_mode:
                remaining_time_actual += self.model.steps_data_list[StepType.work_mode].step_duration_td
                remaining_time_for_work_full = (
                    self.model.steps_data_list[StepType.off_mode].step_duration_td
                    + self.model.steps_data_list[StepType.work_mode].step_duration_td
                    + self.model.steps_data_list[StepType.work_notified_1].step_duration_td
                    + self.model.steps_data_list[StepType.work_notified_2].step_duration_td
                )
            case StepType.work_mode:
                remaining_time_actual += (
                    self.model.steps_data_list[StepType.work_notified_1].step_duration_td
                    + self.model.steps_data_list[StepType.work_notified_2].step_duration_td
                )
            case StepType.work_notified_1:
                remaining_time_actual += self.model.steps_data_list[StepType.work_notified_2].step_duration_td

        logger.debug("Updating time")

        time_until_break_tooltip_string = "Time until break: " + f"{remaining_time_actual}"

        # self.view.tray_icon.title = time_until_break_tooltip_string
        # self.view.wnd_status.lbl_time_until_break.configure(text=time_until_break_tooltip_string)
        # self.view.wnd_status.pbar_time_until_break.set(
        #     1 - remaining_time_actual / remaining_time_for_work_full
        # )

    def __update_model_settings(self):
        logger.trace("EGController: __update_model_settings")
        # self.model.settings.user_settings = self.model.settings.user_settings
        # self.model.(self.model)
        # print(self.model.set_model.user_settings)

        # settings autorefresh not working

        # self.__update_current_state()

    def __update_current_state(self):
        logger.trace("Controller: __update_current_state")

        current_step = self.model.current_state.current_step_type
        self.model.current_state.set_current_step_data(
            step_type=current_step, step_duration=self.model.steps_data_list[current_step].step_duration_td
        )
        if (
            self.model.current_state.current_step_duration
            != self.model.steps_data_list[current_step].step_duration_td
        ):
            self.model.current_state.set_current_step_data(
                step_type=current_step,
                step_duration=self.model.steps_data_list[current_step].step_duration_td,
            )

    def set_new_step_in_sequence(self):
        logger.trace("EGController: __set_new_step_in_sequence")

        # current_step_type = self.model.current_state.current_step_type

        # steps transitions
        match self.current_state.current_step_type:
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

        logger.debug(f"EGModel: new step = {new_step_type}")
        self.__set_current_step(new_step_type)

    def __set_current_step(self, step_type: StepType) -> None:
        """settind step data in current state by step type"""
        logger.trace("EGModel: __set_current_step")

        self.model.current_state.set_current_step_data(
            step_type=step_type, step_duration=self.model.steps_data_list[step_type].step_duration_td
        )
        logger.debug(f"Step_type: {self.model.current_state.current_step_type}")
        logger.debug(f"Step_duration: {self.model.current_state.current_step_duration}")
        logger.debug(f"Steps data list: {self.model.steps_data_list[step_type]}")

    def apply_new_settings(self, user_settings: UserSettingsData) -> None:
        logger.trace("EGModel: applying view settings")
        self.model.model_user_settings = user_settings
