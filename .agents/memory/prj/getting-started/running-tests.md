# Прогон тестов

Из корня проекта (env агента — Linux; тестируются только не-GUI модули: `config/settings.py`, `config/states.py`, тайминги `Model`):

```bash
.venv/bin/python -X utf8 -m pytest ./tests/ -v
```

- Флаг `-X utf8` обязателен (кодировка тестовых данных).
- Ожидаемо на 2026-11-18: 11 passed (`tests/test_settings.py`).
- Тесты кладут `sys.path.insert(0, "./src")` — запускать только из корня репозитория.

## Что покрывать тестами при доработках

- `Settings`: границы валидации (1..100), дефолты при битом файле, запись в файл — образец: `tests/test_settings.py` (параметризация + fixture-JSON в `tests/data/`).
- `CurrentState`/`StepData` (`src/config/states.py`): remaining time, reset/increase.
- Логика таймингов `Model` — через подмену View (Mock) и мок `UserActivityMonitor`/`SoundNotificator` без создания Tkinter (эти зависимости Windows-only — в тестах не импортировать реальными).

GUI-окна в автоматических тестах не запускаются — ручная проверка на Windows.
