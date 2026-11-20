# Известные ошибки тайп-чекера ty (требуемые исправления)

Реестр подавленных диагностик тайп-чекера ty. Все существующие на момент внедрения ошибки
зафиксированы здесь и заглушены в `linter_ty.toml` (per-file overrides); исправление планируется
в будущих релизах. Каждое исправление = удаление соответствующей секции `[[overrides]]`.

- **Дата базовой линии:** 2026-11-20
- **Версия:** ty 0.0.107 (beta, dev-зависимость pyproject)
- **Базовая линия:** **37 диагностик** на Linux; **24** после `python-platform = "win32"` (13 ×
  `missing-attribute` `ctypes.windll` исчезли корректно — это целевая платформа приложения,
  не заглушка)
- **Текущее состояние:** `uv run --no-sync ty check --config-file linter_ty.toml src tests` → **All checks passed**
- **Запуск:** `uv run --no-sync ty check --config-file linter_ty.toml src tests` (из корня проекта;
  нестандартное имя конфига — флаг `--config-file` обязателен, автообнаружение не сработает)
- **Где включено:** pre-commit/pre-push хуки (prek, local hook) + шаг в CI `.github/workflows/tests.yml`

## Как устроено подавление (`linter_ty.toml`)

| Приём | Что это | На что |
|---|---|---|
| `[environment] python-platform = "win32"` | Не заглушка: анализ под целевую платформу приложения (Windows 10) — typeshed-стабы `ctypes.windll` и т.п. разрешаются штатно | `missing-attribute` windll ×14 |
| `[[overrides]]` per-file + `[overrides.rules]` | Аналог per-file-ignores: правило выключено только в указанных файлах | 24 диагностики ниже |
| `# ty: ignore[rule]` (инлайн) | Точечное подавление строки; не использовалось в базовой линии | — |

**Процесс устранения:** исправляете код → удаляете секцию `[[overrides]]` из `linter_ty.toml` →
`ty check` остаётся зелёным → вычёркиваете строку из таблицы. ty 0.0.x — beta: диагноcтики
могут менять имена между релизами; при обновлении версии сверять реестр с прогоном.

## Требуемые исправления

### Высокий приоритет (реальные дефекты контракта)

| # | Диагностика | Где | Суть и требуемое исправление |
|---|---|---|---|
| 1 | `incompatible-method-override` ×3 | `wnd_break.py:83`, `wnd_settings.py:447`, `wnd_status.py:127` | `update(model)` перекрывает `Tk.Misc.update()`. Опасная коллизия: вызов `window.update()` без аргументов (например, чужим кодом или по привычке) запустит Tk event loop внутри метода. **Переименовать в `update_from_model(model)`/`refresh()`** и обновить все вызовы |
| 2 | `invalid-argument-type` ×2 | `settings.py:159,161` | `Settings` допускает `file_name=None` (in-memory), но `apply_settings_from_ui`/`save_settings_to_file` передают `str | None` в методы, ожидающие `str`, и падают `AttributeError` на `__settings_file`. **Сделать путь обязательным или явно разделить файловый и in-memory режимы** (устраняет остаток бывшего known-issue #26) |
| 3 | `missing-union-attribute` ×6 | `test_controller.py:81,108,144,174,212,213` | `Controller.thread: Thread \| None` — тесты вызывают `join()`/`is_alive()` без narrowing. **В тестах добавить `assert controller.thread is not None`; в прод-коде рассмотреть гарантии после `start()`** |

### Средний приоритет (типизация UI и тестовых дублёров)

| # | Диагностика | Где | Суть и требуемое исправление |
|---|---|---|---|
| 4 | `invalid-argument-type` ×3 | `wnd_settings.py:194,213,232` | `StringVar.set(int)` — тайквар ожидает `str`. **Обернуть в `str(...)`** |
| 5 | `invalid-argument-type` ×1 | `wnd_settings.py:51` | `wm_iconphoto(PhotoImage)` — тип не совпадает со стабом `_PhotoImageLike`. **Проверить используемый класс изображения; при необходимости привести к `tk.PhotoImage`** |
| 6 | `invalid-argument-type` ×1 | `conftest.py:123` | `FakeView` в `Model.set_view(View)`. **Ввести `typing.Protocol` (ViewLike/ModelLike) и аннотировать параметры протоколами** |
| 7 | `invalid-argument-type` ×6 | `test_controller.py:73,90,124,167,190,205` | `FakeModel`/`NeverEndingModel` в `Controller.set_model(Model)`. **То же: Protocol-интерфейсы вместо конкретных классов** |

### Низкий приоритет (точечные)

| # | Диагностика | Где | Суть и требуемое исправление |
|---|---|---|---|
| 8 | `missing-argument` ×1 | `test_settings.py:366` | `Settings()` без обязательного `file_name`. **Передать путь (tmp_path)** |
| 9 | `not-subscriptable` ×1 | `test_window_fade.py:68` | Индексация Optional-результата без guard. **Добавить `assert ... is not None` или guard** |

## Связанные документы

- Конфиг подавления: `linter_ty.toml` (секции с комментариями)
- Аналогичный реестр для WPS: [known-wps-linter-problems.md](known-wps-linter-problems.md)
- Стиль кода: [style.md](style.md)
