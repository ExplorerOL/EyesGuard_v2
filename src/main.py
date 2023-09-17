from control_alg import ControlAlg
from settings import Settings
from states import CurrentState
from windows.main_wnd import MainWnd


def main():
    """main function"""
    SETTINGS_FILE = "./settings.json"
    eg_settings = Settings(SETTINGS_FILE)
    current_state = CurrentState(eg_settings)

    eg_app = MainWnd(eg_settings, current_state=current_state)
    eg_control_alg = ControlAlg(settings=eg_settings, current_state=current_state, break_wnd=eg_app.break_wnd)
    eg_control_alg.start()

    print("Programm EyesGuard started!")
    eg_app.mainloop()


# application entry point
if __name__ == "__main__":
    main()


# SETTINGS_FILE = './tests/data/test_config_invalid1.json'
