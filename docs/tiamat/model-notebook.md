# Model notebook

**Dated evidence log.** Raw material — every entry is a run, a date, and what
the check proved. Cite it; do not absorb it.

Operational model knowledge that is NOT worker-injectable. Injectable rules
live in `steering/profiles/` (canon) and `~/.ringer/steering/profiles/`
(installed). Evidence convention: date + run name + what the check proved.

The durable rules distilled from this log were **promoted 2026-07-24** into the
knowledge bundle and deliberately have no copy here:

- Routing constraints, and the harness-trumps-scoreboard rule →
  `knowledge/worker-routing.md`
- Check-design lessons → `knowledge/check-craft.md`

## Evidence log

Migrated verbatim from the local `docs/MODEL-NOTES.md` additions inside the
`ringer/` clone (uncommitted local diff, captured before the Task 1
archive). Nothing below is summarized or trimmed. The routing/process digest
that used to sit above this section was promoted to the bundle (see the header);
this log remains the underlying material it was distilled from, not a
replacement for it. None of this log reads as a sentence
that would be pasted verbatim into a worker's prompt (no "always do X"
addressed to a model performing a task) — it is routing judgment, harness
constraint, or check-design lesson throughout — so no `steering/profiles/`
entries were created from this migration.

- 2026-07-17 — HARNESS CONSTRAINTS TRUMP SCOREBOARD RECORDS on build-gated
  lanes. The claude engine's tool allowlist is deliberately scoped
  (Write/Edit/Read/Glob/Grep + Bash(python3:*) only — no npm; see
  config.toml and the 2026-07-12 claude-worker-lane decision), and
  OpenCode's bash tool times out at ~2 min (default; no override in
  ~/.config/opencode/opencode.json) — shorter than a Next build. Precision
  on WHY this rules them out: ringer.py still executes the check
  harness-side, so a build-gated task on these lanes is still VERIFIED —
  what the worker loses is self-verification (run build → fix → re-run)
  before finishing, so first-try odds collapse and the single retry is the
  only feedback loop. Routing consequence: Codex for anything gated on a
  real build; claude/GLM lanes for docs, python-checked, or non-compile
  work — regardless of first_try_pass_rate on paper (Fable 5's perfect
  code-feature record doesn't transfer to lanes where the harness blinds
  the worker). Both constraints are config knobs, not laws: a narrow
  allowlist addition (e.g. Bash(npm run build:*)) or an OpenCode timeout
  override would re-open those lanes — but the tight allowlist is
  deliberate (keeps the approval gate on), so widening it is a decision,
  not a reflex. The anthropic SDK lane is even more build-blind: single
  API call, no tools at all.
  UPDATE same day, APPLIED (Joe-approved): claude allowlist widened in
  config.toml — Bash(npm:*)/Bash(npx:*)/Bash(node:*)/Bash(pnpm:*) added, so
  the claude lane is now build-eligible and can self-verify builds. Takes
  effect on the next run, no restart needed. Tradeoff on record in the
  config comment: package.json scripts are repo-defined code, so the lane
  trusts the repo it works in. OpenCode's ~2-min bash cap has NO config
  override (schema + docs checked 2026-07-17), so GLM/opencode stays off
  build-gated lanes regardless.

### crm-build session (2026-07-16, fable-5-orchestrator)

