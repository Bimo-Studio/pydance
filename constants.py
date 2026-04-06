# Constants used in the game and some simple initialization routines
# This file should be kept as small as possible, probably. (But I seem
# to be failing at doing that.)


import locale
import logging
import os
import sys

import log_config

log_config.configure()

import sdl_env

sdl_env.apply()

import pygame
from pygame.locals import *  # noqa: F401,F403

import colors
import config
import games

maketrans = str.maketrans

from builtins import range

from i18n import *  # noqa: F401,F403

logger = logging.getLogger(__name__)

VERSION = "1.1.0"

# Menu / navigation UI: black bold (bold applied in fonttheme for listed purposes)
MENU_NAV_TEXT = list(colors.BLACK)
MENU_NAV_SHADOW_LIGHT = [235, 235, 235]

STDOUT_ENCODING = "UTF-8"

if sys.stdout.encoding not in (None, ""):
    STDOUT_ENCODING = sys.stdout.encoding

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error as exc:
    logger.warning("could not set locale LC_ALL: %s", exc)

# Detect the name of the OS - Mac OS X is not really UNIX.
osname = None
if os.name == "nt":
    osname = "win32"
elif os.name == "posix":
    if os.path.islink("/System/Library/CoreServices/WindowServer"):
        osname = "macosx"
    elif "HOME" in os.environ:
        osname = "posix"
else:
    logger.critical(
        "unsupported platform: os.name=%r (need win32, macosx, or posix with HOME)",
        os.name,
    )
    raise SystemExit(
        "Your platform is not supported by pydance. In particular, it\n"
        + "doesn't seem to be Win32, Mac OS X, or a Unix that sets $HOME."
    )

# Find out our real directory - resolve symlinks, etc
# Get the directory of this file (constants.py)
logger.debug("detected osname=%s", osname)
pydance_path = os.path.dirname(os.path.abspath(__file__))
if osname == "posix" and os.path.islink(pydance_path):
    pydance_path = os.path.realpath(pydance_path)
sys.path.insert(0, pydance_path)

if os.path.exists(os.path.join(pydance_path, "pydance.zip")):
    logger.info("adding pydance.zip to sys.path")
    sys.path.insert(0, os.path.join(pydance_path, "pydance.zip"))

logger.debug("pydance_path=%s rc_path will follow config", pydance_path)

# Set up some names for commonly referenced directories
image_path = os.path.join(pydance_path, "images")
sound_path = os.path.join(pydance_path, "sound")

# Set a name for our savable resource directory
rc_path = None
if osname == "posix":
    rc_path = os.path.join(os.environ["HOME"], ".pydance")
elif osname == "macosx":
    rc_path = os.path.join(os.environ["HOME"], "Library", "Preferences", "pydance")
elif osname == "win32":
    rc_path = "."

assert rc_path is not None

if not os.path.isdir(rc_path):
    logger.info("creating rc_path directory: %s", rc_path)
    os.mkdir(rc_path)

search_paths = (pydance_path, rc_path)

input_d_path = os.path.join(rc_path, "input.d")
if not os.path.isdir(input_d_path):
    logger.info("creating input.d directory: %s", input_d_path)
    os.mkdir(input_d_path)

if not sys.stdout.isatty():
    try:
        _log = open(os.path.join(rc_path, "pydance.log"), "w")
        sys.stdout = _log
        sys.stderr = sys.stdout
        logger.info("redirecting stdout/stderr to %s", os.path.join(rc_path, "pydance.log"))
    except OSError as exc:
        logger.warning("could not open pydance.log for redirect: %s", exc)


# SDL_mixer is the bane of my existance.
if osname == "posix":  # We need to force stereo in many cases.
    try:
        pygame.mixer.pre_init(44100, -16, 2)
    except pygame.error as exc:
        logger.warning("mixer pre_init (stereo) failed: %s", exc)

