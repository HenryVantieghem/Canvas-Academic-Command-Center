from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from academics.canvas import CanvasClient, CanvasError
from academics.core import slug
from academics.env import load_env


class CoreTests(unittest.TestCase):
    def test_slug_is_filesystem_safe(self):
        self.assertEqual(slug("MATH 101 / Section 2"), "MATH-101-Section-2")

    def test_env_loader_does_not_override_existing_values(self):
        import os
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / ".env"
            path.write_text("EXAMPLE_VALUE=from-file\n")
            os.environ["EXAMPLE_VALUE"] = "already-set"
            load_env(path)
            self.assertEqual(os.environ["EXAMPLE_VALUE"], "already-set")
            del os.environ["EXAMPLE_VALUE"]

    def test_client_requires_url(self):
        with self.assertRaises(CanvasError):
            CanvasClient("not-a-url", "token")


if __name__ == "__main__":
    unittest.main()
