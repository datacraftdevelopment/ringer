# Tiamat

**A light fork of [Ringer](https://github.com/NateBJones-Projects/ringer)** — Nate B. Jones's verified-swarm orchestrator — under the DataCraft banner. Named for the multi-headed dragon: each head a different worker engine (Codex, Claude, GLM, …), different breath weapons, one body dispatching them, one will — the manifest and its executed check — deciding what counts as a kill.

Upstream stays the brain trust; this fork exists so a couple of our own ideas can live in the codebase without waiting on upstream review, while we keep absorbing everything they ship.

## The fork doctrine

**Track upstream; never drift into our own thing.**

- **Remotes:** `origin` = `datacraftdevelopment/ringer` (ours, push target) · `upstream` = `NateBJones-Projects/ringer` (fetch only; push URL disabled on purpose).
- **Sync by merge, never rebase.** `git fetch upstream && git merge upstream/main`. Merging preserves their timeline with our deltas riding on top; rebasing would rewrite the delta trail every sync.
- **The delta ledger is git itself:** `git log --oneline upstream/main..main` lists exactly what we've changed, always current, can't go stale.
- **One commit (or branch) per delta**, scoped the way their CONTRIBUTING likes PRs — small, one idea, tested. That keeps every delta individually upstreamable.
- **The *why* of each delta is an ADR** in `docs/tiamat/adr/`, written as we go (grill-with-docs discipline). Git holds the *what*, ADRs hold the *why*, upstream merges hold the *current*.
- **Review on every sync:** skim what upstream shipped; adopt or skip *on purpose*, and when something they built supersedes a delta of ours, retire ours and say so in its ADR.
- **Upstreaming:** ideas that prove out go back as PRs (branch from `upstream/main`, per their CONTRIBUTING — small, scoped, executed proof, real motivation). Evolution ideas queue in `docs/tiamat/evolutions/` until proven.

All Tiamat-local material lives in `TIAMAT.md` + `docs/tiamat/` — new files only, so syncs stay conflict-free. Upstream files are only touched when the change *is* a deliberate delta.

## Status

- **Stood up 2026-07-30** from the fork at `4ac3791` (the old Agent-Argus pin), fast-forwarded to upstream `a1a91b8`; 253/253 tests pass locally.
- **Predecessor:** the Agent-Argus periphery experiment (`DC/Agent-Argus`) — Ringer core and the adversarial-review panel proved out there; the standing engine did not. Verdict and archaeology live in that repo.
- **Upstream changes to review since the old pin** (first entries for the adopt-or-skip lane): the `ask` command; the context-packet system (compare with our token-saver skill's bundled `context_packet.py`); `templates/bakeoff-kit`; their updated in-repo `.claude/skills/ringer/SKILL.md` (our global ringer skill was reconciled at `4ac3791` — needs re-reconciling).

## Next steps

1. Run `/setup-matt-pocock-skills` in this repo (first repo to get the kit) — tracker, labels, docs layout; ADR-per-delta rides on it.
2. Work the Argus teardown checklist (stop clock/routines → repoint ringer + cross-review-gate skills and the panel kit here → resolve the Argus-board-vs-Ringside doctrine call → archive `DC/Agent-Argus` to `xArchive/`, committed and pushed first).
3. First evolution candidate: the Ralph-loop backlog burn-down kit (`docs/tiamat/evolutions/ralph-loop-backlog-burndown.md`) — build as `templates/ralph-loop/` here, prove on the cloud-agents experiment, then upstream.
