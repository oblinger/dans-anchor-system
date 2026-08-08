#!/usr/bin/env python3
"""test-t159-c55-blocker-live.py — TINK T159: C55, a `[Blocked X]` edge whose
blocker is dead or invisible.

Dan, 2026-08-08: *"everything is blocked on feature 41, and feature 41 is not
showing up in my list. That's completely illegal."* He had found one instance
of two defects — a blocker parked where the render will not surface it, and a
blocker that has since gone `[Done]` while its dependants sat frozen.

Three things this pins that a live-corpus assertion could not:

  * **The horizon branch fires.** Vault-wide it currently reports ZERO, because
    the one live instance (HA F133 on `HA-T008`) was repaired on 2026-08-08,
    hours after the row was written. A zero is a claim about the checker, so
    case H constructs the exact ATT-F041 shape — `[User]` under `## Later` —
    and asserts the error.
  * **The two resolution traps stay closed.** An anchor-qualified handle must
    have its prefix stripped (case E; not stripping it is what kept `##
    Blockers` empty vault-wide), and a foreign handle must resolve against the
    foreign anchor without a false error (case D).
  * **The WHAT form is out of scope.** `[Blocked X]` legally takes either a row
    handle or a 1–3 word description of a change in the universe. A first cut
    of C55 conflated them and reported 67 findings, ~50 of them on conforming
    brackets. Cases F, G and J hold that line — G especially, because
    `mux-queue-empty` splits into a real anchor plus a plausible-looking
    remainder and is nonetheless not an edge.

Self-contained: builds fixture backlogs in a temp dir. Never reads or writes
any real vault file."""
import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

AQ = Path(__file__).parent / "audit-q.py"
_loader = importlib.machinery.SourceFileLoader("audit_q_t159", str(AQ))
_spec = importlib.util.spec_from_loader("audit_q_t159", _loader)
aq = importlib.util.module_from_spec(_spec)
sys.modules["audit_q_t159"] = aq
_loader.exec_module(aq)

PASS = 0
FAIL = 0


def ok(m):
    global PASS
    PASS += 1
    print(f"  ok    {m}")


def no(m, got=None, want=None):
    global FAIL
    FAIL += 1
    print(f"  FAIL  {m}")
    if got is not None or want is not None:
        print(f"          got  {got!r}")
        print(f"          want {want!r}")


