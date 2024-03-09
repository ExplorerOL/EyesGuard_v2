from pathlib import Path

import pytest
from pydantic import ValidationError

from src.settings import Settings, UserSettingsData

settings_default_str = "{'break_duration': 15, 'notifications': 'on', 'protection_status': 'on', 'sounds': 'on', 'work_duration': 45}"


@pytest.mark.parametrize(
    "settings_file_name, expected_settings_str",
    [
        (
            "tests/data/settings_valid_min_values.json",
            "{'break_duration': 1, 'notifications': 'off', 'protection_status': 'on', 'sounds': 'off', 'work_duration': 1}",
        ),
        (
            "tests/data/settings_valid_mean_values.json",
            "{'break_duration': 50, 'notifications': 'on', 'protection_status': 'on', 'sounds': 'off', 'work_duration': 50}",
        ),
        (
            "tests/data/settings_valid_max_values.json",
            "{'break_duration': 100, 'notifications': 'on', 'protection_status': 'on', 'sounds': 'on', 'work_duration': 100}",
        ),
        (
            "tests/data/settings_valid_empty.json",
            "{'break_duration': 15, 'notifications': 'on', 'protection_status': 'on', 'sounds': 'on', 'work_duration': 45}",
        ),
        (
            "tests/data/settings_valid_no_param.json",
            "{'break_duration': 15, 'notifications': 'off', 'protection_status': 'on', 'sounds': 'off', 'work_duration': 1}",
        ),
    ],
)
def test_read_settings_from_valid_file(settings_file_name, expected_settings_str):
    settings = Settings(settings_file_name)
    settings_str = str(settings)
    print(settings_str)
    assert settings_str == expected_settings_str


@pytest.mark.parametrize(
    "settings_file_name",
    [
        ("./adc.json"),
        ("settings_invalid_not_invalid_json.json"),
        ("settings_invalid_not_int.json"),
        ("settings_invalid_not_string.json"),
    ],
)
def test_read_settings_from_invalid_file(settings_file_name):
    settings = Settings(settings_file_name)
    settings_str = str(settings)
    print(settings_str)
    assert settings_str == settings_default_str


def test_write_default_user_settings_to_file():
    file_to_write = "tests/data/settings_written_file.json"
    Path(file_to_write).unlink(missing_ok=True)

    user_settings = UserSettingsData()
    settings = Settings(file_to_write)
    settings.apply_settings_from_ui(new_settings_data=user_settings)

    settings.save_settings_to_file()

    written_file_content = Path(file_to_write).read_text()
    print(f"Written file content = {written_file_content}")

    expected_file_content = '{\n    "work_duration": 45,\n    "break_duration": 15,\n    "sounds": "on",\n    "notifications": "on",\n    "protection_status": "on"\n}'
    assert written_file_content == expected_file_content, "Written content and expected content are not same!"


def test_write_invalid_settings_to_file():
    file_to_write = "tests/data/settings_written_file.json"
    Path(file_to_write).unlink(missing_ok=True)

    user_settings = UserSettingsData()
    user_settings.work_duration = 111
    user_settings.break_duration = 91
    user_settings.sounds = "off"
    user_settings.notifications = "off"
    settings = Settings(file_to_write)
    settings.apply_settings_from_ui(new_settings_data=user_settings)

    settings.save_settings_to_file()

    written_file_content = Path(file_to_write).read_text()
    print(f"Written file content = {written_file_content}")
    expected_file_content = '{\n    "work_duration": 45,\n    "break_duration": 15,\n    "sounds": "on",\n    "notifications": "on",\n    "protection_status": "on"\n}'
    assert written_file_content == expected_file_content, "Written content and expected content are not same!"
