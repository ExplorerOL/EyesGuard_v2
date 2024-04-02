from controller import Controller
from logger import logger
from model import Model
from view import View


def main():
    """Main function"""

    logger.trace(f"Function started")

    controller = Controller()
    model = Model()
    view = View()

    controller.set_model(model=model)
    model.set_view(view=view)
    view.set_controller(controller=controller)

    controller.start()
    logger.info("Program EyesGuard started!")

    view.mainloop()


# application entry point
if __name__ == "__main__":
    main()
