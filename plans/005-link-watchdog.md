# Plan 005: Add opt-in online check for external link rot

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` — unless a reviewer dispatched you and told you they
> maintain the index.
>
> **Drift check (run first)**: `git diff --stat 4ec3654..HEAD -- scripts/ .github/workflows/`
> If any in-scope file changed since this plan was written, compare the "Current state"
> excerpts against the live code before proceeding; on a mismatch, treat it
> as a STOP condition.

## Status

- **Priority**: P2
- **Effort**: M
- **Risk**: MED (touches the gate + adds a scheduled workflow; network
  flakiness is the inherent risk — contained by the design below)
- **Depends on**: plans/001-baseline-ci.md and plans/002-smoke-robustness.md
  (extends the committed, hardened script and the existing workflow)
- **Category**: tests
- **Planned at**: commit `cb3de7b`, 2026-09-15

## Why this matters

The offline gate proves links are well-formed, never that they resolve —
and every value this repo delivers is a link (portfolio, LinkedIn, seven
projects, badges). Renamed repos (`tuplatainforma` → `Monedario`, fixed in
plans/003 only because a human noticed) are exactly the rot class that
recurs silently. An opt-in online check — stdlib `urllib`, off by default
so the fast offline gate never flakes — plus a weekly scheduled workflow
closes the highest real user-facing risk on a hiring-surface page.

## Current state

The facts the executor needs, inlined:

- `scripts/smoke.py` docstring promises: "No network access, no deps"
  (`:15`). That promise is load-bearing for CI speed and for sandboxed
  executors. **Keep the default offline.** The online check is a separate
  `--check-online` flag, never part of the default run.
- After plans/002, `scripts/smoke.py` has: per-run `failures` reset, guarded
  `--root` parsing (exit 2 on misuse), `#fragment` stripping, `.git` +
  `.codegraph` skip, and `scripts/test_smoke.py` regression tests. Reuse the
  existing link-collection loop (`:73-113` in the `cb3de7b` tree) — collect
  the `http(s)` targets it already visits; do not write a second parser.
- Link surface today: 15 unique URLs (per smoke output), dominated by
  `tooltician.com/*`, `github.com/cortega26/*`, `linkedin.com/in/cortega26`,
  `monedario.cl`, `noticiencias.com`, `img.shields.io/*`, `pypi.org`-style
  badges in future entries.
