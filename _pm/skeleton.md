# Skeleton — Tiamat

> Wei Hao 5-step. Tiamat is an ongoing tool adoption, not a dated engagement — this skeleton frames what the fork must keep true, release after release.

## Outcome

After this stands, **Joe (and any agent orchestrating for him)** can **run verified multi-model swarm work from one living fork of Ringer — current with upstream, carrying our own few deltas, watchable in the Den — without ever owning a divergent codebase.**

## The one user journey that must stay intact

1. A backlog exists (PRD or tracker) with checkable tasks.
2. An orchestrator dispatches work through `ringer.py` — one-off manifests, panels, or the Ralph loop — across the heads (codex / claude / opencode).
3. Every task is verified by an executed check; only the harness verdict counts.
4. Joe watches live in the Den (`/?face=den`) or stock Ringside, and reads the run report after.
5. Results land as commits/artifacts; the scoreboard accumulates honest per-model evidence.
6. `git fetch upstream && git merge upstream/main` at any time keeps the fork current without breaking 1–5.

If an upstream sync breaks this journey, the fork has failed its whole premise.

## Minimum capabilities

- Upstream-current `ringer.py` with all three engine lanes resolving (codex from PATH, claude shim, opencode shim).
- The delta set applying cleanly on top: claude-worker engine, ralph-loop template, face selection, the Den.
- Full test suite green after every sync and every delta (`python3 -m unittest discover -s tests`).
- The delta ledger legible in one command: `git log --oneline upstream/main..main`.

## Fundamental enablers

- Credentials outside the repo: `~/.config/ringer/claude.env` (0600), OpenCode's OpenRouter auth store, codex OAuth.
- Global config at `~/.config/ringer/config.toml` pointing engine bins at this clone.
- Fork doctrine written and followed (`TIAMAT.md`): merge-not-rebase, new-files-only placement for local material, ADR-per-delta.
- Upstream remote push-disabled; contributions go via PR branches cut from `upstream/main`.

## Non-negotiables

- **Exit 0 of an executed check is the only PASS** — no vibes on the scoreboard, no hand-rescued greens.
- **Never edit upstream-owned files except as a deliberate, committed delta.**
- **Displayed data must be true** (their rule, kept as ours): faces and reports render only what the state actually says.
- **Never push to upstream; never run upstream self-update.**

---

## Quick test for any candidate story

A story belongs in Tiamat **only if** it makes at least one of these true:

- The fork stays *more current* (sync/merge/reconciliation work).
- A delta becomes *more upstreamable* (tests, scoping, fixtures, PR prep).
- A run becomes *more verifiable or more watchable* (checks, faces, reports, scoreboard honesty).

If none of the three are true, it likely belongs in a project that *uses* Tiamat, not in Tiamat.

---

## How this artifact is used

- Read at session start alongside `TIAMAT.md` (fork doctrine) — skeleton says *what must stay true*, doctrine says *how we stay current*.
- `TASKS.md` carries active work; `sessions/` the daily what-and-why; `decisions/` the one-way doors; `docs/tiamat/evolutions/` is the idea intake — nothing gets built from there until real demand shows up (a rule broken exactly once, on day one, by the owner asking directly — allowed).
- Flavor-check monthly: if the work drifts from this skeleton, reshape the backlog or rewrite the skeleton — don't stretch it.
