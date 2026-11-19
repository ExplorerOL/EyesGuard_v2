# Status: sounds-volume-setting

## Состояние: реализовано, ожидает ручной проверки на Windows

Дата: 2026-11-19. Ветка: feature/v2.1.0.

## Что сделано

| Слой | Файл | Правка |
|---|---|---|
| Модель | `src/config/settings.py` | `UserSettingsData.volume: int = 100`; `SettingsDataValidator.volume: Field(default=100, ge=10, le=100)` |
| Ресурсы | `src/support/resourses.py` | `ResImages.img_sounds` → `res/img/speaker.png` |
| Плеер (win) | `src/support/sound/windows/sound_player.py` | Новый: `MciSoundPlayer` (MCI open/setaudio/play wait/close, alias = uuid, setaudio-fallback) |
| Фабрика | `src/support/sound/sound_player.py` | `PSoundPlayer.play(file_path, volume)`, `NoopSoundPlayer`, `create_sound_player()` по `sys.platform`; playsound удалён |
| Уведомления | `src/support/sound/sound_notificator.py` | `play(..., volume=user_settings.volume)` во всех трёх методах |
| UI | `src/windows/wnd_settings.py` | Вкладка Sounds: кнопка навигации (row=4, About → row=5), чекбокс «Sounds enabled» (перенесён из General), CTkSlider 10–100 + label «Volume: N %»; `update()`, `select_frame_by_name`, `event_volume_slider_move` |
| Чтение UI | `src/view.py` | `ui_settings_data.volume = int(slider_volume.get())` |
| Зависимости | `pyproject.toml`, `uv.lock`, `wheels/` | playsound и `[tool.uv.sources]` удалены, wheel удалён, `uv lock` — «Removed playsound v1.3.0» |
| Сборка | `EyesGuard-onefile.spec`, `EyesGuard-onedir.spec` | `hiddenimports += 'support.sound.windows.sound_player'` |
| Доки | `README.md`, `CHANGELOG.md`, `.agents/memory/app/settings.md`, граф знаний | Вкладка/volume/MCI-плеер; CHANGELOG — секция `[2.2.0] - 2026-11-19` |
| Тесты | `tests/test_settings.py`, `tests/test_sound_player.py`, `tests/data/*` | Expected-строки обновлены (volume), фикстуры min/mean/max дополнены, +4 volume-фикстуры, +4 теста настроек, +3 теста фабрики плеера |

## Фактические проверки (Linux, агент)

| Команда | Результат |
|---|---|
| `uv run ruff check --fix --config=./linter_ruff.toml <files>` | All checks passed |
| `uv run ruff format --config=./linter_ruff.toml <files>` | 9 files left unchanged |
| `uv run pytest -v` | **23 passed** (было 16) |
| `uv lock` | OK, «Removed playsound v1.3.0» |
| `grep -rn playsound pyproject.toml uv.lock src/` | пусто (не найдено) |
| `uv run python .agents/tasks/sounds-volume-setting/scripts/verify.py` | OK: all 4 checks passed |

## Ревью

Независимый read-only ревьюер: **APPROVED** (Critical/Important — нет). Оба Minor исправлены:

1. `MciSoundPlayer.__play_sound_safely`: `close` теперь только при успешном `open` (флаг
   `opened`) — убран лишний warning при ошибке open.
2. Устаревшие упоминания playsound обновлены в `AGENTS.md` (2 строки) и
   `.agents/memory/prj/known-issues.md` (2 ловушки: Windows-only код, судьба playsound).

Повторные проверки после исправлений: ruff — чисто, pytest — 23 passed, verify.py — all 4 checks passed.

## Отложенные замечания

- `res/img/speaker.png` **не добавлен** (по решению пользователя — добавит сам). Без него
  приложение падает при старте на Windows (PIL `Image.open` в `resourses.py`). Тесты на Linux
  не затронуты. **Условие запуска: файл должен существовать.**
- LSP-диагностика `ctypes.windll` в `src/support/sound/windows/sound_player.py` — ожидаемая:
  модуль Windows-only, на Linux не импортируется (фабрика).

## Ручные проверки (Windows, не проведены)

1. Вкладка Sounds: иконка speaker.png, переключение кадров, чекбокс sounds работает.
2. Слайдер 10–100 %: звук различается на слух (10/50/100), setaudio не даёт ошибок в логе.
3. Mute чекбоксом «Sounds enabled».
4. Round-trip: Apply сохраняет volume в settings.json, при перезапуске значение читается.
5. Обе сборки (onefile, onedir) собираются, звук воспроизводится с громкостью.
