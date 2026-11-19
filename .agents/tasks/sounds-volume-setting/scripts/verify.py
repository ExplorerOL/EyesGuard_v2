"""Machine-checkable invariants of the sounds-volume-setting task.

Run from the project root: uv run python .agents/tasks/sounds-volume-setting/scripts/verify.py
Success = all checks passed.
"""

import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SETTINGS_PY = PROJECT_ROOT / 'src' / 'config' / 'settings.py'
WINDOWS_SOUND_PLAYER = PROJECT_ROOT / 'src' / 'support' / 'sound' / 'windows' / 'sound_player.py'


def check_no_playsound_in_project() -> bool:
    """playsound must not occur in pyproject.toml and src/."""
    targets = [PROJECT_ROOT / 'pyproject.toml', *sorted((PROJECT_ROOT / 'src').rglob('*.py'))]
    offenders = [path for path in targets if 'playsound' in path.read_text(encoding='utf-8')]
    if offenders:
        print(f"FAIL: 'playsound' found in: {[str(path.relative_to(PROJECT_ROOT)) for path in offenders]}")
        return False
    print("PASS: 'playsound' not found in pyproject.toml and src/")
    return True


def check_volume_validator_bounds() -> bool:
    """SettingsDataValidator must declare volume with ge=10, le=100."""
    source = SETTINGS_PY.read_text(encoding='utf-8')
    pattern = re.compile(r'volume:\s*int\s*=\s*Field\([^)]*ge=10[^)]*le=100[^)]*\)')
    if not pattern.search(source):
        print('FAIL: volume field with ge=10, le=100 not found in SettingsDataValidator')
        return False
    print('PASS: SettingsDataValidator has volume with ge=10, le=100')
    return True


def check_windows_sound_player_exists() -> bool:
    """Windows MCI sound player module must exist."""
    if not WINDOWS_SOUND_PLAYER.is_file():
        print(f'FAIL: {WINDOWS_SOUND_PLAYER.relative_to(PROJECT_ROOT)} does not exist')
        return False
    print(f'PASS: {WINDOWS_SOUND_PLAYER.relative_to(PROJECT_ROOT)} exists')
    return True


def check_pytest_green() -> bool:
    """Full pytest run must pass."""
    result = subprocess.run(
        [sys.executable, '-X', 'utf8', '-m', 'pytest', './tests/'],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print('FAIL: pytest run failed:')
        print(result.stdout[-2000:])
        print(result.stderr[-2000:])
        return False
    print('PASS: pytest is green')
    return True


def main() -> int:
    checks = [
        check_no_playsound_in_project,
        check_volume_validator_bounds,
        check_windows_sound_player_exists,
        check_pytest_green,
    ]
    results = [check() for check in checks]
    if all(results):
        print(f'OK: all {len(results)} checks passed')
        return 0
    print(f'FAILED: {results.count(False)} of {len(results)} checks failed')
    return 1


if __name__ == '__main__':
    sys.exit(main())
