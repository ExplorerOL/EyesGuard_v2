"""Module with break window of application"""
import re
import time
from tkinter import StringVar

import customtkinter
from PIL import Image, ImageTk

# from settings import Settings, SettingsData


class BreakWnd(customtkinter.CTkToplevel):
    """Break window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, fg_color="#000000", **kwargs)
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

        self.remaining_break_time = StringVar()
        self.remaining_break_time.set("Remaining break time: 123")
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

        self.pbar_break_progress.start()
