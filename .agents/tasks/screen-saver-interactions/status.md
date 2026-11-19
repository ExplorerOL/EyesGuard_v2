# Статус: screen-saver-interactions

## Этапы

| Этап | Статус | Примечание |
|---|---|---|
| Исследование | Готово | research.md |
| Решения пользователя | Готово | decisions.md (9 решений, 2026-11-19) |
| AI-ready задача | Готово | ai-ready-task.md |
| Реализация | Готово | см. список файлов ниже |
| Ревью | Готово | reviewer: REQUEST_CHANGES (1 Critical, 1 Important, 4 Minor) → все Critical/Important и 3 Minor исправлены, scoped re-review — чисто |
| Документация/закрытие | Готово | CHANGELOG, memory, граф знаний, tasks/README |

## Изменённые файлы

| Файл | Изменение |
|---|---|
| `src/config/settings.py` | + `screensaver_block`("on"), `suspend_on_video`("on"), `reset_work_time_in_idle`("off") в dataclass и pydantic-валидатор |
| `src/support/display/` (новый) | `screensaver_blocker.py` + `video_activity_monitor.py` (фасады/фабрики) и `windows/`-реализации (SetThreadExecutionState; CallNtPowerInformation + debounce 5 тиков) |
| `src/model.py` | `__process_screensaver_block` (вызов в каждом тике wait-цикла — поток контроллера); видео-условия входа/выхода iddle (опрос только в work-цепочке/iddle); `reset_debounce()` при смене шага; сброс elapsed при входе в iddle (reset_work_time_in_idle) |
| `src/support/resourses.py` | `img_monitor` c fallback `img_gear` + warning |
| `src/windows/wnd_settings.py` | вкладка Display (кнопка + фрейм + 2 чекбокса), чекбокс на Time settings, select/update/обработчики |
| `src/view.py` | чтение 3 значений из UI |
| `tests/test_settings.py` | обновлены эталоны (строки/JSON), +2 теста |
| `tests/data/` | + `settings_valid_display_fields.json`, `settings_invalid_new_field_value.json` |
| `EyesGuard-onefile.spec`, `EyesGuard-onedir.spec` | + `support.display.windows.*` в hiddenimports (после ревью) |

## Ревью и исправления

Вердикт reviewer: REQUEST_CHANGES. Исправлено:

| Severity | Замечание | Исправление |
|---|---|---|
| Critical | `block()/release()` могли вызваться из Tk-потока (do_current_step_actions ← set_step ← WndStatus/WndBreak/трей), а `SetThreadExecutionState` привязан к потоку → неснявшаяся блокировка | `__process_screensaver_block` перенесён в тик `wait_for_current_step_is_ended` (всегда поток контроллера); вызов из `do_current_step_actions` убран |
| Important | Видео опрашивалось и в break_mode: собственный ES_DISPLAY_REQUIRED блокера + инерция debounce → ложный вход в iddle сразу после перерыва | Опрос только при шагах {work, n1, n2, iddle}; добавлен `reset_debounce()` (Protocol/noop/Windows), вызывается в `__set_current_step` при каждой смене шага |
| Minor | break+off → release() не вызывался (расхождение со спекой) | `should_block = break and on; if should_block: block() else: release()` |
| Minor | `support.display.windows.*` нет в hiddenimports spec-файлов | Добавлены в оба spec-файла (симметрично sound) |
| Minor | Недостающие `logger.trace` в `__get_display_required_from_os` | Добавлены |
| Minor | CHANGELOG: 2 строки Added вместо 3 (две Display-настройки объединены) | Осознанно оставлено: обе настройки — одна фича «вкладка Display»; правилу «≤1 строка на фичу» соответствует |

Фикс разметки (по обращению пользователя): на вкладке Time settings чекбокс с длинным текстом
расширил колонку 0 — записи (sticky='e', ширина CTkEntry по умолчанию) обрезались. Исправлено:
лейблы/чекбокс sticky='w', записи sticky='w' с фиксированной width=70, pady=10; weight=1 у
колонки 1 убран (обе настройки, включая copy-paste баг в блоке General, настраивавший
time-фрейм). Требует визуальной проверки на Windows.

Фикс разметки, шаг 2 (записи всё ещё выезжали за окно): чекбокс получил columnspan=2 — больше
не расширяет колонку лейблов; зазор между лейблом и записью уменьшен 30px → 10px
(лейблы padx=(20, 5), записи padx=(5, 15)). Требует визуальной проверки на Windows.

Доработки v2.3.0 (по обращению пользователя): порядок вкладок General → Time settings →
Display → Sounds → About; чекбокс переименован в 'Switch to idle mode on video playback'
(внутреннее имя поля `suspend_on_video` не менялось — совместимость settings.json);
версия 2.2.0 → 2.3.0 (app_constants.py + pyproject.toml + uv.lock, CHANGELOG [2.3.0]).

## Фактические проверки (2026-11-19, Linux)

| Команда | Результат |
|---|---|
| `uv run pytest -v` | 25 passed (до и после ревью-фиксов) |
| `uv run ruff check --fix --config=./linter_ruff.toml <затронутые файлы>` | All checks passed (1 рефакторинг в ходе реализации: `__process_screensaver_block` выделен из-за C901 12>10) |
| `uv run ruff format --config=./linter_ruff.toml <затронутые файлы>` | ок |
| Smoke debounce/reset (Linux, Windows-класс с фейком OS-опроса) | флаг→True; 3 тика удержания; False на 4-м; `reset_debounce()` убирает инерцию; повторный флаг→True |

## Отложенные замечания (Minor/Info от re-review, осознанные трейд-оффы)

- Задержка выхода из iddle до ~5 с (debounce_ticks × TIME_TICK_S) после реального конца видео
  при активном пользователе — expected behavior debounce.
- `reset_debounce()` может вызваться из Tk-потока (через `set_step`) — запись int под GIL,
  состояние единственное, гонка безвредна.

## Ручные проверки (Windows) — НЕ выполнено, среда агента Linux

1. Скринсейвер (таймаут 1 мин): не запускается во время перерыва при `screensaver_block=on`;
   при `off` — запускается; после перерыва блокировка снимается.
2. Видео в браузере (fullscreen и окно) + `suspend_on_video=on`: уведомление «iddle mode»,
   отсчёт замирает; видео закончилось + активность — продолжается (~5 с debounce).
3. Вкладка Display: два чекбокса, Apply → значения в settings/settings.json.
4. `reset_work_time_in_idle=on`: бездействие > activity_timeout → iddle; возврат — отсчёт с нуля.
5. Отсутствие `res/img/monitor.png`: запуск без падения, в логе warning, вкладка Display с gear-иконкой.
6. Сценарии из ревью (потоковость блокера): «Take a break» из окна статуса; досрочное закрытие
   окна перерыва крестиком; поведение сразу после окончания перерыва (нет ложного iddle).
