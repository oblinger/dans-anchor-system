"""Regression tests for SKA F227 — audit-q code-span awareness + B-QFix C41
exemption.

Three tool bugs previously combined to make certain B-QFix rows unclosable:

  1. `_strip_code_spans` used a naive single-backtick toggle → misread
     CommonMark N-backtick spans (``double`` etc.) and left interior exposed.
  2. C37 stripped wiki-links but not code-spans → bare F-numbers inside
     filenames like `~/F006-status.md` false-fired.
  3. C41 required `Next:` on the B-QFix machinery row, which is authored by
     --fix itself; a user-added Next: would be clobbered on next --fix pass.

Run with:  python3 -m pytest ~/.claude/skills/audit/tests/test_code_span_awareness.py
"""

import importlib.util
import pathlib
import sys
import textwrap

# Load audit-q.py as a module (hyphenated filename ⇒ can't `import` directly).
_AUDIT_Q_PATH = pathlib.Path(__file__).parent.parent / "scripts" / "audit-q.py"
_spec = importlib.util.spec_from_file_location("audit_q", _AUDIT_Q_PATH)
assert _spec is not None and _spec.loader is not None
audit_q = importlib.util.module_from_spec(_spec)
sys.modules["audit_q"] = audit_q
_spec.loader.exec_module(audit_q)


# ---------------------------------------------------------------------------
# Bug 1 — _strip_code_spans honors N-backtick spans
# ---------------------------------------------------------------------------

def test_strip_single_backtick_span_blanks_interior():
    line = "text `code` more"
    out = audit_q._strip_code_spans(line)
    assert "code" not in out
    assert "text" in out and "more" in out


def test_strip_double_backtick_span_blanks_interior():
    """The failure mode that self-jammed B-QFix on SYS: `_backtick_wiki_links`
    wrapped a single-backticked wiki-link with an outer pair, producing a
    ``[[F006]]`` double-backtick span. The naive stripper opened+closed on the
    first two backticks and left the wiki-link inside exposed to C22."""
    line = "e.g. ``[[F006 — Title|F006]]`` and text"
    out = audit_q._strip_code_spans(line)
    assert "[[F006" not in out, f"double-backtick span leaked: {out!r}"
    assert "e.g." in out
    assert "and text" in out


def test_strip_triple_backtick_span_blanks_interior():
    line = "run ```code with `nested` inside``` and go"
    out = audit_q._strip_code_spans(line)
    assert "code" not in out
    assert "nested" not in out
    assert "run" in out and "and go" in out


def test_strip_unclosed_span_leaves_from_open_onward():
    """Unmatched opening run: blank nothing (no confident span boundary)."""
    line = "text ``unclosed and more"
    out = audit_q._strip_code_spans(line)
    # Behavior: we can't identify the span; leave from opening backtick alone.
    # The critical invariant is that we don't blank arbitrary trailing text.
    assert "text " in out


def test_strip_mismatched_lengths_dont_pair():
    """Opening 1-run doesn't close on a 2-run."""
    line = "a `code`` still open"
    out = audit_q._strip_code_spans(line)
    # The 1-backtick opens; the next 1-backtick (first of the ``) closes.
    # Interior "code" gets blanked; the trailing backtick + " still open" remain.
    assert "code" not in out
    assert "still open" in out


def test_strip_no_backticks_is_identity():
    line = "plain text with no code"
    assert audit_q._strip_code_spans(line) == line


# ---------------------------------------------------------------------------
# Bug 2 — C37 ignores bare F-numbers inside code spans
# ---------------------------------------------------------------------------

def _make_queries_md(tmp_path, body: str) -> pathlib.Path:
    """Build a minimal `<anchor>/<anchor> Track/<anchor> queries.md` file for
    the queries.md scope. audit-q is picky about the surrounding structure."""
    anchor_dir = tmp_path / "TEST"
    track = anchor_dir / "TEST Track"
    track.mkdir(parents=True)
    (anchor_dir / ".anchor").write_text("")
    qfile = track / "TEST queries.md"
    qfile.write_text(body)
    return qfile


def test_c37_ignores_bare_fnum_in_backtick_span(tmp_path):
    """A queries.md whose Verifications item has `~/F006-status.md` inside
    single-backticks should NOT trigger C37 (the F006 is in a code span,
    not a bare reference)."""
    body = textwrap.dedent("""\
        ---
        description: test queries
        ---

        # TEST

        ## Verifications
        - **V1** [[F007 — Some Doc]] — the file `~/F006-status.md` is emitting. · **yes / no**
    """)
    qfile = _make_queries_md(tmp_path, body)
    findings = audit_q.check_q_answer_sections([qfile])
    c37 = [f for f in findings if f.code == "C37"]
    assert c37 == [], f"C37 wrongly fired on backticked F-number: {c37}"


def test_c37_still_fires_on_actually_bare_fnum(tmp_path):
    """Regression the other way — the fix must not blind C37 to real bare
    F-numbers outside code spans."""
    body = textwrap.dedent("""\
        ---
        description: test queries
        ---

        # TEST

        ## Verifications
        - **V1** [[F007 — Some Doc]] — see F006 (bare, no link). · **yes / no**
    """)
    qfile = _make_queries_md(tmp_path, body)
    findings = audit_q.check_q_answer_sections([qfile])
    c37 = [f for f in findings if f.code == "C37"]
    assert len(c37) == 1, f"expected 1 C37 for bare F006, got: {c37}"
    assert "F006" in c37[0].message


# ---------------------------------------------------------------------------
# Bug 3 — C41 exempts B-QFix
# ---------------------------------------------------------------------------

def _make_backlog(tmp_path, body: str) -> pathlib.Path:
    anchor_dir = tmp_path / "TEST"
    track = anchor_dir / "TEST Track"
    track.mkdir(parents=True)
    (anchor_dir / ".anchor").write_text("")
    bfile = track / "TEST Backlog.md"
    bfile.write_text(body)
    return bfile


def test_c41_exempts_b_qfix_ready_without_next(tmp_path):
    """A backlog with `- **B-QFix — QFix** [Ready]` and NO `Next:` sub-bullet
    must produce zero C41 findings — it's a machinery row, not a real Ready."""
    body = textwrap.dedent("""\
        ---
        description: test backlog
        ---

        # TEST Backlog

        ## Ready

        - **B-QFix — QFix** [Ready] — audit q findings routed by --fix. ^B-QFix
          - **C22** somewhere.md:1 — some finding text
    """)
    bfile = _make_backlog(tmp_path, body)
    entries = audit_q.parse_backlog(bfile)
    findings = audit_q.check_c41_soak_question_declared(entries, bfile)
    c41 = [f for f in findings if f.code == "C41"]
    assert c41 == [], f"C41 wrongly fired on exempt B-QFix: {c41}"


def test_c41_still_fires_on_ordinary_ready_without_next(tmp_path):
    """C41 must still catch a real [Ready] row that's missing `Next:`."""
    body = textwrap.dedent("""\
        ---
        description: test backlog
        ---

        # TEST Backlog

        ## Ready

        - **F001 — Some real feature** [Ready] — → [[F001 — Doc]] ^F001
    """)
    bfile = _make_backlog(tmp_path, body)
    entries = audit_q.parse_backlog(bfile)
    findings = audit_q.check_c41_soak_question_declared(entries, bfile)
    c41 = [f for f in findings if f.code == "C41"]
    assert len(c41) == 1, f"expected 1 C41 for F001 missing Next:, got: {c41}"
    assert "F001" in c41[0].message
