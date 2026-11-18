# Стиль кода проекта

Обязателен для **новых** правок. Существующий (legacy) код под эти правила массово не переписывается
(см. [known-issues.md](known-issues.md)); при касании конкретной функции можно привести её к стилю.

## Общее

- Python 3.11; именование: классы `CamelCase`, методы/переменные `snake_case`, константы dataclass-настроек `UPPER_SNAKE_CASE`.
- Комментарии, docstrings, тексты логов и сообщений UI — на английском.
- Длина строки ≤ 110 (`linter_ruff.toml`), кавычки одинарные (`ruff format`, `quote-style = "single"`).
- Вызовы — с именованными аргументами там, где это улучшает читаемость: `set_step(new_step_type=StepType.work_mode)`.
- Приватные поля класса — с двойным подчёркиванием: `self.__settings`; «защищённые» — с одним: `self._activity_timeout`.

## Структура импортов

- Абсолютные импорты «от корня src»: `from config.settings import Settings`, `from support.logger import logger`, `from config.states import StepType`.
- Инфраструктура (`logger`, `resourses`, `sound`, `user_activity_monitor`) — в `src/support/`; конфигурация и состояния — в `src/config/`; не плодить новые плоские модули в корне `src`.

## Логирование (loguru)

Конвенция проекта — логировать **в начале каждого метода** и на значимых ветках:

```python
logger.trace("Model: __set_current_step")          # вход в метод
logger.debug(f"Model: new step {step_type}")        # значимые данные
```

- Формат сообщения: `"<Класс>: <что происходит>"` (префикс класса обязателен).
- Уровни: `trace` — вход в методы; `debug` — данные; `info` — ключевые события; `warning` — невалидные ответы API; `error` — пойманные исключения (логировать сообщение и/или `repr(e)`), затем безопасный дефолт.
- Новые методы добавлять `logger.trace("Class: method_name")` первой строкой.

## Архитектурные конвенции

- MVC: логика таймингов/состояний — только в `Model`; UI — только в `View`/`windows/*`; оркестрация — `Controller`; инфраструктура — `support/`; конфигурация — `config/` (см. [architecture/overview.md](architecture/overview.md)).
- Циклические импорты типов разрывать паттерном `from __future__ import annotations` + `TYPE_CHECKING` (пример: `src/model.py`, `src/windows/wnd_settings.py`).
- Состояния — через `IntEnum StepType` и `match`/`case`; данные шага — dataclass `StepData`.
- Настройки: dataclass-модель + pydantic-валидатор; любое поле с дефолтом и границами (см. [настройки](../app/settings.md)).
- Фоновые операции (звук) — в отдельном потоке, с проверкой ресурса и логом вместо падения (образец: `SoundPlayer`).
- Обработка ошибок — try/except с логированием и безопасным дефолтом (падать нельзя: это фоновая утилита пользователя).

## Тесты

- pytest; параметризация для граничных значений; fixture-файлы JSON в `tests/data/`.
- Тесты не должны требовать GUI и Windows: тестируем `config/settings.py`, `config/states.py`, тайминги `Model` (без создания `View`).
- Запуск из корня проекта: `python -X utf8 -m pytest ./tests/` (флаг `-X utf8` обязателен).

## Версионирование, CHANGELOG и коммиты

- Версии — SemVer (X.Y.Z).
- `CHANGELOG.md` — Keep a Changelog 1.1.0: раздел `[Unreleased]` + категории Added / Changed /
  Deprecated / Removed / Fixed / Security; новая запись — **одна строка** на фичу, язык — английский.
- Коммиты — Conventional Commits, сообщения на английском: `type(scope): description`
  (типы: feat, fix, docs, style, refactor, perf, test, build, ci, chore).

## Чего не делать

- Не переименовывать модули/публичные методы без явного поручения (напр. опечатка `resourses.py` сохранена осознанно).
- Не менять стиль форматтера (одинарные кавычки заданы в `linter_ruff.toml`), не менять стиль логирования.
- Не добавлять новые зависимости без явного согласования с пользователем.
- Не вызывать GUI-API в коде, который должен работать в тестах (Linux, без дисплея).
