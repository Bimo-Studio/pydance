"""Tests for colors module helpers."""

import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import colors


class TestColors(unittest.TestCase):
    def test_brighten_darken(self):
        c = [100, 100, 100]
        self.assertEqual(colors.brighten(c, 10)[0], 110)
        self.assertEqual(colors.darken(c, 10)[0], 90)

    def test_darken_div(self):
        c = [10, 20, 30]
        out = colors.darken_div(c, 2.0)
        self.assertEqual(out[0], 5.0)

    def test_average(self):
        a = colors.average([0, 0, 0], [100, 100, 100], 0.5)
        self.assertEqual(a, [50, 50, 50])

    def test_white_black(self):
        self.assertEqual(len(colors.WHITE), 3)
        self.assertEqual(len(colors.BLACK), 3)


if __name__ == "__main__":
    unittest.main()
