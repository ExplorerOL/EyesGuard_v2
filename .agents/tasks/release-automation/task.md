# release-automation

## Постановка задачи

Доработать приложение так, чтобы при пуше в `master` на GitHub оно собиралось с помощью
PyInstaller и автоматически формировался релиз.

## Решения (согласованы с пользователем)

- Триггер релиза — пуш в `master` со **сменой версии** в `pyproject.toml`; повторные пуши без
  смены версии пропускаются (проверка существования тега `EyesGuard-v<version>`).
- Артефакты релиза — **оба**: onefile exe + onedir zip (`EyesGuard-v<version>-win64.exe`, `.zip`).
- Release notes — секция `[X.Y.Z]` из CHANGELOG.md (fallback-текст при отсутствии).
- Единая версия в UI — константа `APP_VERSION` (`src/config/app_version.py`) + тест сверки с
  `pyproject.toml` (ранее `importlib.metadata` отклонён: проект в non-package mode, uv не
  устанавливает пакет).
- Перед релизом 2.1.0: CHANGELOG `[Unreleased]` → `[2.1.0]`, записи сокращены, агентская/инфра
  рутина удалена; версия `2.1.0` проставлена в UI (6 мест с захардкоженной `2.0.0`).

## Реализация

| Файл | Что сделано |
|------|-------------|
| `.github/workflows/release.yml` | Новый workflow: windows-latest, версия из pyproject (tomllib), skip по тегу, `uv sync --frozen` → pytest → onefile → rename → onedir → rename+Compress-Archive → notes из CHANGELOG (`body_path: release_notes.md`) → `softprops/action-gh-release@v2` |
| `src/config/app_version.py` | Новый: `APP_VERSION = '2.1.0'` |
| `src/view.py`, `src/windows/wnd_*.py` | 6 мест версии → f-строки с `APP_VERSION` |
| `tests/test_app_version.py` | Новый: сверка `APP_VERSION` с `pyproject.toml` |
| `CHANGELOG.md` | `[Unreleased]` → `[2.1.0] - 2026-11-19`, сокращение записей, обновление ссылок compare/tag |
| `README.md` | Секция `Releases`: механика + чек-лист релиза |

## Нюансы реализации

- Все `run`-шаги workflow — `shell: bash` (дефолт на windows-latest — pwsh).
- Python-код во вложенном heredoc обязан стоять на колонке базового отступа YAML block scalar
  (после отсечения — 0 отступов); иначе `PY`-delimiter не распознаётся bash.
- Zip делается шагом `shell: pwsh` (`Compress-Archive` предустановлен на windows-раннере).
- Правило релиза: смена версии = `pyproject.toml` + `uv lock` + секция `[X.Y.Z]` в CHANGELOG,
  одним коммитом в `master`.

## Статус

- Реализовано; локальная симуляция шагов (version, tag-check, notes-извлечение) пройдена.
- Полный прогон workflow — только после пуша в `master` (GitHub Actions): требует проверки в CI.
