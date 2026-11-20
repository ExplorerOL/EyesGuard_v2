# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.1] - 2026-11-20

### Added
- wemake-python-styleguide linting (WPS via flake8, `.flake8`) with pre-commit hooks and CI gate; existing violations suppressed and tracked in `.agents/memory/prj/known-wps-linter-problems.md`
- ty type checking (Astral, `linter_ty.toml`, win32 platform) with pre-commit hooks and CI gate; existing diagnostics suppressed and tracked with required fixes in `.agents/memory/prj/known-ty-linter-problems.md`

### Changed
- Faster window fade-in: fewer animation steps, hidden windows skip per-tick snapshot updates, freshly shown windows receive the latest snapshot immediately, and the settings window redraws its protection decoration only on an actual state change

### Fixed
- GUI windows and tray actions are now handled only in the main UI thread via a snapshot queue, preventing rare freezes and redraw glitches
- Application now shuts down gracefully (stopped controller thread, tray icon) instead of force-killing the process
- Applying settings no longer resets the current step timer or interrupts an active break; only an actual protection on/off change switches the step
- Idle mode now restores the interrupted work phase (including pre-break notifications) with its remaining time instead of restarting the full work interval
- Installed (frozen) builds now store settings and logs in `%LOCALAPPDATA%/EyesGuard` with one-time migration from the executable directory, so installs into Program Files no longer fail on write permissions
- Time displays (status window, tray tooltip, break window) now show whole seconds without microseconds
- Fixed "iddle" typo: renamed `StepType.iddle_mode` to `StepType.idle_mode` and corrected the idle mode notification and log texts

## [2.3.0] - 2026-11-19

### Added
- Display settings tab: block screensaver during breaks (`screensaver_block`) and switch to idle mode on video playback (`suspend_on_video`)
- Time settings tab: reset working time on entering idle mode (`reset_work_time_in_idle`)
- Idle mode on video playback: video is detected via the system `ES_DISPLAY_REQUIRED` flag, entering idle keeps the work timer paused

## [2.2.0] - 2026-11-19

### Added
- Sounds settings tab: sounds on/off checkbox moved from General and new 1-100% volume slider (user setting `volume`)

### Changed
- Sound playback migrated from playsound to the built-in Windows MCI player (winmm, `src/support/sound/windows/`) with volume support
- About tab: copyright year moved to the `APP_YEAR` constant and updated to 2026

### Removed
- playsound dependency and vendored wheel `wheels/playsound-1.3.0-py3-none-any.whl`

## [2.1.0] - 2026-11-19

### Added
- Release automation: GitHub Actions workflow builds PyInstaller artifacts (exe and zip) and publishes a release on version bump in master
- User-configurable activity timeout (30-600 s): settings field, applied live without restart
- One-directory PyInstaller build variant (EyesGuard-onedir.spec)
- PyInstaller packaging: onefile spec with bundled res/ and tray icon

### Fixed
- Sound playback: vendored playsound wheel patched with the upstream MCI fix (PR #76) to stop winmm Error 305
- Settings window icon: fixed FileNotFoundError for res/img in frozen builds

### Changed
- Runtime paths resolved for frozen builds: resources via sys._MEIPASS, settings and logs next to the exe
- PyInstaller bundle slimmed via Analysis excludes: unused stdlib modules and pydantic.v1 shim removed
- Project migrated to uv: pyproject.toml + uv.lock; pillow added; playsound restricted to the win32 marker

### Removed
- requirements.txt: pyproject.toml + uv.lock is now the single source of dependencies

## [2.0.0] - 2024-04-02

### Added
- First release of EyesGuard for Windows written in Python

[Unreleased]: https://github.com/ExplorerOL/EyesGuard_v2/compare/EyesGuard-v2.3.1..HEAD
[2.3.1]: https://github.com/ExplorerOL/EyesGuard_v2/compare/EyesGuard-v2.3.0...EyesGuard-v2.3.1
[2.3.0]: https://github.com/ExplorerOL/EyesGuard_v2/compare/EyesGuard-v2.2.0...EyesGuard-v2.3.0
[2.2.0]: https://github.com/ExplorerOL/EyesGuard_v2/compare/EyesGuard-v2.1.0...EyesGuard-v2.2.0
[2.1.0]: https://github.com/ExplorerOL/EyesGuard_v2/releases/tag/EyesGuard-v2.1.0
[2.0.0]: https://github.com/ExplorerOL/EyesGuard_v2/releases/tag/EyesGuard-v2.0.0
