"""Module with settings window of application"""
import re
import time
from tkinter import *

import customtkinter
from PIL import Image, ImageTk

from settings import Settings


class SettingsWnd(customtkinter.CTkToplevel):
    """Settings window"""

    def __init__(self, settings: Settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        wnd_width = 500
        wnd_height = 400
        border_x = 50
        border_y = 150
        self.attributes("-alpha", 0)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(
            f"{wnd_width}x{wnd_height}+"
            f"{screen_width - wnd_width - border_x}+{screen_height - wnd_height - border_y}"
        )
        self.title("EyesGuard v2 - Settings")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        self.wnd_icon = ImageTk.PhotoImage(file="res/img/eyes_with_protection.png")
        self.after(250, lambda: self.iconphoto(False, self.wnd_icon))

        self.configure(fg_color="LightSteelBlue")

        # window elements
        # images
        self.img_eyes_with_protection = customtkinter.CTkImage(
            Image.open("res/img/eyes_with_protection.png"), size=(50, 50)
        )

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="SteelBlue")
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_lbl_title = customtkinter.CTkLabel(
            self.navigation_frame,
            text="   EyesGuard",
            text_color="White",
            image=self.img_eyes_with_protection,
            compound="left",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            # text_color="GreenYellow",
        )
        self.navigation_frame_lbl_title.grid(row=0, column=0, padx=20, pady=20)

        self.btn_time_settings = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            border_width=1,
            text="Time settings",
            font=("", 14, "bold"),
            fg_color="LightSteelBlue",
            text_color=("gray10", "gray90"),
            hover_color=("LightSkyBlue", "gray30"),
            border_color="Gray",
            # mage=self.image,
            anchor="w",
            # command=self.home_button_event,
        )
        self.btn_time_settings.grid(row=1, column=0, sticky="ew")

        self.btn_general_settings = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            border_width=1,
            text="General",
            font=("", 14, "bold"),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("LightSkyBlue", "gray30"),
            border_color="Gray",
            # image=self.image,
            anchor="w",
            # command=self.frame_2_button_event,
        )
        self.btn_general_settings.grid(row=2, column=0, sticky="ew")

        self.btn_about = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            border_width=1,
            text="About",
            font=("", 14, "bold"),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("LightSkyBlue", "gray30"),
            border_color="Gray",
            # image=self.image,
            anchor="w",
            # command=self.frame_2_button_event,
        )
        self.btn_about.grid(row=3, column=0, sticky="ew")

        # --- create time settings frame ---
        self.frame_time_settings = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_time_settings.grid_columnconfigure(1, weight=1)

        # work duratrion setting
        self.lbl_work_duration = customtkinter.CTkLabel(
            self.frame_time_settings, text="Work duration (minutes)", font=("", 14)
        )
        self.lbl_work_duration.grid(row=0, column=0, padx=20, pady=10)

        self.work_duration_value = StringVar()
        self.work_duration_value.set(self.settings.get().work_duration)
        verify_cmd_work_duration = (self.register(self.is_valid_duration_entry), "%P")
        self.entry_work_duration = customtkinter.CTkEntry(
            self.frame_time_settings,
            textvariable=self.work_duration_value,
            justify="center",
            validate="key",
            validatecommand=verify_cmd_work_duration,
        )
        self.entry_work_duration.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="e")

        # break duratrion setting
        self.lbl_break_duration = customtkinter.CTkLabel(
            self.frame_time_settings, text="Break duration (minutes)", font=("", 14)
        )
        self.lbl_break_duration.grid(row=1, column=0, padx=20, pady=10)

        self.break_duration_value = StringVar()
        self.break_duration_value.set(self.settings.get().break_duration)
        verify_cmd_break_duration = (self.register(self.is_valid_duration_entry), "%P")
        self.entry_break_duration = customtkinter.CTkEntry(
            self.frame_time_settings,
            textvariable=self.break_duration_value,
            justify="center",
            validate="key",
            validatecommand=verify_cmd_break_duration,
        )
        self.entry_break_duration.grid(row=1, column=1, padx=(20, 20), pady=(20, 20), sticky="e")

        self.lbl_test = customtkinter.CTkLabel(
            self.frame_time_settings, textvariable=self.break_duration_value, font=("", 14)
        )
        self.lbl_test.grid(row=2, column=0, padx=20, pady=10)

        # create second frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # self.home_button.configure(fg_color=("gray75", "gray25"))
        self.frame_time_settings.grid(row=0, column=1, sticky="nsew")

        # --- create general settings frame ---
        self.frame_general_settings = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # actions after elements creation
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
        self.update_wnd()
        self.deiconify()

        for i in range(100):
            self.attributes("-alpha", i / 100)
            time.sleep(0.006)

    def is_valid_duration_entry(self, value: str):
        print(value)
        result = re.match("^[1-9][0-9]{0,1}$|^$", value) is not None
        print(result)
        return result

    def update_wnd(self):
        """Updating status window elements states"""
        self.work_duration_value.set(self.settings.get().work_duration)
        self.break_duration_value.set(self.settings.get().break_duration)
