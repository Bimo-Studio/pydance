import logging

logger = logging.getLogger(__name__)

from builtins import range

import pygame

import colors
import ui
from constants import *
from fontfx import TextZoomer, shadow
from fonttheme import FontTheme

# Treat pad/player-scoped navigation the same as global menu keys (keyboard often maps both).
_MENU_NAV_PLAYER_EVENTS = frozenset(
    (
        ui.UP,
        ui.DOWN,
        ui.LEFT,
        ui.RIGHT,
        ui.CONFIRM,
        ui.OPTIONS,
        ui.CANCEL,
        ui.PGUP,
        ui.PGDN,
    )
)

# Hooray! Less magic numbers — menu labels use MENU_NAV_TEXT (black bold).
TOPLEFT = (0, 0)
BUTTON_SIZE = (192, 48)
BUTTON_WIDTH, BUTTON_HEIGHT = BUTTON_SIZE
BUTTON_PADDING = 8
LEFT_OFFSET, TOP_OFFSET = 425, 100
DISPLAYED_ITEMS = 6

# Top-level Main Menu only: minimum ms between accepting UP/DOWN scroll steps (pairs with
# MenuListNavDedupe to tame global + P1 duplicate events and light key bounce).
MAIN_MENU_NAV_GAP_MS = 160

CREATE, SELECT, UNSELECT = 1000, 2000, 3000


def _visible_menu_text(text, font, selected=False):
    """Black label with a light rim so it stays readable on any menu background."""
    off = 5 if selected else 2
    return shadow(
        text,
        font,
        MENU_NAV_TEXT,
        offset=off,
        color2=MENU_NAV_SHADOW_LIGHT,
    )


def _menu_row_rect(row_index):
    """Screen rect for visible row index 0 .. DISPLAYED_ITEMS-1 (not global item index)."""
    return pygame.Rect(
        LEFT_OFFSET,
        TOP_OFFSET + row_index * (BUTTON_HEIGHT + BUTTON_PADDING),
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )


class MenuItem:
    def __init__(self, text, callbacks, args):
        # Dict of callbacks by keycodes, also "initial", "select", "unselect"

        # This looks something like:
        # MenuItem({ 'initial': do_setup, START: do_change,
        #            START: do_change }, (configdata, mystrings))
        # When the button is pressed, do_change(configdata, mystrings) will be
        # called.
        self.callbacks = callbacks
        self.args = args
        self.subtext = None
        self.text = text
        self._selected = False
        self.render()

    # Call an appropriate callback function, for the event given.
    # The function can return up to three arguments - the new
    # text to display on the button, the new subtext to display, and
    # the RGB value of the text.

    def activate(self, ev):  # Note - event ID, not an event tuple
        if ev == SELECT:
            self._selected = True
            self.render()
        elif ev == UNSELECT:
            self._selected = False
            self.render()
        elif self.callbacks is None:
            if ev in [ui.OPTIONS, ui.RIGHT, ui.LEFT, ui.CONFIRM]:
                return ui.CANCEL  # This is a back button
            else:
                return ev  # Shouldn't happen
        elif callable(self.callbacks.get(ev)):
            text, subtext = self.callbacks[ev](*self.args)
            if text is not None:
                self.text = text  # str(text)
            if subtext is not None:
                self.subtext = subtext  # str(subtext)
            self.render()
            return ev
        else:
            return ev

    # Render the image. If subtext is present, the main text gets smaller.
    def render(self):
        self.image = pygame.surface.Surface(BUTTON_SIZE, SRCALPHA, 32)
        self.image.fill((0, 0, 0, 0))
        if self.subtext is None:
            text = _visible_menu_text(self.text, FontTheme.Menu_button_no_sub, self._selected)
            self.image.blit(
                text,
                (
                    BUTTON_WIDTH // 2 - text.get_width() // 2,
                    BUTTON_HEIGHT // 2 - text.get_height() // 2,
                ),
            )
        else:
            text = _visible_menu_text(self.text, FontTheme.Menu_button_if_sub, self._selected)
            subtext = _visible_menu_text(self.subtext, FontTheme.Menu_button_sub, self._selected)
            self.image.blit(
                text,
                (
                    BUTTON_WIDTH // 2 - text.get_width() // 2,
                    BUTTON_HEIGHT // 3 - text.get_height() // 2,
                ),
            )
            self.image.blit(
                subtext,
                (
                    BUTTON_WIDTH // 2 - subtext.get_width() // 2,
                    (2 * BUTTON_HEIGHT) // 3 - subtext.get_height() // 2,
                ),
            )


