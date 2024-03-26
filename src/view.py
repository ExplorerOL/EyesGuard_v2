"""Module with main widnow of application"""

import os

import customtkinter
import pystray

from controller import Controller
from logger import logger
from model import Model
from resourses import ResImages
from settings import Settings, UserSettingsData
from states import CurrentState, StepType
from windows.wnd_break import WndBreak
from windows.wnd_settings import WndSettings
from windows.wnd_status import WndStatus


class View(customtkinter.CTk):
    """Main window of application"""

    def __init__(self):
        super().__init__()
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")

        self.image_protection_active = ResImages.image_protection_active
        self.image_protection_suspended = ResImages.image_protection_suspended
        self.image_protection_off = ResImages.image_protection_off

        self.__settings = Settings()
        self.__current_state = CurrentState()
        self.__wnd_settings = WndSettings(self, self.__settings)
        self.__wnd_break = WndBreak(self, self.__current_state)
        self.__wnd_status = WndStatus(self)
        self.title("EyesGuard v2")

        # tray icon
        menu = (
            pystray.MenuItem("Status", self.__show_status_wnd, default=True),
            pystray.MenuItem("Settings", self.__show_settings_wnd),
            pystray.MenuItem("Exit", self.exit_app),
        )
        self.__tray_icon = pystray.Icon("name", self.image_protection_active, "Eyes Guard", menu)
        self.__tray_icon.run_detached()

        # hide main app wnd
        self.withdraw()
        logger.trace("View: object was created")

    def __show_status_wnd(self):
        """Show status wnd"""
        logger.trace("View: show status wnd")
        self.__wnd_status.show()

    def __show_settings_wnd(self):
        """Show settings wnd"""
        logger.trace("View: show settings wnd")
        self.__wnd_settings.show()

    def show_notification(self, title: str, text: str):
        logger.trace("View: show_notification")
        self.__tray_icon.notify(title, text)

    def set_controller(self, controller: Controller):
        """Assigning controller to view"""
        self.controller = controller
        logger.trace("View: controller was set")

    def exit_app(self):
        """Exit from app"""
        self.__tray_icon.visible = False
        self.__tray_icon.stop()
        self.quit()
        os._exit(0)

    def update_all_wnd_values(self, model: Model):
        """Init all data at windows"""
        logger.trace("View: init_all_views function started")
        self.__wnd_status.update(model)
        self.__wnd_settings.update(model)

    def apply_view_user_settings(self):
        logger.trace("View: applying new settings")
        self.controller.apply_view_user_settings(self.__get_user_settings_from_wnd_settings())

    def __get_user_settings_from_wnd_settings(self) -> UserSettingsData:
        """Get data from all widgets with settings"""
        ui_settings_data = UserSettingsData()
        try:
            ui_settings_data.work_duration = int(self.__wnd_settings.work_duration_value.get())
            ui_settings_data.break_duration = int(self.__wnd_settings.break_duration_value.get())
            ui_settings_data.protection_status = str(self.__wnd_settings.chbox_protection_status_value.get())
            ui_settings_data.sounds = str(self.__wnd_settings.chbox_sounds_value.get())
            ui_settings_data.notifications = str(self.__wnd_settings.chbox_notifications_value.get())
            ui_settings_data.protection_status = str(self.__wnd_settings.chbox_protection_status_value.get())
        except TypeError as error:
            logger.error(f"Error occuired while reading settings from ui: {error}")

        logger.info(f"Settings read from ui: {str(ui_settings_data)}")

        return ui_settings_data

    def show_wnd_break(self):
        self.__wnd_break.show()

    def hide_wnd_break(self):
        self.__wnd_break.hide()

    def update_wnd_status(self, model: Model) -> None:
        self.__wnd_status.update(model)

    def update_wnd_settings(self, model: Model) -> None:
        self.__wnd_settings.update(model)

    def update_wnd_break(self, model: Model) -> None:
        self.__wnd_break.update(model)

    def update_tray_icon_values(self, model: Model) -> None:
        logger.trace("View: update_tray_icon_values")
        self.__tray_icon.title = f"Time until break: {model.remaining_working_time_to_display}"
        if model.current_state.current_step_type == StepType.off_mode:
            logger.debug("View: off cond")
            self.__tray_icon.title = "Protection off"
            self.__tray_icon.icon = self.image_protection_off
        elif model.current_state.current_step_type == StepType.suspended_mode:
            self.__tray_icon.icon = self.image_protection_suspended
            self.__tray_icon.title = (
                f"Time until normal mode: {model.current_state.current_step_remaining_time}"
            )
        else:
            self.__tray_icon.icon = self.image_protection_active

    def switch_suspended_state(self):
        logger.trace("View: switch_suspended_state")
        self.controller.switch_suspended_state()

    def set_step(self, new_step_type: StepType):
        logger.trace("View: set_step")
        self.controller.set_step(new_step_type)
