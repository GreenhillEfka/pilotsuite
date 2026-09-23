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
        dockerfile = (ROOT / "pilotsuite" / "Dockerfile").read_text(encoding="utf-8")
        docker_version = re.search(r'^ARG BUILD_VERSION="([^"]+)"', dockerfile, re.MULTILINE)
        self.assertIsNotNone(docker_version)
        self.assertEqual(VERSION, docker_version.group(1))

        docs = (ROOT / "pilotsuite" / "DOCS.md").read_text(encoding="utf-8")
        self.assertIn(f"Release: `{VERSION}`", docs)

    def test_web_shell_does_not_embed_a_stale_release_number(self) -> None:
        index = (
            ROOT / "pilotsuite" / "pilotsuite" / "web" / "index.html"
        ).read_text(encoding="utf-8")
        self.assertNotRegex(index, r"0\.1\.0-alpha\.\d+")


if __name__ == "__main__":
    unittest.main()
