import logging

logger = logging.getLogger(__name__)

import os
import sys

import pygame

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Pydance Test")
clock = pygame.time.Clock()

# Add paths
sys.path.insert(0, os.getcwd())

# Import needed modules
import dance2 as dance
from constants import *
from fileparsers import SongItem

# Load a song
song_file = "songs/6jan.dance"
print(f"Loading {song_file}...")
song = SongItem(song_file)

# Setup for single player
configs = [player_config]
songconf = game_config
playmode = "SINGLE"

# Create playlist with BASIC difficulty (easier)
difficulty = "BASIC"
playlist = [(song_file, [difficulty])]

print(f"Starting song: {song.info['title']} - {difficulty}")
print("Use arrow keys to hit the notes!")
print("Press ESC to exit")

# Play the song
try:
    dance.play(screen, playlist, configs, songconf, playmode)
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()

pygame.quit()
