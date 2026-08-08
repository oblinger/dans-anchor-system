#!/usr/bin/env python3
"""test-f305-visibility-classes.py — F305: the bracket is a SET, every banner
count is a count of ROWS, and the banner has three zones ordered by attention.

Four claims, each falsifiable on its own:

  A. **Class membership.** Every bracket in the state table lands in the class
     [[DAS Backlog]] assigns it, and membership is tested per-MEMBER so a date
     argument can never collide with a class name.
  B. **Bracket-as-set.** `[Ready, Questions]` puts its row in BOTH classes, so
     class counts may sum to more than the row count. This is the claim most
     likely to be "simplified" away by a later editor, because the sums look
     wrong until you know they are supposed to.
  C. **Rows, not questions.** A row carrying four open questions contributes
     1 to `User`. Dan overturned per-question counting on leverage grounds:
     ten rows with one question each are worth more attention than one row
     with ten.
  D. **One source of truth.** audit-q and queries-render must not merely agree
     — they must be the SAME code. Before F305 each carried its own copy of
     the class logic and its own copy of the format string, with
     queries-render admitting the arrangement in a comment. Identity is
     asserted directly, because equal-output-today is exactly what the two
     copies had right up until they drifted.
"""
import importlib.machinery
import importlib.util
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
PASS = 0
FAIL = 0


def ok(m):
    globals().__setitem__("PASS", PASS + 1)
    print(f"  PASS: {m}")


def no(m):
    globals().__setitem__("FAIL", FAIL + 1)
    print(f"  FAIL: {m}")


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


aq = _load("audit_q", HERE / "audit-q.py")
qr = _load("queries_render_f305", HERE / "queries-render.py")

# ---- A. class membership ----------------------------------------------------
print("== A: every bracket lands in its DAS Backlog class ==")
# (bracket, expected classes) — the state table, transcribed.
TABLE = [
    ("Ready",                ("Ready",)),
    ("Active",               ("Ready",)),
    ("Agreed",               ("Ready",)),        # feature-lifecycle alias
    ("Implementing",         ("Ready",)),        # feature-lifecycle alias
    ("Questions",            ("User",)),
    ("3 Questions",          ("User",)),         # the counted form
    ("User",                 ("User",)),
    ("Designing",            ("User",)),
    ("Verify",               ("Parked",)),
    # `Verify-by` is HIDDEN, not Parked: `sweep_stale_brackets` auto-Dones
    # it on its date, so it leaves its own state with nobody acting — the
    # undo-itself test, applied to the one bracket whose name misleads.
    ("Verify-by 2026-09-01", ("Hidden",)),       # retired form, still live
    ("Blocked F237",         ("Parked",)),       # chained / handle form
    ("Blocked upstream API", ("Parked",)),       # universe form
    ("Waiting 2026-09-01",   ("Hidden",)),
    ("Watching 2026-08-20",  ("Hidden",)),
    ("Done",                 ()),
    ("Done 2026-08-01",      ()),
]
CLASSES = (("Ready", aq.in_class_ready), ("User", aq.in_class_user),
           ("Parked", aq.in_class_parked), ("Hidden", aq.in_class_hidden))
bad = []
for bracket, expected in TABLE:
    got = tuple(n for n, f in CLASSES if f(bracket))
    if got != expected:
        bad.append(f"[{bracket}] -> {got}, expected {expected}")
if bad:
    no("class assignment wrong:\n    " + "\n    ".join(bad))
else:
    ok(f"all {len(TABLE)} brackets land in the right class")

# The argument must never be read as a class name. `[Waiting 2026-09-01]`
# contains no class word, but a future argument could — assert the mechanism
# (per-member matching) rather than trusting today's arguments to be safe.
if not aq.in_class_ready("Blocked ready-queue drain"):
    ok("an ARGUMENT containing a class word does not join that class")
else:
    no("'Blocked ready-queue drain' leaked into class Ready — "
       "membership is matching the whole string, not each member")

# ---- B. bracket-as-set ------------------------------------------------------
print("== B: the bracket is a SET; counts may exceed the row count ==")
if aq.in_class_ready("Ready, Questions") and aq.in_class_user("Ready, Questions"):
    ok("[Ready, Questions] is in BOTH Ready and User")
