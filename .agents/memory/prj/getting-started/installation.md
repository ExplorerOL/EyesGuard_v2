# Установка и запуск

## Требования

- Python 3.11 (файл `.python-version` — uv подберёт интерпретатор автоматически).
- uv.

## Установка (uv — единственный способ)

```bash
uv sync
```

Создаёт `.venv` из `pyproject.toml` + `uv.lock`. Windows-специфичные модули звука
(`support/sound/windows/`, MCI) импортируются фабрикой только на win32 — на других
платформах используется `NoopSoundPlayer`.

## Запуск приложения (только Windows)

```bash
python ./src/main.py   # из корня проекта!
```

CWD = корень проекта: код читает `res/img/`, `res/sounds/`, `./settings/settings.json`,
пишет `./logs/log.log` по относительным путям.

Сборка .exe: `auto-py-to-exe`.
