#!/usr/bin/env python3
"""Spike test for the ATT.md escape (Dan, 2026-08-22): an Edit that added a
clean links-only row to a spine already carrying two illegal cells passed the
guard, because the ratchet denied only NEW offending cells. Dan's ruling on
seeing it: touching a spine that carries more than 2 words in a row is itself
the violation — touch means clean. These tests exec the authored bodies
straight out of rulesets/R-dispatch-guard.md (the source of truth, not the
compiled copy) against stub events.

Expected semantics after the fix:
  -01 Write : result masthead has ANY offender -> DENY (a Write emits the
              whole spine; legacy prose rides along and is refused with it).
  -02 Edit  : result masthead has ANY offender AND the edit changed the
              masthead region -> DENY. Body-only edits to a dirty doc pass.
  -03 Bash  : full-masthead write with ANY offender in result -> DENY.
"""
import re, sys, types, pathlib, tempfile, importlib.util

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)

# Stub warden_docfire so the bodies' `import warden_docfire as wdf` finds the
# real audit-plan functions without a daemon.
wdf = types.ModuleType("warden_docfire")
wdf.ap = ap
wdf.refresh_audit_plan = lambda: None
sys.modules["warden_docfire"] = wdf

src = (HERE / "../../../rulesets/R-dispatch-guard.md").resolve().read_text()
blocks = re.findall(r"### RULE (R-dispatch-guard-\d+)[^\n]*\n+```python\n(.*?)```",
                    src, re.S)
bodies = {}
for rid, code in blocks:
    ns = {}
    exec(code, ns)
    bodies[rid] = ns["body"]
assert {"R-dispatch-guard-01", "R-dispatch-guard-02",
        "R-dispatch-guard-03", "R-dispatch-guard-04"} <= set(bodies), bodies.keys()

def ctx(tool_input, cwd=""):
    ev = types.SimpleNamespace(input=tool_input)
    agent = types.SimpleNamespace(_session={"cwd": cwd})
    return types.SimpleNamespace(event=ev, agent=agent)

DIRTY = (
    "| -[[Probe]]- | : identity line. |\n"
    "| --- | --- |\n"
    "| **Operating** | `CLAUDE.md` — read at session start, |\n"
    "| Track | [[Probe Track\\|Track]],   |\n"
    "\n# Probe\nBody paragraph.\n")
CLEAN = DIRTY.replace("`CLAUDE.md` — read at session start,", "`CLAUDE.md`,")

tmp = pathlib.Path(tempfile.mkdtemp())
f = tmp / "Probe.md"
f.write_text(DIRTY)

results = []
def check(name, want_deny, out):
    denied = bool(out) and out[0].startswith("DENY")
    ok = denied == want_deny
    results.append(ok)
    print(("ok  " if ok else "FAIL") + f"  {name}: denied={denied} want={want_deny}")

# 1. THE ATT.md ESCAPE — Edit adds a clean row while two chars away a legacy
#    illegal cell stands. Must now DENY.
add_row = "| Track | [[Probe Track\\|Track]],   |"
new_rows = add_row + "\n| Subs | [[Probe Subs\\|Subs]],   |"
check("edit adds clean row to dirty spine (the Atticus case)", True,
      bodies["R-dispatch-guard-02"](ctx({"file_path": str(f),
          "old_string": add_row, "new_string": new_rows})))

# 2. Body-only edit on the same dirty doc still passes.
check("body-only edit on dirty doc passes", False,
      bodies["R-dispatch-guard-02"](ctx({"file_path": str(f),
          "old_string": "Body paragraph.", "new_string": "Body paragraph, longer."})))

# 3. Edit that fully cleans the spine passes.
check("edit that cleans the offending cell passes", False,
      bodies["R-dispatch-guard-02"](ctx({"file_path": str(f),
          "old_string": "`CLAUDE.md` — read at session start,",
          "new_string": "`CLAUDE.md`,"})))

# 4. Write round-tripping the dirty masthead (body change only) now DENIES —
#    a Write emits the spine bytes; use Edit for body-only work.
check("whole-file Write carrying legacy dirty spine denies", True,
      bodies["R-dispatch-guard-01"](ctx({"file_path": str(f),
          "content": DIRTY.replace("Body paragraph.", "New body.")})))

