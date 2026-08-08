#!/usr/bin/env python3
"""test-t154-banner-label-target.py — TINK T154: C54, a Q.md banner whose label
and link target belong to different anchors.

`SEEK` sat in Q.md on 2026-08-05 reporting `Runnable 7` for an anchor that has
never existed. It did not link to nothing — it linked to `[[SONAR queries]]`, a
real file owned by a real anchor. C1 tests link EXISTENCE, so it passed the
block silently, and C22 extends the same existence test rather than adding a
new one. Daybreak's Runnable line and LUMEN T021's starvation rule (which picks
the morning's under-served anchor by reading these counts) both believed it.

The live corpus is clean — 35 blocks, zero violations, verified 2026-08-08 —
which is exactly why this is tested against synthetic banners: a rule that
ships green earns its keep on the next regression, and asserting against live
data would assert nothing.

  A. the SEEK/SONAR shape fires, naming both anchors
  B. a well-formed banner is silent
  C. case drift is NOT a mismatch (T138 — Obsidian and APFS both resolve it)
  D. the ` Triage` and bare-slug fallback targets are handled
  E. an unlinked banner is out of scope, not a violation

Self-contained: loads audit-q.py in-process and calls the checker on strings.
Never reads or writes the real Q.md."""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

AQ = Path(__file__).parent / "audit-q.py"
_loader = importlib.machinery.SourceFileLoader("audit_q_mod", str(AQ))
_spec = importlib.util.spec_from_loader("audit_q_mod", _loader)
aq = importlib.util.module_from_spec(_spec)
sys.modules["audit_q_mod"] = aq
_loader.exec_module(aq)

PASS = 0
FAIL = 0


def ok(m):
    global PASS
    PASS += 1
    print(f"  ok    {m}")


def no(m):
    global FAIL
    FAIL += 1
    print(f"  FAIL  {m}")


def check(*lines):
    return aq.check_c54_banner_label_matches_target("\n".join(lines))


BANNER = "# [U+A]  [[{t}|{l}]]  -  Ready 1    User 0   |   Now 1"

print("A: the live SEEK/SONAR shape")
f = check(BANNER.format(t="SONAR queries", l="SEEK"))
if len(f) == 1:
    ok("one finding for the mismatched block")
else:
    no(f"expected 1 finding, got {len(f)}")
if f and f[0].code == "C54":
    ok("coded C54")
else:
    no("wrong code")
if f and "SEEK" in f[0].message and "SONAR" in f[0].message:
    ok("the message names both the label and the anchor it borrowed from")
else:
    no("the message does not name both anchors")
if f and f[0].severity == "error" and not f[0].mechanically_fixable:
    ok("error severity, not auto-fixable — the repair is a judgement call")
else:
    no("wrong severity or fixability")

print("B: a well-formed banner is silent")
if not check(BANNER.format(t="TINK queries", l="TINK")):
    ok("[[TINK queries|TINK]] passes")
else:
    no("a correct banner was flagged")

print("C: case drift is not a mismatch (T138)")
if not check(BANNER.format(t="Tink queries", l="TINK")):
    ok("[[Tink queries|TINK]] passes — same file, cosmetic drift")
else:
    no("case drift was flagged as an anchor mismatch")

print("D: the other fallback targets the render can land on")
if not check(BANNER.format(t="HA Triage", l="HA")):
    ok("the ` Triage` fallback passes")
else:
    no("[[HA Triage|HA]] was flagged")
if not check(BANNER.format(t="MUX", l="MUX")):
    ok("the bare-slug fallback passes")
else:
    no("[[MUX|MUX]] was flagged")
if check(BANNER.format(t="MUX Triage", l="HA")):
    ok("...and a mismatch still fires through the Triage form")
else:
    no("[[MUX Triage|HA]] slipped through")

print("E: scope")
if not check("# [U+A]  LUMEN  -  Ready 0"):
    ok("an unlinked banner is out of scope")
else:
    no("an unlinked banner was flagged")
if not check("Some prose mentioning [[SONAR queries|SEEK]] mid-paragraph."):
    ok("only H1 banners are inspected, not prose links")
else:
    no("a prose link was flagged")

print("F: multiple blocks are each reported")
f = check(BANNER.format(t="SONAR queries", l="SEEK"),
          BANNER.format(t="TINK queries", l="TINK"),
          BANNER.format(t="ASH queries", l="Warden"))
if len(f) == 2 and [x.surface_line for x in f] == [1, 3]:
    ok("two findings, on the right lines, with the clean block skipped")
else:
    no(f"expected findings on lines [1, 3], got {[x.surface_line for x in f]}")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
