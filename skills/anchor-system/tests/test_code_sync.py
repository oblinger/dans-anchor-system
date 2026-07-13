#!/usr/bin/env python3
"""Regression tests for the doc-mirror sync engine (`scripts/code`, verb sync).

Re-runs the sandbox breaking sequences from F188 Code-Sync Audit 2026-07-12
and asserts the fixed behavior (Findings 1-16), plus a forward/backward
round-trip sanity check. Every test builds disposable git repos / plain
folders under a fresh tempdir; HOME is redirected into the sandbox so no real
git config, manifest store, or vault data is ever touched. Runnable
standalone: python3 test_code_sync.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "code"


class SB:
    """One sandbox: anchor + here tree, there tree (git or plain), fake HOME."""

    def __init__(self, td, direction="two-way", git_repo=True):
        self.root = Path(td)
        self.home = self.root / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.anchor = self.root / "anchor"
        self.here = self.anchor / "Docs"
        self.here.mkdir(parents=True)
        if git_repo:
            self.repo = self.root / "repo"
            self.there = self.repo / "docs"
            self.there.mkdir(parents=True)
            self.git("init", "-q")
            self.git("config", "user.email", "t@test")
            self.git("config", "user.name", "t")
            # default quoting active — deterministic for the Finding-2 repro
            self.git("config", "core.quotepath", "true")
        else:
            self.repo = None
            self.there = self.root / "plain" / "docs"
            self.there.mkdir(parents=True)
        self.write_anchor([("Docs", self.there, direction)])

    def write_anchor(self, routes):
        lines = ["slug: TST", "mirror:"]
        for here_raw, there, direction in routes:
            lines += [f"  - here: {here_raw}",
                      f"    there: {there}",
                      f"    direction: {direction}"]
        (self.anchor / ".anchor").write_text("\n".join(lines) + "\n")

    def env(self):
        env = {k: v for k, v in os.environ.items()
               if k != "XDG_CONFIG_HOME" and not k.startswith("GIT_")}
        env["HOME"] = str(self.home)
        env["GIT_CONFIG_NOSYSTEM"] = "1"
        return env

    def git(self, *args):
        res = subprocess.run(["git", "-C", str(self.repo)] + list(args),
                             capture_output=True, text=True, env=self.env())
        assert res.returncode == 0, f"git {args}: {res.stderr}"
        return res.stdout

    def commit(self, msg="x"):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)

    def sync(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "sync", str(self.anchor)] + list(args),
            capture_output=True, text=True, env=self.env())

    def manifest_paths(self):
        d = (self.repo / ".git" / "anchor-sync") if self.repo else \
            (self.home / ".config" / "anchor-system" / "sync-manifests")
        return sorted(d.glob("*.json")) if d.exists() else []


def w(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.chmod(path.stat().st_mode | 0o200)
    path.write_text(text)


def baseline(sb: SB, files: dict, commit=True):
    """Seed here-side files, sync them forward, optionally commit there."""
    for name, content in files.items():
        w(sb.here / name, content)
    res = sb.sync()
    assert res.returncode == 0, res.stdout + res.stderr
    if commit and sb.repo:
        sb.commit("baseline")


# ── Finding 1 — --take-* all must never delete unflagged / one-sided files ───
def test_f01_take_there_all_spares_new_draft():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        baseline(sb, {"a.md": "v1\n"})
        w(sb.there / "a.md", "ILLICIT UNCOMMITTED there edit\n")  # quarantined
        w(sb.here / "draft.md", "my new draft\n")                 # never synced
        res = sb.sync("--take-there", "all")
        assert res.returncode == 0, res.stdout + res.stderr
        assert (sb.here / "draft.md").read_text() == "my new draft\n", \
            "draft.md was deleted by --take-there all"
        assert (sb.there / "draft.md").exists()
        assert (sb.here / "a.md").read_text() == "ILLICIT UNCOMMITTED there edit\n"
    print("PASS  f01_take_there_all_spares_new_draft")


def test_f01_take_here_all_spares_quarantined_wip():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        baseline(sb, {"a.md": "v1\n"})
        w(sb.here / "a.md", "here v2\n")
        w(sb.there / "a.md", "there v2\n")
        sb.commit("there edit")                     # true CONFLICT on a.md
        w(sb.there / "wip.md", "uncommitted WIP\n")  # quarantined new there file
        res = sb.sync("--take-here", "all")
        assert res.returncode == 1, res.stdout + res.stderr
        assert "QUARANTINE" in res.stdout
        assert (sb.there / "wip.md").read_text() == "uncommitted WIP\n", \
            "wip.md was destroyed by --take-here all"
        assert (sb.there / "a.md").read_text() == "here v2\n"  # conflict resolved
        # deleting the quarantined file needs the explicit path
        res = sb.sync("--take-here", "wip.md")
        assert res.returncode == 0, res.stdout + res.stderr
        assert not (sb.there / "wip.md").exists()
    print("PASS  f01_take_here_all_spares_quarantined_wip")


# ── Finding 2 — C-quoted (non-ASCII) paths must still hit the quarantine ─────
def test_f02_nonascii_uncommitted_edit_quarantined():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        baseline(sb, {"plan — notes.md": "clean\n", "plain.md": "clean\n"})
        w(sb.there / "plan — notes.md", "ILLICIT UNCOMMITTED there edit\n")
        w(sb.there / "plain.md", "ILLICIT UNCOMMITTED there edit\n")
        res = sb.sync()
        assert res.returncode == 1, res.stdout + res.stderr
        assert res.stdout.count("QUARANTINE") == 2, res.stdout
        assert (sb.here / "plan — notes.md").read_text() == "clean\n", \
            "uncommitted non-ASCII edit was transported into the anchor"
        assert (sb.here / "plain.md").read_text() == "clean\n"
    print("PASS  f02_nonascii_uncommitted_edit_quarantined")


# ── Finding 3 — case / NFC-NFD collisions conflict instead of clobbering ─────
def test_f03_case_collision_conflicts():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        w(sb.here / "Case.md", "content A\n")
        w(sb.there / "case.md", "content B\n")
        sb.commit("there side")
        res = sb.sync("--init")
        assert res.returncode == 1, res.stdout + res.stderr
        assert "collision" in res.stdout, res.stdout
        assert (sb.here / "Case.md").read_text() == "content A\n"
        assert (sb.there / "case.md").read_text() == "content B\n"
        assert sb.git("status", "--porcelain").strip() == "", \
            "committed there-side content was clobbered"
    print("PASS  f03_case_collision_conflicts")


def test_f03_nfc_nfd_collision_preserves_anchor():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        nfc = unicodedata.normalize("NFC", "café.md")
        nfd = unicodedata.normalize("NFD", "café.md")
        w(sb.here / nfc, "content A\n")
        w(sb.there / nfd, "content B\n")
        sb.commit("there side")
        res = sb.sync("--init")
        assert res.returncode == 1, res.stdout + res.stderr
        assert "collision" in res.stdout, res.stdout
        assert (sb.here / nfc).read_text() == "content A\n", \
            "anchor-side content destroyed by NFD/NFC clobber"
    print("PASS  f03_nfc_nfd_collision_preserves_anchor")


def test_f03_equal_content_variants_in_sync():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        w(sb.here / "Same.md", "identical\n")
        w(sb.there / "same.md", "identical\n")
        sb.commit("there side")
        res = sb.sync("--init")
        assert res.returncode == 0, res.stdout + res.stderr
        assert (sb.here / "Same.md").read_text() == "identical\n"
        assert (sb.there / "same.md").read_text() == "identical\n"
    print("PASS  f03_equal_content_variants_in_sync")


# ── Finding 4 — gitignored there-side files never flow backward ──────────────
def test_f04_gitignored_quarantined():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        w(sb.repo / ".gitignore", "docs/scratch.md\n")
        sb.commit("ignore rule")
        w(sb.there / "scratch.md", "generated build junk\n")
        res = sb.sync()
        assert res.returncode == 1, res.stdout + res.stderr
        assert "QUARANTINE" in res.stdout, res.stdout
        assert not (sb.here / "scratch.md").exists(), \
            "gitignored (never-committed) content entered the anchor"
    print("PASS  f04_gitignored_quarantined")


# ── Finding 5 — manifest loss must not silently resurrect deletions ──────────
def test_f05_manifest_loss_requires_init():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        baseline(sb, {"old.md": "obsolete\n", "keep.md": "keep\n"})
        (sb.here / "old.md").unlink()               # deliberate here-side delete
        for m in sb.manifest_paths():
            m.unlink()                              # manifest lost
        res = sb.sync()
        assert res.returncode == 2, res.stdout + res.stderr
        assert "--init" in res.stderr, res.stderr
        assert not (sb.here / "old.md").exists(), \
            "deleted file resurrected from a lost manifest"
    print("PASS  f05_manifest_loss_requires_init")


# ── Finding 6 — corrupt manifest: safe stop, warning, atomic writes ──────────
def test_f06_corrupt_manifest_and_atomic_write():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        baseline(sb, {"a.md": "v1\n"})
        mpaths = sb.manifest_paths()
        assert mpaths, "manifest not written"
        assert not list(mpaths[0].parent.glob("*.tmp")), "stray tmp manifest left"
        text = mpaths[0].read_text()
        mpaths[0].write_text(text[: len(text) // 2])  # simulated mid-write kill
        res = sb.sync()
        assert res.returncode == 2, res.stdout + res.stderr
        assert "resurrect" in res.stderr, res.stderr
    print("PASS  f06_corrupt_manifest_and_atomic_write")


# ── Finding 7 — there: declared with different case than on-disk ─────────────
def test_f07_case_mismatched_there_path():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td, git_repo=False)
        # build the repo under mixed case, declare `there:` in lowercase
        repo = sb.root / "Repo"
        (repo / "docs").mkdir(parents=True)
        sb.repo = repo
        sb.git("init", "-q")
        sb.git("config", "user.email", "t@test")
        sb.git("config", "user.name", "t")
        w(repo / "docs" / "g.md", "committed content\n")
        sb.commit("seed")
        lower = sb.root / "Repo".lower() / "docs"
        if not lower.exists():
            print("SKIP  f07_case_mismatched_there_path (case-sensitive fs)")
            return
        sb.there = repo / "docs"
        sb.write_anchor([("Docs", lower, "two-way")])
        res = sb.sync()
        assert res.returncode == 0, res.stdout + res.stderr
        assert "Traceback" not in res.stderr, res.stderr
        assert (sb.here / "g.md").read_text() == "committed content\n"
    print("PASS  f07_case_mismatched_there_path")


# ── Finding 8 — no enclosing repo degrades to plain three-way sync ───────────
def test_f08_no_repo_plain_three_way():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td, git_repo=False)
        baseline(sb, {"a.md": "v1\n"})
        w(sb.there / "a.md", "there v2\n")
        res = sb.sync()
        assert res.returncode == 0, res.stdout + res.stderr
        assert (sb.here / "a.md").read_text() == "there v2\n", \
            "no-repo backward transfer blocked (perpetual quarantine)"
        # conflicts must still flag in the degraded mode
        w(sb.here / "a.md", "here v3\n")
        w(sb.there / "a.md", "there v3\n")
        res = sb.sync()
        assert res.returncode == 1 and "CONFLICT" in res.stdout, res.stdout
    print("PASS  f08_no_repo_plain_three_way")


def test_f08_pull_route_to_plain_folder_ingests():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td, direction="pull", git_repo=False)
        w(sb.there / "artifact.md", "fresh generated artifact\n")
        res = sb.sync()
        assert res.returncode == 0, res.stdout + res.stderr
        assert (sb.here / "artifact.md").read_text() == "fresh generated artifact\n"
    print("PASS  f08_pull_route_to_plain_folder_ingests")


# ── Finding 9 — read-only stamp preserves the exec bit ───────────────────────
def test_f09_exec_bit_survives_stamp():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        w(sb.there / "tool.sh", "#!/bin/sh\necho hi\n")
        (sb.there / "tool.sh").chmod(0o755)
        sb.commit("exec tool")
        res = sb.sync()
        assert res.returncode == 0, res.stdout + res.stderr
        tmode = (sb.there / "tool.sh").stat().st_mode
        assert tmode & 0o111, "exec bit stripped on there side"
        assert not tmode & 0o222, "there side left writable"
        assert (sb.here / "tool.sh").stat().st_mode & 0o100, \
            "exec bit lost on backward copy"
        assert sb.git("status", "--porcelain").strip() == "", \
            "stamping left the repo permanently dirty (100755→100644)"
        res = sb.sync()  # second run stays clean too
        assert res.returncode == 0 and \
            sb.git("status", "--porcelain").strip() == ""
    print("PASS  f09_exec_bit_survives_stamp")


# ── Finding 10 — file vs directory name collision flags, never crashes ───────
def test_f10_file_dir_collision_flagged():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        w(sb.here / "notes", "here is a FILE\n")
        w(sb.there / "notes" / "sub.md", "there is a DIRECTORY\n")
        sb.commit("dir side")
        res = sb.sync("--init")
        assert res.returncode == 1, res.stdout + res.stderr
        assert "Traceback" not in res.stderr, res.stderr
        assert "directory" in res.stdout, res.stdout
        assert (sb.here / "notes").read_text() == "here is a FILE\n"
        assert (sb.there / "notes" / "sub.md").exists()
    print("PASS  f10_file_dir_collision_flagged")


# ── Finding 11 — flagged files are not re-stamped read-only ──────────────────
def test_f11_quarantined_file_stays_writable():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        baseline(sb, {"a.md": "v1\n"})
        w(sb.there / "a.md", "user WIP\n")           # w() re-adds the write bit
        res = sb.sync()
        assert res.returncode == 1 and "QUARANTINE" in res.stdout, res.stdout
        assert (sb.there / "a.md").stat().st_mode & 0o200, \
            "quarantined file re-stamped read-only while flag says fix in place"
    print("PASS  f11_quarantined_file_stays_writable")


# ── Finding 12 — unmatched --take-* paths are reported, not ignored ──────────
def test_f12_unmatched_take_reported():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        baseline(sb, {"a.md": "v1\n"})
        res = sb.sync("--take-there", "bogus.md")
        assert res.returncode == 1, res.stdout + res.stderr
        assert "matched no flagged path" in res.stdout, res.stdout
        res = sb.sync("--take-there", "all")
        assert res.returncode == 1, res.stdout + res.stderr
        assert "matched no flagged path" in res.stdout, res.stdout
    print("PASS  f12_unmatched_take_reported")


# ── Finding 13 — skipped symlinks are reported ───────────────────────────────
def test_f13_symlink_noted():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        target = sb.root / "elsewhere"
        target.mkdir()
        w(target / "x.md", "outside\n")
        (sb.here / "linked").symlink_to(target)
        w(sb.here / "a.md", "v1\n")
        res = sb.sync()
        assert res.returncode == 0, res.stdout + res.stderr
        assert "symlink skipped" in res.stdout, res.stdout
        assert not (sb.there / "linked").exists()
    print("PASS  f13_symlink_noted")


# ── Finding 14 — per-route lock blocks concurrent syncs ──────────────────────
def test_f14_lock_blocks_concurrent_and_reclaims_stale():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        baseline(sb, {"a.md": "v1\n"})
        lock = sb.manifest_paths()[0].with_suffix(".lock")
        lock.write_text(str(os.getpid()))           # a live pid holds the lock
        res = sb.sync()
        assert res.returncode == 2, res.stdout + res.stderr
        assert "another sync" in res.stderr, res.stderr
        p = subprocess.Popen([sys.executable, "-c", "pass"])
        p.wait()
        lock.write_text(str(p.pid))                 # stale holder — reclaimed
        res = sb.sync()
        assert res.returncode == 0, res.stdout + res.stderr
        assert not lock.exists(), "lock not released after sync"
    print("PASS  f14_lock_blocks_concurrent_and_reclaims_stale")


# ── Finding 15 — --init exists (CLI/design reconciliation) ───────────────────
def test_f15_init_flag_exists():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        res = subprocess.run([sys.executable, str(SCRIPT), "sync", "--help"],
                             capture_output=True, text=True, env=sb.env())
        assert res.returncode == 0 and "--init" in res.stdout, res.stdout
    print("PASS  f15_init_flag_exists")


# ── Finding 16 — here: confinement + route-overlap rejection ─────────────────
def test_f16_here_confinement_and_overlap():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        sb.write_anchor([("../escape", sb.there, "two-way")])
        res = sb.sync()
        assert res.returncode == 2, res.stdout + res.stderr
        assert "outside the anchor root" in res.stderr, res.stderr

        (sb.here / "sub").mkdir()
        other = sb.root / "other"
        other.mkdir()
        sb.write_anchor([("Docs", sb.there, "two-way"),
                         ("Docs/sub", other, "two-way")])
        res = sb.sync()
        assert res.returncode == 2, res.stdout + res.stderr
        assert "overlap" in res.stderr, res.stderr
    print("PASS  f16_here_confinement_and_overlap")


# ── regression — basic forward/backward round-trip still works ───────────────
def test_round_trip():
    with tempfile.TemporaryDirectory() as td:
        sb = SB(td)
        # dry run changes nothing
        w(sb.here / "a.md", "a1\n")
        w(sb.here / "b.md", "b1\n")
        res = sb.sync("--dry")
        assert res.returncode == 0, res.stdout + res.stderr
        assert not (sb.there / "a.md").exists() and not sb.manifest_paths()

        # forward seed + commit
        res = sb.sync()
        assert res.returncode == 0 and "2 forward" in res.stdout, res.stdout
        sb.commit("seed")

        # committed there-side edit flows backward; there is re-stamped
        w(sb.there / "a.md", "a2 from repo\n")
        sb.commit("edit a")
        res = sb.sync()
        assert res.returncode == 0 and "1 backward" in res.stdout, res.stdout
        assert (sb.here / "a.md").read_text() == "a2 from repo\n"
        assert not (sb.there / "a.md").stat().st_mode & 0o222

        # here-side edit flows forward
        w(sb.here / "b.md", "b2 from anchor\n")
        res = sb.sync()
        assert res.returncode == 0 and "1 forward" in res.stdout, res.stdout
        assert (sb.there / "b.md").read_text() == "b2 from anchor\n"

        # here-side delete propagates
        (sb.here / "b.md").unlink()
        res = sb.sync()
        assert res.returncode == 0 and "1 deleted there" in res.stdout, res.stdout
        assert not (sb.there / "b.md").exists()
        sb.commit("drop b")

        # there-side delete only flags; 'all' cannot accept it; explicit can
        sb.git("rm", "-q", "-f", "docs/a.md")
        sb.commit("drop a")
        res = sb.sync()
        assert res.returncode == 1 and "deletion:" in res.stdout, res.stdout
        assert (sb.here / "a.md").exists()
        res = sb.sync("--take-there", "all")
        assert res.returncode == 1 and (sb.here / "a.md").exists(), res.stdout
        res = sb.sync("--take-there", "a.md")
        assert res.returncode == 0, res.stdout + res.stderr
        assert not (sb.here / "a.md").exists()
    print("PASS  round_trip")


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"\nall {len(tests)} code-sync tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