- **Known bot-blocker (encode this, don't discover it):**
  `linkedin.com` returns 403/999 to non-browser user agents. It must be
  WARN-and-continue, never FAIL — otherwise the job is red from day one.
  Same treatment for any host that returns 403/429 to a scripted HEAD/GET
  while loading fine in browsers: warn, don't fail. FAIL is reserved for:
  DNS failure, connection timeout/refused, HTTP 404/410, and HTTP 5xx on
  both HEAD and GET.
- `.github/workflows/smoke.yml` (plans/001, extended by plans/002) runs the
  offline gate + regression tests on push/PR. The online check gets its OWN
  workflow file with a weekly `cron` + `workflow_dispatch` — never added to
  the push/PR path (network flakes must not block doc edits).
- Conventions: stdlib-only (`urllib.request`, `urllib.error` — no
  `requests`, no lychee action, no new dependencies); conventional commits;
  `python3 scripts/smoke.py` (offline) must stay exit 0 throughout.

## Commands you will need

| Purpose | Command | Provenance | Expected on success |
|---------|---------|------------|---------------------|
| Offline gate | `python3 scripts/smoke.py` | executed | exit 0, `smoke passed` |
| Regression | `python3 scripts/test_smoke.py` | declared | exit 0, `OK` |
| Online run | `python3 scripts/smoke.py --check-online` | declared | exit 0 with WARN lines allowed (see Steps) |
| Unit run | `python3 -m unittest scripts.test_smoke -v` (or `python3 scripts/test_smoke.py`) | declared | exit 0 |

## Suggested executor toolkit

- None. Stdlib `urllib` only.

## Scope

**In scope** (the only files you should modify):
- `scripts/smoke.py` (add `--check-online` + `classify()`-style helper;
  default path byte-for-byte behavior unchanged)
- `scripts/test_smoke.py` (tests for the classifier with stubbed responses —
  no real network in unit tests, see Steps)
- `.github/workflows/online-links.yml` (create: weekly cron + manual dispatch)

**Out of scope** (do NOT touch, even though they look related):
- The offline default path's verdicts — if `--check-online` is absent,
  output must be identical to today (prove via the Step-0 transcript)
- Fixing any rotted link the new check finds beyond reporting (list them in
  your report; each fix is its own editorial decision)
- `README.md`, `TOOLTICIAN.md`, `AGENTS.md`, `smoke.yml`'s push/PR triggers
- Third-party link checkers (lychee action, `requests`): rejected — stdlib
  keeps the zero-dependency contract this repo's scripts promise

## Git workflow

- Branch: `advisor/005-link-watchdog`
- Conventional commits (e.g. `feat(smoke): add opt-in --check-online for external link rot`)
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 0: Establish a green baseline + freeze default output

1. `python3 scripts/smoke.py > /tmp/offline-before.txt 2>&1; echo "rc=$?"` → `rc=0`.
2. `python3 scripts/test_smoke.py` → exit 0, `OK`.
3. Confirm no online flag exists: `python3 scripts/smoke.py --check-online` → expect a link-scan that IGNORES the unknown flag (today's parser only looks for `--root`; extra argv is ignored) OR an error — record exact behavior; after your change it must be a real online run.

**Verify**: offline transcript saved at `/tmp/offline-before.txt` for the
Step-3 comparison. If step 1 isn't green, STOP (baseline broken).

### Step 1: Add --check-online (stdlib urllib, warn-not-fail allowlist)

1. Add a `--check-online` flag to the `__main__` block (same guarded style
   as plans/002's `--root` parse) and a `check_online(urls)` helper that:
   - sends `HEAD` with `User-Agent: github-profile-smoke (+https://tooltician.com/)`
     and `timeout=10`; on 405/501 (HEAD unsupported) retries once with `GET`
     (range-limited: read at most 8 KB, then close — never download bodies).
   - classifies: `OK` (2xx), `WARN` (`linkedin.com/*` with 403/999, any
     403/429, any `img.shields.io` non-2xx — badge CDN rate-limits bots),
     `FAIL` (DNS/connection/timeout errors, 404/410, 5xx on both attempts).
   - prints `ONLINE <status> <url> (<detail>)` per URL, a summary line
     `online: N ok, M warn, K fail`, and returns K.
   - `main()` calls it only when the flag is present, after the offline
     checks; final exit code is 1 if offline failures OR K>0, else 0.
2. Keep the offline path untouched: `python3 scripts/smoke.py > /tmp/offline-after.txt 2>&1` then `diff /tmp/offline-before.txt /tmp/offline-after.txt` → no differences (modulo the pass-count line if you add one — if so, record the exact expected diff here... better: no new stdout on the default path at all).

**Verify**: `diff` of the two transcripts is empty;
`python3 scripts/smoke.py --help` is NOT required (no argparse — keep the
hand-rolled style; document the flag in the docstring instead, updating the
"Run:" line and the "No network access" line to "No network access unless
`--check-online` is passed").

### Step 2: Unit-test the classifier without network

Extend `scripts/test_smoke.py` with tests that stub `urllib.request.urlopen`
(`unittest.mock` is stdlib — allowed) to return/raise canned responses and
assert classification:

1. 200 → OK; 2. 404 → FAIL; 3. `linkedin.com` 403 → WARN (the load-bearing
   case — comment it as "LinkedIn blocks bots; must never fail the job");
   4. `URLError` (DNS) → FAIL; 5. HEAD 405 followed by GET 200 → OK
   (fallback works); 6. end-to-end: `main()` on a temp dir with one good
   and one missing-local link plus online disabled behaves as before
   (offline contract intact).

**Verify**: `python3 scripts/test_smoke.py` → exit 0, `OK`, `Ran` count ≥
(plans/002's 8 + 6 new) = 14 tests. No test may touch the real network
(review: every new test patches `urlopen` or uses temp dirs).

### Step 3: Live-fire once, then add the scheduled workflow

1. Run `python3 scripts/smoke.py --check-online` against the real web.
   Expect: exit 0 or 1 depending on live state; WARNs for LinkedIn Shields
   are ACCEPTABLE. Record every FAIL line verbatim.
   - If K failures are all allowlist-class hosts misbehaving in new ways
     (e.g. a new 403): extend the WARN rule with a comment citing the
     observed status, re-run, proceed.
   - If a FAIL is a genuinely dead link in `README.md`/`TOOLTICIAN.md`: do
     NOT fix it here (out of scope) — record it in your final report as a
     `reconcile` candidate and proceed with the workflow.
   - If the sandbox has no network at all (everything FAILs with DNS/
     timeout): STOP and report — do not "fix" by deleting links or
     widening the allowlist to silence it.
2. Create `.github/workflows/online-links.yml`:
   ```yaml
   name: online-links
   on:
     schedule:
       - cron: "23 6 * * 1"  # weekly, Monday 06:23 UTC
     workflow_dispatch:
   jobs:
     online:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: "3.13"
         - name: External link liveness (warnings allowed, failures fail)
           run: python3 scripts/smoke.py --check-online
   ```
   Do NOT add `push`/`pull_request` triggers (network flakes must not gate
   doc edits) and do NOT touch `smoke.yml`.

**Verify**: offline gate + unit tests still green;
`grep -q "schedule" .github/workflows/online-links.yml` exits 0;
`grep -q "pull_request" .github/workflows/online-links.yml` exits 1.

## Test plan

- New unit tests (6, fully stubbed, zero network): 200→OK, 404→FAIL,
  LinkedIn-403→WARN, DNS-error→FAIL, HEAD-405→GET-200→OK, offline-contract
  intact. Pattern: `unittest.mock.patch` on the opener used by the helper,
  same `TestCase` style as plans/002's file.
- One live-fire run (Step 3) as an integration check — results recorded,
  not asserted (the web moves).
- Verification: `python3 scripts/test_smoke.py` → `OK`, ≥11 tests.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `python3 scripts/smoke.py` exits 0 AND `diff` of default-path output vs Step-0 transcript is empty
- [ ] `python3 scripts/test_smoke.py` exits 0, output contains `OK` and `Ran 14 tests` (or more)
- [ ] `grep -n "urlopen" scripts/test_smoke.py | grep -c "patch"` ≥ 5 (network stubbed, not live)
- [ ] `grep -q "schedule" .github/workflows/online-links.yml` exits 0; `grep -q "pull_request" .github/workflows/online-links.yml` exits 1
- [ ] `grep -n "^import\|^from" scripts/smoke.py` shows only stdlib modules (no `requests`, no third-party)
- [ ] `git diff --name-only main...HEAD` lists only `scripts/smoke.py`, `scripts/test_smoke.py`, `.github/workflows/online-links.yml`
- [ ] `plans/README.md` status row for 005 updated

## STOP conditions

Stop and report back (do not improvise) if:

- plans/001 or plans/002 are not merged (files/flags this plan builds on
  are missing or behave differently than the excerpts).
- The sandbox has no usable network (uniform DNS/timeout FAILs) — report,
  don't silence.
- The live-fire surfaces a dead link — report it, don't fix it here.
- Any host beyond the documented allowlist classes needs WARN treatment to
  go green — one documented extension is fine; a growing allowlist means
  the design is wrong, so stop and report the full FAIL list instead.
- A step's verification fails twice after a reasonable fix attempt.

## Maintenance notes

For the human/agent who owns this code after the change lands:

- Monday-morning red on this workflow means "a link died", not "the build
  broke" — triage by reading the `ONLINE FAIL` lines, not by reverting.
- LinkedIn/Shields WARNs are endemic bot-blocking; only escalate if a WARN
  host starts 404ing (reclassify that host to FAIL then).
- If the URL count grows past ~50, batch with `concurrent.futures`
  (stdlib) — sequential HEADs get slow. Don't reach for asyncio/aiohttp.
- **Deferred:** per-link `data-rot` checks (e.g. PyPI version badges
  drifting) — larger scope, needs its own plan. Write each future deferral
  as `**Deferred:** …` so `reconcile` can find it.
