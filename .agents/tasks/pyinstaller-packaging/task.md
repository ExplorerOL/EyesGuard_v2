# PyInstaller-сборка EyesGuard

## Постановка

Запуск проекта на Windows через PyInstaller: добавить pyinstaller в dev-зависимости,
сделать самодостаточный onefile exe (res/ бандлится внутрь) с правкой резолва путей,
описать сборку в README, добавить конфигурацию PyInstaller в проект.

## Реализация

- `pyinstaller==6.22.3` (dev-зависимость, pyproject.toml + uv.lock).
- `src/support/paths.py`: `app_dir()` (записываемые данные: каталог exe при frozen, CWD в dev),
  `resource_dir()` (ресурсы: `sys._MEIPASS` при frozen, CWD в dev).
- Потребители: `resourses.py` (ресурсы), `model.py` `SETTINGS_FILE`, `logger.py` (sink лога).
- `Settings.save_settings_to_file` создаёт каталог settings/ (первый запуск exe).
- `EyesGuard.spec`: onefile, `res/` через datas, `console=False`, иконка трея,
  `hiddenimports=['pystray._win32']` (условный импорт backend трея).
- README: команда `uv run pyinstaller EyesGuard.spec`.

## Верификация

- pytest: 11 passed (Linux).
- ruff check/format: чисто.
- Пробная сборка на Linux: exe собрался, res/ и все модули проекта в архиве
  (playsound/pystray._win32/tcl-tk — ожидаемые Linux-предупреждения).
- Рабочий exe: ручная проверка на Windows.

## Фикс установки playsound (2026-11-18)

- `uv sync` на Windows падал на сборке sdist playsound 1.3.0: setup.py ищет свой путь
  через `inspect.getsource(lambda:0)` и падает при PEP 517-запуске (exec без файла,
  `OSError: could not get source code`). Хак `[[tool.uv.dependency-metadata]]` спасал
  только резолв lock, но не установку.
- Решение: wheel собран legacy-командой `python setup.py bdist_wheel` из официального
  sdist (pure-python, py3-none-any), закоммичен в `wheels/`, подключён через
  `[tool.uv.sources] playsound = { path = ... }`; metadata-хак удалён, lock содержит
  sha256 wheel'а.

## Фикс звука в frozen exe (2026-11-18, Error 305)

- Симптом: `PlaysoundException Error 305` (MCI winmm: «Лишние символы после текстовой
  строки, заключенной в кавычки») при `open` mp3 из `_MEI.../res/sounds/`.
- Причина (upstream TaylorSMarks/playsound#75): 1.3.0 передаёт в `mciSendStringW`
  байты `encode('utf-16')` без argtypes — ctypes отдаёт их как `char*`, MCI-парсер
  получает мусор. Фикс PR #76 (argtypes + `create_unicode_buffer`, передача `str`)
  есть только в git master — релиз на PyPI так и не вышел.
- Решение: вендоренный wheel пересобран с наложенным патчем PR #76
  (hash `65816450...`), `uv lock` обновлён. Исходники патча — /tmp сборка
  из официального sdist + diff PR #76.

## Фикс запуска frozen exe (2026-11-18)

- Первый запуск exe падал: `wnd_settings.py` открывал иконку напрямую
  `ImageTk.PhotoImage(file='res/img/eyes_with_protection.png')` — относительный путь
  мимо `ResImages` не существует внутри onefile-архива. Заменено на
  `ImageTk.PhotoImage(ResImages.img_protection_active)`.
- Аудит `src/` на прямые пути `res/` повторён — других потребителей нет.
