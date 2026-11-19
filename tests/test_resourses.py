"""Tests for resource loading (known issue 16)."""

from PIL import Image

import support.resourses as resourses_module
from support.resourses import load_image


def test_load_image_existing_file_returns_loaded_copy():
    image = load_image('res/img/gear.png')

    assert isinstance(image, Image.Image)
    # fully loaded independent copy: no open file handle is kept
    assert getattr(image, 'fp', None) is None


def test_load_image_missing_file_returns_placeholder(monkeypatch, tmp_path):
    monkeypatch.setattr(resourses_module, 'resource_dir', lambda: tmp_path)

    image = load_image('res/img/does_not_exist.png')

    assert isinstance(image, Image.Image)
    assert image.size == (48, 48)


def test_load_image_invalid_file_returns_placeholder(monkeypatch, tmp_path):
    monkeypatch.setattr(resourses_module, 'resource_dir', lambda: tmp_path)
    broken_file = tmp_path / 'broken.png'
    broken_file.write_bytes(b'not a png at all')

    image = load_image('broken.png')

    assert isinstance(image, Image.Image)
    assert image.size == (48, 48)


def test_placeholder_has_known_color(monkeypatch, tmp_path):
    monkeypatch.setattr(resourses_module, 'resource_dir', lambda: tmp_path)

    placeholder = load_image('missing.png')

    assert placeholder.getpixel((5, 5)) == (70, 130, 180)
