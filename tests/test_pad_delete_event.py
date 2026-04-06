"""pad.Pad.delete_event / delete_events: safe dict mutation and state keys."""

from pad import Pad


def test_delete_event_no_dict_changed_during_iteration():
    p = object.__new__(Pad)
    p.events = {(-1, 50): (0, 2), (-1, 51): (0, 3)}
    p.states = {(0, 2): False, (0, 3): False}
    Pad.delete_event(p, 0, True, 2)
    assert (-1, 50) not in p.events
    assert (0, 2) not in p.states
    assert (-1, 51) in p.events


def test_delete_event_removes_all_keyboard_bindings_for_same_direction():
    p = object.__new__(Pad)
    p.events = {(-1, 50): (0, 2), (-1, 52): (0, 2)}
    p.states = {(0, 2): False}
    Pad.delete_event(p, 0, True, 2)
    assert p.events == {}
    assert (0, 2) not in p.states


def test_delete_events_removes_pid():
    p = object.__new__(Pad)
    p.events = {(-1, 1): (0, 2), (0, 3): (1, 4)}
    p.states = {(0, 2): False, (1, 4): False}
    Pad.delete_events(p, 0)
    assert (-1, 1) not in p.events
    assert (0, 3) in p.events
    assert (0, 2) not in p.states
    assert (1, 4) in p.states
