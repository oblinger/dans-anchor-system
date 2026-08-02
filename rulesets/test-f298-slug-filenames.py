#!/usr/bin/env python3
"""test-f298-slug-filenames.py — feature-doc filenames carry the anchor slug.

F298 put the anchor slug in front of the F-number (`Tink F298 — Title.md`)
because F-numbers are a PER-ANCHOR namespace that resets at F1 in every anchor:
a bare `F26` names as many files as there are anchors, so an F-number spoken in
chat could not be turned into a file search. Pre-2026-08-02 docs are NOT
renamed, so every matcher must accept BOTH forms permanently — which is what
this suite pins, at all ten sites that anchored on the filename starting with
`F<n> —`.

The load-bearing assertion is the block-ID one. `_container_id_for_doc` fell
through to `re.sub(r"[^\\w\\-]", "-", stem)` on a non-match, so a slug-named doc
would have minted `^Tink-F298---Title-Q1` instead of `^F298-Q1`. Block-IDs are
permanent deep-link targets and `queries.md` / `Q.md` address questions as
`^F<n>-Q<n>` — that failure would have stranded every link into a new doc's
questions while looking like it worked.

Rule bodies are extracted live from the shipped ruleset markdown, and the
scripts are imported from their shipped paths, so this tests what runs.

    python3 test-f298-slug-filenames.py
"""
import importlib.util
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).parent
PATHGUARD = HERE / "R-pathguard.md"
STATE_REGION = HERE / "R-state-region.md"
FCT_FEATURES = HERE / "R-fct-features.md"

DAS = HERE.parent
SKILLS = DAS / "skills"
STATE = SKILLS / "workflow" / "scripts" / "state"
AUDIT = SKILLS / "audit" / "scripts"

# The two names under test, differing ONLY by the slug prefix. Every assertion
# below is "these two behave identically".
LEGACY = "F298 — Feature doc filenames carry the anchor slug.md"
SLUGGED = "Tink F298 — Feature doc filenames carry the anchor slug.md"

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}"
          + ("" if ok else f"  (got {got!r}, want {want!r})"))


def load_body(rule_id: str, ruleset: pathlib.Path):
    """Exec the ```python block under `### RULE {rule_id}` and return body()."""
    text = ruleset.read_text(encoding="utf-8")
    m = re.search(r"^### RULE " + re.escape(rule_id) + r"\b.*?```python\n(.*?)\n```",
                  text, re.S | re.M)
    if not m:
        raise SystemExit(f"could not extract {rule_id} from {ruleset}")
    ns: dict = {}
    exec(m.group(1), ns)
    return ns["body"]


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class Ev:
    def __init__(self, target, inp):
        self.target, self.input = target, inp


class Ctx:
    def __init__(self, target, inp):
        self.event = Ev(target, inp)


def denied(result) -> bool:
    return bool(result) and any("DENY" in r for r in result)


FEATURE = """# [[Tink]] · F298 — Feature doc filenames carry the anchor slug
Some orientation line.

## Open Questions
<!-- state:q ab -->

- **Q1 — Which form?** — slug prefix or not? ^F298-Q1
  - **Recommendation:** None

## Resolved

### Q0 — earlier (resolved)
**Choice:** (A)

## Recovery note
placeholder.
"""


def temp_pair(body=FEATURE):
    """Write the same body under both filenames in one throwaway dir."""
    d = pathlib.Path(tempfile.mkdtemp())
    out = []
    for n in (LEGACY, SLUGGED):
        p = d / n
        p.write_text(body, encoding="utf-8")
        out.append(p)
    return out


# ---------------------------------------------------------------- rule bodies
print("R-pathguard 02/05 — the DENY still fires on a slug-named doc")

legacy, slugged = temp_pair()
body02 = load_body("R-pathguard-02", PATHGUARD)
body05 = load_body("R-pathguard-05", PATHGUARD)

edit_in_region = {"old_string": "slug prefix or not?", "new_string": "which one?"}
for label, p in (("legacy", legacy), ("slug-named", slugged)):
    check(f"rule 02 denies an Open-Questions edit on the {label} doc",
          denied(body02(Ctx(str(p), edit_in_region))), True)

