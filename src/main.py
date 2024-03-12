from controller import EGController
from logger import logger
from model import EGModel
from view import EGView


def main():
    """Main function"""

    logger.trace(f"Function started")

    controller = EGController()
    model = EGModel()
    view = EGView()

    controller.set_model(model=model)
    model.set_view(view=view)
    view.set_controller(controller=controller)

    controller.start()
    logger.info("Program EyesGuard started!")

    view.mainloop()


# application entry point
if __name__ == "__main__":
    main()
