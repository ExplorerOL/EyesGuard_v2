"""Tests for the after()-based fade helper (known issue 17)."""

from windows.window_fade import FADE_STEPS, fade_window


class FakeTkWindow:
    """Window stub recording alpha changes and scheduled after() callbacks."""

    def __init__(self):
        self.alpha = None
        self.after_id = 0
        self.scheduled = None  # (id, callback) scheduled by the last after()
        self.cancelled_ids = []
        self.withdrawn = False
        self.deiconified = False

    def attributes(self, *args):
        if len(args) == 2:
            self.alpha = args[1]

    def after(self, milliseconds, callback):
        self.after_id += 1
        self.scheduled = (self.after_id, callback)
        return self.after_id

    def after_cancel(self, after_id):
        self.cancelled_ids.append(after_id)
        self.scheduled = None

    def withdraw(self):
        self.withdrawn = True

    def deiconify(self):
        self.deiconified = True

    def run_all_pending(self):
        """Execute the scheduled after() callback chain synchronously."""
        while self.scheduled is not None:
            _, callback = self.scheduled
            self.scheduled = None
            callback()


def test_fade_in_runs_without_blocking_and_finishes():
    window = FakeTkWindow()
    finished = []
    fade_window(window, showing=True, on_done=lambda: finished.append(True))

    assert window.alpha == 0.0  # first step applied synchronously
    window.run_all_pending()

    assert window.alpha == 1.0
    assert finished == [True]


def test_fade_out_finishes_at_zero():
    window = FakeTkWindow()
    fade_window(window, showing=False)

    window.run_all_pending()

    assert window.alpha == 0.0


def test_new_fade_cancels_previous_animation():
    window = FakeTkWindow()
    fade_window(window, showing=True)
    first_scheduled_id = window.scheduled[0]

    fade_window(window, showing=False)

    assert first_scheduled_id in window.cancelled_ids


def test_fade_uses_after_schedule_not_sleep():
    window = FakeTkWindow()
    fade_window(window, showing=True)

    # the helper must schedule the next step via after(), never block
    assert window.scheduled is not None
    assert window.after_id == 1


def test_full_animation_applies_all_steps():
    window = FakeTkWindow()
    alphas = []
    original_attributes = window.attributes

    def recording_attributes(*args):
        original_attributes(*args)
        alphas.append(window.alpha)

    window.attributes = recording_attributes
    fade_window(window, showing=True)
    window.run_all_pending()

    assert len(alphas) == FADE_STEPS + 1
    assert alphas == sorted(alphas)  # monotonic fade in
