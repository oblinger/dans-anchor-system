#!/usr/bin/env python3
"""Unit tests for the >4 GB descriptor-wrap rule.

A fixture cannot carry a 4 GB entry, so this tests the predicate directly --
including the two REAL values from the 2019 Drive archive, which is the whole
reason the rule exists.
"""
import importlib.machinery
import pathlib
import sys

src = pathlib.Path(__file__).with_name("salvage_zip.py").read_text().split("def main()")[0]
ns = {}
exec(compile(src, "salvage_zip.py", "exec"), ns)
size_matches = ns["size_matches"]

CASES = [
    # (recorded, measured, expected, why)
    (1251485198, 5546452494, True,
     "REAL: 8.17.2018_ProductDemo.mov -- true length minus exactly 2**32"),
    (677575757, 4972543053, True,
     "REAL: 2015-12-12.backup.gz -- true length minus exactly 2**32"),
    (500, 500, True, "ordinary exact match"),
    (499, 500, False, "off by one under 4 GB must NOT be accepted"),
    (123, 999, False, "unrelated values under 4 GB"),
    (0, 1 << 32, True, "exactly 4 GiB wraps to a recorded 0 -- a real wrap"),
    (1, (1 << 32) + 1, True, "smallest wrap above the boundary"),
    (5, 4294967301, True, "wrap with a small remainder"),
    (1251485198, 1251485198 + 2 * (1 << 32), True, "two full wraps"),
    (0, 0, True, "genuinely empty entry"),
    (0, 500, False, "empty descriptor against a non-empty measurement"),
    (4294967295, (1 << 32) - 1, True, "largest value that needs no wrap"),
]

fails = []
for recorded, measured, expected, why in CASES:
    got = size_matches(recorded, measured)
    ok = got == expected
    print(("  ok    " if ok else "  FAIL  ") + f"{recorded} vs {measured} -> {got}   {why}")
    if not ok:
        fails.append(why)

print(f"\n  {len(CASES) - len(fails)}/{len(CASES)} passed" if not fails
      else f"\n  FAILED: {fails}")
sys.exit(1 if fails else 0)
