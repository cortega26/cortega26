# Plan 006: Add chile-hub to Featured Projects (EN + ES)

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` — unless a reviewer dispatched you and told you they
> maintain the index.
>
> **Drift check (run first)**: `git diff --stat 4ec3654..HEAD -- README.md`
> If README.md changed since this plan was written, compare the "Current
> state" excerpts against the live file before proceeding; on a mismatch,
> treat it as a STOP condition.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: plans/001-baseline-ci.md (CI gates the edit) and
  plans/003-docs-consistency.md (sets the repo-first + EN/ES parity rule
  this entry follows; also avoids editing the same lines concurrently)
- **Category**: docs
- **Planned at**: commit `cb3de7b`, 2026-09-15

## Why this matters

`chile-hub` is the maintainer's strongest proof signal by several measures
— 79 stars, a published PyPI package, CI/CD, MIT license, active
development (pushed the week this plan was written), and an existing
Tooltician badge — yet the profile's Featured Projects list omits it. A
hiring-surface profile that hides its best evidence undersells every other
claim on the page. Adding one entry in each language, following the
repo-first parity rule, fixes that with a two-line diff.

## Current state

The facts the executor needs, inlined:

- Featured Projects, English list (`README.md:24-43`): seven entries, each
  `- [name](https://github.com/cortega26/<repo>) — one-line description.`
  followed by a `  <sub>tags</sub>` line. The second entry
  (`README.md:27-28`):
  ```markdown
  - [conciliador_bancario](https://github.com/cortega26/conciliador_bancario) — fail-closed bank reconciliation CLI with deterministic outputs and audit artifacts.
    <sub>Python · CLI · Auditability · PyPI · Architecture docs</sub>
  ```
- Spanish list mirrors it inside `<details>` (`README.md:73-81`); its
  second entry (`README.md:76`):
  ```markdown
  - [conciliador_bancario](https://github.com/cortega26/conciliador_bancario) — CLI de conciliación bancaria con enfoque fail-closed y trazabilidad.
  ```
  (Spanish entries carry no `<sub>` tags line — match that, don't add one.)
- chile-hub facts, verified 2026-09-15 via `gh repo view cortega26/chile-hub`
  and its README header (do not re-derive; if the STOP check below
  contradicts them, stop):
  - URL: `https://github.com/cortega26/chile-hub` · Python · MIT · not archived
  - Stars: 79 · PyPI package `chile-hub` · CI/CD badge · pushed 2026-09-15
  - Live docs: `https://tooltician.com/chile-hub/`
  - Maintainer's own tagline (ES): "Datos públicos de Chile, curados y
    listos para análisis en una línea de código." Its README already
    carries the Tooltician shields.io badge, so no branding work is needed.
  - Content: 22 curated data layers (geography, demographics, economy,
    health, education, electoral districts; 346 comunas), consumable via
    Polars, DuckDB, SQLite, JSON, Excel.
- Placement rationale (prescribed, reviewer can reorder): insert THIRD in
  both lists, directly after `conciliador_bancario`. Groups the two
  flagship Python/PyPI/CI proof signals together; prominent without
  rewriting the whole list order.
- Parity rule (from plans/003, restated so this plan stands alone): same
  project slugs and link targets in EN and ES; entry links the **repo**
  first. The live-docs URL is evidence only — do NOT link it in the entry
  (sibling entries link repos; reviewer may ask for the site link later).

## Commands you will need

| Purpose | Command | Provenance | Expected on success |
|---------|---------|------------|---------------------|
| Gate | `python3 scripts/smoke.py` | executed | exit 0, `smoke passed` |
| Entry present | `grep -c "github.com/cortega26/chile-hub" README.md` | declared | `2` (EN + ES) |
| Placement | `grep -n "chile-hub\|conciliador_bancario" README.md` | declared | chile-hub lines immediately follow conciliador lines in both lists |

## Suggested executor toolkit

- None.

## Scope

**In scope** (the only files you should modify):
- `README.md` — two inserted entries only (EN block + ES block)

**Out of scope** (do NOT touch, even though they look related):
- Reordering, rewording, or re-linking any other project entry
  (Monedario canonicalization is plans/003's — if 003 isn't merged and the
  Monedario lines differ from its excerpts, STOP per below rather than
  doing 003's work here)
- `TOOLTICIAN.md` (chile-hub already carries the badge; nothing to add),
  `AGENTS.md`, `scripts/*`, workflows
- Adding badges, star counts, or the live-docs link to the entry — keep the
  two-line sibling shape

## Git workflow

- Branch: `advisor/006-chile-hub-featured`
- One commit, conventional style: `docs(profile): add chile-hub to Featured Projects (EN+ES)`
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 0: Establish a green baseline + re-validate the target

1. `python3 scripts/smoke.py` → exit 0.
2. `grep -n "conciliador_bancario" README.md` → expect exactly the two
   lines from Current state (EN entry + ES entry). If the list moved,
   STOP (ordering assumption broken).
3. Re-validate: `gh repo view cortega26/chile-hub --json url,isArchived,stargazerCount --jq '{url, archived: .isArchived, stars: .stargazerCount}'` → expect the same URL, `archived: false`. (Stars will have moved — ignore the count, it was evidence, not a gate.)

**Verify**: gate green; repo exists, unarchived, same URL. If archived,
renamed, or gone — STOP, the premise is false.

### Step 1: Insert the English entry (third position)

Directly after the `conciliador_bancario` EN block (`README.md:27-28`),
insert:
```markdown
- [chile-hub](https://github.com/cortega26/chile-hub) — curated, validated Chilean open datasets (geography, demographics, economy, health, education) consumable in one line with Polars, DuckDB, SQLite, and Excel.
  <sub>Python · PyPI · CI/CD · Open data · 22 datasets</sub>
```
Match sibling style exactly: `  <sub>` with two leading spaces, `·`
separators, one line of description.

**Verify**: `python3 scripts/smoke.py` → exit 0 (new links well-formed).

### Step 2: Insert the Spanish entry (third position)

Directly after the `conciliador_bancario` ES line (`README.md:76`), insert:
```markdown
- [chile-hub](https://github.com/cortega26/chile-hub) — datos públicos de Chile curados, normalizados y validados, listos para consumir en una línea de código con Polars, DuckDB, SQLite y Excel.
```
No `<sub>` line (Spanish entries have none). Wording tracks the
maintainer's own tagline ("Datos públicos de Chile, curados y listos para
análisis en una línea de código", extended with the validated-formats
detail from the repo description).

**Verify**: `grep -c "github.com/cortega26/chile-hub" README.md` → `2`;
`python3 scripts/smoke.py` → exit 0. Commit with the message from Git
workflow.

## Test plan

- Smoke gate after each insert (new-link well-formedness, fence balance,
  surface links intact): `python3 scripts/smoke.py` → exit 0.
- Placement check: `grep -n "chile-hub\|conciliador_bancario" README.md`
  shows chile-hub immediately after conciliador_bancario in both blocks.
- No new test files (doc-only change).

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `grep -c "github.com/cortega26/chile-hub" README.md` outputs `2`
- [ ] `grep -n "chile-hub\|conciliador_bancario" README.md` shows each chile-hub entry directly after its conciliador_bancario entry
- [ ] `python3 scripts/smoke.py` exits 0 with `smoke passed`
- [ ] `git diff --name-only main...HEAD` lists only `README.md`, and `git diff --stat` shows +3 lines (entry + sub-tags + ES entry) — no other hunks
- [ ] `plans/README.md` status row for 006 updated

## STOP conditions

Stop and report back (do not improvise) if:

- plans/003 is not merged AND the live Monedario/conciliador lines differ
  from the excerpts (you'd be editing against a moved list — report).
- The Step-0 re-validation shows chile-hub archived, renamed, or gone.
- Smoke fails after an insert — fix the markdown, never weaken the gate.
- The change wants to sprawl (rewording siblings, adding badges/star
  counts, linking the live-docs site) — that's editorial scope creep;
  report it as a reviewer question instead.

## Maintenance notes

For the human/agent who owns this code after the change lands:

- Parity rule: chile-hub now counts for "same slugs, same targets, both
  languages" — any future entry follows plans/003's rule, enforced in
  review.
- If the maintainer prefers the live-docs URL
  (`https://tooltician.com/chile-hub/`) as the entry link, that's a
  one-line reviewer edit, not a plan failure — but it would break parity
  with the sibling convention (repos first), so decide consciously.
- **Deferred:** nothing. Star counts and PyPI badges deliberately omitted
  to match sibling shape; a profile-wide badge/stats pass would be its own
  plan.
