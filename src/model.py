# For preventing circular import
# https://stackoverflow.com/questions/744373/what-happens-when-using-mutual-or-circular-cyclic-imports/67673741#67673741
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view import EGView

import datetime

from logger import logger
from settings import Settings
from states import CurrentState, StepData, StepType

SETTINGS_FILE = "./settings/settings.json"


class EGModel:
    def __init__(self, settings_file: str = SETTINGS_FILE):
        self.view = None
        self.settings = Settings(settings_file)
        self.current_state = CurrentState(self.settings)

        logger.info(f"User settings: = {self.settings.user_settings}")

        self.steps_data_list: list[StepData] = []

        for step_type in StepType:
            self.steps_data_list.insert(step_type, StepData())
            self.steps_data_list[step_type].step_type = step_type

        logger.info(self.steps_data_list)
        for step in self.steps_data_list:
            logger.info(f"{step.step_type=}")
            logger.info(step.step_duration_td)

        logger.info(self.current_state)

        # setting steps durations
        self.step_off_duration_td = self.settings.system_settings.step_off_mode_duration
        self.step_work_duration_td = datetime.timedelta(minutes=self.settings.user_settings.work_duration)
        self.step_break_duration = datetime.timedelta(minutes=self.settings.user_settings.break_duration)
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
        self.steps_data_list[StepType.break_mode].step_duration_td = self.step_break_duration

        logger.trace("Model object was created")

    def set_view(self, view: EGView):
        """Assigning controller to view"""

        # import placed here for breaking circular import
        # from view import EGView

        self.view = view
        logger.trace("Model: view was set")

    @property
    def model_settings(self):
        logger.trace("Model: getting new settings")
        return self.settings

    @model_settings.setter
    def model_settings(self, settings: Settings):
        logger.trace("Model: saving new settings")
