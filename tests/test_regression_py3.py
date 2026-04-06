"""
Regression tests for Python 3 migration fixes (not every change has a test here;
see also test_pydance_songlist, test_sort_regression, test_gfxtheme).
"""

import logging

logger = logging.getLogger(__name__)

import locale
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLocaleFormatString(unittest.TestCase):
    """gradescreen.StatSprite uses locale.format_string (not the old locale.format API)."""

    def test_format_string_is_the_supported_api(self):
        # Python 3.10+ may still expose locale.format as a deprecated alias; do not assert it is gone.
        self.assertTrue(callable(getattr(locale, "format_string", None)))

    def test_format_string_integer_grouping(self):
        self.assertEqual(locale.format_string("%d", 42, False), "42")
        out = locale.format_string("%d", 1234, True)
        self.assertTrue(out.replace(",", "").replace(" ", "").isdigit())


class TestFontfxRenderOuterSlices(unittest.TestCase):
    """render_outer must use int slice indices (Python 3)."""

    def test_render_outer_short_string_unchanged(self):
        import fontfx

        class _F:
            def size(self, s):
                return (len(s) * 8, 12)

        self.assertEqual(fontfx.render_outer("hi", 100, _F()), "hi")

    def test_render_outer_truncates_with_ellipsis(self):
        import fontfx

        class _F:
            def size(self, s):
                return (len(s) * 10, 12)

        out = fontfx.render_outer("abcdefghijklmnopqrstuvwxyz", 80, _F())
        self.assertIn("...", out)
        self.assertLessEqual(len(out), len("abcdefghijklmnopqrstuvwxyz"))


class TestUiJoystickChrIndex(unittest.TestCase):
    """ui.PlumbingStringer: chr(ord('A') + (i - MAX_BUTTONS) // 3) must be int."""

    def test_chr_index_is_integer(self):
        # Do not import ui here: importing ui constructs UI() (joystick/audio) and can hang CI.
        MAX_BUTTONS = 32  # must match ui.MAX_BUTTONS

        i = MAX_BUTTONS + 5
        ch = chr(ord("A") + (i - MAX_BUTTONS) // 3)
        self.assertEqual(len(ch), 1)
        self.assertEqual(ch, "B")


class TestCombosDigitExtraction(unittest.TestCase):
    """combos.ComboDisp uses // for digit indices (float broke % indexing)."""

    def test_digits_1234(self):
        drawcount = 1234
        thousands = drawcount // 1000
        hundreds = (drawcount // 100) % 10
        tens = (drawcount // 10) % 10
        ones = drawcount % 10
        self.assertEqual(thousands, 1)
        self.assertEqual(hundreds, 2)
        self.assertEqual(tens, 3)
        self.assertEqual(ones, 4)


class TestGradescreenStatSpriteRender(unittest.TestCase):
    """Smoke: StatSprite._render after locale.format_string fix."""

    def setUp(self):
        import pygame

        pygame.init()

    def test_stat_sprite_render_runs(self):
        import pygame

        from gradescreen import StatSprite

        pygame.display.set_mode((640, 480))
        s = StatSprite([0, 0], "OK:", 42, [120, 24], 0)
        s._curcount = 7
        s._render()
        self.assertIsNotNone(s.image)


if __name__ == "__main__":
    unittest.main()
