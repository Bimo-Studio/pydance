import logging

logger = logging.getLogger(__name__)

import os
import sys

import pygame

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Pydance - Working Test")
clock = pygame.time.Clock()

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Import modules
import dance2 as dance
from constants import *
from fileparsers import SongItem

# Load a song
song_file = "songs/6jan.dance"
print(f"Loading {song_file}...")
try:
    song = SongItem(song_file)
    print(f"Song loaded: {song.info['title']}")

    # Setup for single player with BASIC difficulty
    configs = [player_config]
    songconf = game_config
    playmode = "SINGLE"
    difficulty = "BASIC"

    # Create playlist
    playlist = [(song_file, [difficulty])]

    print(f"\nPlaying: {song.info['title']} - {difficulty}")
    print("Press arrow keys to hit notes, ESC to exit")
    print("Waiting for game to start...\n")

    # Play the song
    dance.play(screen, playlist, configs, songconf, playmode)

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()

pygame.quit()
print("Done")