- **codex** — 2026-07-16 — probe (rebuild claude-worker.sh engine shim to an interface contract): PASS attempt 1 (246s, ~57k tok). An earlier run of the same task failed twice purely on the ORCHESTRATOR'S literal-needle static check (demanded the string ANTHROPIC_BASE_URL; worker's prefix-pattern scrub was better) — lesson re-learned: checks verify behavior, not source style. Worker honestly disclosed accidentally invoking the real claude binary once during fixture setup (exit 1, no session).
- **claude-fable-5 (Claude Code lane)** — 2026-07-16 — site-build (design concept, crm-build round 1): PASS attempt 2 (1070s, ~2.78M tok incl. cache reads). Attempt 1 failed the check's currency floor: regex \$[\d,]{3,} counts "$128,000" but not "$48K"-style figures — loosen realism regexes before blaming a worker. Output quality exceptional: fully data-driven concept, computed masthead figures, frozen demo date, 5 live client pages.
- **claude-fable-5** — 2026-07-16 — probe (lane smoke through rebuilt shim): PASS attempt 1 (16s). Shim's live haiku smoke also passed under deliberately poisoned ANTHROPIC_BASE_URL.
- **gpt-5.6-sol (codex)** — 2026-07-16 — site-build (design concept, crm-build round 1): PASS attempt 1 (515s, ~76k tok). Distinctive relationship-intelligence design thinking (signal score, last-touch stat, narrative pulse line) and a responsive spec unprompted. Strong first-try bakeoff citizen.
- **claude-fable-5 (Claude Code lane)** — 2026-07-16 — code-feature ×3 (crm-build round 4, React screen ports in worktrees): Dashboard, ClientDetail, ProjectDetail ALL PASS attempt 1 (~420-480s each; token counts inflated by cache-read summation in the shim). Ports were faithful to reference HTML and wired store/router correctly first try. Heavy design-fidelity ports are a strong Fable lane.
- **gpt-5.6-sol (codex)** — 2026-07-16 — code-feature ×3 (crm-build round 4): Work PASS 1; Contacts PASS 2 and CommandLayer FAIL 2 — BOTH later failures were a harness artifact, not worker error: the orchestrator's initial `git add -A` had committed .DS_Store, Finder modified it inside worktrees, and the ownership check rightly refused the patch. Orchestrator applied command's patch with .DS_Store excluded after its toolchain ran fully green. HARNESS LESSON: gitignore + untrack .DS_Store in any repo used for worktree swarms on macOS; never bless a repo with git add -A.
- **gpt-5.6-sol (codex)** — 2026-07-16 — code-feature (crm-build scaffold, full Vite+React+TS app skeleton to a contracts spec): PASS attempt 1 (818s, ~122k tok) — install/typecheck/vitest/build green first try. Scaffold-to-contract remains a premier Sol lane. Post-integration browser review found 3 real behavior bugs the build-only check couldn't see (sticky sidebar unanchored; palette input never autofocused; palette keyboard model dead) — routed back as a fix swarm; automated checks verify toolchain, orchestrator verifies behavior on render.
- **gpt-5.6-sol (codex)** — 2026-07-16 — code-fix ×2 (crm-build fix swarm on its own round-4/scaffold code): fix--shell PASS 1 (149s), fix--command PASS 2 (218s). All three behavior bugs verified fixed by orchestrator in an independent devtools browser (sticky sidebar pinned; palette autofocus + full keyboard model; toast renders with charter microcopy). Also added the required stage-word unit test (suite 7→8). NOTE: the in-app Browser preview pane produced stale compositor frames + 30s scroll timeouts on long pages — arbitrate UI truth with chrome-devtools before blaming the app.

### Chronoline build (2026-07-17, orchestrator chronoline-orchestrator)

- **gpt-5.6-sol (codex)** — carried 8 of 9 lanes of a full Next 16 + Drizzle
  app build (foundation, seed, 6 feature lanes) against executed build+data
  checks. Foundation and seed PASSED attempt 1 (195k / 207k tok); the seed
  check was heavy (§12 data contract: counts, every status, token-cost range,
  hierarchy rule, idempotency) and it cleared first try. The feature lanes
  that recorded attempt-2 passes were ALL orchestrator check bugs, not model
  faults (see below). Proven lane for heavy single-file feature work against
  a behavioral contract.
- **claude-fable-5 (claude engine)** — FIRST outing on the newly-unblocked npm
  path (allowlist gained Bash(npm/npx/node) same day). Took the REPORTS lane,
  the heaviest spec section (§11: 5 reports + the headline margin math with
  stored-not-recomputed cost). PASSED ATTEMPT 1 at 5.2M tokens — ~25x the
  codex lanes' token spend for comparable work, but correct on the first try
  including the excluded-count honesty and reading stored tokenCost. Fable is
  viable for build-gated code-feature work now; watch the token cost.

### hello-world bakeoff (2026-07-17, orchestrator cc-opus-orchestrator)

- **gpt-5.6-sol (codex)** — 2026-07-17 — bakeoff (hello-world, `print("Hello, World!")`): PASS attempt 1 but **75.8s / ~26k tok** for a one-liner. This machine's Codex install has the superpowers skills in its plugin cache, so a trivial task still triggers the full ritual — it read using-superpowers, brainstorming, TDD, and verification-before-completion, ran a red behavior check, applied the patch, then self-verified stdout+exit. Correct and honest, but the Codex/Sol lane carries fixed ritual overhead; don't route latency-sensitive trivial work here expecting a quick turnaround.
- **claude-opus-4-8 (claude headless)** — 2026-07-17 — bakeoff (same hello-world): PASS attempt 1, **20.3s**, one-shot to the same `print("Hello, World!")`. Token count reads high (~196k) because it's cache-inclusive (cache_read ~92k, cache_creation ~27k, output 460). Faster wall-clock on trivial work than the ritual-heavy Codex lane here.

### Migrated 2026-07-21 (late): concurrent-session append rescued from clone

A session in _Sandbox/helloTest (started before the periphery doctrine landed) appended these to ringer/docs/MODEL-NOTES.md per the old workflow. Content preserved verbatim below; clone restored. Run: hello-world-3-site-test.


## cohere/north-mini-code:free (via opencode) — AUDITION PASSED
- 2026-07-21 site-build (hello-world-3-site-test, exploration slot): **first-try PASS**,
  8,870 tokens, 55.5s, $0. Cheapest and the only clean first attempt of the three.
  Notably self-disciplined: it ran the supplied validator itself before exiting, caught
  its own filler copy in notes.md, fixed it, and re-ran to green — so the failure never
  reached Ringer's retry lane. Output (brutalist type-driven page) was competent and
  on-brief, though plainer than Sol's. Promote untested -> probation for site-build;
  worth a bigger lane on mechanical/tightly-specced front-end tasks.

