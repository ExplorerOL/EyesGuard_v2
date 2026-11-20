import ctypes
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

from support.sound.sound_player import NoopSoundPlayer, create_sound_player


def test_noop_sound_player_play_does_not_raise():
    player = NoopSoundPlayer()
    player.play(file_path=Path('res/sounds/notification_work.mp3'), volume=50)


def test_noop_sound_player_stop_and_close_do_not_raise():
    player = NoopSoundPlayer()
    player.stop()
    player.close()


@pytest.mark.skipif(sys.platform == 'win32', reason='Windows uses the real winmm')
def test_factory_returns_noop_player_on_non_windows():
    assert isinstance(create_sound_player(), NoopSoundPlayer)


def test_factory_player_play_missing_file_does_not_raise():
    player = create_sound_player()
    player.play(file_path=Path('res/sounds/not_existing_sound.mp3'), volume=100)


class FakeWinmm:
    """Fake winmm recording MCI commands; 'play ... wait' blocks until 'stop'."""

    def __init__(self):
        self.commands: list[str] = []
        self.thread_ids: set[int] = set()
        self.lock = threading.Lock()
        self.playing = threading.Event()
        self._stop_events: dict[str, threading.Event] = {}

        def send_command(command, buffer, buffer_length, hwnd):
            parts = command.split()
            with self.lock:
                self.commands.append(command)
                # playback commands must all run on the single worker thread
                if parts[0] in ('open', 'setaudio', 'play', 'close'):
                    self.thread_ids.add(threading.get_ident())
            if parts[0] == 'open':
                alias = command.split('alias ')[-1]
                with self.lock:
                    self._stop_events[alias] = threading.Event()
            elif parts[0] == 'play' and command.endswith(' wait'):
                alias = parts[1]
                self.playing.set()
                with self.lock:
                    stop_event = self._stop_events.get(alias)
                if stop_event is not None:
                    stop_event.wait(timeout=5)
            elif parts[0] in ('stop', 'close'):
                alias = parts[1]
                with self.lock:
                    stop_event = self._stop_events.get(alias)
                if stop_event is not None:
                    stop_event.set()
            return 0

        def get_error(code, buffer, size):
            return 1

        self.mciSendStringW = send_command
        self.mciGetErrorStringW = get_error

    def command_count(self, prefix: str) -> int:
        with self.lock:
            return sum(1 for command in self.commands if command.startswith(prefix))


def make_mci_player(monkeypatch, tmp_path):
    fake_windll = SimpleNamespace(winmm=FakeWinmm())
    monkeypatch.setattr(ctypes, 'windll', fake_windll, raising=False)
    from support.sound.windows.sound_player import MciSoundPlayer

    winmm = fake_windll.winmm
    player = MciSoundPlayer()
    sound_file = tmp_path / 'sound.mp3'
    sound_file.write_text('fake', encoding='utf-8')
    return player, winmm, sound_file


def test_mci_player_uses_single_worker_thread(monkeypatch, tmp_path):
    player, winmm, sound_file = make_mci_player(monkeypatch, tmp_path)

    for _ in range(3):
        player.play(file_path=sound_file, volume=50)
        assert winmm.playing.wait(timeout=5)
        player.stop()
    player.close()

    # all MCI calls come from the single managed worker thread
    assert winmm.thread_ids
    assert len(winmm.thread_ids) == 1


def test_mci_player_play_interrupts_current_sound(monkeypatch, tmp_path):
    player, winmm, sound_file = make_mci_player(monkeypatch, tmp_path)

    player.play(file_path=sound_file, volume=50)
    assert winmm.playing.wait(timeout=5)
    winmm.playing.clear()
    player.play(file_path=sound_file, volume=70)

    # the second play interrupts the first: a stop command is issued
    deadline_stop = threading.Event()

    def wait_for_stop():
        for _ in range(200):
            if winmm.command_count('stop ') > 0:
                deadline_stop.set()
                return
            threading.Event().wait(0.05)

    checker = threading.Thread(target=wait_for_stop)
    checker.start()
    checker.join(timeout=10)
    player.close()
    assert deadline_stop.is_set()


def test_mci_player_close_joins_worker(monkeypatch, tmp_path):
    player, winmm, sound_file = make_mci_player(monkeypatch, tmp_path)

    player.play(file_path=sound_file, volume=50)
    assert winmm.playing.wait(timeout=5)

    player.close()

    assert not player._MciSoundPlayer__worker.is_alive()
    assert winmm.command_count('stop ') >= 1
