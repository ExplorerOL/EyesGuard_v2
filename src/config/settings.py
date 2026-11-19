"""Module for settings management in application."""

import copy
import dataclasses
import datetime
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from support.logger import logger


class OnOffValue(Enum):
    on = 'on'
    off = 'off'


@dataclass
class SystemSettingsData:
    """class for storing system settings."""

    STEP_SUSPENDED_MODE_DURATION = datetime.timedelta(minutes=60)
    STEP_NOTIFICATION_1_DURATION = datetime.timedelta(seconds=55)
    STEP_NOTIFICATION_2_DURATION = datetime.timedelta(seconds=5)
    TIME_TICK_S = 1


@dataclass
class UserSettingsData:
    """class for storing user settings.

    All fields are annotated dataclass fields (known issue 27): the generated
    constructor and equality cover every setting.
    """

    work_duration: int = 45
    break_duration: int = 15
    activity_timeout: int = 180
    volume: int = 100
    sounds: str = OnOffValue.on.value
    notifications: str = OnOffValue.on.value
    protection_status: str = OnOffValue.on.value
    screensaver_block: str = OnOffValue.on.value
    suspend_on_video: str = OnOffValue.on.value
    reset_work_time_in_idle: str = OnOffValue.off.value

    def to_dict(self) -> dict:
        """Convert the object to a plain dict covering all dataclass fields."""
        logger.trace('UserSettingsData: to_dict')
        settings_dict = dataclasses.asdict(self)
        logger.debug(f'UserSettingsData: {settings_dict}')
        return settings_dict

    def __repr__(self) -> str:
        """Object representation as string."""
        return str(self.to_dict())

    def __str__(self) -> str:
        """Object as string."""
        return str(self.to_dict())


class SettingsDataValidator(BaseModel):
    """Validation model for settings."""

    work_duration: int = Field(default=45, gt=0, lt=101)
    break_duration: int = Field(default=15, gt=0, lt=101)
    activity_timeout: int = Field(default=180, ge=30, le=600)
    volume: int = Field(default=100, ge=1, le=100)
    sounds: Literal['on', 'off'] = 'on'
    notifications: Literal['on', 'off'] = 'on'
    protection_status: Literal['on', 'off'] = 'on'
    screensaver_block: Literal['on', 'off'] = 'on'
    suspend_on_video: Literal['on', 'off'] = 'on'
    reset_work_time_in_idle: Literal['on', 'off'] = 'off'


class Settings:
    """class for managing user settings.

    The settings file path is required (known issue 26): a pathless object
    used to break on save with AttributeError.
    """

    def __init__(self, file_name: str | Path):
        self.__user_settings = UserSettingsData()
        self.__system_settings = SystemSettingsData()
        self.__settings_file = Path(file_name)
        self.apply_settings_from_file()

    def to_dict(self) -> dict:
        """Convertation settings object to dict."""
        return self.__user_settings.to_dict()

    def __repr__(self) -> str:
        """Convertation settings object to view in terminal."""
        return str(self.to_dict())

    def __str__(self) -> str:
        """Convertation object to string."""
        return str(self.to_dict())

    def __read_settings_from_file(self) -> str | None:
        """Reading settings from file on disk."""
        settings_str = None
        try:
            settings_str = self.__settings_file.read_text('utf-8')
        except FileNotFoundError as error:
            logger.error(error)
            logger.error(type(error))
            return None
        except ValueError as error:
            logger.error(error)
            logger.error(type(error))
            return None
        # any other filesystem problem (PermissionError, IsADirectoryError,
        # OSError) must not crash the app: keep defaults (known issue 25)
        except OSError as error:
            logger.error(f'Failed to read settings file {self.__settings_file}: {error!r}')
            return None
        return settings_str

    def __validate_settings_str(self, settings_str: str) -> SettingsDataValidator | None:
        """Validation settings."""
        logger.debug(settings_str)
        if settings_str is not None:
            try:
                settings_validated = SettingsDataValidator.model_validate_json(settings_str)
                logger.debug(settings_validated)
                return settings_validated
            except ValidationError as error:
                logger.error(error)
                logger.error(type(error))
                return None
        return None

    def __apply_settings(self, validated_settings: SettingsDataValidator) -> None:
        """Apply given settings to the app."""
        if validated_settings is not None:
            # iterate validated fields explicitly: dir() would catch methods too (known issue 19)
            for field_name, field_value in validated_settings.model_dump().items():
                setattr(self.__user_settings, field_name, field_value)

    def apply_settings_from_file(self):
        """Read, validate and apply settings from file."""
        logger.trace('Settings: apply_settings_from_file')
        settings_from_file_str = self.__read_settings_from_file()
        settings_validated = self.__validate_settings_str(settings_from_file_str)
        logger.debug(f'Settings from file {settings_validated}')
        self.__apply_settings(settings_validated)

    def apply_settings_from_ui(self, new_settings_data: UserSettingsData) -> bool:
        """Validate settings and write them to file. Returns True on success."""
        logger.debug(f'New settings from ui to apply: {new_settings_data}')
        logger.debug(type(new_settings_data))
        try:
            settings_validated = SettingsDataValidator.model_validate(new_settings_data.to_dict())
        except ValidationError as error:
            logger.error(error)
            logger.error(type(error))
            return False
        self.__apply_settings(settings_validated)
        return self.save_settings_to_file()

    def save_settings_to_file(self) -> bool:
        """Save settings to file atomically.

        Writes a temporary file in the same directory and replaces the target
        with it: a failed write never damages the previous valid file
        (known issue 25). Returns True on success.
        """
        logger.trace('Settings: save_settings_to_file')
        settings_dict = self.to_dict()
        logger.debug(settings_dict)
        try:
            settings_validated = SettingsDataValidator.model_validate(settings_dict)
        except ValidationError as error:
            logger.error(error)
            logger.error(type(error))
            return False
        settings_json = settings_validated.model_dump_json(indent=4)
        logger.debug(f'Settings to file {settings_json}')
        temp_file = self.__settings_file.with_suffix(self.__settings_file.suffix + '.tmp')
        try:
            self.__settings_file.parent.mkdir(parents=True, exist_ok=True)
            temp_file.write_text(settings_json, encoding='utf-8')
            temp_file.replace(self.__settings_file)
        except OSError as error:
            logger.error(f'Failed to save settings file {self.__settings_file}: {error!r}')
            temp_file.unlink(missing_ok=True)
            return False
        return True

    def get_settings_copy(self) -> UserSettingsData:
        """Return copy of settings object."""
        return copy.copy(self.__user_settings)

    @property
    def user_settings(self) -> UserSettingsData:
        """User settings object (a copy: external changes cannot bypass validation)."""
        return copy.copy(self.__user_settings)

    @property
    def system_settings(self) -> SystemSettingsData:
        """System settings object."""
        return self.__system_settings
