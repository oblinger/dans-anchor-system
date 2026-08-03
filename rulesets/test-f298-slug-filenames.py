#!/usr/bin/env python3
"""test-f298-slug-filenames.py — the three feature-doc filename forms.

F298 put the anchor slug in front of the F-number (`Tink F298 — Title.md`)
because F-numbers are a PER-ANCHOR namespace that resets at F1 in every anchor:
a bare `F26` names as many files as there are anchors, so an F-number spoken in
chat could not be turned into a file search. F300 then fused the slug to the
number and went ASCII (`TINK298 - Title.md`) so the result is one token that can
be typed from memory. Older docs are NOT renamed, so every matcher must accept
all THREE forms permanently — which is what this suite pins:

    F298 — Title              legacy, every doc before 2026-08-02
    Tink F298 — Title         F298, file-prefix slug + em-dash
    TINK298 - Title           F300, `.anchor` slug fused, ASCII hyphen

The load-bearing assertion is the block-ID one, and F300 sharpens it. Under
F298 the fix was to stop the slug LEAKING into the container token; under F300
the `F` is not in the filename at all, so `feature_number` must RECONSTRUCT it.
Unfixed, `_container_id_for_doc` falls through to `re.sub(r"[^\\w\\-]", "-",
stem)` and mints `^TINK298---Title-Q1` instead of `^F298-Q1`. Block-IDs are
permanent deep-link targets and `queries.md` / `Q.md` address questions as
`^F<n>-Q<n>` — that failure strands every link into a new doc's questions while
looking like it worked.

One fixture uses a MIXED-CASE slug (`Warden`), because the F300 rule is "the
slug's own casing, read verbatim from `.anchor`" — not "uppercase". Asserting
it with an uppercase slug only would leave the rule assumed rather than tested.

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

# The three names under test, differing ONLY in how the stem heads. Every
# assertion below is "these three behave identically".
LEGACY = "F298 — Feature doc filenames carry the anchor slug.md"
SLUGGED = "Tink F298 — Feature doc filenames carry the anchor slug.md"
FUSED = "TINK298 - Feature doc filenames carry the anchor slug.md"
FORMS = (("legacy", LEGACY), ("slug-named", SLUGGED), ("fused", FUSED))

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


FEATURE = """# [[TINK]] · F298 — Feature doc filenames carry the anchor slug
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


def temp_forms(body=FEATURE):
    """Write the same body under all three filenames in one throwaway dir."""
    d = pathlib.Path(tempfile.mkdtemp())
    return [(label, d / n) for label, n in FORMS] + [
        # A mixed-case slug, because F300 reads the slug VERBATIM from
        # `.anchor` — `Warden` is the corpus's one non-uppercase slug, and
        # without it the casing rule is assumed rather than tested.
        ("fused/mixed-case slug", d / "Warden042 - Rule engine budget.md")]


# ---------------------------------------------------------------- rule bodies
print("R-pathguard 02/05 — the DENY fires on all three filename forms")

forms = temp_forms()
for _label, p in forms:
    p.write_text(FEATURE, encoding="utf-8")
body02 = load_body("R-pathguard-02", PATHGUARD)
body05 = load_body("R-pathguard-05", PATHGUARD)

edit_in_region = {"old_string": "slug prefix or not?", "new_string": "which one?"}
for label, p in forms:
    check(f"rule 02 denies an Open-Questions edit on the {label} doc",
          denied(body02(Ctx(str(p), edit_in_region))), True)

dropped = re.sub(r"## Open Questions.*?## Recovery note", "## Recovery note",
                 FEATURE, flags=re.S)
assert "Q1" not in dropped
for label, p in forms:
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

# ...and the F300 widening must not swallow ordinary hyphenated prose. The
# fused branch demands letters IMMEDIATELY followed by digits, so a stem whose
# number is a separate token (`ASP B10 - …`, a real vault shape) is not one.
for stem in ("ASP B10 - World Specification Example Log",
             "KAN - Kolmogorov-Arnold Neworks",
             "2023 - Resume Samples"):
    hyphen_prose = pathlib.Path(tempfile.mkdtemp()) / f"{stem}.md"
    hyphen_prose.write_text(FEATURE, encoding="utf-8")
    check(f"hyphenated prose {stem.split(' - ')[0]!r} is not a feature doc",
          denied(body02(Ctx(str(hyphen_prose), edit_in_region))), False)


