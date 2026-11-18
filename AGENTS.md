## О проекте

EyesGuard_v2 — десктоп-приложение для Windows, напоминающее о перерывах при работе за ПК.
Python 3.11, GUI на CustomTkinter, трей на pystray, настройки на pydantic, логи на loguru,
звуковые уведомления на playsound, монитор неактивности через Windows API, лицензия GPL v3.

- Краткие сведения о проекте — @README.md
- Домен приложения (машина состояний, настройки) — @.agents/memory/app/index.md
- Архитектура и стиль кода — @.agents/memory/prj/index.md
- Структура и описание файлов рабочей директории агента: @.agents/index.md

Архитектура — классический MVC + инфраструктура: `src/main.py` связывает `Controller`
(оркестрация в отдельном потоке), `Model` (тайминги, машина состояний `StepType` с idle-режимом),
`View` (окна CustomTkinter + pystray); `src/config/` (настройки, состояния), `src/support/`
(logger, ресурсы, звук, монитор активности). Запуск только из корня проекта (относительные
пути `res/`, `settings/`, `logs/`).

## Граф знаний проекта (только для этого репозитория)

- `opencode.json` в корне проекта переопределяет MCP-сервер `memory`: его хранилище — файл
  `.agents/knowledge-graph.jsonl` (переменная `MEMORY_FILE_PATH`). Глобальный `~/.config/opencode/memory.jsonl` здесь не используется.
- Граф содержит сущности (MVC-слои, окна, модули, концепции), связи между ними и наблюдения.
  Источник истины — markdown-заметки в `.agents/memory/`; граф — производный индекс для быстрого контекста.
- Работай с графом через инструменты `memory_*`: `memory_read_graph` / `memory_search_nodes` для чтения,
  `memory_create_entities` / `memory_create_relations` / `memory_add_observations` для записи.
  Файл правится вручную только в исключительных случаях (формат JSONL сервера memory).
- При существенных изменениях архитектуры, машины состояний, настроек или тестов дополняй/обновляй
  соответствующие сущности графа и md-заметки в `.agents/memory/`, а также @.agents/index.md.

## Основной промпт

При работе с кодом действуй как опытный разработчик десктоп-приложений на Python (Tkinter-семейство),
соблюдай принципы SOLID, DRY, KISS и стиль существующего кода проекта (см. @.agents/memory/prj/style.md).
При необходимости выдачи информации пользователю максимально используй таблицы и ASCII-диаграммы
для быстрого понимания контекста пользователем.
Общайся с пользователем и пиши документацию (`README.md`, `.agents/`, `CHANGELOG.md`) на русском языке;
код, комментарии, docstrings и тексты логов — на английском.
@CHANGELOG.md пиши кратко — 1-2 строки на пункт.
Никогда не делай пуш в удаленный репозиторий! Попроси об этом пользователя.
Новые зависимости добавляй только после явного согласования с пользователем.

**Правила кода проекта (обязательные):**
- Логирование через loguru по конвенции проекта: `logger.trace("Class: method_name")` первой строкой
  нового метода; формат сообщений `"<Класс>: <что происходит>"`; обработанные ошибки —
  `logger.error(...)`, затем безопасный дефолт (приложение не должно падать).
- Приватные поля — `self.__name`; вызовы с осмысленными именованными аргументами.
- Состояния — только через `StepType` + `match/case`; данные шага — dataclass.
- Настройки: новое поле = `UserSettingsData` + `SettingsDataValidator` (pydantic, границы) + виджет
  `WndSettings` + тест. Валидация обязательна: приложение переживает битый settings.json на дефолтах.
- MVC-границы: логика — в `Model`, UI — в `View`/`windows/`, оркестрация — в `Controller`,
  конфигурация/состояния — `src/config/`, инфраструктура — `src/support/`.
- Циклические импорты типов разрывать через `from __future__ import annotations` + `TYPE_CHECKING`.
- Windows-only код (`user_activity_monitor`, звук) не импортировать в модули, тестируемые на Linux.
- Legacy-код под новые правила массово не переписывается — только файлы/функции, затронутые задачей
  (известный техдолг зафиксирован в @.agents/memory/prj/known-issues.md).

