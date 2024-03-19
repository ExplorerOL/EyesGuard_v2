"""Module with main widnow of application"""

import datetime
import os

import customtkinter
import pystray
from PIL import Image

import data.wnd_values as wnd_values
from controller import Controller
from logger import logger
from model import Model
from settings import OnOffValue, Settings, UserSettingsData
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

        self.__settings = Settings()
        self.__current_state = CurrentState()
        self.__wnd_settings = WndSettings(self, self.__settings)
        self.__wnd_break = WndBreak(self, self.__current_state)
        self.__wnd_status = WndStatus(self)
        self.title("EyesGuard v2")

        # tray icon
        self.image_protection_active = Image.open("res/img/eyes_with_protection.png")
        self.image_protection_suspended = Image.open("res/img/eyes_without_protection.png")
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

    def init_all_views(self, model: Model):
        """Init all data at windows"""
        logger.trace("View: init_all_views function started")
        # self.__wnd_status.update(model.model_user_settings)
        self.__wnd_settings.update(model.model_user_settings)
        # self.__wnd_break.update_values(model.current_state)

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
            logger.error("Error occuired while reading settings from ui: {error}")

        logger.info(f"Settings read from ui: {str(ui_settings_data)}")
        # print(int(self.break_duration_value.get()))
        # print(int(self.work_duration_value.get()))
        # print(self.chbox_sounds_value.get())
        # print(self.chbox_notifications_value.get())

        return ui_settings_data

    def show_wnd_break(self):
        self.__wnd_break.show()

    def hide_wnd_break(self):
        self.__wnd_break.hide()

    def update_wnd_status_values(self, wnd_status_values: wnd_values.WndStatusValues) -> None:
        self.__wnd_status.update_values(wnd_status_values)

    def update_wnd_settings_values(self, wnd_settings_values: wnd_values.WndSettingsValues) -> None:
        self.__wnd_settings.update_values(wnd_settings_values)

    def update_wnd_break_values(self, new_values: wnd_values.WndBreakValues) -> None:
        self.__wnd_break.update_values(new_values)

    def update_tray_icon_values(self, new_tray_icon_values: wnd_values.TryIconValues) -> None:
        self.__tray_icon.title = new_tray_icon_values.tooltip_str
        if new_tray_icon_values.protection_status == OnOffValue.on.value:
            self.__tray_icon.icon = self.image_protection_active
        else:
            self.__tray_icon.icon = self.image_protection_suspended

    def change_protection_state(self):
        self.controller.change_protection_state()

    def set_step(self, new_step_type: StepType):
        self.controller.set_step(new_step_type)
