# Статус: faster-window-fade

## Этапы

| Этап | Статус |
|---|---|
| Диагноз (исследование) | Готово (research.md) |
| Решения (подтверждены пользователем) | Готово (research.md, ai-ready-task.md) |
| Реализация | Готово |
| Независимое ревью | Готово — APPROVE, без Critical/Important |
| Документация | Готово |

## Изменённые файлы

- `src/windows/window_fade.py` — `FADE_STEPS` 100 → 40 (пользователь подтвердил 40; ручная правка 30 в рабочем дереве перезаписана по подтверждению)
- `src/view.py` — кэш `__latest_snapshot`; guard скрытых окон в `__apply_snapshot` (WndBreak — всегда, его `update()` — единственный механизм auto-show/hide); обёртки `__show_status_wnd_action` / `__show_settings_wnd_action` / `__apply_latest_snapshot` (show + свежий снапшот в одном тике poll)
- `src/windows/wnd_settings.py` — кэш `__protection_decor` в `update_protection_status_image`, ранний выход при неизменном декоре (паттерн issue 32)

## Выполненные проверки (2026-11-20)

| Проверка | Команда | Результат |
|---|---|---|
| pytest | `uv run --no-sync pytest -v` | 123 passed |
| ruff | `ruff check --fix --config=./linter_ruff.toml` + `ruff format` (3 файла) | чисто |
| WPS | `uv run --no-sync flake8 --config=.flake8 --select=WPS <3 файла>` | чисто |
| ty | `uv run --no-sync ty check --config-file linter_ty.toml <3 файла>` | чисто |

## Отложенные Minor (из ревью, не блокируют)

1. `src/view.py` `__apply_latest_snapshot` применяет снапшот через полный `__apply_snapshot`: повторно исполняются `WndBreak.update()` и `__update_tray_icon_values` (идемпотентно, ~мс; соответствует спецификации).
2. `src/windows/wnd_settings.py:38` аннотация `tuple | None` без параметризации (можно `tuple[CTkImage, str, str]`); стиль соответствует остальной кодовой базе.

## Ручные проверки на Windows (за пользователем)

- Скорость появления WndSettings / WndStatus / WndBreak после изменений.
- Auto-появление/скрытие окна перерыва при смене шага (guard не должен был его затронуть).
- Свежесть полей при открытии настроек и статуса из трея.
- Отмена фейда при быстром hide/show.
- Декор защиты в настройках меняется при переключении protection_status.
