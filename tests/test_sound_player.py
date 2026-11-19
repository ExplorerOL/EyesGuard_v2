import sys
from pathlib import Path

import pytest

from support.sound.sound_player import NoopSoundPlayer, create_sound_player


def test_noop_sound_player_play_does_not_raise():
    player = NoopSoundPlayer()
    player.play(file_path=Path('res/sounds/notification_work.mp3'), volume=50)


@pytest.mark.skipif(sys.platform == 'win32', reason='Windows uses MciSoundPlayer')
def test_factory_returns_noop_player_on_non_windows():
    assert isinstance(create_sound_player(), NoopSoundPlayer)


def test_factory_player_play_missing_file_does_not_raise():
    player = create_sound_player()
    player.play(file_path=Path('res/sounds/not_existing_sound.mp3'), volume=100)
