#!/usr/bin/env python3
"""F305 — `[Waiting]` and `[Watching]` must say WHEN to look again.

Two refusals with different reasons, and one narrowing that measurement forced.

BARE is refused because it records that a row is deferred and nothing about
when the deferral ends, so no surface can tell a row whose moment has come from
one that is simply forgotten. RELATIVE (`Waiting 7d`) is refused for a sharper
reason: it ages into a lie. `[Watching 7d]` written a month ago still reads
*7d*, because the bracket shows the duration it was SET with while every reader
takes it for the time REMAINING.

THE NARROWING IS THE PART WORTH TESTING. Dan promoted refuse-at-write from the
last step to the first (2026-08-13) precisely so a refusal that blocks real work
would surface early. It did, on the first live probe: written strict — matching
its sibling `blocked_grammar_gate` — the gate refused a plain `--next` edit on
`TINK F288`, because `status == "same"` is resolved to the row's EXISTING
bracket before any gate runs. All 23 vault rows carrying the bare or relative
shape would have become unwritable for ANY edit. The gate now fires only on a
bracket the caller actually asked for, so a NEW bare bracket is impossible while
an existing one stays editable until something deliberately re-brackets it.

Run: python3 test-f305-watch-grammar.py
"""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name that has been seen serving code no longer on
# disk — a green run vouching for a source it had not read.
import sys as _sys; _sys.dont_write_bytecode = True

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("be", HERE / "backlog-edit.py")
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


def refuses(status):
    try:
        be.watch_grammar_gate(status, "T001")
        return False
    except be.BacklogEditError:
        return True


def main():
    print("A bare deferral is refused — it names no moment to come back")
    check("[Waiting]", refuses("Waiting"), True)
    check("[Watching]", refuses("Watching"), True)
    check("lowercase [waiting]", refuses("waiting"), True)
    check("whitespace does not disguise it", refuses("  Waiting  "), True)
    check("bracketed form", refuses("[Waiting]"), True)

    print("\nA relative duration is refused — it ages into a lie")
    for s in ("Waiting 7d", "Watching 14d", "Waiting 3m", "Watching 12h", "Waiting 1y"):
        check(f"[{s}]", refuses(s), True)

    print("\nAn absolute date is the accepted form")
    check("[Waiting 2026-09-01]", refuses("Waiting 2026-09-01"), False)
    check("[Watching 2026-12-25]", refuses("Watching 2026-12-25"), False)
    # A date in the past is ACCEPTED on purpose: it is not wrong, it is due.
    # That is the whole advantage over a duration, which cannot express "due".
    check("a past date is due, not invalid", refuses("Watching 2020-01-01"), False)

    print("\nEvery other bracket is untouched by this gate")
    for s in ("Ready", "Active", "Questions", "Designing", "Verify",
              "Verify-by 2026-09-01", "Blocked F142", "User", "Done 2026-08-13",
              "3 Questions", "same", "delete"):
        check(f"[{s}] passes", refuses(s), False)

    print("\nThe bracket is a SET, so a member is judged as a member")
    check("[Ready, Waiting] is refused on the Waiting", refuses("Ready, Waiting"), True)
    check("[Ready, Waiting 2026-09-01] passes", refuses("Ready, Waiting 2026-09-01"), False)
    check("[Verify, Watching 14d] is refused on the relative form",
          refuses("Verify, Watching 14d"), True)

    print("\nThe refusal tells the author what to write instead")
    try:
        be.watch_grammar_gate("Waiting", "T001")
        msg = ""
    except be.BacklogEditError as e:
        msg = str(e)
    check("names the row", "T001" in msg, True)
    check("gives the replacement form", 'Waiting YYYY-MM-DD' in msg, True)
    check("offers [Questions] when the wait is really on Dan", "[Questions]" in msg, True)
    check("offers [Blocked <handle>] when it waits on a row", "Blocked <handle>" in msg, True)
    try:
        be.watch_grammar_gate("Watching 7d", "T001")
        msg2 = ""
    except be.BacklogEditError as e:
        msg2 = str(e)
    check("the relative refusal explains the AGEING, not just the shape",
          "REMAINING" in msg2, True)

    # ---------------------------------------------------------------- the narrowing
    # End-to-end through `state`, because the defect this pins lives in the
    # CALLER, not in the gate: `status == "same"` is resolved to the existing
    # bracket before the gate is reached. A unit test on the gate alone cannot
    # see it — and did not, which is why the live probe found it instead.
    print("\nThe narrowing — an existing bare bracket stays editable")
    # F269's `ANCHOR_VAULT_ROOT` points the whole toolchain at a fixture vault,
    # which is what makes this reachable end-to-end without writing into the
    # real one. The backlog is named for the SLUG (`PROBE Backlog.md`), because
    # that is what the locator searches for.
    tmp = Path(tempfile.mkdtemp())
    anchor = tmp / "Probe"
    (anchor / "PROBE Track").mkdir(parents=True)
    (anchor / ".anchor").write_text("slug: PROBE\n", encoding="utf-8")
    (anchor / "Probe.md").write_text("# Probe\nA fixture.\n", encoding="utf-8")
    backlog = anchor / "PROBE Track" / "PROBE Backlog.md"
    backlog.write_text(
        "---\ndescription: probe backlog\n---\n\n# PROBE Backlog\nA fixture.\n\n"
        "## Now\n\n"
        "- **T001 — a row written before the gate existed** [Waiting] — body. ^T001\n\n"
        "## Next\n\n## Later\n\n## Icebox\n\n", encoding="utf-8")

    env = dict(os.environ, ANCHOR_VAULT_ROOT=str(tmp))

    def run(*args):
        r = subprocess.run([sys.executable, str(HERE / "state"), *args],
                           capture_output=True, text=True, cwd=str(anchor), env=env)
        return r.returncode, (r.stdout + r.stderr)

    rc, out = run("set", "PROBE", "Backlog", "T001",
                  "--next", "an edit that has nothing to do with the bracket")
    check("a --next edit on a bare [Waiting] row SUCCEEDS", rc == 0, True)
    check("and the bare bracket is left exactly as it was",
          "[Waiting]" in backlog.read_text(encoding="utf-8"), True)

    rc, out = run("set", "PROBE", "Backlog", "T001", "--status", "Waiting")
    check("but writing a NEW bare [Waiting] is refused", rc != 0, True)
    check("the refusal is this gate's, not some other gate's",
          "must say WHEN to look again" in out, True)

    rc, out = run("set", "PROBE", "Backlog", "T001", "--status", "Waiting 2026-09-15")
    check("and the dated form writes cleanly", rc == 0, True)
    check("the row now carries the date",
          "[Waiting 2026-09-15]" in backlog.read_text(encoding="utf-8"), True)

    # RED CHECK — without this the narrowing could silently become "the gate
    # never fires" and every assertion above about acceptance would still pass.
    print("\nRed check — the gate is genuinely reachable through `state`")
    rc, out = run("set", "PROBE", "Backlog", "T001", "--status", "Watching 7d")
    check("a relative form written through `state` is refused end-to-end",
          rc != 0 and "ages into a lie" in out, True)

    print(f"\nF305 watch grammar: {len(FAILURES)} failure(s)")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
