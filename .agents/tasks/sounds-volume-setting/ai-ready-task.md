# AI-ready task

## Problem

Добавить регулировку громкости звуков: в окне настроек — новая вкладка Sounds
(чекбокс включения звуков переезжает туда из General + слайдер громкости 10–100 %),
настройка `volume` сохраняется и читается. Воспроизведение звука переводится с
playsound на собственный MCI-плеер (ctypes winmm), размещённый в платформенной
директории `src/support/sound/windows/`. Зависимость playsound удаляется вместе
с vendored wheel.

## Expected outcome

- Вкладка Sounds в окне настроек: чекбокс «Sounds enabled» и слайдер 10–100 %
  с отображением текущего значения; Apply сохраняет `volume` в settings.json,
  при запуске значение читается.
- Звук воспроизводится `MciSoundPlayer` с применением громкости
  (`setaudio volume` 100…1000); ошибки MCI — в лог, приложение не падает.
- playsound отсутствует в pyproject.toml, uv.lock и wheels/; линт и тесты
  зелёные; обе сборки (onefile, onedir) собираются и работают.

## Known facts

- Диапазон громкости **10–100 %**, дефолт **100**; 0 не предусмотрен — полное
  отключение звука только чекбоксом `sounds` (on/off).
- Виджет громкости — **слайдер** (CTkSlider).
- Иконка вкладки Sounds: пользователь сам добавит `res/img/speaker.png`;
  `ResImages.img_sounds` будет ссылаться на этот файл — без него приложение
  падает при старте (Image.open). Условие запуска: файл должен существовать.
- Конвенция «платформозависимый код → windows/-директории» (решение
  пользователя): плеер — `src/support/sound/windows/sound_player.py`;
  фабрика по `sys.platform` в `src/support/sound/sound_player.py`
  (win32 → MciSoundPlayer, иначе → NoopSoundPlayer — безопасный дефолт).
- `user_activity_monitor.py` (тоже Windows-only, ctypes.windll) в этой задаче
  НЕ переносится — отдельная задача по той же конвенции.
- playsound 1.3.0 не имеет API громкости (open → play wait → close без alias),
  поэтому заменяется собственным MCI-кодом; vendored wheel удаляется.
- MCI-последовательность: `open "<path>" type mpegvideo alias <uniq>` →
  `setaudio <alias> volume to <100…1000>` → `play <alias> wait` →
  `close <alias>`; alias уникальный на каждое воспроизведение; паттерн
  mciSendStringW + mciGetErrorStringW взять из playsound (см. Source of truth).
- Стиль: loguru, `logger.trace('Class: method_name')` первой строкой нового
  метода; приватные поля `self.__name`; вызовы с именованными аргументами.
- Оба spec-файла (EyesGuard.spec, EyesGuard-onedir.spec) остаются как есть,
  кроме `hiddenimports += 'support.sound.windows.sound_player'` (фабричный
  импорт внутри функции — гарантия попадания в бандл).

## Hypotheses

- MCI-команда `setaudio volume` поддерживается MPEGVideo-драйвером для MP3.
  Проверка: воспроизведение на 10/50/100 % на слух на Windows. Если команда
  вернёт ошибку — fallback: играть без setaudio (safe default), логировать
  warning; настройки/архитектуру не менять.

## Constraints

- Windows-only код — только в `src/support/sound/windows/`; на Linux не
  импортируется и не тестируется (no-op ветка фабрики).
- MVC-границы: логика — Model, UI — View/wnd_settings, конфигурация —
  src/config/, инфраструктура — src/support/.
- Новые зависимости не добавлять; playsound удаляется полностью.
- pydantic-валидация обязательна: битый settings.json переживается на
  дефолтах (`volume=100`); границы `ge=10, le=100`.
- Не трогать General-секцию, кроме удаления чекбокса sounds; скрытый чекбокс
  notifications не трогать; `user_activity_monitor.py` не трогать.
- CHANGELOG: Keep a Changelog 1.1.0, английский, записи в [Unreleased].
- Ruff 0.16.4, команды с `--config=./linter_ruff.toml`, только затронутые файлы.

## Non-goals

- Не переносить `user_activity_monitor.py` в windows-директорию (отдельная
  задача).
- Не менять onefile/onedir-структуру spec-файлов (кроме hiddenimports).
- Не добавлять pycaw/per-app громкость, эквалайзеры, предпрослушивание.
- Не менять логику on/off чекбокса sounds в SoundNotificator.

## Source of truth

- Скилл сквозного добавления настройки: `.agents/skills/add-user-setting/SKILL.md`.
- Память проекта: `.agents/memory/app/settings.md`, `.agents/memory/prj/style.md`,
  `.agents/memory/prj/known-issues.md`.
- Эталон добавления настройки по всем слоям: коммит `7f2e702`
  (activity_timeout: settings.py → wnd_settings.py → view.py → model.py → тесты).
- Паттерн MCI-кода: playsound 1.3.0, функция `_playsoundWin`
  (в wheels/ будет удалён — смотри git-историю файла wheels/ или sdist).
- Виджеты окна настроек: `src/windows/wnd_settings.py`
  (frame_general_settings, select_frame_by_name, apply_ui_settings, update).
- Тесты: `tests/test_settings.py`, fixture — `tests/data/*.json`.

## Required checks

- `uv run ruff check --fix --config=./linter_ruff.toml <затронутые файлы>`.
- `uv run ruff format --config=./linter_ruff.toml <затронутые файлы>`.
- `uv run pytest -v` — все зелёные, включая новые тесты volume (границы
  10/100 валидны, 9/101 → дефолт 100).
- `uv lock` — успешная регенерация после удаления playsound.
- Контракт будущего `scripts/verify.py` (в директории задачи): (1) `playsound`
  не встречается в pyproject.toml и src/ (grep); (2) в `SettingsDataValidator`
  есть `volume` с `ge=10, le=100`; (3) существует
  `src/support/sound/windows/sound_player.py`; (4) `pytest` зелёный.
  Успех — все проверки пройдены.
- Ручные на Windows: вкладка Sounds (иконка speaker.png, переключение кадров),
  слайдер 10–100 % на слух, чекбокс mute, round-trip settings.json, обе
  сборки (EyesGuard.spec, EyesGuard-onedir.spec) — запуск и звук.

## Stop conditions

- Готово: все слои настройки добавлены (модель → валидатор → виджет → чтение
  из UI → плеер → тесты), линт и тесты зелёные, playsound удалён из
  зависимостей и кода.
- Остаточные замечания (отсутствие speaker.png, результаты ручной проверки
  звука/сборок) — зафиксировать в `.agents/tasks/sounds-volume-setting/status.md`,
  дальнейшую шлифовку не вести.
