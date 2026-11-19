"""Runtime paths resolution for development and PyInstaller frozen modes."""

import os
import shutil
import sys
from pathlib import Path

APP_DIR_NAME = 'EyesGuard'


def app_dir() -> Path:
    """Directory for writable runtime data (settings, logs).

    In frozen mode it is the per-user writable directory
    %LOCALAPPDATA%/EyesGuard (known issue 36): a regular user may have no
    write permission next to the executable (e.g. Program Files). Legacy
    settings from the executable directory are migrated once. Falls back to
    the executable directory when LOCALAPPDATA is unavailable or the target
    cannot be created. In development mode it is the current working
    directory (project root).
    """
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        local_app_data = os.environ.get('LOCALAPPDATA')
        if not local_app_data:
            return exe_dir
        target_dir = Path(local_app_data) / APP_DIR_NAME
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            return exe_dir
        _migrate_legacy_settings(exe_dir=exe_dir, target_dir=target_dir)
        return target_dir
    return Path.cwd()


def _migrate_legacy_settings(exe_dir: Path, target_dir: Path) -> None:
    """Copy settings.json from the legacy exe-dir location (best effort, once)."""
    legacy_file = exe_dir / 'settings' / 'settings.json'
    target_file = target_dir / 'settings' / 'settings.json'
    if not legacy_file.is_file() or target_file.exists():
        return
    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy_file, target_file)
    except OSError:
        # migration is best-effort: the app starts with defaults on failure
        pass


def resource_dir() -> Path:
    """Directory with bundled read-only resources (res/).

    In frozen mode it is the bundle directory (sys._MEIPASS is set by
    PyInstaller for both onefile and onedir builds);
    in development mode it is the current working directory (project root).
    """
    if getattr(sys, 'frozen', False):
        return Path(getattr(sys, '_MEIPASS', ''))
    return Path.cwd()
