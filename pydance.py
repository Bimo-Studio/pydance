#!/usr/bin/env python
import logging

logger = logging.getLogger(__name__)

# pydance - a dancing game written in Python


import os
import sys
from getopt import getopt

from i18n import _

VERSION = "1.1.0"

from i18n import *


# fuck you, Python.
def print_help():
    print()
    print(_("Usage: %s [options]") % sys.argv[0])
    print(_(" -h, --help         display this help text and exit"))
    print(_(" -v, --version      display the version and exit"))
    print(_(" -f, --filename     load and play a step file"))
    print(_(" -m, --mode         the mode to play the file in (default SINGLE)"))
    print(_(" -d, --difficulty   the difficult to play the file (default BASIC)"))
    raise SystemExit


def print_version():
    print(_("pydance %s by Joe Wreschnig, Brendan Becker, and others") % VERSION)
    print("pyddr-discuss@icculus.org - http://icculus.org/pyddr")
    raise SystemExit


if len(sys.argv) < 2:
    pass
elif sys.argv[1] in ["--help", "-h"]:
    print_help()
elif sys.argv[1] in ["--version", "-v"]:
    print_version()

# Don't import anything that initializes the joysticks or config until
# after we're (reasonably) sure no one wants --help or --version.
import log_config

log_config.configure()
import sdl_env

sdl_env.apply()
import pygame
from pygame.mixer import music

import colors
import courses
import dance2 as dance  # maintained game loop; replaces legacy dance.py
import games
import menudriver
import records
import ui
import util
from constants import *  # This needs to be here to set sys.path.
from error import ErrorMessage
from fileparsers import SongItem
from fontfx import TextProgress
from fonttheme import FontTheme


# Set our required display paramters. Currently, this is nothing
# strange on any platforms, but in the past and likely in the future
# some platforms need other flags.
def set_display_mode():
    try:
        flags = 0
        if mainconfig["fullscreen"]:
            flags |= FULLSCREEN
        screen = pygame.display.set_mode([640, 480], flags, 16)
    except Exception:
        logger.critical("display set_mode failed; pydance requires 16-bit display")
        raise SystemExit(_("E: Can't get a 16 bit display! pydance doesn't work in 8 bit mode."))
    return screen


# Load a single song (given the filename) and then play it on the
# given difficulty.
def play_and_quit(fn, mode, difficulty):
    print(_("Entering debug (play-and-quit) mode."))
    screen = set_display_mode()
    pygame.display.set_caption("pydance " + VERSION)
    pygame.mouse.set_visible(0)
    pc = games.GAMES[mode].players
    dance.play(screen, [(fn, [difficulty] * pc)], [player_config] * pc, game_config, mode)
    raise SystemExit


# Pass a list of files to a constructor (Ctr) that takes the filename
# as the first argument, and the args tuple as the rest.
def load_files(screen, files, type, Ctr, args):
    if len(files) == 0:
        return []

    screen.fill(colors.BLACK)
    pct = 0
    inc = 100.0 / len(files)
    # Remove duplicates (preserve order). Python 2's map(None, files, []) is not valid here.
    files = list(dict.fromkeys(files))
    objects = []
    message = _("Found %d %s. Loading...") % (len(files), _(type))
    pbar = TextProgress(FontTheme.loading_screen, message, colors.WHITE, colors.BLACK)
    r = pbar.render(0).get_rect()
    r.center = [320, 240]
    for f in files:
        try:
            objects.append(Ctr(*((f,) + args)))
        except RuntimeError as message:
            print(_("E:"), f)
            print(_("E:"), message)
            print()
        except Exception as message:
            print(_("E: Unknown error loading"), f)
            print(_("E:"), message)
            print(_("E: Please contact the developers (pyddr-devel@icculus.org)."))
            print()
        pct += inc
        img = pbar.render(pct)
        pygame.display.update(screen.blit(img, r))

    return objects


# Support fullscreen on Win32 / OS X?
if osname != "posix":
    pygame.display.toggle_fullscreen = set_display_mode
else:
    pass


# Actually start the program running.
def main():
    import resource_checks

    missing = resource_checks.verify_install_layout()
    if missing:
        logger.warning(
            "install check: %d required file(s) missing — UI or audio may fail",
            len(missing),
        )

    logger.info("starting pydance %s", VERSION)
    logger.debug("argv=%r", sys.argv)
    print("pydance", VERSION, "<pyddr-discuss@icculus.org> - irc.freenode.net/#pyddr")

    # Psyco was a Python 2-only JIT (http://psyco.sf.net); it does not exist for Python 3+.
    if mainconfig["usepsyco"] and sys.version_info < (3,):
        try:
            import psyco

            print(_("Psyco optimizing compiler found. Using psyco.full()."))
            psyco.full()
        except ImportError:
            print(_("W: Psyco optimizing compiler not found."))

    # default settings for play_and_quit.
    mode = "SINGLE"
    difficulty = "BASIC"
    test_file = None
    for opt, arg in getopt(
        sys.argv[1:],
        "hvf:d:m:",
        ["help", "version", "filename=", "difficulty=", "mode="],
    )[0]:
        if opt in ["-h", _("--help")]:
            print_help()
        elif opt in ["-v", _("--version")]:
            print_version()
        elif opt in ["-f", _("--filename")]:
            test_file = arg
        elif opt in ["-m", _("--mode")]:
            mode = arg
        elif opt in ["-d", _("--difficulty")]:
            difficulty = arg

    if test_file:
        play_and_quit(test_file, mode, difficulty)

    try:
        _main_after_cli()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception:
        logger.exception("fatal error in pydance main")
        surf = None
        try:
            if pygame.display.get_init():
                surf = pygame.display.get_surface()
        except Exception:
            pass
        if surf is not None:
            try:
                ErrorMessage(
                    surf,
                    _("An unexpected error occurred. See the log for details."),
                )
            except Exception:
                pass
        try:
            pygame.quit()
        except Exception:
            pass
        raise SystemExit(1)


