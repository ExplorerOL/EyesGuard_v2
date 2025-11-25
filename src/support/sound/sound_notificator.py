
from config.settings import OnOffValue, Settings
from support.resourses import ResSoundsPaths
from support.sound.sound_player import PSoundPlayer


class SoundNotificator:
    def __init__(self, sound_player: PSoundPlayer, settings: Settings):
        self._sound_player = sound_player
        self._settings = settings

    def play_notification_work(self):
        if self._settings.user_settings.sounds == OnOffValue.on.value:
            self._sound_player.play(file_path=ResSoundsPaths.notification_work)

    def play_notification_break(self):
        if self._settings.user_settings.sounds == OnOffValue.on.value:
            self._sound_player.play(file_path=ResSoundsPaths.notification_break)

    def play_notification_idle(self):
        if self._settings.user_settings.sounds == OnOffValue.on.value:
            self._sound_player.play(file_path=ResSoundsPaths.notification_idle)