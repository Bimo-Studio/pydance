#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)

import os
import sys

# Change to the directory containing this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Import and run the game
from constants import pydance_path, search_paths

print(f"pydance_path: {pydance_path}")
print(f"search_paths: {search_paths}")

# Check if themes can be found
import games
from gfxtheme import GfxTheme

game = games.GAMES["SINGLE"]
try:
    theme = GfxTheme("default", 0, game)
    print(f"Theme loaded successfully from: {theme.path}")

    # Now run the actual game
    from simple_working_test import main

    main()
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
