# Задача: исправить опечатку iddle → idle

## Постановка пользователя

> в проекте используется слово iddle - это ошибка, должно быть idle. Найди все места, предложи правки

> давай (подтверждение плана)

## Согласованный план

- `src/config/states.py`: `iddle_mode = 6` → `idle_mode = 6` (serena_rename_symbol, ссылки обновятся по всему проекту)
- `src/model.py`: тексты логов и уведомления `'iddle mode'` → `'idle mode'` (5 строк)
- `tests/test_model_fsm.py`: docstring + проверка `'iddle' in message` → `'idle' in message`
- `logs/log.log` не трогать (исторические записи)
- Проверки: rg (чисто), pytest, ruff check/format, flake8 WPS, ty
