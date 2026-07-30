# Adversarial-review panel (cross-review-gate dispatch)

The two-seat instantiation of the clone's `ringer/templates/adversarial-review`
kit, as specified by the library skill
`_Core/library/skills/agent-operations/cross-review-gate` ("Dispatch via
Ringer (panel path)"). The upstream kit is N same-engine seats varied by
model; this panel is two seats covering two diversity axes:

- `review-codex` — engine `codex`, no `model` field (config default
  `gpt-5.6-sol`): cross-vendor detection.
- `review-claude` — engine `claude`, `{{CLAUDE_SEAT_MODEL}}`: fresh-context
  detection. Default **`claude-sonnet-5`**; escalate to **`claude-fable-5`**
  when the boundary touches live data (migrations, deploys, schema) — per
  the 2026-07-27 four-seat bakeoff recorded in the skill.

## Fill in

| Placeholder | What goes there |
|---|---|
| `{{RUN_SLUG}}` | Stable slug, e.g. `2026-07-27-billing-migration` |
| `{{WORKDIR}}` | Scratch dir OUTSIDE the repo under review |
| `{{REVIEW_SCOPE}}` | Human-readable name of the thing under review |
| `{{ARTIFACT_PATH_OR_DIFF_COMMAND}}` | Exact diff / paths / command every seat inspects |
| `{{BRIEF}}` | The FULL text of `.review-gate/<slug>/brief.md`, inlined — specs must be self-contained; same brief in both seats |
| `{{REVIEW_FOCUS}}` | One-line focus (what the gate is guarding) |
| `{{CLAUDE_SEAT_MODEL}}` | `claude-sonnet-5`, or `claude-fable-5` for live-data boundaries |
| `{{KIT_DIR}}` | Absolute path to the clone kit: this repo's `templates/adversarial-review` (its `checks/` validator is reused verbatim) |

## Rules from the skill (non-negotiable)

- **Freeze the artifact while the panel is in flight** — a fix applied
  mid-run contaminates any late-finishing seat.
- Offer at a stage boundary, dispatch only on the user's yes.
- After the run: copy each seat's `report.md` verbatim into
  `.review-gate/<slug>/` as `review-codex.md` / `review-claude.md`; triage
  the merged set with a flagged-by column. Both-seats findings are the
  strongest Agree candidates; claude-seat-only findings get extra scrutiny
  (shared family priors).
- PASS means the report satisfied the findings contract — it does not mean
  the artifact is good; the triage verdict stays with the orchestrator.

Lint before running: `python3 …/ringer/ringer.py lint <filled-manifest>`.
