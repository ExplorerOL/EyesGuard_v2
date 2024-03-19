from threading import Thread

from logger import logger
from model import Model
from settings import UserSettingsData
from states import StepType

# from view import EGView


class Controller:
    """Class for time and break control"""

    def __init__(self):
        logger.trace("Controller: object was created")

    def set_model(self, model: Model):
        """Assigning model to controller"""
        logger.trace("Controller: set_model")
        self.model = model
        self.thread_alg = None

    def start(self):
        """Start controller in separated thread"""
        if self.thread_alg is None:
            self.thread_alg = Thread(target=self.main_loop)
            self.thread_alg.start()

    def stop(self):
        pass

    def main_loop(self):
        """Controller main loop in separated thread"""

        logger.trace("Controller: main loop started")
        while True:
            self.model.do_current_step_actions()
            self.model.wait_for_current_step_is_ended()
            self.model.set_new_step_in_sequence()

    def apply_view_user_settings(self, user_settings: UserSettingsData) -> None:
        logger.trace("EGModel: applying view settings")
        self.model.apply_new_settings(user_settings)

    def change_protection_state(self):
        self.model.change_protection_state()

    def set_step(self, new_step_type: StepType):
        self.model.set_step(new_step_type)
