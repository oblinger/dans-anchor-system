#!/usr/bin/env python3
"""test-rec-blank-separator.py — a `- **Recommendation:**` bullet keeps its
trailing blank line through a Backlog `define`.

Why this exists. audit-q C20 requires a blank line after every Recommendation,
separating one Q group from the next content. C20 is skipped while
`recommendation_line == 0`, so it only becomes *reachable* once C9 is satisfied
and a Recommendation bullet exists — and at that moment `state define` used to
strip the blank right back out (`sub_lines = [l for l in body_lines[1:] if
l.strip()]`). Net effect: fixing C8/C9 on a row-hosted question converted one
finding into another and C20 could never be cleared, on any anchor. Found on MUX
2026-08-02 with 6 such questions; see MUX T042.

Covers the shape that actually occurs: a Recommendation at the END of a body,
where the blank never even reached that comprehension because `raw.rstrip("\\n")`
upstream ate it first. A Q group almost always ends its row, and all six MUX
questions were this shape.

NOT asserted here: the mid-body shape (more sub-bullets after the
Recommendation). It works in production — MUX F216 item (3) carries exactly that
layout and audit-q reports 0 — but it cannot be checked in this harness, because
the harness stubs `_selffire`, and `perform_edit` writes a blank sub-bullet as
`"  "` (`backlog-edit.py:1858` prepends two spaces to any line not already
indented). The real write hook normalizes that to an empty line; a stubbed one
does not, so a synthetic assertion here would be testing the stub. Left to the
live row rather than faked.

Also asserts the blank is not handed out indiscriminately: a blank after an
ordinary sub-bullet is still dropped, so this stays a narrow carve-out rather
than a general "preserve blank lines" change.

Safe by construction: a row's extent is delimited by the next row start or the
next H2 (`backlog-edit.py` scan_backlog / boundary_lines), never by a blank
line, so a blank inside a body cannot split the row.

Self-contained: drives the real `state` binary against a scratch vault.
"""
# T170: several of these scripts are extensionless, so the import machinery
# caches them under a mangled name (`stonecpython-312.pyc`) that was seen
# serving code no longer on disk — a green run vouching for a source it had
# not read. Must precede every load in this file, hence the top.
import sys as _sys; _sys.dont_write_bytecode = True

import contextlib
import importlib.machinery
import importlib.util
import io
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


st = _load("state_mod", HERE / "state")
st.be._selffire = lambda *_a, **_k: None

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}")
        if detail:
            print("\n".join("        " + l for l in detail.splitlines()[:12]))


BACKLOG_SEED = """---
description: scratch
---

# TST Backlog

## Now

## Next

## Later

## Verify

## Done
"""


class R:
    def __init__(self, rc, out):
        self.returncode, self.stdout, self.stderr = rc, out, out


def define(anchor_dir, label, body):
    f = anchor_dir / f"_body_{label}.md"
    f.write_text(body)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = st.main(["state", "define", "TST", "Backlog", label,
                          "--from-file", str(f)])
        return R(rc or 0, buf.getvalue())
    except SystemExit as e:
        return R(e.code or 0, buf.getvalue())
    except Exception as e:  # noqa: BLE001 — surface the message in the report
        return R(1, buf.getvalue() + f"\n{type(e).__name__}: {e}")


def text(anchor_dir):
    """Whole backlog with trailing spaces stripped per line, so assertions can
    talk about `\n\n` without tripping over the writer's padding."""
    raw = (anchor_dir / "TST Backlog.md").read_text()
    return "\n".join(l.rstrip() for l in raw.split("\n"))


