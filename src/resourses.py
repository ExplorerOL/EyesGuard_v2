"""Dataclasses for resources"""

from PIL import Image


class ResImages:
    img_protection_active = Image.open("res/img/eyes_with_protection.png")
    img_protection_suspended = Image.open("res/img/eyes_without_protection.png")
    img_protection_off = Image.open("res/img/eyes_protection_off.png")

    img_check_mark = Image.open("res/img/check_mark.png")

    img_break_wnd_bg = Image.open("res/img/break_wnd_bg1.png")

    img_clock = Image.open("res/img/clock.png")
    img_gear = Image.open("res/img/gear.png")
    img_info = Image.open("res/img/info.png")
