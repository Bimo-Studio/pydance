#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)

import sys
import traceback

try:
    import dance2 as dance
except Exception as e:
    print("Error importing dance2:", e)
    traceback.print_exc()
    sys.exit(1)

try:
    # If dance2 has a main function, call it
    if hasattr(dance, "main"):
        dance.main()
    elif hasattr(dance, "play"):
        # Initialize pygame and run
        import pygame

        pygame.init()
        screen = pygame.display.set_mode((640, 480))
        # You might need to provide appropriate parameters here
        print("Game initialized but may need proper setup")
    else:
        print("No main function found in dance2.py")
except Exception as e:
    print("Error running dance:", e)
    traceback.print_exc()
