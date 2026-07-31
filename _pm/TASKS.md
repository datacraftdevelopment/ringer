# Tasks

Active work only — Current / Next / Waiting on / Backlog. Shipped work and thinking-behind-it live in [`sessions/`](./sessions/) (per-day files).

**Current items carry a one-line `Why` + `Done-when`.** Next / Waiting / Backlog don't need them until promoted.

> Review weekly: scan **Waiting on** every Monday — external blockers rot quietly.

## Current

- **Wear in the fork on real work** — Den open during every swarm, Ralph loop on the first real backlog (the stand-up-locally-then-cloud experiment project is the intended candidate).
  - Why: every remaining upstream-PR and adoption decision is gated on real-use evidence, not smoke tests — upstream's own bar is "a swarm pattern that *worked* for you."
  - Done when: one real backlog has burned down end-to-end through `templates/ralph-loop/` (progress.txt + per-task commits + COMPLETE), and the Den has been the watch surface for a week of normal swarm work without reaching for stock.

## Next

1. **Send upstream PR (a): the face-selection mechanism** (`f368e7a` — cut a branch from `upstream/main`, cherry-pick, PR). Their CONTRIBUTING names this exact piece as the ideal first UI PR (#39). Small, tested, zero default-behavior change.
2. **Run `/setup-matt-pocock-skills` in this repo** — tracker, triage labels, docs layout; then grill-with-docs ADRs for every future delta.
3. **Re-reconcile the global ringer skill against `a1a91b8`** — upstream's in-repo skill moved 64 lines since the `4ac3791` reconciliation; our behavior rules may be stale.
4. **Review upstream's context-packet system vs the token-saver skill's bundled `context_packet.py`** — adopt-or-skip on purpose; they may have converged on the same pattern.
5. **Wind down Agent-Argus** — stop argus-clock + indeed-daily, resolve the untracked `.review-gate/` dirs, commit + push, move `DC/Agent-Argus` → `xArchive/` (checklist in `TIAMAT.md`; everything load-bearing already migrated).

## Waiting on

- _Nothing external yet — first upstream PR not sent._

## Backlog

- **Den v2** — per-task-type drilldown in the Heads (upstream's stock models view added this; adopt the idea), live log tails on hunting runs, richer fixture-render tests, empty-state art.
- **Den face upstream PR (b)** — after wear-in, with daily-use evidence.
- **Ralph loop: GitHub Issues task source** — swap `prd.json` for tracker issues (the cloud-agents experiment shape); blocking edges from native issue links.
- **Ralph loop: parallel frontier mode** — worktrees already isolate tasks; independent unblocked tasks could run as one multi-task manifest when the backlog's edges allow it.
- **Steering canon first profile** — `docs/tiamat/steering/profiles/` sprouts when a model-specific rule earns verbatim injection.
- **`task_type: probe` hygiene** — one-off diagnostic manifests (engine smokes etc.) must carry a task_type so the scoreboard's (untyped) bucket stays empty (lesson: 2026-07-30 engine smoke).
