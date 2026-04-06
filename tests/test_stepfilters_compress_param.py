"""Parametrized tests for stepfilters.compress."""

import logging

logger = logging.getLogger(__name__)

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import stepfilters


@pytest.mark.parametrize(
    "steps",
    [
        [
            [1.0, 1, 0, 0, 0],
            [1.0, 0, 0, 0, 0],
            ["D", 4.0],
        ],
        [[4.0, 0, 1, 0, 0], ["D", 8.0]],
    ],
)
def test_compress_runs_and_returns_list(steps):
    out = stepfilters.compress(steps)
    assert isinstance(out, list)
    assert len(out) >= 1


def test_compress_merges_leading_empty_beats():
    steps = [
        [1.0, 0, 0, 0, 0],
        [1.0, 0, 0, 0, 0],
        [1.0, 1, 0, 0, 0],
        ["D", 2.0],
    ]
    out = stepfilters.compress(steps)
    assert out[0][0] == 2.0
