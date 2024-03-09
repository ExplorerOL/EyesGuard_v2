from settings import Settings
from states import CurrentState


class EGModel:
    def __init__(self, settings_file: str):
        self.settings = Settings(settings_file)
        self.current_state = CurrentState(self.settings)
