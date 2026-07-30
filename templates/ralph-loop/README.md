# ralph-loop — backlog burn-down over a Ringer swarm

Ralph (Geoffrey Huntley's technique: the same prompt in a loop, the agent
picking its next task from a PRD, one commit per task) composed with Ringer's
trust model. **Ralph is the scheduler; Ringer is the execution substrate.**
A dumb sequential loop pulls the next incomplete task from a PRD and runs it
as a one-task manifest — fresh worker session, sandbox, executed check as the
only PASS, retry-with-failure-injected, scoreboard row, artifact page.

What the composition fixes in stock Ralph: the worker no longer grades its
own homework or writes its own progress ledger. **The harness verdict flips
`passes: true`; the loop applies and commits; the worker only types.**
Fresh-session-per-iteration — Ralph's load-bearing property — comes free:
Ringer workers are always fresh, so every iteration runs in the smart zone,
and state crosses iterations only through git, the PRD, and `progress.txt`.

## How an iteration works (git mode, the default)

1. The loop picks the first task whose `blocked_by` are all passed and whose
   `loop_attempts` are under the cap (PRD order = priority — put risky,
   architecture-shaping tasks first).
2. It emits a one-task manifest with `worktrees: true`: the worker gets an
   **isolated git worktree at the loop's current HEAD**, so it sees every
   previous iteration's work and can touch nothing real.
3. The task's `check` runs at the worktree root; on success it also exports
   the worker's uncommitted changes as a patch outside the worktree
   (worktrees of passing tasks are deleted by the harness).
4. On PASS the loop `git apply --index`es the patch onto the real repo,
   appends the task's `verified` sentence to `progress.txt`, and commits:
   `ralph: <key> (iN)`. On FAIL the real repo was never touched — the loop
   just records the failure and moves on; a task parks after
   `--task-attempts` (default 2) loop-level failures.
5. All tasks passed → `<promise>COMPLETE</promise>`, exit 0. Cap reached →
   exit 2. Nothing eligible but work remains (blocked/parked) → WEDGED,
   exit 3.

## Quickstart

```bash
python3 ralph_loop.py prd.json --repo /path/to/repo --iterations 8
python3 ralph_loop.py prd.json --repo /path/to/repo --dry-run   # plan only
python3 -m unittest discover -s tests                            # self-test (mock engine, no tokens)
```

The target repo must be **clean** — the loop refuses a dirty tree. Route per
task with `engine` / `model` fields (defaults: `--engine codex`); spend the
strong lanes on risky tasks and the cheap lanes on grind. For a task risky
enough to deserve a swarm rather than one worker, run that task by hand as a
fix-swarm or panel manifest, mark it `"passes": true`, and let the loop
continue — the PRD doesn't care who satisfied the contract.

## PRD format

See `prd.example.json`. Per task: `key`, `spec` (worker instructions),
`check` (shell, runs at the repo/worktree root; exit 0 is the only PASS),
`verified` (one sentence: what a PASS proves), `passes: false`, and
optionally `blocked_by`, `engine`, `model`, `timeout_s`, `task_type`,
`context`. `{repo}` in spec/check expands to the working root. The loop
maintains `passes` and `loop_attempts`; nothing else edits the PRD.

## Caveats

- **Gitignored outputs vanish from patch exports** (`git add -A` cannot
  stage them). If a task must produce ignored paths, its check must copy
  them outside the worktree explicitly.
- `progress.txt` is loop-owned; workers are instructed not to touch it and
  it is excluded from patches.
- Keep the PRD outside the repo, or committed before starting — the
  clean-tree guard enforces the latter automatically.
- `--no-git` runs a bare mode (no worktrees, no commits) for non-repo work;
  checks then run in per-task scratch dirs.

## Provenance

Technique: Geoffrey Huntley (ghuntley.com/ralph). Practice and rules: Matt
Pocock's Ralph writeups (aihero.dev — getting-started, 11 tips, plugin
critique: fresh-session-per-iteration is the load-bearing property).
Composition and status: `docs/tiamat/evolutions/ralph-loop-backlog-burndown.md`.
Status: machinery proven (self-test + live two-lane run, 2026-07-30); the
real-backlog proving run is the upstream-PR bar.
