import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestImports(unittest.TestCase):
    def test_import_constants(self):
        """Test that constants module imports"""
        try:
            import constants

            self.assertTrue(hasattr(constants, "VERSION"))
        except Exception as e:
            self.fail(f"Failed to import constants: {e}")

    def test_import_games(self):
        """Test that games module imports"""
        try:
            import games

            self.assertTrue(hasattr(games, "GAMES"))
        except Exception as e:
            self.fail(f"Failed to import games: {e}")

    def test_games_left_off(self):
        import games

        g = games.GAMES["SINGLE"]
        self.assertIsInstance(g.left_off(0), (int, float))
        self.assertGreater(g.sprite_center, 0)
        self.assertIn("l", g.battle_lefts)

    def test_import_fileparsers(self):
        """Test that fileparsers module imports"""
        try:
            import fileparsers

            self.assertTrue(hasattr(fileparsers, "SongItem"))
        except Exception as e:
            self.fail(f"Failed to import fileparsers: {e}")


if __name__ == "__main__":
    unittest.main()
