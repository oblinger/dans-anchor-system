#!/usr/bin/env python3
"""test-module-doc-c4.py — C4 (breadcrumb) must be masthead-aware.

A page uses ONE navigation form: a masthead when it is the container's own page,
a `:>>` breadcrumb everywhere else (R-spine-01, R-doc-structure-02). C4 used to
fire on every masthead module doc and suggest adding the breadcrumb — which the
on-write Warden then rejected under those same two rules. The finding could not
be satisfied in either direction, so the only correct response was to ignore a
checker. Reported from the HookAnchor side 2026-08-10 after acting on C4's advice
in `HA Commands.md` and being bounced by the write hook.

Both directions are pinned here, because the tempting fix — deleting C4 — would
also pass the masthead half. C4 still has a job on breadcrumb-form docs.

Usage: python3 test-module-doc-c4.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PASS = FAIL = 0


def _load():
    spec = importlib.util.spec_from_file_location("amd", HERE / "audit-module-doc.py")
    m = importlib.util.module_from_spec(spec)
    # Registered BEFORE exec: @dataclass resolves annotations via
    # sys.modules[cls.__module__], which is None for an unregistered module.
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def check(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"PASS  {label}")
    else:
        FAIL += 1
        print(f"FAIL  {label}")


BREADCRUMB_FORM = """---
description: x
---
# Foo Bar
Some overview prose here.
"""

# A dispatch masthead: the identity row is `| -[[Name]]- |`, then the separator
# row, then the electric zone. This is the shape `Spine.table_start` matches.
MASTHEAD_FORM = """---
description: x
---

| -[[Foo Bar]]- | : a module doc |
| --- | --- |
| ... | |

# Foo Bar
Some overview prose here.
"""


def c4s(m, body, name="Foo Bar.md"):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / name
        p.write_text(body, encoding="utf-8")
        findings, _ = m.audit_file(p)
        return [f for f in findings if f.rule == "C4"]


def main():
    m = _load()

    check(len(c4s(m, BREADCRUMB_FORM)) == 1,
          "breadcrumb-form doc with no `:>>` → C4 still fires")

    check(len(c4s(m, BREADCRUMB_FORM.replace(
        "# Foo Bar", ":>> [[A]] → [[B]]\n# Foo Bar"))) == 0,
        "breadcrumb-form doc WITH a `:>>` → no C4")

    check(len(c4s(m, MASTHEAD_FORM)) == 0,
          "masthead doc → C4 suppressed (the unsatisfiable finding)")

    print("-" * 40)
    print(f"C4 masthead-awareness test: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
