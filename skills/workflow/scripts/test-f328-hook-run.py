#!/usr/bin/env python3
"""test-f328-hook-run.py — pins the F328 fallback runner (hook-run).

Every case runs the real bash runner against a scratch registry via the
DAS_HOOK_REGISTRY / DAS_HOOK_LOG overrides, so nothing touches the live
machine state. Covers the design's measured claims: arbitrary whitespace,
spaced paths, comment/blank skipping, file-order execution, moment
filtering, stdin fan-out, failure isolation (broken hook logged, neighbours
run, exit 0), injection inertness, and the no-trailing-newline edge.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RUNNER = Path(__file__).resolve().parent / "hook-run"
PASS = FAIL = 0


def check(name, ok):
    global PASS, FAIL
    print(f"  {'ok ' if ok else 'FAIL'} {name}")
    if ok:
        PASS += 1
    else:
        FAIL += 1


def run(registry_text, moment, stdin="", *, tmp):
    reg = tmp / "registry"
    log = tmp / "hook-run.log"
    reg.write_text(registry_text)
    if log.exists():
        log.unlink()
    env = dict(os.environ, DAS_HOOK_REGISTRY=str(reg), DAS_HOOK_LOG=str(log))
    res = subprocess.run([str(RUNNER), moment], input=stdin, text=True,
                         capture_output=True, env=env)
    return res, (log.read_text() if log.exists() else "")


def hook(tmp, name, body):
    p = tmp / name
    p.write_text("#!/bin/bash\n" + body + "\n")
    p.chmod(0o755)
    return p


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        out = tmp / "out.txt"

        # A) whitespace variants — one space, many spaces, tabs, mixed +
        #    trailing spaces — all parse to the same executable.
        h = hook(tmp, "mark.sh", f'echo fired >> "{out}"')
        reg = (f"m:a {h}\n"
               f"m:a      {h}\n"
               f"m:a\t{h}\n"
               f"  m:a \t {h}   \n")
        res, _ = run(reg, "m:a", tmp=tmp)
        check("whitespace variants all fire (4/4)",
              res.returncode == 0 and out.read_text().count("fired") == 4)

        # B) interior spaces in the path, unquoted in the registry.
        out.unlink()
        spaced_dir = tmp / "dir with space"
        spaced_dir.mkdir()
        hs = spaced_dir / "hook.sh"
        hs.write_text(f'#!/bin/bash\necho spaced >> "{out}"\n')
        hs.chmod(0o755)
        res, _ = run(f"m:b {hs}\n", "m:b", tmp=tmp)
        check("path with interior spaces works",
              res.returncode == 0 and out.exists() and "spaced" in out.read_text())

        # C) comments (flush-left and indented), blank lines, other moments.
        out.unlink()
        res, _ = run(f"# comment\n   # indented comment\n\n"
                     f"m:other {h}\nm:c {h}\n", "m:c", tmp=tmp)
        check("comments/blanks skipped, moment filtered",
              out.read_text().count("fired") == 1)

        # D) file order is execution order.
        out.unlink()
        h1 = hook(tmp, "one.sh", f'echo one >> "{out}"')
        h2 = hook(tmp, "two.sh", f'echo two >> "{out}"')
        res, _ = run(f"m:d {h2}\nm:d {h1}\n", "m:d", tmp=tmp)
        check("file order is execution order",
              out.read_text().splitlines() == ["two", "one"])

        # E) stdin JSON reaches every child.
        out.unlink()
        hc = hook(tmp, "cat.sh", f'cat >> "{out}"; echo >> "{out}"')
        res, _ = run(f"m:e {hc}\nm:e {hc}\n", "m:e",
                     stdin='{"tool":"Read"}', tmp=tmp)
        check("stdin payload fans out to every child",
              out.read_text().count('{"tool":"Read"}') == 2)

        # F) failure isolation: broken hook logged with exit status,
        #    neighbours still run, runner exits 0, both entries in the log.
        out.unlink()
        broken = tmp / "missing.sh"  # never created
        res, log = run(f"m:f {broken}\nm:f {h}\n", "m:f", tmp=tmp)
        check("broken hook does not suppress neighbour",
              "fired" in out.read_text())
        check("runner exits 0 despite failure", res.returncode == 0)
        check("failure logged with moment+path+exit",
              "m:f" in log and str(broken) in log and "exit=1" in log)
        check("success logged too (both entries appear)",
              log.count("m:f") == 2 and "ok" in log)

        # G) hostile registry lines are inert — the remainder is one literal
        #    path, so a `;`-chain or $( ) is a filename that does not exist.
        out.unlink() if out.exists() else None
        canary = tmp / "canary.txt"
        res, log = run(f"m:g /bin/echo; touch {canary}\n"
                       f"m:g $(touch {canary})\n", "m:g", tmp=tmp)
        check("injection attempts execute nothing",
              not canary.exists() and res.returncode == 0)

        # H) final line without trailing newline still fires.
        res, _ = run(f"m:h {h}", "m:h", tmp=tmp)
        check("no-trailing-newline line fires",
              "fired" in out.read_text())

        # I) empty moment arg / missing registry are silent no-ops.
        env = dict(os.environ, DAS_HOOK_REGISTRY=str(tmp / "nope"),
                   DAS_HOOK_LOG=str(tmp / "l"))
        r1 = subprocess.run([str(RUNNER)], input="", text=True,
                            capture_output=True, env=env)
        r2 = subprocess.run([str(RUNNER), "m:x"], input="", text=True,
                            capture_output=True, env=env)
        check("no moment / no registry exit 0 silently",
              r1.returncode == 0 and r2.returncode == 0 and not r2.stdout)

        # J) red check — prove the harness can fail: a hook that writes is
        #    asserted NOT to have run for a non-matching moment.
        out.unlink()
        res, _ = run(f"m:j {h}\n", "m:zzz", tmp=tmp)
        check("red-check: non-matching moment runs nothing",
              not out.exists())

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
