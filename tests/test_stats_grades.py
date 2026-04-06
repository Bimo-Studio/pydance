"""Tests for stats and grades listeners."""

import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grades import DancePointsGrade, EndlessGrade, grade_opt, grades
from stats import Stats


class TestStats(unittest.TestCase):
    def test_stepped_counts(self):
        s = Stats()
        s.stepped(0, "l", 1.0, 1.0, "P", 1)
        self.assertEqual(s["P"], 1)
        self.assertEqual(s.arrow_count, 1)

    def test_early_late(self):
        s = Stats()
        s.stepped(0, "l", 1.05, 1.0, "G", 1)
        self.assertEqual(s.late, 1)
        s.stepped(0, "l", 0.95, 1.0, "G", 2)
        self.assertEqual(s.early, 1)

    def test_times_stddev(self):
        s = Stats()
        s.stepped(0, "l", 1.0, 1.0, "P", 1)
        s.stepped(0, "l", 1.1, 1.0, "P", 2)
        avg, std = s.times()
        self.assertIsInstance(avg, float)
        self.assertIsInstance(std, float)

    def test_offset_ms(self):
        s = Stats()
        s.stepped(0, "l", 1.0, 1.0, "V", 1)
        s.stepped(0, "l", 1.02, 1.0, "V", 2)
        self.assertNotEqual(s.offset(), 0)

    def test_holds(self):
        s = Stats()
        s.ok_hold(0, 0.0, "l", 1)
        s.broke_hold(0, 0.0, "l", 2)
        self.assertEqual(s.hold_count, 2)


class TestGrades(unittest.TestCase):
    def test_grade_by_rank(self):
        self.assertEqual(DancePointsGrade.grade_by_rank(1.0), "AAA")
        self.assertEqual(DancePointsGrade.grade_by_rank(-2), "F")
        self.assertEqual(DancePointsGrade.grade_by_rank(-1), "?")
        self.assertEqual(DancePointsGrade.grade_by_rank(0.4), "D")

    def test_dance_points_flow(self):
        g = DancePointsGrade()
        g.stepped(0, "l", 0, 0, "V", 0)
        g.stepped(0, "l", 0, 0, "M", 0)
        self.assertLess(g.rank(), 1.0)
        letter = g.grade(False)
        self.assertTrue(len(letter) > 0)

    def test_endless_grade(self):
        g = EndlessGrade()
        self.assertNotEqual(g.grade(True), "F")

    def test_grade_lists(self):
        self.assertGreaterEqual(len(grades), 2)
        self.assertGreaterEqual(len(grade_opt), 1)


if __name__ == "__main__":
    unittest.main()
