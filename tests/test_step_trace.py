"""step_trace: optional env-gated logging for the step → sprite → draw pipeline."""

import os

import step_trace


def test_enabled_off_by_default():
    os.environ.pop("PYDANCE_TRACE_STEPS", None)
    assert step_trace.enabled() is False


def test_enabled_respects_env():
    for v in ("1", "true", "yes"):
        os.environ["PYDANCE_TRACE_STEPS"] = v
        assert step_trace.enabled() is True
    os.environ["PYDANCE_TRACE_STEPS"] = "0"
    assert step_trace.enabled() is False
    os.environ.pop("PYDANCE_TRACE_STEPS", None)


def test_log_steps_loaded_no_crash_when_disabled():
    os.environ.pop("PYDANCE_TRACE_STEPS", None)

    class _Ev:
        feet = (1, 0, 0, 0)

    class _Steps:
        events = [_Ev()]
        playmode = "SINGLE"
        difficulty = "BASIC"
        totalarrows = 1
        ready = 0.0
        length = 10.0
        offset = 0.0

    step_trace.log_steps_loaded(_Steps(), "/tmp/fake.dance")