# Set up the configuration file
default_conf = {
    "fonttheme": "default",
    "djtheme": "djenzay",
    "songdir": os.pathsep.join(
        [os.path.join(rc_path, "songs"), os.path.join(pydance_path, "songs")]
    ),
    "coursedir": os.pathsep.join(
        [os.path.join(rc_path, "courses"), os.path.join(pydance_path, "courses")]
    ),
    "stickycombo": 1,
    "lowestcombo": 4,
    "stickyjudge": 1,
    "lyriccolor": "cyan/aqua",
    "onboardaudio": 0,
    "masteroffset": 0,
    "explodestyle": 3,
    "vesacompat": 0,
    "fullscreen": 0,
    "sortmode": 0,
    "folders": 1,
    "previewmusic": 1,
    "showbackground": 1,
    "bgbrightness": 127,
    "gratuitous": 1,
    "assist": 0,
    "fpsdisplay": 1,
    "showlyrics": 1,
    "showcombo": 1,
    "autofail": 1,
    "animation": 1,
    "grading": 1,
    "saveinput": 1,
    "strobe": 0,
    "usepsyco": 0,  # Psyco: Python 2 JIT only; ignored on Python 3
    "autogen": 1,
    "centerconfirm": 1,
    "songinfoscreen": 1,
    # Player config
    "spin": 0,
    "accel": 0,
    "transform": 0,
    "scale": 1,
    "speed": 1.0,
    "fade": 0,
    "size": 0,
    "dark": 0,
    "jumps": 1,
    "holds": 1,
    "colortype": 4,
    "scrollstyle": 0,
    # Game options
    "battle": 0,
    "scoring": 0,
    "combo": 0,
    "grade": 0,
    "judge": 0,
    "judgescale": 1.0,
    "life": 1.0,
    "secret": 1,
    "lifebar": 0,
    "onilives": 3,
    "audiosync": 1,
}

for game in games.GAMES.values():
    default_conf["%s-theme" % game.theme] = game.theme_default

mainconfig = config.Config(default_conf)

if osname == "posix":
    mainconfig.load("/etc/pydance.cfg", True)
elif osname == "macosx":
    mainconfig.load("/Library/Preferences/pydance/pydance.cfg", True)

mainconfig.load("pydance.cfg")
mainconfig.load(os.path.join(rc_path, "pydance.cfg"))
mainconfig["sortmode"] %= 6


def _prepend_bundled_datadir_if_missing(key, subdir):
    """If pydance.cfg replaced e.g. songdir with system paths only, still search bundled data/."""
    bundled = os.path.join(pydance_path, subdir)
    if not os.path.isdir(bundled):
        return
    abs_b = os.path.abspath(bundled)
    parts = [p.strip() for p in mainconfig[key].split(os.pathsep) if p.strip()]
    norms = [os.path.abspath(os.path.expanduser(p)) for p in parts]
    if abs_b not in norms:
        mainconfig[key] = bundled + os.pathsep + mainconfig[key]
        logger.debug("prepended bundled %s: %s", key, bundled)


_prepend_bundled_datadir_if_missing("songdir", "songs")
_prepend_bundled_datadir_if_missing("coursedir", "courses")


def _ensure_data_directories():
    """Create song/course dirs from config if missing (empty dirs are fine)."""
    for key in ("songdir", "coursedir"):
        for part in mainconfig[key].split(os.pathsep):
            p = os.path.abspath(os.path.expanduser(part.strip()))
            if not p:
                continue
            if not os.path.isdir(p):
                try:
                    os.makedirs(p, exist_ok=True)
                    logger.info("created missing data directory: %s", p)
                except OSError as exc:
                    logger.warning("could not create data directory %s: %s", p, exc)


_ensure_data_directories()

player_config = {
    k: mainconfig[k]
    for k in [
        "spin",
        "accel",
        "transform",
        "scale",
        "speed",
        "fade",
        "size",
        "dark",
        "jumps",
        "holds",
        "colortype",
        "scrollstyle",
    ]
}

game_config = {
    k: mainconfig[k]
    for k in [
        "battle",
        "scoring",
        "combo",
        "grade",
        "judge",
        "judgescale",
        "life",
        "secret",
        "lifebar",
        "onilives",
        "audiosync",
    ]
}


