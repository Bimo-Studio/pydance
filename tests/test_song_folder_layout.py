"""Per-song folders under songdir: mix inference and audio fallback."""

import logging
import os
import sys
import tempfile
import unittest

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


MINIMAL_DANCE = """filename song.ogg
title Unit
artist Unit
author test
bpm 120.0
gap 0.0
end
SINGLE
BASIC 1
D 0
e 0000
q 1000
"""


class TestSongFolderLayout(unittest.TestCase):
    def test_infer_mix_from_nested_path(self):
        import fileparsers
        from constants import mainconfig

        old = mainconfig["songdir"]
        tmp = tempfile.mkdtemp()
        try:
            mainconfig["songdir"] = tmp
            pack_dir = os.path.join(tmp, "MyPack", "SongFolder")
            os.makedirs(pack_dir)
            chart = os.path.join(pack_dir, "chart.dance")
            with open(chart, "w", encoding="utf-8") as f:
                f.write(MINIMAL_DANCE)
            ogg = os.path.join(pack_dir, "song.ogg")
            with open(ogg, "wb") as f:
                f.write(b"\0" * 16)

            df = fileparsers.DanceFile(chart, need_steps=True)
            self.assertEqual(df.info.get("mix"), "MyPack")
            self.assertTrue(os.path.isfile(df.info["filename"]))
        finally:
            mainconfig["songdir"] = old

    def test_fallback_audio_matches_stem(self):
        import fileparsers
        from constants import mainconfig

        old = mainconfig["songdir"]
        tmp = tempfile.mkdtemp()
        try:
            mainconfig["songdir"] = tmp
            sdir = os.path.join(tmp, "onlysong")
            os.makedirs(sdir)
            chart = os.path.join(sdir, "onlysong.dance")
            with open(chart, "w", encoding="utf-8") as f:
                f.write(MINIMAL_DANCE.replace("filename song.ogg", "filename missing.ogg"))
            mp3 = os.path.join(sdir, "onlysong.mp3")
            with open(mp3, "wb") as f:
                f.write(b"\0" * 16)

            df = fileparsers.DanceFile(chart, need_steps=True)
            self.assertEqual(df.info["filename"], mp3)
        finally:
            mainconfig["songdir"] = old


if __name__ == "__main__":
    unittest.main()
