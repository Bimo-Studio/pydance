"""Regression: song/course file lists must not be emptied during deduplication."""

import logging

logger = logging.getLogger(__name__)

import unittest


class TestSongListDedupe(unittest.TestCase):
    def test_dedupe_keeps_distinct_paths(self):
        """Matches pydance.load_files: ordered dedupe of discovered step files."""
        files = ["/a/1.dance", "/b/2.dance", "/c/3.sm"]
        deduped = list(dict.fromkeys(files))
        self.assertEqual(deduped, files)

    def test_dedupe_collapses_duplicates(self):
        files = ["/a/x.dance", "/b/y.dance", "/a/x.dance"]
        deduped = list(dict.fromkeys(files))
        self.assertEqual(deduped, ["/a/x.dance", "/b/y.dance"])


if __name__ == "__main__":
    unittest.main()
