"""Runtime paths resolution for development and PyInstaller frozen modes."""

import sys
from pathlib import Path


def app_dir() -> Path:
    """Directory for writable runtime data (settings, logs).

    In frozen mode it is the directory of the executable file;
    in development mode it is the current working directory (project root).
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path.cwd()


def resource_dir() -> Path:
    """Directory with bundled read-only resources (res/).

    In frozen mode it is the PyInstaller onefile extraction folder (sys._MEIPASS);
    in development mode it is the current working directory (project root).
    """
    if getattr(sys, 'frozen', False):
        return Path(getattr(sys, '_MEIPASS', ''))
    return Path.cwd()
