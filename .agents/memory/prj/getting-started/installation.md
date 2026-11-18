# Установка и запуск

## Требования

- Python 3.11 (файл `.python-version` — uv подберёт интерпретатор автоматически).
- uv.

## Установка (uv — единственный способ)

```bash
uv sync
```

Создаёт `.venv` из `pyproject.toml` + `uv.lock`. Зависимость звука `playsound`
помечена маркером `sys_platform == 'win32'` — на других платформах пропускается автоматически
(её setup.py не собирается вне Windows).

## Запуск приложения (только Windows)

```bash
python ./src/main.py   # из корня проекта!
```

CWD = корень проекта: код читает `res/img/`, `res/sounds/`, `./settings/settings.json`,
пишет `./logs/log.log` по относительным путям.

Сборка .exe: `auto-py-to-exe`.
