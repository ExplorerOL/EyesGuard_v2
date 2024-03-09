from control_alg import ControlAlg
from model import EGModel
from settings import Settings
from states import CurrentState
from windows.main_wnd import MainWnd


def main():
    """main function"""
    SETTINGS_FILE = "./settings.json"
    # eg_settings = Settings(SETTINGS_FILE)
    # current_state = CurrentState(eg_settings)

    eg_model = EGModel(SETTINGS_FILE)

    eg_app = MainWnd(eg_model.settings, current_state=eg_model.current_state)
    eg_control_alg = ControlAlg(settings=eg_model.settings, current_state=eg_model.current_state, app=eg_app)
    eg_control_alg.start()

    print("Programm EyesGuard started!")
    eg_app.mainloop()


# application entry point
if __name__ == "__main__":
    main()


# SETTINGS_FILE = './tests/data/test_config_invalid1.json'
