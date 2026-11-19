"""Windows-only sound player based on the MCI API (winmm) with volume support."""

import ctypes
import queue
import threading
from ctypes import wintypes
from pathlib import Path
from uuid import uuid4

from support.logger import logger

# MCI volume scale: 10..1000 corresponds to 1..100 percents
_MCI_VOLUME_PER_PERCENT = 10
_CLOSE_TIMEOUT_S = 3.0


class MciSoundPlayerError(Exception):
    """Raised when an MCI command returns an error code."""


class MciSoundPlayer:
    """Plays MP3 files via the Windows MCI API (winmm) with per-play volume.

    All playback runs in a single managed daemon worker thread (known issue
    33): repeated plays do not spawn unmanaged threads, stop() interrupts the
    current sound, close() shuts the worker down.
    """

    def __init__(self):
        ctypes.windll.winmm.mciSendStringW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.LPWSTR,
            wintypes.UINT,
            wintypes.HANDLE,
        ]
        ctypes.windll.winmm.mciGetErrorStringW.argtypes = [wintypes.DWORD, wintypes.LPWSTR, wintypes.UINT]
        self.__commands: queue.Queue = queue.Queue()
        self.__alias_lock = threading.Lock()
        self.__current_alias: str | None = None
        self.__worker = threading.Thread(target=self.__worker_loop, name='MciSoundPlayerWorker', daemon=True)
        self.__worker.start()

    def play(self, file_path: Path, volume: int) -> None:
        """Playing given file by Path with volume in percents (1-100)."""
        logger.trace('MciSoundPlayer: play')
        if not file_path.exists():
            logger.error(f'File {file_path} does not exist. Skipping playing sound!')
            return
        self.__cancel_current_playback()
        self.__commands.put((file_path, volume))

    def stop(self) -> None:
        """Interrupt the current playback and drop queued commands."""
        logger.trace('MciSoundPlayer: stop')
        with self.__commands.mutex:
            self.__commands.queue.clear()
        self.__cancel_current_playback()

    def close(self) -> None:
        """Stop playback and shut the worker thread down."""
        logger.trace('MciSoundPlayer: close')
        self.stop()
        self.__commands.put(None)
        if self.__worker.is_alive():
            self.__worker.join(timeout=_CLOSE_TIMEOUT_S)

    def __worker_loop(self) -> None:
        """Play queued sounds one by one; None sentinel ends the loop."""
        while True:
            command = self.__commands.get()
            if command is None:
                return
            file_path, volume = command
            self.__play_file_safely(file_path, volume)

    def __play_file_safely(self, file_path: Path, volume: int) -> None:
        """Run the full MCI sequence: open, setaudio, play, close. Safe default on errors."""
        logger.trace('MciSoundPlayer: __play_file_safely')
        alias = f'eg_{uuid4().hex}'
        opened = False
        try:
            with self.__alias_lock:
                self.__current_alias = alias
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
            with self.__alias_lock:
                self.__current_alias = None
            # close only a successfully opened alias: closing a failed one would add error noise
            if opened:
                try:
                    self.__send_mci_command(f'close {alias}')
                except MciSoundPlayerError as error:
                    logger.warning(f'MciSoundPlayer: failed to close MCI alias {alias}: {error}')

    def __cancel_current_playback(self) -> None:
        """Stop the currently playing alias so the blocking 'play wait' returns."""
        with self.__alias_lock:
            alias = self.__current_alias
        if alias is None:
            return
        try:
            self.__send_mci_command(f'stop {alias}')
        except MciSoundPlayerError as error:
            logger.warning(f'MciSoundPlayer: failed to stop MCI alias {alias}: {error}')

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
