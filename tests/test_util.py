"""Unit tests for util.py (pure helpers)."""

import logging
import uuid

logger = logging.getLogger(__name__)

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import util


class TestUtil(unittest.TestCase):
    def test_to_real_time(self):
        self.assertAlmostEqual(util.toRealTime(120, 4), 0.5)

    def test_find_subtitle(self):
        t, s = util.find_subtitle("Song [mix]")
        self.assertEqual(s, "[mix]")
        t2, s2 = util.find_subtitle("Plain")
        self.assertEqual(s2, "")

    def test_difficulty_sort_key(self):
        self.assertLess(util.difficulty_sort_key("BEGINNER"), util.difficulty_sort_key("HARD"))
        self.assertEqual(util.difficulty_sort_key("UNKNOWN"), len(util.DIFFICULTY_LIST))

    def test_difficulty_sort_known(self):
        self.assertLess(util.difficulty_sort("BASIC", "HARD"), 0)
        self.assertEqual(util.difficulty_sort("BASIC", "BASIC"), 0)

    def test_find_files(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "a.dance"), "w").close()
            open(os.path.join(d, "b.txt"), "w").close()
            sub = os.path.join(d, "sub")
            os.mkdir(sub)
            open(os.path.join(sub, "c.dance"), "w").close()
            hits = util.find(d, ["*.dance"], 0)
            self.assertEqual(len(hits), 2)

    def test_find_skips_missing_directory_with_warning(self):
        bad = os.path.join(tempfile.gettempdir(), "pydance_nonexistent_" + uuid.uuid4().hex)
        with self.assertLogs("util", level="WARNING") as cm:
            hits = util.find(bad, ["*.dance"], 0)
        self.assertEqual(hits, [])
        self.assertTrue(any("skipping" in m for m in cm.output))

    def test_find_dedup_prefers_first_pattern(self):
        with tempfile.TemporaryDirectory() as d:
            base = os.path.join(d, "song")
            open(base + ".dance", "w").close()
            open(base + ".sm", "w").close()
            hits = util.find(d, ["*.sm", "*.dance"], 1)
            self.assertEqual(len(hits), 1)

    def test_titlecase_basic(self):
        out = util.titlecase("hello world")
        self.assertTrue(len(out) > 0)


if __name__ == "__main__":
    unittest.main()
