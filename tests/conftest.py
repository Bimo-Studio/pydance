"""Pytest configuration: headless pygame for CI and coverage."""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
import warnings

logger = logging.getLogger(__name__)

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def _configure_logging_fallback() -> None:
    """Mirror log_config.configure() when ../log_config.py is not in the tree (uncommitted on a fork)."""
    level_name = os.environ.get("PYDANCE_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        root.addHandler(handler)
    root.setLevel(level)
    logging.captureWarnings(True)
    warnings.filterwarnings(
        "ignore",
        message=".*pkg_resources is deprecated as an API.*",
        category=UserWarning,
    )


def _load_log_config() -> None:
    """Load repo-root log_config.py by path so it works even if the package install omits it."""
    path = os.path.join(_project_root, "log_config.py")
    if not os.path.isfile(path):
        _configure_logging_fallback()
        logger.debug("log_config.py missing at %s; using conftest fallback", path)
        return
    spec = importlib.util.spec_from_file_location("pydance_log_config", path)
    if spec is None or spec.loader is None:
        _configure_logging_fallback()
        return
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.configure()


_load_log_config()

# Force dummy drivers for every test process. On macOS, SDL's Cocoa backend
# calls RegisterApplication / NSApplication during video init; without a real
# GUI session that can abort the interpreter (SIGABRT). setdefault() is wrong
# here because the shell or IDE may already set SDL_VIDEODRIVER (e.g. cocoa).
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

logger.debug("pytest SDL headless env applied")
