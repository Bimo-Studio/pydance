"""
If the repo ships (or you add) sample charts under songs/, ensure util.find sees them.
Skips when songs/ is missing or empty (e.g. minimal clone).
"""

import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSongsDirSmoke(unittest.TestCase):
    def test_sample_dance_files_discovered_when_present(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        songs = os.path.join(root, "songs")
        if not os.path.isdir(songs):
            self.skipTest("no songs/ directory")
        import util

        hits = util.find(songs, ["*.dance", "*.sm", "*.dwi", "*/song.*"], 1)
        if not hits:
            self.skipTest("songs/ has no .dance/.sm/.dwi (add samples from icculus.org/pyddr)")
        self.assertTrue(any(h.lower().endswith(".dance") for h in hits))


if __name__ == "__main__":
    unittest.main()
