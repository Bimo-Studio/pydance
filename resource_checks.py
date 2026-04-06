"""Startup checks: log missing install assets and optional files.

Imported from pydance.main() after constants (paths, config) are ready.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# Paths relative to pydance install root; fatal for main menu if absent.
REQUIRED_INSTALL_FILES = (
    "sound/menu.ogg",
    "sound/clicked.ogg",
    "sound/move.ogg",
    "sound/back.ogg",
    "themes/font/default.cfg",
)

# Nice-to-have; game may still run with fallbacks.
OPTIONAL_INSTALL_FILES = (
    "icon.png",
    "CREDITS",
)


def verify_install_layout() -> list[str]:
    """Log missing files. Returns list of missing required paths (empty if OK)."""
    from constants import pydance_path

    missing: list[str] = []
    root = pydance_path
    for rel in REQUIRED_INSTALL_FILES:
        path = os.path.join(root, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            missing.append(path)
            logger.error("required install file missing: %s", path)

    for rel in OPTIONAL_INSTALL_FILES:
        path = os.path.join(root, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            logger.info("optional file not present: %s", path)

    return missing
