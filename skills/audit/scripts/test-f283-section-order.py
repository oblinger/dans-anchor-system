#!/usr/bin/env python3
"""F283 stage 2 — the queue file's section contract.

Order is `Blockers → Ready → Questions → Blocked → Verifications → Other`, and
the two ends of that list carry the load:

  - **Blockers** is COMPUTED. A row is in it because some *other* row names it in
    a `[Blocked <handle>]`, and it is promoted out of whatever section would
    otherwise hold it — including Verifications. Before this, the blocked→blocker
    edge was readable only from the waiting end, so a blocker never knew it was
    one and four Dan-gated rows sat still through three clean sweeps.
  - **Other** is F284's catch-all and must STAY LAST. § Design omitted it, which
    reads as an oversight — dropping it would reinstate the exact defect F284
    fixed (47 of 99 frontier rows dropped in silence, 2026-07-29). The coverage
    assertion is what proves it is still total.

`[Verify-by <date>]` renders nowhere: the bracket promises nothing happens until
the date and `sweep_stale_brackets` auto-Dones the row when it arrives.

Run: python3 test-f283-section-order.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "qr", Path(__file__).resolve().parent / "queries-render.py")
qr = importlib.util.module_from_spec(_spec)
sys.modules["qr"] = qr
_spec.loader.exec_module(qr)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


BANNER = "# [T]  [[X|X]]  -  Runnable 1    User 1   |   Now 1    Next 0    Later 0    Verify 0    Icebox 0"


def render(backlog_text, next_actions=None, verify_questions=None):
    """Render a throwaway backlog and return (body_lines, h2_list)."""
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "X Backlog.md"
        f.write_text(backlog_text, encoding="utf-8")
        rows = qr.parse_backlog(f)
        body = qr.build_queries_body(
            "X", BANNER, rows, {}, next_actions or {}, verify_questions or {}, f)
    body = body or []
    return body, [ln for ln in body if ln.startswith("## ")]


# A backlog carrying one row for every section at once. F001 is named by F002's
# bracket, so F001 must leave Ready and lead the file; V-ROW is a Verify that
# nothing depends on, so it stays put at the bottom.
FULL = """# X Backlog

## Now

- **F001 — The blocker** [Ready] — a row others wait on. ^F001
- **F002 — Waits on F001** [Blocked F001] — cannot start. ^F002
- **F003 — Needs an answer** [Questions] — user-gated. ^F003
- **F004 — Plain ready** [Ready] — nothing waits on this. ^F004
- **F005 — Waits on the world** [Waiting] — Waiting on: the bridge. ^F005
- **F006 — A check** [Verify] — did it work. ^F006
- **F007 — Odd state** [Designing] — the catch-all's customer. ^F007
"""


def main():
    body, h2s = render(FULL, next_actions={"F001": "do it", "F004": "do it"})

    # --- the order itself ------------------------------------------------
    check("all six sections render",
          h2s, ["## Blockers", "## Ready", "## Questions",
                "## Blocked", "## Verifications", "## Other"])
    check("Other is last", h2s[-1], "## Other")
    check("Blockers is first", h2s[0], "## Blockers")

    # --- Blockers is computed, and promotes out of Ready ------------------
    blockers = body[body.index("## Blockers") + 1:body.index("")]
    check("Blockers holds exactly the named row", len(blockers), 1)
    check("Blockers names F001", "F001" in blockers[0], True)
    # The waiter is LINKED, not bare — a bare F-number in a rendered queries
    # file trips C37, and the reader wants to jump to the held-up work anyway.
    check("the blocker bullet says what it gates",
          "gates [[X Backlog#^F002|F002]]" in blockers[0], True)
    ready_i = body.index("## Ready")
    ready = [ln for ln in body[ready_i + 1:] if ln.startswith("- ")][:2]
    check("F001 left Ready (promoted)", any("F001" in ln for ln in ready), False)
    check("F004 stayed in Ready", any("F004" in ln for ln in ready), True)

    # --- Blocked is the ledger: handle-rows AND waiting-rows --------------
    blocked_i = body.index("## Blocked")
    blocked = [ln for ln in body[blocked_i + 1:] if ln.startswith("- ")][:2]
    check("Blocked holds the [Blocked F001] row", any("F002" in ln for ln in blocked), True)
    check("Blocked holds the [Waiting] row", any("F005" in ln for ln in blocked), True)
    check("Blocked shows the bracket verbatim",
          any("**[Blocked F001]**" in ln for ln in blocked), True)

    # --- Questions is NOT merged into Blocked (Q2 answered (A)) -----------
    check("Questions is its own section", "## Questions" in h2s, True)
    check("the [Questions] row is not in the ledger",
          any("F003" in ln for ln in blocked), False)

    # --- no section is empty-but-emitted ---------------------------------
    body2, h2s2 = render("""# X Backlog

## Now

