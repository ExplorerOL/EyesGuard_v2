# Changelog

## Unreleased
- Добавлен скилл add-user-setting (сквозное добавление пользовательской настройки: модель → pydantic → виджет → логика → тест) и реестр скиллов в .agents/skills/README.md
- CI: GitHub Actions workflow (ruff + pytest на push/PR); .python-version (3.11), .editorconfig, [tool.pytest.ini_options] в pyproject
- Линт-база очищена: `ruff check .` проходит без ошибок (сортировка импортов, неиспользуемые импорты, f-string, noqa на осознанных safe-default исключениях)
- Добавлена инфраструктура для ИИ-агентов: AGENTS.md, .agents/ (база знаний, граф знаний, ретро, задачи)
- Проект переведён на uv: pyproject.toml ([project] + dev-группа pytest/ruff), uv.lock; pillow добавлен в зависимости; playsound ограничен маркером win32

## v2.0.0 - 2024-04-02
- First release of EyesGuard for Windows written in Python
