"""Module with windows of application"""

import os
import time

import customtkinter
import pystray
from PIL import Image

from settings import Settings


class App(customtkinter.CTk):
    """Main window of application"""

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.title("EyesGuard v2")
        self.status_wnd = StatusWnd(settings)
        self.settings_wnd = SettingsWnd(settings)

        # tray icon
        self.image = Image.open("res/img/eyes_with_protection.png")
        menu = (
            pystray.MenuItem("Exit", self.exit_app),
            pystray.MenuItem("Settings", self.show_settings_wnd),
            pystray.MenuItem("Status", self.show_status_wnd, default=True),
        )
        self.icon = pystray.Icon("name", self.image, "My System Tray Icon1", menu)
        self.icon.run_detached()

        # hide main app wnd
        self.withdraw()
        self.toplevel_window = None
        self.break_wnd = None

    def exit_app(self):
        """Exit from app"""
        self.icon.visible = False
        self.icon.stop()
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


class StatusWnd(customtkinter.CTkToplevel):
    """Status window"""

    def __init__(self, settings: Settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        wnd_width = 280
        wnd_height = 250
        border_x = 50
        border_y = 50
        screen_width = self.winfo_screenwidth()  # width of the screen
        screen_height = self.winfo_screenheight()  # height of the screen
        self.geometry(
            f"{wnd_width}x{wnd_height}+"
            f"{screen_width - wnd_width - border_x}+{screen_height - wnd_height - border_y}"
        )
        self.title("EyesGuard v2 - Status")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.attributes("-toolwindow", True)

        self.configure(fg_color="LightSteelBlue")
        self.img_eyes_with_protection = Image.open("res/img/eyes_with_protection.png")
        self.img_eyes_without_protection = Image.open("res/img/eyes_without_protection.png")
        self.img_check_mark = Image.open("res/img/check_mark.png")

        self.grid_columnconfigure((0), weight=1)

        # label time until break
        self.lbl_time_until_break = customtkinter.CTkLabel(
            self, text="Time until break:  - - -", font=("", 14, "bold")
        )
        self.lbl_time_until_break.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # progress bar time until break
        self.pbar_time_until_break = customtkinter.CTkProgressBar(
            self, orientation="horizontal", height=20, fg_color="GreenYellow"
        )
        self.pbar_time_until_break.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # button take a break
        self.btn_take_break = customtkinter.CTkButton(
            self,
            text="Take a break now",
            text_color="GreenYellow",
            height=40,
            width=150,
            corner_radius=50,
            image=customtkinter.CTkImage(light_image=self.img_check_mark, size=(40, 40)),
            border_spacing=0,
            font=("", 14, "bold"),
        )
        self.btn_take_break.grid(row=11, column=0, padx=20, pady=10, sticky="ew")

        # button change protection state
        self.btn_change_protection_state = customtkinter.CTkButton(
            self,
            text="Protection active",
            text_color="GreenYellow",
            command=self.btn_change_protection_state_action,
            height=40,
            width=150,
            corner_radius=50,
            image=customtkinter.CTkImage(light_image=self.img_eyes_with_protection, size=(40, 40)),
            border_spacing=0,
            font=("", 14, "bold"),
        )
        self.btn_change_protection_state.grid(row=10, column=0, padx=20, pady=10, sticky="ew")

        self.bind("<FocusOut>", self.on_focus_out)
        self.protocol("WM_DELETE_WINDOW", self.hide)
        self.update_wnd()
        self.withdraw()

    def on_focus_out(self, event):
        """Action in calse of loosing focus"""
        self.hide()

    def hide(self):
        """Hide window"""
        for i in range(100):
            self.attributes("-alpha", 1 - i / 100)
            time.sleep(0.006)
        self.withdraw()

    def show(self):
        """Show window"""
        print("showing top level wnd")

        self.deiconify()

        for i in range(100):
            self.attributes("-alpha", i / 100)
            time.sleep(0.006)

    def btn_change_protection_state_action(self):
        """Action for pressing changeing protection state button"""
        self.settings.change_protection_state()
        self.update_wnd()

    def update_wnd(self):
        """Updating status window elements states"""
        if self.settings.get().protection_status == "on":
            self.btn_change_protection_state.configure(
                text="Protection active",
                text_color="GreenYellow",
                image=customtkinter.CTkImage(light_image=self.img_eyes_with_protection, size=(40, 40)),
                require_redraw=True,
            )
        else:
            self.btn_change_protection_state.configure(
                text="Protection suspended",
                text_color="Tomato",
                # hover_color="yellow",
                image=customtkinter.CTkImage(light_image=self.img_eyes_without_protection, size=(40, 40)),
                require_redraw=True,
            )


class SettingsWnd(customtkinter.CTkToplevel):
    """Settings window"""

    def __init__(self, settings: Settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        wnd_width = 500
        wnd_height = 400
        border_x = 50
        border_y = 50
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(
            f"{wnd_width}x{wnd_height}+"
            f"{screen_width - wnd_width - border_x}+{screen_height - wnd_height - border_y}"
        )
        self.title("EyesGuard v2 - Settings")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.hide)
        self.withdraw()

    def on_focus_out(self, event):
        """Action in calse of loosing focus"""
        self.hide()

    def hide(self):
        """Hide window"""
        for i in range(100):
            self.attributes("-alpha", 1 - i / 100)
            time.sleep(0.006)
        self.withdraw()

    def show(self):
        """Show window"""
        print("showing top level wnd")

        self.deiconify()

        for i in range(100):
            self.attributes("-alpha", i / 100)
            time.sleep(0.006)


class SplashWindow:
    pass
