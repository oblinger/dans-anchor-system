#!/usr/bin/env python3
"""F283 stage 1 — `[Blocked]` is a typed edge, not a mood.

Dan's structural claim, 2026-07-29: you can only be blocked ON something. Bare
`[Blocked]` is what let four Dan-gated rows record their real blocker in prose,
where nothing could read it, and drop out of every surface. So the bracket must
name a row handle, and the two cases that are not really blocking get their own
brackets — `[Questions]` (waiting on an answer) and `[Waiting]` (waiting on time
or an external state, condition named in the body).

Enforced at the `state` write rather than audited after, per the standing
preference for a structural gate over one more rule to remember.

Run: python3 test-f283-blocked-grammar.py
"""
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "be", Path(__file__).resolve().parent / "backlog-edit.py")
be = importlib.util.module_from_spec(_spec)
sys.modules["be"] = be
_spec.loader.exec_module(be)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n         got  {got!r}\n         want {want!r}")
        FAILURES.append(name)


def gate_refuses(status):
    """True when blocked_grammar_gate rejects this bracket."""
    try:
        be.blocked_grammar_gate(status, "T001")
        return False
    except be.BacklogEditError:
        return True


def validator_accepts(status):
    return (status in be.VALID_STATUS_BASE
            or any(p.match(status) for p in be.VALID_STATUS_PATTERNS))


def main():
    # --- the gate: bare [Blocked] is the whole point --------------------
    check("bare [Blocked] is refused", gate_refuses("Blocked"), True)
    check("[Blocked] with whitespace is still bare", gate_refuses("  Blocked  "), True)

    # --- a named handle passes, and a handle is ANY row id --------------
    # "a Verify can gate other work, so it can be a blocker" — so the handle
    # is not restricted to F-numbers.
    for handle in ("Blocked F288", "Blocked T048", "Blocked B-QFix",
                   "Blocked DMUX-F034", "Blocked R-Scaffolding.5.2"):
        check(f"{handle!r} passes the gate", gate_refuses(handle), False)
        check(f"{handle!r} passes the validator", validator_accepts(handle), True)

    # --- the two non-blocking cases are untouched ----------------------
    for status in ("Questions", "Waiting", "Ready", "Verify", "Done", "User"):
        check(f"[{status}] is not the gate's business", gate_refuses(status), False)

    # --- bare Blocked still PARSES, so existing rows can be re-bracketed -
    # 33 bare [Blocked] rows existed vault-wide when this landed (2026-07-30).
    # The validator has to read them; the gate is what refuses writing one.
    check("validator still parses bare 'Blocked' (for reading old rows)",
          validator_accepts("Blocked"), True)

    # --- the refusal has to be actionable ------------------------------
    try:
        be.blocked_grammar_gate("Blocked", "T001")
        msg = ""
    except be.BacklogEditError as exc:
        msg = str(exc)
    check("refusal names the row", "T001" in msg, True)
    for alt in ("Blocked <handle>", "Questions", "Waiting"):
        check(f"refusal offers {alt!r}", alt in msg, True)
    check("refusal does not offer a form the validator rejects",
          "Waiting <condition>" in msg, False)

    print()
    if FAILURES:
        print(f"FAILED {len(FAILURES)}: {', '.join(FAILURES)}")
        return 1
    print("all F283 stage-1 assertions pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
