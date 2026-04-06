import logging

logger = logging.getLogger(__name__)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestStepsObject(unittest.TestCase):
    def setUp(self):
        # Mock player for Steps initialization
        class MockPlayer:
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

        self.mock_player = MockPlayer()
        self.song_file = "songs/6jan.dance"

    def test_create_steps_object(self):
        """Test that Steps object can be created"""
        import steps
        from fileparsers import SongItem

        song = SongItem(self.song_file)
        step_obj = steps.Steps(song, "BASIC", self.mock_player, 0, None, "SINGLE", 0)
        self.assertIsNotNone(step_obj)
        self.assertGreater(step_obj.totalarrows, 0)
        print(f"Steps object created: {step_obj.totalarrows} total arrows")

    def test_events_have_appear_times(self):
        """Test that events have valid appear times"""
        import steps
        from fileparsers import SongItem

        song = SongItem(self.song_file)
        step_obj = steps.Steps(song, "BASIC", self.mock_player, 0, None, "SINGLE", 0)

        events_with_appear = [ev for ev in step_obj.events if ev.appear is not None]
        self.assertGreater(len(events_with_appear), 0)
        print(f"Found {len(events_with_appear)} events with appear times")

    def test_get_events_skips_header_and_emits_nevents(self):
        """First chart event has appear=None; nevent_idx must advance or scrolling arrows never spawn."""
        import steps
        from fileparsers import SongItem

        song = SongItem(self.song_file)
        step_obj = steps.Steps(song, "BASIC", self.mock_player, 0, None, "SINGLE", 0)
        self.assertIsNone(
            step_obj.events[0].appear,
            "sanity: index-0 marker should not have appear time",
        )
        step_obj.play()
        _events, nevents, _t, _bpm = step_obj.get_events(10.0)
        self.assertGreater(
            len(nevents),
            0,
            "get_events must emit foot events after time passes appear threshold",
        )


if __name__ == "__main__":
    unittest.main()
