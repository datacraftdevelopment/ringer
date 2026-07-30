"""End-to-end machinery test for the Ralph loop, zero model calls.

Drives ralph_loop.py against the mock engine: a two-task PRD with a blocking
edge (happy path), then a MOCK_FAIL task (failure path). Proves scheduling,
edge-gating, verdict parsing from run state, passes-flag persistence,
progress logging, per-iteration commits, reset-on-fail, and stop conditions.

Run from this directory:  python3 -m unittest discover -s tests
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
RINGER = KIT.parent.parent / "ringer.py"
MOCK_WORKER = KIT.parent.parent / "engines" / "mock_worker.py"


def write_config(root: Path) -> Path:
    cfg = root / "config.toml"
    cfg.write_text(
        f'state_dir = "{root / "state"}"\n'
        f"allow_full_access = false\n"
        f"[update]\nauto = false\n"
        f"[artifact]\nenabled = false\n"
        f"[engines.mock]\n"
        f'bin = "{sys.executable}"\n'
        f'args_template = ["{MOCK_WORKER}", "{{spec}}"]\n'
        f"sandbox_args = []\n"
        f"full_access_args = []\n"
    )
    return cfg


def init_repo(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    for args in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "root"]):
        subprocess.run(["git", "-C", str(repo), *args], check=True,
                       env={**os.environ,
                            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})
    return repo


def mock_task(key: str, filename: str, blocked_by: list[str] | None = None,
              fail: bool = False) -> dict:
    spec = ("MOCK_FAIL\n" if fail else "") + \
           f"MOCK_FILE: {filename}\n{key} content\nMOCK_END\n"
    return {
        "key": key,
        "engine": "mock",
        "timeout_s": 60,
        "spec": spec,
        "check": f"test -f {filename} && grep -q '{key} content' {filename}",
        "verified": f"{filename} exists in the task dir with the expected content",
        **({"blocked_by": blocked_by} if blocked_by else {}),
    }


def run_loop(prd_path: Path, repo: Path, cfg: Path, state: Path,
             iterations: int = 4) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(KIT / "ralph_loop.py"), str(prd_path),
         "--repo", str(repo), "--config", str(cfg), "--state-dir", str(state),
         "--iterations", str(iterations), "--engine", "mock",
         "--identity", "ralph-loop-test"],
        capture_output=True, text=True,
        env={**os.environ, "RINGER_NO_SELF_UPDATE": "1",
             "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


class RalphLoopTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cfg = write_config(self.root)
        self.state = self.root / "state"
        self.repo = init_repo(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_happy_path_with_blocking_edge(self):
        prd_path = self.root / "prd.json"
        prd_path.write_text(json.dumps({
            "name": "happy",
            "tasks": [mock_task("first", "a.txt"),
                      mock_task("second", "b.txt", blocked_by=["first"])],
        }))
        result = run_loop(prd_path, self.repo, self.cfg, self.state)

        self.assertIn("<promise>COMPLETE</promise>", result.stdout, result.stderr)
        self.assertEqual(result.returncode, 0)
        # worker output crossed the worktree boundary via the exported patch
        self.assertEqual((self.repo / "a.txt").read_text(), "first content\n")
        self.assertEqual((self.repo / "b.txt").read_text(), "second content\n")
        prd = json.loads(prd_path.read_text())
        self.assertTrue(all(t["passes"] for t in prd["tasks"]))
        progress = (self.repo / "progress.txt").read_text()
        self.assertIn("PASS first", progress)
        self.assertIn("PASS second", progress)
        log = subprocess.run(["git", "-C", str(self.repo), "log", "--oneline"],
                             capture_output=True, text=True).stdout
        self.assertIn("ralph: first (i1)", log)
        self.assertIn("ralph: second (i2)", log)

    def test_failure_parks_task_and_resets(self):
        prd_path = self.root / "prd.json"
        prd_path.write_text(json.dumps({
            "name": "sad",
            "tasks": [mock_task("doomed", "never.txt", fail=True)],
        }))
        result = run_loop(prd_path, self.repo, self.cfg, self.state)

        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("WEDGED", result.stdout)
        prd = json.loads(prd_path.read_text())
        self.assertFalse(prd["tasks"][0]["passes"])
        self.assertEqual(prd["tasks"][0]["loop_attempts"], 2)
        progress = (self.repo / "progress.txt").read_text()
        self.assertIn("FAIL doomed", progress)
        log = subprocess.run(["git", "-C", str(self.repo), "log", "--oneline"],
                             capture_output=True, text=True).stdout
        self.assertNotIn("ralph:", log)

    def test_dirty_repo_refused(self):
        (self.repo / "scratch.txt").write_text("uncommitted\n")
        prd_path = self.root / "prd.json"
        prd_path.write_text(json.dumps({
            "name": "dirty", "tasks": [mock_task("t", "a.txt")]}))
        result = run_loop(prd_path, self.repo, self.cfg, self.state)
        self.assertEqual(result.returncode, 4)
        self.assertIn("uncommitted changes", result.stderr)


if __name__ == "__main__":
    unittest.main()
