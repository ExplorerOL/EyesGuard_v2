"""Module with main widnow of application"""
import os

import customtkinter
import pystray
from PIL import Image

from control_alg import CurrentState
from settings import Settings
from windows.break_wnd import BreakWnd
from windows.settings_wnd import SettingsWnd
from windows.status_wnd import StatusWnd


class MainWnd(customtkinter.CTk):
    """Main window of application"""

    def __init__(self, settings: Settings, current_state: CurrentState):
        super().__init__()
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")

        self.settings = settings
        self.current_state = current_state
        self.title("EyesGuard v2")
        self.settings_wnd = SettingsWnd(settings)
        self.break_wnd = BreakWnd(self.current_state)
        self.status_wnd = StatusWnd(self.settings, self.break_wnd)

        # tray icon
        self.image = Image.open("res/img/eyes_with_protection.png")
        menu = (
            pystray.MenuItem("Status", self.show_status_wnd, default=True),
            pystray.MenuItem("Settings", self.show_settings_wnd),
            pystray.MenuItem("Exit", self.exit_app),
        )
        self.tray_icon = pystray.Icon("name", self.image, "My System Tray Icon1", menu)
        self.tray_icon.run_detached()

        # hide main app wnd
        self.withdraw()

    def exit_app(self):
        """Exit from app"""
        self.tray_icon.visible = False
        self.tray_icon.stop()
        self.quit()
        os._exit(0)

    def show_status_wnd(self):
        """Show status wnd"""
        print("Show status wnd")
        self.status_wnd.show()

    def show_settings_wnd(self):
        """Show settings wnd"""
        print("Show settings wnd")
        self.settings_wnd.show()
