
from support.resourses import ResSoundsPaths
from support.sound.sound_player import PSoundPlayer


class SoundNotificator:
    def __init__(self, sound_player: PSoundPlayer):
        self._sound_player = sound_player

    def play_notification_work(self):
        self._sound_player.play(file_path=ResSoundsPaths.notification_work)

    def play_notification_break(self):
        self._sound_player.play(file_path=ResSoundsPaths.notification_break)

    def play_notification_idle(self):
        self._sound_player.play(file_path=ResSoundsPaths.notification_idle)