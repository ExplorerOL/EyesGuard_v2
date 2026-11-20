# Индекс директории .agents

Рабочая директория для AI-агентов: база знаний проекта и рабочие материалы задач.
Общий обзор проекта — [README.md](../README.md), правила для агентов — [AGENTS.md](../AGENTS.md).

## С чего начать

1. Архитектура проекта — [memory/prj/architecture/overview.md](memory/prj/architecture/overview.md)
2. Машина состояний приложения — [memory/app/state-machine.md](memory/app/state-machine.md)
3. Стиль кода проекта — [memory/prj/style.md](memory/prj/style.md)
4. Известные проблемы и ловушки — [memory/prj/known-issues.md](memory/prj/known-issues.md)
5. Быстрый контекст — поиск по графу знаний через `memory_search_nodes`

## Структура

```
.agents/
├── index.md                 — этот файл
├── knowledge-graph.jsonl    — производный граф знаний для MCP-сервера memory
├── memory/                  — база знаний (markdown-заметки, источник истины)
│   ├── app/                 — само приложение EyesGuard (домен, поведение)
│   └── prj/                 — проект разработки: архитектура, стиль, гайды
├── retro/                   — журнал ретроспектив и уроков
│   ├── lessons.md           — журнал уроков (записи RETRO-*)
│   └── index.md             — индекс прогонов и уроков для анализа трендов
├── skills/                  — скиллы opencode (см. skills/README.md)
└── tasks/                   — рабочие директории задач (см. tasks/README.md)
```

Шаблон финального SDD-ревью —
[skills/subagent-driven-development/final-reviewer-prompt.md](skills/subagent-driven-development/final-reviewer-prompt.md).

## knowledge-graph.jsonl

Граф знаний (сущности: MVC-слои, окна, модули, концепции + связи между ними).
Производный индекс от markdown-заметок в `memory/`; источник истины — заметки.
Используется MCP-сервером `memory` (переменная `MEMORY_FILE_PATH` в `opencode.json`).
Правится через инструменты `memory_*`, вручную — только в исключительных случаях.

## memory/ — база знаний

### Ключевые файлы

| Файл | Описание |
|------|----------|
| `memory/prj/architecture/overview.md` | Архитектура MVC, структура каталогов, потоки, платформенная специфика |
| `memory/app/state-machine.md` | Машина состояний StepType: шаги, переходы, iddle_mode, длительности |
| `memory/app/settings.md` | Настройки: модель, валидация, файл settings.json |
| `memory/prj/style.md` | Стиль кода проекта — обязательное чтение перед правками |
| `memory/prj/known-issues.md` | Известные проблемы, ловушки, технический долг |
| `memory/prj/known-wps-linter-problems.md` | Реестр нарушений WPS-линтера (подавлены в `.flake8`), план исправления |
| `memory/prj/getting-started/installation.md` | Установка и запуск |
| `memory/prj/getting-started/running-tests.md` | Прогон тестов |

### Директории

| Директория | Описание |
|------------|----------|
| `app/` | Домен приложения EyesGuard: поведение для пользователя, машина состояний, настройки |
| `prj/` | Проект разработки: архитектура, стиль кода, известные проблемы, гайды |

## retro/ — ретроспективы

Журнал уроков и индекс прогонов. Запись урока — при ретроспективе сессии;
индекс — сводка прогонов и таблица уроков со счётчиком промоушена (урок становится
правилом AGENTS.md/скилла после ≥3 повторов за 30 дней или ≥2 задач).

| Файл | Описание |
|------|----------|
| `retro/lessons.md` | Журнал уроков: записи `[RETRO-ГГГГММДД-XXX]` с категорией, решением, статусом, повторами |
| `retro/index.md` | Индекс: прогоны (дата, run, находки H/M/L) + уроки (промоушен «n/3») |

## tasks/ — рабочие директории задач

Конвенция файлов и список задач — [tasks/README.md](tasks/README.md).
Одна директория на задачу: `task.md`, `ai-ready-task.md`, `status.md`, `decisions.md`, `adr/NNNN-name.md` и т.д.

## Поддержка индекса

При добавлении новой директории или файла в `.agents` дополняйте этот файл.
