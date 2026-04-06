"""Unit tests for records.py (in-memory only; restores global state)."""

import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import records


class TestRecords(unittest.TestCase):
    def setUp(self):
        self._saved = dict(records.records)
        self._bad = dict(records.bad_records)
        records.records.clear()
        records.bad_records.clear()

    def tearDown(self):
        records.records.clear()
        records.bad_records.clear()
        records.records.update(self._saved)
        records.bad_records.update(self._bad)

    def test_add_new_and_get(self):
        records.add("songkey", "BASIC", "SINGLE", 0.8, "p1")
        row = records.get("songkey", "BASIC", "SINGLE")
        r, name = row[0], row[1]
        self.assertAlmostEqual(r, 0.8)
        self.assertEqual(name, "p1")

    def test_add_lower_rank_no_replace(self):
        records.add("k2", "BASIC", "SINGLE", 0.9, "a")
        records.add("k2", "BASIC", "SINGLE", 0.5, "b")
        row = records.get("k2", "BASIC", "SINGLE")
        r, _ = row[0], row[1]
        self.assertAlmostEqual(r, 0.9)

    def test_best_worst_like_dislike(self):
        records.add("s1", "BASIC", "SINGLE", 0.3, "x")
        records.add("s2", "BASIC", "SINGLE", 0.9, "y")
        self.assertEqual(records.best(1, "BASIC", "SINGLE"), "s2")
        self.assertEqual(records.worst(1, "BASIC", "SINGLE"), "s1")
        self.assertIsNotNone(records.like(1, "BASIC", "SINGLE"))
        self.assertIsNotNone(records.dislike(1, "BASIC", "SINGLE"))

    def test_verify_moves_unknown_keys(self):
        records.add("known", "BASIC", "SINGLE", 0.5, "z")
        records.records[("unknown", "BASIC", "SINGLE")] = (0.1, "n", 1)
        records.verify(["known"])
        self.assertNotIn(("unknown", "BASIC", "SINGLE"), records.records)


if __name__ == "__main__":
    unittest.main()
