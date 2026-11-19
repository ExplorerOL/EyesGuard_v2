# Машина состояний приложения

Источник кода: `src/config/states.py` (`StepType`, `StepData`, `CurrentState`, `ModelSnapshot`), переходы — `src/model.py` (`set_new_step_in_sequence`, `do_current_step_actions`, `tick`, `__build_steps`/`__init_steps`).

Тайминги — deadline-based от инжектируемых monotonic-часов (`Model(clock=...)`, `__step_started_at`):
elapsed вычисляется от часов в `tick()`, pacing-sleep принадлежит Controller. Эффекты шага
запускаются ровно один раз на фактический переход — внутри `set_step`.

## Шаги StepType (IntEnum)

| Значение | Имя | Смысл | Длительность |
|---|---|---|---|
| 0 | `off_mode` | Защита выключена | STEP_SUSPENDED_MODE_DURATION (60 м), но время не тикает — шаг «висит» |
| 1 | `suspended_mode` | Защита приостановлена | 60 м (system) |
| 2 | `work_mode` | Работа, счёт до перерыва | work_duration − n1 − n2 (если > 0, иначе 0) |
| 3 | `work_notified_1` | Предупреждение «до перерыва 1 минута» | 55 с (system) |
| 4 | `work_notified_2` | Предупреждение «до перерыва 5 секунд» | 5 с (system) |
| 5 | `break_mode` | Перерыв | break_duration (user, 15 м по умолчанию) |
| 6 | `iddle_mode` | Пользователь неактивен (> activity_timeout) ИЛИ играет видео (suspend_on_video=on) | = длительность work-шага; время не тикает |

## Граф переходов

```
                    ┌────────────────────────────────────────┐
                    ▼                                        │
 work_mode ──► work_notified_1 ──► work_notified_2 ──► break_mode
   │   ▲                                                   │
   │   │ пользователь                                      │
   │   │ снова активен                                     │
   ▼   │                                                   │
  iddle_mode                                                │
    ▲   └─────────── пользователь снова активен ────────────┘
    │ неактивен > activity_timeout ИЛИ видео (suspend_on_video=on)
    │ (в любом work-шаге цепочки)
   │
 work_mode (продолжение счёта)

 suspended_mode ──► work_mode        (возврат по таймеру шага)
 off_mode: перехода нет — остаётся в off_mode
```

Переходы в/из `iddle_mode` выполняются **внутри** `wait_for_current_step_is_ended`
(проверка активности каждый тик в `Model.tick()`), а не в `set_new_step_in_sequence`:

- неактивен ИЛИ играет видео (при `suspend_on_video = "on"`, см. ниже) и текущий шаг
  ∈ {work_mode, work_notified_1, work_notified_2} → `set_step(StepType.iddle_mode)`;
- активен И видео НЕ играет и текущий шаг = iddle_mode → `__exit_idle_mode()`:
  при `reset_work_time_in_idle=off` восстанавливается сохранённый перед idle рабочий шаг
  (`__idle_saved_step`: тип + remaining), при `on` — свежий `work_mode`;
- `set_new_step_in_sequence` содержит exhaustive-переходы для всех шагов (для `iddle_mode` —
  возврат в `work_mode`); повторный переход в тот же шаг игнорируется (эффекты не дублируются).

### Видео-idle (suspend_on_video)

Видео определяется по системному флагу занятости экрана: `CallNtPowerInformation(SystemExecutionState)`
→ `ES_DISPLAY_REQUIRED` — его поднимают браузеры/плееры при проигрывании
(`src/support/display/windows/video_activity_monitor.py`, на Linux — noop-фабрика).
Debounce ~5 тиков подряд без флага перед снятием (флаг мигает у плееров с периодическим
сбросом idle-таймера); при каждой смене шага debounce-память сбрасывается
(`reset_debounce()` в `__set_current_step`) — иначе инерция «видео ещё играет» давала бы
ложный вход в iddle сразу после перерыва. Опрос видео выполняется только при шагах
{work_mode, work_notified_1, work_notified_2, iddle_mode}. Вход/выход — штатные действия
iddle (уведомление + звук). В `break_mode` видео не детектируется (окно перерыва само
fullscreen, плюс собственный скринсейвер-блок поднимает ES_DISPLAY_REQUIRED).

### Скринсейвер на перерыве (screensaver_block)

`Model.__process_screensaver_block` — вызывается **в каждом тике** `wait_for_current_step_is_ended`
(этот цикл всегда крутится в потоке контроллера; `SetThreadExecutionState` привязан к потоку —
из `do_current_step_actions` вызывать нельзя, т.к. тот метод вызывается и из Tk-потока через
`set_step`): `break_mode` + `screensaver_block="on"` → `SetThreadExecutionState(ES_CONTINUOUS |
ES_DISPLAY_REQUIRED)`; любой другой шаг (или настройка off) → снятие (`ES_CONTINUOUS`).
Оба вызова идемпотентны.

### Сброс рабочего времени в idle (reset_work_time_in_idle)

При входе в iddle_mode и `reset_work_time_in_idle = "on"` → `reset_elapsed_time()`:
после возврата в work_mode отсчёт начинается с нуля. `"off"` (дефолт) — существующее
поведение «заморозки» (счёт продолжается с того же места).

## Сохранение рабочего времени при idle

`__set_current_step`: `reset_elapsed_time()` вызывается только если ни текущий, ни новый
шаг не `iddle_mode`. Таким образом счёт рабочего времени «замораживается» на время
неактивности и продолжается с того же места при возврате пользователя.
Исключение: `reset_work_time_in_idle = "on"` — сброс elapsed при входе в iddle (см. выше).

## Действия по шагам (do_current_step_actions)

| Шаг | Действие |
|---|---|
| `off_mode` | уведомление «protection is off» |
| `suspended_mode` | уведомление «protection suspended» |
| `break_mode` | обновление окна перерыва + звук `notification_break` + `set_activity_offset()` |
| `work_notified_1` | `set_activity_offset()` + уведомление «1 minute» (если notifications=on) |
| `work_notified_2` | `set_activity_offset()` + уведомление «5 seconds» (если notifications=on) |
| `work_mode` | обновление окна перерыва + звук `notification_work` + `set_activity_offset()` |
| `iddle_mode` | уведомление «iddle mode» + звук `notification_idle` + `reset_activity_offset()` |

Звуки играются только при `sounds = "on"` (проверяет `SoundNotificator`).

## Тик времени

`wait_for_current_step_is_ended`: цикл со `time.sleep(TIME_TICK_S)`; время увеличивается только
если шаг ∉ {off_mode, iddle_mode}. Каждый тик проверяется активность пользователя и видео.
Во время тика обновляются: окно перерыва (break) или окно статуса + трей (остальные).

## Как добавить новый шаг

1. Новый member в `StepType` (значение = следующий IntEnum).
2. Переход в `Model.set_new_step_in_sequence` (match).
3. Действия в `Model.do_current_step_actions` (match).
4. Длительность в `Model.__init_steps` (в `steps_data_list`).
5. Если шаг «замораживает» время — учесть в условиях `wait_for_current_step_is_ended` и `__set_current_step`.
6. При необходимости — обновить расчёты `remaining_working_time_to_display` / `time_for_work_full`.
7. Дополнить тесты и обновить эту заметку + граф знаний (`memory_add_observations`).
