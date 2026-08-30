#!/usr/bin/env python3
"""R-at-entity-11 — the person-page opening. Specimen passes; the old head line warns with each missing piece named; org pages are out of scope."""
import importlib.util, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ap", HERE / "audit-plan.py"); ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)
P = F = 0
def check(c, m):
    global P, F
    if c: P += 1; print("PASS ", m)
    else: F += 1; print("FAIL ", m)
GOOD = """---
description: x
---

:>> [[kmr]] → [[AT]] → [@Ada Lovelace](hook://p/@Ada%20Lovelace) 
# @Ada Lovelace — **[Analyst](https://example.com/) at [[@Babbage & Co]]**

| Card |  |
| --- | --- |
| **Contact** | ada@example.com |
| **Rolodex** | — |

# LOG
"""
OLD = """[[FAANG]]    [Staff Engineer](https://example.com/)  [[@Google]]   #pp

# LOG
"""
with tempfile.TemporaryDirectory() as td:
    root = Path(td); (root / ".anchor").write_text("slug: AT\n")
    g = root / "@Ada Lovelace.md"; g.write_text(GOOD)
    o = root / "@Old Form.md"; o.write_text(OLD)
    (root / "Corp").mkdir(); c = root / "Corp" / "@Acme.md"; c.write_text(OLD)
    s, m = ap.chk_at_entity_person_opening(g, root, []); check(s == "pass", f"specimen passes: {m}")
    s, m = ap.chk_at_entity_person_opening(o, root, []); check(s == "warn" and "breadcrumb" in m and "H1" in m and "#pp" in m, f"old head line warns with the pieces named: {m}")
    s, m = ap.chk_at_entity_person_opening(c, root, []); check(s == "pass" and "org" in m, f"a Corp/ page is out of scope: {m}")
    bad = GOOD.replace("| **Rolodex** | — |\n", ""); g.write_text(bad)
    s, m = ap.chk_at_entity_person_opening(g, root, []); check(s == "warn" and "Rolodex" in m, f"a missing Rolodex row is named: {m}")
print(f"\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
