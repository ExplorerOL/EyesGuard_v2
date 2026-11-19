# tasks/

Рабочие директории задач. Одна директория на задачу, имя — kebab-case по сути задачи.

## Конвенция файлов внутри задачи

| Файл | Описание |
|------|----------|
| `task.md` | Постановка задачи (промпт пользователя) |
| `research.md` | Проверенные факты, пути, символы, ограничения и открытые вопросы |
| `ai-ready-task.md` | Задача, подготовленная для передачи агенту-имплементеру |
| `status.md` | Текущий статус, фактические проверки, отложенные замечания и ручные проверки |
| `decisions.md` / `design_decisions.md` | Принятые решения |
| `acceptance-criteria.md` | Критерии приёмки, если они вынесены из AI-ready задачи |
| `test-cases.md` | Согласованный отдельный тест-дизайн, если он нужен |
| `scripts/verify.py` | Опциональные машинно-проверяемые инварианты задачи |
| `adr/NNNN-name.md` | Архитектурные решения (ADR, сквозная нумерация) |
| `plan_*.md`, `final_plan.md` | Планы реализации |
| `prompt.md` | Финальный промпт для запуска реализации |

`CONTEXT.md` не используется как общий файл контекста задачи: этот формат
зарезервирован скиллом `domain-modeling` для глоссария предметной области.

## Задачи

| Задача | Суть | Статус |
|--------|------|--------|
| [pyinstaller-packaging](pyinstaller-packaging/) | Сборка exe через PyInstaller: spec, резолв путей (frozen/dev), README | Реализована (рабочий exe — ручная проверка на Windows) |
| [activity-timeout-setting](activity-timeout-setting/) | Пользовательская настройка activity_timeout (30–600 сек): UI, сохранение, применение без перезапуска | Реализована (ручная проверка UI на Windows) |
| [release-automation](release-automation/) | Авто-релиз при пуше в master при смене версии: PyInstaller exe+zip, тег EyesGuard-vX.Y.Z, notes из CHANGELOG, единый APP_VERSION | Реализована (требует проверки workflow в GitHub Actions) |
| [sounds-volume-setting](sounds-volume-setting/) | Настройка громкости, вкладка Sounds и переход со playsound на Windows MCI | Подготовлена AI-ready задача |
