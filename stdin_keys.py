"""Map terminal arrow/Enter keys to pygame events when SDL has no keyboard (dummy video).

IDE embedded terminals (e.g. Cursor on macOS) force SDL dummy video; pygame then does not
receive key events from the OS. This module reads ANSI escape sequences from stdin and
posts matching KEYDOWN/KEYUP pairs so ui keyboard plumbing still works.

In canonical TTY mode, arrow keys are often line-buffered and never arrive until Enter.
We call tty.setcbreak() once so each key is readable immediately (restored on exit).

``stdin`` may **not** be a TTY in some IDE terminals (piped pseudo-input). We still try
non-blocking reads so arrow bytes can reach pygame; cbreak is only applied when
``stdin.isatty()`` is true. Piped stdin may remain line-buffered by the parent process.

Disable with PYDANCE_DISABLE_STDIN_KEYS=1. Force on with PYDANCE_FORCE_STDIN_KEYS=1.
Not used on Windows (no select on stdin / no POSIX termios for this path).
"""

from __future__ import annotations

import atexit
import logging
import os
import sys

_stdin_buf = bytearray()
_stdin_keys_logger = logging.getLogger("pydance.stdin_keys")
_logged_not_tty = False
_tty_attrs = None
# Defer KEYUP to the next inject call so ui.pump() never sees KEYDOWN+KEYUP for the same key in
# one batch (keyboard valves would open and close immediately; menus would get no UP/DOWN).
_pending_keyup_key = None


def feed_stdin_bytes_for_tests(data: bytes) -> None:
    """Append bytes and process (for unit tests only)."""
    _flush_pending_keyup()
    _stdin_buf.extend(data)
    _consume_buffer()


def _should_inject_stdin() -> bool:
    if os.environ.get("PYDANCE_DISABLE_STDIN_KEYS", "").lower() in ("1", "true", "yes"):
        return False
    if os.environ.get("PYDANCE_FORCE_STDIN_KEYS", "").lower() in ("1", "true", "yes"):
        return True
    if os.environ.get("SDL_VIDEODRIVER") == "dummy":
        return True
    try:
        import sdl_env

        return bool(sdl_env.headless_sdl)
    except ImportError:
        return False


def _ensure_tty_cbreak() -> None:
    """Switch stdin to cbreak so arrow keys emit escape sequences without waiting for Enter."""
    global _tty_attrs
    if _tty_attrs is not None:
        return
    if sys.platform == "win32":
        return
    if not sys.stdin.isatty():
        return
    if "pytest" in sys.modules:
        return
    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        _tty_attrs = termios.tcgetattr(fd)
        tty.setcbreak(fd)

        def _restore() -> None:
            global _tty_attrs
            if _tty_attrs is None:
                return
            try:
                termios.tcsetattr(fd, termios.TCSAFLUSH, _tty_attrs)
            except OSError:
                pass
            _tty_attrs = None

        atexit.register(_restore)
    except (ImportError, OSError, AttributeError):
        _tty_attrs = None


def _trace_stdin_enabled() -> bool:
    return os.environ.get("PYDANCE_TRACE_MENU_INPUT", "").lower() in ("1", "true", "yes") or os.environ.get(
        "PYDANCE_TRACE_STDIN_KEYS", ""
    ).lower() in ("1", "true", "yes")


def inject_stdin_as_pygame_events() -> None:
    if not _should_inject_stdin():
        return
    if sys.platform == "win32":
        return

    # Flush deferred KEYUP every poll (even if we cannot read stdin this frame) so menus
    # are not stuck with a pending key and KEYDOWN/KEYUP stay on separate pump batches.
    _flush_pending_keyup()

    global _logged_not_tty
    if sys.stdin.isatty():
        _ensure_tty_cbreak()
    elif _trace_stdin_enabled() and not _logged_not_tty:
        _logged_not_tty = True
        _stdin_keys_logger.info(
            "stdin is not a TTY; reading without cbreak (IDE terminals may line-buffer keys)"
        )

    import select

    try:
        r, _, _ = select.select([sys.stdin], [], [], 0)
    except (ValueError, OSError):
        return
    if not r:
        return
    try:
        chunk = os.read(sys.stdin.fileno(), 4096)
    except (BlockingIOError, OSError):
        return
    if not chunk:
        return
    if _trace_stdin_enabled():
        _stdin_keys_logger.info("stdin read %d byte(s)", len(chunk))
    _stdin_buf.extend(chunk)
    _consume_buffer()


def _flush_pending_keyup() -> None:
    global _pending_keyup_key
    if _pending_keyup_key is None:
        return
    import pygame
    from pygame.event import Event

    k = _pending_keyup_key
    _pending_keyup_key = None
    pygame.event.post(Event(pygame.KEYUP, key=k))


def _emit_key(pygame, key) -> None:
    global _pending_keyup_key
    from pygame.event import Event

    if _pending_keyup_key is not None:
        pygame.event.post(Event(pygame.KEYUP, key=_pending_keyup_key))
    pygame.event.post(Event(pygame.KEYDOWN, key=key))
    _pending_keyup_key = key


def _consume_buffer() -> None:
    import pygame
    from pygame.constants import K_DOWN, K_LEFT, K_RETURN, K_RIGHT, K_UP

    patterns = [
        (b"\x1b[A", K_UP),
        (b"\x1b[B", K_DOWN),
        (b"\x1b[C", K_RIGHT),
        (b"\x1b[D", K_LEFT),
        (b"\x1bOA", K_UP),
        (b"\x1bOB", K_DOWN),
        (b"\x1bOC", K_RIGHT),
        (b"\x1bOD", K_LEFT),
    ]
    while _stdin_buf:
        if _stdin_buf[0:1] in (b"\r", b"\n"):
            _emit_key(pygame, K_RETURN)
            del _stdin_buf[0]
            continue
        matched = False
        for prefix, key in patterns:
            if _stdin_buf.startswith(prefix):
                _emit_key(pygame, key)
                del _stdin_buf[: len(prefix)]
                matched = True
                break
        if matched:
            continue
        if _stdin_buf.startswith(b"\x1b") and len(_stdin_buf) < 3:
            break
        del _stdin_buf[0]
    if len(_stdin_buf) > 256:
        _stdin_buf.clear()
