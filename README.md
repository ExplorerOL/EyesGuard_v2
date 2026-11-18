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

Command for building .exe:
```
auto-py-to-exe
```
