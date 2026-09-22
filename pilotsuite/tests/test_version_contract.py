from __future__ import annotations

import re
import unittest
from pathlib import Path

from pilotsuite import VERSION


ROOT = Path(__file__).resolve().parents[2]


class VersionContractTests(unittest.TestCase):
    def test_all_release_markers_match(self) -> None:
        root_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        config = (ROOT / "pilotsuite" / "config.yaml").read_text(encoding="utf-8")
        match = re.search(r"^version:\s*(\S+)\s*$", config, re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(VERSION, root_version)
        self.assertEqual(VERSION, match.group(1))


if __name__ == "__main__":
    unittest.main()