else:
    no("[Ready, Questions] did not join both classes")

if aq.in_class_ready("Ready, 3 Questions, Verify") \
        and aq.in_class_user("Ready, 3 Questions, Verify") \
        and aq.in_class_parked("Ready, 3 Questions, Verify"):
    ok("[Ready, 3 Questions, Verify] is in all three of its classes")
else:
    no("a three-member bracket did not join all three classes")


def mkrow(identifier, bracket, horizon="Now"):
    return qr.Row(line_num=1, raw_line=f"- **{identifier} — t** [{bracket}] — b",
                  horizon=horizon, identifier=identifier, is_h3=False,
                  bracket=bracket, body="b", arrow_link=None)


qr._count_qfix_subs = lambda bf: 0
# ONE row, two classes. If the sums were forced to partition the rows, this
# banner could not read Ready 1 / User 1 over a single row.
banner = qr.derive_banner("ZZS", [mkrow("F1", "Ready, Questions")],
                          Path("/fake/ZZS Backlog.md"), {}) or ""
if "Ready 1" in banner and "User 1" in banner:
    ok(f"one dual-class row counts in both zone-1 buckets: {banner.split('  -  ')[1][:24]}")
else:
    no(f"dual-class row did not count twice: {banner!r}")

# ---- C. rows, not questions -------------------------------------------------
print("== C: every count is a count of ROWS ==")
TMP = Path(tempfile.mkdtemp(prefix="f305-"))
try:
    anc = TMP / "vault" / "ZZQ"
    (anc / "ZZQ Track").mkdir(parents=True)
    (anc / "ZZQ Design" / "ZZQ Features").mkdir(parents=True)
    (anc / ".anchor").write_text("slug: ZZQ\n", encoding="utf-8")
    (anc / "ZZQ Design" / "ZZQ Features" / "F010 — Thing.md").write_text(
        "# F010 — Thing\n\n## Open Questions\n\n"
        "- **Q1 — a** — pick\n- **Q2 — b** — pick\n"
        "- **Q3 — c** — pick\n- **Q4 — d** — pick\n",
        encoding="utf-8")
    bl = anc / "ZZQ Track" / "ZZQ Backlog.md"
    bl.write_text("# ZZQ Backlog\n\n## Now\n\n"
                  "- **F010 — Thing** [4 Questions] — → [[F010 — Thing]] ^F010\n",
                  encoding="utf-8")
    vidx = aq.build_vault_index(TMP / "vault")
    b = aq.derive_anchor_banner("ZZQ", bl, vidx) or ""
    m = re.search(r"User\s+(\d+)", b)
    if m and m.group(1) == "1":
        ok("a row with 4 open questions contributes User 1, not User 4")
    else:
        no(f"User count is per-question, not per-row: {b!r}")

    # ---- D. one source of truth --------------------------------------------
    print("== D: audit-q and queries-render share ONE definition ==")
    shared = [("in_class_ready", qr._in_class_ready, aq.in_class_ready),
              ("in_class_user", qr._in_class_user, aq.in_class_user),
              ("in_class_parked", qr._in_class_parked, aq.in_class_parked),
              ("in_class_hidden", qr._in_class_hidden, aq.in_class_hidden)]
    drifted = [n for n, a, b2 in shared if a is not b2]
    if drifted:
        no(f"queries-render redefines instead of importing: {drifted}")
    else:
        ok("all four class predicates are the SAME object in both modules")

    # The format string: only one module may build the banner line.
    qr_src = (HERE / "queries-render.py").read_text(encoding="utf-8")
    aq_src = (HERE / "audit-q.py").read_text(encoding="utf-8")
    lit = 'f"Ready {'
    if qr_src.count(lit) == 0 and aq_src.count(lit) == 1:
        ok("the banner format string exists in exactly one place")
    else:
        no(f"format string copies — queries-render {qr_src.count(lit)}, "
           f"audit-q {aq_src.count(lit)} (want 0 and 1)")

    # The render predicate: the banner's zone-1 scope IS the body's membership,
    # so the two cannot disagree. This is the MUX 2026-06-04 defect's home.
    if qr._row_should_render(mkrow("F1", "3 Questions", horizon="Later")):
        ok("a [Questions] row under ## Later renders — so it must also count")
    else:
        no("a [Questions] row under ## Later does not render (banner/body split)")
    if not qr._row_should_render(mkrow("F2", "Waiting 2026-09-01", horizon="Later")):
        ok("a [Waiting] row under ## Later does NOT render (Hidden)")
    else:
        no("a Hidden row rendered in the body")

    # ---- E. the three zones -------------------------------------------------
    print("== E: three zones, ordered by attention ==")
    ZONES = re.compile(
        r"^# \[[^\]]*\]  \S+  -  "
        r"Ready \d+    User \d+   \|   "
        r"Now \d+    Next \d+    Later \d+   \|   "
        r"Parked \d+    Waiting \d+    Icebox \d+$")
    rows = [mkrow("F1", "Ready"), mkrow("F2", "Questions"),
            mkrow("F3", "Verify"), mkrow("F4", "Waiting 2026-09-01"),
            mkrow("F5", "Blocked F9")]
    bz = qr.derive_banner("ZZZ", rows, Path("/fake/ZZZ Backlog.md"), {}) or ""
    if ZONES.match(bz):
        ok("banner matches the locked three-zone form + spacing")
    else:
        no(f"banner is off the locked form: {bz!r}")
    # Parked = Verify + Blocked = 2; Waiting = the one dated row = 1. Both were
    # invisible in EVERY count before F305 — that invisibility is the defect.
    if "Parked 2" in bz and "Waiting 1" in bz:
        ok("Parked folds [Verify]+[Blocked]; Waiting folds [Waiting]+[Watching]")
    else:
        no(f"zone 3 counts wrong: {bz!r}")
    if "Verify " not in bz.split("   |   ")[1]:
        ok("Verify left zone 2 — it is a class now, inside Parked")
    else:
        no(f"Verify is still a zone-2 horizon count: {bz!r}")

    # ---- F. the checks SEE a set member ------------------------------------
    # The conversion from `e.status == "Designing"` to `has_member(...)` was
    # verified against the live corpus by diffing all 251 findings before and
    # after — bit-identical, because the vault holds no set brackets yet. That
    # proves the change is safe; it proves NOTHING about whether it works, as a
    # no-op would produce the same diff. These assert the behaviour that
    # bit-identity cannot: a set member is found where a whole-string compare
    # would silently skip the row and report success by saying nothing.
    print("== F: a set member is seen where whole-string matching would skip ==")
    CASES = [
        ("Designing",         "Ready, Designing",        "Designing"),
        ("User",              "Ready, User",             "User"),
        ("Questions",         "Ready, 3 Questions",      "Questions"),
        ("Done",              "Done, Verify",            "Done"),
        ("Active",            "Active, Questions",       "Active"),
    ]
    misses = []
    for name, bracket, member in CASES:
        # the old behaviour, reconstructed exactly
        old_would_match = (bracket.strip() == member)
        new_matches = aq.has_member(bracket, member)
        if not new_matches or old_would_match:
            misses.append(f"[{bracket}] ~ {member}: old={old_would_match} new={new_matches}")
    if misses:
        no("member matching wrong:\n    " + "\n    ".join(misses))
    else:
        ok(f"all {len(CASES)} set brackets are seen now and were missed before")

    # The counted form must yield its NUMBER out of a set, since C24 compares
    # the claim against the doc's real pending count.
    qm = aq.questions_member("Ready, 4 Questions, Verify")
    if qm and qm[1] == 4:
        ok("questions_member pulls the claimed count (4) out of a set")
    else:
        no(f"questions_member lost the count in a set: {qm!r}")
    if aq.questions_member("Ready, Questions")[1] is None:
        ok("a bare Questions member reports no explicit count")
    else:
        no("bare Questions should report count None")
    if aq.questions_member("Ready, Verify") is None:
        ok("a set with no Questions member reports None")
    else:
        no("questions_member matched a set with no Questions")

    # An ARGUMENT must never be mistaken for a member keyword.
    if not aq.has_member("Blocked Questions-doc", "Questions"):
        ok("`[Blocked Questions-doc]` is not read as a Questions row")
    else:
        no("a Blocked ARGUMENT was read as a member keyword")
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
