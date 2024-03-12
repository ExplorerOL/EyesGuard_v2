"""Module with main widnow of application"""

import os

import customtkinter
import pystray
from PIL import Image

from controller import EGController
from logger import logger
from model import CurrentState, EGModel
from settings import Settings, UserSettingsData
from windows.break_wnd import BreakWnd
from windows.settings_wnd import SettingsWnd
from windows.status_wnd import StatusWnd


class EGView(customtkinter.CTk):
    """Main window of application"""

    def __init__(self):
        super().__init__()
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")

        self.settings = Settings()
        self.current_state = CurrentState(self.settings)
        self.title("EyesGuard v2")
        self.wnd_settings = SettingsWnd(self, self.settings)
        self.wnd_break = BreakWnd(self, self.current_state)
        self.wnd_status = StatusWnd(self, self.settings, self.wnd_break)

        # tray icon
        self.image = Image.open("res/img/eyes_with_protection.png")
        menu = (
            pystray.MenuItem("Status", self.__show_status_wnd, default=True),
            pystray.MenuItem("Settings", self.__show_settings_wnd),
            pystray.MenuItem("Exit", self.exit_app),
        )
        self.tray_icon = pystray.Icon("name", self.image, "Eyes Guard", menu)
        self.tray_icon.run_detached()

        # hide main app wnd
        self.withdraw()
        logger.trace("View: object was created")

    def __show_status_wnd(self):
        """Show status wnd"""
        logger.trace("View: show status wnd")
        self.wnd_status.show()

    def __show_settings_wnd(self):
        """Show settings wnd"""
        logger.trace("View: show settings wnd")
        self.wnd_settings.show()

    def __show_notification(self, title: str, text: str):
        self.tray_icon.notify(title, text)

    def set_controller(self, controller: EGController):
        """Assigning controller to view"""
        self.controller = controller
        logger.trace("View: controller was set")

    def exit_app(self):
        """Exit from app"""
        self.tray_icon.visible = False
        self.tray_icon.stop()
        self.quit()
        os._exit(0)

    def init_all_views(self, model: EGModel):
        """Init all data at windows"""
        logger.trace("View: init_all_views function started")
        self.wnd_status.update(model.settings.user_settings)
        self.wnd_settings.update(model.settings.user_settings)
        self.wnd_break.update(model.current_state)

    def apply_view_settings(self):
        logger.trace("View: applying new settings")
        self.controller.apply_view_settings(self.__get_settings_from_widgets())

    def __get_settings_from_widgets(self) -> UserSettingsData:
        """Get data from all widgets with settings"""
        ui_settings_data = UserSettingsData()
        try:
            ui_settings_data.work_duration = int(self.wnd_settings.work_duration_value.get())
            ui_settings_data.break_duration = int(self.wnd_settings.break_duration_value.get())
            ui_settings_data.protection_status = str(self.wnd_settings.chbox_protection_status_value.get())
            ui_settings_data.sounds = str(self.wnd_settings.chbox_sounds_value.get())
            ui_settings_data.notifications = str(self.wnd_settings.chbox_notifications_value.get())
        except TypeError as error:
            print("Error occuired while reading settings from ui: {error}")

        logger.info(f"Settings read from ui: {str(ui_settings_data)}")
        # print(int(self.break_duration_value.get()))
        # print(int(self.work_duration_value.get()))
        # print(self.chbox_sounds_value.get())
        # print(self.chbox_notifications_value.get())

        return ui_settings_data
