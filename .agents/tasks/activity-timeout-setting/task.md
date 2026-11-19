# Задача: вынести activity timeout в пользовательские настройки

## Постановка (промпт пользователя)

Нужно вынести время до включения флага `is_user_active` в настройки приложения:
должна появиться новая настройка в окне настроек, она должна сохраняться и читаться.
Интервал в секундах от 30 до 600.

## Уточнения (решения пользователя)

- Дефолт: **180 сек** (сохранение прежнего поведения — 3 мин).
- Системная константа `SystemSettingsData.USER_ACTIVITY_TIMEOUT` — **удалить**
  (единственный источник истины — `user_settings.activity_timeout`).

## Итог

- Новое поле `UserSettingsData.activity_timeout: int = 180`,
  валидация `SettingsDataValidator`: `Field(default=180, ge=30, le=600)`.
- Виджет: секция Time settings окна настроек (label + CTkEntry с посимвольной
  валидацией до 3 цифр; границы 30–600 проверяет pydantic на Apply).
- Чтение из UI: `View.__get_user_settings_from_wnd_settings`.
- Логика: `Model` создаёт `UserActivityMonitor` с
  `timedelta(seconds=user_settings.activity_timeout)`;
  `apply_new_user_settings` пересоздаёт монитор — смена применяется без перезапуска.
- Тесты: границы 30/600 валидны, 29/601 → откат на дефолт 180
  (fixture-файлы в `tests/data/`); обновлены ожидаемые строки существующих тестов.
- Константа `USER_ACTIVITY_TIMEOUT` удалена из `SystemSettingsData`.
