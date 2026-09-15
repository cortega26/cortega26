# Plan 003: Fix stale branding doc and EN/ES project-list drift

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` — unless a reviewer dispatched you and told you they
> maintain the index.
>
> **Drift check (run first)**: `git diff --stat 4ec3654..HEAD -- README.md TOOLTICIAN.md`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: plans/001-baseline-ci.md (so CI gates these doc edits)
- **Category**: docs
- **Planned at**: commit `cb3de7b`, 2026-09-15

## Why this matters

Two docs defects compound: `TOOLTICIAN.md`'s stated purpose is to ground AI
agents writing ecosystem READMEs, but its "Uso" paragraph describes a badge
pipeline (static SVGs on `tooltician.com/public/`) that the repo already
abandoned for shields.io — agents following it get the wrong source of
truth. Separately, the README's English and Spanish project lists already
disagree about Monedario (site link vs a repo link using the repo's OLD
name), and the Spanish link target `cortega26/tuplatainforma` is stale: the
repo was renamed to `cortega26/Monedario`. Fixing both restores the docs'
job: one true badge canon, one consistent project list in both languages.

## Current state

The facts the executor needs, inlined:

- `TOOLTICIAN.md:10-12` (stale paragraph):
  ```
  SVGs servidos estáticamente desde `tooltician.com/public/`. Cada idioma tiene su propio
  archivo SVG con el texto localizado. Para cambiar el diseño se actualizan solo los SVGs
  y se refleja en todos los proyectos al desplegar.
  ```
  Every badge snippet in the same file (`:17, :23, :29, :46, :58, :70, :82,
  :94, :104`) uses `https://img.shields.io/badge/...` URLs instead, e.g.:
  ```markdown
  [![Parte de Tooltician](https://img.shields.io/badge/Parte_de-Tooltician.com-6C47FF?v=2)](https://tooltician.com)
  ```
  Commit `cb3de7b` ("fix(badge): use shields.io URL and move to last
  position") confirms the shields.io move was deliberate; the paragraph was
  left behind. Verified live 2026-09-15: `chile-hub`'s README (same
  ecosystem) already uses the shields.io badge — the ecosystem converged.
- `README.md:33` (English list):
  ```markdown
  - [Monedario](https://monedario.cl) — Chile-focused personal finance education site with practical calculators, evergreen guides, and editorial governance.
  ```
- `README.md:78` (Spanish list):
  ```markdown
  - [Monedario](https://github.com/cortega26/tuplatainforma) — sitio educativo de finanzas personales para Chile con calculadoras prácticas, guías evergreen y gobernanza editorial. [Sitio](https://monedario.cl/)
  ```
  Verified 2026-09-15 via `gh repo view`: `cortega26/tuplatainforma` no
  longer exists under that name — the repo is now `cortega26/Monedario`
  ("Chile-focused personal finance education site with practical
  calculators and evergreen guides.", not archived, pushed 2026-09-15).
  GitHub renames leave redirects, so the old link likely still resolves,
  but the canonical URL must be used.
- Editorial rule to apply (matches the Spanish entry's shape, which carries
  both links): every project entry that has both a repo and a live site
  links the **repo first**, then a `[Sitio]`/`[Site]` link — same slugs in
  both languages. Convention evidence: sibling entries link repos
  (`rutificador`, `conciliador_bancario`, `polla`, … all point at
  `github.com/cortega26/...`).
- Repo conventions: conventional commits (`docs(...):` prefix for doc
  work); bilingual README = English body + Spanish inside
  `<details><summary>ESPAÑOL — Resumen breve</summary>`; the smoke gate
  (`python3 scripts/smoke.py`, exit 0) must pass after every edit.

## Commands you will need

| Purpose | Command | Provenance | Expected on success |
|---------|---------|------------|---------------------|
| Gate | `python3 scripts/smoke.py` | executed | exit 0, `smoke passed` |
| Verify no stale host | `grep -rn "tooltician.com/public" README.md TOOLTICIAN.md` | declared | exit 1 (no matches) |
| Verify old repo name gone | `grep -rn "tuplatainforma" README.md TOOLTICIAN.md` | declared | exit 1 (no matches) |
| Verify parity | `grep -c "github.com/cortega26/Monedario" README.md` | declared | `2` (EN + ES entries) |

## Suggested executor toolkit

- None.

## Scope

**In scope** (the only files you should modify):
- `TOOLTICIAN.md` (the stale "Uso" paragraph only)
- `README.md` (Monedario EN + ES entries only)

**Out of scope** (do NOT touch, even though they look related):
- Adding `chile-hub` to Featured Projects — plans/006's job (it depends on
  the parity rule set here; do not jump ahead)
- All other project entries, the header link line, skills/contact sections
- `scripts/smoke.py`, workflows, `AGENTS.md`, `.gitignore`,
  `indicadores.png`
