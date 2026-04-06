"""ListBox screen-space hit testing for mouse navigation on menu lists."""

import pygame

from constants import MENU_NAV_TEXT
from fonttheme import FontTheme
from interface import ListBox


def test_listbox_item_index_at_screen_pos_misses_outside():
    pygame.init()
    lb = ListBox(FontTheme.GameSel_list, MENU_NAV_TEXT, 26, 9, 220, [408, 53])
    lb.set_items([str(i) for i in range(5)])
    lb.set_index(2, 1)
    assert lb.item_index_at_screen_pos(0, 0) is None
    assert lb.item_index_at_screen_pos(408 + 500, 53) is None


def test_listbox_item_index_at_screen_pos_hits_row():
    pygame.init()
    lb = ListBox(FontTheme.GameSel_list, MENU_NAV_TEXT, 26, 3, 220, [100, 100])
    lb.set_items(["a", "b", "c"])
    lb.set_index(1, 1)
    # _idx = 0; row 0 -> item (0+0)%3 = 0; row 1 -> 1; row 2 -> 2
    assert lb.item_index_at_screen_pos(105, 100 + 5) == 0
    assert lb.item_index_at_screen_pos(105, 100 + 26 + 5) == 1
    assert lb.item_index_at_screen_pos(105, 100 + 52 + 5) == 2


def test_listbox_item_index_at_screen_pos_wraps_idx():
    pygame.init()
    lb = ListBox(FontTheme.GameSel_list, MENU_NAV_TEXT, 26, 3, 220, [0, 0])
    lb.set_items(["a", "b", "c"])
    lb.set_index(1, 1)
    # _idx = 0; top row shows index 0
    assert lb.item_index_at_screen_pos(5, 5) == 0
    lb.set_index(0, 1)
    # _idx = -1 for count=3 -> _idx = 0 - 1 = -1
    assert lb._idx == -1
    # row 0: (-1 + 0) % 3 = 2
    assert lb.item_index_at_screen_pos(5, 5) == 2
