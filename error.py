import logging

logger = logging.getLogger(__name__)

# Put up a pretty error message.


import fontfx
import ui
from constants import mainconfig
from fonttheme import FontTheme
from interface import *


class ErrorMessage(InterfaceWindow):
    def __init__(self, screen, line):
        InterfaceWindow.__init__(self, screen, "error-bg.png")
        text = fontfx.shadow("Error!", FontTheme.error_message, [255, 255, 255], offset=2)
        text_rect = text.get_rect()
        text_rect.center = [320, 50]
        screen.blit(text, text_rect)

        # FIXME: Remove this when I'm sure that nothing uses the old calling
        # method. (Pre-1.0)
        if isinstance(line, list):
            line = " ".join(line)

        font = fontfx.WrapFont(FontTheme.error_message, 440)
        b = font.render(line, shdw=True, centered=True)
        r = b.get_rect()
        r.center = [320, 240]
        screen.blit(b, r)

        text = fontfx.shadow("Press Enter/Start/Escape", FontTheme.error_message, [160, 160, 160])
        textpos = text.get_rect()
        textpos.center = [320, 440]
        screen.blit(text, textpos)

        pygame.display.update()
        ui.ui.clear()

        pid, ev = (0, ui.PASS)
        while ev not in [ui.OPTIONS, ui.CONFIRM, ui.CANCEL]:
            if ev == ui.FULLSCREEN:
                pygame.display.toggle_fullscreen()
                mainconfig["fullscreen"] ^= 1
            pid, ev = ui.ui.wait()
