from controller import EGController
from model import EGModel
from view import EGView


def main():
    """main function"""
    SETTINGS_FILE = "./settings.json"

    eg_view = EGView()
    eg_model = EGModel(SETTINGS_FILE)
    eg_controller = EGController(model=eg_model, view=eg_view)

    eg_controller.start()
    print("Programm EyesGuard started!")

    eg_view.mainloop()


# application entry point
if __name__ == "__main__":
    main()
