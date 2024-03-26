# For preventing circular import
# https://stackoverflow.com/questions/744373/what-happens-when-using-mutual-or-circular-cyclic-imports/67673741#67673741
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view import View

import datetime
import time

from logger import logger
from settings import OnOffValue, Settings, UserSettingsData
from states import CurrentState, StepData, StepType

SETTINGS_FILE = "./settings/settings.json"


class Model:
    TIME_TICK_S = 1

    def __init__(self, settings_file: str = SETTINGS_FILE):
        self.__view: View
        self.__settings = Settings(settings_file)
        self.__current_state = CurrentState()

        logger.info(f"User settings: = {self.__settings.user_settings}")

        self.steps_data_list: list[StepData] = []
        logger.info(self.__current_state)

        self.__remaining_time_to_display = datetime.timedelta(seconds=0)
        self.__time_for_work_full = datetime.timedelta(seconds=0)

        logger.trace("Model: object was created")

    def __init_steps(self):
        for step_type in StepType:
            self.steps_data_list.insert(step_type, StepData())
            self.steps_data_list[step_type].step_type = step_type

        # setting steps durations
        self.step_off_duration_td = self.__settings.system_settings.step_suspended_mode_duration
        self.step_suspended_duration_td = self.__settings.system_settings.step_suspended_mode_duration
        self.step_work_duration_td = datetime.timedelta(minutes=self.__settings.user_settings.work_duration)
        self.step_break_duration_td = datetime.timedelta(minutes=self.__settings.user_settings.break_duration)
        self.step_notification_1_time_td = self.__settings.system_settings.step_notification_1_duration
        self.step_notification_2_time_td = self.__settings.system_settings.step_notification_2_duration
        logger.info(f"step_work_duration_td {self.step_work_duration_td}")

        self.steps_data_list[StepType.off_mode].step_duration_td = self.step_suspended_duration_td
        self.steps_data_list[StepType.suspended_mode].step_duration_td = self.step_suspended_duration_td
        if self.step_work_duration_td > self.step_notification_1_time_td + self.step_notification_2_time_td:
            logger.info(
                f"cond 1 {self.step_work_duration_td}  {self.step_notification_1_time_td + self.step_notification_2_time_td}"
            )
            self.steps_data_list[StepType.work_mode].step_duration_td = (
                self.step_work_duration_td
                - self.step_notification_1_time_td
                - self.step_notification_2_time_td
            )
        else:
            self.steps_data_list[StepType.work_mode].step_duration_td = datetime.timedelta(seconds=0)

        self.steps_data_list[StepType.work_notified_1].step_duration_td = self.step_notification_1_time_td
        self.steps_data_list[StepType.work_notified_2].step_duration_td = self.step_notification_2_time_td
        self.steps_data_list[StepType.break_mode].step_duration_td = self.step_break_duration_td

        logger.info(self.steps_data_list)
        for step in self.steps_data_list:
            logger.info(f"{step.step_type=}")
            logger.info(step.step_duration_td)

        # set initial step
        logger.debug(f"Off mode: {self.__settings.user_settings.protection_status}")
        logger.debug(f"Off value: {OnOffValue.off}")
        if self.__settings.user_settings.protection_status == OnOffValue.off.value:
            logger.debug("Model: init with off_mode")
            self.set_step(new_step_type=StepType.off_mode)
        else:
            logger.debug("Model: init with work_mode")
            self.set_step(new_step_type=StepType.work_mode)

        self.__view.update_all_wnd_values(self.model)

    def __update_view(self):
        """View initialization with model data"""
        logger.trace("Model: __init_view function")
        self.__init_steps()

        if self.__view is not None:
            self.__view.update_all_wnd_values(self.model)

    def __update_tray_icon_values(self):
        """Updating tray icon values"""
        logger.trace("Controller: __update_tray_icon_values")

        self.__calculate_remaining_time_for_work()
        self.__view.update_tray_icon_values(self.model)

    def __update_wnd_status(self):
        """Updating status window values"""
        logger.trace("Controller: __update_wnd_status_values")

        self.__remaining_time_to_display = self.__calculate_remaining_time_for_work()
        self.__time_for_work_full = self.__calculate_time_for_work()
        self.__view.update_wnd_status(self.model)

    def __update_wnd_settings(self):
        self.__view.update_wnd_settings(self.model)

    def __update_wnd_break(self):
        """Updating break window values"""
        logger.trace("Controller: __update_wnd_break_values")
        self.__view.update_wnd_break(self.model)

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
        logger.debug(f"Model: new step {step_type}")

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
    def remaining_working_time_to_display(self) -> datetime.timedelta:
        logger.trace("Model: remaining_working_time_to_display property")
        return self.__remaining_time_to_display

    @property
    def time_for_work_full(self) -> datetime.timedelta:
        logger.trace("Model: time_for_work_full property")
        return self.__time_for_work_full

    @property
    def current_state(self) -> CurrentState:
        logger.trace("Model: current_state")
        return self.__current_state

    @property
    def settings(self) -> Settings:
        logger.trace("Model: model_settings getter")
        return self.__settings

    @settings.setter
    def settings(self, settings: Settings) -> None:
        logger.trace("Model: model_settings setter")

    @property
    def user_settings(self) -> UserSettingsData:
        logger.trace("Model: model_user_settings getter")
        return self.__settings.user_settings

    @user_settings.setter
    def user_settings(self, user_settings: UserSettingsData) -> None:
        logger.trace("Model: model_user_settings setter")
        self.__settings.apply_settings_from_ui(user_settings)

    def set_view(self, view: View) -> None:
        """Assigning controller to view"""
        logger.trace("Model: set_view started")
        self.__view = view
        self.__update_view()

    def do_current_step_actions(self):
        logger.trace("Model: __do_current_step_actions")
        logger.debug(f"Model: New current step {(self.__current_state.current_step_type)}")
        logger.debug(f"Model: New step type {type(self.__current_state.current_step_type)}")
        logger.debug(f"Model: New step duration {self.__current_state.current_step_duration}")
        logger.debug(f"Model: New step remaining_time {self.__current_state.current_step_remaining_time}")

        match self.model.__current_state.current_step_type:
            case StepType.off_mode:
                logger.trace("Model: off_mode actions")
                self.__view.show_notification("Eyes Guard protection is off!", "Attention!")

            case StepType.suspended_mode:
                logger.trace("Model: off_mode actions")
                self.__view.show_notification("Eyes Guard protection suspended!", "Attention!")

            case StepType.break_mode:
                logger.trace("Model: break_mode actions")
                self.__update_wnd_break()

            case StepType.work_notified_1:
                logger.trace("Model: work_notified_1 actions")
                if self.__settings.user_settings.notifications == "on":
                    pass
                    self.__view.show_notification("Break will start in 1 minute!", "Attention!")

            case StepType.work_notified_2:
                logger.trace("Model: work_notified_2 actions")
                if self.__settings.user_settings.notifications == "on":
                    self.__view.show_notification("Break will start in 5 seconds!", "Attention!")

            case StepType.work_mode:
                logger.trace("Model: work_mode actions")
                self.__view.update_wnd_break(model=self.model)

    def wait_for_current_step_is_ended(self):
        logger.trace("Model: __wait_for_current_step_is_ended")
        while True:
            logger.info(f"Current step type: {self.model.__current_state.current_step_type}")
            logger.info(f"Step duration: {self.model.__current_state.current_step_duration}")
            logger.info(f"Step elapsed time: {self.model.__current_state.current_step_elapsed_time}")

            if self.__current_state.current_step_type != StepType.off_mode:
                if (
                    self.model.__current_state.current_step_elapsed_time
                    < self.model.__current_state.current_step_duration
                ):
                    self.model.__current_state.increase_elapsed_time()
                else:
                    break

            # actions during step is in progress
            match self.model.__current_state.current_step_type:
                case StepType.break_mode:
                    self.__update_wnd_break()

                case _:
                    self.__update_wnd_status()
                    self.__update_tray_icon_values()

            time.sleep(self.TIME_TICK_S)

    def set_new_step_in_sequence(self):
        logger.trace("Controller: __set_new_step_in_sequence")

        # steps transitions
        match self.__current_state.current_step_type:
            case StepType.off_mode:
                new_step_type = self.current_state.current_step_type
                pass
            case StepType.suspended_mode:
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

    def apply_new_user_settings(self, user_settings: UserSettingsData) -> None:
        logger.trace("Model: apply_new_settings")
        self.user_settings = user_settings
        self.__init_steps()

    def switch_suspended_state(self):
        logger.trace("Model: change_suspended_state")
        if self.current_state.current_step_type != StepType.suspended_mode:
            self.set_step(StepType.suspended_mode)
            logger.debug("Model: show notification")
            self.__view.show_notification("Eyes Guard protection suspended!", "Attention!")

        else:
            self.set_step(StepType.work_mode)

    def set_step(self, new_step_type: StepType):
        logger.trace("Model: set_step")
        self.__set_current_step(new_step_type)
        self.do_current_step_actions()
        self.__update_wnd_break()
        self.__update_wnd_status()
        self.__update_wnd_settings()
