# AI-ready task

## Problem

Ускорить видимое появление окон приложения (фейд прозрачности), которое с 2.3.1
стало медленным: 100 шагов `after()` растягиваются таймером Windows и конкуренцией
с перерисовками; окно настроек дополнительно ждёт до 200 мс poll-очереди трея и
грузит UI-поток обновлениями на каждый снапшот, даже будучи скрытым.

## Expected outcome

1. `src/windows/window_fade.py`: `FADE_STEPS = 40` (номинально 240 мс).
2. `src/view.py::__apply_snapshot`: `WndBreak.update()` вызывается всегда
   (это механизм auto-show/hide окна перерыва); `WndStatus` и `WndSettings`
   обновляются только при `state() == 'normal'`; свежий снапшот сохраняется
   в `self.__latest_snapshot`.
3. `src/view.py`: показ из трея идёт через обёртки-методы
   (`__show_status_wnd_action` / `__show_settings_wnd_action`), которые
   вызывают `show()` и затем применяют `__latest_snapshot` (guard `is not None`),
   в одном тике poll — без дополнительных задержек.
4. `src/windows/wnd_settings.py::update_protection_status_image`: приватный кэш
   `self.__protection_decor`; при неизменном (image, text, color) — ранний выход,
   configure не выполняется (паттерн кэша `__btn_state` из `WndStatus`,
   known issue 32).

Тесты `tests/test_window_fade.py` адаптируются к новой константе автоматически
(импортируют `FADE_STEPS`), правок не требуют.

## Known facts

- `show()` всех трёх окон идентичен: `deiconify()` + `fade_window(showing=True)`.
- `View.__apply_snapshot` (view.py:89-94) обновляет все окна на каждый снапшот
  независимо от видимости; Model тикает ~1 раз в секунду.
- `QUEUES_POLL_INTERVAL_MS = 200` (view.py:20) — действия трея ждут до 200 мс.
- Внешних вызовов `View.show_wnd_break`/`hide_wnd_break` нет (проверено grep):
  показ/скрытие окна перерыва живёт только в `WndBreak.update()` (wnd_break.py:95-99).
- `deiconify()` синхронно переводит Tk-состояние в `normal`, поэтому
  `__apply_snapshot` сразу после `show()` проходит guard.
- CTkImage-объекты переиспользуются, сравнение кортежа по идентичности корректно.

## Constraints

- Правила AGENTS.md: приватные поля `self.__name`, логирование loguru
  (`logger.trace('Class: method_name')` первой строкой новых методов),
  комментарии/код на английском, MVC-границы не нарушать.
- Не переписывать unrelated-код (legacy), не добавлять зависимости, не пушить.
- Линтеры: ruff с `--config=./linter_ruff.toml`, WPS через
  `flake8 --config=.flake8 --select=WPS`, ty с `--config-file linter_ty.toml`.

## Non-goals

- Не менять `FADE_STEP_MS`, механику `fade_window`/`cancel_fade` и логику
  showing/on_done.
- Не выносить guard видимости внутрь окон и не менять `WndBreak.update()`.
- Не кэшировать значения `__update_fields` (11 set()) — только декор статуса.
- Не трогать tray-уведомления, звук, монитор активности.

## Source of truth

- Диагноз и факты: `.agents/tasks/faster-window-fade/research.md`
- Паттерн кэша: `src/windows/wnd_status.py:158-160` (`__btn_state`, known issue 32)
- Реестр issues: `.agents/memory/prj/known-issues.md`

## Required checks

- `uv run pytest -v` — все зелёные (123+ тестов).
- `uv run ruff check --fix --config=./linter_ruff.toml` + `ruff format` по
  `src/windows/window_fade.py src/view.py src/windows/wnd_settings.py`.
- `uv run --no-sync flake8 --config=.flake8 --select=WPS <те же файлы>` — чисто.
- `uv run --no-sync ty check --config-file linter_ty.toml <те же файлы>` — чисто.
- Ручная проверка на Windows (не автоматизируется): скорость появления
  settings/status/break; auto-появление break-окна при начале перерыва;
  свежесть полей при открытии настроек; отмена фейда при быстром hide/show.

## Stop conditions

- Все обязательные проверки зелёные, независимое ревью без Critical/Important.
- Остаточные Minor — в `status.md`, не блокируют сдачу.
