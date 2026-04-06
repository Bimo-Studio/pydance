import logging

logger = logging.getLogger(__name__)

import os
import sys

sys.path.insert(0, os.getcwd())

import games
from fileparsers import SongItem

# Load the song
song = SongItem("songs/6jan.dance")
print(f"Song: {song.info['title']}")


# Create a mock player for Steps initialization
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
        self.fade = 0


mock = MockPlayer()
game = games.GAMES["SINGLE"]

# Create Steps object for BASIC difficulty
import steps

step_obj = steps.Steps(song, "BASIC", mock, 0, None, "SINGLE", 0)

print(f"\nTotal events: {len(step_obj.events)}")
print(f"Total arrows: {step_obj.totalarrows}")

# Find events that have appear times (these become nevents)
print("\nEvents with appear times (will become scrolling arrows):")
count = 0
for i, ev in enumerate(step_obj.events):
    if ev.appear is not None and ev.appear > 0:
        print(f"  Event {i}: when={ev.when:.2f}, appear={ev.appear:.2f}, feet={ev.feet}")
        count += 1
        if count >= 10:
            print("  ...")
            break

if count == 0:
    print("  No events with appear times found!")
    print("\nFirst 5 events:")
    for i, ev in enumerate(step_obj.events[:5]):
        print(f"  Event {i}: when={ev.when}, appear={ev.appear}, feet={ev.feet}")
