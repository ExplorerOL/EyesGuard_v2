"""Module with main widnow of application."""

import queue

import customtkinter
import pystray

from config.app_constants import APP_VERSION
from config.settings import UserSettingsData
from config.states import ModelSnapshot, StepType
from controller import Controller
from support.logger import logger
from support.resourses import ResImages
from windows.wnd_break import WndBreak
from windows.wnd_settings import WndSettings
from windows.wnd_status import WndStatus

# how often the Tk thread drains the snapshot and UI action queues
QUEUES_POLL_INTERVAL_MS = 200


class View(customtkinter.CTk):
    """Main window of application."""

    def __init__(self, initial_settings: UserSettingsData):
        """Create the view from the Model's initial settings (no own state)."""
        super().__init__()
        customtkinter.set_appearance_mode('light')
        customtkinter.set_default_color_theme('blue')

        self.image_protection_active = ResImages.img_protection_active
        self.image_protection_suspended = ResImages.img_protection_suspended
        self.image_protection_off = ResImages.img_protection_off

        # snapshots from the Model and UI actions from the tray are applied
        # in the Tk thread only (known issue 3)
        self.__snapshot_queue: queue.Queue[ModelSnapshot] = queue.Queue()
        self.__ui_action_queue: queue.Queue = queue.Queue()

        self.__wnd_settings = WndSettings(self, initial_settings)
        self.__wnd_break = WndBreak(self)
        self.__wnd_status = WndStatus(self)
        self.title(f'EyesGuard v{APP_VERSION}')

        # tray icon
        menu = (
            pystray.MenuItem('Status', self.__show_status_wnd, default=True),
            pystray.MenuItem('Settings', self.__show_settings_wnd),
            pystray.MenuItem('Exit', self.exit_app),
        )
        self.__tray_icon = pystray.Icon('name', self.image_protection_active, 'Eyes Guard', menu)
        self.__tray_icon.run_detached()

        # drain queues in the Tk thread: background threads must not touch widgets
        self.after(QUEUES_POLL_INTERVAL_MS, self.__poll_queues)

        # hide main app wnd
        self.withdraw()
        logger.trace('View: object was created')

    def __poll_queues(self):
        """Drain queues in the Tk thread and reschedule the next poll."""
        logger.trace('View: __poll_queues')
        self.__drain_ui_actions()
        self.__drain_snapshots()
        self.after(QUEUES_POLL_INTERVAL_MS, self.__poll_queues)

    def __drain_ui_actions(self):
        """Execute queued UI actions (window show/hide, exit) in the Tk thread."""
        while True:
            try:
                action = self.__ui_action_queue.get_nowait()
            except queue.Empty:
                break
            action()

    def __drain_snapshots(self):
        """Apply the freshest Model snapshot to all windows in the Tk thread."""
        latest_snapshot = None
        while True:
            try:
                latest_snapshot = self.__snapshot_queue.get_nowait()
            except queue.Empty:
                break
        if latest_snapshot is not None:
            self.__apply_snapshot(latest_snapshot)

    def __apply_snapshot(self, snapshot: ModelSnapshot):
        """Update windows and tray icon values from a Model snapshot."""
        self.__wnd_status.update(snapshot)
        self.__wnd_settings.update(snapshot)
        self.__wnd_break.update(snapshot)
        self.__update_tray_icon_values(snapshot)

    def submit_snapshot(self, snapshot: ModelSnapshot):
        """Enqueue a Model snapshot; thread-safe (called from the controller thread)."""
        self.__snapshot_queue.put(snapshot)

    def __show_status_wnd(self):
        """Show status wnd (called from the tray thread: enqueue the action)."""
        logger.trace('View: show status wnd')
        self.__ui_action_queue.put(self.__wnd_status.show)

    def __show_settings_wnd(self):
        """Show settings wnd (called from the tray thread: enqueue the action)."""
        logger.trace('View: show settings wnd')
        self.__ui_action_queue.put(self.__wnd_settings.show)

    def show_notification(self, title: str, text: str):
        """Show a tray notification (pystray calls are thread-safe)."""
        logger.trace('View: show_notification')
        self.__tray_icon.notify(title, text)

    def set_controller(self, controller: Controller):
        """Assigning controller to view."""
        self.controller = controller
        logger.trace('View: controller was set')

    def exit_app(self):
        """Exit from app (called from the tray thread: enqueue the action)."""
        self.__ui_action_queue.put(self.__shutdown)

    def __shutdown(self):
        """Actual shutdown, always executed in the Tk thread."""
        logger.trace('View: __shutdown')
        self.controller.stop()
        self.__tray_icon.visible = False
        self.__tray_icon.stop()
        self.quit()

    def notify_engine_crashed(self):
        """Show a tray notification when the timer engine has crashed."""
        logger.error('View: timer engine crashed')
        self.__tray_icon.notify('Timer engine stopped unexpectedly! See logs for details.', 'Attention!')

    def apply_view_user_settings(self):
        logger.trace('View: applying new settings')
        settings = self.__get_user_settings_from_wnd_settings()
        if settings is None:
            logger.error('View: reading settings from ui failed, apply skipped')
            return
        self.controller.submit_apply_settings(settings)

    def __get_user_settings_from_wnd_settings(self) -> UserSettingsData | None:
        """Get data from all widgets with settings; None when the form is invalid."""
        ui_settings_data = UserSettingsData()
        try:
            ui_settings_data.work_duration = int(self.__wnd_settings.work_duration_value.get())
            ui_settings_data.break_duration = int(self.__wnd_settings.break_duration_value.get())
            ui_settings_data.activity_timeout = int(self.__wnd_settings.activity_timeout_value.get())
            ui_settings_data.volume = int(self.__wnd_settings.slider_volume.get())
            ui_settings_data.protection_status = str(self.__wnd_settings.chbox_protection_status_value.get())
            ui_settings_data.sounds = str(self.__wnd_settings.chbox_sounds_value.get())
            ui_settings_data.notifications = str(self.__wnd_settings.chbox_notifications_value.get())
            ui_settings_data.protection_status = str(self.__wnd_settings.chbox_protection_status_value.get())
            ui_settings_data.screensaver_block = str(self.__wnd_settings.chbox_screensaver_block_value.get())
            ui_settings_data.suspend_on_video = str(self.__wnd_settings.chbox_suspend_on_video_value.get())
            ui_settings_data.reset_work_time_in_idle = str(
                self.__wnd_settings.chbox_reset_work_time_in_idle_value.get()
            )
        # empty entries raise ValueError, missing widgets raise TypeError (known issue 18)
        except (TypeError, ValueError) as error:
            logger.error(f'Error occuired while reading settings from ui: {error}')
            return None

        logger.info(f'Settings read from ui: {ui_settings_data!s}')

        return ui_settings_data

    def show_wnd_break(self):
        self.__ui_action_queue.put(self.__wnd_break.show)

    def hide_wnd_break(self):
        self.__ui_action_queue.put(self.__wnd_break.hide)

    def __update_tray_icon_values(self, snapshot: ModelSnapshot) -> None:
        logger.trace('View: update_tray_icon_values')
        self.__tray_icon.title = f'Time until break: {snapshot.remaining_working_time_to_display}'
        if snapshot.step_type == StepType.off_mode:
            logger.debug('View: off cond')
            self.__tray_icon.title = 'Protection off'
            self.__tray_icon.icon = self.image_protection_off
        elif snapshot.step_type == StepType.suspended_mode:
            self.__tray_icon.icon = self.image_protection_suspended
            self.__tray_icon.title = f'Time until normal mode: {snapshot.step_remaining_time}'
        else:
            self.__tray_icon.icon = self.image_protection_active

    def switch_suspended_state(self):
        logger.trace('View: switch_suspended_state')
        self.controller.submit_suspend()

    def set_step(self, new_step_type: StepType):
        logger.trace('View: set_step')
        self.controller.submit_set_step(new_step_type)
