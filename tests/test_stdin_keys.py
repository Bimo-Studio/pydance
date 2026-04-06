"""stdin_keys: terminal escape sequences -> pygame KEYDOWN/KEYUP when SDL is headless."""

import os

import pygame

import stdin_keys


def test_feed_arrow_up_emits_keydown_then_keyup_on_next_feed():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.event.clear()
    stdin_keys._stdin_buf.clear()
    stdin_keys._pending_keyup_key = None
    stdin_keys.feed_stdin_bytes_for_tests(b"\x1b[A")
    events = pygame.event.get()
    downs = [e for e in events if e.type == pygame.KEYDOWN]
    ups = [e for e in events if e.type == pygame.KEYUP]
    assert len(downs) == 1 and downs[0].key == pygame.K_UP
    assert len(ups) == 0
    stdin_keys.feed_stdin_bytes_for_tests(b"")
    events = pygame.event.get()
    ups = [e for e in events if e.type == pygame.KEYUP]
    assert len(ups) == 1 and ups[0].key == pygame.K_UP


def test_feed_enter_emits_return():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.event.clear()
    stdin_keys._stdin_buf.clear()
    stdin_keys._pending_keyup_key = None
    stdin_keys.feed_stdin_bytes_for_tests(b"\n")
    events = pygame.event.get()
    downs = [e for e in events if e.type == pygame.KEYDOWN]
    assert downs and downs[0].key == pygame.K_RETURN
