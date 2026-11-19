"""Cross-platform screensaver blocker factory with a safe no-op default."""

import sys
from typing import Protocol

from support.logger import logger


class PScreensaverBlocker(Protocol):
    def block(self) -> None:
        """Prevent the screensaver and display sleep."""
        ...

    def release(self) -> None:
        """Restore the default screensaver behavior."""
        ...


class NoopScreensaverBlocker:
    """No-operation screensaver blocker: safe default for non-Windows platforms."""

    def block(self) -> None:
        """Skip blocking: the screensaver control is supported on Windows only."""
        logger.trace('NoopScreensaverBlocker: block')
        logger.debug('NoopScreensaverBlocker: skipping screensaver block')

    def release(self) -> None:
        """Skip releasing: the screensaver control is supported on Windows only."""
        logger.trace('NoopScreensaverBlocker: release')
        logger.debug('NoopScreensaverBlocker: skipping screensaver release')


def create_screensaver_blocker() -> PScreensaverBlocker:
    """Create a platform-specific screensaver blocker."""
    logger.trace('create_screensaver_blocker')
    if sys.platform == 'win32':
        # Factory import guarantees the Windows-only module is never imported on other platforms
        from support.display.windows.screensaver_blocker import WindowsScreensaverBlocker

        return WindowsScreensaverBlocker()
    return NoopScreensaverBlocker()
