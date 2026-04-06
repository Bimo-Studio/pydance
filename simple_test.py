import logging

logger = logging.getLogger(__name__)

import os
import sys

import pygame

print("Step 1: Initializing pygame...")
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Test")

print("Step 2: Importing modules...")
sys.path.insert(0, os.getcwd())
import dance2 as dance
from constants import *
from fileparsers import SongItem

print("Step 3: Loading song...")
song = SongItem("songs/6jan.dance")
print(f"Song loaded: {song.info['title']}")

print("Step 4: Setting up players...")
configs = [player_config]
songconf = game_config
game_mode = "SINGLE"
diff = "TRICK"

print("Step 5: Creating playlist...")
playlist = [("songs/6jan.dance", [diff])]

print("Step 6: Starting dance...")
try:
    dance.play(screen, playlist, configs, songconf, game_mode)
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()

print("Step 7: Done")
pygame.quit()
