"""Windows-only video activity monitor based on the system execution state.

Browsers and media players raise the ES_DISPLAY_REQUIRED flag while playing
video, so the aggregated system execution state is a reliable proxy for
"the screen is busy with a video".
"""

import ctypes

from support.logger import logger

# POWER_INFORMATION_LEVEL: SystemExecutionState returns aggregated ES_* flags
_SYSTEM_EXECUTION_STATE = 16
_ES_DISPLAY_REQUIRED = 0x00000002
_STATUS_SUCCESS = 0


class WindowsVideoActivityMonitor:
    """Detects video playback via CallNtPowerInformation(SystemExecutionState).

    Some players reset the idle timer periodically instead of holding the
    flag, so "video stopped" is reported only after debounce_ticks consecutive
    polls without the flag.
    """

    def __init__(self, debounce_ticks: int = 5):
        self.__debounce_ticks = debounce_ticks
        self.__ticks_without_flag = self.__debounce_ticks
        logger.debug(f'WindowsVideoActivityMonitor initialized with debounce: {debounce_ticks}')

    def __get_display_required_from_os(self) -> bool:
        """Read the aggregated ES_DISPLAY_REQUIRED flag from the OS."""
        logger.trace('WindowsVideoActivityMonitor: __get_display_required_from_os')
        try:
            execution_state = ctypes.c_ulong(0)
            status = ctypes.windll.powrprof.CallNtPowerInformation(
                _SYSTEM_EXECUTION_STATE,
                None,
                0,
                ctypes.byref(execution_state),
                ctypes.sizeof(execution_state),
            )
            if status != _STATUS_SUCCESS:
                logger.error(f'CallNtPowerInformation failed with NTSTATUS {status}')
                return False
            is_display_required = bool(execution_state.value & _ES_DISPLAY_REQUIRED)
            logger.debug(f'ES_DISPLAY_REQUIRED flag: {is_display_required}')
            return is_display_required
        # Any OS API failure must not crash the app (safe default: no video)
        except Exception as e:  # noqa: BLE001
            logger.error(f'Error getting system execution state: {e}')
            return False

    @property
    def is_video_playing(self) -> bool:
        """Check if video playback currently occupies the screen (with debounce)."""
        logger.trace('WindowsVideoActivityMonitor: is_video_playing')
        if self.__get_display_required_from_os():
            self.__ticks_without_flag = 0
            return True
        if self.__ticks_without_flag < self.__debounce_ticks:
            self.__ticks_without_flag += 1
            logger.debug(f'Video debounce: {self.__ticks_without_flag}/{self.__debounce_ticks} ticks without flag')
            return True
        return False

    def reset_debounce(self) -> None:
        """Drop the debounce memory: the next poll reports the raw flag state."""
        logger.trace('WindowsVideoActivityMonitor: reset_debounce')
        self.__ticks_without_flag = self.__debounce_ticks
