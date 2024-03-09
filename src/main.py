from control_alg import EGController
from model import EGModel
from settings import Settings
from states import CurrentState
from windows.main_wnd import EGView


def main():
    """main function"""
    SETTINGS_FILE = "./settings.json"

    eg_model = EGModel(SETTINGS_FILE)
    eg_view = EGView()

    eg_controller = EGController(model=eg_model, app=eg_view)
    eg_controller.start()

    print("Programm EyesGuard started!")
    eg_view.mainloop()


# application entry point
if __name__ == "__main__":
    main()


# SETTINGS_FILE = './tests/data/test_config_invalid1.json'
