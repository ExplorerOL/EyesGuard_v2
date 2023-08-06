"""Module for settings management in application"""

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError


@dataclass
class SettingsData:
    """class for storing user settings"""

    work_duration = 45
    break_duration = 15
    sounds = "on"
    notifications = "on"
    protection_status = "on"


class SettingsDataValidator(BaseModel):
    """Validation model for settings"""

    work_duration: int = Field(default=45, gt=0, lt=101)
    break_duration: int = Field(default=15, gt=0, lt=101)
    sounds: Literal["on", "off"] = "on"
    notifications: Literal["on", "off"] = "on"
    protection_status: Literal["on", "off"] = "on"


class Settings:
    """class for managing user settings"""

    def __init__(self, file_name: str):
        self._settings = SettingsData()
        self._settings_file = Path(file_name)
        self.apply_settings_from_file()

    def _settings_to_dict(self) -> dict:
        # convertation object to dict
        settings_dict = {}
        for attr in dir(self._settings):
            if not attr.startswith("_"):
                settings_dict[attr] = getattr(self._settings, attr)
        return settings_dict

    def __repr__(self) -> str:
        # convertation object to string
        return str(self._settings_to_dict())

    def _read_settings_from_file(self) -> str:
        """reading settings from file on disk"""
        settings_str = None
        try:
            settings_str = self._settings_file.read_text("utf-8")
        except FileNotFoundError as error:
            print(error)
            print(type(error))
            return None
        except ValueError as error:
            print(error)
            print(type(error))
            return None
        return settings_str

    def _write_settings_to_file(self, settings: SettingsData) -> None:
        """writing settings from file on disk"""

    def _validate_settings_str(self, settings_str: str) -> None:
        """validation settings"""
        print(settings_str)
        if settings_str is not None:
            try:
                settings_validated = SettingsDataValidator.model_validate_json(settings_str)
                print(settings_validated)
                return settings_validated
            except ValidationError as error:
                print(error)
                print(type(error))
                return None
        return None

    def _apply_settings(self, validated_settings: SettingsDataValidator) -> None:
        """apply given settings to the app"""
        if validated_settings is not None:
            for attr in dir(self._settings):
                if not attr.startswith("_"):
                    setattr(self._settings, attr, getattr(validated_settings, attr))
                    print(attr)
                    print(getattr(self._settings, attr))

    def apply_settings_from_file(self):
        """Read, validate and apply settings"""
        settings_from_file_str = self._read_settings_from_file()
        settings_validated = self._validate_settings_str(settings_from_file_str)
        self._apply_settings(settings_validated)

    def save_settings_to_file(self):
        """Save settings to file"""
        settings_dict = self._settings_to_dict()
        print(settings_dict)
        print(type(settings_dict))
        try:
            settings_validated = SettingsDataValidator.model_validate(settings_dict)
        except ValidationError as error:
            print(error)
            print(type(error))
            return

        settings_json = settings_validated.model_dump_json(indent=4)
        print(settings_json)
        self._settings_file.write_text(settings_json, encoding="utf-8")

    def change_protection_state(self):
        """Change protection status"""
        if self._settings.protection_status == "on":
            self._settings.protection_status = "off"
        else:
            self._settings.protection_status = "on"
        self.save_settings_to_file()

    def get(self):
        """Return copy of settings object"""
        return copy.copy(self._settings)