def _scan_song_paths():
    """Walk songdir entries; print per-path OK/FAIL and a final summary."""
    song_list = []
    failed_paths = []
    patterns = ["*.dance", "*.sm", "*.dwi", "*/song.*"]
    for dir in mainconfig["songdir"].split(os.pathsep):
        print(_("Searching for songs in"), dir)
        root = os.path.abspath(os.path.expanduser(dir))
        if not os.path.isdir(root):
            msg = f"  FAILED: not a directory: {root}"
            print(msg)
            logger.warning(msg)
            failed_paths.append(dir)
            continue
        # Order matters for dedup inside util.find (see util.find docstring).
        found = util.find(dir, patterns, 1)
        song_list.extend(found)
        print(f"  OK: found {len(found)} matching file(s)")
    song_list = list(dict.fromkeys(song_list))
    status = "FAIL" if failed_paths else "PASS"
    extra = f" ({len(failed_paths)} path(s) skipped)" if failed_paths else ""
    print(f"Song search complete: {status} — {len(song_list)} unique file(s){extra}")
    logger.info(
        "song search %s: %d unique files, %d path(s) skipped",
        status,
        len(song_list),
        len(failed_paths),
    )
    return song_list


def _scan_course_paths():
    """Walk coursedir entries; print per-path OK/FAIL and a final summary."""
    course_list = []
    failed_paths = []
    for dir in mainconfig["coursedir"].split(os.pathsep):
        print(_("Searching for courses in"), dir)
        root = os.path.abspath(os.path.expanduser(dir))
        if not os.path.isdir(root):
            msg = f"  FAILED: not a directory: {root}"
            print(msg)
            logger.warning(msg)
            failed_paths.append(dir)
            continue
        found = util.find(dir, ["*.crs"], 0)
        course_list.extend(found)
        print(f"  OK: found {len(found)} matching file(s)")
    status = "FAIL" if failed_paths else "PASS"
    extra = f" ({len(failed_paths)} path(s) skipped)" if failed_paths else ""
    print(f"Course search complete: {status} — {len(course_list)} file(s){extra}")
    logger.info(
        "course search %s: %d files, %d path(s) skipped",
        status,
        len(course_list),
        len(failed_paths),
    )
    return course_list


def _main_after_cli():
    song_list = _scan_song_paths()
    course_list = _scan_course_paths()

    screen = set_display_mode()

    pygame.display.set_caption("pydance " + VERSION)
    pygame.mouse.set_visible(False)
    try:
        if os.path.exists("/usr/share/pixmaps/pydance.png"):
            icon = pygame.image.load("/usr/share/pixmaps/pydance.png")
        else:
            icon = pygame.image.load(os.path.join(pydance_path, "icon.png"))
        pygame.display.set_icon(icon)
    except Exception:
        pass

    music.load(os.path.join(sound_path, "menu.ogg"))
    music.play(4, 0.0)

    songs = load_files(screen, song_list, _("songs"), SongItem, (False,))

    # Construct the song and record dictionaries for courses. These are
    # necessary because courses identify songs by title and mix, rather
    # than filename. The recordkey dictionary is needed for player's
    # picks courses.
    song_dict = {}
    record_dict = {}
    for song in songs:
        mix = song.info["mix"].lower()
        title = song.info["title"].lower()
        if song.info["subtitle"]:
            title += " " + song.info["subtitle"].lower()
        if mix not in song_dict:
            song_dict[mix] = {}
        song_dict[mix][title] = song
        record_dict[song.info["recordkey"]] = song

    crs = load_files(
        screen, course_list, _("courses"), courses.CourseFile, (song_dict, record_dict)
    )
    crs.extend(courses.make_players(song_dict, record_dict))
    records.verify(record_dict)

    # Let the GC clean these up if it needs to.
    song_list = None
    course_list = None
    record_dict = None
    ui.ui.clear()

    if len(songs) < 1:
        ErrorMessage(
            screen,
            (
                _(
                    "You don't have any songs or step files. Check out "
                    "http://icculus.org/pyddr/get.php#songs "
                    "and download some free ones. "
                    "If you already have some, make sure they're in "
                )
            )
            + mainconfig["songdir"],
        )
        logger.critical("no songs found; exiting")
        raise SystemExit(
            _("You don't have any songs. Check http://icculus.org/pyddr/get.php#songs .")
        )

    menudriver.do(screen, (songs, crs, screen))

    # Clean up shit.
    music.stop()
    pygame.quit()
    mainconfig.update(game_config)
    mainconfig.update(player_config)
    mainconfig.write(os.path.join(rc_path, "pydance.cfg"))
    records.write()


if __name__ == "__main__":
    main()
