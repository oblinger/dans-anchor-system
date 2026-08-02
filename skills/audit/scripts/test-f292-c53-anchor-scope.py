#!/usr/bin/env python3
"""F292 — a vault-wide C53 collision must not become every anchor's stop-gate.

C53 is computed over the whole vault index, correctly: a basename collision is only
visible vault-wide. The defect was in DELIVERY. `audit-q --scope backlog --anchor
SVP` returned 4 findings with none of them in SVP's tree, the F258 worklist counted
them, `state groom-list` never emptied, and the F244 stop-gate fired forever — for
SVP and simultaneously for every other anchor, since the same two collisions were
reported to all of them. No anchor could reach a groomed frontier by any action of
its own.

C53 already emits one finding per colliding PAGE rather than one per group,
precisely so each half routes to its owning anchor (F281 Q1 (D)). Ownership was
there; only the delivery ignored it.

**The live symptom had already cleared when this landed** — both collisions were
resolved by their owning anchors (F290 renamed the `Audit Design` pair; Scout F002
took `[[Ask]]`), and the vault reports zero C53 findings. So this is measured
against constructed collisions, and the fix is a structural gate against the next
one rather than a repair of a current outage.

    python3 test-f292-c53-anchor-scope.py
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


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


_td = tempfile.TemporaryDirectory()
VAULT = Path(_td.name)

# Two anchors in different trees whose pages share a basename — the C53 shape.
for owner in ("Alpha", "Beta"):
    d = VAULT / owner / "Thing"
    d.mkdir(parents=True)
    (d / ".anchor").write_text("", encoding="utf-8")
    (d / "Thing.md").write_text("# Thing\n", encoding="utf-8")
    trk = VAULT / owner / f"{owner} Track"
    trk.mkdir(parents=True)
    (trk / f"{owner} Backlog.md").write_text("# Backlog\n", encoding="utf-8")
    (VAULT / owner / ".anchor").write_text("", encoding="utf-8")

index = {"Thing": [VAULT / "Alpha" / "Thing" / "Thing.md",
                   VAULT / "Beta" / "Thing" / "Thing.md"]}

print("The collision is still detected vault-wide")

found = aq.check_c53_anchor_name_collisions(index, VAULT)
check("both halves of the pair are reported", len(found), 2)
check("...one per colliding PAGE, so each can route to its owner",
      sorted(str(f.surface_file.relative_to(VAULT)) for f in found),
      ["Alpha/Thing/Thing.md", "Beta/Thing/Thing.md"])
check("and they are C53", sorted({f.code for f in found}), ["C53"])

print("\nBut an anchor only inherits its own half")

alpha_backlog = VAULT / "Alpha" / "Alpha Track" / "Alpha Backlog.md"
alpha_root = aq._anchor_root_for_backlog(alpha_backlog)
check("the anchor root resolves by walking up to the nearest `.anchor`",
      alpha_root, VAULT / "Alpha")
scoped = aq._scope_c53_to_anchor(found, alpha_root)
check("Alpha sees exactly one finding — its own",
      [str(f.surface_file.relative_to(VAULT)) for f in scoped],
      ["Alpha/Thing/Thing.md"])
beta = aq._scope_c53_to_anchor(found, VAULT / "Beta")
check("...and Beta sees the other, so neither half is lost",
      [str(f.surface_file.relative_to(VAULT)) for f in beta],
      ["Beta/Thing/Thing.md"])
# The whole point: a THIRD anchor, uninvolved in the collision, is not blocked by
# it. This is the row's actual complaint — SVP could not reach a groomed frontier
# because of two collisions it had no part in and no power to resolve.
gamma = VAULT / "Gamma"
gamma.mkdir()
(gamma / ".anchor").write_text("", encoding="utf-8")
check("an uninvolved anchor inherits nothing — the F292 complaint",
      aq._scope_c53_to_anchor(found, gamma), [])

print("\nControls — scoping must not become suppression")

check("no --anchor (root None) leaves the vault-wide result untouched",
      len(aq._scope_c53_to_anchor(found, None)), 2)
# An anchor root that is itself the colliding page's folder must keep its finding,
# not fall off the edge of the `in parents` test.
check("an anchor rooted AT the colliding folder still sees it",
      [str(f.surface_file.relative_to(VAULT))
       for f in aq._scope_c53_to_anchor(found, VAULT / "Alpha" / "Thing")],
      ["Alpha/Thing/Thing.md"])
# A backlog outside any anchor has no tree to scope to; returning None must mean
# "do not filter" rather than "filter everything away".
loose = VAULT / "loose"
loose.mkdir()
check("a backlog under no anchor yields no root",
      aq._anchor_root_for_backlog(loose / "X Backlog.md"), None)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
