#!/usr/bin/env python3
"""test-f247-backlog-stamp.py — F247: `state` is the sole write-path.

The backlog banner is a deterministic function of the backlog, so a raw
hand-edit made outside `state` must be DETECTED (integrity stamp) and HEALED
(idempotent refresh_q_md re-derivation + restamp), never left one-link stale
(the T002 stale-banner bug). This exercises the stamp + self-heal core:

  1. Pure stamp round-trip — compute → restamp → read agree; recompute stable.
  2. Drift detection — a hand-edit to a bracket line breaks the stored stamp.
  3. heal_backlog_if_stale:
       - consistent backlog -> no-op, no heal, no complaint.
       - stamped + hand-edited -> heal fires once, restamps, complains.
       - unstamped (grandfathered) -> silent heal + first stamp, no complaint.
  4. state-write end-to-end -> a `state`-driven edit leaves a VALID stamp
       (the next call then only heals on a genuine out-of-band edit).

Self-contained: imports backlog-edit.py in-process, stubs refresh_q_md so the
real vault / audit-q is never touched, builds fixtures in a tmpdir, cleans up."""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path

BE = Path(__file__).parent / "backlog-edit.py"
loader = importlib.machinery.SourceFileLoader("be_mod", str(BE))
spec = importlib.util.spec_from_loader("be_mod", loader)
be = importlib.util.module_from_spec(spec)
sys.modules["be_mod"] = be
loader.exec_module(be)
# Never touch the real vault: silence the warden self-fire on fixture writes.
be._selffire = lambda *a, **k: None

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")

# A realistic backlog: frontmatter + breadcrumb + H1 + TOC + horizon sections.
BACKLOG = (
    "---\n"
    'description: "workflow-state backlog"\n'
    "---\n"
    "\n"
    ":>> [[kmr]] → [[SYS]] → [[ZZR]] → [ZZR Backlog](hook://p/ZZR%20Backlog)\n"
    "# ZZR Backlog\n"
    "\n"
    "Intro line.\n"
    "\n"
    "## Ready\n"
    "\n"
    "- **F247 — sole write-path** [Ready] — → [[F247 — sole write-path]] ^F247\n"
    "\n"
    "## Now\n"
    "\n"
    "- **F243 — boil** [Implementing] — → [[F243 — boil]] ^F243\n"
    "\n"
    "## Done\n"
    "\n"
    "_None._\n"
)

# Record refresh_q_md calls without touching the vault.
heals: list = []
be.refresh_q_md = lambda slug: heals.append(slug)

