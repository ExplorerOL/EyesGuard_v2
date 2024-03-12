from controller import EGController
from logger import logger
from model import EGModel
from view import EGView


def main():
    """main function"""
    logger.trace(f"Function started")

    eg_controller = EGController()
    eg_model = EGModel()
    eg_view = EGView()

    eg_controller.set_model(model=eg_model)
    eg_model.set_view(view=eg_view)
    eg_view.set_controller(controller=eg_controller)

    eg_controller.start()
    logger.info("Program EyesGuard started!")

    eg_view.mainloop()


# application entry point
if __name__ == "__main__":
    main()
