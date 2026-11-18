# Настройки приложения

Код: `src/config/settings.py`. Хранилище: `settings/settings.json` — путь задаёт константа
`SETTINGS_FILE` в `src/model.py` через `support.paths.app_dir()` (dev — от CWD/корня проекта;
frozen-сборка PyInstaller — рядом с exe). Каталог `settings/` создаётся автоматически при первой записи.

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
| `sounds` | Literal["on","off"] | "on" | — (управляет `SoundNotificator`) |
| `notifications` | Literal["on","off"] | "on" | — (управляет уведомлениями трея) |
| `protection_status` | Literal["on","off"] | "on" | — (начальный шаг при старте) |

## SystemSettingsData (константы, UPPER_SNAKE_CASE)

| Поле | Значение | Использование |
|---|---|---|
| `STEP_SUSPENDED_MODE_DURATION` | 60 мин | off_mode / suspended_mode |
| `STEP_NOTIFICATION_1_DURATION` | 55 с | work_notified_1 |
| `STEP_NOTIFICATION_2_DURATION` | 5 с | work_notified_2 |
| `USER_ACTIVITY_TIMEOUT` | 3 мин | порог неактивности в `UserActivityMonitor` |
| `TIME_TICK_S` | 1 с | тик `wait_for_current_step_is_ended` |

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
