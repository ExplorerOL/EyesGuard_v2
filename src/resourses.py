"""Dataclasses for resources"""

from PIL import Image


class ResImages:
    image_protection_active = Image.open("res/img/eyes_with_protection.png")
    image_protection_suspended = Image.open("res/img/eyes_without_protection.png")
    image_protection_off = Image.open("res/img/eyes_protection_off.png")
