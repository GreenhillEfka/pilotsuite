"""Synthetic Git repositories; no network, household data or HA mutations."""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "release_preflight", Path(__file__).resolve().parents[2] / "scripts/release_preflight.py")
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class ReleasePreflightTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Synthetic test")
        self.git("config", "user.email", "test@example.invalid")
        self.old = self.commit_version(14)

    def git(self, *args):
        return release.git(self.root, *args)

    def commit_version(self, number, override=None):
        version = f"0.1.0-alpha.{number}"
        files = {"VERSION": version, "pilotsuite/config.yaml": f"version: {version}",
                 "pilotsuite/pilotsuite/__init__.py": f'VERSION = "{version}"',
                 "pilotsuite/Dockerfile": f'ARG BUILD_VERSION="{version}"',
                 "pilotsuite/DOCS.md": f"- Release: `{version}`",
                 "CHANGELOG.md": f"## [{version}] - 2026-09-23",
                 "pilotsuite/CHANGELOG.md": f"## [{version}] - 2026-09-23"}
        files.update(override or {})
        for name, content in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content + "\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "synthetic", "--allow-empty")
        return self.git("rev-parse", "HEAD")

    def test_new_release_has_exact_identity_but_no_deployment_authority(self):
        new = self.commit_version(15)
        result = release.preflight(self.root, new, self.old)
        self.assertEqual(result["candidate"]["commit"], new)
        self.assertEqual(result["candidate"]["app_tree"], self.git("rev-parse", "HEAD:pilotsuite"))
        self.assertFalse(result["deployment_authorized"])
        self.assertEqual(len(result["remaining_gates"]), 4)

    def test_same_or_older_version_is_rejected(self):
        for number in (14, 13):
            with self.subTest(number=number), self.assertRaisesRegex(ValueError, "newer"):
                release.preflight(self.root, self.commit_version(number), self.old)

    def test_each_stale_marker_is_rejected(self):
        for path in release.MARKERS:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "marker mismatch"):
                release.preflight(self.root, self.commit_version(15, {path: "stale"}), self.old)

    def test_both_changelogs_are_required(self):
        for path in ("CHANGELOG.md", "pilotsuite/CHANGELOG.md"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "changelog"):
                release.preflight(self.root, self.commit_version(15, {path: "Unreleased"}), self.old)

    def test_working_tree_does_not_change_committed_receipt(self):
        new = self.commit_version(15)
        (self.root / "VERSION").write_text("dirty", encoding="utf-8")
        self.assertEqual(release.preflight(self.root, new, self.old)["candidate"]["version"], "0.1.0-alpha.15")

    def test_missing_commit_fails_closed(self):
        with self.assertRaises(subprocess.CalledProcessError):
            release.preflight(self.root, "missing-ref", self.old)

    def test_non_descendant_fails_closed(self):
        self.git("checkout", "--orphan", "unrelated")
        with self.assertRaises(subprocess.CalledProcessError):
            release.preflight(self.root, self.commit_version(15), self.old)

    def test_ci_allows_documentation_only_with_identical_published_app_tree(self):
        (self.root / "NOTE.md").write_text("Synthetic documentation only\n")
        self.git("add", "."); self.git("commit", "-qm", "docs")
        result = release.check_source(self.root, "HEAD", self.old)
        self.assertEqual("unchanged_published_application", result["source_check"])
        self.assertFalse(result["deployment_authorized"])
        self.assertEqual(self.git("rev-parse", "HEAD:pilotsuite"), result["candidate"]["app_tree"])

    def test_ci_rejects_same_version_even_when_only_test_in_app_tree_changes(self):
        candidate = self.commit_version(14, {"pilotsuite/test.txt": "changed"})
        with self.assertRaisesRegex(ValueError, "reuses a published version"):
            release.check_source(self.root, candidate, self.old)

    def test_ci_new_version_still_requires_all_release_gates(self):
        candidate = self.commit_version(15)
        self.assertEqual(release.preflight(self.root, candidate, self.old),
                         release.check_source(self.root, candidate, self.old))

    def test_ci_rejects_older_version_and_unrelated_same_version(self):
        with self.assertRaisesRegex(ValueError, "newer"):
            release.check_source(self.root, self.commit_version(13), self.old)
        self.git("checkout", "--orphan", "unrelated-same")
        with self.assertRaises(subprocess.CalledProcessError):
            release.check_source(self.root, self.commit_version(14, {"NOTE.md": "unrelated root"}), self.old)
