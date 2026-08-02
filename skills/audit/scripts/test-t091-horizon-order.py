#!/usr/bin/env python3
"""T091 — the renderer orders by horizon PRIORITY, not by file position.

`queries-render` built its Questions and Ready lists in raw file order, so a
`## Later` row rendered above a `## Next` row whenever a backlog's horizon H2s sat
out of order. Split off from T076, which fixed the one file that was actually
scrambled — and that is exactly why this stayed latent: the corpus measurement
behind that close (33 of 34 backlogs carry `Now → Next → Later` contiguous and
correctly ordered) means the renderer is right almost everywhere by luck, not by
construction. Repairing the data did not teach the renderer what the priority is.

    python3 test-t091-horizon-order.py
"""
import importlib.util
import sys
from pathlib import Path

_D = Path(__file__).parent.resolve()


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, _D / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


aq = _load("audit_q", "audit-q.py")
qr = _load("queries_render", "queries-render.py")

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


class Row:
    """Only the two fields the ordering reads."""

    def __init__(self, ident, horizon):
        self.identifier, self.horizon = ident, horizon

    def __repr__(self):
        return f"{self.identifier}@{self.horizon}"


print("The priority is named once, and both modules read the same one")

check("audit-q owns the canonical order",
      aq.HORIZON_ORDER,
      ("Active", "Ready", "Now", "Next", "Legwork", "Later", "Verify", "Icebox"))
check("queries-render reads it rather than re-spelling it",
      qr.HORIZON_RANK, aq.HORIZON_RANK)
# Every live horizon must have a rank, or it silently sorts to the end.
check("every LIVE horizon has a rank",
      sorted(h for h in aq.LIVE_HORIZON_H2S if h not in aq.HORIZON_RANK), [])

print("\nOrdering")

# The row's own example: a backlog whose H2s sit Later-before-Next.
scrambled = [Row("A", "Later"), Row("B", "Next"), Row("C", "Now")]
check("a `## Later` row no longer renders above `## Next`",
      [r.identifier for r in qr._by_horizon(scrambled)], ["C", "B", "A"])
check("a correctly-ordered file is left exactly as it was",
      [r.identifier for r in qr._by_horizon(
          [Row("C", "Now"), Row("B", "Next"), Row("A", "Later")])],
      ["C", "B", "A"])

# Stability is the load-bearing half: between-horizon order is imposed, but the
# author's deliberate sequence WITHIN a horizon must survive untouched.
within = [Row("n3", "Next"), Row("n1", "Next"), Row("n2", "Next")]
check("order within one horizon is preserved — the sort is stable",
      [r.identifier for r in qr._by_horizon(within)], ["n3", "n1", "n2"])
mixed = [Row("L1", "Later"), Row("N1", "Next"), Row("L2", "Later"), Row("N2", "Next")]
check("...including when two horizons interleave in the file",
      [r.identifier for r in qr._by_horizon(mixed)], ["N1", "N2", "L1", "L2"])

print("\nAn unrecognised horizon must not crash a live queue")

check("an unknown H2 sorts last instead of raising",
      [r.identifier for r in qr._by_horizon(
          [Row("X", "Someday"), Row("A", "Active")])], ["A", "X"])
check("...and several unknowns keep their relative order",
      [r.identifier for r in qr._by_horizon(
          [Row("X", "Someday"), Row("Y", "Maybe"), Row("R", "Ready")])],
      ["R", "X", "Y"])
check("an empty list is fine", qr._by_horizon([]), [])

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
