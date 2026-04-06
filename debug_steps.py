import logging

logger = logging.getLogger(__name__)

import os
import sys

import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))

sys.path.insert(0, os.getcwd())
import games
import steps
from fileparsers import SongItem

# Load the song
song = SongItem("songs/6jan.dance")
print(f"Song: {song.info['title']}")
print(f"Game modes available: {list(song.difficulty.keys())}")

# Check SINGLE mode steps
if "SINGLE" in song.steps:
    print(f"SINGLE mode difficulties: {list(song.steps['SINGLE'].keys())}")
    if "TRICK" in song.steps["SINGLE"]:
        trick_steps = song.steps["SINGLE"]["TRICK"]
        print(f"TRICK steps count: {len(trick_steps)}")
        print(f"First 10 steps: {trick_steps[:10]}")

        # Create a Steps object to see if it generates events
        # Create a mock player
        class MockPlayer:
            def __init__(self):
                self.target_bpm = None
                self.speed = 1.0
                self.transform = 0
                self.holds = 1
                self.size = 0
                self.jumps = 1
                self.secret_kind = 1
                self.colortype = 4
                self.scrollstyle = 0

        mock_player = MockPlayer()
        game = games.GAMES["SINGLE"]

        # Create Steps object
        step_obj = steps.Steps(song, "TRICK", mock_player, 0, None, "SINGLE", 0)
        print(f"Steps object created: total arrows={step_obj.totalarrows}")
        print(f"Events count: {len(step_obj.events)}")
        print("First 5 events:")
        for i, ev in enumerate(step_obj.events[:5]):
            print(f"  {i}: when={ev.when}, appear={ev.appear}, feet={ev.feet}")
else:
    print("SINGLE mode not found in steps")

pygame.quit()
