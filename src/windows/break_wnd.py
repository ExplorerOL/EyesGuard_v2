"""Module with break window of application"""
import datetime
import re
import time
from tkinter import StringVar

import customtkinter
from PIL import Image, ImageTk

from states import CurrentState

# from settings import Settings, SettingsData


class BreakWnd(customtkinter.CTkToplevel):
    """Break window"""

    def __init__(self, current_state: CurrentState, *args, **kwargs):
        super().__init__(*args, fg_color="#000000", **kwargs)
        self.current_state = current_state

        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen
        self.attributes("-alpha", 0)
        print(ws, hs)
        self.geometry("%dx%d" % (ws, hs))
        self.title("EyesGuard v2.0.0")

        self.attributes("-topmost", True)
        self.attributes("-fullscreen", True)
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.bg_image = customtkinter.CTkImage(Image.open("res/img/break_wnd_bg1.png"), size=(ws, hs))
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image, text="")
        self.bg_image_label.grid(row=0, column=0, rowspan=2)

        self.remaining_break_time = StringVar()

        self.remaining_break_time.set(f"Remaining break time: 0 seconds")
        self.lbl_remain_time = customtkinter.CTkLabel(
            self,
            text="Remaining break time: ",
            text_color="GreenYellow",
            textvariable=self.remaining_break_time,
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.lbl_remain_time.grid(row=1, column=0, padx=20, pady=5)

        self.grid_columnconfigure(0, weight=1)
        self.pbar_break_progress = customtkinter.CTkProgressBar(
            self, orientation="horizontal", fg_color="GreenYellow", determinate_speed=0.05
        )
        self.pbar_break_progress.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.protocol("WM_DELETE_WINDOW", self.hide)
        self.withdraw()

    def hide(self):
        """Hide window"""
        self.pbar_break_progress.stop()
        self.pbar_break_progress.set(1)

        for i in range(100):
            self.attributes("-alpha", 1 - i / 100)
            time.sleep(0.006)
        self.withdraw()

    def show(self):
        """Show window"""
        print("Break wnd: showing break window")

        self.set_lbl_remaining_time_text(self.current_state.get_step_remaining_time())

        pbar_speed = 1 * 1.4455 / self.current_state.get_current_step_duration().seconds
        print(f"pb speed = {pbar_speed}")
        self.pbar_break_progress.configure(determinate_speed=pbar_speed)
        self.pbar_break_progress.set(0)
        self.pbar_break_progress.start()
        self.deiconify()

        for i in range(100):
            self.attributes("-alpha", i / 100)
            time.sleep(0.006)

    def set_lbl_remaining_time_text(self, elapsed_time: datetime.timedelta):
        self.remaining_break_time.set(f"Remaining break time: {elapsed_time.seconds} seconds")
