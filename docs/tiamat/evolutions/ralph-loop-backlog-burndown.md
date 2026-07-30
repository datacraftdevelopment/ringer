# Ringer evolution: Ralph-loop backlog burn-down (scheduler over the swarm)

- **Status:** flagged — unproven idea; do not build until a real project drives it
- **Home:** moved here from `DC/Agent-Argus/docs/evolutions/` at Tiamat stand-up (2026-07-30); this is the living copy
- **Origin:** 2026-07-30 library ingest of Matt Pocock's AI Hero material (Ralph = Geoffrey Huntley's technique); Joe's call to flag it as a Ringer evolution
- **Provenance (library):** `_Core/library/raw/craft/matt-pocock-ralph.md` · `matt-pocock-ralph-tips.md` · `matt-pocock-ralph-plugin-critique.md`; synthesis in `wiki/craft/agents/loop-engineering.md` ("The minimal loop in practice: Ralph") and `wiki/craft/agents/systems/mattpocock-skills.md`

## The idea

Ringer answers *confidence per task* (parallel workers, executed check, one retry, scoreboard). Ralph answers *breadth over time* (serial burn-down of a backlog: pick next incomplete task → fresh session → implement → commit → record → repeat, until `<promise>COMPLETE</promise>` or an iteration cap). They compose cleanly because the seam is already Ringer-shaped:

> **Ralph is the manifest generator; Ringer is the execution substrate.**
> A dumb outer loop pulls the next incomplete task from a task source and emits a **one-task manifest** per iteration. Ringer runs it exactly as it runs anything: fresh worker, sandbox, executed check as the only PASS, retry-with-failure-injected, scoreboard row, Argus visibility.

This upgrades Ralph's weakest point — in Matt's version the same agent that wrote the code runs the tests and declares done (maker grading its own homework) — and gives Ringer the one thing it lacks: a standing scheduler with cross-run progress. It also inherits Ralph's load-bearing property by construction: Ringer workers are already fresh-per-task, so every iteration stays in the smart zone (the exact property Anthropic's in-session `/ralph-loop` plugin deletes — see the plugin-critique capture).

## What the outer loop needs (and Ringer core doesn't have)

1. **Task source** — v1 decision pending: GitHub Issues (fits the cloud-agents experiment; tracker-hosted coordination state) vs local `prd.json` with per-item `passes: false` flags (Matt's completion contract — "done" must be checkable, not vibes).
2. **Next-task selection** — highest-priority incomplete, honoring blocking edges (to-tickets-style tracer bullets).
3. **Progress record across runs** — Ralph's `progress.txt` (task done / decision / files / blockers / notes-for-next), session-scoped, deleted after the sprint; Ringer's `~/.ringer/runs/` covers per-manifest history but not sprint-level resumability.
4. **Stop conditions** — completion promise from the task source (all `passes: true` / no open issues) OR hard iteration cap (the cost cap).
5. **Risk tiering** — grind tasks: one worker + check (cheap, pure Ralph). Risky/quality-critical tasks: widen the iteration to a real swarm (fix-swarm / bakeoff). Matches Matt's risky-first-HITL tip and the ringer skill's "the swarm machinery is not free" gate.

## Upstream verdict (read against `ringer/CONTRIBUTING.md`)

**Worth passing on — but not yet, and not as core code.**

- A scheduler/daemon PR into `ringer.py` risks the explicit scope line: orchestration layers should "build them elsewhere and **Ringer will happily be a component**." The outer loop is periphery by their own philosophy — which is exactly what Agent-Argus is for.
- The blessed vehicle is on their "good first contributions" list verbatim: **"a template kit in `templates/` for a swarm pattern that worked for you."** Note *worked* — past tense. They also weight "real motivation" (an observed failure / real runs) over speculative machinery.

**Path:** build the outer loop here in Tiamat as `templates/ralph-loop/` (loop script + one-task manifest template + check + progress conventions) — building it in the fork's own templates/ means the proven kit IS the upstream PR artifact → prove it on the cloud-agents experiment project (stand up locally → tracker on GitHub → cloud/loop agents burn it down) → then upstream the kit (branch from `upstream/main`) with run evidence and token/iteration numbers in the PR description ("burned N iterations against real backlog X" is the opening line their guide asks for).

## Done-when (for the flag itself)

The kit exists, has burned down one real backlog end-to-end, and an upstream PR branch exists — or the proving run teaches us the composition isn't worth it, and this doc records why.
