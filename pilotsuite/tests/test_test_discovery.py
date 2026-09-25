"""Regression: PR #54 originally contained five tests that CI never executed."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2]/'scripts'/'validate_test_discovery.py'


class TestDiscoveryTests(unittest.TestCase):
    def run_fixture(self, source):
        with tempfile.TemporaryDirectory(prefix='discovery-contract-') as temp:
            root = Path(temp)
            (root/'test_synthetic_discovery.py').write_text(source, encoding='utf-8')
            return subprocess.run([sys.executable, str(SCRIPT), '--directory', str(root)],
                                  capture_output=True, text=True, timeout=15)

    def test_module_function_is_not_silently_accepted(self):
        result = self.run_fixture('def test_synthetic():\n    assert True\n')
        self.assertEqual(1, result.returncode)
        self.assertIn('module-level test_synthetic', result.stderr)

    def test_async_function_is_also_not_collected(self):
        result = self.run_fixture('async def test_synthetic():\n    pass\n')
        self.assertEqual(1, result.returncode)

    def test_valid_unittest_class_is_counted_without_executing_it(self):
        source = 'import unittest\nclass T(unittest.TestCase):\n    def test_case(self):\n        raise AssertionError("not executed by discovery")\n'
        result = self.run_fixture(source)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('1 unittest cases', result.stdout)

    def test_mixed_module_cannot_hide_uncollected_functions(self):
        source = 'import unittest\nclass T(unittest.TestCase):\n    def test_case(self): pass\ndef test_hidden(): pass\n'
        result = self.run_fixture(source)
        self.assertEqual(1, result.returncode)
        self.assertIn('test_hidden', result.stderr)

    def test_empty_module_is_not_a_green_suite(self):
        result = self.run_fixture('# This is not a test\n')
        self.assertEqual(1, result.returncode)
        self.assertIn('no unittest cases', result.stderr)

    def test_import_errors_are_not_counted_as_valid_tests(self):
        result = self.run_fixture('raise RuntimeError("synthetic import failure")\n')
        self.assertEqual(1, result.returncode)
        self.assertIn('synthetic import failure', result.stderr)
