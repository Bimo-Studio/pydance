"""Regression and integration-style tests using bundled fixtures (no songs/ copy required)."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fileparsers import DanceFile, GenericFile, SongItem

logger = logging.getLogger(__name__)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MINIMAL_DANCE = FIXTURES / "minimal.dance"


class MockPlayer:
    """Minimal player config for steps.Steps (matches existing tests)."""

    def __init__(self):
        self.target_bpm = None
        self.speed = 1.0
        self.transform = 0
        self.holds = 1
        self.size = 0
        self.jumps = 1
        self.secret_kind = 1
        self.colortype = 4
        self.scrollstyle = 0
        self.fade = 0


def test_minimal_dance_fixture_exists():
    assert MINIMAL_DANCE.is_file()
    assert (FIXTURES / "dummy.ogg").is_file()


def test_dance_file_parses_fixture():
    df = DanceFile(str(MINIMAL_DANCE), need_steps=True)
    assert df.info["title"] == "Fixture"
    assert float(df.info["bpm"]) == 120.0
    assert "SINGLE" in df.steps
    assert "BASIC" in df.steps["SINGLE"]
    raw = df.steps["SINGLE"]["BASIC"]
    assert len(raw) == 3


def test_song_item_loads_fixture():
    song = SongItem(str(MINIMAL_DANCE))
    assert song.info["title"] == "Fixture"
    assert song.info["recordkey"] == "nomixfixturex"
    assert "SINGLE" in song.steps and "BASIC" in song.difficulty["SINGLE"]


def test_steps_object_from_fixture():
    import steps

    song = SongItem(str(MINIMAL_DANCE))
    step_obj = steps.Steps(song, "BASIC", MockPlayer(), 0, None, "SINGLE", 0)
    assert step_obj.totalarrows >= 1
    assert len(step_obj.events) >= 1


@pytest.mark.parametrize(
    ("string", "gap", "want"),
    [
        ("1:30.5", 0.0, 60 * 1 + 30.5),
        ("90", 0.0, 90 / 1000.0),
        ("2.5", 0.0, 2.5),
        ("+1000", 500.0, 500.0 + 1000 / 1000.0),
    ],
)
def test_parse_time_formats(string: str, gap: float, want: float):
    gf = GenericFile.__new__(GenericFile)
    gf.info = {"gap": gap}
    got = gf.parse_time(string)
    assert abs(got - want) < 1e-6
