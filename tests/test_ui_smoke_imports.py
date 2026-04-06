"""
Smoke: core packages import without pulling in ui (full menu stack imports ui at
module load and can hang headless CI). Sort keys for course/song lists are covered
in test_sort_regression; menu modules need a real display/integration run.
"""

import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestUISmokeImports(unittest.TestCase):
    def test_import_core_packages(self):
        import importlib

        names = ("games", "util", "stepfilters", "fileparsers")
        loaded = [importlib.import_module(n) for n in names]
        self.assertEqual(len(loaded), 4)
        self.assertTrue(getattr(loaded[0], "GAMES", None))
        self.assertTrue(callable(getattr(loaded[1], "difficulty_sort_key", None)))


if __name__ == "__main__":
    unittest.main()
