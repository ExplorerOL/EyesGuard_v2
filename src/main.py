from controller import Controller
from model import Model
from support.logger import logger
from support.sound.sound_player import sound_player
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
    controller.set_on_crash_callback(view.notify_engine_crashed)

    controller.start()
    logger.info('Program EyesGuard started!')

    view.mainloop()

    # graceful shutdown after the mainloop has quit (no os._exit)
    controller.stop()
    view.destroy()
    sound_player.close()
    logger.info('Program EyesGuard finished!')


# application entry point
if __name__ == '__main__':
    main()
