"""Cross-platform sound player factory with a safe no-op default."""

import sys
from pathlib import Path
from typing import Protocol

from support.logger import logger


class PSoundPlayer(Protocol):
    def play(self, file_path: Path, volume: int) -> None:
        """Playing given file by Path with volume in percents (1-100)."""
        ...

    def stop(self) -> None:
        """Interrupt the current playback."""
        ...

    def close(self) -> None:
        """Release player resources (called on shutdown)."""
        ...


class NoopSoundPlayer:
    """No-operation sound player: safe default for non-Windows platforms."""

    def play(self, file_path: Path, volume: int) -> None:
        """Skip playing: sounds are supported on Windows only."""
        logger.trace('NoopSoundPlayer: play')
        logger.debug(f'NoopSoundPlayer: skipping sound {file_path} with volume {volume}')

    def stop(self) -> None:
        """Nothing to stop for the no-op player."""
        logger.trace('NoopSoundPlayer: stop')

    def close(self) -> None:
        """Nothing to close for the no-op player."""
        logger.trace('NoopSoundPlayer: close')


def create_sound_player() -> PSoundPlayer:
    """Create a platform-specific sound player."""
    logger.trace('create_sound_player')
    if sys.platform == 'win32':
        # Factory import guarantees the Windows-only module is never imported on other platforms
        from support.sound.windows.sound_player import MciSoundPlayer

        return MciSoundPlayer()
    return NoopSoundPlayer()


sound_player = create_sound_player()
