import logging

logger = logging.getLogger(__name__)

import os
import sys

import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))

sys.path.insert(0, os.getcwd())
import dance2 as dance
from constants import *
from fileparsers import SongItem

song = SongItem("songs/6jan.dance")
configs = [player_config]
songconf = game_config

# Use BASIC instead of TRICK
playlist = [("songs/6jan.dance", ["BASIC"])]

print("Starting with BASIC difficulty...")
dance.play(screen, playlist, configs, songconf, "SINGLE")
pygame.quit()
