# Известные проблемы и ловушки

Фактическое состояние ветки `feature/v2.1.0` (зафиксировано при онбординге 2026-11-18). Исправлять —
только по явному поручению пользователя, пункт за пунктом.
Пункты 11-20 добавлены по итогам ревью проекта 2026-11-19 (ветка после v2.3.0, коммит d7af539).

## Техдолг (не трогать в рамках других задач)

| # | Проблема | Где |
|---|---|---|
| 1 | ~~Pillow отсутствует в requirements.txt~~ — решено: зависимости переведены на `pyproject.toml` + `uv.lock` (pillow добавлен, requirements.txt удалён 2026-11-18) | зависимости |
| 2 | `Controller.stop()` — пустая заглушка; поток `main_loop` не останавливается никогда; выход через `os._exit(0)` | src/controller.py, src/view.py |
| 3 | Модальные окна обновляются из контроллерного потока — Tkinter формально потоконебезопасен | src/model.py → View.update_* |
| 4 | logger.py пересоздаёт `logs/log.log` при каждом импорте модуля (`unlink`); sink с уровнем `WARNING`, при этом в коде множество `logger.trace/debug/info` — в файл они не попадают | src/support/logger.py |
| 5 | Дублирование строки `ui_settings_data.protection_status = ...` в `__get_user_settings_from_wnd_settings` | src/view.py |
| 6 | `Model.settings` setter пустой (только лог); имя вводит в заблуждение | src/model.py |
| 7 | В тестах одновременно `sys.path.insert(0, "./src")` и импорт `from config.settings import ...` — работает только при запуске из корня | tests/test_settings.py |
| 8 | `set_new_step_in_sequence` не имеет case для `iddle_mode`: если туда попасть из iddle — UnboundLocalError на `new_step_type`. Сейчас не воспроизводится (wait-цикл уходит из iddle раньше), но уязвимость к будущим правкам | src/model.py |
| 9 | Опечатки в сообщениях: "occuired", "settind", "widnow" — в legacy-строках сохраняются | src/view.py, src/model.py |
| 10 | Лог `Switch to iddle mode...` на info-уровне каждый тик при idle — шум в логе при WARNING-синке не виден, но захламляет при смене уровня | src/model.py |
| 11 | **Data race на состояние**: `CurrentState`/`steps_data_list` мутируются из Tk-потока (`view.set_step` → `model.set_step`; `apply_new_user_settings` → `__init_steps`) одновременно с чтением/записью в controller-потоке (`wait_for_current_step_is_ended`) — без блокировок. Шире п.3 (там только потоконебезопасность Tk): гонка на самих данных | src/model.py:296-357, 398 |
| 12 | **`steps_data_list` растёт при каждом Apply настроек**: `apply_new_user_settings` вызывает `__init_steps()`, а тот делает `insert()` в непустой список без очистки → +7 «мусорных» элементов, лог-шум, ловушка для будущих правок | src/model.py:36, 50-53, 386 |
| 13 | **Смена любых настроек сбрасывает таймер шага и играет звук/уведомление**: `apply_new_user_settings` → `__init_steps` → `set_step(...)` → `do_current_step_actions` (включая `play_notification_work`). Изменил только громкость — потерял прогресс до перерыва | src/model.py:380-386, 89-94 |
| 14 | **Двойной звук/действия при старте приложения**: `set_view` → `__init_steps` → `set_step` → `do_current_step_actions`, затем первая итерация `main_loop` вызывает `do_current_step_actions` снова для того же шага | src/controller.py:33-36, src/model.py:96 |
| 15 | **У View собственные источники состояния**: `View.__init__` создаёт `Settings()` (дефолт, без файла) и отдельный `CurrentState()`, передаёт их в `WndSettings`/`WndBreak` — не связаны с Model. Работает случайно, т.к. `update(model)` читает из model | src/view.py:32-35 |
| 16 | **`ResImages`: `Image.open` на атрибутах класса при импорте** — отсутствующий файл = крах на импорте; fallback-try есть только у `monitor.png` (несогласованно) | src/support/resourses.py:11-30 |
| 17 | **`time.sleep(0.006)×100` в `show()/hide()`** — 0.6 с блокировки Tk mainloop; для `WndBreak` анимация запускается и из controller-потока. Правильно — `after()`-анимация | src/windows/wnd_break.py:67-89, src/windows/wnd_status.py:101-114, src/windows/wnd_settings.py:398-411 |
| 18 | `__get_user_settings_from_wnd_settings` ловит только `TypeError`, а `int()` на пустой строке кидает `ValueError` → падение колбэка, настройки не применятся | src/view.py:91-106 |
| 19 | `__repr__` возвращает `dict` в `UserSettingsData`/`Settings`/`CurrentState` — нарушение контракта Python; сериализация через `dir()` хрупка (поймает любой публичный метод). Правильно — `dataclasses.fields`/`asdict` | src/config/settings.py:45-61, src/config/states.py:41-56 |
| 20 | Документация vs реальность: AGENTS.md заявляет покрытие тестами `config/states.py` и «таймингов Model» — таких тестов нет (только settings/sound_player/app_version). Не покрыта главная логика: переходы `set_new_step_in_sequence`, idle/video-debounce | tests/, AGENTS.md |

## Ловушки для агента

- **CWD обязателен — корень проекта**: относительные пути `res/img/`, `res/sounds/`, `./settings/`, `./logs/` ломаются при запуске из другого каталога.
- **`-X utf8` обязателен** при запуске pytest (символы в тестовых данных).
- **Не запускать `ruff check --fix` на всём проекте**: на legacy ~100+ находок — массовый автофикс замусорит diff. Линтер — только на затронутые задачей файлы/функции.
- **Windows-only код**: `user_activity_monitor.py` (`ctypes.windll`) и MCI-плеер
  (`support/sound/windows/sound_player.py`, импортируется фабрикой только на win32) на Linux
  не работают — их не импортировать в тестируемые на Linux модули без изоляции.
- ~~**`playsound==1.3.0`** — старый пакет, известен проблемами на некоторых системах; замена — только по согласованию.~~ Решено: с v2.2.0 заменён собственным MCI-плеером (`src/support/sound/windows/`), зависимость и vendored wheel удалены.
- Тесты GUI отсутствуют: на Linux (агентная среда) можно гонять только не-GUI тесты; ручная проверка GUI — только на Windows.
- `steps_data_list` — list, индексируемый `IntEnum`; `insert` в цикле работает только потому, что enum — 0..N подряд (не «улучшать» на dict без задачи).
- Property `Model.model` возвращает `self` — обращения `self.model.X` легитимны в этом коде.
- Скрытые директории `.codegraph/`, `.serena/`, `.venv/` — локальная инфраструктура агента, в git не коммитятся (см. `.gitignore`).

## Аналитика линтера

2026-11-18: «генеральная уборка» выполнена — `uv run ruff check .` → **0 находок** (было 21:
I001, F401, F541, PIE790, RUF010, UP031 исправлены; BLE001 ×2 помечены `# noqa: BLE001`
как осознанный паттерн «safe default»). Новая база приёмки: линт на весь проект должен
оставаться зелёным, CI гоняет его на каждом PR.
