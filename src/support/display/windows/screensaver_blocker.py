"""Windows-only screensaver blocker based on the SetThreadExecutionState API (kernel32)."""

import ctypes

from support.logger import logger

# Execution state flags from winbase.h
_ES_CONTINUOUS = 0x80000000
_ES_DISPLAY_REQUIRED = 0x00000002


class WindowsScreensaverBlocker:
    """Blocks the screensaver and display sleep via SetThreadExecutionState.

    The OS binds the execution state to the calling thread, so block() and
    release() must be called from the same thread (the controller main loop).
    """

    def __init__(self):
        self.__is_blocked = False
        logger.debug('WindowsScreensaverBlocker initialized')

    def block(self) -> None:
        """Prevent the screensaver and display sleep until release()."""
        logger.trace('WindowsScreensaverBlocker: block')
        if self.__is_blocked:
            logger.debug('WindowsScreensaverBlocker: already blocked')
            return
        previous_state = ctypes.windll.kernel32.SetThreadExecutionState(_ES_CONTINUOUS | _ES_DISPLAY_REQUIRED)
        if previous_state:
            self.__is_blocked = True
            logger.debug('WindowsScreensaverBlocker: screensaver blocked')
        else:
            logger.error('WindowsScreensaverBlocker: SetThreadExecutionState failed on block')

    def release(self) -> None:
        """Restore the default screensaver behavior."""
        logger.trace('WindowsScreensaverBlocker: release')
        if not self.__is_blocked:
            logger.debug('WindowsScreensaverBlocker: not blocked, nothing to release')
            return
        previous_state = ctypes.windll.kernel32.SetThreadExecutionState(_ES_CONTINUOUS)
        if previous_state:
            self.__is_blocked = False
            logger.debug('WindowsScreensaverBlocker: screensaver released')
        else:
            logger.error('WindowsScreensaverBlocker: SetThreadExecutionState failed on release')
