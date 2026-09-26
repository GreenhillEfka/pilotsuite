from __future__ import annotations

import re
import unittest
from pathlib import Path

from pilotsuite.app import create_app


ROOT = Path(__file__).resolve().parents[2]
DOCUMENTED_ROUTE = re.compile(
    r"^\| `(?P<method>GET|POST|PUT|PATCH|DELETE)` "
    r"\| `(?P<path>/api/v1[^`]*)` \|",
    re.MULTILINE,
)


class ApiDocumentationContractTests(unittest.TestCase):
    def test_every_registered_api_method_and_path_is_documented_once(self) -> None:
        app = create_app()
        registered = [
            (route.method, route.resource.canonical)
            for route in app.router.routes()
            if route.method != "HEAD" and route.resource.canonical.startswith("/api/v1")
        ]
        document = (ROOT / "docs" / "API.md").read_text(encoding="utf-8")
        documented = [match.groups() for match in DOCUMENTED_ROUTE.finditer(document)]

        self.assertEqual(len(registered), len(set(registered)), "duplicate registered API route")
        self.assertEqual(len(documented), len(set(documented)), "duplicate documented API route")
        self.assertEqual(
            set(registered),
            set(documented),
            "docs/API.md and the registered /api/v1 surface have drifted",
        )


if __name__ == "__main__":
    unittest.main()
