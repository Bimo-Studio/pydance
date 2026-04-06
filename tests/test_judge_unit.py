"""Tests for TimeJudge / BeatJudge (Announcer mocked)."""

import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTimeJudge(unittest.TestCase):
    @patch("judge.Announcer")
    def test_ratings_and_miss(self, mock_ann):
        import judge

        mock_ann.return_value = MagicMock()
        j = judge.TimeJudge(0, {"judgescale": 1.0})
        j.set_song(0, 120, "BASIC", 10, 0, 3)
        j.handle_arrow("l", 5.0, False)
        r, d, t = j.handle_key("l", 5.0)
        self.assertIsNotNone(r)
        self.assertTrue(j._is_miss(10.0, 5.0))

    @patch("judge.Announcer")
    def test_expire_arrows(self, mock_ann):
        import judge

        mock_ann.return_value = MagicMock()
        j = judge.TimeJudge(0, {"judgescale": 1.0})
        j.set_song(0, 120, "BASIC", 1, 0, 3)
        j.handle_arrow("lr", 1.0, False)
        misses = j.expire_arrows(100.0)
        self.assertIsInstance(misses, str)

    @patch("judge.Announcer")
    def test_beat_judge_bpm_change(self, mock_ann):
        import judge

        mock_ann.return_value = MagicMock()
        j = judge.BeatJudge(0, {"judgescale": 1.0})
        j.set_song(0, 120, "BASIC", 8, 0, 3)
        j.change_bpm(0, 0.0, 140)
        self.assertGreater(j._tick, 0)


if __name__ == "__main__":
    unittest.main()