**Линт и формат (обязательные команды):**
- lint: `uv run ruff check --fix <затронутые файлы>`
- format: `uv run ruff format <затронутые файлы>`
- Конфиг берётся из `pyproject.toml` (`[tool.ruff]`) — отдельный файл конфига не используется.
- Запуск на всём проекте запрещён: на legacy ~100+ находок — массовый автофикс недопустим, только затронутые файлы.

**Тесты (обязательная команда):**
- `uv run pytest -v` (эквивалент `python -X utf8 -m pytest ./tests/`, из корня проекта).
- Тесты не должны требовать GUI и Windows: покрыты `config/settings.py`, `config/states.py`,
  тайминги `Model` (View/монитор/звук мокаются).

**Платформы:**
- Код целился под Windows 10: GUI, трей, уведомления, звук и монитор активности проверяются
  вручную только на Windows (`ctypes.windll` и `playsound` на Linux не работают).
- Агент в Linux запускает pytest для не-GUI частей; GUI-фичи помечай как «требует ручной проверки на Windows».

## Работа с кодом: codegraph, serena, ast-grep

При любой работе с кодом (поиск, чтение, анализ, правки) всегда используй MCP-инструменты codegraph,
serena, ast-grep вместо циклов grep/find/Read. Этот промпт должен получать каждый из субагентов.

### CodeGraph — навигация и контекст (первый шаг)

- `codegraph_explore` — один вызов возвращает исходники релевантных символов с номерами строк + пути
  вызовов между ними (включая dynamic dispatch). Запрос — имена символов/файлов или вопрос на
  естественном языке; параметр `projectPath` — путь к проекту с индексом `.codegraph/`.
- Репозиторий проиндексирован (`codegraph init`, индекс в `.codegraph/`, в git не коммитится — см. `.gitignore`).
  Индекс подхватывается live; shell-альтернатива: `codegraph explore "<query>"`.

### Serena — символьная навигация и правки

- Перед задачей: `serena_initial_instructions` (обязательно), при необходимости `serena_activate_project`.
- Обзор и поиск: `serena_get_symbols_overview` (вход в новый файл), `serena_find_symbol`,
  `serena_find_declaration`, `serena_find_referencing_symbols`, `serena_find_implementations`,
  `serena_search_for_pattern` (regex по проекту).
- Правки: `serena_replace_symbol_body`, `serena_insert_before_symbol` / `serena_insert_after_symbol`,
  `serena_replace_in_files` (массовые замены; сначала `dry_run=true`, затем применить по `occurrence_ids`),
  `serena_rename_symbol`, `serena_safe_delete_symbol` (удаляет символ только при отсутствии ссылок).
- Диагностика: `serena_get_diagnostics_for_file` — после правок.

### ast-grep

- `ast-grep` (алиас `sg`) — приоритет после codegraph и serena, до текстового grep: структурный
  поиск/правки по AST-паттернам (`ast-grep -p 'foo($$$)'`). Если не установлен в окружении — обычный grep.

### Приоритет

1. `codegraph_explore` — быстро понять код, найти символы и связи между ними.
2. Serena — символьная навигация и семантические правки (точечнее текстовых edit).
3. ast-grep.
4. Встроенные Grep/Read/Edit — только fallback (codegraph недоступен, serena не активна).

## Поддержка документации агента

- Существенное изменение кода → обнови заметки `.agents/memory/` и граф знаний (`memory_*`).
- Урок из ретроспективы → `.agents/retro/lessons.md` + счётчик в `.agents/retro/index.md`
  (промоушен в правила AGENTS.md после ≥3 повторов за 30 дней или ≥2 задач).
- Новая задача → директория в `.agents/tasks/` по конвенции из @.agents/tasks/README.md.
- Новые файлы/директории в `.agents` → дополни @.agents/index.md.
