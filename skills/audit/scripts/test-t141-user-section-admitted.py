#!/usr/bin/env python3
"""T141 — R-query-03 rejected `## User`, a section the renderer must write.

F259 added the `## User` section to `queries-render.py` (between
`## Verifications` and `## Other`). `R-query-03` — the rule that whitelists the
queue file's sections — was never updated, so from F259 onward every render of
any anchor holding a `[User]` row fired a warden `R-query-03: foreign H2
section(s): User` warning against output the renderer is *required* to produce.
Six anchors were in that state when it was found on 2026-08-05.

The placement is not decided here. `queries-render.py` chose it at F259 and is
the file's only writer; a rule that contradicts the sole writer is the side that
is wrong. This test pins the two together so they cannot drift again — which is
the actual failure, since neither half was individually incorrect.

Why F283's own section-order test did not catch it: its fixture carries no
`[User]` rows, so it renders six sections and never exercises the seventh.

    python3 test-t141-user-section-admitted.py
"""
import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).parent


def _load(name, filename):
    loader = importlib.machinery.SourceFileLoader(name, str(_HERE / filename))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


ap = _load("ap", "audit-plan.py")

results = []
_td = tempfile.TemporaryDirectory()
ROOT = Path(_td.name)


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def verdict(sections, n=[0]):
    """Run the checker over a queue file carrying exactly `sections`."""
    n[0] += 1
    p = ROOT / f"q{n[0]} queries.md"
    p.write_text("# [OK]  [[FX|FX]]  -  Runnable 0    User 0\n\n"
                 + "".join(f"## {s}\n\n- a row\n\n" for s in sections),
                 encoding="utf-8")
    return ap.chk_queries_sections_subsequence(p, None, None)


print("R-query-03 — the seventh section")

# The regression itself.
check("a lone ## User section is admitted",
      verdict(["User"])[0], "pass")
check("the full seven-section render passes",
      verdict(["Blockers", "Ready", "Questions", "Blocked",
               "Verifications", "User", "Other"])[0], "pass")
# The exact live shape that was failing — SONAR/TINK and four others.
check("Verifications → User → Other passes",
      verdict(["Verifications", "User", "Other"])[0], "pass")

# Position is pinned on both sides, so `User` cannot drift within the order.
v = verdict(["User", "Verifications"])
check("User before Verifications fails", v[0], "fail")
check("...for being out of order, not foreign", "out of order" in v[1], True)
v = verdict(["Other", "User"])
check("User after Other fails", v[0], "fail")
check("...also as an ordering failure", "out of order" in v[1], True)

# Widening the set must not have weakened the rule. This is the shape the
# F283 corpus fixture `query-003-bad-order` pins.
v = verdict(["Verifications", "Ready"])
check("the F283 bad-order shape still fails", v[0], "fail")
v = verdict(["Ready", "Wibble"])
check("a genuinely foreign H2 still fails", v[0], "fail")
check("...and is named in the message", "Wibble" in v[1], True)
check("a repeated section still fails",
      verdict(["Ready", "Ready"])[0], "fail")
check("an empty file passes (all sections omitted)",
      verdict([])[0], "pass")


print("\nThe rule and the renderer agree — which is the point of T141")

# The drift, stated as an assertion: every H2 `queries-render.py` can emit must
# be admissible. Read from the renderer's source so adding a section there
# without touching the rule fails HERE rather than on Dan's next render.
render_src = (_HERE.parent.parent / "audit" / "scripts"
              / "queries-render.py").read_text(encoding="utf-8")
import re
emitted = re.findall(r'_h2\("## ([^"]+)"\)', render_src)
allowed = ["Blockers", "Ready", "Questions", "Blocked",
           "Verifications", "User", "Other"]
unadmitted = [s for s in emitted if s not in allowed]
check("every section the renderer emits is admitted by the rule",
      unadmitted, [])
check("...and the renderer's order matches the rule's order",
      emitted, [s for s in allowed if s in emitted])


print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
