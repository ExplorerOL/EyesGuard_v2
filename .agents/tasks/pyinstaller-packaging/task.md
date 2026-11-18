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
