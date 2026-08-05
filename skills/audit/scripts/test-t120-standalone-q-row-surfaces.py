#!/usr/bin/env python3
"""T120 — a standalone `Q<n>` row was rejected by three of the four checks that see it.

`DAS State.md` § Q rows specifies the feature-less question: `state define <anchor>
Backlog Q+` mints a row whose *body is the question*, sibling to `F`/`T`. It is
**self-backing** — the number is in the header, so there is no doc to link and no
sub-bullet to nest.

T079 taught C34 that. Nothing taught C44, C46, or C6, so minting one produced:

  C44  "row 'Q004' is [Questions] but names no Q-bearing target"
  C46  "links the backlog row but the row carries no inline Q sub-bullets"
  C6   "Q4 missing block-ID; expected ^TINK-Q4"  (on a line already ending ^Q004)

C6 is the one that made the rest incoherent rather than merely noisy. It applied the
CONTAINER convention (`^{container}-Q{n}`) to a row, while `queries-render` emits the
ROW convention (`#^Q004`) — so obeying C6 produced a link that resolved to nothing,
which is what made C46 fire. Three checks, three different beliefs about the same
construct's identity.

This had been *recorded* — the F292 row carries it as a second-order finding, noting
that "either the spec or the rules are stale; they currently contradict each other on
the same construct" — and left standing, because from where it was hit it read as a
one-off rather than as four surfaces sharing one stale assumption.

    python3 test-t120-standalone-q-row-surfaces.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_S = (Path(__file__).parent / "audit-q.py").resolve()
_spec = importlib.util.spec_from_file_location("aq", _S)
aq = importlib.util.module_from_spec(_spec)
sys.modules["aq"] = aq
_spec.loader.exec_module(aq)

results = []
_td = tempfile.TemporaryDirectory()
ROOT = Path(_td.name)


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


Q_ROW = (
    "- **Q004 — Should the facet be re-derived or retired?** [Questions] — the spec "
    "declares a structure no instance follows. ^Q004\n"
    "  - **(A)** Re-derive the spec from the instances.\n"
    "  - **(B)** Keep the spec and migrate the instances.\n"
    "  - **Recommendation:** Lean **(A)**\n"
    "  - **Damage:** locking — a shipped ruleset and 16 documents commit to the pick.\n"
    "  - **On answer:** (A) → rewrite the spec; (B) → arm the rule as authored.\n"
)


def backlog(body, name="TINK Backlog.md"):
    p = ROOT / name
    p.write_text("# Tink Backlog\n\n## Now\n\n" + body, encoding="utf-8")
    return p


print("C6 — the block-ID a Q ROW should carry is the ROW form, not the container form")

bl = backlog(Q_ROW)
qs = aq.extract_q_entries(bl, "TINK Backlog")
check("the row is seen as one Q entry", len(qs), 1)
q = qs[0]
# The whole defect in one assertion: `^TINK-Q4` is a container-scoped id, and this Q
# is not inside a container — it IS the row.
check("expected block-ID is the row form", aq._expected_block_id(q), "Q004")
check("...and the row's existing `^Q004` is RECOGNISED as a block-ID",
      q.has_block_id, True)
check("...with the value read off correctly", q.block_id_value, "Q004")
check("so C6 reports nothing", aq.check_c6_block_id_present(qs), [])

# The container form must still be expected everywhere it was before — this fix
# narrows to Q-rows only, and a doc-hosted Q is the overwhelmingly common case.
feat = ROOT / "TINK300 - A Feature.md"
feat.write_text("# [[TINK]] · F300 — A Feature\nOrientation.\n\n## Open Questions\n\n"
                "- **Q1 — a question?** ^F300-Q1\n"
                "  - **(A)** one\n  - **(B)** two\n"
                "  - **Recommendation:** None\n", encoding="utf-8")
fqs = aq.extract_q_entries(feat, "TINK300 - A Feature")
# Assert the SHAPE, not a hard-coded number: how the container id is derived from a
# feature filename is F300's business, not this fix's. What matters here is that a
# doc-hosted Q still gets the container form and never the bare row form.
check("a doc-hosted Q still expects the container form",
      aq._expected_block_id(fqs[0]) == f"{fqs[0].container_id}-Q1", True)
check("...and specifically NOT the bare row form",
      aq._expected_block_id(fqs[0]) == "Q001", False)

print("\nC44 — a self-backing row names no target because it IS the target")

INDEX: dict = {}
rows = [e for e in aq.backlog_entries(bl, INDEX) if e.identifier == "Q004"]
check("the row parses with its identifier", len(rows), 1)
check("C44 reports nothing on it",
      [f.code for f in aq.check_c44_questions_row_has_target(rows)], [])
# Guard the narrowing: a T-row with neither an arrow nor inline Qs is still a dead
# end, and must still be caught — otherwise this fix would have traded a false
# positive for a blind spot.
dead = backlog("- **T001 — a task** [Questions] — no target anywhere. ^T001\n",
               name="HBR Backlog.md")
dead_rows = [e for e in aq.backlog_entries(dead, INDEX) if e.identifier == "T001"]
check("...but a T-row with no target at all still fails",
      [f.code for f in aq.check_c44_questions_row_has_target(dead_rows)], ["C44"])

print("\nThe regex change is narrow — it adds one form, it does not loosen the others")

check("the container form still matches",
      bool(aq.Q_BLOCK_ID_TRAILING_RE.search("- **Q1 — x** ^F300-Q1")), True)
check("the bare row form now matches",
      bool(aq.Q_BLOCK_ID_TRAILING_RE.search("- **Q004 — x** ^Q004")), True)
# The F251 foreign-anchor guard depends on this regex NOT matching a non-Q id —
# a foreign `^F077-note` must stay unrecognised so apply_c6_fix skips rather than
# stranding it mid-line.
check("a foreign non-Q anchor is still not a Q block-ID",
      bool(aq.Q_BLOCK_ID_TRAILING_RE.search("- **Q1 — x** ^F077-note")), False)
check("...and a bare row id that is not a Q is still not one",
      bool(aq.Q_BLOCK_ID_TRAILING_RE.search("- **T116 — x** ^T116")), False)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
