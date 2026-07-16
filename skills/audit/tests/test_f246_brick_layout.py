"""Regression tests for SKA F246 — question-option layout ("no inline brick").

The written-surface floor already exists: an agent that packs a question's
options and Recommendation inline as one paragraph "brick" is caught by the
existing ask-format checks, and a properly-stacked question (each labeled option
on its own sub-bullet, Recommendation OUTDENTED to the question's own level per
C10) passes clean. These tests lock that floor so a future refactor cannot
silently drop it:

  - inline options `(A) x (B) y` in the Q header    → C8 (inline prose alternatives)
  - inline `Recommendation: ...` (not its own bullet) → C9 (missing Recommendation)
  - the canonical stacked form                       → no C8 / C9 / C19 / C20

Run with:  python3 -m pytest ~/.claude/skills/audit/tests/test_f246_brick_layout.py
"""

import pathlib
import subprocess
import sys

_AUDIT_Q = pathlib.Path(__file__).parent.parent / "scripts" / "audit-q.py"

_HEAD = (
    "---\ndescription: fixture\n---\n\n"
    "# [[SKA]] · F999 — Fixture\none-line orientation.\n\n"
    "## Open Questions\n<!-- state:q 00 -->\n\n"
)
_TAIL = "\n## Summary\nx\n\n## Status\nQuestions — test.\n"

# The failure the user observed (2026-07-16): options AND the recommendation
# packed inline into the question's prose instead of each on its own line.
BRICK_Q = (
    "- **Q1 — Which suffix?** — context here. (A) bare nouns — no suffix "
    "(B) -Mode suffix — verbose. Recommendation: Lean (A) — matches F090. ^F999-Q1\n"
)

# The canonical stacked form: each option its own labeled sub-bullet, and the
# Recommendation OUTDENTED to the question's level (C10), not nested under options.
STACKED_Q = (
    "- **Q1 — Which suffix?** — context here. ^F999-Q1\n"
    "  - **(A)** bare nouns — no suffix.\n"
    "  - **(B)** -Mode suffix — verbose.\n"
    "- **Recommendation:** Lean (A). matches F090.\n"
)


def _audit(tmp_path, body):
    doc = tmp_path / "fixture.md"
    doc.write_text(_HEAD + body + _TAIL, encoding="utf-8")
    res = subprocess.run(
        [sys.executable, str(_AUDIT_Q), "--scope", "feature-doc",
         "--feature-doc", str(doc), "--dry"],
        capture_output=True, text=True, timeout=60,
    )
    return res.stdout + res.stderr


def test_inline_brick_options_flagged_by_c8(tmp_path):
    out = _audit(tmp_path, BRICK_Q)
    assert " C8 " in out, f"expected C8 (inline options) — got:\n{out}"


def test_inline_brick_recommendation_flagged_by_c9(tmp_path):
    out = _audit(tmp_path, BRICK_Q)
    assert " C9 " in out, f"expected C9 (missing Recommendation bullet) — got:\n{out}"


def test_stacked_form_passes_layout_checks(tmp_path):
    out = _audit(tmp_path, STACKED_Q)
    for code in (" C8 ", " C9 ", " C19 ", " C20 "):
        assert code not in out, f"stacked form should not trip{code}— got:\n{out}"
