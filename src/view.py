"""Module with main widnow of application"""

import os

import customtkinter
import pystray
from PIL import Image

from controller import EGController
from model import CurrentState, EGModel
from settings import Settings
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
        self.wnd_settings = SettingsWnd(self.settings)
        self.wnd_break = BreakWnd(self.current_state)
        self.wnd_status = StatusWnd(self.settings, self.wnd_break)

        # tray icon
        self.image = Image.open("res/img/eyes_with_protection.png")
        menu = (
            pystray.MenuItem("Status", self.show_status_wnd, default=True),
            pystray.MenuItem("Settings", self.show_settings_wnd),
            pystray.MenuItem("Exit", self.exit_app),
        )
        self.tray_icon = pystray.Icon("name", self.image, "Eyes Guard", menu)
        self.tray_icon.run_detached()

        # hide main app wnd
        self.withdraw()

    def set_controller(self, controller: EGController):
        """Assigning controller to view"""
        self.controller = controller

    def exit_app(self):
        """Exit from app"""
        self.tray_icon.visible = False
        self.tray_icon.stop()
        self.quit()
        os._exit(0)

    def show_status_wnd(self):
        """Show status wnd"""
        print("Show status wnd")
        self.wnd_status.show()

    def show_settings_wnd(self):
        """Show settings wnd"""
        print("Show settings wnd")
        self.wnd_settings.show()

    def show_notification(self, title: str, text: str):
        self.tray_icon.notify(title, text)

    def init_all_views(self, model: EGModel):
        """Init all data at windows"""
        self.wnd_status.update(model.settings.user_settings)
        self.wnd_settings.update(model.settings.user_settings)
        self.wnd_break.update(model.current_state)