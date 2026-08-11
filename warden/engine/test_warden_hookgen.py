#!/usr/bin/env python3
"""Regression test for warden_hookgen.py (Tink F299 — hook fan-in).

The property under test is not "the file is generated" but the four things
fan-in has to be true about, or it is worse than the per-process status quo it
replaces:

  * **one interpreter** — every module on a moment runs in the same process, so
    the win is real. Asserted directly: each module records `os.getpid()` and
    all of them must match.
  * **failure isolation** — a module that raises is skipped and its siblings
    still run and can still block. Without this, one script's bug silently
    disarms every other hook on the moment.
  * **the failure is reported, not swallowed** — the raiser is named in the
    emitted block reason and in the log.
  * **order independence** — any block wins and every reason is included, so a
    hook's outcome never changes because another script was added ahead of it.

Runs under pytest or standalone (`python3 test_warden_hookgen.py`).
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import warden_hookgen as hg  # noqa: E402


def check(name, cond, detail=""):
    """Print like the other engine suites, but fail the pytest run too."""
    print(f"  {'PASS' if cond else 'FAIL'}: {name}")
    assert cond, f"{name}{(' — ' + detail) if detail else ''}"


# ── fixture: three synthetic hook modules on one moment ──────────────────────
#
# Names are chosen so the manifest's module-name sort puts the RAISER FIRST:
# a raiser that ran last would prove nothing about isolation.

RAISER = '''# warden-hook: Stop
raise RuntimeError("import-time explosion")


def warden_hook(event):
    return None
'''

BLOCKER = '''# warden-hook: Stop
import os


def warden_hook(event):
    open(os.environ["PIDFILE"], "a").write("blocker %d\\n" % os.getpid())
    return {"decision": "block", "reason": "blocker says no"}
'''

SILENT = '''# warden-hook: Stop
import os


def warden_hook(event):
    open(os.environ["PIDFILE"], "a").write("silent %d\\n" % os.getpid())
    return None
'''

UNDECLARED = '''"""No declaration — must not be picked up."""


def warden_hook(event):
    return {"decision": "block", "reason": "should never run"}
'''

BAD_MOMENT = '''# warden-hook: Stopp


def warden_hook(event):
    return None
'''

USER_HOOK = '''import os


def warden_hook(event):
    open(os.environ["PIDFILE"], "a").write("user %d\\n" % os.getpid())
    return None
'''


class Fixture:
    """A sandboxed corpus + output dir. Nothing here touches the live tree:
    `roots` is passed explicitly so the scan never reaches into `~/.claude`."""

    def __init__(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.scripts = self.tmp / "corpus" / "skills" / "demo" / "scripts"
        self.scripts.mkdir(parents=True)
        for name, src in (("a_raiser.py", RAISER), ("b_blocker.py", BLOCKER),
                          ("c_silent.py", SILENT), ("d_undeclared.py", UNDECLARED),
                          ("e_bad_moment.py", BAD_MOMENT)):
            (self.scripts / name).write_text(src, encoding="utf-8")
        self.corpus = self.tmp / "corpus"
        self.out = self.tmp / "warden"
        self.config = self.tmp / "config.yaml"
        self.config.write_text("corpus_root: /nowhere\n", encoding="utf-8")
        self.pidfile = self.tmp / "pids.txt"
        self.entrypoint = self.out / "hook_stop.py"

    def generate(self):
        return hg.generate(self.out, self.corpus, self.config,
                           roots=[self.corpus / "skills"])

    def manifest(self):
        return json.loads((self.out / "hooks-ir.json").read_text(encoding="utf-8"))

    def run(self, event):
        """Run the generated entrypoint as its own process, as Claude Code does."""
        self.pidfile.unlink(missing_ok=True)
        env = dict(os.environ, PIDFILE=str(self.pidfile))
        p = subprocess.run([sys.executable, str(self.entrypoint)],
                           input=json.dumps(event), text=True,
                           capture_output=True, timeout=60, env=env)
        out = p.stdout.strip()
        return p.returncode, (json.loads(out) if out.startswith("{") else {})

    def pids(self):
        if not self.pidfile.exists():
            return [], set()
        f = self.pidfile.read_text(encoding="utf-8").split()
        return [f[i] for i in range(0, len(f), 2)], {f[i] for i in range(1, len(f), 2)}


def test_declaration_scan():
    print("declaration scan")
    fx = Fixture()
    stats = fx.generate()
    mods = [e["module"] for e in fx.manifest()["moments"].get("Stop", [])]
    check("declared scripts are picked up, in module order",
          mods == ["a_raiser", "b_blocker", "c_silent"], f"got {mods}")
    check("an undeclared script is not registered", "d_undeclared" not in mods)
    check("an unknown moment warns instead of generating",
          any("Stopp" in w for w in stats["warnings"]), f"{stats['warnings']}")
    check("the manifest carries the generated-header contract",
          "do not edit" in fx.manifest()["generated_by"])
    check("one entrypoint per moment, named for the moment", fx.entrypoint.is_file())
    check("the entrypoint declares itself generated",
          fx.entrypoint.read_text(encoding="utf-8").startswith(
              "#!/usr/bin/env python3\n# GENERATED by warden_hookgen.py"))


def test_isolation_and_one_interpreter():
    print("\nfailure isolation + one interpreter")
    fx = Fixture()
    fx.generate()
    rc, decision = fx.run({"session_id": "t", "last_assistant_message": "x"})

    check("the entrypoint always exits 0 (fail open)", rc == 0, f"rc={rc}")
    check("the surviving blocker still blocks despite the raiser",
          decision.get("decision") == "block", f"got {decision}")
    check("the blocker's own reason is carried",
          "blocker says no" in decision.get("reason", ""))
    check("the raiser's failure is reported alongside, not swallowed",
          "a_raiser" in decision.get("reason", "")
          and "RuntimeError" in decision.get("reason", ""),
          f"reason={decision.get('reason', '')[:300]}")
    check("the silent module contributes no spurious decision",
          "c_silent" not in decision.get("reason", ""))

    names, pids = fx.pids()
    check("every non-raising module ran", sorted(names) == ["blocker", "silent"],
          f"got {names}")
    check("all modules share ONE interpreter process", len(pids) == 1, f"pids={pids}")

    log = fx.out / "hookgen.log"
    check("the raiser is logged even though the turn was blocked",
          log.is_file() and "a_raiser" in log.read_text(encoding="utf-8"))


def test_config_yaml_is_the_users_only_surface():
    print("\nconfig.yaml is the user's only surface")
    fx = Fixture()
    fx.generate()
    extra = fx.tmp / "user_hook.py"
    extra.write_text(USER_HOOK, encoding="utf-8")
    veto = fx.tmp / "veto.sh"
    veto.write_text("#!/bin/bash\necho 'command veto' >&2\nexit 2\n", encoding="utf-8")
    veto.chmod(0o755)
    fx.config.write_text(
        "corpus_root: /nowhere\nhooks:\n  Stop:\n"
        f"    - script: {extra}\n    - command: bash {veto}\n", encoding="utf-8")
    fx.generate()

    sources = [e["source"] for e in fx.manifest()["moments"]["Stop"]]
    check("a user hook joins the moment with no script edit anywhere",
          sources == ["declaration"] * 3 + ["config.yaml"] * 2, f"got {sources}")

    _rc, decision = fx.run({"session_id": "t"})
    names, pids = fx.pids()
    check("a config-added python hook shares the SAME interpreter",
          "user" in names and len(pids) == 1, f"names={names} pids={pids}")
    check("a config-added command hook can block (exit 2)",
          "command veto" in decision.get("reason", ""), f"got {decision}")
    check("both blocking reasons are present — any-block-wins, reasons joined",
          "blocker says no" in decision.get("reason", "")
          and "command veto" in decision.get("reason", ""))


def test_emptied_moment_stays_inert_not_missing():
    print("\nemptying a moment leaves an inert entrypoint, not a missing file")
    fx = Fixture()
    fx.generate()
    for f in fx.scripts.glob("*.py"):
        f.unlink()
    fx.generate()
    check("the entrypoint survives when its last hook leaves", fx.entrypoint.is_file())
    rc, decision = fx.run({"session_id": "t"})
    check("an emptied entrypoint is a silent pass-through",
          rc == 0 and decision == {}, f"rc={rc} decision={decision}")


def main():
    test_declaration_scan()
    test_isolation_and_one_interpreter()
    test_config_yaml_is_the_users_only_surface()
    test_emptied_moment_stays_inert_not_missing()
    print("\nall warden_hookgen tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
