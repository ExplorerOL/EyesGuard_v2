# Исследование: screen-saver-interactions

Дата: 2026-11-19. Ветка: feature/v2.1.0.

## Проверенные факты (codegraph + чтение файлов)

### Точки интеграции

| Область | Файл | Факт |
|---|---|---|
| Настройки | `src/config/settings.py` | `UserSettingsData` (dataclass, `_settings_to_dict` идёт по `dir()` — новые поля подхватываются автоматически), `SettingsDataValidator` (pydantic, `Literal['on','off']` для on/off), `Settings.apply_settings_from_ui/save_settings_to_file` |
| Машина состояний | `src/model.py` | `wait_for_current_step_is_ended` — тик 1 с (`TIME_TICK_S`), переходы в/из `iddle_mode` внутри цикла: вход при `not is_user_active and step in {work_mode, work_notified_1, work_notified_2}`, выход при `is_user_active and step == iddle_mode` |
| Заморозка времени | `src/model.py:161` `__set_current_step` | `reset_elapsed_time()` вызывается только если ни текущий, ни новый шаг не `iddle_mode` — счёт «замораживается» при idle |
| Действия шагов | `src/model.py` `do_current_step_actions` | вызывается из `set_step` и из `main_loop` контроллера — единая точка для block/release скринсейвера |
| Окно перерыва | `src/windows/wnd_break.py` | fullscreen (`-fullscreen True`) — детекция «занятости экрана» при break_mode неприменима (само окно заняло бы экран) |
| Окно настроек | `src/windows/wnd_settings.py` | «вкладки» = кнопки навигации + фреймы (Time/General/Sounds/About); чекбокс-образец: `chbox_sounds` (CTkCheckBox + StringVar, onvalue/offvalue='on'/'off') |
| Чтение UI | `src/view.py` `__get_user_settings_from_wnd_settings` | по строке на каждое поле |
| Ресурсы | `src/support/resourses.py` | PNG-иконки вкладок: clock/gear/info/speaker; `monitor.png` отсутствует (пользователь добавит позже) |
| Платформенная конвенция | `src/support/sound/` | фасад + `create_*()` по `sys.platform` ('win32' → `windows/`, иначе noop); windows-модуль импортируется только внутри фабрики |

### Windows API для реализации

- Блокировка скринсейвера: `kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_DISPLAY_REQUIRED)`; снятие — `SetThreadExecutionState(ES_CONTINUOUS)`. Привязано к потоку вызова → block/release обязаны идти из одного потока (поток `Controller.main_loop` — так и будет).
- Детекция видео: `powrprof.CallNtPowerInformation(SystemExecutionState=16, NULL, 0, &ULONG, sizeof)` возвращает агрегированные ES-флаги системы; `ES_DISPLAY_REQUIRED` (0x2) поднимают браузеры/плееры при проигрывании видео. NTSTATUS 0 = успех.
- Ограничение: некоторые плееры сбрасывают idle-таймер периодически (флаг мигает) → нужен debounce на снятие (~5 тиков подряд без флага).

### Тесты

- `tests/test_settings.py`: `str(settings)` сравнивается с ожидаемой строкой — `dir()` даёт алфавитный порядок, новые поля попадут в середину строк-эталонов; `test_write_*` сравнивают точный JSON (порядок полей = порядок объявления в `SettingsDataValidator`, новые поля в конце).
- `tests/data/*.json` — fixtures по образцу (`settings_valid_no_param.json` уже покрывает частичный JSON → дефолты pydantic).

## Открытые вопросы

Все решены пользователем (см. decisions.md).
