#!/usr/bin/env python3
"""Regression tests for scripts/smoke.py (stdlib only)."""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

SMOKE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smoke.py")


def load_smoke():
    spec = importlib.util.spec_from_file_location("smoke", SMOKE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


smoke = load_smoke()

VALID_README = (
    "# Title\n\n"
    "[site](https://tooltician.com/) "
    "[li](https://www.linkedin.com/in/cortega26)\n"
)


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def make_valid_root(tmpdir, readme_content=VALID_README):
    write(os.path.join(tmpdir, "README.md"), readme_content)
    write(os.path.join(tmpdir, "TOOLTICIAN.md"), "# Tool\n")


class SmokeRegressionTests(unittest.TestCase):
    def test_bare_root_flag_exits_2(self):
        proc = subprocess.run(
            [sys.executable, SMOKE_PATH, "--root"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("usage:", proc.stderr + proc.stdout)

    def test_double_main_resets_failures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            make_valid_root(tmpdir)
            # Pollute with a failing run first so a missing reset would leak.
            self.assertEqual(smoke.main(os.path.join(tmpdir, "does-not-exist")), 1)
            self.assertEqual(smoke.main(tmpdir), 0)
            self.assertEqual(smoke.main(tmpdir), 0)

    def test_fragment_link_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            make_valid_root(tmpdir)
            write(
                os.path.join(tmpdir, "index.md"),
                "# Index\n\nSee [other](other.md#sec).\n",
            )
            write(os.path.join(tmpdir, "other.md"), "# Other\n\nHi.\n")
            self.assertEqual(smoke.main(tmpdir), 0)

    def test_missing_relative_target_still_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            make_valid_root(tmpdir)
            write(
                os.path.join(tmpdir, "index.md"),
                "# Index\n\nSee [gone](nope.md).\n",
            )
            self.assertEqual(smoke.main(tmpdir), 1)

    def test_unbalanced_fences_still_fail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            make_valid_root(tmpdir)
            write(
                os.path.join(tmpdir, "bad.md"),
                "# Bad\n\n```python\nprint('oops')\n",
            )
            self.assertEqual(smoke.main(tmpdir), 1)

    def test_surface_missing_exact_present(self):
        missing = smoke.surface_missing(
            {"https://tooltician.com/", "https://www.linkedin.com/in/cortega26"},
            smoke.SURFACE_URLS,
        )
        self.assertEqual(missing, [])

    def test_surface_missing_rejects_substring(self):
        # Regression test for the live 2026-09-15 misfire: a bare domain
        # requirement must not be satisfied by longer suffixed targets.
        missing = smoke.surface_missing(
            {
                "https://github.com/cortega26/polla",
                "https://github.com/cortega26/tool",
            },
            ["https://github.com/cortega26"],
        )
        self.assertEqual(missing, ["https://github.com/cortega26"])

    def test_surface_missing_empty_targets(self):
        missing = smoke.surface_missing(set(), smoke.SURFACE_URLS)
        self.assertEqual(missing, list(smoke.SURFACE_URLS))


if __name__ == "__main__":
    unittest.main()