TMP = Path(tempfile.mkdtemp())
try:
    bl = TMP / "ZZR Track" / "ZZR Backlog.md"
    bl.parent.mkdir(parents=True, exist_ok=True)

    # ---- 1. Pure stamp round-trip ------------------------------------------
    print("== 1. compute → restamp → read round-trip is stable ==")
    lines = BACKLOG.splitlines(keepends=True)
    rng = be._backlog_stamp_range(lines)
    if rng and lines[rng[0]].strip() == "# ZZR Backlog":
        ok("_backlog_stamp_range finds the H1 (skips frontmatter + breadcrumb)")
    else:
        no(f"stamp range wrong: {rng}")

    stamped = be.restamp_backlog(lines)
    r2 = be._backlog_stamp_range(stamped)
    stored = be.read_backlog_stamp(stamped, *r2)
    computed = be.compute_backlog_stamp(stamped, *r2)
    if stored is not None and stored == computed:
        ok(f"stored stamp matches recomputed after restamp (stamp={stored})")
    else:
        no(f"stored={stored} computed={computed} mismatch after restamp")

    # Re-stamping an already-stamped backlog is idempotent (no change).
    if be.restamp_backlog(stamped) == stamped:
        ok("restamp is idempotent on an already-stamped backlog")
    else:
        no("restamp changed an already-stamped backlog")

    # The stamp sits directly under the H1 as an HTML comment.
    if stamped[r2[0] + 1].strip().startswith("<!-- state:backlog "):
        ok("stamp is written on the line directly under the H1")
    else:
        no(f"stamp misplaced: {stamped[r2[0] + 1]!r}")

    # ---- 2. Drift detection -------------------------------------------------
    print("== 2. a bracket hand-edit breaks the stored stamp ==")
    edited = [ln.replace("[Ready]", "[Questions]") if "F247" in ln else ln
              for ln in stamped]
    re2 = be._backlog_stamp_range(edited)
    if be.read_backlog_stamp(edited, *re2) != be.compute_backlog_stamp(edited, *re2):
        ok("hand-editing a bracket makes stored != computed (drift detected)")
    else:
        no("bracket edit did not break the stamp")

    # ---- 3. heal_backlog_if_stale semantics --------------------------------
    print("== 3. heal_backlog_if_stale — no-op / heal+complain / grandfather ==")

    # (a) consistent backlog -> no-op, no heal, no complaint.
    heals.clear()
    bl.write_text("".join(stamped), encoding="utf-8")
    msg = be.heal_backlog_if_stale("ZZR", bl)
    if msg is None and heals == []:
        ok("consistent backlog: no heal, no complaint")
    else:
        no(f"consistent backlog healed unexpectedly — msg={msg!r} heals={heals}")

    # (b) stamped + hand-edited -> heal fires once, restamps, complains.
    heals.clear()
    bl.write_text("".join(edited), encoding="utf-8")   # stale stamp on disk
    msg = be.heal_backlog_if_stale("ZZR", bl)
    after = bl.read_text(encoding="utf-8").splitlines(keepends=True)
    ra = be._backlog_stamp_range(after)
    valid = be.read_backlog_stamp(after, *ra) == be.compute_backlog_stamp(after, *ra)
    if (msg and "hand-edit detected" in msg and heals == ["ZZR"] and valid
            and "[Questions]" in "".join(after)):
        ok("hand-edited backlog: heal fired once, restamped valid, edit preserved, complaint returned")
    else:
        no(f"heal wrong — msg={msg!r} heals={heals} valid={valid}")

    # (b2) calling heal again is now a no-op (idempotent convergence).
    heals.clear()
    msg = be.heal_backlog_if_stale("ZZR", bl)
    if msg is None and heals == []:
        ok("second heal on the now-consistent backlog is a no-op")
    else:
        no(f"heal not idempotent — msg={msg!r} heals={heals}")

    # (c) unstamped backlog (legacy) -> silent heal + first stamp, no complaint.
    heals.clear()
    bl.write_text(BACKLOG, encoding="utf-8")   # never stamped
    msg = be.heal_backlog_if_stale("ZZR", bl)
    after = bl.read_text(encoding="utf-8").splitlines(keepends=True)
    ra = be._backlog_stamp_range(after)
    if (msg is None and heals == ["ZZR"]
            and be.read_backlog_stamp(after, *ra) is not None):
        ok("unstamped backlog: silent heal + first stamp added, no accusation")
    else:
        no(f"grandfather path wrong — msg={msg!r} heals={heals}")

    # ---- 4. a state-driven edit leaves a valid stamp -----------------------
    print("== 4. perform_edit + end-restamp leaves a valid state:backlog stamp ==")
    bl.write_text("".join(stamped), encoding="utf-8")
    be.perform_edit(bl, "same", "F247", "Active", "", "", False, False,
                    next_text="build the stamp + heal")
    # Mirror the state cascade's end-restamp step.
    ln3 = bl.read_text(encoding="utf-8").splitlines(keepends=True)
    st3 = be.restamp_backlog(ln3)
    if st3 != ln3:
        bl.write_text("".join(st3), encoding="utf-8")
    final = bl.read_text(encoding="utf-8").splitlines(keepends=True)
    rf = be._backlog_stamp_range(final)
    if (be.read_backlog_stamp(final, *rf) == be.compute_backlog_stamp(final, *rf)
            and "[Active]" in "".join(final)):
        ok("after a state-style edit + restamp, the stamp is valid for the new content")
    else:
        no("state-style edit left an invalid/stale stamp")

finally:
    import shutil
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
