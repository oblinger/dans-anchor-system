#!/usr/bin/env python3
"""T143 — the landing check compared a raw request against a normalized row.

`verify_write_landed` re-reads the file after a write and asserts the asked-for
text is present. It tested `str(want).strip() not in got` — a raw substring
compare — while `render_row` normalizes the body on the way in with
`_strip_trailing_anchors`. So a body ending in `^T+` was written correctly,
looked absent to the verifier, and the whole edit was **reverted**.

The irony is the point: that strip is T140's fix, and this fires on exactly the
input T140 exists to clean. The two shipped a day apart, so `state define …
--from-file` on a body still carrying the mint placeholder became a hard revert
reporting "the edit reported success but the file does not reflect it" — a
message that sends you off rewording a body that was never the problem.

A second trigger shares the root cause and is NOT a false alarm: a body holding
a blank line renders its tail below the bullet, outside the row grammar. That
one must still fail — a row is one line — but the old message named the wrong
thing, so it is now diagnosed rather than merely refused.

    python3 test-t143-landing-check-normalization.py
"""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

_HERE = Path(__file__).parent


def _load(name, filename):
    loader = importlib.machinery.SourceFileLoader(name, str(_HERE / filename))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


be = _load("be", "backlog-edit.py")

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"\n          got  {got!r}\n          want {want!r}"))


def landing(row_body, requested_body, row_id="T007", status="Ready",
            title="Title"):
    """Write one row, then ask `verify_write_landed` whether it landed."""
    lines = be.render_row(row_id, status, title, row_body).split("\n")
    return be.verify_write_landed(
        lines, row_id, {"status": status, "body": requested_body})


# ------------------------------------------------- the false failure itself

print("a trailing anchor in the request is not a failed write")

# The exact MUSE T007 shape: a body piped in still carrying `^T+`.
check("a body ending in the mint placeholder lands",
      landing("Some finding text. ^T+", "Some finding text. ^T+"), [])
check("...and so does one ending in a real anchor",
      landing("Some finding text. ^T007", "Some finding text. ^T007"), [])
check("...and a whole run of them",
      landing("Some finding text. ^T+ ^T007", "Some finding text. ^T+ ^T007"),
      [])
# The control: identical body, no anchor. This passed before the fix too — it
# is here so a regression that breaks the ordinary path is visible as such.
check("a plain body still lands", landing("Some finding text.",
                                          "Some finding text."), [])


print("\nthe check still catches a write that genuinely did not land")

# Narrowing the comparison must not blind it. The row says one thing, the
# caller asked for another — the failure `verify_write_landed` exists for.
fails = landing("What the row actually says.", "What the caller asked for.")
check("a body that really is absent still fails", len(fails), 1)
check("...with the original message", "absent from the row line" in fails[0],
      True)
# A trailing anchor must not become a wildcard: stripping it off the request
# cannot make an otherwise-wrong body match.
fails = landing("What the row actually says.", "Something else entirely. ^T+")
check("stripping the anchor does not excuse a wrong body", len(fails), 1)


print("\na multi-line body is refused — and now says why")

fails = landing("First para.\n\nSecond para.", "First para.\n\nSecond para.")
check("a body with a blank line still fails", len(fails), 1)
check("...naming the one-line row as the cause",
      "multi-line text cannot live on a row line" in fails[0], True)
check("...and pointing at the two ways out",
      "Next:" in fails[0] and "one paragraph" in fails[0], True)
check("...rather than the old misleading message",
      "absent from the row line" in fails[0], False)


print("\nthe writer and the verifier agree — which is the point of T143")

# Stated as an assertion rather than left implicit: whatever `render_row` does
# to a body, the verifier must accept the result. If a future normalization is
# added to the writer without teaching the check about it, this fails HERE
# rather than as a silent revert on someone's next `state define`.
for body in ("plain", "plain ^T+", "plain ^T007", "plain ^T+ ^T002 ^T002",
             "trailing spaces   ", "  leading spaces"):
    rendered = be.render_row("T007", "Ready", "Title", body)
    check(f"round trip: {body!r}",
          be.verify_write_landed(rendered.split("\n"), "T007",
                                 {"status": "Ready", "body": body}), [])


print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
