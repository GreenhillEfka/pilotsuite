#!/usr/bin/env python3
"""Fail when unittest would silently ignore a Python test module/function."""
from __future__ import annotations
import argparse
import ast
from collections import Counter
from pathlib import Path
import sys
import unittest


def source_issues(source: str, label: str) -> list[str]:
    tree = ast.parse(source, filename=label)
    return [f'{label}:{node.lineno}: module-level {node.name} is not collected by unittest'
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_')]


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def validate(directory: Path) -> tuple[list[str], int]:
    paths = sorted(directory.glob('test_*.py'))
    if not paths:
        return ['No test modules found'], 0
    errors = []
    for path in paths:
        try:
            errors.extend(source_issues(path.read_text(encoding='utf-8'), path.name))
        except (SyntaxError, UnicodeError) as exc:
            errors.append(f'{path.name}: {exc}')
    loader = unittest.TestLoader()
    suite = loader.discover(str(directory))
    errors.extend(loader.errors)
    collected = list(cases(suite))
    modules = Counter(case.__class__.__module__ for case in collected)
    for path in paths:
        if not modules[path.stem]:
            errors.append(f'{path.name}: no unittest cases collected')
    return errors, len(collected)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path,
                        default=Path(__file__).resolve().parents[1]/'pilotsuite'/'tests')
    args = parser.parse_args()
    errors, count = validate(args.directory.resolve())
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Test discovery: {count} unittest cases collected; no silently ignored modules/functions')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
