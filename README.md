## About EyesGuard
Program EyesGuard helps you to keep vision in order.
It reminds about necessity to have a break during long work and informs about the start and the end of the break.

EyesGuard is distributed under GPL v3 licence. By for now it is tested with Python 3.11 and Windows 10.

You can find more info about EyesGuard at [www.eyesguard.ru](https://eyesguard.ru).

## Development setup (uv)

```
uv sync
```

Creates `.venv` from `pyproject.toml` + `uv.lock` (sound dependency `playsound` is Windows-only and is skipped on other platforms automatically).
`playsound` is installed from the vendored wheel `wheels/playsound-1.3.0-py3-none-any.whl`: its PyPI sdist does not build under PEP 517 (buggy `setup.py` that resolves its own path via `inspect.getsource`).
The wheel also carries the upstream MCI fix (playsound PR #76, never released to PyPI) — without it `winmm` may fail playback with `Error 305` on some systems.

## Commands

Command to start app while developing (Windows only):
```
python ./src/main.py
```
Run it from the project root: the app reads `res/`, `settings/`, `logs/` by relative paths.

Commands for lint and format (only on files touched by your change):
```
uv run ruff check --fix <files>
uv run ruff format <files>
```

Command for running tests:
```
uv run pytest -v
```

Command for building .exe (Windows only, from the project root):
```
uv run pyinstaller EyesGuard.spec
```
Result: `dist/EyesGuard.exe` — a single self-contained executable (`res/` resources are bundled inside).
At runtime the app creates `settings/` and `logs/` directories next to the exe file.

Alternative one-directory build (faster startup: no archive unpacking to %TEMP% at every launch;
`res/` is shipped next to the exe):
```
uv run pyinstaller EyesGuard-onedir.spec
```
Result: `dist/EyesGuard/` — a folder with `EyesGuard.exe` and bundled files; run the exe from there.

### Building from a WSL checkout

PyInstaller builds only for the platform it runs on, so the build must be executed by Windows-native
`uv`/Python — WSL produces a Linux binary instead of `.exe`. Do not run `uv` from Windows against a
WSL checkout (`\\wsl.localhost\...`): Windows `uv` breaks the Linux `.venv` over the UNC share.
Recommended workflow — development in WSL, build in a one-time clone on a native NTFS folder:

```
git clone \\wsl.localhost\Debian\home\<user>\git\github\ExplorerOL\EyesGuard_v2 C:\Users\<user>\EyesGuard_build
cd C:\Users\<user>\EyesGuard_build
uv sync
uv run pyinstaller EyesGuard.spec
```

The clone remembers the WSL path as origin: after new commits in WSL run `git pull` in the build
clone and rebuild. `.venv` is gitignored, so WSL and the clone keep independent virtual environments.
