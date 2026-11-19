"""Cross-platform video activity monitor factory with a safe no-op default."""

import sys
from typing import Protocol

from support.logger import logger


class PVideoActivityMonitor(Protocol):
    @property
    def is_video_playing(self) -> bool:
        """Check if video playback currently occupies the screen."""
        ...

    def reset_debounce(self) -> None:
        """Drop the debounce memory: the next poll reports the raw flag state."""
        ...


class NoopVideoActivityMonitor:
    """No-operation video activity monitor: safe default for non-Windows platforms."""

    @property
    def is_video_playing(self) -> bool:
        """Always False: the video detection is supported on Windows only."""
        logger.trace('NoopVideoActivityMonitor: is_video_playing')
        return False

    def reset_debounce(self) -> None:
        """Nothing to reset for the no-op monitor."""
        logger.trace('NoopVideoActivityMonitor: reset_debounce')


def create_video_activity_monitor(debounce_ticks: int = 5) -> PVideoActivityMonitor:
    """Create a platform-specific video activity monitor."""
    logger.trace('create_video_activity_monitor')
    if sys.platform == 'win32':
        # Factory import guarantees the Windows-only module is never imported on other platforms
        from support.display.windows.video_activity_monitor import WindowsVideoActivityMonitor

        return WindowsVideoActivityMonitor(debounce_ticks=debounce_ticks)
    return NoopVideoActivityMonitor()
