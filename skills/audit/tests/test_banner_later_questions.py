"""Regression test — a `[Questions]` row under `## Later` must surface in the
Q.md banner (SYS bug, 2026-07-16).

The bug: `derive_banner` counted `[Questions]` rows only in the active horizons
(Active/Ready/Now/Next/Legwork), so a `[Questions]` row filed under `## Later`
rendered in the body but was invisible to the banner — the anchor tagged `[A]`
(agent-ready) with `Questions 0`, hiding a live user question. Observed on a
T002 row an agent had just questioned: the backlog showed `[Questions]` while
the banner "said Ready."

Fix: `BODY_RENDERED_HORIZONS_FOR_QUESTIONS` now includes `Later`, so a pending
question surfaces wherever it is filed (overrides the 2026-06-04 "Later
questions invisible to the banner" call, which produced exactly this failure).

Run with:  python3 -m pytest ~/.claude/skills/audit/tests/test_banner_later_questions.py
"""

import importlib.util
import re
import sys
import tempfile
from pathlib import Path

_QR_PATH = Path.home() / ".claude" / "skills" / "audit" / "scripts" / "queries-render.py"
_spec = importlib.util.spec_from_file_location("qr", _QR_PATH)
assert _spec is not None and _spec.loader is not None
qr = importlib.util.module_from_spec(_spec)
sys.modules["qr"] = qr
_spec.loader.exec_module(qr)


def _row(horizon, ident, bracket):
    return qr.Row(line_num=1, raw_line="", horizon=horizon, identifier=ident,
                  is_h3=False, bracket=bracket, body="", arrow_link=None)


def _banner(rows):
    tf = tempfile.NamedTemporaryFile("w", suffix=" Backlog.md", delete=False, dir="/tmp")
    tf.write("# TEST Backlog\n")
    tf.close()
    try:
        return qr.derive_banner("TEST", rows, Path(tf.name), {})
    finally:
        Path(tf.name).unlink(missing_ok=True)


def test_later_questions_row_surfaces_in_banner():
    """A `[Questions]` row under `## Later` counts toward the banner Questions
    total and flips the TAG to a user-actionable state (not pure `[A]`)."""
    banner = _banner([_row("Later", "T002", "Questions"),
                      _row("Now", "F999", "Ready")])
    q = re.search(r"Questions (\d+)", banner)
    tag = re.search(r"# \[([^\]]*)\]", banner)
    assert q and int(q.group(1)) == 1, f"Later [Questions] not counted: {banner}"
    assert tag and "U" in tag.group(1), f"TAG missing user-actionable U: {banner}"


def test_later_only_question_tags_user_actionable():
    """An anchor whose only live row is a Later `[Questions]` tags `[U]`, not
    `[?]` (deferred) — the question is the point, not the horizon."""
    banner = _banner([_row("Later", "T002", "Questions")])
    tag = re.search(r"# \[([^\]]*)\]", banner)
    assert tag and tag.group(1) == "U", f"expected [U], got: {banner}"


if __name__ == "__main__":
    test_later_questions_row_surfaces_in_banner()
    test_later_only_question_tags_user_actionable()
    print("PASS — Later [Questions] rows surface in the banner")
