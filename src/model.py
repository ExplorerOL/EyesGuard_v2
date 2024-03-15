# For preventing circular import
# https://stackoverflow.com/questions/744373/what-happens-when-using-mutual-or-circular-cyclic-imports/67673741#67673741
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view import View

import datetime
import time

import data.wnd_values as wnd_values
from logger import logger
from settings import OnOffValue, Settings, UserSettingsData
from states import CurrentState, StepData, StepType

SETTINGS_FILE = "./settings/settings.json"


class Model:
    TIME_TICK_S = 1

    def __init__(self, settings_file: str = SETTINGS_FILE):
        self.__view: View | None = None
        self.__settings = Settings(settings_file)
        self.__current_state = CurrentState(self.__settings)

        logger.info(f"User settings: = {self.__settings.user_settings}")

        self.steps_data_list: list[StepData] = []
        self.__init_steps()

        logger.info(self.__current_state)

        logger.trace("Model: object was created")

    def __init_steps(self):
        for step_type in StepType:
            self.steps_data_list.insert(step_type, StepData())
            self.steps_data_list[step_type].step_type = step_type

        # setting steps durations
        self.step_off_duration_td = self.__settings.system_settings.step_off_mode_duration
        self.step_work_duration_td = datetime.timedelta(minutes=self.__settings.user_settings.work_duration)
        self.step_break_duration_td = datetime.timedelta(minutes=self.__settings.user_settings.break_duration)
        self.step_notification_1_time_td = self.__settings.system_settings.step_notification_1_duration
        self.step_notification_2_time_td = self.__settings.system_settings.step_notification_2_duration
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

    def __init_view(self):
        """View initialization with model data"""
        logger.trace("Model: __init_view function started")
        if self.__view is not None:
            self.__view.init_all_views(self.model)

    def __change_step_if_protection_mode_was_changed(self):
        logger.trace(f"Model: __change_step_if_protection_mode_was_changed")
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

    def __update_tray_icon_values(self):
        """Updating tray icon values"""
        logger.trace("Controller: __update_tray_icon_values")

        remaining_time_to_display = self.__calculate_remaining_time_for_work()
        # logger.debug("Updating time")

        time_until_break_tooltip_string = "Time until break: " + f"{remaining_time_to_display}"
        new_tray_icon_values = wnd_values.TryIconValues()
        new_tray_icon_values.tooltip_str = time_until_break_tooltip_string
        new_tray_icon_values.protection_status = self.__settings.user_settings.protection_status
        self.__view.update_tray_icon_values(new_tray_icon_values)

    def __update_wnd_status_values(self):
        """Updating status window values"""
        logger.trace("Controller: __update_wnd_status_values")

        remaining_time_to_display = self.__calculate_remaining_time_for_work()
        remaining_time_for_work_full = self.__calculate_time_for_work()
        # logger.debug("Updating time")

        time_until_break_tooltip_string = "Time until break: " + f"{remaining_time_to_display}"

        new_wnd_status_values = wnd_values.WndStatusValues()
        new_wnd_status_values.remaining_time_str = time_until_break_tooltip_string
        new_wnd_status_values.remaining_time_pbar_value = (
            1 - remaining_time_to_display / remaining_time_for_work_full
        )
        new_wnd_status_values.protection_status = self.model_user_settings.protection_status
        self.__view.update_wnd_status_values(new_wnd_status_values)

    def __update_wnd_settings_values(self):
        new_wnd_settings_values = wnd_values.WndSettingsValues()
        new_wnd_settings_values.protection_status = self.model_user_settings.protection_status
        self.__view.update_wnd_settings_values(new_wnd_settings_values)

    def __update_wnd_break_values(self):
        """Updating break window values"""
        logger.trace("Controller: __update_wnd_break_values")
        new_wnd_break_values = wnd_values.WndBreakValues()
        new_wnd_break_values.remaining_time_str = (
            f"Remaining break time: {self.model.__current_state.current_step_remaining_time}"
        )
        new_wnd_break_values.remaining_time_pbar_value = (
            1
            - self.model.__current_state.current_step_remaining_time
            / self.model.steps_data_list[StepType.break_mode].step_duration_td
        )
        self.__view.update_wnd_break_values(new_wnd_break_values)

    def __calculate_remaining_time_for_work(self) -> datetime.timedelta:
        remaining_time_actual: datetime.timedelta = self.model.__current_state.current_step_remaining_time
        logger.debug(remaining_time_actual)
        match self.model.__current_state.current_step_type:
            case StepType.off_mode:
                remaining_time_actual += (
                    self.model.steps_data_list[StepType.work_mode].step_duration_td
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
        return remaining_time_actual

    def __calculate_time_for_work(self) -> datetime.timedelta:
        # remaining_time_actual: datetime.timedelta = self.model.__current_state.current_step_remaining_time
        time_for_work = (
            self.model.steps_data_list[StepType.work_mode].step_duration_td
            + self.model.steps_data_list[StepType.work_notified_1].step_duration_td
            + self.model.steps_data_list[StepType.work_notified_2].step_duration_td
        )
        match self.model.__current_state.current_step_type:
            case StepType.off_mode:
                time_for_work = (
                    self.model.steps_data_list[StepType.off_mode].step_duration_td
                    + self.model.steps_data_list[StepType.work_mode].step_duration_td
                    + self.model.steps_data_list[StepType.work_notified_1].step_duration_td
                    + self.model.steps_data_list[StepType.work_notified_2].step_duration_td
                )
        return time_for_work

    def __set_current_step(self, step_type: StepType) -> None:
        """settind step data in current state by step type"""
        logger.trace("Model: __set_current_step")

        self.model.__current_state.reset_elapsed_time()
        self.model.__current_state.set_current_step_data(
            step_type=step_type, step_duration=self.model.steps_data_list[step_type].step_duration_td
        )
        logger.debug(f"Step_type: {self.model.__current_state.current_step_type}")
        logger.debug(f"Step_duration: {self.model.__current_state.current_step_duration}")
        logger.debug(f"Steps data list: {self.model.steps_data_list[step_type]}")

    @property
    def model(self) -> Model:
        logger.trace("Model: getting model data")
        return self

    @property
    def current_state(self) -> CurrentState:
        logger.trace("Model: current_state")
        return self.__current_state

    @property
    def model_settings(self) -> Settings:
        logger.trace("Model: getting settings")
        return self.__settings

    @model_settings.setter
    def model_settings(self, settings: Settings) -> None:
        logger.trace("Model: saving new settings")

    @property
    def model_user_settings(self) -> UserSettingsData:
        logger.trace("Model: getting user settings")
        return self.__settings.user_settings

    @model_user_settings.setter
    def model_user_settings(self, user_settings: UserSettingsData) -> None:
        logger.trace("Model: saving new settings")
        self.__settings.apply_settings_from_ui(user_settings)

    def set_view(self, view: View) -> None:
        """Assigning controller to view"""
        logger.trace("Model: set_view started")

        # import placed here for breaking circular import
        # from view import EGView

        self.__view = view
        self.__init_view()

    def do_current_step_actions(self):
        logger.trace("Model: __do_current_step_actions")
        # self.model.__current_state.reset_elapsed_time()
        logger.debug(f"New current step {(self.__current_state.current_step_type)}")
        logger.debug(f"New step type {type(self.__current_state.current_step_type)}")
        logger.debug(f"New step duration {self.__current_state.current_step_duration}")
        logger.debug(f"New step remaining_time {self.__current_state.current_step_remaining_time}")

        match self.model.__current_state.current_step_type:
            case StepType.off_mode:
                logger.trace("Model: off_mode actions")
                self.__view.show_notification("Eyes Guard is in suspended mode!", "Attention!")

            case StepType.break_mode:
                logger.trace("Model: break_mode actions")
                self.__update_wnd_break_values()
                self.__view.show_wnd_break()

            case StepType.work_notified_1:
                logger.trace("Model: work_notified_1 actions")
                if self.__settings.user_settings.notifications == "on":
                    pass
                    # self.view.show_notification("Break will start in 1 minute!", "Attention!")

            case StepType.work_notified_2:
                logger.trace("Model: work_notified_2 actions")
                if self.__settings.user_settings.notifications == "on":
                    self.__view.show_notification("Break will start in 5 seconds!", "Attention!")

            case StepType.work_mode:
                logger.trace("Model: work_mode actions")
                if self.model_user_settings.protection_status == OnOffValue.off.value:
                    self.change_protection_state()

                self.__view.hide_wnd_break()
                # self.break_wnd.hide()

    def wait_for_current_step_is_ended(self):
        logger.trace("Model: __wait_for_current_step_is_ended")
        while True:
            # print info
            logger.info(f"Current step type: {self.model.__current_state.current_step_type}")
            logger.info(f"Step duration: {self.model.__current_state.current_step_duration}")
            logger.info(f"Step elapsed time: {self.model.__current_state.current_step_elapsed_time}")
            self.__change_step_if_protection_mode_was_changed()
            # time.sleep(1)

            if (
                self.model.__current_state.current_step_elapsed_time
                < self.model.__current_state.current_step_duration
            ):
                self.model.__current_state.increase_elapsed_time()
                # self._update_time_until_break()
            else:
                break

            # actions during step is in progress
            match self.model.__current_state.current_step_type:
                case StepType.break_mode:
                    self.__update_wnd_break_values()

                case _:
                    self.__update_wnd_status_values()
                    self.__update_tray_icon_values()

            time.sleep(self.TIME_TICK_S)

    def set_new_step_in_sequence(self):
        logger.trace("Controller: __set_new_step_in_sequence")

        # steps transitions
        match self.__current_state.current_step_type:
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

        logger.debug(f"Model: new step = {new_step_type}")
        self.__set_current_step(new_step_type)

    def apply_new_settings(self, user_settings: UserSettingsData) -> None:
        logger.trace("Model: apply_new_settings")
        self.model_user_settings = user_settings
        self.__init_steps()
        self.__set_current_step(StepType.work_mode)

    def change_protection_state(self):
        logger.trace("Model: change_protection_state")
        new_user_settings = self.model_user_settings
        if new_user_settings.protection_status == OnOffValue.on.value:
            new_user_settings.protection_status = OnOffValue.off.value
        else:
            new_user_settings.protection_status = OnOffValue.on.value
        self.model_user_settings = new_user_settings
        self.__init_steps()

        if new_user_settings.protection_status == OnOffValue.off.value:
            self.__set_current_step(StepType.off_mode)
        else:
            self.__set_current_step(StepType.work_mode)
        self.__update_wnd_status_values()
        self.__update_wnd_settings_values()

    def set_break_mode(self):
        logger.trace("Model: set_break_mode")
        self.__set_current_step(StepType.break_mode)
        self.__update_wnd_break_values()
        self.__view.show_wnd_break()
