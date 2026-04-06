"""Tests for config.Config."""

import logging

logger = logging.getLogger(__name__)

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class TestConfig(unittest.TestCase):
    def test_user_overrides_master(self):
        c = Config()
        c.update({"a": 1, "b": 2}, master=True)
        c.update({"b": 99}, master=False)
        self.assertEqual(c["b"], 99)
        self.assertEqual(c["a"], 1)

    def test_setitem_master_flag(self):
        c = Config()
        c.__setitem__("onlymaster", 42, master=True)
        self.assertEqual(c["onlymaster"], 42)

    def test_load_blank_and_comment_lines(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".cfg") as f:
            f.write("# comment\n\n")
            f.write("k 1\n")
            path = f.name
        try:
            c = Config()
            c.load(path, master=False, should_exist=True)
            self.assertEqual(c["k"], 1)
        finally:
            os.unlink(path)

    def test_get_default(self):
        c = Config()
        self.assertIsNone(c.get("missing", None))
        self.assertEqual(c.get("missing", 7), 7)

    def test_delitem(self):
        c = Config()
        c.update({"x": 1}, master=True)
        c.update({"x": 2}, master=False)
        del c["x"]
        self.assertIsNone(c.get("x"))

    def test_load_and_write_roundtrip(self):
        c = Config()
        c.update({"fullscreen": 0, "volume": 5}, master=True)
        c.update({"volume": 7}, master=False)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".cfg") as f:
            path = f.name
        try:
            c.write(path)
            c2 = Config()
            c2.load(path, master=False, should_exist=True)
            self.assertEqual(c2["volume"], 7)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
