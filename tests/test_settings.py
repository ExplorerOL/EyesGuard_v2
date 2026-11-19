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


def test_read_settings_from_missing_file_returns_defaults():
    """A missing settings file must fall back to defaults (FileNotFoundError branch)."""
    settings = Settings(fixture_path('settings_not_existing.json'))
    assert str(settings) == settings_default_str


def test_read_settings_from_malformed_json_returns_defaults(tmp_path):
    """JSON syntax error must go through ValidationError and keep all defaults.

    The malformed content is generated at runtime: a broken JSON file must not
    live in the repo (pre-commit check-json would reject it).
    """
    malformed_file = tmp_path / 'settings_malformed.json'
    malformed_file.write_text('{"work_duration": asd", "sounds": "on"}', encoding='utf-8')
    settings = Settings(malformed_file)
    assert str(settings) == settings_default_str


@pytest.mark.parametrize(
    'settings_file_name',
    [
        # work_duration is a non-numeric string: int coercion fails
        ('settings_invalid_not_int.json'),
        # sounds is an int instead of the on/off literal
        ('settings_invalid_not_string.json'),
    ],
)
def test_read_settings_from_invalid_file_returns_defaults(settings_file_name):
    """Invalid file content must be fully rejected: all fields keep defaults.

    Policy: all-or-nothing — a file that fails validation does not partially
    apply its valid fields.
    """
    settings = Settings(fixture_path(settings_file_name))
    assert str(settings) == settings_default_str


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


expected_file_content_default = (
    '{\n    "work_duration": 45,\n    "break_duration": 15,\n    "activity_timeout": 180,\n'
    '    "volume": 100,\n    "sounds": "on",\n    "notifications": "on",\n    "protection_status": "on",\n'
    '    "screensaver_block": "on",\n    "suspend_on_video": "on",\n    "reset_work_time_in_idle": "off"\n}'
)


def test_apply_settings_from_ui_saves_to_file(tmp_path):
    """Apply from UI must persist settings itself, without an extra save call."""
    settings_file = tmp_path / 'settings.json'
    settings = Settings(settings_file)

    settings.apply_settings_from_ui(new_settings_data=UserSettingsData())

    written_file_content = settings_file.read_text(encoding='utf-8')
    assert written_file_content == expected_file_content_default


def test_save_settings_to_file_writes_valid_json(tmp_path):
    """Direct save of valid current settings must write the canonical JSON."""
    settings_file = tmp_path / 'settings.json'
    settings = Settings(settings_file)

    settings.save_settings_to_file()

    written_file_content = settings_file.read_text(encoding='utf-8')
    assert written_file_content == expected_file_content_default


def test_apply_invalid_settings_from_ui_keeps_previous_file(tmp_path):
    """Rejected UI settings must not overwrite the previously saved valid file."""
    settings_file = tmp_path / 'settings.json'
    settings = Settings(settings_file)
    valid_settings = UserSettingsData()
    valid_settings.work_duration = 30
    valid_settings.break_duration = 10
    settings.apply_settings_from_ui(new_settings_data=valid_settings)
    content_before = settings_file.read_text(encoding='utf-8')

    invalid_settings = UserSettingsData()
    invalid_settings.work_duration = 111
    invalid_settings.break_duration = 91
    settings.apply_settings_from_ui(new_settings_data=invalid_settings)

    assert settings_file.read_text(encoding='utf-8') == content_before


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
