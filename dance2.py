"""
Gameplay loop for pydance. This module is the maintained entrypoint; the main
launcher imports it as ``dance`` (see pydance.py). Legacy dance.py is retained
only until the migration is finished.
"""

import logging

logger = logging.getLogger(__name__)

import os
import sys
import traceback

import log_config

log_config.configure()
import sdl_env

sdl_env.apply()
import pygame

pygame.init()

# Display is created by pydance.set_display_mode() or dance_minimal; avoid a stray
# set_mode at import time (wrong depth / double-init on some platforms).
screen = None

clock = pygame.time.Clock()

sys.path.insert(0, os.getcwd())

from pygame.mixer import music

import fileparsers
import games
import steps
from constants import *
from player import Player

# ---------------- DEBUG ----------------

DEBUG = True


def debug(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}", flush=True)


# ---------------- SAFE BACKGROUND ----------------


def load_background(song):
    try:
        if hasattr(song, "background") and song.background:
            bg = pygame.image.load(song.background).convert()
            return pygame.transform.scale(bg, (640, 480))
    except Exception:
        traceback.print_exc()

    surf = pygame.Surface((640, 480))
    surf.fill((0, 0, 0))
    return surf


# ---------------- MAIN DANCE LOOP ----------------


def dance(screen, song, players, prevscr, ready_go, game):

    debug("Entering dance()")

    # Static background surface for Group.clear() (same pattern as legacy dance.py).
    background = load_background(song)
    screen.blit(background, (0, 0))
    pygame.display.update()

    # Initialize song playback
    try:
        song.init()
        song.play()
    except Exception:
        traceback.print_exc()
        debug("Song playback failed")

    for p in players:
        p.start_song()

    start_ticks = pygame.time.get_ticks()

    autofail = mainconfig.get("autofail", False)

    while True:
        # --- TIMING ---
        pos = music.get_pos()
        if pos == -1:
            curtime = (pygame.time.get_ticks() - start_ticks) / 1000.0
        else:
            curtime = pos / 1000.0

        # --- GAME STATE ---
        songFailed = False

        if autofail:
            for p in players:
                if not p.lifebar.gameover:
                    songFailed = False
                    break
            else:
                songFailed = True

        if songFailed:
            debug("Autofail triggered")
            song.kill()
            return True

        try:
            # Same order as legacy dance.py: sync steps before input so fx_data exists
            # and handle_keydown appends are not wiped by get_next_events.
            for p in players:
                p.get_next_events(song, curtime)

            if song.is_over():
                debug("Song ended")
                break

            # --- INPUT (after get_next_events) ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

                if event.type == pygame.KEYDOWN:
                    debug(f"KEYDOWN {event.key}")

                    if event.key == pygame.K_ESCAPE:
                        return False

                    for p in players:
                        if event.key == pygame.K_LEFT:
                            p.handle_keydown((p.pid, "l"), curtime)
                        elif event.key == pygame.K_RIGHT:
                            p.handle_keydown((p.pid, "r"), curtime)
                        elif event.key == pygame.K_UP:
                            p.handle_keydown((p.pid, "u"), curtime)
                        elif event.key == pygame.K_DOWN:
                            p.handle_keydown((p.pid, "d"), curtime)

                if event.type == pygame.KEYUP:
                    for p in players:
                        if event.key == pygame.K_LEFT:
                            p.handle_keyup((p.pid, "l"), curtime)
                        elif event.key == pygame.K_RIGHT:
                            p.handle_keyup((p.pid, "r"), curtime)
                        elif event.key == pygame.K_UP:
                            p.handle_keyup((p.pid, "u"), curtime)
                        elif event.key == pygame.K_DOWN:
                            p.handle_keyup((p.pid, "d"), curtime)

            rectlist = []

            for p in players:
                rectlist.extend(p.game_loop(curtime, screen))

            # pygame.display.update([]) updates nothing; fall back to full flip.
            if rectlist:
                pygame.display.update(rectlist)
            else:
                pygame.display.update()

            for p in players:
                p.clear_sprites(screen, background)

        except Exception:
            traceback.print_exc()
            debug("Crash inside game loop")
            return True

        clock.tick(60)

    # --- END OF SONG ---
    debug("Exiting dance loop")

    return False


# ---------------- PLAY ----------------


def play(screen, playlist, configs, songconf, playmode):

    game = games.GAMES[playmode]

    players = []
    for pid in range(len(configs)):
        players.append(Player(pid, configs[pid], songconf, game))

    first = True
    songs_played = 0

    for songfn, diff in playlist:
        debug(f"Loading song: {songfn}")

        try:
            current_song = fileparsers.SongItem(songfn)
        except Exception:
            traceback.print_exc()
            continue

        songs_played += 1

        prevscr = pygame.transform.scale(screen, (640, 480))
        songdata = steps.SongData(current_song, songconf)

        # assign song to players
        for pid, player in enumerate(players):
            player.set_song(current_song, diff[pid], songdata.lyricdisplay)

        print("Playing", songfn)
        print(songdata.title, "by", songdata.artist)

        failed = dance(screen, songdata, players, prevscr, first, game)

        first = False

        if failed:
            debug("Dance() reported failure")
            break

        if any(p.escaped for p in players):
            break

    # grading
    if mainconfig.get("grading", False) and songs_played == 1:
        try:
            import gradescreen

            gradescreen.GradingScreen(screen, players, songdata.banner)
        except Exception:
            traceback.print_exc()

    # records
    if songs_played == 1 and not players[0].escaped:
        try:
            import records

            for p in players:
                if not p.failed:
                    records.add(
                        current_song.info["recordkey"],
                        diff[p.pid],
                        playmode,
                        p.grade.rank(),
                        " ",
                    )
                else:
                    records.add(
                        current_song.info["recordkey"],
                        diff[p.pid],
                        playmode,
                        -2,
                        " ",
                    )
        except Exception:
            traceback.print_exc()


# ---------------- ENTRY ----------------


if __name__ == "__main__":
    import os

    # One-shot song test: PYDANCE_QUICK_PLAY=1 python dance2.py
    if os.environ.get("PYDANCE_QUICK_PLAY"):
        try:
            screen = pygame.display.set_mode([640, 480], 0, 16)
            pygame.display.set_caption("Pydance Debug")
            play(
                screen,
                [("songs/6jan.dance", ["BASIC"])],
                [player_config],
                game_config,
                "SINGLE",
            )
        except Exception:
            traceback.print_exc()
        finally:
            pygame.quit()
            debug("Quit cleanly")
    else:
        import pydance

        pydance.main()
