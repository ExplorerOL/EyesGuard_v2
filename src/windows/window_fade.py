"""Non-blocking window fade animations based on after() (known issue 17).

The old show()/hide() blocked the Tk mainloop with time.sleep loops; the
helper schedules alpha changes via after() and cancels a running animation
when a new one starts.
"""

FADE_STEPS = 40
FADE_STEP_MS = 6
FADE_AFTER_ATTR = 'fade_after_id'


def fade_window(window, *, showing: bool, on_done=None) -> None:
    """Fade the window alpha without blocking; cancels the previous fade.

    Args:
        window: a Tk-like widget with attributes/after/after_cancel.
        showing: True fades 0 -> 1, False fades 1 -> 0.
        on_done: optional callback fired when the animation completes.
    """
    cancel_fade(window)
    start_alpha = 0.0 if showing else 1.0
    end_alpha = 1.0 if showing else 0.0

    def run_step(step_index: int) -> None:
        alpha = start_alpha + (end_alpha - start_alpha) * step_index / FADE_STEPS
        window.attributes('-alpha', alpha)
        if step_index < FADE_STEPS:
            setattr(window, FADE_AFTER_ATTR, window.after(FADE_STEP_MS, lambda: run_step(step_index + 1)))
        else:
            setattr(window, FADE_AFTER_ATTR, None)
            if on_done is not None:
                on_done()

    run_step(0)


def cancel_fade(window) -> None:
    """Cancel a running fade animation on the window, if any."""
    after_id = getattr(window, FADE_AFTER_ATTR, None)
    if after_id is not None:
        window.after_cancel(after_id)
        setattr(window, FADE_AFTER_ATTR, None)
