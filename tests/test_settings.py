from pathlib import Path

import pytest
from conftest import fixture_path

from config.settings import Settings, UserSettingsData

settings_default = {
    'work_duration': 45,
    'break_duration': 15,
    'activity_timeout': 180,
    'volume': 100,
    'sounds': 'on',
    'notifications': 'on',
    'protection_status': 'on',
    'screensaver_block': 'on',
    'suspend_on_video': 'on',
    'reset_work_time_in_idle': 'off',
}


@pytest.mark.parametrize(
    'settings_file_name, expected_settings',
    [
        (
            'settings_valid_min_values.json',
            {
                'work_duration': 1,
                'break_duration': 1,
                'activity_timeout': 30,
                'volume': 1,
                'sounds': 'off',
                'notifications': 'off',
                'protection_status': 'on',
                'screensaver_block': 'on',
                'suspend_on_video': 'on',
                'reset_work_time_in_idle': 'off',
            },
        ),
        (
            'settings_valid_mean_values.json',
            {
                'work_duration': 50,
                'break_duration': 50,
                'activity_timeout': 315,
                'volume': 50,
                'sounds': 'off',
                'notifications': 'on',
                'protection_status': 'on',
                'screensaver_block': 'on',
                'suspend_on_video': 'on',
                'reset_work_time_in_idle': 'off',
            },
        ),
        (
            'settings_valid_max_values.json',
            {
                'work_duration': 100,
                'break_duration': 100,
                'activity_timeout': 600,
                'volume': 100,
                'sounds': 'on',
                'notifications': 'on',
                'protection_status': 'on',
                'screensaver_block': 'on',
                'suspend_on_video': 'on',
                'reset_work_time_in_idle': 'off',
            },
        ),
        (
            'settings_valid_empty.json',
            {
                'work_duration': 45,
                'break_duration': 15,
                'activity_timeout': 180,
                'volume': 100,
                'sounds': 'on',
                'notifications': 'on',
                'protection_status': 'on',
                'screensaver_block': 'on',
                'suspend_on_video': 'on',
                'reset_work_time_in_idle': 'off',
            },
        ),
        (
            'settings_valid_no_param.json',
            {
                'work_duration': 1,
                'break_duration': 15,
                'activity_timeout': 180,
                'volume': 100,
                'sounds': 'off',
                'notifications': 'off',
                'protection_status': 'on',
                'screensaver_block': 'on',
                'suspend_on_video': 'on',
                'reset_work_time_in_idle': 'off',
            },
        ),
    ],
)
def test_read_settings_from_valid_file(settings_file_name, expected_settings):
    settings = Settings(fixture_path(settings_file_name))
    assert settings.to_dict() == expected_settings


def test_read_settings_from_missing_file_returns_defaults():
    """A missing settings file must fall back to defaults (FileNotFoundError branch)."""
    settings = Settings(fixture_path('settings_not_existing.json'))
    assert settings.to_dict() == settings_default


def test_read_settings_from_malformed_json_returns_defaults(tmp_path):
    """JSON syntax error must go through ValidationError and keep all defaults.

    The malformed content is generated at runtime: a broken JSON file must not
    live in the repo (pre-commit check-json would reject it).
    """
    malformed_file = tmp_path / 'settings_malformed.json'
    malformed_file.write_text('{"work_duration": asd", "sounds": "on"}', encoding='utf-8')
    settings = Settings(malformed_file)
    assert settings.to_dict() == settings_default


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
    assert settings.to_dict() == settings_default


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


def test_user_settings_constructor_accepts_all_fields():
    settings = UserSettingsData(
        work_duration=30,
        break_duration=10,
        activity_timeout=60,
        volume=42,
        sounds='off',
        notifications='off',
        protection_status='off',
        screensaver_block='off',
        suspend_on_video='off',
        reset_work_time_in_idle='on',
    )
    assert settings.work_duration == 30
    assert settings.volume == 42
    assert settings.sounds == 'off'
    assert settings.protection_status == 'off'
    assert settings.reset_work_time_in_idle == 'on'


def test_user_settings_equality_covers_all_fields():
    """Regression for known issue 27: non-annotated fields used to be ignored by ==."""
    base = UserSettingsData()
    same = UserSettingsData()
    changed_sounds = UserSettingsData()
    changed_sounds.sounds = 'off'

    assert base == same
    assert base != changed_sounds


def test_user_settings_to_dict_roundtrip():
    settings = UserSettingsData()
    settings.work_duration = 33
    settings.suspend_on_video = 'off'

    as_dict = settings.to_dict()

    assert as_dict['work_duration'] == 33
    assert as_dict['suspend_on_video'] == 'off'
    assert len(as_dict) == 10
    restored = UserSettingsData(**as_dict)
    assert restored == settings


def test_settings_repr_is_string(tmp_path):
    """Regression for known issue 19: __repr__ must return a string."""
    settings = Settings(tmp_path / 'settings.json')

    representation = repr(settings)

    assert isinstance(representation, str)
    assert "'work_duration': 45" in representation


def test_read_settings_from_directory_returns_defaults(tmp_path):
    """Regression for known issue 25: a directory instead of the file must not crash."""
    settings_dir = tmp_path / 'settings.json'
    settings_dir.mkdir()

    settings = Settings(settings_dir)

    assert settings.to_dict() == settings_default


def test_read_settings_unreadable_file_returns_defaults(tmp_path, monkeypatch):
    settings_file = tmp_path / 'settings.json'
    settings_file.write_text('{}', encoding='utf-8')

    def deny_read(self, *args, **kwargs):
        raise PermissionError('read denied')

    monkeypatch.setattr(Path, 'read_text', deny_read)
    settings = Settings(settings_file)

    assert settings.to_dict() == settings_default


def test_save_settings_failure_preserves_old_file_and_returns_false(tmp_path, monkeypatch):
    """Regression for known issue 25: failed save must not damage the previous file."""
    settings_file = tmp_path / 'settings.json'
    settings = Settings(settings_file)
    settings.apply_settings_from_ui(new_settings_data=UserSettingsData())
    old_content = settings_file.read_text(encoding='utf-8')

    def fail_replace(self, target):
        raise OSError('replace denied')

    monkeypatch.setattr(Path, 'replace', fail_replace)
    assert settings.save_settings_to_file() is False

    assert settings_file.read_text(encoding='utf-8') == old_content
    # no temporary artifacts left behind
    assert list(tmp_path.iterdir()) == [settings_file]


def test_save_settings_creates_missing_parent_directories(tmp_path):
    settings_file = tmp_path / 'nested' / 'dir' / 'settings.json'
    settings = Settings(settings_file)

    assert settings.save_settings_to_file() is True
    assert settings_file.exists()


def test_save_settings_returns_true_on_success(tmp_path):
    settings = Settings(tmp_path / 'settings.json')

    assert settings.save_settings_to_file() is True


def test_settings_requires_file_path():
    """Regression for known issue 26: no pathless Settings objects with broken save."""
    with pytest.raises(TypeError):
        Settings()
