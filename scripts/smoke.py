#!/usr/bin/env python3
"""Profile-surface smoke check for the github-profile repo (stdlib only).

Gates the only thing this repo ships: profile markdown + its link surface.
Run:  python3 scripts/smoke.py [--root PATH] [--check-online]

Checks:
  1. README.md and TOOLTICIAN.md exist.
  2. Fenced code blocks are balanced in every *.md file.
  3. Every inline markdown link has non-empty text and a well-formed URL
     (http(s) URLs need a host; mailto: needs an address).
  4. Relative links resolve to a file on disk.
  5. README keeps the profile surface links (portfolio, LinkedIn).
  6. README EN/ES featured-project lists match (same link targets).

Exit 0 when all checks pass, 1 otherwise. No network access unless
`--check-online` is passed, no deps.
"""
import os
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

SURFACE_URLS = [
    "https://tooltician.com/",
    "https://www.linkedin.com/in/cortega26",
]

failures = []

ONLINE_USER_AGENT = "github-profile-smoke (+https://tooltician.com/)"
ONLINE_TIMEOUT = 10
ONLINE_MAX_BYTES = 8192


def fail(msg):
    failures.append(msg)
    print(f"FAIL {msg}")


def ok(label):
    print(f"PASS {label}")


def surface_missing(readme_targets, surface_urls):
    """Which required surface URLs lack an exact link target."""
    targets = set(readme_targets)
    return [u for u in surface_urls if u not in targets]


def featured_targets(lines, start, end_prefixes):
    """First-link http(s) targets of `- [` bullets between markers.

    Used for the EN/ES featured-project parity check: the English list
    lives under `## Featured Projects`, the Spanish mirror under
    `#### Proyectos destacados`. A missing start marker yields no targets
    (check skipped) so minimal fixtures stay valid.
    """
    targets = []
    in_section = False
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not in_section:
            if stripped == start:
                in_section = True
            continue
        if stripped.startswith(end_prefixes) or stripped == "</details>":
            break
        if stripped.startswith("- ["):
            for m in LINK_RE.finditer(line):
                target = m.group(2)
                if target.startswith(("http://", "https://")):
                    targets.append(target)
                    break  # first link = the project link
    return targets


def classify_http_status(url, code):
    """WARN for known bot-blockers/rate-limiters, FAIL otherwise.

    WARN: linkedin.com 403/999, any host 403/429, any img.shields.io
    non-2xx (badge CDN rate-limits bots). Everything else non-2xx FAILs.
    """
    host = urlparse(url).netloc.lower()
    if host == "img.shields.io":
        return "WARN"
    if code in (403, 429):
        return "WARN"
    if code == 999 and (host == "linkedin.com" or host.endswith(".linkedin.com")):
        return "WARN"
    return "FAIL"


def _response_code(resp):
    code = getattr(resp, "status", None)
    if code is None:
        try:
            code = resp.getcode()
        except Exception:
            code = None
    return code


def _fetch_once(url, method):
    """Single HTTP attempt. Returns (code, detail); raises on network error."""
    req = urllib.request.Request(
        url, method=method, headers={"User-Agent": ONLINE_USER_AGENT}
    )
    with urllib.request.urlopen(req, timeout=ONLINE_TIMEOUT) as resp:
        if method == "GET":
            resp.read(ONLINE_MAX_BYTES)
        code = _response_code(resp)
        if code is None:
            return 200, "HTTP 200"
        return code, f"HTTP {code}"


def check_one_url(url):
    """Check a single URL. Returns (status, detail) with status OK/WARN/FAIL."""
    try:
        code, detail = _fetch_once(url, "HEAD")
    except urllib.error.HTTPError as e:
        if e.code in (405, 501) or 500 <= e.code <= 599:
            pass  # fall through to GET retry below
        else:
            return classify_http_status(url, e.code), f"HTTP {e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        reason = getattr(e, "reason", e)
        return "FAIL", f"{type(e).__name__}: {reason}"
    except Exception as e:  # one bad URL must not crash the whole run
        return "FAIL", f"{type(e).__name__}: {e}"
    else:
        if 200 <= code < 300:
            return "OK", detail
        if code in (405, 501) or 500 <= code <= 599:
            pass  # HEAD unsupported or server error: retry with GET
        else:
            return classify_http_status(url, code), detail
    # GET retry (HEAD unsupported or HEAD drew a 5xx): range-limited read.
    try:
        code, detail = _fetch_once(url, "GET")
    except urllib.error.HTTPError as e:
        return classify_http_status(url, e.code), f"HTTP {e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        reason = getattr(e, "reason", e)
        return "FAIL", f"{type(e).__name__}: {reason}"
    except Exception as e:
        return "FAIL", f"{type(e).__name__}: {e}"
    if 200 <= code < 300:
        return "OK", detail
    return classify_http_status(url, code), detail


def check_online(urls):
    """Check external URLs, print per-URL lines + summary. Returns fail count."""
    n_ok = n_warn = n_fail = 0
    for url in sorted(urls):
        status, detail = check_one_url(url)
        print(f"ONLINE {status} {url} ({detail})")
        if status == "OK":
            n_ok += 1
        elif status == "WARN":
            n_warn += 1
        else:
            n_fail += 1
    print(f"online: {n_ok} ok, {n_warn} warn, {n_fail} fail")
    return n_fail


def main(root, do_online=False):
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
            ok("README keeps portfolio/LinkedIn surface links")

    # 6. EN/ES featured-project parity (same link targets, both languages)
    if os.path.isfile(readme_path):
        with open(readme_path, encoding="utf-8") as f:
            readme_lines = f.read().splitlines()
        en_targets = featured_targets(
            readme_lines, "## Featured Projects", ("## ",)
        )
        es_targets = featured_targets(
            readme_lines, "#### Proyectos destacados", ("#### ",)
        )
        if en_targets or es_targets:
            en_only = sorted(set(en_targets) - set(es_targets))
            es_only = sorted(set(es_targets) - set(en_targets))
            if en_only or es_only:
                fail(
                    "README EN/ES project mismatch: "
                    f"only in EN: {en_only}; only in ES: {es_only}"
                )
            else:
                ok(
                    "README EN/ES project lists match "
                    f"({len(set(en_targets))} targets)"
                )

    online_fails = 0
    if do_online:
        http_urls = [
            u for u in all_urls if u.startswith(("http://", "https://"))
        ]
        online_fails = check_online(http_urls)

    if failures or online_fails:
        total = len(failures) + online_fails
        print(f"\nsmoke FAILED: {total} problem(s)")
        return 1
    print("\nsmoke passed")
    return 0


if __name__ == "__main__":
    root = REPO_ROOT
    if "--root" in sys.argv:
        idx = sys.argv.index("--root")
        if idx + 1 >= len(sys.argv):
            print(
                "usage: python3 scripts/smoke.py [--root PATH] [--check-online]",
                file=sys.stderr,
            )
            sys.exit(2)
        root = sys.argv[idx + 1]
    do_online = "--check-online" in sys.argv
    sys.exit(main(root, do_online))
