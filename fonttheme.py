# Define and precompute font themes.

from __future__ import annotations

import logging
import os
from builtins import range
from configparser import ConfigParser

import pygame

from constants import *

logger = logging.getLogger(__name__)

# Purposes that use bold black menu/navigation styling (see constants.MENU_NAV_TEXT).
_MENU_NAV_FIXED_PURPOSES = frozenset(
    {
        "help",
        "SongSel_list",
        "Menu_button_no_sub",
        "Menu_button_if_sub",
        "Menu_button_sub",
        "Menu_rotating_top",
        "GameSel_list",
        "GameSel_description",
        "Opts_list",
        "Opts_description",
        "Opts_choices",
        "Opts_choice_description",
        "Crs_list",
        "Crs_song_title",
        "Crs_song_subtitle",
        "Menu_credits",
        "SongInfo_countdown",
        "SongInfo_player",
        "SongInfo_current_options",
        "MapKeys_message",
        "MapKeys_player",
        "MapKeys_input_type",
        "MapKeys_entries",
        "Endless_player",
        "Endless_filter_by",
        "Endless_filter_range",
        "diffbox",
    }
)
_MENU_NAV_VAR_PURPOSES = frozenset(
    {
        "SongSel_sort_mode",
        "GameSel_screen_title",
        "GameSel_selected_title",
        "Crs_course_list_head",
        "Crs_course_name",
        "SongInfo_controls",
        "SongInfo_screen_title",
    }
)


def _set_bold_if_menu_nav(purpose, font):
    if not isinstance(font, pygame.font.Font):
        return
    if purpose in _MENU_NAV_FIXED_PURPOSES or purpose in _MENU_NAV_VAR_PURPOSES:
        try:
            font.set_bold(True)
        except (AttributeError, TypeError):
            pass


# Find the appropriate font size to fit string into max_width pixels,
# that's at most max_size, and at least 6.
def max_size(font, string, max_width, max_size):
    for size in range(max_size, 0, -1):
        f = pygame.font.Font(font, size)
        if f.size(string)[0] < max_width:
            return f
    return pygame.font.Font(font, 6)


class FontTheme:
    _themes: dict[str, FontTheme] = {}
    # These "purposes" only ever appear in one size, set by the theme.
    _FIXED_SIZE = [
        "help",
        "SongSel_list",
        "loading_screen",
        "Menu_button_no_sub",
        "Menu_button_if_sub",
        "Menu_button_sub",
        "Menu_rotating_top",
        "BannerDisp_BPM",
        "GameSel_list",
        "GameSel_description",
        "Opts_list",
        "Opts_description",
        "Opts_choices",
        "Opts_choice_description",
        "Crs_list",
        "Crs_song_title",
        "Crs_song_subtitle",
        "error_message",
        "Dance_lifebar_text",
        "Dance_score_display",
        "Dance_lyrics_display",
        "Dance_FPS_display",
        "Dance_elapsed_time",
        "MapKeys_message",
        "MapKeys_player",
        "MapKeys_input_type",
        "MapKeys_entries",
        "Dance_step_judgment",
        "Dance_hold_judgment",
        "SongInfo_countdown",
        "SongInfo_player",
        "SongInfo_current_options",
        "GrScr_text",
        "GrScr_tocontinue",
        "Endless_player",
        "Endless_filter_by",
        "Endless_filter_range",
        "diffbox",
        "Menu_credits",
    ]
    # These "purposes" are resized to fit a particular total string length.
    _VAR_SIZE = [
        "BannerDisp_title",
        "BannerDisp_artist",
        "BannerDisp_subtitle",
        "SongSel_sort_mode",
        "GameSel_screen_title",
        "GameSel_selected_title",
        "Crs_course_list_head",
        "Crs_course_name",
        "SongInfo_controls",
        "SongInfo_screen_title",
    ]
    # These "purposes" have scaling handled by the actual rendering code.
    _SCALE_SIZE = ["Dance_title_artist", "Dance_combo_display"]

    @classmethod
    def load_themes(cls):
        for path in search_paths:
            fontdir = os.path.join(path, "themes", "font")
            if os.path.exists(fontdir) and os.path.isdir(fontdir):
                for fontcfg in os.listdir(fontdir):
                    if fontcfg.endswith(".cfg"):
                        theme = FontTheme(os.path.join(fontdir, fontcfg))
                        cls._themes[theme.title] = theme

    @classmethod
    def themes(cls):
        if cls._themes == {}:
            cls.load_themes()
        return list(cls._themes.keys())

    @classmethod
    def set(cls, title):
        if cls._themes == {}:
            cls.load_themes()

        cls._current = title

        for purpose in cls._FIXED_SIZE:
            fontfn, fontsize = cls._themes[title].fonts[purpose]
            f = pygame.font.Font(fontfn, fontsize)
            _set_bold_if_menu_nav(purpose, f)
            setattr(cls, purpose, f)

        for purpose in cls._SCALE_SIZE:
            setattr(cls, purpose, cls._themes[title].fonts[purpose])

    @classmethod
    def font(cls, purpose, string="", max_width=None, size=None):
        if purpose in cls._FIXED_SIZE:
            return getattr(cls, purpose)

        elif purpose in cls._VAR_SIZE:
            if max_width is not None:
                fontfn, maxsize = cls._themes[cls._current].fonts[purpose]
                f = max_size(fontfn, string, max_width, maxsize)
                _set_bold_if_menu_nav(purpose, f)
                return f
            elif size is not None:
                fontfn = cls._themes[cls._current].fonts[purpose][0]
                f = pygame.font.Font(fontfn, size)
                _set_bold_if_menu_nav(purpose, f)
                return f
            else:
                f = cls._themes[cls._current].fonts[purpose][0]
                if hasattr(f, "set_bold"):
                    _set_bold_if_menu_nav(purpose, f)
                return f

        elif purpose in cls._SCALE_SIZE:
            return cls._themes[cls._current].fonts[purpose]

        else:
            raise Exception("Requested font purpose not found.")

    def __init__(self, path):
        fontconf = ConfigParser()
        fontconf.read(path)

        self.fonts = {}

        self.title = fontconf.get("global", "title")

        if fontconf.has_option("global", "font"):
            defFont = os.path.join(os.path.dirname(path), fontconf.get("global", "font"))
        else:
            defFont = None

        for purpose in FontTheme._FIXED_SIZE + FontTheme._VAR_SIZE + FontTheme._SCALE_SIZE:
            if fontconf.has_option(purpose, "font"):
                fontfn = os.path.join(os.path.dirname(path), fontconf.get(purpose, "font"))
            else:
                fontfn = defFont
            fontsize = fontconf.getint(purpose, "size")
            self.fonts[purpose] = (fontfn, fontsize)


# Initialize function to be called after mainconfig is ready
def init_fonttheme():
    FontTheme.load_themes()
    try:
        FontTheme.set(mainconfig["fonttheme"])
    except KeyError:
        # If default theme not found, try to use the first available theme
        themes = FontTheme.themes()
        if themes:
            print(f"Font theme 'default' not found, using '{themes[0]}' instead")
            FontTheme.set(themes[0])
        else:
            print("Warning: No font themes found! Text may not display correctly.")
            # Create a dummy theme
            FontTheme._current = "dummy"
            for purpose in FontTheme._FIXED_SIZE:
                f = pygame.font.Font(None, 12)
                _set_bold_if_menu_nav(purpose, f)
                setattr(FontTheme, purpose, f)
