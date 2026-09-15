# Plan 002: Fix smoke.py defects (CLI crash, state, fragments, surface check)

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` — unless a reviewer dispatched you and told you they
> maintain the index.
>
> **Drift check (run first)**: `git diff --stat 4ec3654..HEAD -- scripts/ .github/workflows/smoke.yml`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: plans/001-baseline-ci.md (needs the CI workflow present
  to hook the new tests into)
- **Category**: bug
- **Planned at**: commit `cb3de7b`, 2026-09-15

## Why this matters

`scripts/smoke.py` is the CI gate for the whole repo (plans/001). Four
defects make it unworthy of that job today: a bare `--root` argument
crashes with an `IndexError` traceback instead of a clean usage error; the
module-global `failures` list is never reset, so calling `main()` twice in
one process (exactly what regression tests do) accumulates stale failures;
relative links with `#anchor` fragments are reported as missing files even
though the file exists; and the profile-surface check is substring-based
(`url in readme_text`), so ANY project link containing a listed domain
satisfies it — verified live on 2026-09-15, when the post-sync README
passed the surface check despite the header self-link being gone. Fix all
four and lock them with stdlib-only regression tests.

## Current state

The facts the executor needs, inlined — never "as discussed":

- `scripts/smoke.py` — 137-line stdlib-only markdown/link gate, tracked and
  unmodified (operator custody commit; content identical to the `cb3de7b`
  tree). The four defect sites:
  1. Global mutable state, `scripts/smoke.py:32`: `failures = []` at module
     level, appended by `fail()` (`:35-37`), never cleared. `main()` returns
     1 whenever the list is non-empty (`:126-130`), so a second `main()`
     call in the same process sees the first run's failures.
  2. Unguarded argv parsing, `scripts/smoke.py:133-137`:
     ```python
     if __name__ == "__main__":
         root = REPO_ROOT
         if "--root" in sys.argv:
             root = sys.argv[sys.argv.index("--root") + 1]
         sys.exit(main(root))
     ```
     `python3 scripts/smoke.py --root` (no value) raises
     `IndexError: list index out of range`.
  3. Fragment-blind relative resolution, `scripts/smoke.py:105-111`:
     ```python
     else:
         resolved = os.path.normpath(
             os.path.join(os.path.dirname(fpath), target)
         )
         if not os.path.exists(resolved):
             fail(f"{rel}:{lineno}: relative link target missing: {target!r}")
             link_failures += 1
     ```
     A target with a fragment is joined whole, so `os.path.exists`
     is False and a valid link FAILs.
  4. Substring surface check, `scripts/smoke.py:115-124` (shape):
     ```python
     readme = <full README.md text>
     missing = [u for u in SURFACE_URLS if u not in readme]
     ```
     `u not in readme` is a substring test on the whole file: any project
     link under the same domain satisfies an entry. The bare
     `https://github.com/cortega26` entry in `SURFACE_URLS` (`:26-30`) is
     satisfied by every project link, although upstream `77224fb`
     deliberately removed the actual self-link.
- Today's directory walk (`:46-50`) skips only `.git`. The `.codegraph/`
  directory (local indexer state) is walked pointlessly; harmless today (no
  `.md` inside) but skip it while here — one-word change, same line.
