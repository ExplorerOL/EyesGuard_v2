# Статус: fix-known-issues

Дата: 2026-11-19, ветка `release/v2.3.1`.

## Итог

Все открытые пункты `known-issues.md` (№2–37; №1 был закрыт ранее) исправлены и отмечены
в этом файле. 35 коммитов (один коммит = одна проблема; для №8/12/19/26/18/10/9/35/34/36/31/5/27/28/37/25/33/2/3/11/15/13/14/21/24/23/22/4/16/17/32/6/10 + docs-коммиты статусов).

## Проверки

- `uv run pytest -v` — **118 passed** (было 25 на старте)
- `uv run ruff check . --config=./linter_ruff.toml` — 0 находок
- `uv run ruff format --check . --config=./linter_ruff.toml` — 37 files already formatted
- Все коммиты прошли prek-хуки (ruff check/format, check-yaml/json, large-files, name-tests-test)

## Новые тестовые файлы

- `tests/test_states.py`, `tests/test_model_fsm.py` (FSM, часы, idle, Apply, эффекты)
- `tests/test_controller.py` (очередь команд, единственный писатель, stop/restart, crash-callback)
- `tests/test_user_activity_monitor.py` (wrap-safe idle, сброс offset)
- `tests/test_paths.py` (LOCALAPPDATA, миграция, fallback)
- `tests/test_logger.py`, `tests/test_resourses.py`, `tests/test_window_fade.py`

## Требует ручной проверки на Windows

- Трей: открытие окон, уведомления, штатный выход (без os._exit), отсутствие Tcl-ошибок (п.2, 3)
- Автоматический/ручной перерыв, Apply во время таймера, suspend/resume, idle/видео (п.11, 13, 14, 21)
- Звук: повторные переходы, прерывание, завершение без зависания (п.33)
- Длительный uptime — расчёт idle (п.23); тайминги шагов без накопления ошибки (п.24)
- Установленная сборка в каталог без прав записи (Program Files) — миграция настроек, логи (п.36)
- Анимации окон, dirty-форма настроек при смене шага во время редактирования (п.17, 31)
- Workflows на PR и тестовом релизном коммите (п.34)
