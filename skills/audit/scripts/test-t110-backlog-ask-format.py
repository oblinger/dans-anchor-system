#!/usr/bin/env python3
"""T110 — ask-format checks reach a backlog's row-scoped Qs.

A Q can live in a backlog row as well as in a feature doc, and both go through
the same gate on write. Three things had to be true before the backlog could
join the checked set, and this test pins each:

  1. a Q's option zone ends at its hosting block, not at the next Q or EOF —
     otherwise every intervening row's prose reads as malformed options;
  2. a bullet-form Q header stamped `(resolved …)` is a record, not a pending
     Q — the guard existed only on the H3 path;
  3. a row-hosted Q's container is its ROW (`^T001-Q1`), not the anchor —
     otherwise C6 flags correct block-IDs and `--fix` rewrites them wrong.

Run: python3 test-t110-backlog-ask-format.py
"""
import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

AUDIT_Q = Path.home() / ".claude" / "skills" / "audit" / "scripts" / "audit-q.py"

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}{(' — ' + detail) if detail else ''}")


spec = importlib.util.spec_from_loader(
    "aq_t110", importlib.machinery.SourceFileLoader("aq_t110", str(AUDIT_Q)))
assert spec is not None and spec.loader is not None
aq = importlib.util.module_from_spec(spec)
sys.modules["aq_t110"] = aq
spec.loader.exec_module(aq)

TMP = Path(tempfile.mkdtemp())

# A backlog shaped like the real ones: a Q with no Recommendation (so its zone
# is unbounded under the old rule), an unrelated row after it carrying ordinary
# prose sub-bullets, a resolved Q, and a well-formed Q with a block-ID.
BACKLOG = """# ZZT Backlog

## Now

- **T001 — first row** [Questions] — body prose. ^T001
  - **Q1 — Which isolation mechanism?** Context sentence here.
    - **(A)** per-process temp path
    - **(B)** point HOME at a temp dir
    - **Recommendation:** None
  - **Q2 — Something with no recommendation at all?** Context. ^T001-Q2
    - **(A)** do it
    - **(B)** skip it

- **T002 — unrelated row** [Ready] — a different row entirely. ^T002
  - **Next:** do the thing.
  - Shipped 2026-08-02 — commit `abc1234`. Root cause was a stale path.
  - **Implementation note — split the seam.** Long prose that is not an option.

- **T003 — resolved-Q row** [Done] — body. ^T003
  - **Q1 — Which mechanism should win?** (resolved 2026-08-02) ^T003-Q1
    - **Resolved:** none of the above — the premise was wrong.
    - **Known cost to plan for:** moving HOME changes tilde resolution.

## Later
"""

bl = TMP / "ZZT Backlog.md"
bl.write_text(BACKLOG, encoding="utf-8")
entries = aq.extract_q_entries(bl, "ZZT")

print("pending-Q extraction")
nums = sorted((e.q_num, e.container_id) for e in entries)
check("resolved bullet-form Q is not pending",
      not any(e.source_line == 27 for e in entries))
check("two pending Qs found, both on T001", nums == [(1, "T001"), (2, "T001")],
      f"got {nums}")

print("\ncontainer attribution")
check("row-hosted Q takes the ROW as container, not the anchor",
      all(e.container_id == "T001" for e in entries),
      f"got {[e.container_id for e in entries]}")

print("\noption-zone bound")
c19 = aq.check_c19_option_bullets(entries)
check("T002's prose sub-bullets are not read as T001-Q2's options",
      c19 == [], f"got {[(f.surface_file.name, f.surface_line) for f in c19]}")

print("\nblock-ID expectations follow the row")
c6 = aq.check_c6_block_id_present(entries)
c6_lines = {f.surface_line for f in c6}
check("the Q carrying ^T001-Q2 is accepted", 12 not in c6_lines)
check("the Q with no block-ID is flagged", len(c6) == 1, f"got {len(c6)}")

print("\nwalk set includes the backlog")
files = aq.find_ask_format_files({"ZZT": bl}, vault_index={}, reachable_only=True)
check("find_ask_format_files yields the backlog", bl in [p for _, p in files],
      f"got {[p.name for _, p in files]}")

# A feature doc must be unaffected: no row openers, so no row attribution.
fd = TMP / "F001 — fixture.md"
fd.write_text(
    "---\ndescription: fixture\n---\n\n# F001 — fixture\nOrientation.\n\n"
    "## Open Questions\n\n"
    "- **Q1 — a question?** Context. ^F001-Q1\n"
    "  - **(A)** one\n"
    "  - **(B)** two\n"
    "- **Recommendation:** None\n"
    "\n## Summary\n\nbody\n", encoding="utf-8")
fd_entries = aq.extract_q_entries(fd, "F001")
print("\nfeature docs unchanged")
check("feature-doc Q keeps the file container",
      [e.container_id for e in fd_entries] == ["F001"],
      f"got {[e.container_id for e in fd_entries]}")
check("feature-doc Q raises no C19", aq.check_c19_option_bullets(fd_entries) == [])
check("feature-doc Q raises no C6", aq.check_c6_block_id_present(fd_entries) == [])

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
