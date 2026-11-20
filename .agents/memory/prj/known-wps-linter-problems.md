# Известные нарушения wemake-python-styleguide (WPS)

Реестр подавленных нарушений WPS-линтера. Все существующие на момент внедрения нарушения
зафиксированы здесь и подавлены конфигом `.flake8`; исправление планируется в будущих релизах.

- **Дата базовой линии:** 2026-11-20
- **Версии:** wemake-python-styleguide 1.9.0, flake8 7.5.0 (dev-зависимость pyproject, `uv.lock`)
- **Базовая линия:** **566 нарушений** в `src/` + `tests/` (прогон `--select=WPS --max-line-length=120`)
- **Текущее состояние:** `uv run --no-sync flake8 --config=.flake8 --count src tests` → **0 нарушений**
- **Запуск:** `uv run --no-sync flake8 --config=.flake8 --select=WPS src tests` (из корня проекта;
  `--select=WPS` — документированный способ запуска WPS, только WPS-коды)
- **Где включено:** pre-commit/pre-push хуки (prek, local hook) + шаг в CI `.github/workflows/tests.yml`

## Как устроено подавление (уровни в `.flake8`)

| Уровень | Что это | Коды |
|---|---|---|
| 1. `ignore` (постоянное) | Конфликт с конвенцией проекта или осознанный дизайн | WPS112, WPS120, WPS230, WPS365 |
| 2. Лимиты (правило активно) | Порог поднят от дефолта WPS; новые нарушения сверх лимита ловятся | WPS118, WPS201, WPS210, WPS213, WPS214, WPS218, WPS221, WPS226, WPS229, WPS231, WPS236 |
| 3. `per-file-ignores` (временное) | Legacy-выбросы сверх лимитов и коды без настраиваемых порогов | см. секции per-file в `.flake8` |
| 4. `# noqa` (точечное) | Разрешено: `max-noqa-comments = 5`; каждый noqa — с обоснованием в комментарии | — |

**Процесс устранения:** исправляете код → удаляете код нарушения из per-file-ignores
(или затягиваете лимит обратно) → `uv run --no-sync flake8 --config=.flake8 src tests` остаётся
зелёным → вычёркиваете строку из таблиц ниже. После полного устранения legacy-выбросов
рекомендуется затянуть лимиты: `max-jones-score = 16` → 14, `max-try-body-length = 5` → 1,
`max-string-usages = 6` → 3, `max-expressions = 14` → 9.

## Уровень 1 — постоянные отключения (не исправляются)

| Код | Нарушений | Обоснование |
|---|---|---|
| WPS112 private name pattern `__name` | 112 | Конвенция проекта: приватные поля — `self.__name` (WPS требует `_name`) |
| WPS120 trailing underscore `_fields_` | 1 | Обязательная идиома ctypes-прототипов WinAPI (`user_activity_monitor.py`) |
| WPS230 public instance attributes > 6 | 4 | Норма для Tk-форм: `WndSettings` — 53 атрибута-виджета; контейнеры состояния — dataclass-подобные |
| WPS365 `match` → `if` | 1 | Конвенция: состояния — только через `StepType` + `match/case` |

## Уровень 2 — лимиты (правило активно, текущий код проходит)

| Лимит в `.flake8` | Правило | WPS default → Наш лимит | Макс. факт | Комментарий |
|---|---|---|---|---|
| max-name-length | WPS118 too long name | 45 → 80 | 46 | pytest-имена ×49 (все в tests) |
| max-imports | WPS201 | 12 → 15 | 15 | ×3 (model, view, wnd_settings) |
| max-methods | WPS214 | 7 → 14 | 13 (25 у Model — пер-file) | ×9 |
| max-expressions | WPS213 | 9 → 14 | 50 (wnd_settings — per-file) | ×12 |
| max-asserts | WPS218 | 5 → 7 | 7 | ×2 (tests) |
| max-local-variables | WPS210 | 5 → 9 | 9 | ×5 |
| max-tuple-unpack-length | WPS236 | 4 → 5 | 5 | ×29 (tests/test_model_fsm) |
| max-string-usages | WPS226 | 3 → 6 | 30 (tests — per-file) | ×44 |
| max-try-body-length | WPS229 | 1 → 5 | 10 (per-file) | ×7 |
| max-jones-score | WPS221 | 14 → 16 | 19 (per-file) | ×43; после исправлений → 14 |
| max-cognitive-score | WPS231 | 12 → 14 | 23 (tests — per-file) | ×4 |

## Уровень 3 — реестр временных исключений (по кодам)

### Простые переименования / косметика (исправить первыми)