print("R-state-region 01/02 — the feature-doc branch is taken for all forms")

# For a feature doc the heads NARROW to ('## Resolved', '## Status') because the
# open block stays R-pathguard's DENY (F291). Getting the branch wrong would
# advise the open block here as if it were an ordinary doc.
sr01 = load_body("R-state-region-01", STATE_REGION)
sr02 = load_body("R-state-region-02", STATE_REGION)
resolved_edit = {"old_string": "**Choice:** (A)", "new_string": "**Choice:** (B)"}
for label, p in forms:
    check(f"rule 01 warns on a Resolved edit to the {label} doc",
          bool(sr01(Ctx(str(p), resolved_edit))), True)
    check(f"rule 02 warns on a Write carrying Resolved to the {label} doc",
          bool(sr02(Ctx(str(p), {"content": FEATURE}))), True)


# ------------------------------------------------------------------- block-ID
print("Block-IDs — the slug must NOT leak into the container token")

be = load_module("backlog_edit", SKILLS / "workflow" / "scripts" / "backlog-edit.py")
for label, name in FORMS:
    check(f"_container_id_for_feature({label}) is the bare F-number",
          be._container_id_for_feature(pathlib.Path(name)), "F298")
check("_container_id_for_feature(fused/mixed-case slug) reconstructs the F",
      be._container_id_for_feature(pathlib.Path("Warden042 - Rule engine budget.md")),
      "F042")
check("a prose stem still falls through unchanged",
      be._container_id_for_feature(pathlib.Path("Smoke Design.md")), "Smoke Design")
check("a hyphenated prose stem still falls through unchanged",
      be._container_id_for_feature(pathlib.Path("KAN - Kolmogorov-Arnold Neworks.md")),
      "KAN - Kolmogorov-Arnold Neworks")
check("the canonical extractor is exported for `state` to reuse",
      be.feature_number("SKA F294 — x"), "F294")
# The fused slug is letters-only ON PURPOSE. `[A-Za-z0-9]*\\d+` would be
# ambiguous: greedy matching splits `TINK300` into slug `TINK30` + number `0`,
# so the container would come out `F0` and every deep link would collide.
check("the fused form does not mis-split the slug against the number",
      be.feature_number("TINK300 - x"), "F300")


# ------------------------------------------------------------------- audit-q
print("audit-q — F-number extraction from the stem")

aq = load_module("audit_q", AUDIT / "audit-q.py")
for label, name in FORMS:
    check(f"audit-q extracts F298 from the {label} stem",
          aq.feature_number(pathlib.Path(name).stem), "F298")
check("audit-q leaves a prose stem unmatched",
      aq.feature_number("KAN - Kolmogorov-Arnold Neworks"), None)


# ----------------------------------------------------------------- audit-roadmap
print("audit-roadmap — M-position filenames")

ar = load_module("audit_roadmap", AUDIT / "audit-roadmap.py")
for label, stem in (("legacy", "F012 — M-Core.2: Ship the thing"),
                    ("slug-named", "SKA F012 — M-Core.2: Ship the thing"),
                    ("fused", "SKA012 - M-Core.2: Ship the thing")):
    check(f"the {label} M-position filename is well-formed",
          bool(ar.FEATURE_MPOS_FILENAME_RE.match(stem)), True)
for label, stem in (("legacy", "F012 — M-Core.2 missing the colon"),
                    ("slug-named", "SKA F012 — M-Core.2 missing the colon"),
                    ("fused", "SKA012 - M-Core.2 missing the colon")):
    check(f"a malformed {label} M-position is still caught as an attempt",
          bool(ar.FEATURE_MPOS_PREFIX_RE.match(stem))
          and not bool(ar.FEATURE_MPOS_FILENAME_RE.match(stem)), True)


# ------------------------------------------------------------------ audit-plan
print("audit-plan — R-naming-03 and the R-fct-features selector")

ap = load_module("audit_plan", AUDIT / "audit-plan.py")

