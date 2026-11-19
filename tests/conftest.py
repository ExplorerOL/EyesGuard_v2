"""Shared test bootstrap: src import path and fixture path helper.

Importing src modules in tests works regardless of the current working
directory: the path is derived from this conftest file location.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

FIXTURES_DIR = Path(__file__).resolve().parent / 'data'


def fixture_path(file_name: str) -> Path:
    """Absolute path to a fixture file from tests/data."""
    return FIXTURES_DIR / file_name