## gpt-5.6-sol (codex) — skills-inheritance footgun
- 2026-07-21 site-build (hello-world-3-site-test): attempt 1 **failed with rc=0 and zero
  files**, burning 12,457 tokens. Root cause is environmental, not model quality: the
  Codex worker inherits this machine's superpowers skills, invoked the `brainstorming`
  workflow on a trivial hello-world page, and ended its turn with "Approve this direction
  and I'll create exactly index.html and notes.md" — waiting for a human who does not
  exist. Ringer's check caught it cleanly ("missing expected files") and attempt 2
  delivered the best artifact of the run (CSS scanlines, vignette, blinking cursor,
  prefers-reduced-motion guard, aria-labelledby).
- **Action for future manifests:** every codex-engine spec on this machine should carry an
  explicit non-interactive clause — "You cannot ask questions and no human will reply.
  Do not propose a direction or wait for approval; produce the deliverables in this single
  run." Do NOT read this attempt-1 failure as a quality signal on Sol.

## nvidia/nemotron-3-super-120b-a12b:free (addendum)
- 2026-07-21 site-build (hello-world-3-site-test): attempt 1 died on OpenCode's
  `database is locked` (SQLite contention — two opencode workers launched in the same
  second at max_parallel 3). Infrastructure failure, not model failure; attempt 2 passed
  in 42.3s / 12,654 tokens. **Scoreboard caveat:** this run records a first-try FAIL for
  Nemotron on site-build that it did not earn. Consider staggering opencode task starts
  when two or more share a run.
- Artifact quality (my read, not the check's): met the contract but generic — both
  "leaves" reuse one identical blob path with a 15deg rotation, and a comment labels a
  green fill as "muted clay". Passes verification; would not ship as design work.

## 2026-07-21 hello-world-pair (site-build bakeoff, Argus board first live watch)
- **gpt-5.6-sol (codex)**: first-try PASS with the non-interactive clause in the
  spec — confirms the 7/21 footgun fix works; the clause is now standing practice
  for codex-engine specs. 72,522 tokens / 3m31s for a 409-line page with a design
  token system. Spend Sol when the artifact is the product.
- **cohere/north-mini-code:free (opencode)**: second consecutive first-try PASS on
  site-build (8,515 tok / 59.5s — right on its medians). One more clean site-build
  reaches proven (3+ at ≥0.67 first-try). Output honest but template-adjacent
  (cyberpunk neon default aesthetic).
- Process: `run --baseline` before first run caught nothing this time (0 pass at
  baseline = checks non-vacuous) — keep as standing pre-flight on new manifests.
- **Process (manifest-authoring)**: `max_parallel` defaults to **1 = serial**
  (ringer.py:1105) — the hello-world-pair run serialized because the field was
  omitted. Templates set it explicitly (bakeoff: 6). ALWAYS set `max_parallel`
  in every multi-task manifest; the Argus board made the serialization visible
  (cohere finished before sol spawned).

## 2026-07-28 argus-engine-review-panel (first local run of the two-seat cross-review panel)

- **gpt-5.6-sol (codex)**: code-review PASS attempt 1, 946.6s / 303,684 tok.
  9/9 findings verified real on triage — zero false positives, five unique
  catches (routine type-validation escape, check_pass/terminal atomicity,
  mid-DDL wedge, ghost routine_state, silent client catch). Ran the pytest
  suite AND all three argus shell suites itself in a disposable scoped copy
  before asserting the baseline. Model pinned in the manifest this run
  (`"model": "gpt-5.6-sol"`) so the scoreboard row is attributed — keep doing
  that; the engine block has no model_default and otherwise inherits
  ~/.codex/config.toml drift.
- **claude-sonnet-5 (claude headless)**: code-review PASS attempt 2, 579.2s
  total / 4.24M tok (cache-inclusive). Attempt-1 failure was FORMAT ONLY:
  it wrote `**Finding:**` (markdown-bold) and the kit's
  check_review_report.py demands plain `Finding:` labels; the retry prompt
  carried the check output and it re-emitted identical content with plain
  labels. 4/4 findings verified real, one unique catch (install-time TZ pin
  never re-checked). Do NOT read attempt-1 as a quality signal — it's the
  charlie-quirk class (format literal in a check). Candidate fixes: steer
  claude seats to plain-text labels, or make the check accept bolded labels
  (check lives in the pristine clone's kit — a tolerance fix must go via
  upstream-pr/ or a periphery-owned check copy, never an in-clone edit).
- **Panel design (both-seats evidence)**: the two-axis panel worked as
  specified — 3 findings flagged by both seats (health-state precedence,
  email-delivery honesty, next_fire DST split) and all 3 survived
  verification; each axis also caught things the other missed. 10/10 merged
  findings real; the brief's known-issues list held (neither seat burned a
  finding on the Resend placeholder or the ingest path).
