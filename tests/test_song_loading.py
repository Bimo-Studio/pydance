import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSongLoading(unittest.TestCase):
    def setUp(self):
        self.song_file = "songs/6jan.dance"
        if not os.path.isfile(self.song_file):
            self.skipTest("Song file not found: %s" % self.song_file)

    def test_load_song(self):
        """Test that a .dance file can be loaded"""
        from fileparsers import SongItem

        song = SongItem(self.song_file)
        self.assertIsNotNone(song)
        self.assertIn("title", song.info)
        print(f"Loaded song: {song.info['title']}")

    def test_song_has_steps(self):
        """Test that loaded song has steps for SINGLE mode"""
        from fileparsers import SongItem

        song = SongItem(self.song_file)
        self.assertIn("SINGLE", song.steps)
        self.assertIn("BASIC", song.steps["SINGLE"])
        steps = song.steps["SINGLE"]["BASIC"]
        self.assertGreater(len(steps), 0)
        print(f"Found {len(steps)} steps for BASIC difficulty")


if __name__ == "__main__":
    unittest.main()
