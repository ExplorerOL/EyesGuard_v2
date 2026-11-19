# Настройки приложения

Код: `src/config/settings.py`. Хранилище: `settings/settings.json` — путь задаёт константа
`SETTINGS_FILE` в `src/model.py` через `support.paths.app_dir()` (dev — от CWD/корня проекта;
frozen-сборка PyInstaller — `%LOCALAPPDATA%/EyesGuard` с миграцией из каталога exe).
Каталог создаётся автоматически; запись атомарная (tmp-файл + `replace()`), чтение переживает
любые `OSError`. Путь `Settings(file_name)` обязателен; `user_settings` на чтение возвращает
копию; `apply_settings_from_ui`/`save_settings_to_file` возвращают `bool`. Контракт типов —
нестрогой (lax): строки-числа и целочисленные float коэрцируются, дробные/null/неверные
литералы отклоняются, файл с одним невалидным полем отклоняется целиком, неизвестные поля
игнорируются (см. docstring `SettingsDataValidator`).

## Модель

| Класс | Тип | Назначение |
|---|---|---|
| `UserSettingsData` | dataclass | Пользовательские настройки (то, что редактируется в UI) |
| `SystemSettingsData` | dataclass | Системные константы таймингов (UPPERCASE-поля, не в JSON) |
| `SettingsDataValidator` | pydantic BaseModel | Валидация значений (чтение из файла и из UI) |
| `Settings` | — | Фасад: чтение/валидация/применение/сохранение |

## Поля UserSettings

| Поле | Тип | Дефолт | Границы валидации |
|---|---|---|---|
| `work_duration` | int | 45 | 0 < x < 101 (мин) |
| `break_duration` | int | 15 | 0 < x < 101 (мин) |
| `activity_timeout` | int | 180 | 30 <= x <= 600 (сек; порог `is_user_active` в `UserActivityMonitor`) |
| `volume` | int | 100 | 1 <= x <= 100 (%; громкость MCI-плеера, 0 не предусмотрен — mute чекбоксом `sounds`) |
| `sounds` | Literal["on","off"] | "on" | — (управляет `SoundNotificator`) |
| `notifications` | Literal["on","off"] | "on" | — (управляет уведомлениями трея) |
| `protection_status` | Literal["on","off"] | "on" | — (начальный шаг при старте) |
| `screensaver_block` | Literal["on","off"] | "on" | — (блокировка скринсейвера на время break; `src/support/display/`) |
| `suspend_on_video` | Literal["on","off"] | "on" | — (переход в iddle при видео — системный флаг `ES_DISPLAY_REQUIRED`) |
| `reset_work_time_in_idle` | Literal["on","off"] | "off" | — (сброс elapsed при входе в iddle_mode; off = существующая заморозка) |

## SystemSettingsData (константы, UPPER_SNAKE_CASE)

| Поле | Значение | Использование |
|---|---|---|
| `STEP_SUSPENDED_MODE_DURATION` | 60 мин | off_mode / suspended_mode |
| `STEP_NOTIFICATION_1_DURATION` | 55 с | work_notified_1 |
| `STEP_NOTIFICATION_2_DURATION` | 5 с | work_notified_2 |
| `TIME_TICK_S` | 1 с | тик `wait_for_current_step_is_ended` |

> Примечание: раньше порог неактивности был константой `USER_ACTIVITY_TIMEOUT` в
> `SystemSettingsData`; с версии с настройкой `activity_timeout` он вынесен в
> пользовательские настройки (виджет в секции Time settings окна настроек).
> `Model.apply_new_user_settings` пересоздаёт `UserActivityMonitor` — смена порога
> применяется без перезапуска приложения.

> Звук (v2.2.0): чекбокс `sounds` и слайдер `volume` (CTkSlider 1–100 %) живут на
> вкладке Sounds окна настроек. Воспроизведение — Windows MCI-плеер
> `MciSoundPlayer` (`src/support/sound/windows/sound_player.py`); фабрика
> `create_sound_player()` по `sys.platform` (win32 → MCI, иначе `NoopSoundPlayer`).
> Громкость передаётся в `play(file_path, volume)` при каждом вызове — смена
> применяется к следующему воспроизведению без перезапуска. Платформенная
> конвенция: Windows-only код — в `src/support/<module>/windows/`.

> Дисплей (после v2.2.0): чекбоксы `screensaver_block` и `suspend_on_video` живут на
> вкладке Display окна настроек (иконка `res/img/monitor.png` с fallback на `gear.png`);
> `reset_work_time_in_idle` — на вкладке Time settings. Windows-реализации —
> `src/support/display/windows/` (`SetThreadExecutionState` для блокировки скринсейвера
> на break; `CallNtPowerInformation(SystemExecutionState)` → `ES_DISPLAY_REQUIRED` как
> детектор видео с debounce ~5 тиков); фабрики по `sys.platform` (иначе noop). Подробности:
> `state-machine.md`, задача `.agents/tasks/screen-saver-interactions/`.

## Поведение при ошибках

- Файл не найден / невалидный JSON / невалидные значения → лог error + применение **дефолтных** значений (приложение продолжает работать). Покрыто тестами `tests/test_settings.py`.
- `apply_settings_from_ui` при невалидных данных: лог error, настройки НЕ применяются, файл НЕ пишется.
- `save_settings_to_file` валидирует перед записью (`model_dump_json(indent=4)`).

## Поток данных

```
UI (WndSettings) → View.__get_user_settings_from_wnd_settings() → UserSettingsData
  → Controller.apply_view_user_settings → Model.apply_new_user_settings
  → Settings.apply_settings_from_ui (валидация + файл) → Model.__init_steps (пересчёт таймингов)
```

## Как добавить новое поле

1. Поле в `UserSettingsData` (со значением по умолчанию).
2. Поле в `SettingsDataValidator` (тип + ограничения + дефолт).
3. Виджет в `WndSettings` + чтение в `View.__get_user_settings_from_wnd_settings`.
4. Использование в `Model.__init_steps` / действиях шагов.
5. Тест в `tests/test_settings.py` (валидные границы + дефолт) + fixture-файл в `tests/data/` при необходимости.
6. Обновить эту заметку и граф знаний.
