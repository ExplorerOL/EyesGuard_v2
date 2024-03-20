"""Module with status window of application"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view import View

import datetime
import time

import customtkinter
from PIL import Image

import data.wnd_values as wnd_values
from logger import logger
from model import Model
from settings import Settings, UserSettingsData
from states import StepType
from windows.wnd_break import WndBreak


class WndStatus(customtkinter.CTkToplevel):
    """Status window"""

    def __init__(self, view: View, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.settings = settings
        # self.wnd_break = break_wnd
        self.view = view

        wnd_width = 250
        wnd_height = 210
        border_x = 50
        border_y = 50
        self.attributes("-alpha", 0)
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
            self, text="Time until break:  - - -", font=("", 13, "bold")
        )
        self.lbl_time_until_break.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")

        # progress bar time until break
        self.pbar_time_until_break = customtkinter.CTkProgressBar(
            self, orientation="horizontal", height=20, fg_color="#3B8ED0", progress_color="GreenYellow"
        )
        self.pbar_time_until_break.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        logger.debug(
            f' ---------------- progress_color = {self.pbar_time_until_break.cget("progress_color")}'
        )
        # button change protection state
        self.btn_change_suspended_state = customtkinter.CTkButton(
            self,
            text="Protection active",
            text_color="GreenYellow",
            command=self.__btn_change_protection_state_action,
            height=30,
            width=120,
            corner_radius=50,
            image=customtkinter.CTkImage(light_image=self.img_eyes_with_protection, size=(25, 25)),
            border_spacing=0,
            font=("", 13, "bold"),
        )
        self.btn_change_suspended_state.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # button take a break
        self.btn_take_break = customtkinter.CTkButton(
            self,
            text="Take a break now",
            text_color="GreenYellow",
            command=self.__btn_take_break_action,
            height=30,
            width=150,
            corner_radius=50,
            image=customtkinter.CTkImage(light_image=self.img_check_mark, size=(30, 30)),
            border_spacing=0,
            font=("", 13, "bold"),
        )
        self.btn_take_break.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.bind("<FocusOut>", self.on_focus_out)
        self.protocol("WM_DELETE_WINDOW", self.hide)
        # self.update_view()
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
        print("Showing status wnd")
        # self.update_view()
        self.deiconify()

        for i in range(100):
            self.attributes("-alpha", i / 100)
            time.sleep(0.006)

    def __btn_change_protection_state_action(self):
        """Action for pressing changeing protection state button"""
        self.view.switch_suspended_state()
        # self.update_view()

    def __btn_take_break_action(self):
        """Action for pressing button for taking a break"""
        logger.trace("Wnd_status: __btn_take_break_action")
        self.view.set_step(StepType.break_mode)

    def update(self, model: Model):
        """Updating status window elements states"""
        logger.trace("Wnd status: update")
        # self.lbl_time_until_break.configure(
        #     text=f"Time until break: {model.remaining_working_time_to_display}"
        # )
        if model.time_for_work_full > datetime.timedelta(seconds=0):
            pbar_value = 1 - model.remaining_working_time_to_display / model.time_for_work_full
        else:
            pbar_value = 0
        self.pbar_time_until_break.set(value=pbar_value)

        # if new_values.protection_status == "off":

        match model.current_state.current_step_type:
            case StepType.off_mode:
                # if update permanently - abberrations of button present
                if self.btn_change_suspended_state.cget("state") != "disabled":
                    self.btn_take_break.configure(state="disabled")
                    self.lbl_time_until_break.configure(text="Time until break: ∞ : ∞ : ∞")
                    self.btn_change_suspended_state.configure(
                        text="Protection off",
                        # text_color="",
                        image=customtkinter.CTkImage(
                            light_image=self.view.image_protection_off, size=(30, 30)
                        ),
                        require_redraw=True,
                        state="disabled",
                    )
                    # self.btn_change_suspended_state.configure()
                    self.pbar_time_until_break.set(0)

                # if self.btn_change_suspended_state.cget("state") != "disabled":

            case StepType.suspended_mode:
                if self.btn_take_break.cget("state") != "disabled":
                    self.btn_take_break.configure(state="disabled")

                    # button configuring is here for preventing visual artefacts
                    # if update permanently - abberrations of button present
                    self.btn_change_suspended_state.configure(
                        text="Protection suspended",
                        text_color="Tomato",
                        # hover_color="yellow",
                        image=customtkinter.CTkImage(
                            light_image=self.view.image_protection_suspended, size=(30, 30)
                        ),
                        require_redraw=True,
                    )
                self.lbl_time_until_break.configure(
                    text=f"Time without protection: {model.current_state.current_step_duration - model.current_state.current_step_elapsed_time}"
                )
            case _:
                self.lbl_time_until_break.configure(
                    text=f"Time until break: {model.remaining_working_time_to_display}"
                )
                self.btn_change_suspended_state.configure(
                    text="Protection active",
                    text_color="GreenYellow",
                    image=customtkinter.CTkImage(
                        light_image=self.view.image_protection_active, size=(30, 30)
                    ),
                    require_redraw=True,
                )
                # if update permanently - abberrations of button present
                if self.btn_take_break.cget("state") != "normal":
                    self.btn_take_break.configure(state="normal")

                if self.btn_change_suspended_state.cget("state") != "normal":
                    self.btn_change_suspended_state.configure(state="normal")

    # def update(self, model: Model):
    #     logger.trace("Wnd status: update_values")
    #     self.lbl_time_until_break.configure(text=model.remaining_working_time_to_display)

    #     if model.time_for_work_full > datetime.timedelta(seconds=0):
    #         pbar_value = 1 - model.remaining_working_time_to_display / model.time_for_work_full
    #     else:
    #         pbar_value = 0
    #     self.pbar_time_until_break.set(value=pbar_value)

    #     # self.pbar_time_until_break.set(
    #     #     value=1 - model.remaining_working_time_to_display / model.__time_for_work_full
    #     # )

    #     # if new_values.protection_status == "off":

    #     if model.model_user_settings.protection_status == "on":
    #         self.btn_change_suspended_state.configure(
    #             text="Protection active",
    #             text_color="GreenYellow",
    #             image=customtkinter.CTkImage(light_image=self.img_eyes_with_protection, size=(30, 30)),
    #             require_redraw=True,
    #         )
    #     else:
    #         self.btn_change_suspended_state.configure(
    #             text="Protection suspended",
    #             text_color="Tomato",
    #             # hover_color="yellow",
    #             image=customtkinter.CTkImage(light_image=self.img_eyes_without_protection, size=(30, 30)),
    #             require_redraw=True,
    #         )

    #     # if new_values.protection_status == "off":
    #     #     # if update permanently - abberrations of button present
    #     #     if self.btn_take_break.cget("state") != "disabled":
    #     #         self.btn_take_break.configure(state="disabled")

    #     #     if self.btn_change_suspended_state.cget("state") != "disabled":
    #     #         self.btn_change_suspended_state.configure(state="disabled")
    #     # else:
    #     #     # if update permanently - abberrations of button present
    #     #     if self.btn_take_break.cget("state") != "normal":
    #     #         self.btn_take_break.configure(state="normal")

    #     #     if self.btn_change_suspended_state.cget("state") != "normal":
    #     #         self.btn_change_suspended_state.configure(state="normal")
