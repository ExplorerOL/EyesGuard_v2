"""Module with settings window of application."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view import View

import re
import time
from tkinter import StringVar

import customtkinter
from PIL import ImageTk

from config.app_constants import APP_VERSION, APP_YEAR
from config.settings import UserSettingsData
from config.states import ModelSnapshot, StepType
from support.logger import logger
from support.resourses import ResImages


class WndSettings(customtkinter.CTkToplevel):
    """Settings window."""

    def __init__(self, view: View, settings: UserSettingsData, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.view = view
        self.settings = settings
        wnd_width = 500
        wnd_height = 420
        border_x = 50
        border_y = 150
        self.attributes('-alpha', 0)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(
            f'{wnd_width}x{wnd_height}+{screen_width - wnd_width - border_x}+{screen_height - wnd_height - border_y}'
        )
        self.title(f'EyesGuard v{APP_VERSION} - Settings')
        self.attributes('-topmost', True)
        self.resizable(False, False)

        self.wnd_icon = ImageTk.PhotoImage(ResImages.img_protection_active)
        self.after(250, lambda: self.iconphoto(False, self.wnd_icon))

        self.configure(fg_color='LightSteelBlue')

        # images
        self.img_eyes_with_protection = customtkinter.CTkImage(self.view.image_protection_active, size=(50, 50))
        self.img_eyes_protection_suspended = customtkinter.CTkImage(self.view.image_protection_suspended, size=(50, 50))
        self.img_eyes_protection_off = customtkinter.CTkImage(self.view.image_protection_off, size=(50, 50))
        self.img_clock = customtkinter.CTkImage(ResImages.img_clock, size=(25, 25))
        self.img_gear = customtkinter.CTkImage(ResImages.img_gear, size=(25, 25))
        self.img_info = customtkinter.CTkImage(ResImages.img_info, size=(25, 25))
        self.img_sounds = customtkinter.CTkImage(ResImages.img_sounds, size=(25, 25))
        self.img_monitor = customtkinter.CTkImage(ResImages.img_monitor, size=(25, 25))

        # set grid layout 2x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # window elements
        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color='SteelBlue')
        self.navigation_frame.grid(row=0, column=0, sticky='nsew')

        self.navigation_frame_lbl_title = customtkinter.CTkLabel(
            self.navigation_frame,
            text='   EyesGuard',
            text_color='White',
            image=self.img_eyes_with_protection,
            compound='left',
            font=customtkinter.CTkFont(size=18, weight='bold'),
        )
        self.navigation_frame_lbl_title.grid(row=0, column=0, padx=20, pady=5)

        self.navigation_frame_lbl_description = customtkinter.CTkLabel(
            self.navigation_frame,
            text='Cares about your vision',
            text_color='GreenYellow',
            compound='center',
            font=customtkinter.CTkFont(size=13, weight='bold'),
        )
        self.navigation_frame_lbl_description.grid(row=1, column=0, padx=0, pady=1)

        self.btn_time_settings = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=5,
            border_width=1,
            text='Time settings',
            font=('', 14, 'bold'),
            fg_color='LightSteelBlue',
            text_color=('gray10', 'gray90'),
            hover_color=('LightSkyBlue', 'gray30'),
            border_color='LightSteelBlue',
            # mage=self.image,
            anchor='w',
            command=self.event_btn_time_settings_click,
            image=self.img_clock,
        )
        self.btn_time_settings.grid(row=3, column=0, sticky='ew')

        self.btn_general_settings = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=5,
            border_width=1,
            text='General',
            font=('', 14, 'bold'),
            fg_color='transparent',
            text_color=('gray10', 'gray90'),
            hover_color=('LightSkyBlue', 'gray30'),
            border_color='LightSteelBlue',
            anchor='w',
            command=self.event_btn_general_settings_click,
            image=self.img_gear,
        )
        self.btn_general_settings.grid(row=2, column=0, sticky='ew')

        self.btn_sounds_settings = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=5,
            border_width=1,
            text='Sounds',
            font=('', 14, 'bold'),
            fg_color='transparent',
            text_color=('gray10', 'gray90'),
            hover_color=('LightSkyBlue', 'gray30'),
            border_color='LightSteelBlue',
            anchor='w',
            command=self.event_btn_sounds_settings_click,
            image=self.img_sounds,
        )
        self.btn_sounds_settings.grid(row=5, column=0, sticky='ew')

        self.btn_display_settings = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=5,
            border_width=1,
            text='Display',
            font=('', 14, 'bold'),
            fg_color='transparent',
            text_color=('gray10', 'gray90'),
            hover_color=('LightSkyBlue', 'gray30'),
            border_color='LightSteelBlue',
            anchor='w',
            command=self.event_btn_display_settings_click,
            image=self.img_monitor,
        )
        self.btn_display_settings.grid(row=4, column=0, sticky='ew')

        self.btn_about = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=5,
            border_width=1,
            text='About',
            font=('', 14, 'bold'),
            fg_color='transparent',
            text_color=('gray10', 'gray90'),
            hover_color=('LightSkyBlue', 'gray30'),
            border_color='LightSteelBlue',
            anchor='w',
            command=self.event_btn_about_click,
            image=self.img_info,
        )
        self.btn_about.grid(row=6, column=0, sticky='ew')

        # --- create time settings frame ---
        self.frame_time_settings = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent')

        # work duratrion setting
        self.lbl_work_duration = customtkinter.CTkLabel(
            self.frame_time_settings, text='Work duration (minutes)', font=('', 13)
        )
        self.lbl_work_duration.grid(row=0, column=0, padx=(20, 5), pady=10, sticky='w')

        self.work_duration_value = StringVar()
        self.work_duration_value.set(self.settings.work_duration)
        verify_cmd_work_duration = (self.register(self.is_valid_duration_entry), '%P')
        self.entry_work_duration = customtkinter.CTkEntry(
            self.frame_time_settings,
            width=70,
            textvariable=self.work_duration_value,
            justify='center',
            validate='key',
            validatecommand=verify_cmd_work_duration,
        )
        self.entry_work_duration.grid(row=0, column=1, padx=(5, 15), pady=10, sticky='w')

        # break duratrion setting
        self.lbl_break_duration = customtkinter.CTkLabel(
            self.frame_time_settings, text='Break duration (minutes)', font=('', 13)
        )
        self.lbl_break_duration.grid(row=1, column=0, padx=(20, 5), pady=10, sticky='w')

        self.break_duration_value = StringVar()
        self.break_duration_value.set(self.settings.break_duration)
        verify_cmd_break_duration = (self.register(self.is_valid_duration_entry), '%P')
        self.entry_break_duration = customtkinter.CTkEntry(
            self.frame_time_settings,
            width=70,
            textvariable=self.break_duration_value,
            justify='center',
            validate='key',
            validatecommand=verify_cmd_break_duration,
        )
        self.entry_break_duration.grid(row=1, column=1, padx=(5, 15), pady=10, sticky='w')

        # activity timeout setting
        self.lbl_activity_timeout = customtkinter.CTkLabel(
            self.frame_time_settings, text='Activity timeout (seconds)', font=('', 13)
        )
        self.lbl_activity_timeout.grid(row=2, column=0, padx=(20, 5), pady=10, sticky='w')

        self.activity_timeout_value = StringVar()
        self.activity_timeout_value.set(self.settings.activity_timeout)
        verify_cmd_activity_timeout = (self.register(self.is_valid_activity_timeout_entry), '%P')
        self.entry_activity_timeout = customtkinter.CTkEntry(
            self.frame_time_settings,
            width=70,
            textvariable=self.activity_timeout_value,
            justify='center',
            validate='key',
            validatecommand=verify_cmd_activity_timeout,
        )
        self.entry_activity_timeout.grid(row=2, column=1, padx=(5, 15), pady=10, sticky='w')

        # reset work time in idle mode setting
        self.chbox_reset_work_time_in_idle_value = customtkinter.StringVar(value=self.settings.reset_work_time_in_idle)
        self.chbox_reset_work_time_in_idle = customtkinter.CTkCheckBox(
            self.frame_time_settings,
            text='Reset working time in idle mode',
            variable=self.chbox_reset_work_time_in_idle_value,
            onvalue='on',
            offvalue='off',
            font=('', 13),
        )
        self.chbox_reset_work_time_in_idle.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky='w')

        # --- create general settings frame ---
        self.frame_general_settings = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent')

        # protextion status setting
        self.chbox_protection_status_value = customtkinter.StringVar(value=self.settings.protection_status)
        self.chbox_protection_status = customtkinter.CTkCheckBox(
            self.frame_general_settings,
            text='Protection status',
            variable=self.chbox_protection_status_value,
            onvalue='on',
            offvalue='off',
            font=('', 13),
        )
        self.chbox_protection_status.grid(row=0, column=0, padx=20, pady=10, sticky='ew')

        # notifications setting
        self.chbox_notifications_value = customtkinter.StringVar(value=self.settings.notifications)
        self.chbox_notifications = customtkinter.CTkCheckBox(
            self.frame_general_settings,
            text='Notifications enabled',
            variable=self.chbox_notifications_value,
            onvalue='on',
            offvalue='off',
            font=('', 13),
        )
        # Temporaly not used
        # self.chbox_notifications.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # --- create sounds settings frame ---
        self.frame_sounds_settings = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent')
        self.frame_sounds_settings.grid_columnconfigure(1, weight=1)

        # sounds on/off setting (moved from the General tab)
        self.chbox_sounds_value = customtkinter.StringVar(value=self.settings.sounds)
        self.chbox_sounds = customtkinter.CTkCheckBox(
            self.frame_sounds_settings,
            text='Sounds enabled',
            variable=self.chbox_sounds_value,
            onvalue='on',
            offvalue='off',
            font=('', 13),
        )
        self.chbox_sounds.grid(row=0, column=0, padx=20, pady=10, sticky='ew')

        # sounds volume setting
        self.lbl_volume = customtkinter.CTkLabel(
            self.frame_sounds_settings,
            text=f'Volume: {self.settings.volume} %',
            font=('', 13),
        )
        self.lbl_volume.grid(row=1, column=0, padx=20, pady=10)

        self.slider_volume = customtkinter.CTkSlider(
            self.frame_sounds_settings,
            from_=1,
            to=100,
            number_of_steps=99,
            command=self.event_volume_slider_move,
        )
        self.slider_volume.set(self.settings.volume)
        self.slider_volume.grid(row=1, column=1, padx=20, pady=20, sticky='ew')

        # --- create display settings frame ---
        self.frame_display_settings = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent')
        self.frame_display_settings.grid_columnconfigure(1, weight=1)

        # screensaver block setting
        self.chbox_screensaver_block_value = customtkinter.StringVar(value=self.settings.screensaver_block)
        self.chbox_screensaver_block = customtkinter.CTkCheckBox(
            self.frame_display_settings,
            text='Block screensaver during breaks',
            variable=self.chbox_screensaver_block_value,
            onvalue='on',
            offvalue='off',
            font=('', 13),
        )
        self.chbox_screensaver_block.grid(row=0, column=0, padx=20, pady=10, sticky='ew')

        # suspend on video playback setting
        self.chbox_suspend_on_video_value = customtkinter.StringVar(value=self.settings.suspend_on_video)
        self.chbox_suspend_on_video = customtkinter.CTkCheckBox(
            self.frame_display_settings,
            text='Switch to idle mode on video playback',
            variable=self.chbox_suspend_on_video_value,
            onvalue='on',
            offvalue='off',
            font=('', 13),
        )
        self.chbox_suspend_on_video.grid(row=1, column=0, padx=20, pady=10, sticky='ew')

        # --- create frame about---
        self.frame_about = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent')
        self.frame_about.grid_columnconfigure(1, weight=1)

        self.lbl_about_text = (
            f'\nEyesGuard v{APP_VERSION}\n\nAuthor: Dmitry Vorobjev\nSite: www.eyesguard.ru\n'
            f'E-mail: eyesguard@yandex.ru\nLicense: © GPL v3\nYear: {APP_YEAR}'
        )
        self.lbl_about = customtkinter.CTkLabel(self.frame_about, text=self.lbl_about_text, justify='left')
        self.lbl_about.grid(row=1, column=0, padx=20, pady=10, sticky='e')

        # --- create left footer frame ---
        self.frame_footer_left = customtkinter.CTkFrame(self, corner_radius=0, fg_color='SteelBlue', height=50)

        self.frame_footer_left.grid(row=1, column=0, sticky='sew')

        # --- create right footer frame ---
        self.frame_footer_right = customtkinter.CTkFrame(self, corner_radius=0, fg_color='transparent', height=50)
        self.frame_footer_right.grid_columnconfigure(0, weight=1)
        self.frame_footer_right.grid_columnconfigure(1, weight=1)
        self.frame_footer_right.grid(row=1, column=1, sticky='new')

        self.btn_apply = customtkinter.CTkButton(
            self.frame_footer_right,
            text='Apply',
            width=50,
            fg_color='Green',
            hover_color='DarkGreen',
            command=self.apply_ui_settings,
        )
        self.btn_apply.grid(row=0, column=0, padx=30, pady=10, sticky='ew')

        self.discrad = customtkinter.CTkButton(self.frame_footer_right, text='Hide', width=50, command=self.hide)
        self.discrad.grid(row=0, column=1, padx=30, pady=10, sticky='ew')

        # actions after elements creation
        self.bind('<FocusIn>', self.on_focus_in)
        self.protocol('WM_DELETE_WINDOW', self.hide)
        self.event_btn_time_settings_click()
        self.withdraw()

    def on_focus_in(self, event):
        """Actions on focus at window."""

    def on_focus_out(self, event):
        """Actions on focus out of window."""

    def hide(self):
        """Hide window."""
        for i in range(100):
            self.attributes('-alpha', 1 - i / 100)
            time.sleep(0.006)
        self.withdraw()

    def show(self):
        """Show window."""
        self.deiconify()

        for i in range(100):
            self.attributes('-alpha', i / 100)
            time.sleep(0.006)

    def is_valid_duration_entry(self, value: str):
        result = re.match('^[1-9][0-9]{0,1}$|^$', value) is not None
        return result

    def is_valid_activity_timeout_entry(self, value: str):
        result = re.match('^[1-9][0-9]{0,2}$|^$', value) is not None
        return result

    def update_protection_status_image(self, snapshot: ModelSnapshot):
        """Updating protection status at settings window."""
        match snapshot.step_type:
            case StepType.off_mode:
                self.navigation_frame_lbl_title.configure(image=self.img_eyes_protection_off)
                self.navigation_frame_lbl_description.configure(text='Protection off!', text_color='Black')
            case StepType.suspended_mode:
                self.navigation_frame_lbl_title.configure(image=self.img_eyes_protection_suspended)
                self.navigation_frame_lbl_description.configure(text='Protection suspended!', text_color='Tomato')
            case _:
                self.navigation_frame_lbl_title.configure(image=self.img_eyes_with_protection)
                self.navigation_frame_lbl_description.configure(
                    text='Cares about your vision', text_color='GreenYellow'
                )

    def update(self, snapshot: ModelSnapshot):
        """Updating settings window elements from a model snapshot."""
        logger.trace('Settings wnd: update function started')
        logger.debug(f'Model settings: {snapshot.user_settings}')

        user_settings = snapshot.user_settings
        self.work_duration_value.set(str(user_settings.work_duration))
        self.break_duration_value.set(str(user_settings.break_duration))
        self.activity_timeout_value.set(str(user_settings.activity_timeout))
        self.slider_volume.set(user_settings.volume)
        self.lbl_volume.configure(text=f'Volume: {user_settings.volume} %')
        self.chbox_sounds_value.set(value=user_settings.sounds)
        self.chbox_notifications_value.set(value=user_settings.notifications)
        self.chbox_protection_status_value.set(value=user_settings.protection_status)
        self.chbox_screensaver_block_value.set(value=user_settings.screensaver_block)
        self.chbox_suspend_on_video_value.set(value=user_settings.suspend_on_video)
        self.chbox_reset_work_time_in_idle_value.set(value=user_settings.reset_work_time_in_idle)

        self.update_protection_status_image(snapshot)

    def select_frame_by_name(self, name: str) -> None:
        self.btn_time_settings.configure(fg_color='LightSteelBlue' if name == 'frame_time_settings' else 'transparent')
        self.btn_general_settings.configure(
            fg_color='LightSteelBlue' if name == 'frame_general_settings' else 'transparent'
        )
        self.btn_sounds_settings.configure(
            fg_color='LightSteelBlue' if name == 'frame_sounds_settings' else 'transparent'
        )
        self.btn_display_settings.configure(
            fg_color='LightSteelBlue' if name == 'frame_display_settings' else 'transparent'
        )
        self.btn_about.configure(fg_color='LightSteelBlue' if name == 'frame_about' else 'transparent')

        # show selected frame
        if name == 'frame_time_settings':
            self.frame_time_settings.grid(row=0, column=1, sticky='nsew')
        else:
            self.frame_time_settings.grid_forget()
        if name == 'frame_general_settings':
            self.frame_general_settings.grid(row=0, column=1, sticky='nsew')
        else:
            self.frame_general_settings.grid_forget()
        if name == 'frame_sounds_settings':
            self.frame_sounds_settings.grid(row=0, column=1, sticky='nsew')
        else:
            self.frame_sounds_settings.grid_forget()
        if name == 'frame_display_settings':
            self.frame_display_settings.grid(row=0, column=1, sticky='nsew')
        else:
            self.frame_display_settings.grid_forget()
        if name == 'frame_about':
            self.frame_about.grid(row=0, column=1, sticky='nsew')
        else:
            self.frame_about.grid_forget()

    def event_btn_time_settings_click(self) -> None:
        self.select_frame_by_name('frame_time_settings')

    def event_btn_general_settings_click(self) -> None:
        self.select_frame_by_name('frame_general_settings')

    def event_btn_sounds_settings_click(self) -> None:
        self.select_frame_by_name('frame_sounds_settings')

    def event_btn_display_settings_click(self) -> None:
        self.select_frame_by_name('frame_display_settings')

    def event_volume_slider_move(self, value: float) -> None:
        """Update the volume label while the slider is moving."""
        self.lbl_volume.configure(text=f'Volume: {int(value)} %')

    def event_btn_about_click(self) -> None:
        self.select_frame_by_name('frame_about')

    def apply_ui_settings(self):
        """Coll method of view for applying new settings."""
        self.view.apply_view_user_settings()
