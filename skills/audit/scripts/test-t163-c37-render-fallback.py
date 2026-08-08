#!/usr/bin/env python3
"""test-t163-c37-render-fallback.py — TINK T163: C37 must not fire on the
renderer's own bullet label.

`{slug} queries.md` is machine-rendered and says so in its own frontmatter
("Do not hand-edit; edit the backlog rows"). Its bullets have two authors:

  LABEL  queries-render.py `_bullet_link`. Its resolve-before-emit chain ends
         at a PLAIN-TEXT last resort when nothing resolves — no `→ [[…]]`
         arrow link, no feature-doc basename, no `^{id}` block anchor.
  BODY   copied verbatim from the backlog row, i.e. authored prose.

On 2026-08-08 six of the seven surviving vault-wide C37 errors were the label,
not the body: the audit reporting its own writer's output as a defect (the
T137 / T120 shape). The seventh — LRN TPM's `per SKA F062`, inside a bullet
BODY — was genuine, and this test pins that it stays reported.

The exemption is conditional, not blanket: `_render_label_fallback` replays the
renderer's chain, so a bare label whose row DOES have a resolvable target is
stale render output and still fires. That is what makes this a narrowing of
C37 rather than a hole in it.

  A. the exact live shape — malformed header, nothing resolves → silent
  B. the same bullet's BODY prose still fires (the exemption is positional)
  C. a row with a resolvable arrow link → bare label still fires (stale render)
  D. a row with a resolvable bold-run title → still fires
  E. a row with a `^{id}` block anchor → still fires
  F. `- **U1** F020 — …` (the User section's label slot) is exempt too
  G. a label whose row is absent from this backlog is NOT exempt

Self-contained: writes fixture Backlog/queries files to a temp dir and calls
the checker in-process. Never reads or writes any real vault file."""
import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

AQ = Path(__file__).parent / "audit-q.py"
_loader = importlib.machinery.SourceFileLoader("audit_q_t163", str(AQ))
_spec = importlib.util.spec_from_loader("audit_q_t163", _loader)
aq = importlib.util.module_from_spec(_spec)
sys.modules["audit_q_t163"] = aq
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


FM = [
    "---",
    "description: FIX queries — mechanically rendered from the backlog. "
    "Do not hand-edit; edit the backlog rows.",
    "---",
    "",
    "# [A]  [[FIX|FIX]]  -  Ready 1    User 0",
    "",
]


def run(backlog_lines, queries_body, extra_docs=()):
    """Render a fixture anchor and return its C37 findings."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "FIX Backlog.md").write_text(
            "\n".join(backlog_lines) + "\n", encoding="utf-8")
        (root / "FIX queries.md").write_text(
            "\n".join(FM + queries_body) + "\n", encoding="utf-8")
        for d in extra_docs:
            (root / f"{d}.md").write_text("stub\n", encoding="utf-8")
        index = aq.build_vault_index(root)
        found = aq.check_c37_queries_item_format(
            {"FIX": root / "FIX Backlog.md"}, index)
        return [f for f in found if f.code == "C37"]


def codes(findings):
    return sorted({f.message.split("`")[1] for f in findings})


# ---------------------------------------------------------------- A
print("A: the live shape — malformed header, chain falls all the way through")
# `- **F020 [Ready]** — body` is LRN TPM's shape: status inside the bold, no
# title. The bold run is `F020 [Ready]`, which resolves to no document.
f = run(
    ["## Now", "- **F020 [Ready]** — Set up the tooling stack for the take-home."],
    ["## Other", "- F020 — **[no state]** Set up the tooling stack for the take-home."],
)
ok("bare label is silent") if not f else no("bare label is silent", codes(f), [])

# ---------------------------------------------------------------- B
print("\nB: the exemption is positional — BODY prose still fires")
f = run(
    ["## Now", "- **F020 [Ready]** — Set up the tooling stack."],
    ["## Other", "- F020 — **[no state]** Build the Interface doc per SKA F062."],
)
if codes(f) == ["F062"]:
    ok("the label is exempt and the body reference is reported")
else:
    no("the label is exempt and the body reference is reported", codes(f), ["F062"])

# ---------------------------------------------------------------- C
print("\nC: a resolvable arrow link — a bare label is stale render, not fallback")
f = run(
    ["## Now", "- **F020 [Ready]** — body → [[F020 — Take-Home Velocity Tooling]]"],
    ["## Other", "- F020 — **[no state]** body"],
    extra_docs=["F020 — Take-Home Velocity Tooling"],
)
ok("still fires") if codes(f) == ["F020"] else no("still fires", codes(f), ["F020"])

# ---------------------------------------------------------------- D
print("\nD: a resolvable bold-run title — still fires")
f = run(
    ["## Now", "- **F020 — Take-Home Velocity Tooling** [Ready] — body"],
    ["## Other", "- F020 — **[no state]** body"],
    extra_docs=["F020 — Take-Home Velocity Tooling"],
)
ok("still fires") if codes(f) == ["F020"] else no("still fires", codes(f), ["F020"])

# ---------------------------------------------------------------- E
print("\nE: a `^{id}` block anchor on the row — still fires")
f = run(
    ["## Now", "- **F020 [Ready]** — body ^F020"],
    ["## Other", "- F020 — **[no state]** body"],
)
ok("still fires") if codes(f) == ["F020"] else no("still fires", codes(f), ["F020"])

# ---------------------------------------------------------------- F
print("\nF: the User section's `- **U1** {ID} — …` label slot")
f = run(
    ["## Now", "- **F020 [Ready]** — body"],
    ["## User", "- **U1** F020 — plug in the drive"],
)
ok("exempt too") if not f else no("exempt too", codes(f), [])

# ---------------------------------------------------------------- G
print("\nG: a label with no matching row in this backlog is NOT exempt")
f = run(
    ["## Now", "- **F001 [Ready]** — body"],
    ["## Other", "- F020 — **[no state]** body"],
)
ok("fires") if codes(f) == ["F020"] else no("fires", codes(f), ["F020"])

print("\n" + "-" * 40)
print(f"test-t163-c37-render-fallback: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