# The legacy and F298 forms satisfy R-naming-01 by a different route than the
# F300 one. The first two pass the `{slug} `-prefix test directly (or the
# `^F\d+ [—-] ` allowlist); the FUSED form passes NEITHER — `TINK298` has no
# space after the slug — so it needs the `^[A-Za-z]+\d{3} - ` allowlist entry.
# That was the twelfth site, missed by F300's inventory of eleven and caught
# here. Asserted so a later "tidy" of _NAME_ALLOWLIST can't silently break it.
anchor = pathlib.Path(tempfile.mkdtemp()) / "Tink"
(anchor / "Tink Design" / "Tink Features").mkdir(parents=True)
(anchor / ".anchor").write_text("slug: TINK\n", encoding="utf-8")
for label, name in FORMS:
    f = anchor / "Tink Design" / "Tink Features" / name
    f.write_text(FEATURE, encoding="utf-8")
    # The F298 form is the one exception, and it is F300's whole point. Here the
    # anchor's folder is `Tink` while its slug is `TINK`, so `Tink F298 — …`
    # leads with the FOLDER NAME — which R-naming-01's recast (T112) refuses,
    # because that is the spelling that makes `{slug}` interpolation resolve to
    # a token no file matches. It passes wherever the two agree (`SKA F294 — …`
    # under folder `Skill Agent`, slug `SKA`), asserted just below. No live doc
    # carries the failing shape: the one that did was renamed forward by F300.
    want = "fail" if label == "slug-named" else "pass"
    check(f"chk_name_slug_prefixed {want}s the {label} doc",
          ap.chk_name_slug_prefixed(f, anchor, [])[0], want)

# ...and the F298 form is fine when the folder name IS the slug, which is the
# common case — only the four Staff agents ever diverged.
ska = pathlib.Path(tempfile.mkdtemp()) / "Skill Agent"
(ska / "SKA Design" / "SKA Features").mkdir(parents=True)
(ska / ".anchor").write_text("slug: SKA\n", encoding="utf-8")
f = ska / "SKA Design" / "SKA Features" / "SKA F294 — URL validation.md"
f.write_text(FEATURE, encoding="utf-8")
check("the F298 form passes where the prefix IS the slug",
      ap.chk_name_slug_prefixed(f, ska, [])[0], "pass")

# `{slug}` in a where:: selector is the `.anchor` slug (`_anchor_name` reads the
# `slug:` key) — which is exactly the token F300 fuses to the number. Pinned
# because the F300 feature-doc terms are built on that equality.
check("{slug} resolves to the .anchor slug, not the folder name",
      ap._anchor_name(anchor), "TINK")

# The R-fct-features `where::` must reach all three forms. Read the selector from
# the shipped ruleset rather than restating it, so the test tracks the real file.
_sel_m = re.search(r"^where:: `file: (.+?)`\s*$",
                   FCT_FEATURES.read_text(encoding="utf-8"), re.M)
if _sel_m is None:
    raise SystemExit("could not read the where:: selector from R-fct-features.md")
sel = _sel_m.group(1)
scope = [anchor / "Tink Design" / "Tink Features" / n for _l, n in FORMS]
matched = {p.name for p in ap._match_file_glob(sel, scope, anchor)}
for label, name in FORMS:
    check(f"the where:: selector reaches the {label} filename", name in matched, True)

# The fused form must also be reachable where the `{slug}`-pinned terms CANNOT
# help: 18 `* Features/` folders are themselves anchors, and inside one the
# doc's anchor-relative path is a bare filename whose slug (`SKA294`) is the
# PARENT anchor's, while `{slug}` there resolves to the folder name
# (`SKA Features`). That case is what the slug-agnostic third term exists for.
fa = pathlib.Path(tempfile.mkdtemp()) / "SKA Features"
fa.mkdir()
(fa / ".anchor").write_text("description: dated feature specs\n", encoding="utf-8")
nested = fa / "SKA294 - URL validation.md"
nested.write_text(FEATURE, encoding="utf-8")
check("the where:: selector reaches a fused doc at a Features-anchor root",
      nested in ap._match_file_glob(sel, [nested], fa), True)

# The index-page term must reach the index page, and it CANNOT be `{slug}`-pinned
# (T111). Written `**/{slug} Features.md` it reached 0 of 22 index pages vault-wide
# — self-reference, not casing: `SKA Features.md` sits inside `SKA Features/`,
# which is itself an anchor, so `{slug}` there IS `SKA Features` and the term
# expands to `SKA Features Features.md`. Silent inertness is the T101 disease, so
# it gets a regression guard rather than a comment.
idx = fa / "SKA Features.md"
idx.write_text("# SKA Features\n\nindex.\n", encoding="utf-8")
check("the where:: selector reaches the index page inside a Features-anchor",
      idx in ap._match_file_glob(sel, [idx], fa), True)
