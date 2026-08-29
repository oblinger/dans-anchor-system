#!/usr/bin/env python3
"""test-f601-deny-confirm.py — every deny in the corpus declares `confirm:: user`.

F601 (D), Dan 2026-08-28: every moment rule is exceptable, deny included; what
differs is who may award the letter, and that is carried by `confirm:: user` on
the rule or its ruleset. A deny added later without the line would be silently
agent-exceptable — the one failure (D) admitted. This reads the rulesets with the
shipped compiler's parser, so it cannot drift from what actually compiles.

A "deny" is a `when::` rule whose Python source carries a `DENY:` string literal
(the sentinel `warden_fire.fire` turns into a permissionDecision). Comments that
merely mention DENY do not count — R-state-region-01 is advisory and says so.
"""
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
ENGINE = REPO / "warden" / "engine"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(ENGINE))
wc = _load("warden_compile_f601", ENGINE / "warden_compile.py")
ap = _load("audit_plan_f601", REPO / "skills" / "audit" / "scripts" / "audit-plan.py")

LIT = re.compile(r"""["']DENY:""")
bad, denies = [], 0
for f in sorted(HERE.glob("R-*.md")):
    text = f.read_text(encoding="utf-8")
    for m in re.finditer(r"^# RULESET (\S+)", text, re.M):
        rs = wc.parse_ruleset(text, m.group(1), f.name)
        if not rs:
            continue
        for r in rs["rules"]:
            if not r.get("when") or not LIT.search(r.get("py_src") or ""):
                continue
            denies += 1
            if ap.effective_confirm(r, rs) != "user":
                bad.append(r["id"])

print(f"test-f601-deny-confirm: {denies} deny rules, {len(bad)} without confirm:: user")
for b in bad:
    print(f"  MISSING confirm:: user — {b}")
assert denies >= 20, f"expected the corpus to hold 20+ deny rules, parsed {denies} — the detector is broken"
sys.exit(1 if bad else 0)
