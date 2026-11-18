# Установка и запуск

## Требования

- Python 3.11 (проверено; приложение целится в Windows 10; не-GUI тесты идут и на Linux).
- uv (рекомендуется для агента) или pip.

## Вариант uv (рекомендуется)

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements.txt pillow
```

> `pillow` нужен для импорта `src/support/resourses.py` и окон, но пока отсутствует в
> `requirements.txt` (см. [known-issues.md](../known-issues.md)) — для тестов он не требуется.
> После перевода проекта на uv: `uv sync` (зависимости из pyproject.toml + uv.lock).

## Вариант pip

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Запуск приложения (только Windows)

```bash
python ./src/main.py   # из корня проекта!
```

CWD = корень проекта: код читает `res/img/`, `res/sounds/`, `./settings/settings.json`,
пишет `./logs/log.log` по относительным путям.

Сборка .exe: `auto-py-to-exe`.
