#!/usr/bin/env python3
"""test-t038-q-separator.py — redefining a Q must not eat the blank separator.

`_find_q_bullet` returns an end index pointing at the NEXT Q-header bullet, so
the replaced span includes the blank line between the two Qs. The rewrite path
substitutes a bullet with no trailing blank, which used to delete that separator
and trip audit-q C20 on every redefine of a non-terminal Q (T038, seen on MUX
F173 Q10). The Open-Questions region is Edit-hook-blocked, so the only recovery
was a raw perl insert — hence a regression test rather than a one-time fix.

    python3 test-t038-q-separator.py
"""
import importlib.util
import pathlib

SCRIPT = pathlib.Path(__file__).parent / "backlog-edit.py"
_spec = importlib.util.spec_from_file_location("backlog_edit", SCRIPT)
be = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(be)

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f"  (got {got!r}, want {want!r})"))


def q(n, text):
    return [f"- **Q{n}** — {text}", "  - **(A)** one", "  - **(B)** two",
            "  - **Recommendation:** None"]


def build(n_qs):
    lines = ["# F001 — Fixture", "", "## Open Questions", ""]
    for i in range(1, n_qs + 1):
        lines += q(i, f"question {i}") + [""]
    return lines


def separators(lines, q_num):
    """Blank lines immediately preceding the Q<q_num> header bullet."""
    for i, line in enumerate(lines):
        if line.startswith(f"- **Q{q_num}**"):
            n = 0
            while i - n - 1 >= 0 and not lines[i - n - 1].strip():
                n += 1
            return n
    return -1


def rewrite(lines, q_num, new_text):
    """Drive the real locator + the real splice the `rewrite` verb uses."""
    start, end, _ = be._find_q_bullet(lines, q_num)
    return be.replace_q_bullet(lines, start, end, q(q_num, new_text))


print("T038 — blank separator survives a redefine")

lines = build(3)
check("fixture starts with one separator before Q2", separators(lines, 2), 1)
check("fixture starts with one separator before Q3", separators(lines, 3), 1)

out = rewrite(lines, 2, "rewritten body")
check("separator before Q3 survives rewriting Q2", separators(out, 3), 1)
check("separator before Q2 untouched", separators(out, 2), 1)
check("Q2 body actually changed",
      any("rewritten body" in line for line in out), True)
check("no Q was lost", sum(1 for line in out if line.startswith("- **Q")), 3)

out2 = rewrite(out, 2, "rewritten twice")
check("idempotent — separator stable across repeat rewrites",
      separators(out2, 3), 1)

print("terminal Q — nothing following to separate from")
lines = build(1)
out = rewrite(lines, 1, "only question")
check("terminal Q rewrite keeps the trailing blank", out[-1], "")
check("terminal Q still present",
      sum(1 for line in out if line.startswith("- **Q")), 1)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
