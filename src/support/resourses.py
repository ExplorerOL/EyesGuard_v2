"""Dataclasses for resources."""

from pathlib import Path

from PIL import Image

from support.logger import logger
from support.paths import resource_dir

# fallback placeholder for missing or broken image files
_PLACEHOLDER_SIZE = (48, 48)
_PLACEHOLDER_COLOR = (70, 130, 180)


def load_image(relative_path: str) -> Image.Image:
    """Load an image resource as a fully loaded independent copy.

    A missing or broken file must not crash the app on import (known issue
    16): a plain placeholder is returned and the error is logged.
    """
    file_path = Path(resource_dir()) / relative_path
    try:
        with Image.open(file_path) as opened:
            opened.load()
            return opened.copy()
    except OSError as error:
        logger.error(f'ResImages: failed to load {relative_path}: {error!r}; using placeholder')
        return Image.new('RGB', _PLACEHOLDER_SIZE, color=_PLACEHOLDER_COLOR)


class ResImages:
    img_protection_active = load_image('res/img/eyes_with_protection.png')
    img_protection_suspended = load_image('res/img/eyes_without_protection.png')
    img_protection_off = load_image('res/img/eyes_protection_off.png')

    img_check_mark = load_image('res/img/check_mark.png')

    img_break_wnd_bg = load_image('res/img/break_wnd_bg1.png')

    img_clock = load_image('res/img/clock.png')
    img_gear = load_image('res/img/gear.png')
    img_info = load_image('res/img/info.png')
    img_sounds = load_image('res/img/speaker.png')

    # the monitor icon is added manually: until the file exists, the
    # placeholder fallback keeps the app importable (same as any other image)
    img_monitor = load_image('res/img/monitor.png')


class ResSoundsPaths:
    notification_work = Path(resource_dir() / 'res/sounds/notification_work.mp3')
    notification_break = Path(resource_dir() / 'res/sounds/notification_break.mp3')
    notification_idle = Path(resource_dir() / 'res/sounds/notification_idle.mp3')
