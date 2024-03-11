from controller import EGController
from model import EGModel
from view import EGView


def main():
    """main function"""
    SETTINGS_FILE = "./settings.json"

    eg_controller = EGController()
    eg_model = EGModel(SETTINGS_FILE)
    eg_view = EGView()

    eg_controller.set_model(model=eg_model)
    eg_model.set_view(view=eg_view)
    eg_view.set_controller(controller=eg_controller)

    eg_controller.start()
    print("Programm EyesGuard started!")

    eg_view.mainloop()


# application entry point
if __name__ == "__main__":
    main()
