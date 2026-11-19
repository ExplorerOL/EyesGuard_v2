"""Dataclasses for resources."""

from pathlib import Path

from PIL import Image

from support.paths import resource_dir


class ResImages:
    img_protection_active = Image.open(resource_dir() / 'res/img/eyes_with_protection.png')
    img_protection_suspended = Image.open(resource_dir() / 'res/img/eyes_without_protection.png')
    img_protection_off = Image.open(resource_dir() / 'res/img/eyes_protection_off.png')

    img_check_mark = Image.open(resource_dir() / 'res/img/check_mark.png')

    img_break_wnd_bg = Image.open(resource_dir() / 'res/img/break_wnd_bg1.png')

    img_clock = Image.open(resource_dir() / 'res/img/clock.png')
    img_gear = Image.open(resource_dir() / 'res/img/gear.png')
    img_info = Image.open(resource_dir() / 'res/img/info.png')


class ResSoundsPaths:
    notification_work = Path(resource_dir() / 'res/sounds/notification_work.mp3')
    notification_break = Path(resource_dir() / 'res/sounds/notification_break.mp3')
    notification_idle = Path(resource_dir() / 'res/sounds/notification_idle.mp3')
