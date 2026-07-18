#!/usr/bin/env python3
"""test-f260-runnable-user-banner.py — F260: the status-line banner's two
actionable buckets are Runnable (= [Ready]/[Agreed] + [Active]/[Implementing])
and User (= [Questions] + [User]); Verify is dropped from the pair (stays a
horizon count). Asserts queries-render.py:derive_banner on a fixture backlog
carrying one of each bracket.

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

# Runnable = Ready(1) + Implementing(1) + Active(1) = 3
ok("Runnable = Ready + Active + Implementing (3)") if "Runnable 3" in banner \
    else no(f"expected 'Runnable 3' in: {banner}")

# User = Questions(1) + User(1) = 2
ok("User = Questions + User (2)") if "User 2" in banner \
    else no(f"expected 'User 2' in: {banner}")

# The old labels are gone.
ok("no 'Ready N' actionable label") if "Ready 3" not in banner and " Ready " not in banner \
    else no(f"stale Ready label in: {banner}")
ok("no 'Questions N' actionable label") if "Questions " not in banner \
    else no(f"stale Questions label in: {banner}")

# Verify is NOT in the actionable pair — it only appears as the horizon count.
# (derive_banner's Verify horizon count is 0 here since F6 is in Now, not the
# Verify horizon — so the point is simply that no "User" count absorbed it.)
ok("Verify not folded into User (User stays 2, not 3)") if "User 2" in banner \
    else no("Verify leaked into the User bucket")

# TAG must be U+A (has both a User-plate item and a Runnable item).
ok("TAG is U+A (both plates non-empty)") if banner.startswith("# [U+A]") \
    else no(f"expected TAG [U+A], got: {banner[:12]}")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