| Код | Сообщение | Всего | Где | Стратегия исправления |
|---|---|---|---|---|
| WPS110 | wrong variable name (`value`) | 16 | wnd_settings ×6, tests ×8, time_format ×1, user_activity_monitor ×1 | Осмысленные имена вместо `value` |
| WPS111 | too short name (`e`) | 3 | video_activity_monitor, sound_player, user_activity_monitor | `e` → `exc` |
| WPS114 | underscored number name (`STEP_NOTIFICATION_1_DURATION`) | 12 | settings ×2, states ×2, model ×2, tests ×6 | `STEP_NOTIFICATION_1_DURATION` → `STEP_FIRST_NOTIFICATION_DURATION` и т.п. |
| WPS115 | upper-case constant in a class | 6 | settings ×4, controller ×1, tests ×1 | Константы из класса → module-level |
| WPS339 | number with meaningless zeros (`0x00000002`) | 2 | screensaver_blocker, video_activity_monitor | `0x2` |
| WPS358 | float zero (`0.0`) | 4 | window_fade ×2, tests ×2 | `0.0` → `0` |
| WPS336 | explicit string concatenation | 1 | settings | Одна строка или join |
| WPS459 | comparison with float | 3 | tests/test_window_fade | `pytest.approx` |
| WPS301 | dotted raw import | 1 | tests/test_resourses | `from support import resourses` |
| WPS122 | all unused variables definition | 1 | user_activity_monitor | Убрать переменную или использовать |

### Поток/структура (средняя сложность)

| Код | Сообщение | Всего | Где | Стратегия исправления |
|---|---|---|---|---|
| WPS420 | wrong keyword: `pass` | 3 | controller, paths, user_activity_monitor | Логирование/явная обработка вместо `pass` (соответствует конвенции проекта) |
| WPS504 | negated condition | 2 | model ×2 | Инвертировать условие |
| WPS505 | nested `try` block | 2 | sound_player ×2 | Вынести вложенный try в функцию |
| WPS501 | `finally` without `except` | 2 | wnd_settings, tests/test_model_fsm | Добавить except или убрать finally |
| WPS404 | complex default value | 3 | states ×2, user_activity_monitor | Дефолт `None` + инициализация в теле |
| WPS604 | incorrect node in class body | 1 | controller | Вынести выражение из тела класса |
| WPS458 | imports collision (`dataclasses`) | 2 | settings, sound_player | Единый стиль импорта модуля |
| WPS338 | incorrect order of methods | 9 | 9 файлов src | Порядок public → private |
| WPS430 | nested function | 10 | window_fade ×1, tests ×9 | Вынести вложенные функции |
| WPS229 | too long try body | 7 (выбросы 6/9/10) | settings ×2, view, video_activity_monitor, user_activity_monitor, paths, sound_player | Вынести тело try в методы |
| WPS220 | too deep nesting (24 > 20) | 1 | controller | Декомпозиция вложенного блока |
| WPS204 | overused expression `(25, 25)` | 13 | wnd_settings ×7, tests ×6 | Константа `ICON_SIZE = (25, 25)` |

### Требуют рефакторинга (связаны с known-issues.md)

| Код | Сообщение | Всего | Где | Стратегия исправления |
|---|---|---|---|---|
| WPS237 | too complex formatted string | 19 | model ×12, time_format ×2, wnd_settings ×2, wnd_status ×2, sound_player ×1 | Промежуточные переменные вместо выражений в f-строках |
| WPS221 | high Jones Complexity (выбросы 17–19) | 43 (≈20 на лимите 16) | wnd_settings ×17, wnd_status ×5, tests ×21, window_fade, wnd_break, sound_player | Разнести сложные выражения; после — jones 16 → 14 |
| WPS213 | too many expressions (выбросы 17/27/50) | 12 (≈9 на лимите 14) | wnd_settings ×3 (до 50), model ×3 (до 27), wnd_status ×2 (до 17), settings, controller, main, wnd_break | Разбиение init-методов на helpers |
| WPS214 | too many methods (выбросы 20/20/25) | 9 (≈5 на лимите 14) | model ×1 (25), view ×1 (20), wnd_settings ×1 (20), settings, states, controller, sound_player, wnd_status, tests | Разбиение крупных классов Model/View/WndSettings на меньше классы/модули |
| WPS231 | cognitive complexity (выбросы 16/23) | 4 (модель/звук на лимите 14) | model, sound_player, tests ×2 | Декомпозиция FSM/звуковых функций (тестовые — реорганизация теста) |
| WPS202 | too many module members | 6 | tests ×6 | Разнести тесты по модулям |
| WPS615 | unpythonic getter/setter (`set_model` и т.п.) | 4 | controller ×2, model, view | property вместо set_X-методов |
| WPS432 | magic number | 115 (115 в tests и windows, вне их — 10) | wnd_settings ×28, wnd_status ×11, wnd_break ×4, settings ×8, tests ×60+, time_format ×1, user_activity_monitor ×1 | Константы для таймингов/размеров; GUI-координаты — оставить исключение |

## Связанные документы

- Конфиг подавления: `.flake8` (уровни 1–3 с комментариями)
- Связанный техдолг: [known-issues.md](known-issues.md) (ловушки для агента; WPS214/WPS231 — крупные классы Model/View/WndSettings)
- Стиль кода: [style.md](style.md)
