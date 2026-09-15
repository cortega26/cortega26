# Plan 001: Verify the committed gate and run it in CI

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` — unless a reviewer dispatched you and told you they
> maintain the index.
>
> **Drift check (run first)**: `git diff --stat 4ec3654..HEAD -- .github/workflows/smoke.yml`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: tests
- **Planned at**: commit `cb3de7b`, 2026-09-15

## Why this matters

This repo ships a public hiring-surface profile, and its only automated
quality gate — `scripts/smoke.py`, which checks required files, balanced
code fences, link well-formedness, relative-link resolution, and the
profile surface links — was committed to the repo but nothing on GitHub
runs it, so broken links or fences still land silently. Wiring it into
GitHub Actions turns the existing passing check into real protection on
every push and pull request.

Two things this plan does NOT do (both discovered during planning, both
owned elsewhere): the `origin/main` sync already happened (operator,
2026-09-15 — see Current state), and the surface check turned out to be
substring-based, so it cannot actually enforce the header link line —
hardening its semantics is plans/002's job, not this plan's.

## Current state

The facts the executor needs, inlined:

- `main` already includes `origin/main` `77224fb` ("Update README.md",
  2026-08-18), which changed `README.md` line 5 to (current content,
  verify with `sed -n '5p' README.md`):
  ```
  [Portfolio](https://tooltician.com/) · [LinkedIn](https://www.linkedin.com/in/cortega26) · [Email](mailto:carlosortega77@gmail.com) · [Monedario](https://monedario.cl/) · [Noticiencias](https://www.noticiencias.com/)
  ```
  i.e. the maintainer deliberately removed the GitHub self-link (the
  profile page IS the GitHub presence). Make NO manual edits to `README.md`
  in this plan.
- `scripts/smoke.py` (137 lines, stdlib only) is tracked and unmodified
  (operator custody commit, content identical to the `cb3de7b` tree). Run:
  `python3 scripts/smoke.py [--root PATH]`. Exit 0 = pass. Its surface
  list (`scripts/smoke.py:26-30`) still contains three entries including
  the bare self-link — left intentionally alone here; plans/002 replaces
  the substring check with exact-target matching and drops that entry.
- No `.github/workflows/` directory exists today (`.github/` holds only
  `instructions/codacy.instructions.md`, which is gitignored and out of scope).
- Repo conventions to match: conventional-commit messages, e.g.
  `fix(badge): use shields.io URL and move to last position`,
  `docs(badge): actualizar TOOLTICIAN.md con SVGs centralizados por idioma`
  (see `git log --oneline -10`). Scripts stay stdlib-only (see the
  `smoke.py` docstring: "No network access, no deps").

## Commands you will need

| Purpose   | Command                  | Provenance | Expected on success |
|-----------|--------------------------|------------|---------------------|
| Gate      | `python3 scripts/smoke.py` | executed | exit 0, ends with `smoke passed` |
| Sync proof| `git merge-base --is-ancestor 77224fb HEAD` | declared | exit 0 (sync absorbed) |
| Tracked?  | `git ls-files scripts/smoke.py` | declared | prints `scripts/smoke.py` |
| YAML keys | `grep -q "scripts/smoke.py" .github/workflows/smoke.yml` | declared | exit 0 |

**Provenance**: `executed` = the advisor ran it during recon and saw it
work. `declared` = read from repo state but not run. A `declared` command
that fails on an unmodified checkout is a broken baseline — STOP and report.

## Suggested executor toolkit

- None required. Stdlib Python 3.13 and git only.

## Scope

**In scope** (the only file you should modify):
- `.github/workflows/smoke.yml` (create)

**Out of scope** (do NOT touch, even though they look related):
- `scripts/smoke.py` — tracked and frozen for this plan; its `--root`
  crash, global `failures`, `#fragment` handling, and surface-check
  semantics are all plans/002's job
- `README.md`, `TOOLTICIAN.md`, `AGENTS.md`, `.gitignore`,
  `indicadores.png` — other plans' scope; no manual edits here

## Git workflow

- Branch: `advisor/001-baseline-ci` (repo has no branch convention; all past
  work landed on `main`, so use the advisor default)
- One commit, conventional style:
  `test(ci): run smoke gate on push and pull requests`
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 0: Establish a green baseline

Run on the unmodified checkout:

1. `python3 scripts/smoke.py` → expect exit 0 ending with `smoke passed`.
2. `git status --short` → expect only `?? .codegraph/` (local indexer
   state — never stage or commit it) and nothing else.
3. `git merge-base --is-ancestor 77224fb HEAD` → expect exit 0 (the
   upstream sync is absorbed); `git log --oneline HEAD..origin/main` →
   expect empty (in sync with origin).
4. `git ls-files scripts/smoke.py` → expect `scripts/smoke.py` (custody
   commit present).

**Verify**: all four match. If smoke fails on the unmodified checkout,
STOP and report (the repo drifted since this plan was written).

### Step 1: Confirm sync state (no pull expected)

1. `git fetch origin`; `git log --oneline HEAD..origin/main` → expect
   empty (already in sync).
2. `sed -n '5p' README.md` → expect the line-5 content from Current state
   (no GitHub self-link).
3. If HEAD is behind (non-empty log): `git pull --ff-only`, then re-run
   Step 0. If the pull refuses (non-fast-forward) or `origin/main` has
   moved past `77224fb`, STOP and report — the surface assumptions may
   need re-evaluation.

**Verify**: in sync, line 5 matches. This step changes nothing in the
normal case.

### Step 2: Add the CI workflow

Create `.github/workflows/smoke.yml` with exactly this content:

```yaml
name: smoke

on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - name: Profile-surface smoke check
        run: python3 scripts/smoke.py
```

Notes: stdlib-only means no install step is needed. `push` covers direct
`main` edits (this repo's history is mostly web edits to `main`); keep all
three triggers.

**Verify**:
- `grep -q "scripts/smoke.py" .github/workflows/smoke.yml` → exit 0
- `grep -q "pull_request" .github/workflows/smoke.yml` → exit 0
- `python3 scripts/smoke.py` → exit 0 (workflow runs the same command)
- Commit: `git add .github/workflows/smoke.yml`; message
  `test(ci): run smoke gate on push and pull requests`

## Test plan

- No new test files in this plan (regression tests for the script itself
  are plans/002's job).
- Existing gate as the test: `python3 scripts/smoke.py` → exit 0,
  `smoke passed`, run before and after the commit.
- Structural checks on the workflow file via the `grep` commands in Step 2
  (no YAML parser in stdlib; do not add a dependency to validate it).

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `python3 scripts/smoke.py` exits 0 and prints `smoke passed`
- [ ] `grep -q "scripts/smoke.py" .github/workflows/smoke.yml && grep -q "pull_request" .github/workflows/smoke.yml` exits 0
- [ ] `git ls-files scripts/smoke.py` prints `scripts/smoke.py`
- [ ] `git diff --name-only main...HEAD` lists only
      `.github/workflows/smoke.yml` (three dots — compares against the
      merge base, so it still holds if other work landed on `main`
      meanwhile). `git status` is not a scope check here: this plan tells
      you to commit, and committed work leaves it clean.
- [ ] `plans/README.md` status row for 001 updated to DONE

## STOP conditions

Stop and report back (do not improvise) if:

- The drift-check diff shows the workflow file already exists with
  different content (someone wired CI independently).
- `origin/main` has moved past `77224fb`, or Step 1's pull refuses —
  report instead of merging.
- Any step's smoke run fails: a fence or link broke; fix nothing,
  report it (content edits belong to other plans).
- The work appears to require touching an out-of-scope file.

## Maintenance notes

For the human/agent who owns this code after the change lands:

- After plans/002 lands, the surface check enforces exact link targets —
  if the maintainer ever re-adds a header link, `SURFACE_URLS` must be
  updated in lockstep or CI goes red. That coupling is intentional.
- **Deferred:** CI run for the script's own regression tests — covered when
  plans/002 adds `scripts/test_smoke.py`; this workflow file is in that
  plan's scope for the one-line hookup.
- Reviewer focus: this plan adds CI only; no gate semantics changed here.