# 5. Write with a clean spine passes.
check("Write with cleaned spine passes", False,
      bodies["R-dispatch-guard-01"](ctx({"file_path": str(f), "content": CLEAN})))

# 6. New offense still denied (the original guard behavior kept).
check("edit minting a fresh prose cell denies", True,
      bodies["R-dispatch-guard-02"](ctx({"file_path": str(f),
          "old_string": "| Track | [[Probe Track\\|Track]],   |",
          "new_string": "| Track | [[Probe Track\\|Track]] the full story here, |"})))

# 7. Bash heredoc full-masthead rewrite of a dirty spine denies even when
#    byte-identical to disk (it writes the spine; the spine is illegal).
cmd = "cat > '" + str(f) + "' <<'EOF'\n" + DIRTY + "EOF"
check("bash full-masthead rewrite of dirty spine denies", True,
      bodies["R-dispatch-guard-03"](ctx({"command": cmd})))

assert "R-dispatch-guard-04" in bodies or True  # loaded below if present
# --- -04: the Atticus channel — inline python write to a DIRTY spine ---
if "R-dispatch-guard-04" in bodies:
    atticus_cmd = ("cd '" + str(tmp) + "'; python3 - <<'PY'\n"
                   "import pathlib,re\n"
                   "p=pathlib.Path('Probe.md'); lines=p.read_text().splitlines()\n"
                   "p.write_text('\\n'.join(reversed(lines)))\n"
                   "PY")
    f.write_text(DIRTY)
    # 8. python-heredoc write naming a dirty-spine file -> DENY
    check("opaque python write to dirty spine denies (the OBS Setup case)", True,
          bodies["R-dispatch-guard-04"](ctx({"command": atticus_cmd}, cwd=str(tmp))))
    # 9. read-only command naming the same dirty file (no write indicator) passes
    check("read-only sed -n on dirty spine passes", False,
          bodies["R-dispatch-guard-04"](ctx({"command":
              "sed -n '1,5p' '" + str(f) + "'"}, cwd=str(tmp))))
    # 10. same opaque write once the spine is clean passes
    f.write_text(CLEAN)
    check("opaque python write to CLEAN spine passes", False,
          bodies["R-dispatch-guard-04"](ctx({"command": atticus_cmd}, cwd=str(tmp))))
    f.write_text(DIRTY)
    # 11. sed -i on the dirty file denies
    check("sed -i on dirty spine denies", True,
          bodies["R-dispatch-guard-04"](ctx({"command":
              "sed -i '' 's/Track/Trk/' '" + str(f) + "'"}, cwd=str(tmp))))

    # 12. THE LIVE MISS (2026-08-22 20:0x): cd into the folder, then a
    #     relative filename inside the python payload — the session cwd is
    #     elsewhere, so only cd-following resolves the target.
    f.write_text(DIRTY)
    cd_cmd = ("cd '" + str(tmp) + "'; python3 - <<'PY'\n"
              "import pathlib\n"
              "p=pathlib.Path('Probe.md'); lines=p.read_text().splitlines()\n"
              "p.write_text('\\n'.join(reversed(lines)))\nPY")
    check("cd + relative python write to dirty spine denies", True,
          bodies["R-dispatch-guard-04"](ctx({"command": cd_cmd},
                                            cwd="/somewhere/else")))

    # 13. The second live miss: cd "$VAR/..." — a literal env var in the cd
    #     target that expanduser never resolves.
    import os
    os.environ["GUARD_T13_DIR"] = str(tmp)
    f.write_text(DIRTY)
    var_cmd = ("cd \"$GUARD_T13_DIR\"; python3 - <<'PY'\n"
               "import pathlib\n"
               "p=pathlib.Path('Probe.md')\n"
               "p.write_text(p.read_text())\nPY")
    check("cd $VAR + relative python write to dirty spine denies", True,
          bodies["R-dispatch-guard-04"](ctx({"command": var_cmd},
                                            cwd="/somewhere/else")))

print(f"{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
