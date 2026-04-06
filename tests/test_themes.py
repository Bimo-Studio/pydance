import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestThemes(unittest.TestCase):
    def test_font_themes_exist(self):
        """Test that font themes are available"""
        import os

        font_theme_dir = "themes/font"
        if os.path.exists(font_theme_dir):
            themes = [f for f in os.listdir(font_theme_dir) if f.endswith(".cfg")]
            print(f"Available font themes: {themes}")
            self.assertGreater(len(themes), 0, "No font themes found")
        else:
            self.fail(f"Font theme directory not found: {font_theme_dir}")

    def test_gfx_themes_exist(self):
        """Test that graphics themes are available"""
        import os

        gfx_theme_dir = "themes/gfx/64x64"
        if os.path.exists(gfx_theme_dir):
            themes = os.listdir(gfx_theme_dir)
            print(f"Available graphics themes: {themes}")
            self.assertGreater(len(themes), 0, "No graphics themes found")
        else:
            self.fail(f"Graphics theme directory not found: {gfx_theme_dir}")


if __name__ == "__main__":
    unittest.main()