# The list of options that are safe to change between songs on a
# playlist
# Each tuple has the following entries:
# 0. Option "key", like the one used in the options.OPTIONS dictionary
# 1. A dictionary of option values that require special displaying:
#    the key is the value of the option and the value is a string that
#    should be shown on the song info screen if that option is
#    selected.  If there is no key for a particular option, the string
#    that is displayed for that value in the option menu is used.
#    E.g. for the "jumps" option, value 0 will map to "No Jumps" while
#    value 2 is not in the dictionary so will display "Wide".

changeable_between = [
    ("speed", {}),
    ("transform", {}),
    ("size", {}),
    ("fade", {}),
    ("accel", {}),
    ("scale", {}),
    ("scrollstyle", {}),
    ("jumps", {0: "No Jumps"}),
    ("spin", {1: "Spin"}),
    ("colortype", {}),
    ("dark", {1: "Dark"}),
    ("holds", {0: "No Holds"}),
]


pygame.init()
pygame.event.set_blocked(list(range(pygame.NUMEVENTS)))
pygame.event.set_allowed(
    (
        pygame.KEYUP,
        pygame.KEYDOWN,
        pygame.MOUSEBUTTONDOWN,
        pygame.MOUSEBUTTONUP,
        pygame.JOYBUTTONUP,
        pygame.JOYBUTTONDOWN,
        pygame.QUIT,
        pygame.JOYAXISMOTION,
        pygame.JOYHATMOTION,
    )
)

if (
    os.environ.get("SDL_VIDEODRIVER") == "dummy"
    and "pytest" not in sys.modules
    and os.environ.get("CI", "").lower() not in ("1", "true", "yes")
    and os.environ.get("PYDANCE_SUPPRESS_HEADLESS_WARNING") != "1"
):
    logger.warning(
        "SDL dummy video driver is active (e.g. Cursor/VS Code terminal on macOS). "
        "Menus try terminal arrow keys via stdin_keys; for full SDL input run from "
        "Terminal.app or iTerm outside the editor (or set PYDANCE_ALLOW_WINDOW=1 there)."
    )

if (
    "pytest" not in sys.modules
    and os.environ.get("CI", "").lower() not in ("1", "true", "yes")
):
    logger.info(
        "SDL headless=%s SDL_VIDEODRIVER=%r (arrow keys: %s)",
        sdl_env.headless_sdl,
        os.environ.get("SDL_VIDEODRIVER"),
        "stdin_keys + pygame queue" if sdl_env.headless_sdl else "click the game window so it has focus",
    )

# The different colors pydance uses for difficulties in the UI.
DIFF_COLORS = {
    "BEGINNER": colors.color[_("white")],
    "LIGHT": colors.color[_("orange")],
    "EASY": colors.color[_("orange")],
    "BASIC": colors.color[_("orange")],
    "STANDARD": colors.color[_("red")],
    "STANDER": colors.color[_("red")],  # Shit you not, 3 people.
    "TRICK": colors.color[_("red")],
    "MEDIUM": colors.color[_("red")],
    "DOUBLE": colors.color[_("red")],
    "ANOTHER": colors.color[_("red")],
    "PARA": colors.color[_("blue")],
    "NORMAL": colors.color[_("red")],
    "MANIAC": colors.color[_("green")],
    "HARD": colors.color[_("green")],
    "HEAVY": colors.color[_("green")],
    "HARDCORE": colors.color[_("purple")],
    "SMANIAC": colors.color[_("purple")],
    "S-MANIAC": colors.color[_("purple")],  # Very common typo
    "CHALLENGE": colors.color[_("purple")],
    "CRAZY": colors.color[_("purple")],
    "EXPERT": colors.color[_("purple")],
}

ZERO_ALPHA = str.maketrans(
    "".join(
        [chr(x) for x in list(range(ord("a"), ord("z") + 1)) + list(range(ord("A"), ord("Z") + 1))]
    ),
    "0" * 26 * 2,
)

# Initialize font theme after mainconfig is ready
from fonttheme import init_fonttheme

init_fonttheme()

logger.info("pygame initialized; constants ready (version %s)", VERSION)
logger.debug("event filter: only keyboard, joystick, quit allowed")