- Repo conventions: scripts stay **stdlib-only** (docstring: "No network
  access, no deps"); conventional-commit messages, e.g.
  `fix(badge): use shields.io URL and move to last position`.
- CI workflow `.github/workflows/smoke.yml` (added by plans/001) runs
  `python3 scripts/smoke.py` on push/PR. This plan hooks the new regression
  tests into it.

## Commands you will need

| Purpose   | Command                              | Provenance | Expected on success |
|-----------|--------------------------------------|------------|---------------------|
| Gate      | `python3 scripts/smoke.py`           | executed   | exit 0, `smoke passed` |
| Reg. tests| `python3 scripts/test_smoke.py`      | declared   | exit 0 (unittest OK) |
| Repro     | `python3 scripts/smoke.py --root`    | declared   | exit 2 + usage line (after fix; crashes before) |
| Workflow  | `grep -q "test_smoke" .github/workflows/smoke.yml` | declared | exit 0 (after hookup) |

## Suggested executor toolkit

- None. Stdlib `unittest` + `tempfile` only.

## Scope

**In scope** (the only files you should modify):
- `scripts/smoke.py` (the four fixes + `.codegraph` skip)
- `scripts/test_smoke.py` (create — stdlib `unittest` regression tests)
- `.github/workflows/smoke.yml` (one step: run the regression tests)

**Out of scope** (do NOT touch, even though they look related):
- Online/external link checking (`--check-online`) — plans/005's job; keep
  this script offline
- `README.md`, `TOOLTICIAN.md`, `AGENTS.md`, `.gitignore`,
  `indicadores.png` — other plans' scope
- Adding any third-party dependency (violates the script's stdlib-only contract)

## Git workflow

- Branch: `advisor/002-smoke-robustness`
- Commit per fix or per logical unit; message style: conventional commits
  (e.g. `fix(smoke): handle bare --root flag without IndexError`)
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 0: Establish a green baseline

On the unmodified checkout (with plans/001 merged):

1. `python3 scripts/smoke.py` → exit 0, `smoke passed`.
2. `python3 scripts/smoke.py --root` → expect the `IndexError` crash
   (reproduces defect 2 — this is supposed to fail here; record the output).
3. Reproduce defect 1: `python3 -c "import sys; sys.path.insert(0, 'scripts'); import smoke; smoke.main('does-not-exist'); print('second run rc=', smoke.main('.'))"` → expect the second run to report stale failures (rc=1 with leftover FAILs). Record the output.
4. Note defect 4 live: `grep -c "github.com/cortega26" README.md` → ≥8
   (project links), yet the surface check passes — substring weakness
   confirmed, no command needed beyond the count.

**Verify**: step 1 green; steps 2–3 fail exactly as described; step 4 count
is ≥8. Any other failure is drift — STOP and report.

### Step 1: Reset failures per run and guard --root

1. At the top of `main()`, reset the accumulator as the first statement:
   ```python
   def main(root):
       global failures
       failures = []
       md_files = []
   ```
   (Minimal change: keeps `fail()`/`ok()` signatures. Do NOT redesign into
   a class or pass-through parameter — the next maintainer's diff stays
   reviewable.)
2. Replace the `__main__` block with a guarded parse:
   ```python
   if __name__ == "__main__":
       root = REPO_ROOT
       if "--root" in sys.argv:
           idx = sys.argv.index("--root")
           if idx + 1 >= len(sys.argv):
               print("usage: python3 scripts/smoke.py [--root PATH]", file=sys.stderr)
               sys.exit(2)
           root = sys.argv[idx + 1]
       sys.exit(main(root))
   ```
   Exit code 2 = CLI misuse (distinct from the gate's 0/1).

**Verify**: `python3 scripts/smoke.py` → 0; `python3 scripts/smoke.py --root` → exit 2 with the usage line; the Step-0 `python3 -c` double-`main()` repro now prints `second run rc=0` on a clean tree.

### Step 2: Strip #fragments and skip .codegraph

1. In the relative-link branch, split the fragment before resolving:
   ```python
   else:
       path_part = target.split("#", 1)[0]
       if not path_part:
           continue  # pure "#anchor" on a relative line; same-page anchor
       resolved = os.path.normpath(
           os.path.join(os.path.dirname(fpath), path_part)
       )
       ...
   ```
   Keep the existing FAIL message but report the original `target`.
2. Change the walk filter from `d != ".git"` to
   `d not in (".git", ".codegraph")`.

**Verify**: `python3 scripts/smoke.py` → exit 0. Then create a scratch
fixture OUTSIDE the repo (e.g. `/tmp/smoke-frag/` with an `index.md`
containing a link with a fragment — target file `other.md`, anchor `sec` —
plus a real `other.md` file) and run
`python3 scripts/smoke.py --root /tmp/smoke-frag` → exit 0. Delete the
scratch dir afterwards. (Do not put fixtures in the repo — the gate scans
every repo `.md`, so a deliberately-broken fixture would fail CI.)

### Step 3: Enforce exact-target surface matching

1. Add a pure helper next to `fail()`/`ok()`:
   ```python
   def surface_missing(readme_targets, surface_urls):
       """Which required surface URLs lack an exact link target."""
       targets = set(readme_targets)
       return [u for u in surface_urls if u not in targets]
   ```
2. In the link loop, collect real `http(s)` targets from `README.md`
   (outside fences — the loop already skips fenced lines): when the file
   being scanned is `README.md` and the target starts with `http://` or
   `https://`, add the full target string to a `readme_targets` set
   initialized at the top of `main()`.
3. Replace the substring surface check with:
   ```python
   missing = surface_missing(readme_targets, SURFACE_URLS)
   ```
   keeping the existing FAIL/PASS messages.
4. Delete the `"https://github.com/cortega26",` line from `SURFACE_URLS`.
   Rationale (use as the commit body): upstream `77224fb` deliberately
   removed the self-link and the exact-target check now enforces reality —
   the profile page IS the GitHub presence. Do not restore the link.

**Verify**: `python3 scripts/smoke.py` → exit 0 (portfolio + LinkedIn
targets still exact-matched); `grep -n '"https://github.com/cortega26"' scripts/smoke.py`
→ exit 1 (bare entry gone).

### Step 4: Add stdlib regression tests and hook up CI

1. Create `scripts/test_smoke.py` using only `unittest`, `tempfile`,
   `os`, `importlib.util` (load `smoke.py` by path — `scripts/` is not a
   package, so do NOT add `__init__.py`). Cover exactly these 8 cases:
    - bare `--root` is handled (invoke the parse path via `subprocess`:
      run `[sys.executable, smoke_path, "--root"]`, assert returncode 2).
      `subprocess` is stdlib — allowed.
    - double `main()` on a missing dir returns 1 then 1-without-growth:
      call `main()` twice on a `tempfile.TemporaryDirectory` containing one
      valid `.md`, assert both return 0 (proves the reset).
    - fragment link in a temp dir passes (proves the fragment fix; target
      file plus anchor — write the link target with a `#sec` suffix).
    - an actually-missing relative target still FAILs (guards the fix
      against over-correction).
    - unbalanced fences still FAIL (characterize existing behavior so the
      `.codegraph` one-word change can't silently break scanning).
    - `surface_missing` with exact targets present returns empty.
    - `surface_missing` with only longer URLs under the same domain (e.g.
      requiring a bare domain while targets are all suffixed paths)
      reports it missing — the regression test for the live 2026-09-15
      misfire. Pure unit test, no I/O.
    - `surface_missing` with an empty target set reports every entry.
   Model structure on nothing in-repo (no test exemplar exists) — plain
   `unittest.TestCase` classes with `if __name__ == "__main__": unittest.main()`.
2. `python3 scripts/test_smoke.py` → exit 0, `OK`, at least 8 tests run
   (`Ran 8 tests` or more in the output).
3. Add one step to `.github/workflows/smoke.yml` after the smoke step:
   ```yaml
      - name: smoke regression tests
        run: python3 scripts/test_smoke.py
   ```

**Verify**: both `python3 scripts/smoke.py` (exit 0) and
`python3 scripts/test_smoke.py` (exit 0, `OK`) pass;
`grep -q "test_smoke" .github/workflows/smoke.yml` exits 0.

## Test plan

- New `scripts/test_smoke.py`: 8 cases listed in Step 4 (bare `--root`
  exit 2; double-`main()` reset; fragment link passes; missing target still
  fails; unbalanced fences still fail; surface exact-match, substring
  rejection, empty set). File fixtures in `tempfile` directories, surface
  cases pure — never in the repo tree, never on the network.
- Verification: `python3 scripts/test_smoke.py` → all pass, `Ran N tests`
  with N ≥ 8.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `python3 scripts/smoke.py` exits 0 with `smoke passed`
- [ ] `python3 scripts/smoke.py --root` exits 2 and prints a `usage:` line
- [ ] `python3 scripts/test_smoke.py` exits 0, output contains `OK` and `Ran 8 tests` (or more)
- [ ] `grep -q "test_smoke" .github/workflows/smoke.yml` exits 0
- [ ] `grep -rn "failures = \[\]" scripts/smoke.py` shows the reset inside `main()` (not only module level)
- [ ] `grep -n '"https://github.com/cortega26"' scripts/smoke.py` exits 1 (bare self-link entry removed)
- [ ] No new third-party imports: `grep -n "^import\|^from" scripts/smoke.py scripts/test_smoke.py` lists only stdlib modules (`os`, `re`, `sys`, `urllib`, `unittest`, `tempfile`, `importlib`, `subprocess`, `pathlib`)
- [ ] `git diff --name-only main...HEAD` (three dots — compares against the
      merge base with `main`, so it holds if other work landed there)
      lists only `scripts/smoke.py`, `scripts/test_smoke.py`,
      `.github/workflows/smoke.yml`
- [ ] `plans/README.md` status row for 002 updated

## STOP conditions

Stop and report back (do not improvise) if:

- The code at `scripts/smoke.py:32`, `:105-111`, `:115-124`, or `:133-137`
  doesn't match the excerpts (drift since planning).
- plans/001 is not merged (no CI workflow file) — this plan builds on that
  baseline. (`scripts/smoke.py` itself is already tracked.)
- A step's verification fails twice after a reasonable fix attempt.
- The fix appears to require touching an out-of-scope file (e.g. the
  temptation to "fix" `README.md` links while testing — don't; test in
  `/tmp` with pure unit cases where possible).
- A `declared` command fails on the unmodified checkout — broken baseline,
  report it rather than repairing it.

## Maintenance notes

For the human/agent who owns this code after the change lands:

- Test fixtures must live in `tempfile` dirs, never in the repo: the gate
  scans every repo `.md`, so a committed broken fixture fails CI by design.
  (Planning caught its own draft tripping the gate this way.)
- If new CLI flags are added later, replace the hand-rolled `--root` parse
  with `argparse` (stdlib) — the current guard is minimal on purpose.
- `surface_missing` is pure on purpose: surface-policy changes stay unit
  testable without fixtures. If the maintainer re-adds a header link, add
  its exact target URL to `SURFACE_URLS` — substring will NOT save you
  anymore, which is the point.
- **Deferred:** online link checking is explicitly NOT here; see plans/005.
  Keep this script's offline guarantee (its docstring promises it).
