#!/usr/bin/env python3
"""test-t045-pathguard.py — the feature-doc question-region pathguard (R-pathguard 02/05).

Two T045 defects, both fixed here and pinned so they can't regress:

  * FALSE POSITIVE (rule 02) — the Edit guard matched the heading string as a
    bare substring (`any(h in old or h in new)`), so editing an unrelated
    `## Recovery note` that merely *quoted* `## Open Questions` in prose was
    refused. The match is now LINE-ANCHORED (`^## Open Questions$`): prose
    mentions pass, a real heading line still fires.
  * TOO BLUNT (rule 05) — the Write guard denied ANY whole-file Write to an
    existing feature doc whose content mentioned the heading, so a legitimate
    prose rewrite that left the region untouched was blocked, and a doc merely
    quoting the heading false-positived. It now REGION-DIFFS: a Write that
    preserves the managed region verbatim passes; one that changes or drops it
    (how Lumen F002 lost a pending Q2 + its resolved archive) is denied.

The bodies are extracted live from R-pathguard.md, so this tests the shipped
source, not a copy.

    python3 test-t045-pathguard.py
"""
import re
import pathlib
import tempfile

RULESET = pathlib.Path(__file__).parent / "R-pathguard.md"
STATE_REGION = pathlib.Path(__file__).parent / "R-state-region.md"


def load_body(rule_id: str, ruleset: pathlib.Path = RULESET):
    """Exec the ```python block under `### RULE {rule_id}` and return its body()."""
    text = ruleset.read_text(encoding="utf-8")
    m = re.search(r"^### RULE " + re.escape(rule_id) + r"\b.*?```python\n(.*?)\n```",
                  text, re.S | re.M)
    if not m:
        raise SystemExit(f"could not extract {rule_id} from {ruleset}")
    ns: dict = {}
    exec(m.group(1), ns)
    return ns["body"]


body02 = load_body("R-pathguard-02")
body05 = load_body("R-pathguard-05")


class Ev:
    def __init__(self, target, inp):
        self.target = target
        self.input = inp


class Ctx:
    def __init__(self, target, inp):
        self.event = Ev(target, inp)


def denied(result) -> bool:
    return bool(result) and any("DENY" in r for r in result)


results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f"  (got {got!r}, want {want!r})"))


# ---- shared on-disk fixture: a feature doc with a real managed region --------
FEATURE = """# F002 — Morning ritual
Some orientation line.

## Design
prose about the design.

## Open Questions
<!-- state:q ab -->

- **Q2 — Which inbox?** — should the ritual read Gmail or Fastmail? ^F002-Q2
  - **Recommendation:** None

## Resolved

### Q1 — earlier (resolved)
**Choice:** (A)

## Recovery note
placeholder.
"""


def temp_feature(body=FEATURE, name="F002 — Morning ritual.md"):
    d = pathlib.Path(tempfile.mkdtemp())
    p = d / name
    p.write_text(body, encoding="utf-8")
    return p


print("Rule 02 (Edit) — line-anchored, not substring")

p = temp_feature()

# 1. THE FALSE POSITIVE: editing ## Recovery note prose that quotes the headings
old_rn = "placeholder."
new_rn = ("the loss wiped the managed region (## Open Questions / ## Resolved) "
          "wholesale; filed as T045.")
check("prose quoting the heading inline does NOT fire (the T045 FP)",
      denied(body02(Ctx(str(p), {"old_string": old_rn, "new_string": new_rn}))), False)

# 2. new_string carries a REAL heading line → fires (hand-creating the region)
check("a real `## Open Questions` heading line in new_string fires",
      denied(body02(Ctx(str(p), {"old_string": "x", "new_string": "\n## Open Questions\n\n- **Q3 — ?**\n"}))), True)

# 3. old_string sits inside the on-disk managed region → fires (location-based)
check("editing inside the on-disk Open Questions section fires",
      denied(body02(Ctx(str(p), {"old_string": "should the ritual read Gmail or Fastmail?",
                                 "new_string": "which inbox?"}))), True)

# 4. old_string inside the on-disk Resolved section → NO LONGER this rule's.
# F291 moved a feature doc's `## Resolved` to R-state-region as a warn, on the
# rule *deny where desync is possible, detect where it is not*: an archived
# decision is not rendered, not counted, and gates nothing, so there is no live
# state left to protect. Both halves are asserted so the handoff cannot quietly
# become a coverage hole.
resolved_edit = Ctx(str(p), {"old_string": "**Choice:** (A)",
                             "new_string": "**Choice:** (B)"})
check("editing the on-disk Resolved section no longer DENIES here (F291)",
      denied(body02(resolved_edit)), False)
check("...and R-state-region picks it up as a warning instead",
      bool(load_body("R-state-region-01", STATE_REGION)(resolved_edit)), True)

# 5. non-feature-doc filename is never guarded by this rule
q = temp_feature(name="Some Note.md")
check("a non-feature-doc edit is not guarded",
      denied(body02(Ctx(str(q), {"old_string": "x", "new_string": "## Open Questions\n"}))), False)


print("Rule 05 (Write) — region-diff, not 'mentions the heading'")

# 6. prose-only rewrite that preserves the region verbatim → allow
p2 = temp_feature()
preserved = FEATURE.replace("prose about the design.", "COMPLETELY rewritten design prose.")
assert "## Open Questions" in preserved
check("a prose rewrite preserving the region verbatim passes",
      denied(body05(Ctx(str(p2), {"content": preserved}))), False)

# 7. a Write that edits the Q body → deny
changed = FEATURE.replace("Gmail or Fastmail", "Gmail, Fastmail, or Proton")
check("a Write that changes the managed region is denied",
      denied(body05(Ctx(str(p2), {"content": changed}))), True)

# 8. a Write that DROPS the whole region (the Lumen F002 loss) → deny
dropped = re.sub(r"## Open Questions.*?## Recovery note", "## Recovery note",
                 FEATURE, flags=re.S)
assert "Q2" not in dropped
check("a Write that drops the managed region is denied (the Lumen loss)",
      denied(body05(Ctx(str(p2), {"content": dropped}))), True)

# 9. a Write that only QUOTES the heading inline, on a doc with no real region → allow
p3 = temp_feature(body="# F009 — Note\norient\n\n## Body\nno managed region here.\n",
                  name="F009 — Note.md")
quoting = "# F009 — Note\norient\n\n## Body\nmentions ## Open Questions in prose.\n"
check("a doc with no on-disk region is not protected by a prose mention",
      denied(body05(Ctx(str(p3), {"content": quoting}))), False)

# 10. doc CREATION (target does not yet exist) is exempt
ghost = pathlib.Path(tempfile.mkdtemp()) / "F050 — New.md"
check("creating a new feature doc is exempt (target not on disk)",
      denied(body05(Ctx(str(ghost), {"content": FEATURE}))), False)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