def run(backlogs: dict, scope=None):
    """backlogs: {anchor: [lines]}. Returns C55 findings for `scope` anchors
    (default: all)."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        paths = {}
        for name, lines in backlogs.items():
            d = root / name
            d.mkdir()
            p = d / f"{name} Backlog.md"
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")
            paths[name] = p
        index = aq.build_vault_index(root)
        scoped = ({k: paths[k] for k in scope} if scope else paths)
        return [f for f in aq.check_c55_blocker_live_and_visible(
            scoped, paths, index) if f.code == "C55"]


def msgs(findings):
    return [f.message for f in findings]


# ---------------------------------------------------------------- A
print("A: the EMBER shape — the blocker is already [Done]")
f = run({"EMBER": [
    "## Later",
    "- **F007 — Thing** [Blocked EMBER-F005] — body ^F007",
    "## Done",
    "- **F005 — The blocker** [Done 2026-08-01] — body ^F005",
]})
if len(f) == 1 and "already [Done" in f[0].message:
    ok("fires, and says the row is runnable now")
else:
    no("fires, and says the row is runnable now", msgs(f), ["…already [Done…"])

# ---------------------------------------------------------------- B
print("\nB: the blocker does not exist at all")
f = run({"EMBER": [
    "## Later",
    "- **F007 — Thing** [Blocked F999] — body ^F007",
]})
if len(f) == 1 and "no row 'F999'" in f[0].message:
    ok("fires, naming the missing handle")
else:
    no("fires, naming the missing handle", msgs(f), ["…no row 'F999'…"])

# ---------------------------------------------------------------- C
print("\nC: a FOREIGN handle resolves against that anchor's backlog")
f = run({
    "MUX": ["## Later", "- **T068 — Thing** [Blocked DKT-T001] — body ^T068"],
    "DKT": ["## Done", "- **T001 — Blocker** [Done 2026-07-01] — body ^T001"],
}, scope=["MUX"])
if len(f) == 1 and "in DKT" in f[0].message and "already [Done" in f[0].message:
    ok("fires, and names the foreign anchor")
else:
    no("fires, and names the foreign anchor", msgs(f), ["…'T001' in DKT…[Done…"])

# ---------------------------------------------------------------- D
print("\nD: a foreign handle that resolves FINE is not a false error")
f = run({
    "MUX": ["## Later", "- **T068 — Thing** [Blocked DKT-T001] — body ^T068"],
    "DKT": ["## Now", "- **T001 — Blocker** [Ready] — body ^T001"],
}, scope=["MUX"])
ok("silent") if not f else no("silent", msgs(f), [])

# ---------------------------------------------------------------- E
print("\nE: an OWN-anchor qualified handle has its prefix stripped")
# `[Blocked ATT-F041]` against a row identified `F041`. Without the strip this
# looks up `ATT-F041`, misses, and reports a false MISSING — and worse, the
# same miss is what left `## Blockers` empty vault-wide until T161.
f = run({"ATT": [
    "## Later",
    "- **F040 — Thing** [Blocked ATT-F041] — body ^F040",
    "## Now",
    "- **F041 — The blocker** [User] — body ^F041",
]})
ok("silent") if not f else no("silent", msgs(f), [])

# ---------------------------------------------------------------- F
print("\nF: the WHAT form names no row and is out of scope")
f = run({"MUX": [
    "## Later",
    "- **F199 — Thing** [Blocked haorui-reboot] — body ^F199",
]})
ok("silent") if not f else no("silent", msgs(f), [])

# ---------------------------------------------------------------- G
print("\nG: a WHAT form whose first word IS an anchor is still a WHAT form")
f = run({
    "MUX": ["## Later", "- **F248 — Thing** [Blocked mux-queue-empty] — body ^F248"],
})
ok("silent") if not f else no("silent", msgs(f), [])

# ---------------------------------------------------------------- H
print("\nH: the blocker is live but parked where nothing renders it")
# The ATT-F041 shape as it stood before the 2026-08-08 repair: `[User]` under
# `## Later` renders in NO section, so the reader is told nine rows are blocked
# and given no way to reach the one action that releases them.
f = run({"ATT": [
    "## Later",
    "- **F040 — Thing** [Blocked F041] — body ^F040",
    "- **F041 — The blocker** [User] — body ^F041",
]})
if len(f) == 1 and "renders in no queue" in f[0].message and "## Later" in f[0].message:
    ok("fires, naming the horizon the blocker is hiding in")
else:
    no("fires, naming the horizon the blocker is hiding in",
       msgs(f), ["…[User] under ## Later…renders in no queue…"])

# ---------------------------------------------------------------- I
print("\nI: a blocker that DOES render from Later is not a finding")
# `renders_in_body` admits Blocked/Questions/Verify from Later — the same
# predicate the renderer and the banner use, not a fourth horizon list.
f = run({"ATT": [
    "## Later",
    "- **F040 — Thing** [Blocked F041] — body ^F040",
    "- **F041 — The blocker** [Blocked upstream API] — body ^F041",
]})
ok("silent") if not f else no("silent", msgs(f), [])

# ---------------------------------------------------------------- J
print("\nJ: `B-QFix` is an identifier that contains a dash, not a qualifier")
f = run({"TINK": [
    "## Later",
    "- **T010 — Thing** [Blocked B-QFix] — body ^T010",
    "## Ready",
    "- **B-QFix — The blocker** [Ready] — body ^B-QFix",
]})
ok("silent") if not f else no("silent", msgs(f), [])

# ---------------------------------------------------------------- K
print("\nK: the bracket is a SET — C55 loops members, but the PARSER cannot "
      "deliver one")
# F305 makes the bracket a set: `[Ready, Blocked F999]` is legal and `state`
# will write it. C55 therefore iterates `bracket_members`, not the whole
# string. But audit-q's `BRACKET_RE` has no comma in its character class, so
# `_detect_status` returns '' for a compound bracket and NO entry-level checker
# — C13, C14, C16, C55, all of them — ever sees the row.
#
# Measured 2026-08-08: zero rows vault-wide carry a compound STATE bracket, so
# the gap is latent rather than active, and closing it means touching a regex
# every checker reads. Pinned here instead of quietly worked around: the first
# assertion documents the limit and will fail the day someone fixes it, which
# is the moment to delete it and assert the finding instead.
assert aq._detect_status("- **T010 — X** [Ready, Blocked F999] — body") == "", \
    "BRACKET_RE learned commas — replace this case with a live C55 assertion"
ok("the compound-bracket parse gap is real, and pinned where it will be seen")
if [m for m in aq.bracket_members("Ready, Blocked F999")
        if aq._C55_BLOCKED_RE.match(m)]:
    ok("C55's member loop already handles a compound bracket's Blocked member")
else:
    no("C55's member loop already handles a compound bracket's Blocked member",
       aq.bracket_members("Ready, Blocked F999"), ["Ready", "Blocked F999"])

# ---------------------------------------------------------------- L
print("\nL: a bare `[Blocked]` predates the grammar gate and names no edge")
f = run({"TINK": [
    "## Later",
    "- **T010 — Thing** [Blocked] — body ^T010",
]})
ok("silent") if not f else no("silent", msgs(f), [])

print("\n" + "-" * 40)
print(f"test-t159-c55-blocker-live: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
