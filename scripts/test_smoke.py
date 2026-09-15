#!/usr/bin/env python3
"""Regression tests for scripts/smoke.py (stdlib only)."""
import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

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


class FakeOnlineResponse:
    """Minimal urlopen context manager stub (status + range-limited read)."""

    def __init__(self, code=200):
        self.status = code

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, n=-1):
        return b"x" * 8

    def getcode(self):
        return self.status


def http_error(url, code):
    return urllib.error.HTTPError(url, code, f"HTTP {code}", None, None)


class OnlineCheckTests(unittest.TestCase):
    def test_online_200_is_ok(self):
        with patch("urllib.request.urlopen", return_value=FakeOnlineResponse(200)):
            status, _detail = smoke.check_one_url("https://example.com/")
        self.assertEqual(status, "OK")

    def test_online_404_is_fail(self):
        err404 = http_error("https://example.com/nope", 404)
        with patch("urllib.request.urlopen", side_effect=err404):
            status, _detail = smoke.check_one_url("https://example.com/nope")
        self.assertEqual(status, "FAIL")

    def test_online_linkedin_403_is_warn(self):
        # LinkedIn blocks bots; must never fail the job.
        err403 = http_error("https://www.linkedin.com/in/cortega26", 403)
        with patch("urllib.request.urlopen", side_effect=err403):
            status, _detail = smoke.check_one_url("https://www.linkedin.com/in/cortega26")
        self.assertEqual(status, "WARN")

    def test_online_dns_error_is_fail(self):
        dns_err = urllib.error.URLError("Name or service not known")
        with patch("urllib.request.urlopen", side_effect=dns_err):
            status, _detail = smoke.check_one_url("https://nonexistent.invalid/")
        self.assertEqual(status, "FAIL")

    def test_online_head_405_falls_back_to_get(self):
        def fake_open(req, timeout=None):
            if req.get_method() == "HEAD":
                raise http_error(req.full_url, 405)
            return FakeOnlineResponse(200)

        with patch("urllib.request.urlopen", side_effect=fake_open) as m:
            status, _detail = smoke.check_one_url("https://example.com/")
        self.assertEqual(status, "OK")
        self.assertEqual(m.call_count, 2)

    def test_offline_main_ignores_online_without_network(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            make_valid_root(tmpdir)
            write(
                os.path.join(tmpdir, "index.md"),
                "# Index\n\nSee [ok](https://example.com/) and [gone](nope.md).\n",
            )
            no_net = AssertionError("offline path must not touch network")
            with patch("urllib.request.urlopen", side_effect=no_net):
                self.assertEqual(smoke.main(tmpdir), 1)

    def test_online_failures_counted_in_footer(self):
        def fake_open(req, timeout=None):
            if "example.com" in req.full_url:
                raise http_error(req.full_url, 404)
            return FakeOnlineResponse(200)

        with tempfile.TemporaryDirectory() as tmpdir:
            make_valid_root(tmpdir)
            write(
                os.path.join(tmpdir, "index.md"),
                "# Index\n\nSee [ok](https://example.com/).\n",
            )
            buf = io.StringIO()
            with patch("urllib.request.urlopen", side_effect=fake_open):
                with contextlib.redirect_stdout(buf):
                    rc = smoke.main(tmpdir, True)
        self.assertEqual(rc, 1)
        # 0 offline problems + 1 stubbed online FAIL = combined footer.
        self.assertIn("\nsmoke FAILED: 1 problem(s)", buf.getvalue())


PARITY_README = (
    "# Title\n\n"
    "[site](https://tooltician.com/) "
    "[li](https://www.linkedin.com/in/cortega26)\n\n"
    "## Featured Projects\n\n"
    "- [a](https://github.com/cortega26/a) — A.\n"
    "- [b](https://example.com/b) — B.\n\n"
    "## Next\n\n"
    "<details>\n<summary>ES</summary>\n\n"
    "#### Proyectos destacados\n\n"
    "- [a](https://github.com/cortega26/a) — A es.\n"
    "- [b](https://example.com/b) — B es.\n\n"
    "#### Fin\n\n</details>\n"
)


def make_parity_root(tmpdir, readme_content=PARITY_README):
    write(os.path.join(tmpdir, "README.md"), readme_content)
    write(os.path.join(tmpdir, "TOOLTICIAN.md"), "# Tool\n")


class ProjectParityTests(unittest.TestCase):
    def test_parity_match_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            make_parity_root(tmpdir)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = smoke.main(tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("project lists match", buf.getvalue())

    def test_parity_es_drift_fails(self):
        bad = PARITY_README.replace(
            "- [a](https://github.com/cortega26/a) — A es.",
            "- [a](https://github.com/cortega26/a-fork) — A es.",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            make_parity_root(tmpdir, bad)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = smoke.main(tmpdir)
        self.assertEqual(rc, 1)
        self.assertIn("project mismatch", buf.getvalue())
        self.assertIn("only in ES", buf.getvalue())

    def test_parity_missing_entry_fails(self):
        bad = PARITY_README.replace(
            "- [b](https://example.com/b) — B es.\n", ""
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            make_parity_root(tmpdir, bad)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = smoke.main(tmpdir)
        self.assertEqual(rc, 1)
        self.assertIn("project mismatch", buf.getvalue())
        self.assertIn("only in EN", buf.getvalue())

    def test_parity_skipped_without_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            make_valid_root(tmpdir)  # no Featured sections
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = smoke.main(tmpdir)
        self.assertEqual(rc, 0)
        self.assertNotIn("project lists match", buf.getvalue())
        self.assertNotIn("project mismatch", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
