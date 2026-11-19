"""Windows-only sound player based on the MCI API (winmm) with volume support."""

import ctypes
from ctypes import wintypes
from pathlib import Path
from threading import Thread
from uuid import uuid4

from support.logger import logger

# MCI volume scale: 10..1000 corresponds to 1..100 percents
_MCI_VOLUME_PER_PERCENT = 10


class MciSoundPlayerError(Exception):
    """Raised when an MCI command returns an error code."""


class MciSoundPlayer:
    """Plays MP3 files via the Windows MCI API (winmm) with per-play volume."""

    def __init__(self):
        ctypes.windll.winmm.mciSendStringW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.LPWSTR,
            wintypes.UINT,
            wintypes.HANDLE,
        ]
        ctypes.windll.winmm.mciGetErrorStringW.argtypes = [wintypes.DWORD, wintypes.LPWSTR, wintypes.UINT]

    def play(self, file_path: Path, volume: int) -> None:
        """Playing given file by Path with volume in percents (1-100)."""
        logger.trace('MciSoundPlayer: play')
        if not file_path.exists():
            logger.error(f'File {file_path} does not exist. Skipping playing sound!')
            return
        Thread(
            target=self.__play_sound_safely,
            name=self.__class__.__name__,
            args=(file_path, volume),
        ).start()

    def __play_sound_safely(self, file_path: Path, volume: int) -> None:
        """Run the full MCI sequence: open, setaudio, play, close. Safe default on errors."""
        logger.trace('MciSoundPlayer: __play_sound_safely')
        alias = f'eg_{uuid4().hex}'
        opened = False
        try:
            self.__send_mci_command(f'open "{file_path}" type mpegvideo alias {alias}')
            opened = True
            try:
                self.__send_mci_command(f'setaudio {alias} volume to {volume * _MCI_VOLUME_PER_PERCENT}')
            except MciSoundPlayerError as error:
                # setaudio may be unsupported by the driver: play with the default volume instead
                logger.warning(f'MciSoundPlayer: setaudio failed, playing with default volume: {error}')
            self.__send_mci_command(f'play {alias} wait')
        # Any playback error must not crash the app (safe default: skip sound)
        except Exception as e:  # noqa: BLE001
            logger.error(f'Error while playing sound!\n {e!r}')
        finally:
            # close only a successfully opened alias: closing a failed one would add error noise
            if opened:
                try:
                    self.__send_mci_command(f'close {alias}')
                except MciSoundPlayerError as error:
                    logger.warning(f'MciSoundPlayer: failed to close MCI alias {alias}: {error}')

    def __send_mci_command(self, command: str) -> None:
        """Send an MCI command via winmm; raise MciSoundPlayerError on failure."""
        logger.trace('MciSoundPlayer: __send_mci_command')
        buffer_length = 600
        buffer = ctypes.create_unicode_buffer(buffer_length)
        error_code = int(ctypes.windll.winmm.mciSendStringW(command, buffer, buffer_length - 1, 0))
        if error_code:
            error_buffer = ctypes.create_unicode_buffer(buffer_length)
            ctypes.windll.winmm.mciGetErrorStringW(error_code, error_buffer, buffer_length - 1)
            raise MciSoundPlayerError(f'Error {error_code} for command "{command}": {error_buffer.value}')
