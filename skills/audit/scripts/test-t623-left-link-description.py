#!/usr/bin/env python3
"""test-t623-left-link-description.py — TINK T623 (Dan, 2026-08-29).

A masthead row whose LEFT cell is a wiki-link is a child pulled above the
separator by hand; its right cell is that child's description and may be a
sentence. R-dispatch-table-06's two-word cap applies to LABEL rows only."""
import sys as _sys; _sys.dont_write_bytecode = True
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py")
ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)

TEXT = """---
description: x
---

| -[[Disk]]- | : Catalog of drives.<br>→ [[kmr]] → [Disk](hook://p/Disk)  |
| --- | --- |
| Related | [[Disks]] and a long explanation of what that page is about |
| **Registers** | *entity-keyed: you arrive knowing an identity and look it up* |
| **Umbrellas** | *routers over many sub-anchors* — and prose outside the italics |
|  | *an italic gloss with no label at all is not a group label* |
| **DISKS** |  |
| [[Disk 10T\\|10T]]  | 10 TB Seagate NAS HDD, APFS, encrypted — the master of everything since June |
| [[Disk BLACK\\|BLACK]]  | 5 TB USB drive, the former snapshot master, now offsite |
| --- | |
| [[Disk 8T\\|8T]]  | the machine wrote this sentence below the marker |

# Disk
"""
off = ap.masthead_narrative_offenders(TEXT, "Disk")
labels = [l for l, _ in off]
ok = 0; bad = 0
def check(cond, msg):
    global ok, bad
    if cond: ok += 1; print("  PASS:", msg)
    else: bad += 1; print("  FAIL:", msg, "->", labels)
check("Related" in labels, "a label row with prose in the right cell is still an offender")
check("**Registers**" not in labels, "Q4: a described group label — label left, ALL-italic gloss right — is exempt")
check("**Umbrellas**" in labels, "Q4: prose outside the italics is still narrative")
check(any(l == "" for l in labels), "Q4: an italic gloss with an empty left cell is not a group label")
check(not any("10T" in l or "BLACK" in l for l in labels), "rows whose left cell is a wiki-link are exempt, sentence and all")
check(len(off) == 3, "exactly the three offending rows fire (Related, Umbrellas, the unlabeled gloss)")
print(f"\n{ok} passed, {bad} failed"); _sys.exit(1 if bad else 0)
