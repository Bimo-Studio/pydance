"""Optional trace: chart data → **scrolling step arrows** (timing) → draw.

The **scrolling arrows** move toward the receptors and show when to step. The static
row at the top (receptors) is separate; this trace focuses on the scrolling sprites.

Enable with::

    PYDANCE_TRACE_STEPS=1 python pydance.py

Logs go to stderr via logger ``pydance.steps_trace`` (respects ``PYDANCE_LOG_LEVEL``).
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger("pydance.steps_trace")

_nevent_logs = 0
_sprite_logs = 0
_draw_last_sec: int | None = None


def enabled() -> bool:
    return os.environ.get("PYDANCE_TRACE_STEPS", "").lower() in ("1", "true", "yes")


def log_steps_loaded(steps_obj, song_filename: str) -> None:
    """Call from ``Steps.__init__`` after events are built."""
    if not enabled():
        return
    events = steps_obj.events
    samples: list[tuple] = []
    for ev in events:
        if ev.feet:
            samples.append((ev.when, ev.beat, tuple(ev.feet), ev.appear))
        if len(samples) >= 20:
            break
    logger.info(
        "steps loaded: file=%s mode=%s diff=%s chart_events=%d totalarrows=%d "
        "ready=%.4f length=%.4f offset=%.4f",
        song_filename,
        steps_obj.playmode,
        steps_obj.difficulty,
        len(events),
        steps_obj.totalarrows,
        float(steps_obj.ready or 0.0),
        float(steps_obj.length),
        float(steps_obj.offset),
    )
    if samples:
        logger.info("steps sample (first foot events): %s", samples)


def log_get_events(curtime: float, steps_obj, nevents: list) -> None:
    """Log when scrolling timing arrows become due to spawn (``appear`` window)."""
    global _nevent_logs
    if not enabled() or not nevents:
        return
    if _nevent_logs >= 40:
        return
    _nevent_logs += 1
    ev = nevents[0]
    feet = ev.feet if ev.feet else ()
    logger.info(
        "get_events (scrolling arrows due): t=%.4f chart_events=%d nevents_batch=%d "
        "first_when=%.4f beat=%.4f feet=%s appear=%s",
        curtime,
        len(steps_obj.events),
        len(nevents),
        float(ev.when),
        float(ev.beat),
        feet,
        ev.appear,
    )


def log_arrow_sprites(pid: int, created: int, ev_when: float, feet) -> None:
    """Log first batches of **scrolling step** sprites from ``Player._get_next_events``."""
    global _sprite_logs
    if not enabled() or created <= 0:
        return
    if _sprite_logs >= 30:
        return
    _sprite_logs += 1
    logger.info(
        "scrolling_step_arrow_sprites: pid=%d created=%d hit_time=%.4f feet=%s",
        pid,
        created,
        float(ev_when),
        feet,
    )


def log_start_song(pid: int, dark: int, n_receptor_sprites: int, game_dirs: tuple) -> None:
    global _nevent_logs, _sprite_logs, _draw_last_sec
    if not enabled():
        return
    _nevent_logs = 0
    _sprite_logs = 0
    _draw_last_sec = None
    logger.info(
        "start_song: pid=%d dark=%s — static receptor row (top) %s; "
        "n_receptor_sprites=%d (not the scrolling timing arrows) dirs=%s",
        pid,
        dark,
        "hidden" if dark else "visible",
        n_receptor_sprites,
        game_dirs,
    )


def log_draw(
    pid: int,
    curtime: float,
    n_scroll: int,
    n_top: int,
    n_fx: int,
    n_hud: int,
    first_scroll_rect: tuple[int, int, int, int] | None = None,
) -> None:
    """Once per second: scrolling sprite counts + optional first arrow rect (640×480 space)."""
    global _draw_last_sec
    if not enabled() or pid != 0:
        return
    sec = int(curtime)
    if _draw_last_sec == sec:
        return
    _draw_last_sec = sec
    extra = ""
    if first_scroll_rect is not None:
        left, top, w, h = first_scroll_rect
        extra = f" sample_scrolling_arrow_rect=({left},{top},{w}x{h})"
    logger.info(
        "draw ~t=%ds scrolling_step_arrows=%d static_receptor_row=%d fx=%d hud=%d%s",
        sec,
        n_scroll,
        n_top,
        n_fx,
        n_hud,
        extra,
    )
