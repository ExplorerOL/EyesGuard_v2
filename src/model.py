from settings import Settings
from states import CurrentState


class EGModel:
    def __init__(self, settings_file: str):
        self.view = None
        self.settings = Settings(settings_file)
        self.current_state = CurrentState(self.settings)

    def set_view(self, view: object):
        """Assigning controller to view"""

        # import placed here for breaking circular import
        from view import EGView

        self.view = view
