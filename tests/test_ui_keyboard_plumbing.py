"""Regression: keyboard plumbing must use a sparse container for pygame 2 / SDL2 key codes."""

import os
import unittest


class TestKeyboardPlumbingContainer(unittest.TestCase):
    def test_default_keyboard_plumbing_is_dict_not_huge_list(self):
        import ui

        c = ui.default_keyboard_plumbing.container
        self.assertIsInstance(c, dict)
        # SDL2 keycodes are large (e.g. K_LEFT=1073741904); a list backend would be billions of slots.
        self.assertLess(len(c), 500)

    def test_ui_pump_accepts_sdl2_arrow_key_codes(self):
        """key_state was a 512-list; SDL2 K_UP etc. are ~1e9 — they must reach keyboard_plumbing."""
        import pygame

        import ui

        u = ui.UI()
        k_up = pygame.K_UP
        self.assertGreaterEqual(k_up, 512)
        u.pump([pygame.event.Event(pygame.KEYDOWN, key=k_up)])
        self.assertTrue(u.key_state.get(k_up))
        u.pump([pygame.event.Event(pygame.KEYUP, key=k_up)])
        self.assertFalse(u.key_state.get(k_up, False))

    def test_menu_list_nav_dedupe_skips_p1_after_global(self):
        import ui

        d = ui.MenuListNavDedupe()
        self.assertTrue(d.consume_ud(-1, ui.UP))
        self.assertFalse(d.consume_ud(0, ui.UP))
        d = ui.MenuListNavDedupe()
        self.assertTrue(d.consume_ud(0, ui.DOWN))

    def test_keydown_after_stale_key_state_emits_plumbing(self):
        """After KEYDOWN+KEYDOWN with no KEYUP, resync must emit events (lost KEYUP / duplicate KEYDOWN)."""
        import pygame

        import ui

        old = os.environ.get("PYDANCE_DISABLE_STDIN_KEYS")
        os.environ["PYDANCE_DISABLE_STDIN_KEYS"] = "1"
        try:
            pygame.event.clear()
            u = ui.UI()
            u.event_buffer.clear()
            k = pygame.K_DOWN
            u.pump([pygame.event.Event(pygame.KEYDOWN, key=k, repeat=0)])
            u.event_buffer.clear()
            u.pump([pygame.event.Event(pygame.KEYDOWN, key=k, repeat=0)])
            self.assertGreater(len(u.event_buffer), 0)
        finally:
            if old is None:
                os.environ.pop("PYDANCE_DISABLE_STDIN_KEYS", None)
            else:
                os.environ["PYDANCE_DISABLE_STDIN_KEYS"] = old

    def test_single_arrow_key_emits_direction_event(self):
        """Default keyboard maps one arrow key to DOWN (not AND with keypad)."""
        import pygame

        import ui

        old = os.environ.get("PYDANCE_DISABLE_STDIN_KEYS")
        os.environ["PYDANCE_DISABLE_STDIN_KEYS"] = "1"
        try:
            pygame.event.clear()
            u = ui.UI()
            u.event_buffer.clear()
            u.pump([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, repeat=0)])
            self.assertTrue(any(ev == ui.DOWN for _pid, ev in u.event_buffer))
        finally:
            if old is None:
                os.environ.pop("PYDANCE_DISABLE_STDIN_KEYS", None)
            else:
                os.environ["PYDANCE_DISABLE_STDIN_KEYS"] = old

    def test_poll_always_pumps_pygame_while_semantic_buffer_nonempty(self):
        """poll() must not skip pygame.event.get() when event_buffer still has pending UI events."""
        import pygame

        import ui

        old = os.environ.get("PYDANCE_DISABLE_STDIN_KEYS")
        os.environ["PYDANCE_DISABLE_STDIN_KEYS"] = "1"
        try:
            pygame.event.clear()
            u = ui.UI()
            u.event_buffer.clear()
            u.event_buffer.append((-1, ui.UP))
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
            pid, ev = u.poll()
            self.assertEqual((pid, ev), (-1, ui.UP))
            self.assertTrue(u.key_state.get(pygame.K_DOWN))
        finally:
            if old is None:
                os.environ.pop("PYDANCE_DISABLE_STDIN_KEYS", None)
            else:
                os.environ["PYDANCE_DISABLE_STDIN_KEYS"] = old


if __name__ == "__main__":
    unittest.main()
