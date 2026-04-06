"""Tests for gfxtheme (ThemeFile, GFXTheme)."""

import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest

import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGfxTheme(unittest.TestCase):
    def setUp(self):
        pygame.init()

    def test_theme_file_list_themes_returns_list(self):
        from gfxtheme import ThemeFile

        themes = ThemeFile.list_themes("SINGLE")
        self.assertIsInstance(themes, list)

    def test_gfx_theme_alias(self):
        from gfxtheme import GFXTheme, GfxTheme

        self.assertIs(GfxTheme, GFXTheme)

    def test_arrow_set_indexing_shape(self):
        """ArrowSet exposes per-direction keys without loading a full theme."""
        import games
        from gfxtheme import ArrowSet

        game = games.GAMES["SINGLE"]
        # Minimal fake theme with only the methods ArrowSet needs

        class _FakeTheme:
            size = game.width

            def get_arrow(self, type, dir, color):
                surf = pygame.Surface((game.width, game.width))
                surf.fill((1, 2, 3))
                return surf, 0, color

        fake = _FakeTheme()
        arrow_set = ArrowSet(fake, game, 0)
        for d in game.dirs:
            for cnum in range(4):
                key = d + repr(cnum)
                self.assertIn(key, arrow_set.arrows)


if __name__ == "__main__":
    unittest.main()
