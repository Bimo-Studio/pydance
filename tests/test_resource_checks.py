"""resource_checks: startup file presence checks."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestResourceChecks(unittest.TestCase):
    def test_verify_install_layout_returns_list(self):
        import resource_checks

        missing = resource_checks.verify_install_layout()
        self.assertIsInstance(missing, list)
        # In a full checkout, required theme/menu assets should exist.
        self.assertEqual(
            missing,
            [],
            "expected repo install files under pydance_path (run from project root)",
        )


if __name__ == "__main__":
    unittest.main()
