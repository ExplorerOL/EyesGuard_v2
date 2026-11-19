from pathlib import Path

import pytest
from conftest import fixture_path

from config.settings import Settings, UserSettingsData

settings_default_str = (
    "{'activity_timeout': 180, 'break_duration': 15, 'notifications': 'on', 'protection_status': 'on', "
    "'reset_work_time_in_idle': 'off', 'screensaver_block': 'on', 'sounds': 'on', 'suspend_on_video': 'on', "
    "'volume': 100, 'work_duration': 45}"
)


@pytest.mark.parametrize(
    'settings_file_name, expected_settings_str',
    [
        (
            fixture_path('settings_valid_min_values.json'),
            '{'
            "'activity_timeout': 30, 'break_duration': 1, 'notifications': 'off', 'protection_status': 'on', "
            "'reset_work_time_in_idle': 'off', 'screensaver_block': 'on', 'sounds': 'off', "
            "'suspend_on_video': 'on', 'volume': 1, 'work_duration': 1"
            '}',
        ),
        (
            fixture_path('settings_valid_mean_values.json'),
            '{'
            "'activity_timeout': 315, 'break_duration': 50, 'notifications': 'on', 'protection_status': 'on', "
            "'reset_work_time_in_idle': 'off', 'screensaver_block': 'on', 'sounds': 'off', "
            "'suspend_on_video': 'on', 'volume': 50, 'work_duration': 50"
            '}',
        ),
        (
            fixture_path('settings_valid_max_values.json'),
            '{'
            "'activity_timeout': 600, 'break_duration': 100, 'notifications': 'on', 'protection_status': 'on', "
            "'reset_work_time_in_idle': 'off', 'screensaver_block': 'on', 'sounds': 'on', "
            "'suspend_on_video': 'on', 'volume': 100, 'work_duration': 100"
            '}',
        ),
        (
            fixture_path('settings_valid_empty.json'),
            '{'
            "'activity_timeout': 180, 'break_duration': 15, 'notifications': 'on', 'protection_status': 'on', "
            "'reset_work_time_in_idle': 'off', 'screensaver_block': 'on', 'sounds': 'on', "
            "'suspend_on_video': 'on', 'volume': 100, 'work_duration': 45"
            '}',
        ),
        (
            fixture_path('settings_valid_no_param.json'),
            '{'
            "'activity_timeout': 180, 'break_duration': 15, 'notifications': 'off', 'protection_status': 'on', "
            "'reset_work_time_in_idle': 'off', 'screensaver_block': 'on', 'sounds': 'off', "
            "'suspend_on_video': 'on', 'volume': 100, 'work_duration': 1"
            '}',
        ),
    ],
)
def test_read_settings_from_valid_file(settings_file_name, expected_settings_str):
    settings = Settings(settings_file_name)
    settings_str = str(settings)
    assert settings_str == expected_settings_str


@pytest.mark.parametrize(
    'settings_file_name',
    [
        ('./adc.json'),
        ('settings_invalid_not_invalid_json.json'),
        ('settings_invalid_not_int.json'),
        ('settings_invalid_not_string.json'),
    ],
)
def test_read_settings_from_invalid_file(settings_file_name):
    settings = Settings(settings_file_name)
    settings_str = str(settings)
    assert settings_str == settings_default_str


@pytest.mark.parametrize(
    'settings_file_name, expected_activity_timeout',
    [
        (fixture_path('settings_valid_activity_timeout_min.json'), 30),
        (fixture_path('settings_valid_activity_timeout_max.json'), 600),
    ],
)
def test_read_activity_timeout_boundaries(settings_file_name, expected_activity_timeout):
    settings = Settings(settings_file_name)
    assert settings.user_settings.activity_timeout == expected_activity_timeout


@pytest.mark.parametrize(
    'settings_file_name',
    [
        (fixture_path('settings_invalid_activity_timeout_low.json')),
        (fixture_path('settings_invalid_activity_timeout_high.json')),
    ],
)
def test_read_settings_with_invalid_activity_timeout(settings_file_name):
    settings = Settings(settings_file_name)
    assert settings.user_settings.activity_timeout == 180


@pytest.mark.parametrize(
    'settings_file_name, expected_volume',
    [
        (fixture_path('settings_valid_volume_min.json'), 1),
        (fixture_path('settings_valid_volume_max.json'), 100),
    ],
)
def test_read_volume_boundaries(settings_file_name, expected_volume):
    settings = Settings(settings_file_name)
    assert settings.user_settings.volume == expected_volume


@pytest.mark.parametrize(
    'settings_file_name',
    [
        (fixture_path('settings_invalid_volume_low.json')),
        (fixture_path('settings_invalid_volume_high.json')),
    ],
)
def test_read_settings_with_invalid_volume(settings_file_name):
    settings = Settings(settings_file_name)
    assert settings.user_settings.volume == 100


def test_write_default_user_settings_to_file():
    file_to_write = fixture_path('settings_written_file.json')
    Path(file_to_write).unlink(missing_ok=True)

    user_settings = UserSettingsData()
    settings = Settings(file_to_write)
    settings.apply_settings_from_ui(new_settings_data=user_settings)

    settings.save_settings_to_file()

    written_file_content = Path(file_to_write).read_text(encoding='utf-8')

    expected_file_content = (
        '{\n    "work_duration": 45,\n    "break_duration": 15,\n    "activity_timeout": 180,\n'
        '    "volume": 100,\n    "sounds": "on",\n    "notifications": "on",\n    "protection_status": "on",\n'
        '    "screensaver_block": "on",\n    "suspend_on_video": "on",\n    "reset_work_time_in_idle": "off"\n}'
    )
    assert written_file_content == expected_file_content, 'Written content and expected content are not same!'


def test_write_invalid_settings_to_file():
    file_to_write = fixture_path('settings_written_file.json')
    Path(file_to_write).unlink(missing_ok=True)

    user_settings = UserSettingsData()
    user_settings.work_duration = 111
    user_settings.break_duration = 91
    user_settings.sounds = 'off'
    user_settings.notifications = 'off'
    settings = Settings(file_to_write)
    settings.apply_settings_from_ui(new_settings_data=user_settings)

    settings.save_settings_to_file()

    written_file_content = Path(file_to_write).read_text(encoding='utf-8')
    expected_file_content = (
        '{\n    "work_duration": 45,\n    "break_duration": 15,\n    "activity_timeout": 180,\n'
        '    "volume": 100,\n    "sounds": "on",\n    "notifications": "on",\n    "protection_status": "on",\n'
        '    "screensaver_block": "on",\n    "suspend_on_video": "on",\n    "reset_work_time_in_idle": "off"\n}'
    )
    assert written_file_content == expected_file_content, 'Written content and expected content are not same!'


def test_read_display_settings_from_valid_file():
    settings = Settings(fixture_path('settings_valid_display_fields.json'))
    assert settings.user_settings.screensaver_block == 'off'
    assert settings.user_settings.suspend_on_video == 'off'
    assert settings.user_settings.reset_work_time_in_idle == 'on'


def test_read_settings_with_invalid_new_field_value():
    settings = Settings(fixture_path('settings_invalid_new_field_value.json'))
    assert settings.user_settings.screensaver_block == 'on'
    assert settings.user_settings.suspend_on_video == 'on'
    assert settings.user_settings.reset_work_time_in_idle == 'off'
