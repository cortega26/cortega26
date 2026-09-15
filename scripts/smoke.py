#!/usr/bin/env python3
"""Profile-surface smoke check for the github-profile repo (stdlib only).

Gates the only thing this repo ships: profile markdown + its link surface.
Run:  python3 scripts/smoke.py [--root PATH]

Checks:
  1. README.md and TOOLTICIAN.md exist.
  2. Fenced code blocks are balanced in every *.md file.
  3. Every inline markdown link has non-empty text and a well-formed URL
     (http(s) URLs need a host; mailto: needs an address).
  4. Relative links resolve to a file on disk.
  5. README keeps the profile surface links (portfolio, LinkedIn, GitHub).

Exit 0 when all checks pass, 1 otherwise. No network access, no deps.
"""
import os
import re
import sys
from urllib.parse import urlparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

SURFACE_URLS = [
    "https://tooltician.com/",
    "https://www.linkedin.com/in/cortega26",
]

failures = []


def fail(msg):
    failures.append(msg)
    print(f"FAIL {msg}")


def ok(label):
    print(f"PASS {label}")


def surface_missing(readme_targets, surface_urls):
    """Which required surface URLs lack an exact link target."""
    targets = set(readme_targets)
    return [u for u in surface_urls if u not in targets]


def main(root):
    global failures
    failures = []
    md_files = []
    readme_targets = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", ".codegraph")]
        for fname in filenames:
            if fname.endswith(".md"):
                md_files.append(os.path.join(dirpath, fname))

    # 1. required files
    for required in ("README.md", "TOOLTICIAN.md"):
        if os.path.isfile(os.path.join(root, required)):
            ok(f"required file present: {required}")
        else:
            fail(f"required file missing: {required}")

    # 2. balanced fences
    fence_ok = True
    for fpath in md_files:
        with open(fpath, encoding="utf-8") as f:
            text = f.read()
        if text.count("```") % 2 != 0:
            fail(f"unbalanced code fences in {os.path.relpath(fpath, root)}")
            fence_ok = False
    if fence_ok:
        ok("code fences balanced in all markdown files")

    # 3+4. link validity + relative resolution
    link_failures = 0
    all_urls = set()
    for fpath in sorted(md_files):
        rel = os.path.relpath(fpath, root)
        with open(fpath, encoding="utf-8") as f:
            text = f.read()
        in_fence = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue  # template examples, not real links
            for m in LINK_RE.finditer(line):
                label, target = m.group(1), m.group(2)
                if not label.strip():
                    fail(f"{rel}:{lineno}: empty link text")
                    link_failures += 1
                if not target.strip():
                    fail(f"{rel}:{lineno}: empty link URL")
                    link_failures += 1
                    continue
                all_urls.add(target)
                if target.startswith("mailto:"):
                    addr = target[len("mailto:"):]
                    if "@" not in addr or " " in addr:
                        fail(f"{rel}:{lineno}: malformed mailto: {target!r}")
                        link_failures += 1
                elif target.startswith(("http://", "https://")):
                    if not urlparse(target).netloc:
                        fail(f"{rel}:{lineno}: URL without host: {target!r}")
                        link_failures += 1
                    if rel == "README.md":
                        readme_targets.add(target)
                elif target.startswith("#"):
                    continue  # same-page anchor; out of scope for a smoke gate
                else:
                    path_part = target.split("#", 1)[0]
                    if not path_part:
                        continue  # pure "#anchor" on a relative line; same-page anchor
                    resolved = os.path.normpath(
                        os.path.join(os.path.dirname(fpath), path_part)
                    )
                    if not os.path.exists(resolved):
                        fail(f"{rel}:{lineno}: relative link target missing: {target!r}")
                        link_failures += 1
    if link_failures == 0:
        ok(f"all markdown links well-formed ({len(all_urls)} unique URLs)")

    # 5. profile surface links in README
    readme_path = os.path.join(root, "README.md")
    if os.path.isfile(readme_path):
        missing = surface_missing(readme_targets, SURFACE_URLS)
        if missing:
            fail(f"README missing profile surface links: {missing}")
        else:
            ok("README keeps portfolio/LinkedIn/GitHub surface links")

    if failures:
        print(f"\nsmoke FAILED: {len(failures)} problem(s)")
        return 1
    print("\nsmoke passed")
    return 0


if __name__ == "__main__":
    root = REPO_ROOT
    if "--root" in sys.argv:
        idx = sys.argv.index("--root")
        if idx + 1 >= len(sys.argv):
            print("usage: python3 scripts/smoke.py [--root PATH]", file=sys.stderr)
            sys.exit(2)
        root = sys.argv[idx + 1]
    sys.exit(main(root))
