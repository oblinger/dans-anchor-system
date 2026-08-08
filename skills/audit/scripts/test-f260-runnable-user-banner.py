#!/usr/bin/env python3
"""test-f260-runnable-user-banner.py — F260's SEMANTICS, which survive F305.

F260's claim was about what the two zone-1 buckets MEAN, not what they are
called: the agent-plate bucket folds `[Active]`/`[Implementing]` in beside
`[Ready]`/`[Agreed]` (so it promises will-run-if-you-crank, not
fresh-and-untouched), the user-plate bucket folds `[User]` in beside
`[Questions]`, and `[Verify]` belongs to NEITHER.

F305 (2026-08-07) renamed the first bucket back from `Runnable` to `Ready` on
brevity and gave `[Verify]` a home of its own in the new `Parked` class. The
two assertions here that locked the WORD `Runnable` were updated; every
assertion about MEANING is unchanged and still passes, which is the useful
signal — the rename did not move a single row between buckets.

Self-contained: imports queries-render in-process, builds Row objects directly
(no vault I/O), and reads the emitted banner string."""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


qr = _load("queries_render_mod", HERE / "queries-render.py")

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")


def mkrow(identifier, bracket, horizon="Now"):
    """A minimal Row — only the fields derive_banner reads."""
    return qr.Row(
        line_num=1,
        raw_line=f"- **{identifier} — t** [{bracket}] — body",
        horizon=horizon,
        identifier=identifier,
        is_h3=False,
        bracket=bracket,
        body="body",
        arrow_link=None,
    )


# Stub _row_q_count (a [Questions] row would otherwise resolve a doc): 1 each.
qr._row_q_count = lambda r, vi: 1
qr._count_qfix_subs = lambda bf: 0  # no B-QFix noise

# Fixture: one of each actionable bracket, all in an active horizon.
rows = [
    mkrow("F1", "Ready"),
    mkrow("F2", "Implementing"),   # alias for Active
    mkrow("F3", "Active"),
    mkrow("F4", "Questions"),
    mkrow("F5", "User"),
    mkrow("F6", "Verify"),         # off the actionable pair (horizon count only)
]

banner = qr.derive_banner("ZZR", rows, Path("/fake/ZZR Backlog.md"), {})
print(f"== banner ==\n  {banner}\n")

# The agent plate = Ready(1) + Implementing(1) + Active(1) = 3. THE CLAIM IS
# THE FOLD, not the label: an alias bracket counts as its principal.
ok("agent plate = Ready + Active + Implementing (3)") if "Ready 3" in banner \
    else no(f"expected 'Ready 3' in: {banner}")

# User = Questions(1) + User(1) = 2
ok("User = Questions + User (2)") if "User 2" in banner \
    else no(f"expected 'User 2' in: {banner}")

# The pre-F260 label is gone: `Questions N` was the user-plate's original name
# and folding `[User]` in is what retired it.
ok("no 'Questions N' actionable label") if "Questions " not in banner \
    else no(f"stale Questions label in: {banner}")

# `[Verify]` is in NEITHER zone-1 bucket. Before F305 that was asserted only
# negatively (it must not inflate User); now it has a positive home, so assert
# both halves — a row that leaves one bucket must arrive somewhere, and
# "absent from zone 1" alone would also be satisfied by dropping it entirely.
ok("Verify not folded into User (User stays 2, not 3)") if "User 2" in banner \
    else no("Verify leaked into the User bucket")
ok("Verify not folded into the agent plate (Ready stays 3)") if "Ready 3" in banner \
    else no("Verify leaked into the agent plate")
ok("Verify lands in Parked (1)") if "Parked 1" in banner \
    else no(f"expected 'Parked 1' in: {banner}")

# TAG must be U+A (has both a User-plate item and a Runnable item).
ok("TAG is U+A (both plates non-empty)") if banner.startswith("# [U+A]") \
    else no(f"expected TAG [U+A], got: {banner[:12]}")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
