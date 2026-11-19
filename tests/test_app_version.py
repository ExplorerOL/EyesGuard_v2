import sys

sys.path.insert(0, './src')

from pathlib import Path

import tomllib

from config.app_version import APP_VERSION


def test_app_version_matches_pyproject():
    """APP_VERSION constant must stay in sync with the version in pyproject.toml."""
    pyproject_path = Path(__file__).parents[1] / 'pyproject.toml'
    expected_version = tomllib.loads(pyproject_path.read_text(encoding='utf-8'))['project']['version']
    assert APP_VERSION == expected_version
