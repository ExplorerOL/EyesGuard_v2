# Машина состояний приложения

Источник кода: `src/config/states.py` (`StepType`, `StepData`, `CurrentState`), переходы — `src/model.py` (`set_new_step_in_sequence`, `do_current_step_actions`, `wait_for_current_step_is_ended`, `__init_steps`).

## Шаги StepType (IntEnum)

| Значение | Имя | Смысл | Длительность |
|---|---|---|---|
| 0 | `off_mode` | Защита выключена | STEP_SUSPENDED_MODE_DURATION (60 м), но время не тикает — шаг «висит» |
| 1 | `suspended_mode` | Защита приостановлена | 60 м (system) |
| 2 | `work_mode` | Работа, счёт до перерыва | work_duration − n1 − n2 (если > 0, иначе 0) |
| 3 | `work_notified_1` | Предупреждение «до перерыва 1 минута» | 55 с (system) |
| 4 | `work_notified_2` | Предупреждение «до перерыва 5 секунд» | 5 с (system) |
| 5 | `break_mode` | Перерыв | break_duration (user, 15 м по умолчанию) |
| 6 | `iddle_mode` | Пользователь неактивен (> USER_ACTIVITY_TIMEOUT = 3 мин) | = длительность work-шага; время не тикает |

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
   │ неактивен > 3 мин (в любом work-шаге цепочки)
   │
 work_mode (продолжение счёта)

 suspended_mode ──► work_mode        (возврат по таймеру шага)
 off_mode: перехода нет — остаётся в off_mode
```

Переходы в/из `iddle_mode` выполняются **внутри** `wait_for_current_step_is_ended`
(проверка активности каждый тик), а не в `set_new_step_in_sequence`:

- неактивен и текущий шаг ∈ {work_mode, work_notified_1, work_notified_2} → `set_step(StepType.iddle_mode)`;
- активен и текущий шаг = iddle_mode → `set_step(StepType.work_mode)`;
- `set_new_step_in_sequence` для `iddle_mode` перехода не содержит — попадание туда означало бы UnboundLocalError; этого не происходит, т.к. время в iddle не тикает и wait-цикл переключает шаг раньше.

## Сохранение рабочего времени при idle

`__set_current_step`: `reset_elapsed_time()` вызывается только если ни текущий, ни новый
шаг не `iddle_mode`. Таким образом счёт рабочего времени «замораживается» на время
неактивности и продолжается с того же места при возврате пользователя.

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
если шаг ∉ {off_mode, iddle_mode}. Каждый тик проверяется активность пользователя.
Во время тика обновляются: окно перерыва (break) или окно статуса + трей (остальные).

## Как добавить новый шаг

1. Новый member в `StepType` (значение = следующий IntEnum).
2. Переход в `Model.set_new_step_in_sequence` (match).
3. Действия в `Model.do_current_step_actions` (match).
4. Длительность в `Model.__init_steps` (в `steps_data_list`).
5. Если шаг «замораживает» время — учесть в условиях `wait_for_current_step_is_ended` и `__set_current_step`.
6. При необходимости — обновить расчёты `remaining_working_time_to_display` / `time_for_work_full`.
7. Дополнить тесты и обновить эту заметку + граф знаний (`memory_add_observations`).
