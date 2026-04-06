"""Configure SDL environment before pygame/SDL init.

On macOS, SDL's Cocoa backend registers an NSApplication; in VS Code/Cursor
embedded terminals and some CI contexts that can abort the process (SIGABRT)
(``Cocoa_RegisterApp`` / ``abort()`` in the crash log).

Call :func:`apply` once before ``import pygame`` in each entrypoint.

``PYDANCE_ALLOW_WINDOW=1`` only applies outside IDE-embedded terminals: from
**Terminal.app** or **iTerm** it leaves the video driver unset so you get a real
window. From **Cursor/VS Code’s integrated terminal**, that flag is **ignored**
and SDL stays on the dummy driver so the process does not crash.

With the dummy driver, **keyboard/mouse events do not reach pygame** for gameplay;
constants logs a warning unless ``PYDANCE_SUPPRESS_HEADLESS_WARNING=1`` or pytest/CI.
"""

from __future__ import annotations

import logging
import os
import sys

logger = logging.getLogger(__name__)

_applied = False

# True after _force_headless_sdl() (dummy video); other code may consult this.
headless_sdl: bool = False


def _is_ide_embedded_terminal() -> bool:
    """True when stdout is likely Cursor/VS Code's integrated terminal on macOS."""
    term = (os.environ.get("TERM_PROGRAM") or "").lower()
    if term in ("vscode", "cursor", "cursor-editor"):
        return True
    return bool(os.environ.get("VSCODE_PID") or os.environ.get("CURSOR_TRACE_ID"))


def apply() -> None:
    """Set SDL_VIDEODRIVER/AUDIODRIVER for safe contexts; no-op after first call."""
    global _applied
    if _applied:
        return
    _applied = True

    if sys.platform != "darwin":
        return

    if "pytest" in sys.modules or (os.environ.get("CI", "").lower() in ("1", "true", "yes")):
        logger.info("headless SDL (pytest/CI) on macOS")
        _force_headless_sdl()
        return

    # Never open a real Cocoa SDL window from an IDE terminal: it can SIGABRT
    # (HIServices RegisterApplication) even if PYDANCE_ALLOW_WINDOW=1.
    if _is_ide_embedded_terminal():
        _force_headless_sdl()
        if os.environ.get("PYDANCE_ALLOW_WINDOW") == "1":
            logger.warning(
                "Ignoring PYDANCE_ALLOW_WINDOW=1 in an IDE embedded terminal on macOS "
                "(SDL Cocoa would abort). Use Terminal.app / iTerm for a real window, "
                "or run without this flag for dummy video here."
            )
        else:
            logger.info("headless SDL (IDE terminal on macOS)")
        return

    if os.environ.get("PYDANCE_ALLOW_WINDOW") == "1":
        logger.debug("PYDANCE_ALLOW_WINDOW=1: leaving SDL video driver unchanged")
        return


def _force_headless_sdl() -> None:
    global headless_sdl
    headless_sdl = True
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    logger.debug("SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy")
