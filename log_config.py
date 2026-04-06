"""Central logging setup for pydance (stdlib ``logging``; levels like Log4j: DEBUG, INFO, WARNING, ERROR, CRITICAL).

Control verbosity with the environment variable ``PYDANCE_LOG_LEVEL`` (default ``INFO``).
Example: ``PYDANCE_LOG_LEVEL=DEBUG python pydance.py``

**Scrolling step-arrow trace** (chart → spawn timing arrows → draw): set ``PYDANCE_TRACE_STEPS=1``
(logger ``pydance.steps_trace``). Labels distinguish **scrolling** timing arrows from the static receptor row.

**Menu / keyboard poll trace**: ``PYDANCE_TRACE_MENU_INPUT=1`` logs pygame drain + semantic buffer sizes and each
``poll`` result (logger ``pydance.menu_input``). Also enables ``pydance.stdin_keys`` one-shot notice when stdin is not a
TTY, and per-read byte counts. Or set ``PYDANCE_TRACE_STDIN_KEYS=1`` for stdin logging only.

**Differentiated loggers** (same hierarchy as Log4j category names): use ``logging.getLogger(__name__)``
per module (e.g. ``[ui]``, ``[menus]``). For **raw input tracing**, use logger ``pydance.input`` — enable with::

    PYDANCE_LOG_LEVEL=DEBUG PYDANCE_DEBUG_INPUT=1 python dance.py

That prints ``KEYDOWN`` / ``MOUSEBUTTONDOWN`` lines and non-``PASS`` ``poll -> (...)`` semantic events.

Each module should use::

    import logging

    logger = logging.getLogger(__name__)
"""

from __future__ import annotations

import logging
import os
import sys
import warnings

_configured = False


def configure() -> None:
    """Attach a stderr handler to the root logger once; respect ``PYDANCE_LOG_LEVEL``."""
    global _configured
    if _configured:
        return
    _configured = True

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
    # Pygame still imports pkg_resources; setuptools emits a noisy UserWarning even when pinned.
    warnings.filterwarnings(
        "ignore",
        message=".*pkg_resources is deprecated as an API.*",
        category=UserWarning,
    )

    log = logging.getLogger(__name__)
    log.debug("logging configured at level %s", logging.getLevelName(level))
