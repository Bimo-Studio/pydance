"""Tests for stepfilters (pure transforms and helpers)."""

import logging

logger = logging.getLogger(__name__)

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import stepfilters


class TestNonRandom(unittest.TestCase):
    def test_deterministic_sequence(self):
        a = stepfilters.NonRandom(42)
        b = stepfilters.NonRandom(42)
        for _ in range(50):
            self.assertEqual(a.random(), b.random())

    def test_seed(self):
        r = stepfilters.NonRandom(1)
        stepfilters.NonRandom.seed(r, 99)
        self.assertEqual(r.seed, 99)


class TestCompress(unittest.TestCase):
    def test_compress_merges_empty_beats(self):
        steps = [
            [1.0, 1, 0, 0, 0],
            [1.0, 0, 0, 0, 0],
            ["D", 4.0],
        ]
        out = stepfilters.compress(steps)
        self.assertTrue(len(out) >= 1)


class TestTransforms(unittest.TestCase):
    def test_mapping_mirror_single(self):
        t = stepfilters.MirrorTransform("SINGLE")
        self.assertEqual(len(t._mapping), 4)

    def test_shuffle_changes_mapping(self):
        random.seed(0)
        t = stepfilters.ShuffleTransform("SINGLE")
        self.assertEqual(len(t._mapping), 4)

    def test_rotate_list_length(self):
        self.assertEqual(len(stepfilters.rotate), 6)


if __name__ == "__main__":
    unittest.main()
