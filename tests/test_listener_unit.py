"""Cover listener.Listener default no-op hooks."""

import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from listener import Listener


class DummyListener(Listener):
    """Concrete listener without the abstract __init__ guard."""

    def __init__(self):
        pass


class TestListener(unittest.TestCase):
    def test_default_hooks_are_noops(self):
        d = DummyListener()
        d.ok_hold(0, 0.0, "l", 1)
        d.broke_hold(0, 0.0, "l", 1)
        d.stepped(0, "l", 0.0, 0.0, "P", 1)
        d.set_song(0, 120.0, "BASIC", 10, 0, 3)
        d.change_bpm(0, 0.0, 140.0)


if __name__ == "__main__":
    unittest.main()