- Verifying external URLs are live (no network probing in this plan —
  plans/005 builds that gate; here use only the `gh`-verified facts above)

## Git workflow

- Branch: `advisor/003-docs-consistency`
- Commit style: conventional commits, `docs(...):` prefix (e.g.
  `docs(branding): drop stale static-SVG paragraph, shields.io is canonical`)
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 0: Establish a green baseline

1. `python3 scripts/smoke.py` → exit 0.
2. `grep -rn "tooltician.com/public" TOOLTICIAN.md` → confirms the stale
   paragraph is still there (this greps SHOULD match pre-fix; record it).
3. `grep -n "tuplatainforma" README.md` → expect line 78 (Spanish entry).

**Verify**: gate green; both greps locate the exact lines above. Anything
else is drift — STOP.

### Step 1: Fix the TOOLTICIAN.md badge-source paragraph

Replace `TOOLTICIAN.md:10-12`:
```
SVGs servidos estáticamente desde `tooltician.com/public/`. Cada idioma tiene su propio
archivo SVG con el texto localizado. Para cambiar el diseño se actualizan solo los SVGs
y se refleja en todos los proyectos al desplegar.
```
with:
```
Badges servidos vía `img.shields.io` (fuente canónica desde `cb3de7b`).
Cada idioma tiene su propio snippet abajo. Para cambiar el diseño se actualizan
los snippets en este archivo y se refleja en todos los proyectos al adoptarlos.
```
Do NOT touch any badge snippet, tagline, footer, or project-eligibility
section — paragraph only.

**Verify**: `grep -rn "tooltician.com/public" README.md TOOLTICIAN.md` →
exit 1 (no matches); `python3 scripts/smoke.py` → exit 0 (snippets live
inside fenced blocks, which the gate skips — confirm nothing broke anyway).

### Step 2: Unify the Monedario entries (repo-first, canonical name)

1. English entry (`README.md:33`) becomes:
   ```markdown
   - [Monedario](https://github.com/cortega26/Monedario) — Chile-focused personal finance education site with practical calculators, evergreen guides, and editorial governance. [Site](https://monedario.cl/)
   ```
2. Spanish entry (`README.md:78`) becomes:
   ```markdown
   - [Monedario](https://github.com/cortega26/Monedario) — sitio educativo de finanzas personales para Chile con calculadoras prácticas, guías evergreen y gobernanza editorial. [Sitio](https://monedario.cl/)
   ```
   Changes vs today: canonical repo name in both; EN gains the `[Site]`
   link so both languages carry repo + site (parity rule).

**Verify**: `grep -c "github.com/cortega26/Monedario" README.md` → `2`;
`grep -rn "tuplatainforma" README.md TOOLTICIAN.md` → exit 1;
`python3 scripts/smoke.py` → exit 0. Commit both steps' files together or
separately with `docs(...):` messages.

## Test plan

- The smoke gate is the test harness: `python3 scripts/smoke.py` → exit 0
  after each step (validates fences still balanced, new links well-formed,
  relative `TOOLTICIAN.md` link still resolves).
- No new test files (doc-only change; structural parity is asserted by the
  `grep -c … → 2` check in Done criteria).

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `python3 scripts/smoke.py` exits 0 with `smoke passed`
- [ ] `grep -rn "tooltician.com/public" README.md TOOLTICIAN.md` exits 1 (no matches)
- [ ] `grep -rn "tuplatainforma" README.md TOOLTICIAN.md` exits 1 (no matches)
- [ ] `grep -c "github.com/cortega26/Monedario" README.md` outputs `2`
- [ ] `git diff --name-only main...HEAD` lists only `README.md` and `TOOLTICIAN.md`
- [ ] `plans/README.md` status row for 003 updated

## STOP conditions

Stop and report back (do not improvise) if:

- The excerpts for `TOOLTICIAN.md:10-12` or `README.md:33` / `:78` don't
  match the live files (drift since `cb3de7b`).
- `gh repo view cortega26/Monedario` (re-run to confirm) shows the repo
  renamed again, archived, or gone — the canonical-URL assumption is false.
- Any step's smoke run fails: a fence or link broke; fix the edit, don't
  weaken the gate.
- The change appears to require touching an out-of-scope file (e.g. other
  projects' entries look stale too — list them in your report, don't fix).

## Maintenance notes

For the human/agent who owns this code after the change lands:

- Parity rule going forward: **same project slugs, same link targets, in
  both EN and ES lists** — plans/006 (chile-hub) follows it; enforce it in
  review until/unless a parity check is automated.
- If GitHub ever reclaims/removes the `tuplatainforma` redirect, the old URL
  dies silently — another reason plans/005's liveness gate matters.
- **Deferred:** automated EN/ES parity checking (direction option in the
  audit) — not built here; it needs an editorial decision on strictness
  first. Recorded for `reconcile`, not started.
