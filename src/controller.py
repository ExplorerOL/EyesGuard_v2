from threading import Thread

from logger import logger
from model import EGModel
from settings import UserSettingsData

# from view import EGView


class EGController:
    """Class for time and break control"""

    def __init__(self):
        logger.trace("EGController: object was created")

    def set_model(self, model: EGModel):
        """Assigning model to controller"""
        logger.trace("EGController: set_model")
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

        logger.trace("EGController: main loop started")
        while True:
            self.model.do_current_step_actions()
            self.model.wait_for_current_step_is_ended()
            self.model.set_new_step_in_sequence()

    def apply_view_settings(self, user_settings: UserSettingsData) -> None:
        logger.trace("EGModel: applying view settings")
        self.model.apply_new_settings(user_settings)
