#!/usr/bin/env python3
"""Ralph loop over a Ringer swarm — backlog burn-down with executed verification.

The composition: Ralph is the scheduler, Ringer is the execution substrate.
A dumb sequential loop pulls the next incomplete task from a PRD, emits a
one-task manifest, and runs it through ringer.py — fresh worker session,
sandbox, executed check, retry-with-failure, scoreboard row. The HARNESS
VERDICT, never the worker, flips a task's "passes" flag; the LOOP, never the
worker, commits. Fresh-session-per-iteration is the load-bearing property:
state crosses iterations only through the repo, the PRD, and progress.txt.

PRD schema (JSON):
  {
    "name": "short-slug",
    "tasks": [
      {
        "key": "unique-key",
        "spec": "worker instructions ({repo} expands to the repo path)",
        "check": "shell command; exit 0 is the only PASS ({repo} expands)",
        "verified": "one sentence: what a PASS proves",
        "passes": false,
        "blocked_by": ["other-key", ...],        # optional
        "engine": "codex", "model": "...",       # optional per-task routing
        "timeout_s": 900, "task_type": "code-feature",  # optional
        "context": "standing context for the worker"    # optional
      }, ...
    ]
  }

Exit codes: 0 = all tasks pass (<promise>COMPLETE</promise> printed),
2 = iteration cap reached with work remaining, 3 = wedged (nothing eligible:
blocked or attempt-capped), 4 = precondition failure.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
import sys
from pathlib import Path

PROMISE = "<promise>COMPLETE</promise>"
PROGRESS_TAIL_LINES = 20


def sh(args: list[str], cwd: Path | None = None, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=capture, text=True)


def die(msg: str, code: int = 4) -> None:
    print(f"ralph-loop: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load_prd(path: Path) -> dict:
    try:
        prd = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        die(f"cannot read PRD {path}: {exc}")
    if not isinstance(prd.get("tasks"), list) or not prd["tasks"]:
        die("PRD needs a non-empty tasks list")
    keys = [t.get("key") for t in prd["tasks"]]
    if len(set(keys)) != len(keys) or not all(keys):
        die("every task needs a unique non-empty key")
    for t in prd["tasks"]:
        for field in ("spec", "check", "verified"):
            if not t.get(field):
                die(f"task {t['key']}: missing {field}")
        t.setdefault("passes", False)
        t.setdefault("loop_attempts", 0)
    return prd


def save_prd(path: Path, prd: dict) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(prd, indent=2) + "\n")
    tmp.replace(path)


def eligible(prd: dict, max_task_attempts: int) -> list[dict]:
    passed = {t["key"] for t in prd["tasks"] if t["passes"]}
    out = []
    for t in prd["tasks"]:
        if t["passes"] or t["loop_attempts"] >= max_task_attempts:
            continue
        if all(dep in passed for dep in t.get("blocked_by", [])):
            out.append(t)
    return out


def progress_tail(progress: Path) -> str:
    if not progress.exists():
        return ""
    lines = progress.read_text().splitlines()[-PROGRESS_TAIL_LINES:]
    return "\n".join(lines)


def build_spec(task: dict, prd: dict, repo: Path, progress: Path, git_mode: bool) -> str:
    repo_ref = "." if git_mode else str(repo)
    parts = [
        "You are one iteration of a Ralph loop: a fresh, stateless worker "
        "doing exactly ONE task from a larger backlog. Do not attempt any "
        "other task. Work small and finish.",
        "Your current working directory is an isolated checkout of the "
        "repository at the loop's current state — work directly here. "
        "Do not run git commit; leave every change uncommitted (the loop "
        "verifies your work, then applies and commits it). Do not touch "
        "progress.txt." if git_mode else
        f"Working root: {repo}",
        f"Standing context: {prd.get('context', '').strip()}" if prd.get("context") else "",
        f"Task context: {task['context'].strip()}" if task.get("context") else "",
        "Recent progress log (what previous iterations did):\n" + tail
        if (tail := progress_tail(progress)) else "",
        "YOUR TASK:\n" + task["spec"].replace("{repo}", repo_ref),
    ]
    return "\n\n".join(p for p in parts if p)


def build_manifest(task: dict, prd: dict, repo: Path, progress: Path, rundir: Path,
                   iteration: int, args: argparse.Namespace) -> tuple[Path, str, Path]:
    slug = prd.get("name", "prd").strip() or "prd"
    run_name = f"ralph-{slug}-i{iteration:03d}"
    git_mode = not args.no_git
    patch_path = rundir / f"i{iteration:03d}-{task['key']}.patch"
    if git_mode:
        # Check runs at the worktree root; a PASS also exports the worker's
        # uncommitted changes as a patch OUTSIDE the worktree (worktrees of
        # passing tasks are deleted by the harness).
        check = (f"( {task['check'].replace('{repo}', '.')} ) && "
                 f"git add -A && git reset -q -- progress.txt && "
                 f"git diff --cached --binary > '{patch_path}'")
    else:
        check = task["check"].replace("{repo}", str(repo))
    manifest = {
        "run_name": run_name,
        "workdir": str(rundir / "work" / f"i{iteration:03d}"),
        "max_parallel": 1,
        **({"worktrees": True, "repo": str(repo)} if git_mode else {}),
        "tasks": [{
            "key": task["key"],
            "engine": task.get("engine", args.engine),
            **({"model": task["model"]} if task.get("model") else
               ({"model": args.model} if args.model else {})),
            "task_type": task.get("task_type", "code-feature"),
            "timeout_s": int(task.get("timeout_s", args.timeout)),
            "spec": build_spec(task, prd, repo, progress, git_mode),
            "check": check,
            **({"expect_files": [str(patch_path)]} if git_mode else {}),
            "verified": task["verified"],
        }],
    }
    path = rundir / f"i{iteration:03d}-{task['key']}.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    return path, run_name, patch_path


def run_ringer(manifest: Path, args: argparse.Namespace) -> int:
    cmd = [sys.executable, str(args.ringer), "run", str(manifest),
           "--identity", args.identity]
    if args.config:
        cmd += ["--config", str(args.config)]
    print(f"ralph-loop: spawning ringer: {' '.join(cmd)}", flush=True)
    proc = subprocess.run(cmd, env={**os.environ, "RINGER_NO_SELF_UPDATE": "1"})
    return proc.returncode


def read_verdict(state_dir: Path, run_name: str, task_key: str) -> dict:
    runs = sorted((state_dir / "runs").glob(f"{run_name}*.json"),
                  key=lambda p: p.stat().st_mtime)
    if not runs:
        die(f"no run state matching {run_name} under {state_dir}/runs — "
            f"did ringer start? (check --state-dir/--config agreement)")
    state = json.loads(runs[-1].read_text())
    for t in state.get("tasks", []):
        if t.get("key") == task_key:
            return {"status": t.get("status"), "attempts": t.get("attempts"),
                    "tokens": t.get("tokens"), "run_json": str(runs[-1]),
                    "check_tail": (t.get("check_output_tail") or "")[-400:]}
    die(f"task {task_key} not found in run state {runs[-1]}")


def git(repo: Path, *args_: str) -> subprocess.CompletedProcess:
    return sh(["git", "-C", str(repo), *args_])


def guard_clean_repo(repo: Path) -> None:
    if git(repo, "rev-parse", "--git-dir").returncode != 0:
        die(f"{repo} is not a git repository (use --no-git for bare mode)")
    dirty = git(repo, "status", "--porcelain").stdout.strip()
    if dirty:
        die(f"{repo} has uncommitted changes — the loop requires a clean "
            f"tree so failed iterations can be reset safely:\n{dirty}")


def append_progress(progress: Path, line: str) -> None:
    stamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    with progress.open("a") as fh:
        fh.write(f"[{stamp}] {line}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Ralph loop over a Ringer swarm")
    ap.add_argument("prd", type=Path)
    ap.add_argument("--repo", type=Path, help="target repo/work root (default: PRD's directory)")
    ap.add_argument("--iterations", type=int, default=8)
    ap.add_argument("--task-attempts", type=int, default=2,
                    help="loop-level attempts per task before it parks (ringer retries once inside each)")
    ap.add_argument("--engine", default="codex")
    ap.add_argument("--model", default=None)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--ringer", type=Path,
                    default=Path(__file__).resolve().parent.parent.parent / "ringer.py")
    ap.add_argument("--config", type=Path, default=None,
                    help="forwarded to ringer.py --config")
    ap.add_argument("--state-dir", type=Path, default=Path.home() / ".ringer",
                    help="where ringer writes runs/ (must match config)")
    ap.add_argument("--identity", default="ralph-loop")
    ap.add_argument("--no-git", action="store_true",
                    help="bare mode: no clean guard, no reset, no commits")
    ap.add_argument("--no-commit", action="store_true",
                    help="git mode but the loop never commits (you commit)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    prd_path = args.prd.resolve()
    prd = load_prd(prd_path)
    repo = (args.repo or prd_path.parent).resolve()
    if not args.ringer.exists():
        die(f"ringer.py not found at {args.ringer} (pass --ringer)")
    if not args.no_git:
        guard_clean_repo(repo)
    progress = repo / "progress.txt"
    slug = prd.get("name", "prd").strip() or "prd"
    rundir = args.state_dir.expanduser() / "ralph" / slug
    rundir.mkdir(parents=True, exist_ok=True)

    for iteration in range(1, args.iterations + 1):
        todo = eligible(prd, args.task_attempts)
        if not todo:
            remaining = [t["key"] for t in prd["tasks"] if not t["passes"]]
            if not remaining:
                print(PROMISE)
                return 0
            print(f"ralph-loop: WEDGED — nothing eligible; remaining: {remaining}")
            return 3

        task = todo[0]
        manifest, run_name, patch_path = build_manifest(task, prd, repo, progress,
                                                        rundir, iteration, args)
        print(f"\n=== ralph-loop iteration {iteration}/{args.iterations}: "
              f"{task['key']} (engine {task.get('engine', args.engine)}) ===", flush=True)
        if args.dry_run:
            print(f"dry-run: manifest at {manifest}; stopping before spawn")
            return 0

        run_ringer(manifest, args)  # verdict comes from state, not exit code
        verdict = read_verdict(args.state_dir.expanduser(), run_name, task["key"])

        if verdict["status"] == "pass":
            if not args.no_git and patch_path.exists() and patch_path.stat().st_size:
                applied = git(repo, "apply", "--index", str(patch_path))
                if applied.returncode != 0:
                    die(f"verified patch failed to apply to {repo}: "
                        f"{applied.stderr.strip()}", 4)
            task["passes"] = True
            save_prd(prd_path, prd)
            append_progress(progress,
                            f"PASS {task['key']} (iter {iteration}, attempts "
                            f"{verdict['attempts']}, tokens {verdict['tokens']}) — {task['verified']}")
            if not args.no_git and not args.no_commit:
                git(repo, "add", "-A")
                git(repo, "commit", "-q", "-m",
                    f"ralph: {task['key']} (i{iteration})")
                print(f"ralph-loop: applied + committed {task['key']}")
        else:
            # Worktree mode: the real repo was never touched — bookkeeping only.
            task["loop_attempts"] += 1
            save_prd(prd_path, prd)
            append_progress(progress,
                            f"FAIL {task['key']} (iter {iteration}) — check tail: "
                            f"{verdict['check_tail'][:200]!r}")

    remaining = [t["key"] for t in prd["tasks"] if not t["passes"]]
    if not remaining:
        print(PROMISE)
        return 0
    print(f"ralph-loop: iteration cap reached; remaining: {remaining}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
