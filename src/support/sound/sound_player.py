import threading
from pathlib import Path
from typing import Protocol

import playsound

from support.logger import logger


class PSoundPlayer(Protocol):
    def play(self, file_path: Path) -> None:
        """Playing given file by Path"""
        ...

class SoundPlayer(PSoundPlayer):
    def play(self, file_path: Path) -> None:
        if not file_path.exists():
            logger.error(
                f"File {file_path} does not exist. Skipping playing sound!"
            )
            return
        threading.Thread(target=self.__play_sound, name=self.__class__.__name__, args=(file_path,)).start()

    def __play_sound(self, file_path: Path) -> None:
        try:
            playsound.playsound(sound=file_path)
        except Exception as e:
            logger.error(f'Error while playing sound!\n {e!r}')

sound_player = SoundPlayer()