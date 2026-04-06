"""Pytest configuration: headless pygame for CI and coverage."""

import logging
import os
import sys

# Repo root must be importable before log_config (same pattern as test_resource_checks).
# Relying only on pip -e + setuptools py-modules or pytest's pythonpath is brittle on CI.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

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
