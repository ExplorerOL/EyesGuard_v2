"""Module with break window of application."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view import View

import datetime
import time
from tkinter import StringVar

import customtkinter

from config.app_constants import APP_VERSION
from config.states import ModelSnapshot, StepType
from support.logger import logger
from support.resourses import ResImages


class WndBreak(customtkinter.CTkToplevel):
    """Break window."""

    def __init__(self, view: View, *args, **kwargs):
        super().__init__(*args, fg_color='#000000', **kwargs)
        self.view = view

        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen
        self.attributes('-alpha', 0)
        self.geometry(f'{ws}x{hs}')
        self.title(f'EyesGuard v{APP_VERSION}')

        self.attributes('-topmost', True)
        self.attributes('-fullscreen', True)
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.bg_image = customtkinter.CTkImage(ResImages.img_break_wnd_bg, size=(ws, hs))
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image, text='')
        self.bg_image_label.grid(row=0, column=0, rowspan=2)

        self.remaining_break_time = StringVar()

        self.remaining_break_time.set('Remaining break time: 0 seconds')
        self.lbl_remain_time = customtkinter.CTkLabel(
            self,
            text='Remaining break time: ',
            text_color='GreenYellow',
            textvariable=self.remaining_break_time,
            font=customtkinter.CTkFont(size=18, weight='bold'),
        )
        self.lbl_remain_time.grid(row=1, column=0, padx=20, pady=5)

        self.grid_columnconfigure(0, weight=1)
        self.pbar_break_progress = customtkinter.CTkProgressBar(
            self, orientation='horizontal', fg_color='GreenYellow', determinate_speed=0.05
        )
        self.pbar_break_progress.grid(row=2, column=0, padx=20, pady=5, sticky='ew')

        self.protocol('WM_DELETE_WINDOW', self.on_close_action)
        self.withdraw()

    def hide(self):
        """Hide window."""
        logger.trace('Wnd break: hide')

        for i in range(100):
            self.attributes('-alpha', 1 - i / 100)
            time.sleep(0.006)
        self.withdraw()

    def on_close_action(self):
        logger.trace('Wnd break: on_close_action')

        self.view.set_step(new_step_type=StepType.work_mode)

    def show(self):
        """Show window."""
        logger.trace('Break wnd: show')

        self.deiconify()

        for i in range(100):
            self.attributes('-alpha', i / 100)
            time.sleep(0.006)

    def update(self, snapshot: ModelSnapshot):
        logger.trace('WndBreak: update')

        if snapshot.step_type == StepType.break_mode:
            if snapshot.step_elapsed_time > datetime.timedelta(seconds=0):
                pbar_value = snapshot.step_elapsed_time / snapshot.step_duration
            else:
                pbar_value = 0
            self.pbar_break_progress.set(pbar_value)
            step_duration = snapshot.break_step_duration
            elapsed_time = snapshot.step_elapsed_time
            self.remaining_break_time.set(f'Remaining break time: {step_duration - elapsed_time}')
            if self.state() != 'normal':
                self.show()
        else:
            if self.state() == 'normal':
                self.hide()

            self.pbar_break_progress.set(0)
            self.remaining_break_time.set(f'Remaining break time: {snapshot.break_step_duration}')
