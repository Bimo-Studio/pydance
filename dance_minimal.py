import logging

logger = logging.getLogger(__name__)

import os
import sys
import traceback

import pygame

# --- INIT ---
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Pydance Debug Build")
clock = pygame.time.Clock()

sys.path.insert(0, os.getcwd())

import games
import steps
from constants import *
from fileparsers import SongItem
from player import Player


# --- DEBUG HELPERS ---
def debug(msg):
    print(f"[DEBUG] {msg}", flush=True)


# --- SAFE BACKGROUND (no movie support) ---
def load_background(song):
    try:
        bg = pygame.image.load(song.background).convert()
        return pygame.transform.scale(bg, (640, 480))
    except Exception:
        debug("Failed to load background, using black")
        surf = pygame.Surface((640, 480))
        surf.fill((0, 0, 0))
        return surf


# --- MAIN DANCE LOOP (rewritten) ---
def dance(screen, songdata, players, game):
    background = load_background(songdata)
    screen.blit(background, (0, 0))
    pygame.display.update()

    # --- AUDIO ---
    try:
        songdata.init()
        songdata.play()
    except Exception:
        traceback.print_exc()
        debug("Audio failed → timing will break")

    for p in players:
        p.start_song()

    running = True
    start_ticks = pygame.time.get_ticks()

    while running:
        # --- TIMING ---
        curtime = (pygame.time.get_ticks() - start_ticks) / 1000.0
        debug(f"time={curtime:.3f}")

        # --- INPUT (RAW pygame, no ui layer) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                debug(f"KEYDOWN: {event.key}")

                if event.key == pygame.K_ESCAPE:
                    return False

                # crude mapping
                keymap = {
                    pygame.K_LEFT: "l",
                    pygame.K_RIGHT: "r",
                    pygame.K_UP: "u",
                    pygame.K_DOWN: "d",
                }

                if event.key in keymap:
                    players[0].handle_keydown((0, keymap[event.key]), curtime)

            if event.type == pygame.KEYUP:
                keymap = {
                    pygame.K_LEFT: "l",
                    pygame.K_RIGHT: "r",
                    pygame.K_UP: "u",
                    pygame.K_DOWN: "d",
                }

                if event.key in keymap:
                    players[0].handle_keyup((0, keymap[event.key]), curtime)

        # --- GAME LOGIC ---
        try:
            for p in players:
                p.get_next_events(songdata, curtime)

            # --- RENDER ---
            screen.blit(background, (0, 0))

            for p in players:
                p.game_loop(curtime, screen)

            pygame.display.update()

        except Exception:
            traceback.print_exc()
            debug("Game loop crashed")
            return False

        clock.tick(60)

    return False


# --- PLAY WRAPPER ---
def play(song_file):
    debug(f"Loading {song_file}")

    song = SongItem(song_file)
    songdata = steps.SongData(song, game_config)

    game = games.GAMES["SINGLE"]

    player = Player(0, player_config, game_config, game)
    player.set_song(song, "BASIC", songdata.lyricdisplay)

    debug("Starting dance loop")

    dance(screen, songdata, [player], game)

    debug("Finished")


# --- ENTRYPOINT ---
if __name__ == "__main__":
    try:
        play("songs/6jan.dance")
    except Exception:
        traceback.print_exc()
    finally:
        pygame.quit()