dropped = re.sub(r"## Open Questions.*?## Recovery note", "## Recovery note",
                 FEATURE, flags=re.S)
assert "Q1" not in dropped
for label, p in (("legacy", legacy), ("slug-named", slugged)):
    check(f"rule 05 denies dropping the managed region on the {label} doc",
          denied(body05(Ctx(str(p), {"content": dropped}))), True)

# The widening must not swallow ordinary prose stems. A multi-token prefix is
# NOT a slug — `[A-Za-z][A-Za-z0-9]*` is one bare token by construction.
prose = pathlib.Path(tempfile.mkdtemp()) / "Notes on F12 — the meeting.md"
prose.write_text(FEATURE, encoding="utf-8")
check("a multi-token prose stem is still not a feature doc (rule 02)",
      denied(body02(Ctx(str(prose), edit_in_region))), False)
check("a multi-token prose stem is still not a feature doc (rule 05)",
      denied(body05(Ctx(str(prose), {"content": dropped}))), False)


print("R-state-region 01/02 — the feature-doc branch is taken for both forms")

# For a feature doc the heads NARROW to ('## Resolved', '## Status') because the
# open block stays R-pathguard's DENY (F291). Getting the branch wrong would
# advise the open block here as if it were an ordinary doc.
sr01 = load_body("R-state-region-01", STATE_REGION)
sr02 = load_body("R-state-region-02", STATE_REGION)
resolved_edit = {"old_string": "**Choice:** (A)", "new_string": "**Choice:** (B)"}
for label, p in (("legacy", legacy), ("slug-named", slugged)):
    check(f"rule 01 warns on a Resolved edit to the {label} doc",
          bool(sr01(Ctx(str(p), resolved_edit))), True)
    check(f"rule 02 warns on a Write carrying Resolved to the {label} doc",
          bool(sr02(Ctx(str(p), {"content": FEATURE}))), True)


# ------------------------------------------------------------------- block-ID
print("Block-IDs — the slug must NOT leak into the container token")

be = load_module("backlog_edit", SKILLS / "workflow" / "scripts" / "backlog-edit.py")
for label, name in (("legacy", LEGACY), ("slug-named", SLUGGED)):
    check(f"_container_id_for_feature({label}) is the bare F-number",
          be._container_id_for_feature(pathlib.Path(name)), "F298")
check("a prose stem still falls through unchanged",
      be._container_id_for_feature(pathlib.Path("Smoke Design.md")), "Smoke Design")
check("the canonical stem regex is exported for `state` to reuse",
      bool(be.FEATURE_STEM_RE.match("SKA F294 — x")), True)


# ------------------------------------------------------------------- audit-q
print("audit-q — F-number extraction from the stem")

aq = load_module("audit_q", AUDIT / "audit-q.py")
for label, name in (("legacy", LEGACY), ("slug-named", SLUGGED)):
    m = aq.F_NUMBER_PREFIX_RE.match(pathlib.Path(name).stem)
    check(f"F_NUMBER_PREFIX_RE extracts F298 from the {label} stem",
          m.group(1) if m else None, "F298")


# ----------------------------------------------------------------- audit-roadmap
print("audit-roadmap — M-position filenames")

ar = load_module("audit_roadmap", AUDIT / "audit-roadmap.py")
for label, stem in (("legacy", "F012 — M-Core.2: Ship the thing"),
                    ("slug-named", "SKA F012 — M-Core.2: Ship the thing")):
    check(f"the {label} M-position filename is well-formed",
          bool(ar.FEATURE_MPOS_FILENAME_RE.match(stem)), True)
for label, stem in (("legacy", "F012 — M-Core.2 missing the colon"),
                    ("slug-named", "SKA F012 — M-Core.2 missing the colon")):
    check(f"a malformed {label} M-position is still caught as an attempt",
          bool(ar.FEATURE_MPOS_PREFIX_RE.match(stem))
          and not bool(ar.FEATURE_MPOS_FILENAME_RE.match(stem)), True)


# ------------------------------------------------------------------ audit-plan
print("audit-plan — R-naming-03 and the R-fct-features selector")

ap = load_module("audit_plan", AUDIT / "audit-plan.py")

