"""Module with break window of application"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view import View

import datetime
import re
import time
from tkinter import StringVar

import customtkinter
from PIL import Image, ImageTk

import data.wnd_values as wnd_values
from logger import logger
from states import CurrentState, StepType

# from settings import Settings, SettingsData


class WndBreak(customtkinter.CTkToplevel):
    """Break window"""

    def __init__(self, view: View, current_state: CurrentState, *args, **kwargs):
        super().__init__(*args, fg_color="#000000", **kwargs)
        self.current_state = current_state
        self.view = view

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

        self.protocol("WM_DELETE_WINDOW", self.on_close_action)
        self.withdraw()

    def hide(self):
        """Hide window"""
        logger.trace("Wnd break: hide")
        self.pbar_break_progress.stop()
        self.pbar_break_progress.set(1)

        for i in range(100):
            self.attributes("-alpha", 1 - i / 100)
            time.sleep(0.006)
        self.withdraw()

    def on_close_action(self):
        logger.trace("Wnd break: on_close_action")
        self.view.set_step(new_step_type=StepType.work_mode)

    def show(self):
        """Show window"""
        logger.trace("Break wnd: show")

        # self.update_values(self.current_state)

        # self.pbar_break_progress.set(0)
        # self.pbar_break_progress.start()
        self.deiconify()

        for i in range(100):
            self.attributes("-alpha", i / 100)
            time.sleep(0.006)

    # def set_lbl_remaining_time_text(self, elapsed_time: datetime.timedelta):
    #     self.remaining_break_time.set(f"Remaining break time: {elapsed_time.seconds} seconds")

    def update_values(self, new_values: wnd_values.WndBreakValues):
        self.remaining_break_time.set(new_values.remaining_time_str)
        # self.__set_pbar_speed(current_state=new_values.remaining_time_pbar_value)
        logger.debug(f"WndBreak: pb speed = {new_values.remaining_time_pbar_value}")
        # self.pbar_break_progress.configure(determinate_speed=new_values.remaining_time_pbar_value)
        self.pbar_break_progress.set(new_values.remaining_time_pbar_value)

    # def __set_pbar_speed(self, current_state: CurrentState):
    #     logger.trace("WndBreak: __set_pbar_speed")
    #     logger.debug(
    #         f"WndBreak: current_state.current_step_duration.seconds = {current_state.current_step_duration.seconds}"
    #     )

    #     pbar_speed = 1
    #     if current_state.current_step_duration.seconds > 0:
    #         pbar_speed = 1 * 1.4455 / current_state.current_step_duration.seconds
