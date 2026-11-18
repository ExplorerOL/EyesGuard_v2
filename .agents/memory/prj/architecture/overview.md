# Архитектура EyesGuard_v2 (ветка feature/v2.1.0)

Обзор в [README.md](../../../README.md). Связанные материалы: [стиль кода](../style.md), [машина состояний](../../app/state-machine.md), [настройки](../../app/settings.md).

## Структура каталогов

```
src/
├── main.py                     # точка входа: создание и связывание MVC
├── controller.py               # Controller: оркестрация в отдельном потоке
├── model.py                    # Model: тайминги, машина состояний
├── view.py                     # View: главное окно + трей
├── config/                     # конфигурация и состояния
│   ├── settings.py             # UserSettingsData/SystemSettingsData + pydantic-валидатор
│   └── states.py               # StepType, StepData, CurrentState
├── support/                    # инфраструктурные модули
│   ├── logger.py               # loguru
│   ├── paths.py                # резолв путей: dev (CWD) / frozen (sys._MEIPASS, каталог exe)
│   ├── resourses.py            # ResImages (PNG) + ResSoundsPaths (MP3)
│   ├── user_activity_monitor.py# Windows API: неактивность пользователя
│   └── sound/
│       ├── sound_player.py     # playsound в отдельном потоке (синглтон sound_player)
│       └── sound_notificator.py# SoundNotificator: звук если sounds=on
└── windows/                    # окна приложения
    ├── wnd_status.py
    ├── wnd_settings.py
    └── wnd_break.py
```

Все модули — плоский пакет `src` (без `__init__.py` у корня), импорты абсолютные
«от корня src»: `from config.settings import Settings`, `from support.logger import logger`.

Приложение запускается как `python ./src/main.py` **из корня проекта**. Пути к данным
резолвит `support/paths.py`: в dev-режиме — от CWD (`res/img/`, `res/sounds/`,
`settings/settings.json`, `logs/log.log`), в замороженном (PyInstaller) — ресурсы из
`sys._MEIPASS`, настройки и логи — рядом с exe (`app_dir()`).

## Сборка (PyInstaller)

- Команда: `uv run pyinstaller EyesGuard.spec` из корня проекта, **только на Windows**.
- Spec: onefile (`dist/EyesGuard.exe`), `res/` бандлится через `datas`, `console=False`,
  иконка `res/img/eyes_with_protection.ico`, `hiddenimports=['pystray._win32']`
  (backend трея выбирается условным импортом).
- `customtkinter` подхватывается хуком из `pyinstaller-hooks-contrib`; `playsound`
  ставится только по маркеру win32. Сборка проверена на Linux только механически
  (datas/модули в архиве) — рабочий exe собирается на Windows.

## Общая схема

```
                 main.py
                    │ (создание + связывание set_*)
     ┌──────────────┼──────────────────┐
     ▼              ▼                  ▼
Controller ─────► Model ◄──────────── View
 (Thread)          │                    │
                   ├── Settings         ├── WndStatus / WndSettings / WndBreak
                   ├── CurrentState     ├── pystray.Icon (трей, уведомления)
                   │   └── StepType     └── ResImages (PIL)
                   ├── steps_data_list
                   ├── UserActivityMonitor  (Windows API, idle)
                   └── SoundNotificator ── SoundPlayer (playsound)
```

## Поток выполнения

1. `main()` создаёт три слоя и связывает циклически:
   `controller.set_model(model)`, `model.set_view(view)`, `view.set_controller(controller)`.
2. `controller.start()` — запуск `main_loop` в отдельном `Thread`.
3. `view.mainloop()` — цикл Tkinter в главном потоке.
4. `Controller.main_loop` (бесконечный цикл, тик `TIME_TICK_S` = 1 с):
   `model.do_current_step_actions()` → `model.wait_for_current_step_is_ended()` → `model.set_new_step_in_sequence()`.

## Направления связи

| Откуда → Куда | Механизм | Пример |
|---|---|---|
| Controller → Model | прямые вызовы | `model.set_step(new_step_type=...)` |
| Model → View | прямые вызовы обновления | `__view.update_wnd_status(self.model)` (модель передаёт сама себя) |
| View → Controller | прямые вызовы событий | `controller.apply_view_user_settings(...)`, `switch_to_suspended_state()` |
| Model → Model | self-reference | property `model` возвращает `self` — обращения вида `self.model.__current_state` |

Особенности, которые надо учитывать при правках:

- Model ссылается на себя через property `model` (`src/model.py`) — не «выпрямлять» без необходимости.
- Циклический импорт Model ↔ View разорван через `from __future__ import annotations` + `TYPE_CHECKING`.
- View создаёт собственные `Settings()` и `CurrentState()` для окон (двойное владение состоянием — осознанное упрощение).
- `Model` владеет `UserActivityMonitor` и `SoundNotificator`; `sound_player` — модульный синглтон.

## Потоки (threading)

- Tkinter mainloop — главный поток; `pystray` — `run_detached()`; `Controller.main_loop` — отдельный `Thread`;
  проигрывание звука — ещё один короткоживущий `Thread` на каждый звук (`SoundPlayer.play`).
- Обновления окон из контроллерного потока идут напрямую — при доработках помнить про потокобезопасность Tkinter.
- Выход из приложения — жёсткий `os._exit(0)` в `View.exit_app` (не останавливает потоки штатно).

## Платформенная специфика

- `UserActivityMonitor` использует `ctypes.windll` — **только Windows**. На Linux API недоступен (безопасный дефолт в методе, но сам вызов упадёт).
- `playsound` на Windows использует winsound-бэкенд; звук — фича только для запущенного приложения на Windows.
- GUI-часть в автоматических тестах не покрывается; на Linux тестируются только `config/settings.py` (+ потенциально `states`).

## Границы расширения

- Новые шаги состояния → `StepType` + переходы в `Model.set_new_step_in_sequence` + действия в `do_current_step_actions` + длительность в `__init_steps` (см. [state-machine.md](../../app/state-machine.md)).
- Новые настройки → `UserSettingsData` + `SettingsDataValidator` + окно `WndSettings` (см. [settings.md](../../app/settings.md)).
- Новые звуки → mp3 в `res/sounds/` + путь в `ResSoundsPaths` + метод в `SoundNotificator`.
- Новые окна → класс в `src/windows/`, создание в `View.__init__`, метод `update(model)` по образцу существующих.
