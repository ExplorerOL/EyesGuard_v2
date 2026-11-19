from controller import Controller
from model import Model
from support.logger import logger
from view import View


def main():
    """Main function."""
    logger.trace('Function started')

    controller = Controller()
    model = Model()
    view = View(initial_settings=model.settings.get_settings_copy())

    controller.set_model(model=model)
    model.set_view(view=view)
    view.set_controller(controller=controller)

    controller.start()
    logger.info('Program EyesGuard started!')

    view.mainloop()


# application entry point
if __name__ == '__main__':
    main()
