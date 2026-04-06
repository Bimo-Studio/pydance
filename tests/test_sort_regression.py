"""
Regression tests for Python 3 list.sort(key=...) behavior.

These paths used to pass cmp-style functions to sort() and would raise
TypeError at runtime. Automated tests reduce manual QA for course/song
sorting and endless-mode difficulty ordering.
"""

import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class _CourseStub:
    __slots__ = ("name", "mixname")

    def __init__(self, name, mixname):
        self.name = name
        self.mixname = mixname


# Keep in sync with courseselect.SORTS — do not import courseselect here: importing it
# loads ui + dance2 and can block indefinitely in headless/CI (joystick init, etc.).
def _course_sort_key_title(x):
    return x.name.lower()


def _course_sort_key_mix(x):
    return (str(x.mixname).lower(), x.name.lower())


class TestSortRegression(unittest.TestCase):
    def test_courseselect_sort_by_title_key(self):
        items = [_CourseStub("Zeta", "m1"), _CourseStub("Alpha", "m2")]
        items.sort(key=_course_sort_key_title)
        self.assertEqual([x.name for x in items], ["Alpha", "Zeta"])

    def test_courseselect_sort_by_mix_then_name(self):
        items = [
            _CourseStub("B", "zebra"),
            _CourseStub("A", "apple"),
            _CourseStub("C", "apple"),
        ]
        items.sort(key=_course_sort_key_mix)
        self.assertEqual(
            [(x.mixname, x.name) for x in items],
            [("apple", "A"), ("apple", "C"), ("zebra", "B")],
        )

    def test_songselect_folder_names_sort_case_insensitive(self):
        lst = ["Banana", "apple", "Cherry"]
        lst.sort(key=lambda x: x.lower())
        self.assertEqual(lst, ["apple", "Banana", "Cherry"])

    def test_endless_difficulties_use_sort_key(self):
        import util

        diffs = ["MANIAC", "BASIC", "HEAVY"]
        diffs.sort(key=util.difficulty_sort_key)
        # Order follows util.DIFFICULTY_LIST indices (e.g. MANIAC before HEAVY).
        self.assertEqual(diffs, ["BASIC", "MANIAC", "HEAVY"])


if __name__ == "__main__":
    unittest.main()
