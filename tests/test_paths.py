"""Tests for runtime paths resolution (known issue 36)."""

from pathlib import Path

from support.paths import app_dir, resource_dir


def test_dev_mode_app_dir_is_cwd(monkeypatch):
    monkeypatch.setattr('sys.frozen', False, raising=False)
    monkeypatch.delattr('sys.frozen', raising=False)

    assert app_dir() == Path.cwd()


def test_frozen_mode_app_dir_is_local_appdata(monkeypatch, tmp_path):
    exe_dir = tmp_path / 'Program Files' / 'EyesGuard'
    exe_dir.mkdir(parents=True)
    monkeypatch.setattr('sys.frozen', True, raising=False)
    monkeypatch.setattr('sys.executable', str(exe_dir / 'EyesGuard.exe'))
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'local'))

    result = app_dir()

    assert result == tmp_path / 'local' / 'EyesGuard'
    assert result.is_dir()


def test_frozen_mode_migrates_legacy_settings_once(monkeypatch, tmp_path):
    exe_dir = tmp_path / 'Program Files' / 'EyesGuard'
    legacy_settings = exe_dir / 'settings' / 'settings.json'
    legacy_settings.parent.mkdir(parents=True)
    legacy_settings.write_text('{"work_duration": 30}', encoding='utf-8')
    monkeypatch.setattr('sys.frozen', True, raising=False)
    monkeypatch.setattr('sys.executable', str(exe_dir / 'EyesGuard.exe'))
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'local'))

    app_dir()
    migrated = tmp_path / 'local' / 'EyesGuard' / 'settings' / 'settings.json'
    assert migrated.read_text(encoding='utf-8') == '{"work_duration": 30}'

    # an existing new-world file must not be overwritten by migration
    migrated.write_text('{"work_duration": 50}', encoding='utf-8')
    app_dir()
    assert migrated.read_text(encoding='utf-8') == '{"work_duration": 50}'


def test_frozen_mode_without_localappdata_falls_back_to_exe_dir(monkeypatch, tmp_path):
    exe_dir = tmp_path / 'EyesGuard'
    exe_dir.mkdir()
    monkeypatch.setattr('sys.frozen', True, raising=False)
    monkeypatch.setattr('sys.executable', str(exe_dir / 'EyesGuard.exe'))
    monkeypatch.delenv('LOCALAPPDATA', raising=False)

    assert app_dir() == exe_dir


def test_frozen_mode_uncreatable_target_falls_back_to_exe_dir(monkeypatch, tmp_path):
    exe_dir = tmp_path / 'EyesGuard'
    exe_dir.mkdir()
    # LOCALAPPDATA points to a file: mkdir under it is impossible
    blocker = tmp_path / 'blocker'
    blocker.write_text('not a dir', encoding='utf-8')
    monkeypatch.setattr('sys.frozen', True, raising=False)
    monkeypatch.setattr('sys.executable', str(exe_dir / 'EyesGuard.exe'))
    monkeypatch.setenv('LOCALAPPDATA', str(blocker))

    assert app_dir() == exe_dir


def test_resource_dir_frozen_uses_megipass(monkeypatch, tmp_path):
    exe_dir = tmp_path / 'EyesGuard'
    exe_dir.mkdir()
    monkeypatch.setattr('sys.frozen', True, raising=False)
    monkeypatch.setattr('sys.executable', str(exe_dir / 'EyesGuard.exe'))
    monkeypatch.setattr('sys._MEIPASS', str(tmp_path / 'bundle'), raising=False)

    assert resource_dir() == tmp_path / 'bundle'
