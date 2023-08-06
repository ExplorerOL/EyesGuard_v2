import pytest
from pathlib import Path
from src.settings import Settings
from pydantic import ValidationError

settings_default_str = "{'break_duration': 15, 'notifications': 'on', 'sounds': 'on', 'work_duration': 45}"

@pytest.mark.parametrize("settings_file_name, expected_settings_str", [
    ('tests/data/settings_valid_min_values.json', "{'break_duration': 1, 'notifications': 'off', 'sounds': 'off', 'work_duration': 1}"),
    ('tests/data/settings_valid_mean_values.json', "{'break_duration': 50, 'notifications': 'on', 'sounds': 'off', 'work_duration': 50}"),
    ('tests/data/settings_valid_max_values.json', "{'break_duration': 100, 'notifications': 'on', 'sounds': 'on', 'work_duration': 100}"),
    ('tests/data/settings_valid_empty.json', "{'break_duration': 15, 'notifications': 'on', 'sounds': 'on', 'work_duration': 45}"),
    ('tests/data/settings_valid_no_param.json', "{'break_duration': 15, 'notifications': 'off', 'sounds': 'off', 'work_duration': 1}"),
    ]
)

def test_read_settings_from_valid_file(settings_file_name, expected_settings_str):
    settings = Settings(settings_file_name)
    settings_str = str(settings)
    print(settings_str)
    assert settings_str == expected_settings_str

@pytest.mark.parametrize("settings_file_name", [
    ('./adc.json'),
    ('settings_invalid_not_invalid_json.json'),
    ('settings_invalid_not_int.json'),
    ('settings_invalid_not_string.json'),
    ]
)
def test_read_settings_from_invalid_file(settings_file_name):
    settings = Settings(settings_file_name)
    settings_str = str(settings)
    print(settings_str)
    assert settings_str == settings_default_str

def test_write_valid_settings_to_file():
    file_to_write = 'tests/data/settings_written_file.json'
    Path(file_to_write).unlink(missing_ok=True)
    settings = Settings(file_to_write)
    settings._settings.work_duration = 90
    settings._settings.break_duration = 91
    settings._settings.sounds = 'off'
    settings._settings.notifications = 'off'

    settings.save_settings_to_file()

    written_file_content = Path(file_to_write).read_text()
    print(f'Written file content = {written_file_content}')

    expected_file_content = '{\n    "work_duration": 90,\n    "break_duration": 91,\n    "sounds": "off",\n    "notifications": "off"\n}'
    assert written_file_content == expected_file_content, 'Written content and expected content are not same!'

def test_write_invalid_settings_to_file():
    file_to_write = 'tests/data/settings_written_file.json'
    Path(file_to_write).unlink(missing_ok=True)
    settings = Settings(file_to_write)
    try:
        settings._settings.work_duration = 111
        settings._settings.break_duration = 91
        settings._settings.sounds = 'off'
        settings._settings.notifications = 'off'
    except ValidationError as error:
        print(error)

    settings.save_settings_to_file()

    assert not Path(file_to_write).is_file(), 'Settings file was erroneously saved!'