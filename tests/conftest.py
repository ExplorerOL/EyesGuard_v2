"""Shared test bootstrap: src import path, fixture path helper and Model test harness.

Importing src modules in tests works regardless of the current working
directory: the path is derived from this conftest file location.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

FIXTURES_DIR = Path(__file__).resolve().parent / 'data'


def fixture_path(file_name: str) -> Path:
    """Absolute path to a fixture file from tests/data."""
    return FIXTURES_DIR / file_name


class FakeActivityMonitor:
    """Deterministic stub for UserActivityMonitor.

    Reports the user inactive for the first `inactive_reads` reads, then
    falls back to the `active` flag. The wait loop never exits on its own
    while the user stays inactive, so tests must script the return of
    activity to let the loop terminate.
    """

    def __init__(self, active: bool = True, inactive_reads: int = 0):
        self.active = active
        self._reads_left = inactive_reads
        self.offset_set_count = 0
        self.offset_reset_count = 0

    @property
    def is_user_active(self) -> bool:
        if self._reads_left > 0:
            self._reads_left -= 1
            return False
        return self.active

    def set_activity_offset(self) -> None:
        self.offset_set_count += 1

    def reset_activity_offset(self) -> None:
        self.offset_reset_count += 1


class FakeView:
    """Records snapshots and notifications instead of touching Tk."""

    def __init__(self):
        self.notifications: list[tuple[str, str]] = []
        self.snapshots: list = []

    def submit_snapshot(self, snapshot) -> None:
        self.snapshots.append(snapshot)

    def show_notification(self, title: str, text: str) -> None:
        self.notifications.append((title, text))


def make_model(tmp_path: Path, monkeypatch, settings: dict | None = None, inactive_reads: int = 0):
    """Create a Model with stubbed activity monitor and a recording FakeView.

    `inactive_reads` scripts the monitor: the first N reads report the user
    inactive, afterwards the user is active. Returns
    (model, view, activity_monitor).
    """
    import model as model_module

    activity_monitor = FakeActivityMonitor(active=True, inactive_reads=inactive_reads)
    monkeypatch.setattr(model_module, 'UserActivityMonitor', lambda activity_timeout: activity_monitor)

    settings_file = tmp_path / 'settings.json'
    settings_file.write_text(json.dumps(settings or {}), encoding='utf-8')

    model = model_module.Model(settings_file=settings_file)
    view = FakeView()
    model.set_view(view=view)
    return model, view, activity_monitor


def run_ticks_until_step_ends(model, max_ticks: int = 100_000) -> int:
    """Drive model.tick() until the current step ends (no real waiting)."""
    ticks = 0
    while not model.tick():
        ticks += 1
        if ticks > max_ticks:
            raise AssertionError('model.tick() did not end the step within the tick limit')
    return ticks
