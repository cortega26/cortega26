# Roadmap — github-profile

Backlog, scoreboard, entry point, and tracking file for the September 2026
improvement pass. Planned at commit `cb3de7b` (2026-09-15).

**How to use this file (goto):**

| I want to… | Go to… |
|------------|--------|
| See overall progress at a glance | [Scoreboard](#scoreboard) |
| Know what to run next | [Waves](#waves) — lowest incomplete wave, plans in listed order |
| Execute a plan | The plan file, e.g. `001-baseline-ci.md` (same directory) |
| Check or update per-plan status | `README.md` (same directory) — the source of truth executors update |
| Propose or prioritize future work | [Backlog](#backlog) |
| Resume after a break | [Tracking protocol](#tracking-protocol) |

**Rule that keeps this file honest:** per-plan status lives ONLY in
`README.md` (executors update it per their plan instructions). This file
tracks WAVE-level progress and order. Never duplicate per-plan rows here —
two status tables always drift.

## Scoreboard

Overall: **0 / 6 plans DONE · 0 / 3 waves complete.**

| Wave | Theme | Plans | Done | Status |
|------|-------|-------|------|--------|
| 1 | Foundation & safety net | 001 | 0/1 | TODO |
| 2 | Parallel hardening & hygiene | 002, 003, 004 | 0/3 | TODO (locked until Wave 1 DONE) |
| 3 | Compound value | 005, 006 | 0/2 | TODO (locked until Wave 2 DONE) |

Advance a wave's Status to IN PROGRESS when its first plan starts, DONE when
all its plans are DONE. If any plan goes BLOCKED, the wave is BLOCKED with
the same one-line reason — see `README.md` for which plan.

## Waves

Plans are ordered for efficiency: foundation first (everything builds on
it), then maximum parallelization of independent work, then the compound
plans that consume the hardened base. Critical path is
001 → 003 → 006 (visible content) and 001 → 002 → 005 (gate maturity);
004 floats anywhere in Wave 2.

### Wave 1 — Foundation & safety net (sequential, do first)

| Plan | Title | Effort / Risk | Why now |
|------|-------|---------------|---------|
| [001](001-baseline-ci.md) | Commit smoke gate + CI | S / LOW | Unblocks every other plan: verifies the committed gate, wires CI. Origin/main sync already done by operator. Nothing else should land first. |

Wave 1 DONE criteria: `python3 scripts/smoke.py` green on `main`,
`smoke.yml` present and running on push/PR, `scripts/` tracked.

### Wave 2 — Parallel hardening & hygiene (parallel-safe, any order, separate branches)

These three touch disjoint files. They may run concurrently on separate
`advisor/NNN-*` branches; merge in numerical order to keep conflict risk
at zero.

| Plan | Title | Effort / Risk | Why now |
|------|-------|---------------|---------|
| [002](002-smoke-robustness.md) | Smoke robustness + regression tests | S / LOW | Makes the Wave-1 gate worthy of CI: fixes `--root` crash, state reset, fragment links, surface-check exactness. Required before 005 extends the script. |
| [003](003-docs-consistency.md) | Stale badge paragraph + EN/ES parity | S / LOW | Restores the docs' job (badge canon + consistent project list); sets the parity rule 006 follows. Fixes the stale `tuplatainforma` repo name. |
| [004](004-asset-config-hygiene.md) | Remove orphan PNG + AGENTS.md guidance | S / LOW | Cheapest win on the board; off the critical path — slip it anywhere in the wave. Gives future executors their contract. |

Wave 2 DONE criteria: `test_smoke.py` green in CI, no `tooltician.com/public`
or `tuplatainforma` references, `indicadores.png` untracked-but-recoverable,
`AGENTS.md` carries the executor section.

### Wave 3 — Compound value (parallel-safe after Wave 2)

| Plan | Title | Effort / Risk | Why now |
|------|-------|---------------|---------|
| [005](005-link-watchdog.md) | Opt-in online link-rot check | M / MED | Builds on the hardened script (002). Scheduled weekly so network flakes never gate edits. Expect it to surface real rot — triage, don't auto-fix. |
| [006](006-chile-hub-featured.md) | Add chile-hub (EN+ES) | S / LOW | Highest-visibility content change, saved for after the parity rule (003) so it lands clean. 79 stars, PyPI, CI — the profile's best evidence. |

Wave 3 DONE criteria: `online-links.yml` scheduled and green-or-WARN-only,
chile-hub present in both language lists, smoke green throughout.

All-waves DONE = profile has a gated CI baseline, a tested gate, consistent
docs, no dead weight, a rot watchdog, and its strongest project featured.

## Backlog

Future candidates, explicitly NOT planned yet. Promote via a `plan
<description>` invocation; don't freelance them inside wave work.

| ID | Candidate | Source | Effort | Notes |
|----|-----------|--------|--------|-------|
| B1 | Automated EN/ES parity gate (same slugs/targets both lists) | Audit direction #2 | S | Needs an editorial strictness decision first. Natural follow-up to 003. |
| B2 | Per-link data freshness checks (e.g. badge versions drifting) | Deferred from 005 | M | Only if Wave-3 watchdog proves its worth. |
| B3 | Dead-link fixes surfaced by 005's live-fire run | Unknown until 005 runs | S each | Triage bucket: each fix is its own editorial decision, not a batch. |
| B4 | Profile-wide badge/stats pass (stars, PyPI badges on entries) | Deferred from 006 | S | Deliberately omitted from 006 to match sibling shape; do repo-wide or not at all. |
| B5 | Cross-repo Tooltician badge-compliance checking | Audit rejected for this repo | — | Spans other repos; home is elsewhere (ecosystem tooling), not here. Listed so it isn't re-proposed. |

## Tracking protocol

1. **Executors** update their row in `README.md` (TODO → IN PROGRESS → DONE
   / BLOCKED) as their plan instructs. They do NOT edit this file.
2. **Maintainer (or `reconcile`)** advances wave Status here when wave
   DONE criteria hold, and refreshes the Scoreboard counts.
3. **Resuming after a break:** read Scoreboard → open the lowest incomplete
   wave → read that plan fully → run its drift check first (plans stamp
   `cb3de7b`; if in-scope files moved, treat as STOP).
4. **Blocked waves:** record the one-line reason in the Scoreboard table and
   in `README.md`; blocked plans keep their wave locked — do not start the
   next wave to "stay busy" (Wave 3 builds on Wave 2's outputs).
5. **New findings mid-flight** (e.g. 005's live-fire surfacing rot): append
   to Backlog as B-next, don't expand the running plan. Plans have hard
   boundaries for a reason.
