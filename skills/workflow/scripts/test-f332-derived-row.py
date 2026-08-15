#!/usr/bin/env python3
"""test-f332-derived-row.py — F332: pure-link (derived) backlog rows.

A row whose body LEADS with the arrow pointer is derived: on every touch,
everything after the pointer regenerates from the doc — `next::` first,
then frontmatter description, then the H1 orientation line — and the
pointer's display text collapses to the bare row id. Pins:

  1. Touch regenerates the derived line from the doc's `next::` and DROPS
     the row's `- **Next:**` sub-bullet (the doc owns it).
  2. A [Ready] set with NO --next passes the F171 gate when the doc carries
     `next::`, and materializes no sub-bullet.
  3. No `next::` → derived line falls back to the frontmatter description.
  4. A prose-led (non-derived) body is never rewritten.
  5. An unresolvable pointer leaves the row untouched (no crash).
  6. verify_write_landed accepts the normalized pointer (same target).
"""
import sys as _sys; _sys.dont_write_bytecode = True

import contextlib
import importlib.machinery
import importlib.util
import io
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


st = _load("state_mod_drv", HERE / "state")
be = st.be

PASS = 0
FAIL = 0
def ok(m): globals().__setitem__("PASS", PASS + 1); print(f"  PASS: {m}")
def no(m): globals().__setitem__("FAIL", FAIL + 1); print(f"  FAIL: {m}")

TMP = Path(tempfile.mkdtemp())
be.VAULT_ROOT = TMP

BL = TMP / "ZZD Track" / "ZZD Backlog.md"
BL.parent.mkdir(parents=True)
BL.write_text(
    "---\ndescription: t\n---\n\n# ZZD Backlog\n\n## Now\n\n"
    "- **F001 — nexted** [Ready] — → [[ZZD001 - nexted|F001 — nexted]] — "
    "stale hand prose to be overwritten ^F001\n"
    "  - **Next:** stale row-side next.\n"
    "- **F002 — descful** [Questions] — → [[ZZD002 - descful|F002]] ^F002\n"
    "- **T003 — prose** [Ready] — prose first, then → [[ZZD001 - nexted]] ^T003\n"
    "  - **Next:** keep me.\n"
    "- **T004 — dangling** [Waiting 2026-09-01] — → [[No Such Doc|T004]] ^T004\n"
    "\n## Done\n",
    encoding="utf-8",
)

D1 = TMP / "ZZD Design" / "ZZD Features" / "ZZD001 - nexted.md"
D1.parent.mkdir(parents=True)
D1.write_text(
    "---\ndescription: doc one description\n---\n\n"
    "# [[ZZD]] · F001 — nexted\nOne-line orientation.\n\n"
    "next:: run the derived thing\n\n"
    "## Status\n\n**Ready** — set.\n",
    encoding="utf-8",
)
D2 = TMP / "ZZD Design" / "ZZD Features" / "ZZD002 - descful.md"
D2.write_text(
    "---\ndescription: two's description line\n---\n\n"
    "# [[ZZD]] · F002 — descful\nOrientation two.\n\n"
    "## Open Questions\n\n- **Q1 — pick?** — context. ^F002-Q1\n"
    "- **(A)** a\n- **(B)** b\n"
    "- **Recommendation:** None\n\n"
    "## Status\n\n**Questions** — one open.\n",
    encoding="utf-8",
)

be.find_backlog = lambda slug: BL
be.find_icebox = lambda slug: None
be.refresh_q_md = lambda slug: None
be.append_messages = lambda *a, **k: None
be.write_state = lambda *a, **k: None
be.heal_backlog_if_stale = lambda *a, **k: None
be._selffire = lambda *a, **k: None
st._selffire = lambda *a, **k: None


def touch(label, status, next_text=None, body=None):
    a = SimpleNamespace(
        doc="Backlog", label=label, verb="set", inline=body, from_file=None,
        why_ask=None, horizon=None, status=status, title=None,
        next_step=next_text, verify=None, user=None, why_user=None,
        why_user_action=None,
    )
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            rc = st.cmd_item("ZZD", TMP, a)
        except SystemExit as e:
            rc = e.code
    return rc, buf.getvalue()


def row_block(rid):
    lines = BL.read_text().splitlines()
    out, on = [], False
    for l in lines:
        if l.startswith(f"- **{rid}"):
            on = True
        elif on and (l.startswith("- ") or l.startswith("## ")):
            break
        if on:
            out.append(l)
    return "\n".join(out)


print("== 1. touch regenerates from next:: and drops the Next sub-bullet ==")
rc, out = touch("F001", "Ready")
blk = row_block("F001")
if ("→ [[ZZD001 - nexted|F001]] — run the derived thing" in blk
        and "stale hand prose" not in blk):
    ok("derived line regenerated from doc next::, display collapsed to bare id")
else:
    no(f"rc={rc} out={out}\nblock:\n{blk}")
if "**Next:**" not in blk:
    ok("row-side `- **Next:**` dropped — the doc owns it")
else:
    no(f"Next sub-bullet survived:\n{blk}")

print("== 2. [Ready] with no --next passes via the doc's next:: ==")
rc, out = touch("F001", "Ready")   # second touch, still no --next anywhere
blk = row_block("F001")
if rc in (0, None) and "**Next:**" not in blk:
    ok("F171 Next gate satisfied by the doc; no sub-bullet materialized")
else:
    no(f"rc={rc} out={out}\nblock:\n{blk}")

print("== 3. no next:: → derived line falls back to the description ==")
rc, out = touch("F002", "Questions")
blk = row_block("F002")
if "→ [[ZZD002 - descful|F002]] — two's description line" in blk:
    ok("derived line fell back to frontmatter description")
else:
    no(f"rc={rc} out={out}\nblock:\n{blk}")

print("== 4. a prose-led body is never rewritten ==")
rc, out = touch("T003", "Ready")
blk = row_block("T003")
if "prose first, then" in blk and "**Next:** keep me." in blk:
    ok("non-derived row untouched (body + Next kept)")
else:
    no(f"rc={rc} out={out}\nblock:\n{blk}")

print("== 5. unresolvable pointer: row left alone, no crash ==")
rc, out = touch("T004", "Waiting 2026-09-01")
blk = row_block("T004")
if rc in (0, None) and "→ [[No Such Doc|T004]]" in blk:
    ok("dangling pointer untouched")
else:
    no(f"rc={rc} out={out}\nblock:\n{blk}")

print("== 6. landed check accepts the normalized pointer body ==")
rc, out = touch("F001", "Ready",
                body="→ [[ZZD001 - nexted|F001 — long display text]]")
blk = row_block("F001")
if rc in (0, None) and "→ [[ZZD001 - nexted|F001]] — run the derived thing" in blk:
    ok("explicit derived body normalized; write reported landed")
else:
    no(f"rc={rc} out={out}\nblock:\n{blk}")

shutil.rmtree(TMP, ignore_errors=True)
print("-" * 40)
print(f"test-f332-derived-row: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
