#!/usr/bin/env python3
"""test-f328-hook-install.py — pins the F328 installer (hook-install/-uninstall).

Every case runs the real installer against a scratch settings.json, registry,
adoption record and wrappers dir via the DAS_HOOK_* overrides — nothing
touches live machine state. Covers the three occupancy cases (empty /
stranger-adopt / Warden), the malformed-settings refusal, the Warden-only
moment refusal, wrapper generation for arg-carrying occupants, the
broad-matcher coexistence rule, and — the Success Criteria scenario — two
hooks (one broken) at an already-occupied moment fired through hook-run,
then unwound to byte-identical settings.json.
"""
import json
import os
import subprocess
import sys
import tempfile
import shlex
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
INSTALL = SCRIPTS / "hook-install"
UNINSTALL = SCRIPTS / "hook-uninstall"
RUNNER = SCRIPTS / "hook-run"
PASS = FAIL = 0


def check(name, ok):
    global PASS, FAIL
    print(f"  {'ok ' if ok else 'FAIL'} {name}")
    if ok:
        PASS += 1
    else:
        FAIL += 1


class Rig:
    """One scratch machine: settings.json + registry + adopted + wrappers."""

    def __init__(self, tmp, settings_obj):
        self.tmp = tmp
        self.settings = tmp / "settings.json"
        self.registry = tmp / "registry"
        self.adopted = tmp / "adopted.json"
        self.wrappers = tmp / "wrappers"
        self.log = tmp / "hook-run.log"
        self.settings.write_text(json.dumps(settings_obj, indent=2) + "\n")

    def env(self):
        return dict(os.environ,
                    DAS_HOOK_SETTINGS=str(self.settings),
                    DAS_HOOK_REGISTRY=str(self.registry),
                    DAS_HOOK_ADOPTED=str(self.adopted),
                    DAS_HOOK_WRAPPERS=str(self.wrappers),
                    DAS_HOOK_LOG=str(self.log))

    def run(self, tool, *args):
        return subprocess.run([str(tool), *args], capture_output=True,
                              text=True, env=self.env())

    def fire(self, moment, stdin=""):
        return subprocess.run([str(RUNNER), moment], input=stdin, text=True,
                              capture_output=True, env=self.env())

    def bytes(self):
        return self.settings.read_bytes()

    def reg_lines(self):
        if not self.registry.exists():
            return []
        return [l for l in self.registry.read_text().splitlines()
                if l.strip() and not l.strip().startswith("#")]


