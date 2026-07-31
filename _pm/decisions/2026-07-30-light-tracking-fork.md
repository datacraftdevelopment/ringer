# 2026-07-30 — Light tracking fork, git as the delta ledger

**Status:** accepted

## Context

Agent-Argus wrapped a pristine, OID-pinned Ringer clone in a periphery (updater scripts, engine shims, kits) — fork hygiene without a fork. Joe's verdict on the wider Argus engine: the overhead didn't pay. He wants Ringer current with upstream, a couple of our own ideas living *in* the codebase, upstream's new ideas reviewed as they ship, and changes tracked with plain git — under a name of its own (Tiamat).

## Decision

Run a **light tracking fork**: clone of `datacraftdevelopment/ringer` with `upstream` → `NateBJones-Projects/ringer` (push disabled). Sync by **merge, never rebase**. One commit or branch per delta. Local material in new files only (`TIAMAT.md`, `docs/tiamat/`, `_pm/`, `templates/<ours>/`, `dashboard/faces/`); upstream-owned files touched only as deliberate deltas. The delta ledger is `git log --oneline upstream/main..main`. Contributions branch from `upstream/main`.

## Alternatives considered

- **Pristine clone + periphery (the Argus model)** — proved fork hygiene but kept our ideas outside the codebase and carried a custom updater; retired with Argus.
- **Hard fork** — full ownership of a divergent codebase; loses upstream's velocity and review culture (their main merged four community PRs same-day the week the guide was written). Rejected outright by Joe: "do not fork so far that it is its own thing."
- **No fork (subscribe only)** — can't carry the claude engine lane, the Ralph loop, or the Den at all.

## Consequences

Commits us to: reviewing upstream on every sync (adopt-or-skip on purpose), keeping deltas small and individually upstreamable, and running their full test suite after every sync and delta. Makes easier: staying current (first sync was a fast-forward), contributing back (their CONTRIBUTING's shapes map 1:1 onto our deltas). Makes harder: nothing yet — revisit if a merge ever conflicts painfully with a delta, which is the signal a delta should either upstream or shrink. The fork's README credits its own author because their contributor-audit test enforces it — accepted as charming.
