import logging

logger = logging.getLogger(__name__)

import gettext
import os
import sys

__all__ = ["_"]


def _localedirs() -> list[str]:
    """Search paths for gettext ``pydance.mo`` (``<dir>/<lang>/LC_MESSAGES/pydance.mo``)."""
    base = os.path.dirname(os.path.abspath(__file__))
    argv0 = os.path.abspath(sys.argv[0])
    mydir = os.path.dirname(argv0)

    dirs: list[str] = [
        os.path.join(base, "mo"),
        "/usr/share/locale",
        "/usr/local/share/locale",
        os.path.join(mydir, "mo"),
        mydir + "/../../locale",
        mydir + "/../share/locale",
    ]
    seen: set[str] = set()
    out: list[str] = []
    for d in dirs:
        if os.path.isdir(d) and d not in seen:
            seen.add(d)
            out.append(d)
    return out


def _load_translation() -> gettext.NullTranslations | gettext.GNUTranslations:
    """Return the best-available translation; fall back to untranslated strings."""
    last: OSError | None = None
    for localedir in _localedirs():
        try:
            t = gettext.translation("pydance", localedir, fallback=False)
        except OSError as e:
            last = e
            continue
        logger.info("gettext catalog loaded for pydance from %s", localedir)
        return t

    if last is not None:
        logger.debug("no pydance.mo in search path (%s); using untranslated msgids", last)
    else:
        logger.debug("no locale directories found; using untranslated msgids")
    return gettext.NullTranslations()


_lang = _load_translation()
_lang.install()
_ = _lang.gettext