def hook(tmp, name, body="exit 0"):
    p = tmp / name
    p.write_text("#!/bin/bash\n" + body + "\n")
    p.chmod(0o755)
    return p


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        out = tmp / "out.txt"

        # ---- Case 1: empty moment -------------------------------------
        rig = Rig(tmp / "a", (tmp / "a").mkdir() or {"hooks": {}})
        h = hook(tmp, "mine.sh", f'echo mine >> "{out}"')
        before = rig.bytes()
        r = rig.run(INSTALL, "tool:post:Read", str(h))
        s = json.loads(rig.bytes())
        grp = s["hooks"]["PostToolUse"][0]
        check("case 1: registry line + runner entry at right event/matcher",
              r.returncode == 0
              and rig.reg_lines() == [f"tool:post:Read\t{h}"]
              and grp["matcher"] == "Read"
              and grp["hooks"][0]["command"] == f"{shlex.quote(str(RUNNER))} tool:post:Read")
        r = rig.run(UNINSTALL, "tool:post:Read", str(h))
        check("case 1: uninstall restores settings byte-for-byte",
              r.returncode == 0 and rig.bytes() == before
              and rig.reg_lines() == [])

        # matcher-less moment: no matcher key on the runner group
        r = rig.run(INSTALL, "prompt:submit", str(h))
        s = json.loads(rig.bytes())
        check("case 1: matcher-less moment omits the matcher key",
              r.returncode == 0
              and "matcher" not in s["hooks"]["UserPromptSubmit"][0])
        rig.run(UNINSTALL, "prompt:submit", str(h))

        # ---- runner already present: second hook is registry-only -----
        h2 = hook(tmp, "second.sh", f'echo second >> "{out}"')
        rig.run(INSTALL, "tool:post:Read", str(h))
        mid = rig.bytes()
        r = rig.run(INSTALL, "tool:post:Read", str(h2))
        check("second hook at managed moment: settings untouched, 2 lines",
              r.returncode == 0 and rig.bytes() == mid
              and len(rig.reg_lines()) == 2)
        r = rig.run(UNINSTALL, "tool:post:Read", str(h2))
        check("uninstall non-last line keeps the runner entry",
              r.returncode == 0 and rig.bytes() == mid
              and len(rig.reg_lines()) == 1)
        rig.run(UNINSTALL, "tool:post:Read", str(h))
        check("uninstall last line restores the empty settings",
              rig.bytes() == before)

        # duplicate registration refused
        rig.run(INSTALL, "tool:post:Read", str(h))
        r = rig.run(INSTALL, "tool:post:Read", str(h))
        check("duplicate registration refused", r.returncode != 0)
        rig.run(UNINSTALL, "tool:post:Read", str(h))

        # ---- Case 2: bare-path occupant is adopted --------------------
        occ = hook(tmp, "occupant.sh", f'echo occupant >> "{out}"')
        (tmp / "b").mkdir()
        rig = Rig(tmp / "b", {"hooks": {"PostToolUse": [
            {"matcher": "WebFetch", "hooks": [{"type": "command",
                                               "command": "bash /x/webfetch.sh"}]},
            {"matcher": "Read", "hooks": [{"type": "command",
                                           "command": str(occ)}]},
        ]}})
        before = rig.bytes()
        r = rig.run(INSTALL, "tool:post:Read", str(h))
        s = json.loads(rig.bytes())
        check("case 2: occupant adopted as first registry line",
              r.returncode == 0
              and rig.reg_lines() == [f"tool:post:Read\t{occ}",
                                      f"tool:post:Read\t{h}"]
              and rig.adopted.exists())
        check("case 2: runner replaces occupant at its original index",
              s["hooks"]["PostToolUse"][1]["hooks"][0]["command"]
              == f"{shlex.quote(str(RUNNER))} tool:post:Read"
              and s["hooks"]["PostToolUse"][0]["matcher"] == "WebFetch"
              and len(s["hooks"]["PostToolUse"]) == 2)
        rig.fire("tool:post:Read")
        check("case 2: stranger runs first, unchanged",
              out.read_text().splitlines() == ["occupant", "mine"])
        out.unlink()
        r = rig.run(UNINSTALL, "tool:post:Read", str(h))
        check("case 2: unwind restores settings byte-for-byte",
              r.returncode == 0 and rig.bytes() == before
              and rig.reg_lines() == [] and not rig.adopted.exists())

        # ---- Case 2: arg-carrying occupant rides a generated wrapper --
        (tmp / "c").mkdir()
        blob = f"sh -c 'echo blob >> \"{out}\"'"
        rig = Rig(tmp / "c", {"hooks": {"Stop": [
            {"hooks": [{"type": "command", "command": blob}]}]}})
        before = rig.bytes()
        r = rig.run(INSTALL, "prompt:stop", str(h))
        wrappers = list(rig.wrappers.glob("*.sh")) if rig.wrappers.exists() else []
        check("case 2: wrapper generated, carries the command verbatim",
              r.returncode == 0 and len(wrappers) == 1
              and blob in wrappers[0].read_text()
              and os.access(wrappers[0], os.X_OK))
        rig.fire("prompt:stop")
        check("case 2: wrapped occupant still fires",
              out.exists() and "blob" in out.read_text())
        out.unlink()
        r = rig.run(UNINSTALL, "prompt:stop", str(h))
        check("case 2: unwind deletes the wrapper and restores bytes",
              r.returncode == 0 and rig.bytes() == before
              and not list(rig.wrappers.glob("*.sh")))

        # adopted line cannot be uninstalled directly
        rig.run(INSTALL, "prompt:stop", str(h))
        w = list(rig.wrappers.glob("*.sh"))[0]
        r = rig.run(UNINSTALL, "prompt:stop", str(w))
        check("adopted occupant refuses direct uninstall", r.returncode != 0)
        rig.run(UNINSTALL, "prompt:stop", str(h))

        # ---- broad matcher coexists, is never adopted -----------------
        (tmp / "d").mkdir()
        rig = Rig(tmp / "d", {"hooks": {"PostToolUse": [
            {"matcher": "Read|Write", "hooks": [{"type": "command",
                                                 "command": "bash /x/broad.sh"}]}]}})
        r = rig.run(INSTALL, "tool:post:Read", str(h))
        s = json.loads(rig.bytes())
        check("broad-matcher occupant left in place, runner added beside it",
              r.returncode == 0 and len(s["hooks"]["PostToolUse"]) == 2
              and s["hooks"]["PostToolUse"][0]["matcher"] == "Read|Write"
              and not rig.adopted.exists())

        # ---- Case 3: Warden covers the moment -------------------------
        warden = hook(tmp, "warden-rs", "exit 0")
        (tmp / "e").mkdir()
        rig = Rig(tmp / "e", {"hooks": {"PostToolUse": [
            {"matcher": "Write|Edit", "hooks": [{"type": "command",
                                                 "command": f"{warden} hook"}]}]}})
        before = rig.bytes()
        r = rig.run(INSTALL, "tool:post:Write", str(h))
        check("case 3: registry line only, settings untouched",
              r.returncode == 0 and rig.bytes() == before
              and rig.reg_lines() == [f"tool:post:Write\t{h}"])
        r = rig.run(UNINSTALL, "tool:post:Write", str(h))
        check("case 3: uninstall is registry-only too",
              r.returncode == 0 and rig.bytes() == before
              and rig.reg_lines() == [])

        # warden-only moment with Warden present: case 3
        r = rig.run(INSTALL, "write:paper", str(h))
        check("write:{kind} with Warden present installs as case 3",
              r.returncode == 0 and rig.bytes() == before
              and rig.reg_lines() == [f"write:paper\t{h}"])

        # warden registered but binary missing: refuse
        (tmp / "f").mkdir()
        rig = Rig(tmp / "f", {"hooks": {"PostToolUse": [
            {"matcher": "Write", "hooks": [{"type": "command",
                                            "command": "/nope/warden-rs hook"}]}]}})
        before = rig.bytes()
        r = rig.run(INSTALL, "tool:post:Write", str(h))
        check("Warden registered with missing binary refuses",
              r.returncode != 0 and rig.bytes() == before
              and not rig.registry.exists())

        # ---- refusals -------------------------------------------------
        (tmp / "g").mkdir()
        rig = Rig(tmp / "g", {"hooks": {}})
        r = rig.run(INSTALL, "write:paper", str(h))
        check("write:{kind} without Warden refuses and says why",
              r.returncode != 0 and "Warden" in r.stderr)
        r = rig.run(INSTALL, "skill:pre:crank", str(h))
        check("skill:pre without Warden refuses too", r.returncode != 0)
        r = rig.run(INSTALL, "bogus:moment", str(h))
        check("unknown moment refused with vocabulary", r.returncode != 0
              and "vocabulary" in r.stderr)
        r = rig.run(INSTALL, "tool:post:Read", str(tmp / "missing.sh"))
        check("nonexistent hook refused", r.returncode != 0)
        plain = tmp / "plain.txt"
        plain.write_text("x")
        r = rig.run(INSTALL, "tool:post:Read", str(plain))
        check("non-executable hook refused", r.returncode != 0)
        r = rig.run(UNINSTALL, "tool:post:Read", str(h))
        check("uninstall of unregistered hook refused", r.returncode != 0)

        # malformed settings.json: refuse, touch nothing
        (tmp / "hm").mkdir()
        rig = Rig(tmp / "hm", {})
        rig.settings.write_text('{"hooks": {broken')
        raw = rig.bytes()
        r = rig.run(INSTALL, "tool:post:Read", str(h))
        check("malformed settings.json refused, file untouched",
              r.returncode != 0 and "malformed" in r.stderr
              and rig.bytes() == raw and not rig.registry.exists())

        # ---- Success Criteria: two hooks, one broken, occupied moment -
        (tmp / "sc").mkdir()
        occ2 = hook(tmp, "occ2.sh", f'echo occupant >> "{out}"')
        rig = Rig(tmp / "sc", {"hooks": {"PostToolUse": [
            {"matcher": "Read", "hooks": [{"type": "command",
                                           "command": str(occ2)}]}]}})
        before = rig.bytes()
        good = hook(tmp, "good.sh", f'echo good >> "{out}"')
        broken = hook(tmp, "broken.sh", "exit 1")
        r1 = rig.run(INSTALL, "tool:post:Read", str(good))
        r2 = rig.run(INSTALL, "tool:post:Read", str(broken))
        rig.fire("tool:post:Read", stdin='{"tool":"Read"}')
        log = rig.log.read_text()
        check("SC: occupant + working hook ran, broken did not suppress",
              r1.returncode == 0 and r2.returncode == 0
              and out.read_text().splitlines() == ["occupant", "good"])
        check("SC: all three firings logged, broken named with its exit",
              log.count("tool:post:Read") == 3 and "exit=1" in log
              and str(broken) in log)
        rig.run(UNINSTALL, "tool:post:Read", str(broken))
        rig.run(UNINSTALL, "tool:post:Read", str(good))
        check("SC: full removal returns settings.json to prior bytes",
              rig.bytes() == before and rig.reg_lines() == [])

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
