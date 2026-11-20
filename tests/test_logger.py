"""Tests for the logger setup (known issue 4)."""

import importlib

from support import logger as logger_module


def reload_logger_module():
    """Re-run the logger module setup (adds a fresh sink)."""
    return importlib.reload(logger_module)


def test_logger_does_not_delete_existing_log_file(tmp_path, monkeypatch):
    """Regression for known issue 4: importing the logger must not unlink the old log."""
    monkeypatch.chdir(tmp_path)
    logs_dir = tmp_path / 'logs'
    logs_dir.mkdir()
    log_file = logs_dir / 'log.log'
    log_file.write_text('previous run record', encoding='utf-8')

    reloaded = reload_logger_module()
    reloaded.logger.debug('new run record')

    content = log_file.read_text(encoding='utf-8')
    assert 'previous run record' in content
    assert 'new run record' in content
    reloaded.logger.remove()


def test_logger_file_sink_accepts_debug_messages(tmp_path, monkeypatch):
    """The file sink level must match the actually used trace/debug/info levels."""
    monkeypatch.chdir(tmp_path)

    reloaded = reload_logger_module()
    reloaded.logger.debug('debug record for sink level test')

    content = (tmp_path / 'logs' / 'log.log').read_text(encoding='utf-8')
    assert 'debug record for sink level test' in content
    reloaded.logger.remove()


def test_logger_survives_unwritable_log_directory(tmp_path, monkeypatch):
    """A broken file sink must not crash the import: stderr fallback is used."""
    monkeypatch.chdir(tmp_path)
    blocker = tmp_path / 'logs'
    blocker.write_text('not a directory', encoding='utf-8')

    reloaded = reload_logger_module()

    reloaded.logger.info('still works')
    reloaded.logger.remove()
