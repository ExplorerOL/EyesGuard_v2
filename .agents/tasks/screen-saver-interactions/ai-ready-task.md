# AI-ready задача: screen-saver-interactions

## Problem

Пользователю нужны: (1) блокировка скринсейвера на время перерыва; (2) автоматический
переход в `iddle_mode` при проигрывании видео (экран «занят»); (3) три новые настройки
в UI, включая сброс рабочего времени при переходе в idle.

## Context

- Проект: EyesGuard_v2, Python 3.11, CustomTkinter, Windows 10 — читать `AGENTS.md`.
- Домен: `.agents/memory/app/state-machine.md`, `.agents/memory/app/settings.md`.
- Решения и их обоснование: `decisions.md` (обязателен к соблюдению).
- Факты исследования: `research.md`.

## Scope

Реализовать exactly:

1. **Настройки** (`src/config/settings.py`):
   - `UserSettingsData`: `screensaver_block = OnOffValue.on.value`,
     `suspend_on_video = OnOffValue.on.value`, `reset_work_time_in_idle = OnOffValue.off.value`.
   - `SettingsDataValidator`: `Literal['on', 'off']` с теми же дефолтами.
   - `_settings_to_dict`/`__apply_settings` идут по `dir()` — доработка не нужна.

2. **Новый модуль** `src/support/display/` (образец — `src/support/sound/sound_player.py`:
   Protocol + noop + фабрика по `sys.platform == 'win32'`, windows-импорт только внутри фабрики):
   - `screensaver_blocker.py`: `PScreensaverBlocker` (Protocol: `block()`, `release()`),
     `NoopScreensaverBlocker`, `create_screensaver_blocker()`.
   - `video_activity_monitor.py`: `PVideoActivityMonitor` (Protocol: property
     `is_video_playing -> bool`), `NoopVideoActivityMonitor` (False),
     `create_video_activity_monitor(debounce_ticks=5)`.
   - `windows/screensaver_blocker.py`: `WindowsScreensaverBlocker` —
     `ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_DISPLAY_REQUIRED)`
     в `block()`, `SetThreadExecutionState(ES_CONTINUOUS)` в `release()`; внутренний флаг
     активности (idempotent); NULL-результат → `logger.error`, приложение не падает.
     Docstring: вызовы обязаны идти из одного потока (поток контроллера).
   - `windows/video_activity_monitor.py`: `WindowsVideoActivityMonitor` —
     `ctypes.windll.powrprof.CallNtPowerInformation(16, None, 0, buf, 4)`; NTSTATUS != 0 или
     исключение → safe default `False` (как `UserActivityMonitor.__get_user_idle_time_from_os`);
     флаг `ES_DISPLAY_REQUIRED` (0x2) → True; debounce: False только после `debounce_ticks`
     последовательных опросов без флага.

3. **Model** (`src/model.py`):
   - `__init__`: создать `self.__screensaver_blocker`, `self.__video_activity_monitor` фабриками.
   - `do_current_step_actions` (в начале): `break_mode` + `screensaver_block=='on'` → `block()`;
     иначе → `release()`.
   - `wait_for_current_step_is_ended`:
     - `video_active = suspend_on_video=='on' and self.__video_activity_monitor.is_video_playing`;
     - вход в iddle: `(not is_user_active or video_active) and step in {work_mode, work_notified_1, work_notified_2}`;
     - выход: `is_user_active and not video_active and step == iddle_mode`.
   - `__set_current_step`: при `step_type == iddle_mode` и `reset_work_time_in_idle=='on'` →
     `self.__current_state.reset_elapsed_time()` (до `set_current_step_data`).

4. **Ресурсы** (`src/support/resourses.py`): `img_monitor` = `res/img/monitor.png`;
   `except OSError` → fallback `img_gear` + `logger.warning` (файл добавит пользователь позже).

5. **UI** (`src/windows/wnd_settings.py`):
   - Кнопка `btn_display_settings` «Display» (между Sounds и About; About → row=6),
     иконка `ResImages.img_monitor` (size 25×25).
   - `frame_display_settings`: `chbox_screensaver_block` «Block screensaver during breaks»,
     `chbox_suspend_on_video` «Suspend timer on video playback» (образец — `chbox_sounds`).
   - Вкладка Time settings: `chbox_reset_work_time_in_idle` «Reset working time in idle mode» (row=3).
   - `select_frame_by_name` + `event_btn_display_settings_click` + `update()` для трёх значений.

6. **Чтение UI** (`src/view.py`, `__get_user_settings_from_wnd_settings`): +3 строки по образцу `sounds`.

7. **Тесты** (`tests/test_settings.py` + fixtures в `tests/data/`):
   - Обновить строковые эталоны: `str(settings)` — алфавитный порядок (`dir()`), новые поля
     `reset_work_time_in_idle`, `screensaver_block`, `suspend_on_video` на своих местах;
     `test_write_*` — JSON-эталоны (новые поля в конце, порядок объявления валидатора).
   - Новые: валидные on/off значения; невалидное значение (напр. `"yes"`) → весь файл
     отбрасывается, дефолты (существующее поведение валидатора); частичный/старый JSON →
     дефолты новых полей (`settings_valid_no_param.json` — расширить ожидания).

8. **Документация**: CHANGELOG `[Unreleased]`/новая версия — 3 строки Added (английский);
   `.agents/memory/app/settings.md` (таблица полей), `.agents/memory/app/state-machine.md`
   (переходы по видео, сброс elapsed, блокировка скринсейвера); граф знаний
   (`memory_add_observations` к Settings/Model/WndSettings + при необходимости сущность
   display-модуля); `.agents/tasks/README.md` — статус задачи.

## Non-goals

- Не менять `SystemSettingsData` и 60-минутную длительность suspended_mode.
- Не рефакторить legacy (known-issues.md), включая пустой `Controller.stop()`.
- Не добавлять зависимости; не трогать звук/уведомления iddle (используются штатные).
- Не реализовывать «auto-suspend через suspended_mode» (снято решением пользователя).
- Скринсейвер блокируется ТОЛЬКО на время break_mode (не «пока приложение работает»).

## Required checks

```sh
uv run ruff check --fix --config=./linter_ruff.toml src/config/settings.py src/model.py src/view.py src/support/resourses.py src/support/display src/windows/wnd_settings.py tests/test_settings.py
uv run ruff format --config=./linter_ruff.toml <те же файлы>
uv run pytest -v
```

Критерий: ruff — 0 находок, pytest — все тесты зелёные (запуск из корня проекта).

## Stop conditions

- Противоречие между решениями пользователя (`decisions.md`) и кодом — остановиться и спросить.
- Тесты/линт не зелёные после исправимых правок — не «подгонять» тесты ослаблением проверок
  без понимания; сообщить.

## Ручные проверки (Windows, после реализации)

1. Скринсейвер с таймаутом 1 мин не запускается во время перерыва (screensaver_block=on);
   при off — запускается.
2. Видео в браузере (fullscreen и в окне) → уведомление «iddle mode», отсчёт замирает;
   после окончания видео и при активности — продолжается.
3. Вкладка Display: два чекбокса; Time settings: чекбокс сброса; Apply → settings.json.
4. reset_work_time_in_idle=on: войти в idle (бездеятельность 3+ мин), вернуться — отсчёт с нуля.