- **F001 — Only ready** [Ready] — alone. ^F001
""", next_actions={"F001": "go"})
    check("empty sections are omitted", h2s2, ["## Ready"])

    # --- [Verify-by] renders nowhere -------------------------------------
    body3, h2s3 = render("""# X Backlog

## Now

- **F001 — Deferred check** [Verify-by 2099-01-01] — auto-Dones on its date. ^F001
- **F002 — Plain check** [Verify] — wants a look. ^F002
""")
    check("[Verify-by] produces no section of its own", h2s3, ["## Verifications"])
    check("[Verify-by] row is absent entirely",
          any("F001" in ln for ln in body3), False)
    check("plain [Verify] still renders", any("F002" in ln for ln in body3), True)
    check("no coverage failure from dropping Verify-by",
          any("Coverage failure" in ln for ln in body3), False)

    # --- a Verify CAN be a blocker, and is promoted out of Verifications --
    body4, h2s4 = render("""# X Backlog

## Now

- **T048 — A verify that gates** [Verify] — someone waits on this. ^T048
- **F002 — Waits on the verify** [Blocked T048] — held. ^F002
""")
    check("a blocked-on Verify is promoted", h2s4[0], "## Blockers")
    check("Verifications is gone once its only row was promoted",
          "## Verifications" in h2s4, False)

    # --- a blocker is only a blocker if the waiting row is on the frontier -
    # Dan, 2026-07-30: a blocker for something parked in `## Later` is not a
    # blocker, it is a note — nothing he is working on is held up, so the row
    # is noise at the position of highest attention. Tink shipped exactly this
    # case for weeks (F238 waits on F230, both in Later) and it read as a real
    # obstruction he had never been told about.
    body5, h2s5 = render("""# X Backlog

## Now

- **F001 — Named, but only by parked work** [Ready] — nothing live waits. ^F001

## Later

- **F002 — Parked, and waiting** [Blocked F001] — deferred by intent. ^F002
""", next_actions={"F001": "go"})
    check("a Later-only waiter does not make a blocker",
          "## Blockers" in h2s5, False)
    check("the un-promoted blocker stays in Ready",
          any("F001" in ln for ln in body5), True)

    # The same edge, with the waiter moved to the frontier, DOES surface —
    # so the assertion above is about horizon and not about the edge failing
    # to parse at all.
    _, h2s6 = render("""# X Backlog

## Now

- **F001 — Named by live work** [Ready] — something live waits. ^F001

## Next

- **F002 — Live, and waiting** [Blocked F001] — on the frontier. ^F002
""", next_actions={"F001": "go"})
    check("a Next-horizon waiter does make a blocker", h2s6[0], "## Blockers")

    # --- totality: the coverage assertion still holds ---------------------
    UNCLASSIFIED = """# X Backlog

## Now

- **F001 — no bracket at all** — the largest pre-F284 class. ^F001
- **F002 — prose bracket** [big task] — bracket used as prose. ^F002
"""
    for label, text in (("full", FULL), ("unclassified", UNCLASSIFIED)):
        b, _ = render(text)
        check(f"no coverage failure ({label})",
              any("Coverage failure" in ln for ln in b), False)

    # --- a bare [Blocked] promotes nothing (33 such rows predate the gate) -
    body5, h2s5 = render("""# X Backlog

## Now

- **F001 — Bare blocked** [Blocked] — names no edge. ^F001
""")
    check("bare [Blocked] renders in the ledger", h2s5, ["## Blocked"])
    check("bare [Blocked] promotes nothing to Blockers",
          "## Blockers" in h2s5, False)

    # --- mixed waiters: one parked, one live — the live one carries it -----
    # A blocker gating both a Later row and a frontier row surfaces, and names
    # only the frontier waiter. The parked edge is real but says nothing about
    # what is held up now, so putting it in the bullet would restate the noise
    # this rule exists to remove.
    body7, h2s7 = render("""# X Backlog

## Now

- **F001 — The blocker** [Ready] — gates one parked row and one live one. ^F001

## Next

- **F008 — Live and blocked** [Blocked F001] — on the frontier. ^F008

## Later

- **F009 — Parked and blocked** [Blocked F001] — not on the frontier. ^F009
""", next_actions={"F001": "go"})
    check("a mixed blocker still surfaces", h2s7[0], "## Blockers")
    check("the frontier waiter is named",
          any("gates [[X Backlog#^F008|F008]]" in ln for ln in body7), True)
    check("the parked waiter is not named",
          any("F009" in ln for ln in body7 if ln.startswith("- ")), False)

    # --- the case that decided the design: the BLOCKER itself is off-frontier
    # Measured 2026-07-30: all four named `[Blocked <handle>]` edges vault-wide
    # point at rows the eligibility test excludes, so drawing blockers from the
    # eligible set renders the empty set forever. Being named is the reason to
    # render, and it overrides every ordinary reason not to.
    body7, h2s7 = render("""# X Backlog

## Now

- **F238 — Waits on a parked row** [Blocked F230] — cannot start. ^F238

