#!/usr/bin/env python3
"""test-t153-set-bracket-sections.py — TINK T153: the body's section router is
member-aware, so a SET bracket renders in every class it claims.

F305 rules that a bracket is a SET — `[Ready, User]` is legal and a row may
carry more than one class — and `validate_status` accepts it, splitting on
commas and validating each member. The renderer did not. Setting F217 and F307
to `[Ready, User]` on 2026-08-08 put both into `## Other`: neither appeared
under `## Ready` with its `Next:`, nor under `## User` with its ask, so the two
things that made each row actionable both vanished. The banner meanwhile read
`Ready 12    User 3`, counting them in BOTH classes, because
`in_class_ready`/`in_class_user` are member-aware while the section router was
not — precisely the banner/body disagreement F305 exists to make impossible.

**A set-bracket row renders once PER MEMBER CLASS.** The banner counts per class
through independent `any()` predicates, so a row genuinely in two classes is
counted twice; rendering it once would force the banner to pick a primary too,
re-opening the divergence and discarding what the set bracket carries. The two
appearances are not duplicates — each carries a different payload (`Next:` under
Ready, the ask under User).

  A. `[Ready, User]` reaches BOTH sections, with the right payload in each
  B. ...and does not fall into the catch-all
  C. the coverage assertion stays silent — a two-class row is not a breach
  D. single-member brackets are unchanged
  E. the coverage assertion still fires on a row that reaches NO section

Self-contained: fixture backlog in a tmpdir, parsed by queries-render's own
parser. Never touches the vault."""
import importlib.machinery
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


qr = _load("queries_render_mod", HERE / "queries-render.py")

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


FIXTURE = """# FX Backlog

## Now

- **F217 — legacy anchor-root pages** [Ready, User] — body ^F217
  - **Next:** survey the 1350 anchors and fill the subtype catalogue
  - **User:** sit down with Tink and settle the target anchor-page form
- **F001 — a plain ready row** [Ready] — body ^F001
  - **Next:** do the thing
- **F002 — a plain user row** [User] — body ^F002
  - **User:** log in to the thing
- **F003 — ready and questioning** [Ready, 2 Questions] — body ^F003
  - **Next:** do the other thing

## Done

- **F999 — finished** [Done] — body ^F999
"""


def section_of(text, title):
    """The lines under `## <title>`, up to the next H2."""
    lines = text.splitlines()
    try:
        at = next(i for i, l in enumerate(lines) if l.strip() == f"## {title}")
    except StopIteration:
        return ""
    end = next((i for i in range(at + 1, len(lines))
                if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[at + 1:end])


def render(fixture):
    d = Path(tempfile.mkdtemp())
    backlog = d / "FX Backlog.md"
    backlog.write_text(fixture, encoding="utf-8")
    rows = qr.parse_backlog(backlog)
    body = qr.build_queries_body(
        "FX", "# [A]  FX  -  Runnable 2", rows, {},
        qr.extract_next_actions(backlog), qr.extract_verify_questions(backlog),
        backlog)
    shutil.rmtree(d, ignore_errors=True)
    return "\n".join(body or [])


text = render(FIXTURE)

print("A: a [Ready, User] row reaches both sections")
if "F217" in section_of(text, "Ready"):
    ok("F217 renders under ## Ready")
else:
    no("F217 is absent from ## Ready — the Next: is invisible")
if "F217" in section_of(text, "User"):
    ok("F217 renders under ## User")
else:
    no("F217 is absent from ## User — the ask is invisible")
if "survey the 1350 anchors" in section_of(text, "Ready"):
    ok("...carrying its Next: under Ready")
else:
    no("the Ready appearance does not carry the Next:")

print("B: and not into the catch-all")
if "F217" not in section_of(text, "Other"):
    ok("F217 is not in ## Other")
else:
    no("F217 still falls into the catch-all — the T153 defect")

print("C: coverage stays silent — two classes is not a breach")
if "Coverage failure" not in text:
    ok("the coverage assertion did not fire")
else:
    no("a legitimate two-class row was read as a coverage failure")

print("D: single-member brackets are unchanged")
if "F001" in section_of(text, "Ready") and "F001" not in section_of(text, "User"):
    ok("a plain [Ready] row renders only under Ready")
else:
    no("a plain [Ready] row leaked across sections")
if "F002" in section_of(text, "User") and "F002" not in section_of(text, "Ready"):
    ok("a plain [User] row renders only under User")
else:
    no("a plain [User] row leaked across sections")
if "F003" in section_of(text, "Ready") and "F003" in section_of(text, "Questions"):
    ok("[Ready, 2 Questions] reaches Ready and Questions both")
else:
    no("the Questions member of a set bracket was not honoured")

print("E: the assertion still catches a row that reaches no section")
# Prove the gate is live rather than merely quiet: force a leak by making every
# section reject the row, and confirm the complaint reaches the page.
_ready = qr.READY_ACTIVE_BRACKETS
try:
    qr.READY_ACTIVE_BRACKETS = set()
    leaked = render("# FX Backlog\n\n## Now\n\n"
                    "- **F004 — a lone ready row** [Ready] — body ^F004\n"
                    "  - **Next:** do it\n")
    # With Ready disabled the row must land in the catch-all, not vanish.
    if "F004" in leaked:
        ok("a row no named section claims still reaches the page (catch-all)")
    else:
        no("a row disappeared entirely — F284's totality is broken")
finally:
    qr.READY_ACTIVE_BRACKETS = _ready

# And the assertion itself, driven directly: a section list that omits an
# eligible row must produce the complaint.
class _R:
    def __init__(self, i):
        self.identifier = i


a, b = _R("F100"), _R("F101")
warn = qr._coverage_warning([a, b], [[a]], [])
if warn and "F101" in "\n".join(warn):
    ok("_coverage_warning names the unrendered row")
else:
    no(f"the coverage assertion did not fire on a real leak: {warn}")
if not qr._coverage_warning([a, b], [[a], [a, b]], []):
    ok("...and is silent when a row appears in two sections")
else:
    no("the assertion still treats a two-section row as a failure")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