class Menu:
    _display_depth = 0
    # Plain white; no .convert() here — import runs before pygame.display.set_mode().
    _menu_bg_plain = pygame.Surface((640, 480))
    _menu_bg_plain.fill((255, 255, 255))
    bgimage = _menu_bg_plain
    try:
        click_sound = pygame.mixer.Sound(os.path.join(sound_path, "clicked.ogg"))
        click_sound.set_volume(0.45)
    except pygame.error:
        raise SystemExit("You need SDL_mixer 1.2.5 with Vorbis support.")
    move_sound = pygame.mixer.Sound(os.path.join(sound_path, "move.ogg"))
    back_sound = pygame.mixer.Sound(os.path.join(sound_path, "back.ogg"))

    # Menus are defined based on a tree of tuples (submenus) ending
    # in a list (the final item). The first item of the tuple is
    # a string of text which gets displayed.
    def __init__(self, name, itemlist, screen, sprites):
        self.items = []
        self.sprites = sprites
        self.text = name
        self._selected = False
        self.screen = screen
        self.render()
        for i in itemlist:
            if isinstance(i, list):  # Menuitems are lists
                self.items.append(MenuItem(i[0], i[1], i[2]))
                self.items[-1].activate(CREATE)
            elif isinstance(i, tuple):  # New submenus are tuples
                self.items.append(Menu(i[0], i[1:], screen, sprites))

    # Menu rendering is tons easier, since it never changes.
    def render(self):
        self.image = pygame.surface.Surface(BUTTON_SIZE, SRCALPHA, 32)
        self.image.fill((0, 0, 0, 0))
        text = _visible_menu_text(self.text, FontTheme.Menu_button_no_sub, self._selected)
        self.image.blit(
            text,
            (
                BUTTON_WIDTH // 2 - text.get_width() // 2,
                BUTTON_HEIGHT // 2 - text.get_height() // 2,
            ),
        )

    def activate(self, ev):
        if ev in [ui.OPTIONS, ui.CONFIRM, ui.RIGHT]:
            self.display()
        elif ev == SELECT:
            self._selected = True
            self.render()
        elif ev == UNSELECT:
            self._selected = False
            self.render()

    # Render and start navigating the menu.
    # Postcondition: Screen buffer is in an unknown state!
    def display(self):
        screen = self.screen
        clock = pygame.time.Clock()
        Menu._display_depth += 1
        pygame.mouse.set_visible(True)
        Menu.bgimage.set_alpha(255)
        pygame.display.update(screen.blit(Menu.bgimage, TOPLEFT))
        curitem = 0
        topitem = 0
        toprotater = TextZoomer(
            self.text,
            FontTheme.Menu_rotating_top,
            (640, 64),
            MENU_NAV_TEXT,
            (0, 0, 0, 0),
        )

        self.items[curitem].activate(SELECT)

        ev = ui.PASS
        # Keyboard maps one key to both global (-1) UP/DOWN and P1_UP/P1_DOWN (0); poll() returns
        # those as two events on successive frames. Game select uses MenuListNavDedupe for that;
        # apply the same on the top-level Main Menu only (depth 1), plus a short cooldown.
        main_nav_ud = ui.MenuListNavDedupe() if Menu._display_depth == 1 else None
        main_menu_nav_next_ok = 0
        try:
            while ev != ui.CANCEL:
                r = []
                # Top-level Main Menu only (_display_depth == 1): disable poll() autorepeat so one
                # key press moves one row. Nested submenus (depth > 1) keep repeat for long lists.
                pid, ev = ui.ui.poll(autorepeat=(Menu._display_depth > 1))
                # Use player-scoped keys for menu too (many configs only bind P1_UP / P1_DOWN).
                if pid >= 0 and ev not in _MENU_NAV_PLAYER_EVENTS:
                    ev = ui.PASS
                if main_nav_ud is not None and ev in (ui.UP, ui.DOWN):
                    t = pygame.time.get_ticks()
                    if t < main_menu_nav_next_ok:
                        ev = ui.PASS
                    elif not main_nav_ud.consume_ud(pid, ev):
                        ev = ui.PASS
                    else:
                        main_menu_nav_next_ok = t + MAIN_MENU_NAV_GAP_MS

                # Scroll down through the menu
                if ev == ui.DOWN:
                    Menu.move_sound.play()
                    ev = self.items[curitem].activate(UNSELECT)
                    curitem += 1
                    if curitem == len(self.items):  # Loop at the bottom
                        curitem = 0
                        topitem = 0
                    elif curitem >= topitem + DISPLAYED_ITEMS:  # Advance the menu
                        topitem += 1
                    ev = self.items[curitem].activate(SELECT)

                # Same as above, but up
                elif ev == ui.UP:
                    Menu.move_sound.play()
                    ev = self.items[curitem].activate(UNSELECT)
                    curitem -= 1
                    if curitem < 0:
                        curitem = len(self.items) - 1
                        topitem = max(0, curitem - DISPLAYED_ITEMS + 1)
                    elif curitem < topitem:
                        topitem = curitem
                    ev = self.items[curitem].activate(SELECT)

                elif ev == ui.FULLSCREEN:
                    mainconfig["fullscreen"] ^= 1
                    pygame.display.toggle_fullscreen()

                elif ev == ui.MOUSE_CLICK:
                    mx, my = ui.ui.last_mouse_pos
                    hit = None
                    for row in range(DISPLAYED_ITEMS):
                        idx = topitem + row
                        if idx >= len(self.items):
                            break
                        if _menu_row_rect(row).collidepoint(mx, my):
                            hit = idx
                            break
                    if hit is not None:
                        if hit != curitem:
                            self.items[curitem].activate(UNSELECT)
                            curitem = hit
                            if curitem < topitem:
                                topitem = curitem
                            elif curitem >= topitem + DISPLAYED_ITEMS:
                                topitem = curitem - DISPLAYED_ITEMS + 1
                            self.items[curitem].activate(SELECT)
                            Menu.move_sound.play()
                        Menu.click_sound.play()
                        ev = self.items[curitem].activate(ui.CONFIRM)
                        ui.ui.clear()
                        ev = ui.PASS

                # Otherwise, if the event actually happened, pass it on to the button.
                elif ev != ui.PASS and ev != ui.CANCEL:
                    if ev in [ui.OPTIONS, ui.CONFIRM]:
                        Menu.click_sound.play()
                    ev = self.items[curitem].activate(ev)
                    ui.ui.clear()

                toprotater.iterate()
                # Always record the full background blit for partial updates (SDL needs the rect).
                r.append(screen.blit(Menu.bgimage, TOPLEFT))
                r.append(screen.blit(toprotater.tempsurface, TOPLEFT))
                for i in range(DISPLAYED_ITEMS):
                    if i + topitem < len(self.items):
                        r.append(
                            screen.blit(
                                self.items[i + topitem].image,
                                (
                                    LEFT_OFFSET,
                                    TOP_OFFSET + i * (BUTTON_HEIGHT + BUTTON_PADDING),
                                ),
                            )
                        )
                sel_row = curitem - topitem
                if 0 <= sel_row < DISPLAYED_ITEMS:
                    hl = _menu_row_rect(sel_row).inflate(6, 4)
                    pygame.draw.rect(screen, colors.WHITE, hl, 2)
                    caret = shadow(
                        ">",
                        FontTheme.Menu_button_no_sub,
                        MENU_NAV_TEXT,
                        offset=1,
                        color2=MENU_NAV_SHADOW_LIGHT,
                    )
                    cx = max(2, hl.left - 8 - caret.get_width())
                    r.append(screen.blit(caret, (cx, hl.centery - caret.get_height() // 2)))

                self.sprites.update()
                r.extend(self.sprites.draw(screen))
                pygame.display.update(r)
                # self.sprites.clear(screen, Menu.bgimage)
                clock.tick(30)

            if ev == ui.CANCEL:
                Menu.back_sound.play()
                self.items[curitem].activate(UNSELECT)
        finally:
            Menu._display_depth -= 1
            if Menu._display_depth == 0:
                pygame.mouse.set_visible(False)
