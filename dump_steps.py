import logging

logger = logging.getLogger(__name__)

import os
import sys

sys.path.insert(0, os.getcwd())

from fileparsers import SongItem

song = SongItem("songs/6jan.dance")
steps = song.steps["SINGLE"]["TRICK"]

print(f"Song: {song.info['title']}")
print(f"Number of steps: {len(steps)}")
print("\nFirst 20 steps:")
for i, step in enumerate(steps[:20]):
    print(f"{i}: {step}")
