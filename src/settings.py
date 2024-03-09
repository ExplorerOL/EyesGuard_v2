"""Module for settings management in application"""

import copy
import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError


@dataclass
class SystemSettingsData:
    """class for storing system settings"""

    step_off_mode_duration = datetime.timedelta(minutes=60)
    step_notification_1_duration = datetime.timedelta(seconds=55)
    step_notification_2_duration = datetime.timedelta(seconds=5)


@dataclass
class UserSettingsData:
    """class for storing user settings"""

    work_duration = 45
    break_duration = 15
    sounds = "on"
    notifications = "on"
    protection_status = "on"

    def _settings_to_dict(self) -> dict:
        # convertation object to dict
        settings_dict = {}
        for attr in dir(self):
            if not attr.startswith("_"):
                settings_dict[attr] = getattr(self, attr)
        return settings_dict

    def __repr__(self) -> dict:
        # convertation object to string
        return self._settings_to_dict()

    def __str__(self) -> str:
        # convertation object to string
        return str(self._settings_to_dict())


class SettingsDataValidator(BaseModel):
    """Validation model for settings"""

    work_duration: int = Field(default=45, gt=0, lt=101)
    break_duration: int = Field(default=15, gt=0, lt=101)
    sounds: Literal["on", "off"] = "on"
    notifications: Literal["on", "off"] = "on"
    protection_status: Literal["on", "off"] = "on"


class Settings:
    """class for managing user settings"""

    def __init__(self, file_name: str | None = None):
        self.__user_settings = UserSettingsData()
        self.__system_settings = SystemSettingsData()
        if file_name is not None:
            self.__settings_file = Path(file_name)
            self.apply_settings_from_file()

    def _settings_to_dict(self) -> dict:
        """Convertation settings object to dict"""

        settings_dict = {}
        for attr in dir(self.__user_settings):
            if not attr.startswith("_"):
                settings_dict[attr] = getattr(self.__user_settings, attr)
        return settings_dict

    def __repr__(self) -> dict:
        """Convertation settings object to view in terminal"""

        return self._settings_to_dict()

    def __str__(self) -> str:
        """Convertation object to string"""

        return str(self._settings_to_dict())

    def _read_settings_from_file(self) -> str | None:
        """Reading settings from file on disk"""

        settings_str = None
        try:
            settings_str = self.__settings_file.read_text("utf-8")
        except FileNotFoundError as error:
            print(error)
            print(type(error))
            return None
        except ValueError as error:
            print(error)
            print(type(error))
            return None
        return settings_str

    def _write_settings_to_file(self, settings: UserSettingsData) -> None:
        """writing settings from file on disk"""

    def _validate_settings_str(self, settings_str: str) -> SettingsDataValidator | None:
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
        """Apply given settings to the app"""

        if validated_settings is not None:
            for attr in dir(self.__user_settings):
                if not attr.startswith("_"):
                    setattr(self.__user_settings, attr, getattr(validated_settings, attr))
                    print(attr)
                    print(getattr(self.__user_settings, attr))

    def apply_settings_from_file(self):
        """Read, validate and apply settings from file"""

        settings_from_file_str = self._read_settings_from_file()
        settings_validated = self._validate_settings_str(settings_from_file_str)
        self._apply_settings(settings_validated)

    def apply_settings_from_ui(self, new_settings_data: UserSettingsData):
        """Validate settings and write them to file"""
        # new_settings_dict = self._settings_to_dict()
        print(f"New settings from ui to apply: {new_settings_data}")
        print(type(new_settings_data))
        try:
            settings_validated = SettingsDataValidator.model_validate(new_settings_data.__repr__())
        except ValidationError as error:
            print(error)
            print(type(error))
            return
        self._apply_settings(settings_validated)
        self.save_settings_to_file()

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
        self.__settings_file.write_text(settings_json, encoding="utf-8")

    def change_protection_state(self):
        """Change protection status"""

        if self.__user_settings.protection_status == "on":
            self.__user_settings.protection_status = "off"
        else:
            self.__user_settings.protection_status = "on"
        self.save_settings_to_file()

    def get_settings_copy(self) -> UserSettingsData:
        """Return copy of settings object"""

        return copy.copy(self.__user_settings)

    @property
    def user_settings(self) -> UserSettingsData:
        """Return of user settings object"""

        return self.__user_settings

    @property
    def system_settings(self) -> SystemSettingsData:
        """Return of system settings object"""

        return self.__system_settings
