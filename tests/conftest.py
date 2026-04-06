"""Pytest configuration: headless pygame for CI and coverage."""

import logging
import os

import log_config

log_config.configure()

logger = logging.getLogger(__name__)

# Force dummy drivers for every test process. On macOS, SDL's Cocoa backend
# calls RegisterApplication / NSApplication during video init; without a real
# GUI session that can abort the interpreter (SIGABRT). setdefault() is wrong
# here because the shell or IDE may already set SDL_VIDEODRIVER (e.g. cocoa).
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

logger.debug("pytest SDL headless env applied")