check("...which a {slug}-pinned index term would NOT have reached",
      idx in ap._match_file_glob("**/{slug} Features.md", [idx], fa), False)

# ...and must NOT reach the dated log shape, nor the hyphenated prose the two
# extra F300 negations exclude. Both negations are structural, not
# file-specific: a valid `{SLUG}{NNN}` stem is >= 5 chars (2 letters + 3
# digits) so `!**/???? - *` can never hit one, and none contains a `.` before
# the separator so `!**/*.? - *` cannot either.
for why, name in (
        ("a dated log doc", "2026-07-17 F221 Fable Scan — audit.md"),
        ("a bare-year stem", "2023 - Resume Samples.md"),
        ("a dotted section number", "Section 3.4 - User Engagement Ideas.md"),
        ("multi-token hyphenated prose", "ASP B10 - World Specification Log.md")):
    p = anchor / "Tink Design" / "Tink Features" / name
    p.write_text(FEATURE, encoding="utf-8")
    check(f"the where:: selector excludes {why}",
          p in ap._match_file_glob(sel, [p], anchor), False)


# ------------------------------------------------------- end-to-end: state mint
print("state define — a live Q on a fused-name doc gets a bare ^F<n>-Qn block-ID")

# The whole point of the block-ID fix, exercised through the real CLI rather
# than the helper: a wrong container here is invisible until a deep link breaks.
#
# `state` resolves its anchor argument to a `{prefix} Backlog.md` by searching
# the vault, so the fixture must live IN the vault, not in /tmp — same shape as
# test-f241-q-stamp.sh, under Topic/Misc/Test/ with a slug no real anchor uses.
#
# The fixture slug is letters-only ON PURPOSE. The fused grammar is
# `[A-Za-z]+(\d+)`, so a slug that itself ends in digits cannot use the fused
# form unambiguously — `F298FIX007` would extract `F298`. Every real anchor
# slug in the corpus is letters-only (`TINK`, `SKA`, `LUMEN`, `Warden`), which
# is what makes the form safe; a future digit-bearing slug would have to keep
# one of the two older filename shapes.
FIX = pathlib.Path.home() / "ob/kmr/Topic/Misc/Test/SLUGFIX"
SLUGGED_DOC = "SLUGFIX F007 — Slug-named fixture doc.md"
FUSED_DOC = "SLUGFIX008 - Fused fixture doc.md"
import shutil
shutil.rmtree(FIX, ignore_errors=True)
try:
    feats = FIX / "SLUGFIX Design" / "SLUGFIX Features"
    feats.mkdir(parents=True)
    (FIX / ".anchor").write_text("slug: SLUGFIX\ntitle: Filename Fixture\n",
                                 encoding="utf-8")
    (FIX / "SLUGFIX Backlog.md").write_text(
        "# SLUGFIX Backlog\n\n## Now\n\n"
        "- **F007 — Slug-named fixture doc** [Designing]\n"
        "- **F008 — Fused fixture doc** [Designing]\n",
        encoding="utf-8")
    for name, fnum, title in ((SLUGGED_DOC, "F007", "Slug-named fixture doc"),
                              (FUSED_DOC, "F008", "Fused fixture doc")):
        doc = feats / name
        doc.write_text(f"# [[SLUGFIX]] · {fnum} — {title}\n"
                       "Orientation line.\n\n## Summary\n\nBody.\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(STATE), "define", "SLUGFIX", str(doc), "Q+",
             "--body", "**Q1 — Which form?** — which filename shape?\n"
                       "  - **(A)** Slug prefix.\n"
                       "  - **(B)** Fused.\n"
                       "  - **Recommendation:** None"],
            capture_output=True, text=True)
        text = doc.read_text(encoding="utf-8")
        found = re.search(r"\^([\w\-]+)-Q1\b", text)
        if found is None:
            print(f"       (state stdout: {proc.stdout.strip()!r} "
                  f"stderr: {proc.stderr.strip()[:400]!r})")
        check(f"the block-ID minted on {name!r} is the bare F-number",
              found.group(1) if found else None, fnum)
finally:
    shutil.rmtree(FIX, ignore_errors=True)


print(f"\nFeature-doc filename forms (F298 + F300): "
      f"{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
