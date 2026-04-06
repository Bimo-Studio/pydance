"""sdl_env: idempotent SDL preconfiguration."""

import logging

logger = logging.getLogger(__name__)

import unittest


class TestSdlEnv(unittest.TestCase):
    def test_apply_twice_is_safe(self):
        import sdl_env

        sdl_env.apply()
        sdl_env.apply()


if __name__ == "__main__":
    unittest.main()
