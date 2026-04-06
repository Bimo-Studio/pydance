import logging

logger = logging.getLogger(__name__)

import os
import sys

import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))

sys.path.insert(0, os.getcwd())
from constants import *

print("Current configuration:")
print(f"Scroll style: {player_config['scrollstyle']}")
print(f"Speed: {player_config['speed']}")
print(f"Game width: {games.GAMES['SINGLE'].width}")
print(f"Game dirs: {games.GAMES['SINGLE'].dirs}")

# Check if theme exists
import os

theme_path = "themes/gfx/64x64/default"
if os.path.exists(theme_path):
    print(f"Theme exists: {theme_path}")
    arrow_files = [f for f in os.listdir(theme_path) if f.startswith("arr_c_")]
    print(f"Arrow files found: {len(arrow_files)}")
else:
    print(f"Theme not found: {theme_path}")

pygame.quit()
