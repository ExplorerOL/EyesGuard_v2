# Статус: fix-idle-typo

## Результат: реализована, проверки зелёные

## Изменения

| Файл | Что изменено |
|---|---|
| `src/config/states.py` | `iddle_mode = 6` → `idle_mode = 6` (serena_rename_symbol + текстовые правки) |
| `src/model.py` | 13 символьных ссылок `StepType.iddle_mode` → `StepType.idle_mode` (включая `__exit_idle_mode`), 5 текстов логов/уведомления `iddle mode` → `idle mode` |
| `tests/test_model_fsm.py` | 6 `StepType.idle_mode`, docstring, проверка `'idle' in message` |
| `.agents/memory/app/state-machine.md` | 15 вхождений (таблица шагов, ASCII-диаграмма, описания) |
| `.agents/memory/app/settings.md` | 2 вхождения |
| `.agents/index.md` | 1 вхождение (описание state-machine.md) |
| `.agents/knowledge-graph.jsonl` | 15 вхождений в наблюдениях сущностей Model, StepType, Settings (текстовая замена; валидация чтения сервером memory — `memory_open_nodes` OK) |
| `CHANGELOG.md` | `[Unreleased]` → Fixed: запись о переименовании |

## Решения

- `logs/log.log` — не трогать (исторические записи).
- `.agents/tasks/screen-saver-interactions/*`, `.agents/memory/prj/known-issues.md` — не трогать: архив закрытой задачи и зачёркнутые исторические записи решённых проблем, описывают прошлое состояние кода.
- `StepType` — IntEnum, сериализуется по значению (6), в settings.json не сохраняется → переименование члена обратно совместимо.
- Граф знаний правлен текстовой заменой (исключительный случай): массовая правка текста наблюдений без изменения структуры; API memory не имеет операции редактирования наблюдения. Валидировано чтением через `memory_open_nodes`.

## Проверки (фактические)

| Команда | Результат |
|---|---|
| `uv run ruff check --fix --config=./linter_ruff.toml src/model.py src/config/states.py tests/test_model_fsm.py` | All checks passed |
| `uv run ruff format --config=./linter_ruff.toml <те же файлы>` | 3 files left unchanged |
| `uv run pytest -v` | 123 passed |
| `uv run --no-sync flake8 --config=.flake8 --select=WPS <те же файлы>` | exit 0 |
| `uv run --no-sync ty check --config-file linter_ty.toml <те же файлы>` | All checks passed |
| `rg -i --hidden --no-ignore "iddle"` (с исключениями архивов) | только намеренная цитата в CHANGELOG.md |

## Остаток

- Ручная проверка на Windows не требуется: пользовательски видимое изменение — только текст уведомления («switched to idle mode!»), логика не менялась.