## Later

- **F230 — Parked, and gating F238** [Waiting] — nobody is looking at this. ^F230
""")
    check("an off-frontier blocker is promoted", "## Blockers" in h2s7, True)
    check("the promoted blocker is named", any("F230" in ln for ln in body7), True)
    check("the bullet says it is parked",
          any("parked in **Later**" in ln for ln in body7), True)
    check("no coverage failure when an off-frontier row joins",
          any("Coverage failure" in ln for ln in body7), False)

    # A [Done] blocker means the WAITING row is stale — a different finding, and
    # already /groom's. Surfacing the resolved row would be noise.
    body8, h2s8 = render("""# X Backlog

## Now

- **F238 — Waits on a finished row** [Blocked F230] — stale. ^F238

## Done

- **F230 — Finished** [Done] — resolved. ^F230
""")
    check("a [Done] blocker is not promoted", "## Blockers" in h2s8, False)
    check("no coverage failure with a Done blocker",
          any("Coverage failure" in ln for ln in body8), False)

    # --- the frontmatter description names the sections, so it must refresh ---
    # `render_queries_doc` preserves existing frontmatter so a human's edits
    # survive. But the description line is machine-authored and says "do not
    # hand-edit", and preserving it verbatim left every file written before F283
    # advertising the pre-F283 section set forever — only a brand-new file ever
    # saw the updated default. Ours refreshes; anything else is left alone.
    with tempfile.TemporaryDirectory() as td:
        bl = Path(td) / "X Backlog.md"
        bl.write_text("# X Backlog\n\n## Now\n\n"
                      "- **F001 — Only ready** [Ready] — alone. ^F001\n",
                      encoding="utf-8")
        qf = Path(td) / "X queries.md"
        qf.write_text(
            "---\n"
            "description: X queries — mechanically rendered from the backlog "
            "(Verifications / Ready+Next / Questions), and copied verbatim into "
            "Q.md. Do not hand-edit; edit the backlog rows.\n"
            "aliases: [XQ]\n"
            "---\n\n# stale\n", encoding="utf-8")
        qr.render_queries_doc("X", BANNER, qr.parse_backlog(bl), {},
                              {"F001": "go"}, {}, bl)
        fm = qf.read_text(encoding="utf-8").splitlines()
        check("the machine description is refreshed to the F283 sections",
              any("(Blockers / Ready+Next / Questions / Blocked / "
                  "Verifications / Other)" in ln for ln in fm), True)
        check("the pre-F283 section list is gone",
              any("(Verifications / Ready+Next / Questions)" in ln for ln in fm),
              False)
        check("other frontmatter keys survive the refresh",
              any(ln.startswith("aliases:") for ln in fm), True)

        # The match is on the CLAIM, not the phrasing. All three are real: DKT
        # credited the retired `triage`, FEX called itself `CAE` — and both were
        # quoted, which is what a `description: {name}` prefix test trips on.
        # Tink is the last file still carrying the pre-F231 engine's claim, and
        # it is the reason that claim is matched at all: recognizing only the
        # current wording made the older one read as hand-authored, so it was
        # preserved on every render and its stale section list was unfixable.
        for label, line in (
            ("quoted + credits the retired triage engine",
             'description: "DKT queries — mechanically rendered from the backlog '
             'by triage (Verifications / Ready+Next / Questions). Do not '
             'hand-edit; edit the backlog rows."'),
            ("quoted + names a different anchor",
             'description: "CAE queries — mechanically rendered from the backlog '
             'by `queries-render.py` (Verifications / Ready+Next / Questions). '
             'Do not hand-edit; edit the backlog rows."'),
            ("pre-F231 claim — signed `Built by /ask`",
             'description: "Tink queries — agent resolutions, specific '
             'verifications, and the questions awaiting your call. Built by '
             '/ask; trims as you answer."'),
        ):
            qf.write_text(f"---\n{line}\n---\n\n# x\n", encoding="utf-8")
            qr.render_queries_doc("X", BANNER, qr.parse_backlog(bl), {},
                                  {"F001": "go"}, {}, bl)
            check(f"refreshed: {label}",
                  "(Blockers / Ready+Next / Questions / Blocked / "
                  "Verifications / Other)" in qf.read_text(encoding="utf-8"), True)

        # A description a human rewrote into their own words is NOT ours to
        # rewrite — the prefix match is what tells the two apart.
        qf.write_text("---\ndescription: Dan's own words about this page.\n---\n\n# x\n",
                      encoding="utf-8")
        qr.render_queries_doc("X", BANNER, qr.parse_backlog(bl), {},
                              {"F001": "go"}, {}, bl)
        check("a hand-authored description is preserved",
              "description: Dan's own words about this page."
              in qf.read_text(encoding="utf-8"), True)

    print()
    if FAILURES:
        print(f"FAILED {len(FAILURES)}: {', '.join(FAILURES)}")
        return 1
    print("all F283 stage-2 assertions pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
