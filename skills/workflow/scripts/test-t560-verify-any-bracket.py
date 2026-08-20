#!/usr/bin/env python3
"""test-t560-verify-any-bracket.py — TINK T560: an explicit `--verify` is
honoured whatever the bracket.

`_subbullets_to_write` is one dispatch that has now had the same hole found in
it four times. Each field was opened to "write it when the caller explicitly
passed it, regardless of bracket" one at a time:

    Next   T046  (2026-07)   Verify-family rows silently dropped --next
    Verify T123  (2026-08-08) opened for TERMINAL rows only
    User   T236  (2026-08-17) SONAR T031, a [Waiting] row with a user action
    Probe  F305             written this way from the start

Verify kept a bracket test — `_verify_family(status) or _terminal_bracket(
status)` — and [[SCOUT]] hit the remaining hole 2026-08-19 on a
`[Waiting 2026-09-20]` row: neither verify-family nor terminal, so no arm
matched, the CLI printed `updated`, and T050's landing check reverted the file
with "the edit reported success but the file does not reflect it". That message
reads like a writer bug and is really this dispatch declining to write.

**A parked soak row is exactly where a Verify question legitimately sits before
its date arrives**, which is why the bracket was never the right thing to test.

The assertions below deliberately cover the whole bracket space rather than
just Scout's [Waiting], because the defect's history is that fixing one bracket
at a time is how it survived four rounds. §4 pins the T056 no-op guarantee that
makes "write it whenever passed" safe, and §5 pins that the F240 `why-user`
trailer folded into `eff_verify` is not dropped — a latent second bug in T123's
block, which wrote the raw text.

Run: python3 test-t560-verify-any-bracket.py
"""
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

BE = Path(__file__).parent / "backlog-edit.py"
_loader = importlib.machinery.SourceFileLoader("be_mod", str(BE))
_spec = importlib.util.spec_from_loader("be_mod", _loader)
be = importlib.util.module_from_spec(_spec)
sys.modules["be_mod"] = be
_loader.exec_module(be)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def written(status, **kw):
    """The (label, text) pairs `_subbullets_to_write` emits, as a dict."""
    args = dict(eff_verify=None, eff_next=None, eff_user=None, next_text=None,
                verify_text=None, probe_text=None, eff_probe=None,
                user_text=None, why_user_action=None)
    args.update(kw)
    out = be._subbullets_to_write(status, args.pop("eff_verify"),
                                  args.pop("eff_next"), args.pop("eff_user"),
                                  args.pop("next_text"), **args)
    return {lbl: txt for lbl, txt in out}


Q = "Does it still feel better than an ordinary tee? yes = worth it"

print("1. Scout's case — a parked soak row takes an explicit --verify")
for bracket in ("Waiting 2026-09-20", "Waiting", "Blocked", "Blocked T012",
                "Questions", "2 Questions", "Designing"):
    check(f"[{bracket}]",
          written(bracket, verify_text=Q, eff_verify=Q).get("Verify"), Q)

print("2. The brackets that already worked still do")
check("[Verify] (the family arm)",
      written("Verify", verify_text=Q, eff_verify=Q).get("Verify"), Q)
check("[Verify-by 2026-09-01] (the family arm)",
      written("Verify-by 2026-09-01", verify_text=Q, eff_verify=Q).get("Verify"), Q)
check("[Watching 7d] (the family arm)",
      written("Watching 7d", verify_text=Q, eff_verify=Q).get("Verify"), Q)
check("[Done] (T123's terminal case)",
      written("Done", verify_text=Q, eff_verify=Q).get("Verify"), Q)

print("3. A [Ready] row keeps its Next and takes the Verify too")
out = written("Ready", verify_text=Q, eff_verify=Q, eff_next="run it",
              next_text="run it")
check("Next still written", out.get("Next"), "run it")
check("Verify written alongside", out.get("Verify"), Q)

print("4. T056 — an ordinary re-touch does NOT rewrite (and reorder) it")
# eff_verify carries the EXISTING text; verify_text is None because no --verify
# was passed. Writing here would re-insert the sub-bullet directly under the row
# line on every unrelated edit.
check("[Waiting] re-touch emits no Verify",
      "Verify" in written("Waiting 2026-09-20", eff_verify=Q), False)
check("[Done] re-touch emits no Verify",
      "Verify" in written("Done", eff_verify=Q), False)
check("[Ready] re-touch emits no Verify",
      "Verify" in written("Ready", eff_verify=Q, eff_next="x"), False)
# ...and a bracket that REQUIRES one still writes from eff_verify on a re-touch,
# because that is the family arm's job and T123 pinned it.
check("[Verify] re-touch still writes from eff_verify",
      written("Verify", eff_verify=Q).get("Verify"), Q)

print("5. It writes eff_verify, so the F240 why-user trailer survives")
ANNOTATED = Q + " · *why-user: taste — his own reading of his own queue*"
check("[Waiting] writes the annotated form, not the raw text",
      written("Waiting 2026-09-20", verify_text=Q,
              eff_verify=ANNOTATED).get("Verify"), ANNOTATED)

print("6. Removal and non-invention are unchanged")
check("--verify '' removes on any bracket",
      written("Waiting", verify_text="", eff_verify="").get("Verify", "MISSING"),
      None)
check("no --verify invents nothing on [Done]",
      "Verify" in written("Done"), False)
check("no --verify invents nothing on [Waiting]",
      "Verify" in written("Waiting"), False)

print()
if FAILURES:
    print(f"test-t560-verify-any-bracket: {len(FAILURES)} FAILED — {FAILURES}")
    sys.exit(1)
print("test-t560-verify-any-bracket: all checks pass")