# A slug-named doc needs NO allowlist entry: it satisfies R-naming-01 directly,
# because the name literally starts with `{slug} `. This is why audit-plan was
# the one inventoried site that needed no code change — asserted so a later
# "tidy" of _NAME_ALLOWLIST can't silently break it.
anchor = pathlib.Path(tempfile.mkdtemp()) / "Tink"
(anchor / "Tink Design" / "Tink Features").mkdir(parents=True)
(anchor / ".anchor").write_text("", encoding="utf-8")
for label, name in (("legacy", LEGACY), ("slug-named", SLUGGED)):
    f = anchor / "Tink Design" / "Tink Features" / name
    f.write_text(FEATURE, encoding="utf-8")
    check(f"chk_name_slug_prefixed passes the {label} doc",
          ap.chk_name_slug_prefixed(f, anchor, [])[0], "pass")

# The R-fct-features `where::` must reach both forms. Read the selector from the
# shipped ruleset rather than restating it, so the test tracks the real file.
_sel_m = re.search(r"^where:: `file: (.+?)`\s*$",
                   FCT_FEATURES.read_text(encoding="utf-8"), re.M)
if _sel_m is None:
    raise SystemExit("could not read the where:: selector from R-fct-features.md")
sel = _sel_m.group(1)
scope = [anchor / "Tink Design" / "Tink Features" / n for n in (LEGACY, SLUGGED)]
matched = {p.name for p in ap._match_file_glob(sel, scope, anchor)}
check("the where:: selector reaches the legacy filename", LEGACY in matched, True)
check("the where:: selector reaches the slug-named filename", SLUGGED in matched, True)

# ...and must NOT reach the dated log shape the `!` negation excludes.
dated = anchor / "Tink Design" / "Tink Features" / "2026-07-17 F221 Fable Scan — audit.md"
dated.write_text(FEATURE, encoding="utf-8")
check("the where:: selector excludes a dated log doc",
      dated in ap._match_file_glob(sel, [dated], anchor), False)


# ------------------------------------------------------- end-to-end: state mint
print("state define — a live Q on a slug-named doc gets a bare ^F<n>-Qn block-ID")

# The whole point of the block-ID fix, exercised through the real CLI rather
# than the helper: a wrong container here is invisible until a deep link breaks.
#
# `state` resolves its anchor argument to a `{prefix} Backlog.md` by searching
# the vault, so the fixture must live IN the vault, not in /tmp — same shape as
# test-f241-q-stamp.sh, under Topic/Misc/Test/ with a slug no real anchor uses.
FIX = pathlib.Path.home() / "ob/kmr/Topic/Misc/Test/F298FIX"
FIX_DOC_NAME = "F298FIX F007 — Slug-named fixture doc.md"
import shutil
shutil.rmtree(FIX, ignore_errors=True)
try:
    (FIX / "F298FIX Design" / "F298FIX Features").mkdir(parents=True)
    (FIX / ".anchor").write_text("slug: F298FIX\ntitle: F298 Fixture\n", encoding="utf-8")
    (FIX / "F298FIX Backlog.md").write_text(
        "# F298FIX Backlog\n\n## Now\n\n- **F007 — Slug-named fixture doc** [Designing]\n",
        encoding="utf-8")
    doc = FIX / "F298FIX Design" / "F298FIX Features" / FIX_DOC_NAME
    doc.write_text("# [[F298FIX]] · F007 — Slug-named fixture doc\n"
                   "Orientation line.\n\n## Summary\n\nBody.\n", encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(STATE), "define", "F298FIX", str(doc), "Q+",
         "--body", "**Q1 — Which form?** — slug prefix or not?\n"
                   "  - **(A)** Slug prefix.\n"
                   "  - **(B)** Bare F-number.\n"
                   "  - **Recommendation:** None"],
        capture_output=True, text=True)
    text = doc.read_text(encoding="utf-8")
    found = re.search(r"\^([\w\-]+)-Q1\b", text)
    if found is None:
        print(f"       (state stdout: {proc.stdout.strip()!r} "
              f"stderr: {proc.stderr.strip()[:400]!r})")
    check("the minted block-ID container is the bare F-number, not the sanitized stem",
          found.group(1) if found else None, "F007")
finally:
    shutil.rmtree(FIX, ignore_errors=True)


print(f"\nF298 slug-prefixed feature filenames: {sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