def main():
    with tempfile.TemporaryDirectory() as td:
        vault = Path(td)
        st.be.VAULT_ROOT = vault
        anchor = vault / "TST"
        anchor.mkdir()
        (anchor / ".anchor").write_text("slug: TST\n")
        (anchor / "TST Backlog.md").write_text(BACKLOG_SEED)

        # --- shape 2: Recommendation ENDS the body (the common case) -------
        r = define(anchor, "T1", (
            "- **T1 — trailing recommendation** [Questions] — body text.\n"
            "  - **Q1 — a question?** ^T1-Q1\n"
            "    - **(A)** first option.\n"
            "    - **(B)** second option.\n"
            "    - **Recommendation:** None — no lean.\n"
        ))
        ok = r.returncode == 0
        check("define with a trailing Recommendation succeeds", ok,
              (r.stdout or "") + (r.stderr or ""))
        if ok:
            t = text(anchor)
            check("trailing Recommendation is followed by a blank line",
                  "- **Recommendation:** None — no lean.\n\n" in t,
                  t)

        # --- a mid-body Recommendation must not lose the content after it ---
        r = define(anchor, "T2", (
            "- **T2 — mid-body recommendation** [Questions] — body text.\n"
            "  - **Q1 — a question?** ^T2-Q1\n"
            "    - **(A)** first option.\n"
            "    - **Recommendation:** Lean (A) — because.\n"
            "  - **(2) a later item that must survive.**\n"
        ))
        ok = r.returncode == 0
        check("define with a mid-body Recommendation succeeds", ok,
              (r.stdout or "") + (r.stderr or ""))
        if ok:
            t = text(anchor)
            check("content after a mid-body Recommendation survives",
                  "a later item that must survive" in t, t)

        # --- T137: the separator follows the last CONTINUATION -------------
        # C20 wants the blank before the next non-continuation content. When a Q
        # ends in F270's `- **Damage:**` or F275 M3's `- **On answer:**` — both
        # minted after the C20 rule — the blank has to land after THOSE, not
        # after the Recommendation line. It did not, so every inline row-Q of
        # that shape carried an unfixable C20: the caller could supply the blank
        # and `raw.rstrip("\n")` ate it.
        r = define(anchor, "T4", (
            "- **T4 — a Q ending in On-answer** [Questions] — body text.\n"
            "  - **Q1 — a question?** ^T4-Q1\n"
            "    - **(A)** first option.\n"
            "    - **(B)** second option.\n"
            "  - **Recommendation:** Lean (A) — because.\n"
            "  - **Damage:** locking — callers hard-code it.\n"
            "  - **On answer:** (A) → do the thing.\n"
        ))
        ok = r.returncode == 0
        check("define with a Q ending in On-answer succeeds", ok,
              (r.stdout or "") + (r.stderr or ""))
        if ok:
            t = text(anchor)
            check("the separator lands after On-answer, not after Recommendation",
                  "  - **On answer:** (A) → do the thing.\n\n" in t, t)
            # ...and it must not ALSO appear mid-block, which would split the
            # Recommendation from its own continuations.
            check("no blank is inserted between Recommendation and Damage",
                  "because.\n  - **Damage:**" in t, t)

        r = define(anchor, "T5", (
            "- **T5 — a Q ending in Damage** [Questions] — body text.\n"
            "  - **Q1 — a question?** ^T5-Q1\n"
            "    - **(A)** first option.\n"
            "  - **Recommendation:** None.\n"
            "  - **Damage:** reversible.\n"
        ))
        if r.returncode == 0:
            t = text(anchor)
            check("a Q ending in Damage also gets the separator",
                  "  - **Damage:** reversible.\n\n" in t, t)

        # A continuation with NO Recommendation above it earns nothing — the
        # separator exists for the Recommendation, not for the bullet's name.
        # Asserted on an interior bullet: the last row in a section is followed
        # by a blank whatever the guard does, so a trailing-position check would
        # pass for the wrong reason.
        r = define(anchor, "T6", (
            "- **T6 — a bare Damage bullet** [Ready] — body text.\n"
            "  - **Next:** do the thing.\n"
            "  - **Damage:** orphaned, with no Recommendation above it.\n"
            "  - a plain sub-bullet after it.\n"
        ))
        if r.returncode == 0:
            t = text(anchor)
            check("a continuation with no Recommendation gets no separator",
                  "  - **Damage:** orphaned, with no Recommendation above it.\n"
                  "  - a plain sub-bullet after it." in t, t)

        # --- the carve-out stays narrow ------------------------------------
        r = define(anchor, "T3", (
            "- **T3 — ordinary sub-bullets** [Ready] — body text.\n"
            "  - **Next:** do the thing.\n"
            "  - a plain sub-bullet.\n"
            "\n"
            "  - another plain sub-bullet.\n"
        ))
        ok = r.returncode == 0
        check("define with plain sub-bullets succeeds", ok,
              (r.stdout or "") + (r.stderr or ""))
        if ok:
            t = text(anchor)
            check("a blank after a NON-Recommendation bullet is still dropped",
                  "  - a plain sub-bullet.\n  - another plain sub-bullet." in t,
                  t)

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
