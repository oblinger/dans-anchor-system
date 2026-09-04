#!/usr/bin/env python3
"""T659 — `skill-usage` counts Skill tool calls and typed slash commands per skill.

Fixture: a projects dir with two transcripts and a skills dir with four skills.
Asserts agent/user counts, the window cut, uuid de-duplication, the plugin form,
built-ins listed apart, and script-run skills kept out of the zero list.
Run: python3 test_skill_usage.py
"""
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "skill-usage"


def line(typ, content, ts, uid):
    return json.dumps({"type": typ, "uuid": uid, "timestamp": ts, "message": {"role": typ, "content": content}})


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="t659-"))
    skills = root / "skills"
    for s in ("crank", "audit", "streams", "workflow"):
        (skills / s).mkdir(parents=True)
        (skills / s / "SKILL.md").write_text(f"# {s}\n")
    (skills / "notaskill").mkdir()                      # folder without SKILL.md — ignored
    projects = root / "projects" / "-Users-x-proj"
    (projects / "sess1" / "subagents").mkdir(parents=True)

    now = datetime.now(timezone.utc)
    fresh = now.isoformat()
    stale = (now - timedelta(days=90)).isoformat()
    skill_call = lambda s: [{"type": "tool_use", "name": "Skill", "input": {"skill": s}}]
    cmd = lambda s: f"<command-name>/{s}</command-name>\n<command-message>{s}</command-message>"

    t1 = "\n".join([
        line("assistant", skill_call("crank"), fresh, "u1"),
        line("assistant", skill_call("crank"), fresh, "u1"),        # duplicate uuid → counted once
        line("assistant", skill_call("dans:audit"), fresh, "u2"),   # plugin form
        line("user", cmd("audit"), fresh, "u3"),
        line("user", [{"type": "text", "text": cmd("compact")}], fresh, "u4"),  # built-in
        line("assistant", skill_call("crank"), stale, "u5"),        # outside the window
    ]) + "\n"
    (projects / "a.jsonl").write_text(t1)
    (projects / "sess1" / "subagents" / "b.jsonl").write_text(line("user", cmd("crank"), fresh, "u6") + "\n")

    env = dict(os.environ, HOME=str(root))            # cache lands under the fixture HOME
    r = subprocess.run([sys.executable, str(SCRIPT), "--projects", str(root / "projects"),
                        "--skills", str(skills), "--json"], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print(r.stderr); print("FAIL"); return 1
    out = json.loads(r.stdout)
    rows = {x["skill"]: x for x in out["rows"]}
    checks = {
        "crank agent 1 (uuid dedupe + window)": rows["crank"]["agent"] == 1,
        "crank user 1 (subagent transcript)": rows["crank"]["user"] == 1,
        "audit agent 1 via plugin form": rows["audit"]["agent"] == 1,
        "audit user 1": rows["audit"]["user"] == 1,
        "streams zero": out["zero"] == ["streams"],
        "workflow zero but script-run": out["zero_script_run"] == ["workflow"],
        "compact listed as built-in": out["builtins"].get("compact") == 1,
        "notaskill ignored": "notaskill" not in rows,
    }
    # second run must hit the cache and agree
    r2 = subprocess.run([sys.executable, str(SCRIPT), "--projects", str(root / "projects"),
                         "--skills", str(skills), "--json"], capture_output=True, text=True, env=env)
    checks["cached run agrees"] = json.loads(r2.stdout)["rows"] == out["rows"]
    checks["cache files written"] = any((root / ".config" / "anchor-system" / "skill-usage" / "cache").glob("*.json"))
    for k, v in checks.items():
        print(("ok   " if v else "FAIL ") + k)
    ok = all(checks.values())
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
