"""Module for monitoring user activity on Windows systems.

This module provides functionality to detect if a user is active or idle
based on the last input time from the Windows operating system.
"""

import ctypes
import datetime
from typing import Optional

from support.logger import logger


class LASTINPUTINFO(ctypes.Structure):
    """Structure for holding last input information from Windows API."""

    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint),
    ]


class UserActivityMonitor:
    """Monitors user activity by checking the last input time on Windows.

    This class uses Windows API calls to determine if the user has been
    active within a specified timeout period.
    """

    def __init__(self, activity_timeout: datetime.timedelta = datetime.timedelta(seconds=60)):
        """Initialize the UserActivityMonitor.

        Args:
            activity_timeout: The time duration after which the user is considered inactive.
            Defaults to 60 seconds.
        """
        self._activity_timeout: datetime.timedelta = activity_timeout
        self._idle_time_offset: datetime.timedelta = datetime.timedelta(seconds=0)
        logger.debug(f"UserActivityMonitor initialized with timeout: {activity_timeout}")

    def __get_user_idle_time_from_os(self) -> datetime.timedelta:
        """Get the user idle time from the operating system.

        Returns:
            The time duration since the last user input event.
        """
        try:
            last_input_info = LASTINPUTINFO()
            last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)

            # Get last input time from Windows API
            result = ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info))
            if not result:
                logger.warning("Failed to get last input info from Windows API")
                return datetime.timedelta(seconds=0)

            # Get system uptime using 64-bit function to avoid 49.7-day wraparound
            tick_count = ctypes.windll.kernel32.GetTickCount64()
            time_ms = tick_count - last_input_info.dwTime
            idle_time = datetime.timedelta(milliseconds=time_ms)

            logger.debug(f"User idle time: {idle_time}")
            return idle_time

        except Exception as e:
            logger.error(f"Error getting user idle time: {e}")
            # Return zero idle time as safe default
            return datetime.timedelta(seconds=0)

    @property
    def is_user_active(self) -> bool:
        """Check if the user is currently active.

        Returns:
            True if the user is active (idle time is less than timeout), False otherwise.
        """
        idle_time = self.__get_user_idle_time_from_os()
        adjusted_idle_time = idle_time - self._idle_time_offset
        is_active = adjusted_idle_time <= self._activity_timeout

        logger.debug(f"User active check: idle_time={idle_time}, "
                    f"adjusted={adjusted_idle_time}, timeout={self._activity_timeout}, "
                    f"active={is_active}")
        return is_active

    def set_activity_offset(self) -> None:
        """Set the activity offset when user is inactive.

        This method is used to adjust the idle time calculation when the user
        switches to an idle state.
        """
        if not self.is_user_active:
            self._idle_time_offset = self.__get_user_idle_time_from_os()
            logger.debug(f"Activity offset set to: {self._idle_time_offset}")

    def reset_activity_offset(self) -> None:
        """Reset the activity offset to zero.

        This method is used to reset the idle time calculation when the user
        becomes active again.
        """
        if self.is_user_active:
            self._idle_time_offset = datetime.timedelta(seconds=0)
            logger.debug("Activity offset reset to zero")
