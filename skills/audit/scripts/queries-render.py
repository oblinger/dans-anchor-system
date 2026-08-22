#!/usr/bin/env python3
"""queries-render.py — rewrite a single anchor's per-anchor section in Q.md.

Usage: queries-render.py <NAME>

Reads `<vault>/<...>/<NAME> Backlog.md`, derives the canonical Q.md section
(banner + body H2s + bullets), and atomically replaces the existing section
in `<vault>/Q.md`. The new section is bubbled to the top of Q.md's body
(immediately after the YAML frontmatter).

If the anchor has zero items anywhere (TAG `[]` + Icebox 0), the section is
removed from Q.md entirely.

Per F104 — replaces the prose-driven Q.md regeneration in /triage's SKILL.md
with one mechanical script that every consumer skill shells out to.

Exit codes:
  0 — section written or removed
  1 — anchor name not found / backlog not found
  2 — Q.md not found / not writable
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# --- Warden self-fire (fork 9 option A, 2026-07-13) -------------------------
# Script-written files bypass Warden's PostToolUse hook (agent tool calls
# only), so writer scripts report their own writes through the same dispatch
# path. Best-effort: Warden off/uninstalled means silence; never raises.
try:
    import importlib.util as _wsf_il
    _WSF_PATH = ((Path.home() / ".claude" / "skills").resolve().parent
                 / "warden" / "engine" / "warden_selffire.py")
    _wsf_spec = _wsf_il.spec_from_file_location("warden_selffire", _WSF_PATH)
    _warden_selffire = _wsf_il.module_from_spec(_wsf_spec)
    _wsf_spec.loader.exec_module(_warden_selffire)
except Exception:
    _warden_selffire = None


def _selffire(path):
    """Report a just-written markdown file to Warden (best-effort)."""
    if _warden_selffire is not None:
        _warden_selffire.fire_write(path)
# ---------------------------------------------------------------------------



# ============================================================
# Load audit-q.py for parsing utilities (hyphenated filename
# blocks plain `import`).
# ============================================================

_AUDIT_Q_PATH = Path.home() / ".claude" / "skills" / "audit" / "scripts" / "audit-q.py"
# Reuse an already-loaded audit_q rather than re-executing it. This block used
# to exec unconditionally and overwrite `sys.modules["audit_q"]`, so any caller
# that had loaded audit-q first ended up holding a DIFFERENT module object than
# this one — two live copies of the same 6k-line module, with two copies of
# every class predicate. Harmless while nothing compared them by identity, and
# invisible for the same reason. F305 made the classes shared state, so the
# duplicate would have quietly restored the very split it was removing.
def _same_file(a, b) -> bool:
    """Path equality by identity on disk, not by string. `~/.claude/skills` is
    a symlink into the DAS repo, so the same file has at least two spellings
    and a string compare would re-exec the module every time."""
    try:
        return a is not None and Path(a).resolve() == Path(b).resolve()
    except OSError:
        return False


_loaded = sys.modules.get("audit_q")
if _loaded is not None and _same_file(getattr(_loaded, "__file__", None), _AUDIT_Q_PATH):
    audit_q = _loaded
else:
    _spec = importlib.util.spec_from_file_location("audit_q", _AUDIT_Q_PATH)
    assert _spec is not None and _spec.loader is not None, f"cannot load {_AUDIT_Q_PATH}"
    audit_q = importlib.util.module_from_spec(_spec)
    sys.modules["audit_q"] = audit_q  # required so @dataclass can resolve the module
    _spec.loader.exec_module(audit_q)

LinkEntry = audit_q.LinkEntry
BacklogEntry = audit_q.BacklogEntry
LIVE_HORIZON_H2S = audit_q.LIVE_HORIZON_H2S
HORIZON_RANK = audit_q.HORIZON_RANK


def _by_horizon(rows):
    """Rows in canonical horizon priority, stable within a horizon (T091).

    The renderer took its order from raw FILE POSITION, so a `## Later` row rendered
    above a `## Next` row whenever a backlog's horizon H2s sat out of order. That is
    latent rather than loud only by luck of the corpus — [[T076]] measured 33 of 34
    backlogs carrying `Now -> Next -> Later` contiguous and correctly ordered, and
    fixed the one file that was scrambled. Fixing the file did not fix the renderer,
    which still has no idea what the priority IS.

    Sorting is stable, so within one horizon the author's deliberate ordering is
    preserved — only the between-horizon order is imposed. Unknown horizons sort
    last rather than raising: a new H2 should not crash the render of an existing
    queue, and it lands where an unrecognised bucket belongs anyway.
    """
    return sorted(rows, key=lambda r: HORIZON_RANK.get(r.horizon, len(HORIZON_RANK)))
ACTIVE_HORIZONS_BANNER = {"Active", "Ready", "Now", "Next", "Legwork"}
# Banner `Questions` total counts `[Questions]` rows ONLY in active horizons
# (matches ACTIVE_HORIZONS_BANNER above) — `## Later` is deferred by user
# intent and shouldn't pull weight in the headline number. Per user direction
# 2026-06-04 (final, reaffirmed 2026-07-16): Later [Questions] are visible in
# the body (rendered under ## Later for context) but invisible to the banner
# count. (The banner never includes Later in Ready or Questions.)
BODY_RENDERED_HORIZONS_FOR_QUESTIONS = ACTIVE_HORIZONS_BANNER

# ============================================================
# Configuration
# ============================================================

VAULT_ROOT = audit_q._resolve_vault_root()
Q_MD = VAULT_ROOT / "Q.md"

# ============================================================
# Regexes (some overlap with audit-q.py; kept local so this
# script's behavior is auditable in one file)
# ============================================================

# Bullet row opener: `- **F091 — Title**` or `- **B-name — Title**`.
# Identifier grammar: F091 / T007 / B-QFix / DMUX-F034, plus dotted roadmap-task
# handles like R-Scaffolding.5.2 (name-path with numeric sub-levels).
_ID = r"[A-Za-z][A-Za-z0-9_\-]*(?:\.[A-Za-z0-9_\-]+)*"

ROW_OPENER_BULLET_RE = re.compile(
    r"^- \*\*"
    r"(?:\[\[)?"
    r"(?:\[[A-Z]+\]\s+)?"
    r"(" + _ID + r")\b"
)

# H3 row opener (HA-style): `### F068 — Title [Bracket]` or `### BUG — Title [Bracket]`.
ROW_OPENER_H3_RE = re.compile(
    r"^### "
    r"(?:\[[A-Z]+\]\s+)?"
    r"(" + _ID + r")\b"
)


def _anchor_of(identifier: str) -> str:
    """Obsidian block-anchor for a row identifier — dots→dashes, matching
    backlog-edit `render_row` (`^id` anchors allow only [\\w-]). No-op for the
    dot-free F/T/B ids; only dotted R handles (R-Scaffolding.5.2) change."""
    return re.sub(r"[^\w\-]", "-", identifier)

H2_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")

# Bracket extraction — allow leading digit (`[4 Questions]`) and any non-bracket
# char inside (so `[Done 2026-06-01 — superseded by F094]` matches).
BRACKET_RE = re.compile(r"\[([A-Za-z0-9][^\[\]]*?)\]")

# Wiki-link
WIKI_LINK_RE = re.compile(r"\[\[([^\[\]]+)\]\]")

# Arrow-trailing link `→ [[X]]`
ARROW_LINK_RE = re.compile(r"→\s*\[\[([^\[\]]+)\]\]")

# Trailing block-ID `^F104`
TRAILING_BLOCK_ID_RE = re.compile(r"\s+\^[A-Za-z][A-Za-z0-9_\-]*\s*$")

# Q.md banner line for an anchor
QMD_BANNER_RE_TEMPLATE = (
    # H1 banner detection. Matches the section's H1 regardless of which target
    # the fallback chain landed on — `[[{slug} queries|{slug}]]`, `[[{slug} Triage|{slug}]]`,
    # `[[{slug}|{slug}]]`, or plain `{slug}` (no link). The display label is
    # always `{slug}`; that's what we match on. Critical for the dedupe step:
    # without this, a fresh regen at the top wouldn't recognize an older OLD
    # header with a different link target, leaving the OLD section orphaned.
    r"^# \[[^\]]*\]\s+(?:\[\[[^|\]]+\|" r"{name}" r"\]\]|" r"{name}" r")(?:\s|$)"
)

# ============================================================
# Parsing
# ============================================================


def _strip_code_spans(line: str) -> str:
    return re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), line)


def _find_separator_outside_wikilinks(text: str) -> int:
    """Return the index *after* the first ` — ` separator in `text` that lies
    outside any `[[...]]` wiki-link, or -1 if no such separator exists.

    Why: backlog rows commonly use ` — ` as the title/body separator AND
    contain wiki-links like `[[F037 — Programmable Permissions Bootstrap]]`
    whose internal em-dash matches the separator pattern. A naive `re.search`
    picks the link-internal one and corrupts the parsed body.
    """
    # Mask wiki-link content with spaces (preserves indices) then search.
    masked = re.sub(r"\[\[[^\[\]]*\]\]", lambda m: " " * len(m.group(0)), text)
    m = re.search(r"\s+—\s+", masked)
    return m.end() if m else -1


def _extract_bullet_bracket(line: str) -> str:
    """Bracket from a bullet row: lives immediately after the title bold close,
    optionally preceded by a `[TYPE]` prefix. Returns '' if absent.

    Anchored to the start of post-title so body brackets can't false-positive.
    Note: BRACKET_RE allows em-dash inside the bracket, so brackets like
    `[Done 2026-06-01 — superseded by F094]` extract correctly."""
    cleaned = _strip_code_spans(line)
    cleaned = re.sub(r"\[\[[^\[\]]*\]\]", lambda m: " " * len(m.group(0)), cleaned)
    title_match = re.match(r"^- \*\*[^*]+\*\*", cleaned)
    if not title_match:
        return ""
    post_title = cleaned[title_match.end():]
    m = re.match(
        r"^\s*(?:\[[A-Z]+\]\s+)?"            # optional `[BUG] ` type prefix
        r"\[([A-Za-z0-9][^\[\]]*?)\]",       # workflow bracket
        post_title,
    )
    return m.group(1).strip() if m else ""


def _extract_h3_bracket(line: str) -> str:
    """Bracket from an H3 row: lives at the END of the line.
    `### F068 — Title [Done 2026-06-02]` → 'Done 2026-06-02'."""
    cleaned = _strip_code_spans(line)
    cleaned = re.sub(r"\[\[[^\[\]]*\]\]", lambda m: " " * len(m.group(0)), cleaned)
    # Last bracket on the line
    matches = list(BRACKET_RE.finditer(cleaned))
    return matches[-1].group(1).strip() if matches else ""


@dataclass
class Row:
    """A parsed backlog row (bullet OR H3)."""
    line_num: int            # 1-indexed
    raw_line: str            # the full source line (no trailing newline)
    horizon: str             # ## H2 the row is under (e.g., 'Now', 'Verify')
    identifier: str          # e.g., 'F091', 'B-roots-reconcile'
    is_h3: bool              # True if H3-style, False if bullet
    bracket: str             # the workflow-state bracket, e.g., 'Ready', '4 Questions'
    body: str                # text after the em-dash separator (bullet) or after the title (H3)
    arrow_link: Optional[str]  # the basename inside `→ [[X]]`, if present


def parse_backlog(backlog_file: Path) -> list[Row]:
    """Parse a backlog file into a flat list of Row objects in source order.

    Handles two row formats:
    - **Bullet-style** (most anchors): `- **F<n> — Title** [Bracket] — body`.
    - **H3-style** (HA): `### F<n> — Title [Bracket]` followed by paragraph
      text and sub-bullets that belong to the H3 row's body (not separate rows).
    """
    try:
        text = backlog_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    lines = text.splitlines()
    rows: list[Row] = []
    current_horizon = ""
    inside_h3_body = False  # True after an H3 row until next H2/H3 — suppresses bullets
    for line_num, line in enumerate(lines, start=1):
        m = H2_HEADING_RE.match(line)
        if m:
            current_horizon = m.group(1).strip()
            inside_h3_body = False
            continue
        if not current_horizon:
            continue
        # H3 row?
        m3 = ROW_OPENER_H3_RE.match(line)
        if m3:
            identifier = m3.group(1)
            bracket = _extract_h3_bracket(line)
            # Body for H3 rows: everything after the H3 heading content's em-dash.
            # `### F068 — Title [Bracket]` — body is just "Title" (no extended prose
            # on the same line). For HA, prose lives in sub-bullets below.
            header_text = line[len("### "):].rstrip()
            # Strip trailing bracket
            header_text = re.sub(r"\s*\[[^\]]+\]\s*$", "", header_text)
            # Split on first ' — '
            em_split = re.split(r"\s+—\s+", header_text, maxsplit=1)
            body = em_split[1] if len(em_split) == 2 else ""
            rows.append(Row(
                line_num=line_num,
                raw_line=line,
                horizon=current_horizon,
                identifier=identifier,
                is_h3=True,
                bracket=bracket,
                body=body,
                arrow_link=_pick_arrow_link(line, identifier),
            ))
            inside_h3_body = True
            continue
        # Bullet row? Suppress when we're inside an H3 row's body — those
        # bullets are sub-content of the H3, not separate rows.
        #
        # **Sibling-detection escape** (2026-06-04, observed on HA): in some
        # conventions, top-level `- **F<n> — Title** [Bracket]` rows appear
        # AFTER H3 rows in the same H2 as *siblings* of the H3, not as its
        # children — e.g., HA's `## Now` has `### BUG — ...` followed by
        # `- **F079 — ...** [4 Questions]`. The distinguishing signal: real
        # rows carry a workflow-state bracket (`[Active]` / `[Ready]` /
        # `[N Questions]`/…); H3-body Q-sub-bullets like `- **Q1 — title?**`
        # don't. When we see a top-level bullet WITH a workflow-state
        # bracket, treat it as a sibling row — exit the H3-body context.
        if inside_h3_body:
            if line.startswith("- **") and _extract_bullet_bracket(line):
                inside_h3_body = False
            else:
                continue
        mb = ROW_OPENER_BULLET_RE.match(line)
        if mb:
            identifier = mb.group(1)
            bracket = _extract_bullet_bracket(line)
            # Body: everything after the FIRST ` — ` separator that occurs
            # AFTER the closing `**` of the title AND outside any wiki-link.
            # Wiki-links like `[[F037 — Programmable Permissions Bootstrap]]`
            # contain ` — ` inside; without skipping link content, the parser
            # picks the link-internal separator and corrupts the body with
            # link-trailing fragments (observed 2026-06-04 on MUX F037 row).
            title_match = re.match(r"^- \*\*[^*]+\*\*", line)
            if title_match:
                post_title = line[title_match.end():]
                sep_idx = _find_separator_outside_wikilinks(post_title)
                body = post_title[sep_idx:] if sep_idx >= 0 else ""
            else:
                body = ""
            body = TRAILING_BLOCK_ID_RE.sub("", body)
            rows.append(Row(
                line_num=line_num,
                raw_line=line,
                horizon=current_horizon,
                identifier=identifier,
                is_h3=False,
                bracket=bracket,
                body=body,
                arrow_link=_pick_arrow_link(line, identifier),
            ))
    return rows


# ============================================================
# Banner derivation
# ============================================================
# This header read "mirrors audit_q.derive_anchor_banner" until F305. It did,
# and that was the defect: two copies of the class logic and two copies of the
# format string, each self-consistent and therefore each invisible to the
# other. The classes and the format string are now `audit_q`'s alone and are
# imported below; what stays here is only what genuinely differs — this module
# scopes zone 1 by the render predicate (so banner and body cannot disagree)
# and appends the QFix residual suffix.


def _row_basename_is_own_doc(basename: str, identifier: str) -> bool:
    """Does `basename` name the doc belonging to row `identifier`?

    T581. This delegates to `audit_q`'s regexes rather than re-stating the
    rule, because the rule is that **three naming conventions coexist in the
    vault permanently** and any local copy of it goes stale the moment a
    fourth appears:

        F332 — Title        legacy, everything before 2026-08-02
        TINK F332 - Title   F298, the one morning that convention lasted
        TINK332 - Title     F300, current — the kind letter is DROPPED

    What this replaced was `basename.startswith(f"{identifier} ")`, a test
    written against the legacy form — the only one of the three that puts the
    row's identifier at the head of the filename. Under F298 and F300 it
    matches NOTHING, so every row minted since 2026-08-02 failed the own-doc
    test and fell through to the caller's `matches[0]` fallback. That is
    invisible almost everywhere, because on most rows the first arrow IS the
    own-doc arrow — which is exactly why it survived: the fallback and the
    correct answer agree until a row mentions another doc first.

    `audit_q` hit this same stale test as `_basename_is_own_doc` and fixed it
    2026-08-19, after C57 false-fired on eight migrated rows and C24/C48/C50
    turned out to have been silently passing on them for the same reason. The
    fix was never propagated here; this is that propagation.

    ONE DELIBERATE DIFFERENCE from audit_q's version: the fused form carries no
    kind letter, so `TINK575` is ambiguous between T575 and F575, and audit_q
    resolves it by reading the target doc's H1. There is no resolved path at
    pick time here, so the number match stands alone — which audit_q's own
    docstring already licenses for its unresolved-link case: *slug+number is
    unique within an anchor by construction*.
    """
    want = audit_q._ROW_ID_RE.match(identifier or "")
    if not want:
        return False
    letter, number = want.group(1).upper(), int(want.group(2))
    m = audit_q._OWN_DOC_LETTERED_RE.match(basename)
    if m:
        return m.group(1).upper() == letter and int(m.group(2)) == number
    m = audit_q._OWN_DOC_FUSED_RE.match(basename)
    return bool(m) and int(m.group(1)) == number


def _pick_arrow_link(line: str, identifier: str) -> Optional[str]:
    """T012: choose the row's OWN doc among its `→ [[…]]` links — prefer the
    LAST one whose basename names the row's own doc, else the FIRST arrow
    link. A plain first-match (the old `ARROW_LINK_RE.search`) picks a prose
    arrow on rows like F149 whose own-doc arrow trails several prose arrows;
    plain last-match fails on F220-style rows with a prose arrow after the
    own-doc one.

    T581 — CODE SPANS ARE STRIPPED FIRST, and that is not a nicety. A backlog
    row may *write about* the pointer syntax, and rows about the backlog
    machinery routinely do: T578's body says `--body` is discarded "when the
    row carries a `→ [[doc]]` pointer". Scanning the raw line read that
    illustration as T578's own pointer and rendered a dead `[[doc]]` link on
    [[TINK queries]] where the row's identity belongs — on the surface Dan
    reads, not in a log. `backlog-edit.py`'s F102 gate warns about this exact
    hazard in its refusal text and audit-q's C57 strips spans before the same
    scan; this was the one reader that did not.
    """
    # Decide on the STRIPPED line, but return text sliced from the ORIGINAL.
    # `_strip_code_spans` replaces each span with an equal number of spaces, so
    # the two strings are the same length and a match's offsets mean the same
    # thing in both — which is the whole reason it pads instead of deleting.
    #
    # Slicing the stripped text instead would blank any code span inside a
    # link's DISPLAY ALIAS, and rows carry those: ATT's F054 alias is
    # ``F054 — `bridge run`: unattended remote work…``, which came back with
    # eleven spaces where the command name belongs. Caught by diffing the old
    # picker against the new one across every backlog in the vault before
    # shipping — it was the only row of 3 that changed for the wrong reason.
    stripped = _strip_code_spans(line)
    matches = [line[m.start(1):m.end(1)] for m in ARROW_LINK_RE.finditer(stripped)]
    if not matches:
        return None
    own = [m for m in matches
           if _row_basename_is_own_doc(
               m.split("#")[0].split("|")[0].strip(), identifier)]
    return own[-1] if own else matches[0]


def _read_q_marker_count(target_path: Path) -> int:
    """Count PENDING Q-markers only — skip anything inside a Resolved section
    (`## Resolved` H2 or `### Resolved` H3, case-insensitive), mirroring
    audit-q's extract_q_entries gate. Counting the whole file over-reported
    docs that archive answered Qs at the bottom (F171 bug, 2026-07-02)."""
    try:
        lines = target_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return 0
    count = 0
    in_h2_resolved = False
    in_h3_resolved = False
    for line in lines:
        if line.startswith("## "):
            in_h2_resolved = line[3:].strip().lower().startswith(("resolved", "removed"))
            in_h3_resolved = False
            continue
        if line.startswith("### "):
            tail = line[4:].strip()
            in_h3_resolved = tail.lower().startswith(("resolved", "removed"))
            # The H3 Q shape `state q` writes (`### Q1 — …`) counts as pending
            # unless it sits under a Resolved H2 (2026-07-06 — H3-form docs
            # rendered no (NQ) count at all) or carries an archive marker —
            # `### Q5 — … (removed …)` is a record, not a pending Q (T024).
            if re.match(r"Q\d+\s+—", tail) and re.search(
                    r"\((?:removed|resolved)\b", tail, re.IGNORECASE):
                in_h3_resolved = True
                continue
            if not in_h2_resolved and not in_h3_resolved and re.match(r"Q\d+\s+—", tail):
                count += 1
            continue
        if in_h2_resolved or in_h3_resolved:
            continue
        if re.match(r"\s*-\s+\*\*Q\d+\s+—", line):
            count += 1
    return count


def _option_gloss(rest: str, cap: int = 58) -> str:
    """The shortest phrase that says what an option IS.

    An ask-format option reads `- **(A)** **Bracket becomes DERIVED** — computed
    from the open items…`: a bolded short name, then the argument. The bolded
    name is the gloss when it exists — it was written to be the option's handle.
    Otherwise take the head of the prose up to the first sentence or clause
    break, so the gloss ends on a word rather than mid-thought. The cap applies
    to both, on a word boundary: three options plus the question stem share one
    line, and an option nobody finishes reading is no better than one that was
    never printed."""
    m = re.match(r"\s*\*\*(.+?)\*\*", rest)
    head = (m.group(1) if m else
            re.split(r"\s+—\s+|(?<=[.;])\s+", rest.strip(), maxsplit=1)[0])
    head = head.strip()
    if len(head) > cap:
        head = head[:cap].rsplit(" ", 1)[0] + "…"
    return head.rstrip(".").strip()


def _read_open_questions(target_path: Path) -> list[tuple[str, str, str, list]]:
    """Pending open questions as (qid, question_text, recommendation, options) —
    mirrors _read_q_marker_count's pending gate but captures the human-facing
    text so the queue file can LIST the actual questions inline (user
    2026-07-18: a bare `(NQ)` badge is unreadable — the questions themselves
    must be visible in Q.md, exactly like the Verifications section shows each
    verify's text).

    `options` is [(label, gloss)] read from the Q's `- **(A)**` sub-bullets.
    T130: the render used to carry the question stem and the Recommendation and
    drop the options entirely, so a question whose content IS its options came
    out as a stem, an ellipsis, and a bare `Lean **(B)**` naming a choice the
    reader could not see. Showing a lean for an invisible option is worse than
    showing neither — it reads as a decision already made, about nothing."""
    try:
        lines = target_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    out: list[tuple[str, str, str, list]] = []
    in_resolved = False
    cur_id = cur_text = cur_rec = ""
    cur_opts: list[tuple[str, str]] = []

    def flush():
        nonlocal cur_id, cur_text, cur_rec, cur_opts
        if cur_id:
            out.append((cur_id, cur_text.strip(), cur_rec.strip(), cur_opts))
        cur_id = cur_text = cur_rec = ""
        cur_opts = []

    for line in lines:
        # The resolved zone is `### Resolved` INSIDE the block (F241's two-zone
        # shape) as often as it is a bottom `## Resolved` H2, and only the H2
        # form was recognized — so on a doc using the in-block form the scanner
        # never left the pending zone and kept accreting onto the last pending
        # Q. Latent until T130 started reading option bullets: F303's Q1 came
        # out carrying its own (A)(B)(C) plus resolved Q2's (A)(B)(C)(D).
        if line.startswith("## "):
            flush()
            in_resolved = line[3:].strip().lower().startswith(("resolved", "removed"))
            continue
        if line.startswith("### "):
            # Only an H2 leaves a resolved zone. An H3 inside one is a resolved
            # question's own heading, not an exit — treating it as an exit would
            # re-admit every archived Q whose heading lacks a `(resolved …)`
            # marker, which is a worse failure than the one being fixed.
            if not in_resolved:
                flush()
                if line[4:].strip().lower().startswith(("resolved", "removed")):
                    in_resolved = True
                    continue
        if in_resolved:
            continue
        # bullet-form pending Q: `- **Q10 — Title** — question text ^anchor`
        # The `—` after the bold title is OPTIONAL: `/feature`-authored Qs write
        # `- **Q8 — Title.** How should …` with the body running straight on. The
        # earlier form required the em-dash, so those questions matched nothing
        # and vanished from the render entirely — the row still showed `(2Q)`
        # but never listed a single one. Same fix already applied to
        # `_read_row_inline_questions`; this is its twin.
        m = re.match(r"\s*-\s+\*\*(Q\d+)\s+—\s+(.*?)\*\*\s*(?:—\s*)?(.*)$", line)
        if m:
            flush()
            cur_id = m.group(1)
            title, rest = m.group(2).strip(), (m.group(3) or "").strip()
            rest = re.sub(r"\s*\^\S+\s*$", "", rest)
            # Lead with the TITLE, then the body. The title is where the actual
            # question lives (`**Q8 — Should the cascade become the default?**`);
            # dropping it whenever a body existed meant the rendered line opened
            # on background — "Today `anchor rename` renames only the anchor
            # page…" — and never stated what was being asked. Since the line is
            # truncated to `qlimit`, the question has to come first or it is the
            # part that gets cut.
            cur_text = f"{title} {rest}".strip() if rest else title
            continue
        # H3-form pending Q: `### Q1 — question?`
        m3 = re.match(r"###\s+(Q\d+)\s+—\s+(.*)$", line)
        if m3 and not re.search(r"\((?:removed|resolved)\b", m3.group(2), re.IGNORECASE):
            flush()
            cur_id = m3.group(1)
            cur_text = re.sub(r"\s*\^\S+\s*$", "", m3.group(2)).strip()
            continue
        if cur_id:
            rm = re.match(r"\s*-\s+\*\*Recommendation:\*\*\s*(.*)$", line)
            if rm:
                cur_rec = re.split(r"\s*·\s*\*why-ask", rm.group(1).strip())[0].strip()
                continue
            # Option bullets (C19 shape): `- **(A)** **Short name** — argument`.
            # Captured only between a Q header and the next one, so the
            # Recommendation's own `(B)` reference cannot be mistaken for one.
            om = re.match(r"\s*-\s+\*\*\(([A-Z])\)\*\*\s*(.*)$", line)
            if om:
                cur_opts.append((om.group(1), _option_gloss(om.group(2))))
    flush()
    return out


def _read_row_inline_questions(backlog_file: Path, r: "Row") -> list[tuple[str, str, str, list]]:
    """Pending Qs hosted INLINE in a backlog row's own sub-bullets, as
    (qid, question_text, recommendation, options) — the same shape
    `_read_open_questions` returns for doc-backed rows.

    A row-hosted Q comes in two shapes and both are read. The **packed** form
    puts `**(A)**`/`**(B)**` on the question's own line, so the options are
    already inside the returned text and `options` stays empty — a separate
    option line would print them twice. The **nested** form gives each option
    its own sub-bullet, which is what audit-q C8 requires and therefore what any
    Q authored to pass the checker looks like; those are collected into
    `options` exactly as the doc-hosted reader does.

    T-/B-rows may carry their questions inline (F233) instead of in a feature
    doc. The Questions section used to skip those on the reasoning that such a
    row "carries its Qs in the row body already" — but the body is truncated to
    160 chars before it is rendered, so the Q text was silently dropped and the
    user saw only a `(1Q)` badge with no question attached (Dan, 2026-08-02:
    *"Does T18 have questions? … I can't see the questions here"*). A counted
    but unreadable question is a question that was never actually asked.
    """
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    out: list[tuple[str, str, str, list]] = []
    # Scan the row's sub-bullets: everything indented under the opener, stopping
    # at the next H2, H3, or top-level bullet (the next row).
    for line in lines[r.line_num:]:
        if H2_HEADING_RE.match(line) or line.startswith("### ") or line.startswith("- **"):
            break
        if not line.strip():
            continue
        # A row's `- **Resolved**` sub-bullet opens its resolved zone; every Q
        # below it is archived history, not pending. `backlog-edit.py`'s
        # [Questions] gate (`row_pending_q_lines`) already stops here — this
        # reader didn't, so a resolved row-Q rendered as pending and inflated
        # the (NQ) badge (T197 Q1, found 2026-08-14).
        if re.match(r"\s+-\s+\*\*Resolved\*\*\s*$", line):
            break
        # A row-hosted Q may carry its options as NESTED sub-bullets rather than
        # packed onto the header line — which is what audit-q C8 requires, so it
        # is the shape any Q authored to pass the checker will have. T130 taught
        # the doc-hosted reader to collect these and left this one believing
        # every inline Q packs its options into the text; the result was that a
        # C8-conforming row-Q rendered as a bare stem with no options and no
        # lean, the exact defect T130 existed to fix. Found by using the fix.
        om = re.match(r"\s+-\s+\*\*\(([A-Z])\)\*\*\s*(.*)$", line)
        if om and out:
            out[-1][3].append((om.group(1), _option_gloss(om.group(2))))
            continue
        # A nested `- **Recommendation:**` belongs to the Q above it, same as in
        # the doc-hosted form.
        rm_sub = re.match(r"\s+-\s+\*\*Recommendation:\*\*\s*(.*)$", line)
        if rm_sub and out and not out[-1][2]:
            rec_txt = re.split(r"\s*·\s*\*why-ask", rm_sub.group(1).strip())[0].strip()
            qid_, txt_, _, opts_ = out[-1]
            out[-1] = (qid_, txt_, rec_txt, opts_)
            continue
        # `  - **Q1 — title?** rest…` — the rest may follow directly with no
        # em-dash separator (the inline form packs context + options + the
        # recommendation onto the one line), so the tail is captured either way.
        m = re.match(r"\s+-\s+\*\*(Q\d+)\s+—\s+(.*?)\*\*\s*(?:—\s*)?(.*)$", line)
        if not m:
            continue
        qid = m.group(1)
        title, rest = m.group(2).strip(), (m.group(3) or "").strip()
        rest = re.sub(r"\s*\^\S+\s*$", "", rest)
        text = rest if rest else title
        # An inline Q packs its options and recommendation into the same line.
        # Split the recommendation off so it renders in the same `· *…*` slot
        # doc-backed Qs use, rather than trailing off the end of the truncation.
        rec = ""
        rm = re.search(r"\*\*Recommendation:\*\*\s*(.*)$", text)
        if rm:
            rec = re.split(r"\s*·\s*\*why-ask", rm.group(1).strip())[0].strip()
            text = text[:rm.start()].rstrip()
        # Keep the leading title when the body opened with one — an inline Q's
        # title IS the question ("land the bundle-relative fix?").
        if rest and title and not text.startswith(title):
            text = f"{title} — {text}"
        out.append((qid, text.strip(), rec, []))
    return out


def _row_q_doc_path(r: "Row", vault_index: dict):
    """Resolve the on-disk doc a `[Questions]` row's Qs live in (same resolution
    _row_q_count uses), for reading the question text to inline in the queue."""
    target = r.arrow_link or (r.identifier if r.identifier.startswith("F") else None)
    if not target:
        return None
    target = target.split("#")[0].split("|")[0].strip().lower()
    candidates = vault_index.get(target) or vault_index.get(target + ".md") or []
    if not candidates and r.identifier.startswith("F"):
        fid = r.identifier.lower()
        for bn, paths in vault_index.items():
            if bn.startswith(fid + " —") or bn == fid:
                candidates = paths
                break
    return candidates[0] if candidates else None


def _feature_doc_link(r: "Row", vault_index: dict,
                      backlog_file: Path) -> Optional[str]:
    """Wiki-link to the row's feature doc, else None (F235 — the feature doc is the
    verification's home; V-entries link it first so the queue file never loses the
    path to the feature's context). T-rows and doc-less F-rows return None.

    F-numbers are per-anchor namespaces (F27), so `F220 — …` docs exist in several
    anchors: pick the candidate sharing the longest path prefix with the backlog
    (i.e. this anchor's own doc), and require it to be closer than the vault root."""
    if not r.identifier or not r.identifier.startswith("F"):
        return None
    prefix = r.identifier.lower() + " —"
    candidates: list[Path] = []
    for bn, paths in vault_index.items():
        stem = bn[:-3] if bn.endswith(".md") else bn
        if stem.lower().startswith(prefix):
            candidates.extend(paths)
    if not candidates:
        return None
    bparts = backlog_file.parts

    def common(p: Path) -> int:
        n = 0
        for a, b in zip(bparts, p.parts):
            if a != b:
                break
            n += 1
        return n

    best = max(candidates, key=common)
    # must share more than the vault root with the backlog — else it's another
    # anchor's F<n> doc; fall back to the row-only link rather than mislink.
    anchor_depth = common(best)
    others = [c for c in candidates if c != best]
    if others and anchor_depth <= max(common(c) for c in others):
        return None  # ambiguous — don't guess
    if anchor_depth < len(backlog_file.parts) - 3:
        return None
    return f"[[{best.stem}|{r.identifier}]]"


def _q_home_link(r: "Row", vault_index: dict, backlog_file: Path) -> Optional[str]:
    """Link to the row's Q-bearing DOC — the surface the reader must land on to
    actually see the open questions (user 2026-07-13: following a Questions
    entry's link must end on a document with the open questions at the top;
    the backlog-row link alone fails that). Arrow target first (authoritative
    for Questions rows), else the identifier-matched feature doc. Returns None
    for inline T-/B-rows — there the backlog row IS the Q home and the row
    link is correct."""
    if r.arrow_link:
        bn = r.arrow_link.split("#")[0].split("|")[0].strip()
        if vault_index.get(bn.lower()):
            return f"[[{bn}|{r.identifier}]]"
    return _feature_doc_link(r, vault_index, backlog_file)


def _doc_next_fallback(r: "Row", vault_index: dict,
                       backlog_file: Path) -> Optional[str]:
    """F332 — a derived (pure-link) row carries no `- **Next:**` sub-bullet;
    its Next is the arrow-linked doc's `next::` Dataview field. Resolve the
    doc and read it, sharing the writer's own reader so the render and
    `state` agree on what the field says."""
    if not r.arrow_link:
        return None
    bn = r.arrow_link.split("#")[0].split("|")[0].strip()
    target = audit_q.resolve_target(bn, backlog_file, vault_index)
    if target is None:
        return None
    try:
        return audit_q._be_mod.read_doc_next(target)
    except Exception:
        return None


def _doc_q_anchor(qdoc, q_entries: list) -> Optional[str]:
    """The in-document anchor a Q-bearing link must carry, or None.

    T216 (Dan, 2026-08-11, on F312, the **second** report of the same
    complaint): *"It says F312, one question. But when I click on it, it
    doesn't go to the questions."* T211 had fixed the half it could see — the
    question renders — and left the half nobody had named: the emitted handle
    is `[[TINK312 - …|F312]]`, an unanchored link, so it lands at the top of
    the doc. F312's `## Open Questions` is 33 lines down behind a 28-row Table
    of Contents, so the first screen is entirely TOC and the question is
    invisible *at the place the link delivers you to*. The render already
    holds everything needed to aim better — it prints the question's own text
    beside the link — so the anchor is recoverable, not new information.

    Prefer the exact `^F<n>-Q<n>` block when the row has exactly one pending
    question (lands ON the question), else the `## Open Questions` heading.
    Verified against the doc's real text both times: an anchor that does not
    resolve is worse than none, since Obsidian silently drops the reader at
    the top again with no indication the aim was wrong.
    """
    if not qdoc or not q_entries:
        return None
    try:
        text = qdoc.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if len(q_entries) == 1:
        m = re.search(r"\^([A-Za-z0-9]+-" + re.escape(q_entries[0][0]) + r")(?!\S)",
                      text)
        if m:
            return "#^" + m.group(1)
    # F305: aim at whichever heading the doc ACTUALLY carries — canonical
    # `## Open Items` first, legacy `## Open Questions` second. An anchor
    # naming the wrong spelling silently drops the reader at the top of the
    # doc, which is the exact T216 failure this function exists to fix.
    for head in ("Open Items", "Open Questions"):
        if re.search(r"^##\s+" + head + r"\s*$", text, re.M):
            return "#" + head
    return None


def _with_anchor(link: str, anchor: Optional[str]) -> str:
    """Splice an in-document anchor into an already-emitted wiki-link (T216).

    Kept separate from the link builders because every one of them
    (`_bullet_link`, `_q_home_link`, `_feature_doc_link`) resolves a *target*
    and none of them knows whether the row has questions — the anchor is a
    property of the row's Q state, not of its link. An already-anchored link
    and a plain-text fallback are both returned untouched: aiming a non-link is
    meaningless, and re-aiming a hand-authored `→ [[X#Y]]` would override the
    author.
    """
    if not anchor or not link.startswith("[[") or not link.endswith("]]"):
        return link
    inner = link[2:-2]
    target = inner.split("|", 1)[0]
    if "#" in target:
        return link
    if "|" in inner:
        return f"[[{target}{anchor}|{inner.split('|', 1)[1]}]]"
    # No pipe: add one, so the anchor does not leak into the displayed text
    # as Obsidian's `Doc > Open Questions` form.
    return f"[[{inner}{anchor}|{inner}]]"


def _row_q_count(r: "Row", vault_index: dict, backlog_file=None) -> int:
    """Pending-question count for a `[Questions]` row — the `(NQ)` the user sees.
    Recount from the linked doc when one resolves (T012 — the bracket can be
    stale or corrupted; the doc is ground truth). Fall back to an explicit
    `[N Questions]` bracket only when nothing resolves (T-/B-rows with inline
    Qs, whose bracket C24's fixer maintains from the row's own sub-bullet
    span). Returns 0 when neither is available (no count shown)."""
    target_basename = r.arrow_link or (r.identifier if r.identifier.startswith("F") else None)
    candidates: list = []
    if target_basename:
        # vault_index keys are lower-cased (audit_q.build_vault_index, T002);
        # a case-sensitive get here left the doc-recount path silently dead.
        target_basename = target_basename.split("#")[0].split("|")[0].strip().lower()
        candidates = (vault_index.get(target_basename)
                      or vault_index.get(target_basename + ".md") or [])
        if not candidates and r.identifier.startswith("F"):
            fid = r.identifier.lower()
            for bn, paths in vault_index.items():
                if bn.startswith(fid + " —") or bn == fid:
                    candidates = paths
                    break
    if candidates:
        return _read_q_marker_count(candidates[0])
    m = re.match(r"(\d+)\s+Questions", r.bracket)
    if m:
        return int(m.group(1))
    # Last resort: count the row's OWN inline Qs (F233 form). This used to read
    # `1 if "Questions" in r.bracket else 0` — a bracket test, which made the
    # count disagree with the preview beside it the moment a row carried
    # questions under some other bracket. T213: a `[Ready]` row rendered its
    # question text with NO `(NQ)` badge, because the preview asks the row and
    # the badge asked the bracket. Counting the sub-bullets keeps this function
    # doing what its own docstring says throughout — recount from ground truth,
    # and treat the bracket as the weakest evidence rather than the deciding
    # one. It also stops overstating: a `[Questions]` row whose Qs have all
    # resolved reported 1 forever, since the bracket outlives the questions.
    if backlog_file is not None:
        return len([q for q in _read_row_inline_questions(backlog_file, r) if q[1]])
    return 1 if "Questions" in r.bracket else 0


# ---- F305 visibility classes -------------------------------------------------
# Imported, NOT redefined. These used to be two independent copies — this file
# carried its own class logic and its own banner format string, and said so at
# line 331: *"Banner derivation (mirrors audit_q.derive_anchor_banner)"*. The
# mirror drifted. One definition now lives in `audit_q`, which this module
# already imports; see the block above `audit_q.derive_anchor_banner` for why
# that direction and not the reverse.
_in_class_ready = audit_q.in_class_ready
_in_class_user = audit_q.in_class_user
_in_class_parked = audit_q.in_class_parked
_in_class_hidden = audit_q.in_class_hidden


def derive_banner(name: str, rows: list[Row], backlog_file: Path,
                  vault_index: dict) -> Optional[str]:
    """Compute the H1 banner line. Returns None if anchor has zero items."""
    live = [r for r in rows
            if r.horizon in LIVE_HORIZON_H2S
            and not r.bracket.startswith("Done")]
    # ---- zone 1: visibility classes, scoped to what the BODY renders --------
    # F305: every count is a count of ROWS. Dan, 2026-08-07: *"if I have 10 items
    # that each have one question, I'm much more motivated to answer a bunch of
    # questions since I'm going to unblock a tremendous amount of work. If I had
    # one ticket that had 10 questions, I'm not really very motivated."* The
    # number that drives action is how many things are blocked on the user, not
    # how much answering work is queued — so a row carrying four open questions
    # contributes 1. This replaces the per-`Q<n>` sum `_row_q_count` produced.
    #
    # The scope is `_row_should_render`, i.e. exactly the rows the body lists.
    # It is NOT the active horizons: the body also renders `[Questions]` and
    # `[Verify]` rows under `## Later`, and scoping the banner more narrowly is
    # what made banner and body disagree (MUX 2026-06-04 — banner `Questions 0`
    # while the body listed two). That fix was written as a widened constant,
    # `BODY_RENDERED_HORIZONS_FOR_QUESTIONS`, which was then aliased straight
    # back to `ACTIVE_HORIZONS_BANNER` — so the comment promised the wider scope
    # while the code kept the narrow one, and two live rows (Anchorage F029,
    # Docket F054) were still rendered-but-uncounted on 2026-08-07. Deriving the
    # scope from the render predicate itself is what makes the two agree by
    # construction rather than by a constant somebody has to keep in sync.
    shown = [r for r in live if _row_should_render(r)]
    # Exclude an empty B-QFix (0 residuals) — it's not actionable Ready work.
    _qfix_empty = _count_qfix_subs(backlog_file) == 0
    ready_n = sum(1 for r in shown if _in_class_ready(r.bracket)
                  and not (r.identifier == "B-QFix" and _qfix_empty))
    user_n = sum(1 for r in shown if _in_class_user(r.bracket))
    # ---- zone 3: the quiet classes, unscoped by horizon --------------------
    # Counted precisely BECAUSE they are omitted from the body — a class that
    # appears in no list and no count is invisible everywhere but the raw file.
    parked_n = sum(1 for r in live if _in_class_parked(r.bracket))
    waiting_n = sum(1 for r in live if _in_class_hidden(r.bracket))
    # TAG input only — `verify_n` no longer has a banner slot of its own.
    verify_n = sum(1 for r in live
                   if r.horizon in ACTIVE_HORIZONS_BANNER
                   and _in_class_parked(r.bracket))
    # Per-horizon counts (live, non-Done)
    horizon_counts = {h: 0 for h in ("Active", "Ready", "Now", "Next", "Later", "Verify", "Icebox")}
    for r in rows:
        if r.horizon in horizon_counts and not r.bracket.startswith("Done"):
            horizon_counts[r.horizon] += 1
    # Icebox count from {slug} Icebox.md
    icebox_file = audit_q.backlog_track_dir(backlog_file) / f"{name} Icebox.md"
    if icebox_file.is_file():
        try:
            icebox_text = icebox_file.read_text(encoding="utf-8")
            icebox_count = sum(
                1 for line in icebox_text.splitlines()
                if ROW_OPENER_BULLET_RE.match(line) or ROW_OPENER_H3_RE.match(line)
            )
            horizon_counts["Icebox"] = icebox_count
        except (OSError, UnicodeDecodeError):
            pass
    # TAG cascade. Per F100 every row in `## Verify` is awaiting confirmation,
    # so the Verify horizon counts toward the user-pending signal even though
    # verify_n (banner Questions/Verify, active-horizon-only) is separate.
    has_u = (
        user_n > 0
        or verify_n > 0
        or horizon_counts["Verify"] > 0
    )
    has_a = ready_n > 0
    has_g = horizon_counts["Now"] > 0 or horizon_counts["Next"] > 0
    has_later = horizon_counts["Later"] > 0
    if has_u and has_a:
        tag = "U+A"
    elif has_u:
        tag = "U"
    elif has_a:
        tag = "A"
    elif has_g:
        tag = "G"
    elif has_later:
        tag = "?"
    elif horizon_counts["Icebox"] > 0:
        tag = "-"
    else:
        tag = ""
    if not tag:
        return None
    # Per F176: H1 link target is `{slug} queries.md` (the /query drain page where
    # the user actually answers questions). Fallback chain when files don't
    # exist yet (avoids emitting a C1-failing wiki-link in Q.md):
    #   `{slug} queries` → `{slug} Triage` → `{slug}` (anchor page) → plain text
    candidates = [f"{name} queries", f"{name} Triage", name]
    # vault_index keys are lower-cased (audit_q.build_vault_index, T002) —
    # test lowered, emit original case (T017: the case-sensitive test left
    # every banner on the plain-text fallback, dropping the F176 wiki-link).
    h1_target = next((c for c in candidates if c.lower() in vault_index), None)
    if h1_target:
        slug_label = f"[[{h1_target}|{name}]]"
    else:
        slug_label = name  # plain text — anchor has no clickable target
    # Trailing `{N}` — outstanding audit-q residual count on this anchor's
    # B-QFix row. Per user direction 2026-06-04 (final): show only when
    # N > 0; clean anchors emit no suffix. The signal is noise-only-when-
    # there's-noise — most banners are silent; a `{N}` pops to your eye as
    # the anchors needing attention.
    qfix_n = _count_qfix_subs(backlog_file)
    qfix_suffix = f"    {{{qfix_n}}}" if qfix_n > 0 else ""
    # F305 — THREE ZONES, ORDERED BY ATTENTION. This is the whole design and it
    # is not a taxonomy. Zone 1 = what do I act on. Zone 2 = what is coming.
    # Zone 3 = what am I not looking at.
    #
    # Zone 3 deliberately mixes a horizon (Icebox) in with two classes, and the
    # mix is correct. Dan named it and kept it: *"I know it kind of mixes things
    # up a little bit, but I do think that's the better ordering… The reason is
    # simply visibility."* An editor who later regularizes these into
    # classes-then-horizons will have destroyed the design. A new count goes in
    # the zone matching how much ATTENTION it deserves, never the zone matching
    # what kind of thing it is.
    #
    # `Verify` left zone 2 when it became a class — it is now inside `Parked`,
    # alongside `[Blocked …]`, which had no banner slot at all before this.
    # `Runnable` reverted to `Ready` (F260's word, kept three rounds, reverted
    # on brevity); the class name now collides with the `[Ready]` bracket and
    # that is deliberate — see [[DAS Backlog]] § The state table.
    # `Inbox N` (T131 leg 2) — zone 1, emitted only when N > 0. The count is
    # `audit_q.count_pending_inbox`, shared with `derive_anchor_banner` rather
    # than reimplemented here, so the banner this module renders and the banner
    # audit-q derives cannot disagree about how many entries are pending.
    return audit_q.format_status_banner(
        tag, slug_label,
        ready_n, user_n,
        horizon_counts["Now"], horizon_counts["Next"], horizon_counts["Later"],
        parked_n, waiting_n, horizon_counts["Icebox"],
        qfix_suffix,
        inbox=audit_q.count_pending_inbox(name, backlog_file),
    )


# ============================================================
# Body rendering
# ============================================================

# Brackets that DO get rendered under ## Later (everything else is hidden)
LATER_RENDERED_BRACKETS_PREFIX = ("Questions", "Verify")  # "Verify" matches "Verify" and "Verify-by ..."

_VERIFY_BY_RE = re.compile(r"^Verify-by\s+(\d{4}-\d{2}-\d{2})", re.I)

# F283 — `[Blocked <handle>]` is a typed edge: the handle names the row this one
# waits on. `blocked_grammar_gate` in backlog-edit.py refuses a bare `[Blocked]`
# at the write, but 33 bare rows predate the gate, so the group is optional here
# — a bare row still parses, it just names no edge and promotes nothing.
_BLOCKED_HANDLE_RE = re.compile(
    r"^Blocked\s+([A-Za-z][A-Za-z0-9_\-]*(?:\.[A-Za-z0-9_\-]+)*)\s*$", re.I)

# T551 — a pebble handle, `<SLUG> P<digits>`. Note the SPACE: `_BLOCKED_HANDLE_RE`
# above forbids one inside the handle, so `[Blocked ATT P0004]` matches nothing
# there and names no edge — which is why these rows have always rendered as
# ordinary blocked rows rather than promoting anything. Hyphenated and bare
# forms are accepted too; no backlog row id begins with `P`, so there is nothing
# for a bare `P0004` to be confused with.
_PEBBLE_BLOCKED_RE = re.compile(
    r"^Blocked\s+(?:[A-Za-z][A-Za-z0-9]*[\s\-])?P\d+\s*$", re.I)


def pebble_suppressed_ids(rows: list[Row], name: str) -> set[str]:
    """Row identifiers Q.md must not show — those parked behind a pebble.

    Dan, 2026-08-18: *"There shouldn't be any references to things blocked on
    pebbles that are visible to me."* Under the umbrella-pebble model a pebble
    is a cohesive chunk of work and the rows belonging to it hang off it,
    parked, until he pulls the whole pebble — so a `[Blocked <SLUG> P####]` row
    is **inventory inside a container he already knows about**, and putting it
    on his screen defeats the point of having containerised it (*"I'm getting
    overwhelmed by the size of the backlog"*).

    **Transitive, and that is the load-bearing half.** ATT T193 is
    `[Blocked T192]` and T192 is pebble-blocked; suppressing only the direct
    edge leaks the container straight back onto the screen through the chain.
    The closure runs to a fixed point, so any depth works and a cycle
    terminates.

    **Q.md only.** The per-anchor `{slug} queries.md` is the agent's working
    view and keeps showing every row — the anchor's own agent must still see
    its inventory. Atticus was explicit about this, and it is why the
    suppression is applied to the ROW SET handed to one of the two renders
    rather than built into `build_queries_body`: the renderer stays total over
    whatever it is given (F284), and the divergence between the two surfaces is
    one named filter at one call site instead of a mode flag threaded through
    the render.

    Note this is deliberately NOT the data-side fix. Atticus tried that first —
    moving the four rows to `## Parked` — and C16 moved them straight back,
    correctly, since `[Blocked]` belongs in `## Later`. Mis-bracketing rows to
    hide them would be worse than the symptom; only the renderer can express
    "real, tracked, and not on this surface."
    """
    prefix = f"{name}-".casefold()

    def edge(r: Row) -> Optional[str]:
        """The row id this row waits on, or None. Mirrors `gated_by`'s handle
        normalisation so the two agree about what an edge points at."""
        m = _BLOCKED_HANDLE_RE.match(r.bracket)
        if not m:
            return None
        handle = m.group(1)
        if handle.casefold().startswith(prefix):
            handle = handle[len(prefix):]
        return handle

    suppressed = {r.identifier for r in rows
                  if _PEBBLE_BLOCKED_RE.match(r.bracket)}
    changed = True
    while changed:
        changed = False
        for r in rows:
            if r.identifier in suppressed:
                continue
            target = edge(r)
            if target and target in suppressed:
                suppressed.add(r.identifier)
                changed = True
    return suppressed

# A frontmatter description this function wrote, in any generation of its
# wording. The anchor name, the optional quote, and the credited engine
# (`by triage`, `by queries-render.py`) all drifted over time and none of them
# is the signal; what stays put is the self-describing CLAIM, so each generation
# is matched by its own claim.
#
# Two generations have shipped. The pre-F231 engine signed its work "Built by
# /ask"; everything since says it is mechanically rendered from the backlog.
# Recognizing only the current claim left the older one looking hand-authored,
# so it was preserved verbatim on every render and could never be refreshed —
# Tink, the one file still carrying it, kept re-appearing with the pre-F231
# section list no matter how many times the render ran over it.
_MACHINE_DESC_RE = re.compile(
    r'^description:\s*"?[^"]*?queries\s+—\s+(?:'
    r'mechanically rendered from the backlog'   # F231 and later
    r'|.*?\bBuilt by /ask\b'                    # pre-F231
    r')',
    re.I)


def _row_should_render(row: Row) -> bool:
    """True if a row is eligible for rendering in the Q.md body.

    Delegates to `audit_q.renders_in_body` so that the BANNER's zone-1 scope
    and the BODY's membership are one predicate rather than two that agree
    today. Both audit-q and this module count zone 1 through it."""
    return audit_q.renders_in_body(row.horizon, row.bracket)


def _wikilink_spans(text: str) -> list:
    """(start, end) for every `[[…]]` in `text`, so a cut can avoid landing
    inside one."""
    return [(m.start(), m.end()) for m in re.finditer(r"\[\[[^\]]*\]\]", text)]


def _safe_cut(text: str, cut: int) -> int:
    """Move `cut` back to before any `[[wiki-link]]` it would land inside.

    Cutting mid-link produces `[[F237 — Golden corpus exists in two...`, which
    is broken markup AND a bare F-number, so it trips C37 while looking like a
    link. Observed on TINK T150 the moment F305 made `[Blocked …]` rows render
    — the row had a perfectly good `[[F237 — …]]` link and truncation sawed it
    in half. Silent until then only because the row rendered nowhere."""
    for start, end in _wikilink_spans(text):
        if start < cut < end:
            return start
    return cut


def _truncate_body(text: str, soft_cap: int = 250) -> str:
    """Truncate body text at a sentence boundary near soft_cap; append '...' if cut."""
    text = text.strip()
    # Strip the arrow-link `→ [[X]]` (it's redundant with the bullet's link)
    text = ARROW_LINK_RE.sub("", text).strip()
    # An arrow-link at the start often leaves a dangling ` — ` separator
    # (`→ [[X]] — body` → ` — body`); drop it so the bullet reads cleanly.
    text = re.sub(r"^\s*[—–-]\s*", "", text)
    # Strip trailing block-ID
    text = TRAILING_BLOCK_ID_RE.sub("", text).rstrip()
    if len(text) <= soft_cap:
        return text
    # Find sentence-end break in [soft_cap - 80, soft_cap + 40]
    window_start = max(0, soft_cap - 80)
    window_end = min(len(text), soft_cap + 40)
    window = text[window_start:window_end]
    # Prefer "." or "!" or "?" followed by space
    for offset in range(len(window) - 1, -1, -1):
        ch = window[offset]
        if ch in ".!?" and offset + 1 < len(window) and window[offset + 1] == " ":
            cut = _safe_cut(text, window_start + offset + 1)
            return text[:cut].rstrip() + "..."
    # Fall back to word boundary near soft_cap
    cut = soft_cap
    while cut > 0 and text[cut] not in " \t":
        cut -= 1
    if cut <= 0:
        cut = soft_cap
    cut = _safe_cut(text, cut)
    return text[:cut].rstrip() + "..."


def _question_sentence(text: str, limit: int = 200) -> str:
    """Return just the ASK — the question's own sentence, without its context.

    Q005 (Dan, 2026-08-08): a doc-backed question renders as a preview, and the
    preview's whole job is to let the reader recognise which question this is
    before clicking the `(NQ)` link. That is one sentence, not a paragraph
    truncated at a character count.

    The `?` is preferred over `.` deliberately. A question stem often opens with
    a declarative clause that ends in a period — *"Slugged anchor = an anchor
    that explicitly declares `slug:`. Confirm, and accept the ~342-anchor review
    it implies?"* — where cutting at the first period keeps the premise and
    throws away the ask. Cutting at the first `?` keeps both.

    Falls back to `_truncate_body` when there is no question mark inside the
    budget, which covers questions phrased as statements.
    """
    text = text.strip()
    text = ARROW_LINK_RE.sub("", text).strip()
    text = re.sub(r"^\s*[—–-]\s*", "", text)
    text = TRAILING_BLOCK_ID_RE.sub("", text).rstrip()
    q = text.find("?")
    # A `?` inside a `[[wiki-link]]` is part of a filename, not a sentence end.
    while q != -1 and _safe_cut(text, q + 1) != q + 1:
        q = text.find("?", q + 1)
    if q != -1 and q + 1 <= limit:
        return text[:q + 1]
    return _truncate_body(text, limit)


def _bullet_bracket_display(bracket: str, name: str = "",
                            block_ids: Optional[set] = None) -> str:
    """Return the bracket text as it should appear in the Q.md bullet, with a
    `[Blocked <handle>]` handle turned into a link to the blocker's row.

    F283's design says the chained handle IS the description and *"the user
    clicks `F<NNN>` to learn the actual current state of the blocker"* — so it
    has to be clickable, and a bare F-number in a rendered queries file also
    trips C37. The `## Blockers` bullet already links its waiters for exactly
    this reason; the bracket itself was missed, and the gap stayed invisible
    because the rows carrying these brackets rendered nowhere. Making them
    visible surfaced 13 real C37 errors that had been latent, which is the
    point of a visibility ledger.

    Resolve-before-emit, as everywhere else: no block-id, no link — a link to
    a row that does not exist is worse than the bare handle."""
    m = _BLOCKED_HANDLE_RE.match(bracket)
    if m and name and block_ids and m.group(1) in block_ids:
        handle = m.group(1)
        return f"**[Blocked [[{name} Backlog#^{handle}|{handle}]]]**"
    return f"**[{bracket}]**"


def _count_qfix_subs(backlog_file: Path) -> int:
    """Count sub-bullets under the singleton `B-QFix` `[Ready]` row, if
    present. Each sub-bullet is one outstanding audit-q residual that the
    owning anchor's next /ask or /audit q-fix needs to drive to zero per
    the 100%-fix discipline. The banner surfaces this count as `{N}` at the
    very end of the H1 (when N > 0) so the user can glance Q.md and see
    instantly which anchors still have warnings."""
    try:
        text = backlog_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return 0
    lines = text.splitlines()
    in_qfix = False
    count = 0
    for line in lines:
        if line.lstrip().startswith("- **B-QFix"):
            in_qfix = True
            continue
        if not in_qfix:
            continue
        if line.startswith("  - "):
            count += 1
            continue
        # Blank line in the middle of the sub-bullet block is OK; keep going.
        if not line.strip():
            continue
        # Any other content (a new top-level row, a new H2, etc.) ends the
        # QFix block.
        break
    return count


def _extract_block_ids(backlog_file: Path) -> set[str]:
    """Return the set of `^block-id` markers present in the backlog file.
    Used by `_bullet_link` to verify a speculative `^<identifier>` link
    actually has a target before emitting it (no script-generated dead links).
    """
    try:
        text = backlog_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    return set(re.findall(r"\^([A-Za-z][A-Za-z0-9_\-]*)\b", text))


def _extract_h3_headings(backlog_file: Path) -> set[str]:
    """Return the set of H3 heading texts present in the backlog file.
    Used to verify `[[Backlog#<heading>]]` resolves before emitting.
    """
    try:
        text = backlog_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    return set(m.strip() for m in re.findall(r"^### ([^\n]+)$", text, re.MULTILINE))


# Brackets whose rows MUST declare a concrete next autonomous action (the step
# the agent will take WITHOUT user involvement). A [Ready]/[Active] row with no
# stateable autonomous next-action isn't really Ready — the missing Next is
# surfaced as a warning so it can't masquerade.
# F284 — `Implementing` is the feature-lifecycle alias for `Active` and
# `derive_banner` has always counted it as Runnable; it was missing here, so the
# banner promised rows the body then refused to show (3 rows vault-wide,
# 2026-07-29). Both aliases must be in the same set or banner and body disagree.
READY_ACTIVE_BRACKETS = {"Ready", "Agreed", "Active", "Implementing"}

# Labeled sub-bullets under a row carry the concrete, user-facing text the
# render surfaces (so the mechanical render isn't stuck quoting the row's
# internal-jargon body):
#   `  - **Next:** <no-user action>`     on [Ready]/[Active] rows
#   `  - **Verify:** <yes/no question>`  on [Verify*]/[Watching*] rows
# Both accept a `(...)` qualifier and a non-bold fallback.
def _subbullet_res(label: str) -> tuple[re.Pattern, re.Pattern]:
    return (
        re.compile(rf"^\s+-\s+\*\*{label}(?:\s*\([^)]*\))?:\*\*\s*(.+?)\s*$"),
        re.compile(rf"^\s+-\s+{label}(?:\s*\([^)]*\))?:\s*(.+?)\s*$"),
    )


def _extract_labeled_subbullets(backlog_file: Path, label: str) -> dict[str, str]:
    """Map each top-level row identifier → the text of its `**<label>:**`
    sub-bullet, if present. Generic over the label (Next / Verify)."""
    bold_re, plain_re = _subbullet_res(label)
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return {}
    out: dict[str, str] = {}
    current: Optional[str] = None
    for line in lines:
        if H2_HEADING_RE.match(line):
            current = None
            continue
        m3 = ROW_OPENER_H3_RE.match(line)
        if m3:
            current = m3.group(1)
            continue
        mb = ROW_OPENER_BULLET_RE.match(line)
        if mb and _extract_bullet_bracket(line):
            current = mb.group(1)
            continue
        if current is None:
            continue
        m = bold_re.match(line) or plain_re.match(line)
        if m:
            out[current] = m.group(1).strip()
    return out


def extract_next_actions(backlog_file: Path) -> dict[str, str]:
    """`Next:` sub-bullets — the no-user next step on each [Ready]/[Active] row."""
    return _extract_labeled_subbullets(backlog_file, "Next")


def extract_verify_questions(backlog_file: Path) -> dict[str, str]:
    """`Verify:` sub-bullets — the concrete yes/no question on each
    [Verify*]/[Watching*] row, surfaced verbatim as the V-item so the user sees
    a real question, not the row's internal verify-plan jargon."""
    return _extract_labeled_subbullets(backlog_file, "Verify")


# ============================================================
# Worktree findings splice — successor to /triage's retired § 5.5
# (worktree-check + lazy refresh, F231). worktree-check (workflow/scripts/)
# scans `claude --worktree` checkouts for un-landed work and caches its
# findings (already carrying their own `## Worktrees needing attention` H2)
# at ~/.config/worktree-check/findings.md. This render owns the splice now
# that /triage is gone. Un-landed worktrees are cross-anchor infrastructure
# health, not any one anchor's backlog content, so the block is surfaced on
# exactly ONE canonical anchor — SKA, which owns worktree-check — instead of
# every anchor queries-render.py happens to be called for (avoids the same
# block being duplicated across N sections of Q.md).
# ============================================================

WORKTREE_FINDINGS = Path.home() / ".config" / "worktree-check" / "findings.md"
WORKTREE_CANONICAL_ANCHOR = "SKA"
WORKTREE_CHECK_SCRIPT = (
    Path.home() / ".claude" / "skills" / "workflow" / "scripts" / "worktree-check"
)


def _worktree_findings_lines(name: str) -> list[str]:
    """Findings block to prepend to `name`'s queries body — [] unless `name`
    is the canonical anchor AND the cache is non-empty (mirrors /triage's old
    'if non-empty, splice verbatim; else surface nothing')."""
    if name != WORKTREE_CANONICAL_ANCHOR:
        return []
    try:
        text = WORKTREE_FINDINGS.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    if not text.strip():
        return []
    return text.rstrip("\n").splitlines()


def _fire_worktree_rescan() -> None:
    """Lazy background refresh, mirroring /triage's old
    `worktree-check --if-stale 72 --quiet &`. Never blocks the render — the
    current render always uses whatever the cache already holds; errors are
    swallowed (best-effort, off the critical path)."""
    try:
        subprocess.Popen(
            [sys.executable, str(WORKTREE_CHECK_SCRIPT), "--if-stale", "72", "--quiet"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except OSError:
        pass


def build_queries_body(name: str, banner: Optional[str], rows: list[Row],
                       vault_index: dict, next_actions: dict[str, str],
                       verify_questions: dict[str, str],
                       backlog_file: Path) -> Optional[list[str]]:
    """Build the canonical queries body from backlog state — the SINGLE render that
    is both written to `{name} queries.md` AND copied into the anchor's Q.md section
    (F231 — the query file IS what goes into the queue file; one render, two
    destinations). Pure (no file writes); `render_queries_doc` writes the file and
    `main()` reuses the return for Q.md. Fully script-owned; edit the backlog rows.

    The render is TOTAL over the rows `_row_should_render` admits (F284) — every
    eligible row lands in exactly one section, in emission order (F283):
      ## Blockers       ← computed, not authored: any row some OTHER row names in
                          its `[Blocked <handle>]`, promoted out of whatever
                          section it would otherwise occupy. Empty is the good
                          state, and it reads in one glance.
      ## Ready          ← `[Ready]`/`[Agreed]`/`[Active]`/`[Implementing]` rows,
                          each with its declared `**Next:**` no-user action (⚠ if
                          none). First among the working sections because it is
                          short and orients the rest.
      ## Questions      ← `[Questions]` rows, linking to the source's open Qs.
                          The one pile the user personally unsticks.
      ## Blocked        ← the visibility ledger: `[Blocked <handle>]` and
                          `[Waiting …]` together, so nothing disappears. Scanned,
                          not worked.
      ## Verifications  ← `[Verify]` / `[Watching*]` rows (each `**V<n>**` + the
                          row's verify-plan body + `· **yes / no**`). Last: an
                          unverified check is only a problem when something
                          depends on it, and then Blockers has already raised it.
      ## Other          ← the catch-all: every remaining eligible row, bracket
                          shown verbatim. Before F284 these rows were silently
                          dropped — 47 of 99 frontier rows vault-wide, including
                          every row with no bracket at all.
    `[Verify-by <date>]` rows render nowhere — see `_row_should_render`.
    Totality is asserted, not assumed: `_coverage_warning` re-checks the partition
    and emits a visible section if it ever breaks, so a future unclaimed row shows
    up as a complaint rather than an absence.
    Returns the body lines, or None when the anchor is empty (banner is None)."""
    if banner is None:
        return None
    block_ids = _extract_block_ids(backlog_file)
    h3_headings = _extract_h3_headings(backlog_file)
    # F283 — invert the `[Blocked <handle>]` edge (the render target F268 has been
    # waiting for). `gated_by` maps a blocker's identifier to the rows waiting on
    # it, so the bullet can say what it holds up — but ONLY the waiting rows that
    # are themselves on the frontier are collected, because only those make the
    # blocker worth the top of the file.
    #
    # This section first shipped drawing from ALL rows, on the reasoning that
    # "nobody is looking at the thing your work waits on" is worth surfacing
    # regardless of where the waiting work sits. Dan's correction, 2026-07-30:
    # a blocker for something parked in `## Later` is not a blocker, it is a note.
    # Nothing he is working on is held up, so the row is noise at the position of
    # highest attention. The known cost is that all four named edges vault-wide
    # currently point at Later rows (Tink F238 waits on F230, both parked), so the
    # section renders empty everywhere until a frontier row actually gets blocked
    # — which is the honest reading of "nothing is blocked."
    # Dan, 2026-08-08, after failing to find ATT F041 while eight rows announced
    # they were blocked on it: *"if an item is blocking other items, create a
    # category at the very top, even above Ready… that way my eyes are drawn
    # right to it."* The section already existed and already sat first; it was
    # firing on nothing, for two independent reasons, and BOTH had to go.
    #
    # (1) SCOPE. The gate was `r.horizon in ACTIVE_HORIZONS_BANNER`, so only a
    # blocked row on the Now/Next frontier could promote its blocker. But a
    # `[Blocked …]` row under `## Later` DOES render — F283 admits it into the
    # visibility ledger precisely so nothing disappears — and it is just as
    # stuck. The honest test is not "is the waiting row on the frontier" but
    # "does the waiting row appear on this page at all": if the reader can see a
    # row saying it waits on X, the reader must be able to find X. Using
    # `_row_should_render` also keeps this in step with the body automatically,
    # rather than being a third horizon list that agrees with the other two
    # today.
    #
    # (2) THE HANDLE NEVER MATCHED. `gated_by` is keyed by the handle text and
    # looked up against `r.identifier`, so `[Blocked ATT-F041]` stored `ATT-F041`
    # and the row it names is `F041` — no match, ever. Every anchor-qualified
    # handle in the vault was inert, which is most of them: the qualified form is
    # what a cross-anchor blocker has to use, and agents write it in-anchor too
    # because it reads better. Stripping this anchor's own prefix makes the two
    # spellings the same edge. A handle naming a DIFFERENT anchor still matches
    # nothing here, which is correct — that row is not on this page to promote.
    prefix = f"{name}-".casefold()
    gated_by: dict[str, list[str]] = {}
    for r in rows:
        m = _BLOCKED_HANDLE_RE.match(r.bracket)
        if m and _row_should_render(r):
            handle = m.group(1)
            if handle.casefold().startswith(prefix):
                handle = handle[len(prefix):]
            gated_by.setdefault(handle, []).append(r.identifier)
    # `[Done]` is the one further exclusion: a resolved blocker means the WAITING
    # row is stale, which is a different finding and already /groom's.
    # Dan, 2026-08-08, on the first render that actually populated this section:
    # *"I don't think if something is truly Ready it's actually a blocker. It is
    # a blocker, but it's just a TEMPORARY blocker — as soon as you go through
    # the ready queue, it becomes unblocked. So blockers should only be things
    # which are blocking other things and are not themselves ready."*
    #
    # The test is therefore not "does this gate something" but "would working
    # the Ready queue clear it". A row every member of which is agent-runnable
    # clears itself by being worked, so it belongs in `## Ready` where it will
    # be, not at the position of highest attention where it displaces rows that
    # nothing an agent does will move. TINK's first populated render made the
    # point: three of six entries were `[Ready]` (F303, F312, F305) and would
    # have resolved themselves that same session.
    #
    # `all(...)`, not `any(...)`, and the difference is a real case: `[Ready,
    # User]` has an agent phase AND a gate only Dan can lift, so working the
    # Ready queue does NOT clear it and it stays elevated. Suppression requires
    # the row to be agent-runnable and nothing else.
    def _self_clearing(bracket):
        members = audit_q.bracket_members(bracket)
        return bool(members) and all(m in READY_ACTIVE_BRACKETS for m in members)

    blockers = [r for r in rows
                if r.identifier in gated_by and not r.bracket.startswith("Done")
                and not _self_clearing(r.bracket)]
    promoted = {id(r) for r in blockers}
    # Promotion happens FIRST, so a blocker leaves whatever section would
    # otherwise hold it — including Verifications — and a promoted off-frontier
    # row JOINS the eligible set rather than being counted as a coverage leak.
    eligible = blockers + [r for r in rows
                           if id(r) not in promoted and _row_should_render(r)]
    # An empty B-QFix (zero residuals) is NOT Ready — nothing to do — so drop it
    # from the Ready render (per user 2026-06-29: "not really ready, what's it doing there").
    qfix_empty = _count_qfix_subs(backlog_file) == 0
    # Same ordering defect, same fix — leaving the sibling list on file order is
    # exactly the "fixed one, left the other" failure T099 keeps naming.
    # T153 — the section router is MEMBER-AWARE, matching the class predicates
    # the banner already uses. F305 rules that a bracket is a SET: `[Ready, User]`
    # is legal and `validate_status` accepts it, splitting on commas and
    # validating each member. These tests did not, so the vault's first real set
    # bracket put F217 and F307 into `## Other` — neither under `## Ready` with
    # its `Next:`, nor under `## User` with its ask, so the two things that made
    # each row actionable both vanished while the banner read `Ready 12  User 3`
    # because `in_class_ready`/`in_class_user` ARE member-aware. That is exactly
    # the disagreement F305 was built to make impossible.
    #
    # A set-bracket row renders ONCE PER MEMBER CLASS, not once in a "primary"
    # section. The banner counts per class through independent `any()`
    # predicates, so a row genuinely in two classes is counted twice; showing it
    # once would need the banner to pick a primary too, re-opening the same
    # divergence and discarding the information the set bracket exists to carry.
    # The two appearances are not a duplicate — each carries a different payload
    # (`Next:` under Ready, the ask under User), which is what "the row is both"
    # means. F217's Phase 1 and F307's draft phase are precisely this shape: an
    # executable agent step that must run BEFORE Dan can usefully answer.
    def _member(r, pred):
        return any(pred(m) for m in audit_q.bracket_members(r.bracket))

    ready = _by_horizon([r for r in eligible if id(r) not in promoted
                         and _member(r, lambda m: m in READY_ACTIVE_BRACKETS)
                         and not (r.identifier == "B-QFix" and qfix_empty)])
    qs = _by_horizon([r for r in eligible if id(r) not in promoted
                      and _member(r, lambda m: "Questions" in m)])
    # The ledger. `[Waiting]` rides with `[Blocked <handle>]` because both mean
    # "not moving, and not by the user's hand" — the difference is only who
    # eventually moves it, which the bracket itself already says.
    blocked = [r for r in eligible if id(r) not in promoted
               and _member(r, lambda m: m.startswith("Blocked")
                           or m.startswith("Waiting"))]
    verifs = [r for r in eligible if id(r) not in promoted
              and _member(r, lambda m: m.startswith("Verify")
                          or m.startswith("Watching"))]
    # F259 minted `[User]` for an action only the human can perform (log in,
    # click a permission dialog, run an experiment on a display the agent
    # cannot see), and the banner has counted them since — but no section ever
    # claimed them, so every one fell into `## Other` beside unbracketed
    # leftovers and went unread. Dan, 2026-08-05: *"I don't even see a T21. I
    # don't even see it there."* A pile the user is the ONLY possible actor for
    # is the last thing that should be in the catch-all.
    users = [r for r in eligible if id(r) not in promoted
             and _member(r, lambda m: m == "User")]
    # F284 — the catch-all. Anything eligible that the named sections did not
    # claim renders here rather than falling off the end of the function.
    # `suppressed` is the ONE deliberate omission (the empty B-QFix row above);
    # it is tracked so the coverage assertion can account for it instead of
    # reading it as a leak.
    claimed = (promoted | {id(r) for r in ready} | {id(r) for r in qs}
               | {id(r) for r in blocked} | {id(r) for r in verifs}
               | {id(r) for r in users})
    suppressed = [r for r in eligible
                  if r.identifier == "B-QFix" and qfix_empty and id(r) not in claimed]
    accounted = claimed | {id(r) for r in suppressed}
    other = [r for r in eligible if id(r) not in accounted]

    body: list[str] = []
    body.extend(_worktree_findings_lines(name))

    def _h2(title: str) -> None:
        # Blank line before every H2 (R-progressive-02) — surfaced the moment
        # Warden could see script-written files (fork 9 option A, 2026-07-13).
        if body:
            body.append("")
        body.append(title)

    def _q_affordance(r) -> tuple[str, list[str], Optional[str]]:
        """The `**(NQ)**` badge, the indented question preview, and the anchor.

        Returns `(badge, preview_lines, anchor)` so a caller can splice the
        badge into its own bullet, append the preview under it, and aim its
        link at the questions with `_with_anchor` (T216 — the badge, the
        preview and the anchor are three views of the same pending-Q state, and
        computing them anywhere but together is how the link came to point at a
        doc whose top is a table of contents). `## Questions` and
        `## Blockers` both call it, and that sharing is the point: promotion
        moves a `[Questions]` row OUT of `## Questions` (one row, one section),
        so a question that is holding other work up used to render with its
        bracket and its waiters but **no question anywhere** — the most urgent
        kind of question was the one kind the user could not read. Dan,
        2026-08-11, on F312: *"you list 312 as a blocker with questions. But if
        I click on 312, I don't see a question there."* The 2026-07-18 rule that
        the queue must SHOW the questions rather than a bare badge was being
        silently exempted by the promotion, which is why this lives in one
        function instead of two.
        """
        n = _row_q_count(r, vault_index, backlog_file)
        badge = f" **({n}Q)**" if n else ""
        # Inline each pending question's TEXT under the row. A doc-backed row
        # reads its feature doc's `## Open Questions`; a doc-less T-/B-row reads
        # its OWN sub-bullets (F233 inline form) — the latter used to be skipped,
        # which left the question invisible everywhere the user looks (Dan,
        # 2026-08-02).
        qdoc = _row_q_doc_path(r, vault_index)
        q_entries = (_read_open_questions(qdoc) if qdoc
                     else _read_row_inline_questions(backlog_file, r))
        # A doc-backed Q is a PREVIEW — the answerable form (options, block-id,
        # Recommendation) lives one click away in the feature doc, so its
        # QUESTION alone is enough to identify it. An inline row Q has no such
        # home: this render is the only place the user will read it, so it must
        # carry its `**(A)**`/`**(B)**` options or it is unanswerable (North
        # Star 2 — everything needed to answer is in the entry).
        qlimit = 200 if qdoc else 420
        lines: list[str] = []
        for qid, qtext, qrec, qopts in q_entries:
            if not qtext:
                continue
            # Q005 (Dan, 2026-08-08, on F311's four questions: *"see how
            # unreadable these questions are… the options are just jammed
            # together"*). Every part of the ask — stem, options, lean — shared
            # one markdown line, so Obsidian wrapped them into a run-on
            # paragraph in which nothing was distinguishable and each part was
            # cut mid-sentence. A doc-backed Q now renders as its handle plus its
            # question sentence and NOTHING else; the `(NQ)` link beside the row
            # is what the reader clicks for the answerable form.
            #
            # T130 survives intact, by suppressing MORE rather than less. Its
            # rule is that a lean must never name an option the reader cannot
            # see (2026-08-05 on F305 Q1: *"you're telling me you lean B on
            # what?"*) — dropping the options and the recommendation together
            # honours it; dropping only the options would reintroduce exactly
            # that defect.
            if qdoc:
                # F332 (Dan, 2026-08-15) — the queue is a pure link-list: a
                # doc-backed entry is ONE line, and the anchored link already
                # lands the reader ON the question (T216), where the doc-level
                # info box and the full ask-format entry live. The preview
                # line this used to emit was exactly the meta-text Dan said he
                # has learned to ignore. Inline (docless) rows below keep
                # their preview: on an unmigrated anchor this render is still
                # the only place the user can read the question at all.
                continue
            opt_txt = ""
            if qopts:
                opt_txt = " · " + " · ".join(
                    f"**({lab})** {gloss}" for lab, gloss in qopts)
            rec_txt = f" · *{_truncate_body(qrec, 90)}*" if qrec else ""
            # DISPLAY PREVIEW, not a formal ask-format Q entry. The answerable Qs
            # (block-IDs, Recommendations, option bullets) live in the source
            # feature doc's `## Open Questions`, which audit-q enforces there.
            # This inline copy is a dashboard preview only, so it deliberately
            # does NOT lead with `- **Q<n>` — that shape is parsed by audit-q's
            # Q_HEADER_RE as a formal Q and would trip C6 (block-id)/C9
            # (recommendation) on every render of this generated file.
            lines.append(f"    - {qid} — {_truncate_body(qtext, qlimit)}"
                         f"{opt_txt}{rec_txt}")
        return badge, lines, _doc_q_anchor(qdoc, q_entries)

    # F283 — Blockers first. Computed, never authored: these rows are here only
    # because something else names them. Each bullet says WHAT it holds up, which
    # is the whole point — the `[Blocked <handle>]` edge was previously readable
    # only from the waiting end, so a blocker had no idea it was one.
    if blockers:
        _h2("## Blockers")
        for r in blockers:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            btxt = _bullet_bracket_display(r.bracket, name, block_ids) if r.bracket else "**[no state]**"
            # Link each waiter to its backlog row so the reader can jump to the
            # work being held up — and so the bare handle does not trip C37
            # (bare F-numbers in a rendered queries file must be wiki-links).
            # Resolve-before-emit as everywhere else: no block-id, no link.
            waiters = ", ".join(
                f"[[{name} Backlog#^{_anchor_of(w)}|{w}]]"
                if _anchor_of(w) in block_ids else w
                for w in gated_by.get(r.identifier, []))
            # Say so when the blocker was dragged up from off-frontier. "F230
            # gates F238, and F230 is parked in Later" is the actionable shape;
            # without the horizon the row reads as ordinary pending work.
            parked = "" if _row_should_render(r) else f" · parked in **{r.horizon}**"
            txt = _truncate_body(r.body, 160)
            # A promoted `[Questions]` row is still a question, and this is now
            # the ONLY place it renders — so it carries the same badge and
            # question preview `## Questions` would have given it. Without this
            # the bullet said "[Questions]" and showed none.
            badge, qlines, qanchor = (_q_affordance(r)
                                      if _member(r, lambda m: "Questions" in m)
                                      else ("", [], None))
            link = _with_anchor(link, qanchor)
            body.append(f"- {link}{badge} — {btxt} **gates {waiters}**{parked}"
                        + (f" — {txt}" if txt else ""))
            body.extend(qlines)
    # Ready first among the working sections: it is short, it is what the agent
    # can act on with no user involvement, and it orients everything below it.
    if ready:
        _h2("## Ready")
        for r in ready:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            na = (next_actions.get(r.identifier)
                  or _doc_next_fallback(r, vault_index, backlog_file))
            na_txt = (_truncate_body(na, 200) if na
                      else "⚠ none declared — not really Ready; add a no-user next-action or rebracket")
            # A `[Ready]` row can hold pending questions without being a
            # `[Questions]` row — its agent work is genuinely runnable AND its
            # doc is waiting on an answer, which is a normal state for a feature
            # mid-flight. The bracket is a SET but the render picks one section,
            # so before this the questions rendered nowhere: F303 gained Q3 and
            # Q5 on 2026-08-11 and the queue file showed the row under `## Ready`
            # with its Next and no hint that two answers were owed. Same defect
            # T211 fixed for promoted `[Questions]` rows, reached by the other
            # side — there the bracket was right and the section moved, here the
            # section is right and the bracket is something else. Both violate
            # the 2026-07-18 rule that the queue must SHOW its questions, and
            # both are fixed by calling the one affordance rather than
            # reimplementing it per section.
            badge, qlines, qanchor = _q_affordance(r)
            link = _with_anchor(link, qanchor)
            body.append(f"- {link}{badge} — **Next:** {na_txt}")
            body.extend(qlines)
    # Questions — the one pile the user personally unsticks. Kept separate from
    # Blocked (F283 Q2 (A)): the axis that earns a section break is "can the user
    # act on it", not "is it stopped".
    if qs:
        _h2("## Questions")
        for r in qs:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            txt = _truncate_body(r.body, 160)
            # Pending-Q count in bold parens — the user sees how many answers the
            # feature needs at a glance (`[[F181 …]] **(5Q)**`). Per /query North
            # Star. Shared with `## Blockers`, which renders promoted `[Questions]`
            # rows and needs the identical affordance.
            cnt, qlines, qanchor = _q_affordance(r)
            # The Q-bearing doc is the entry's home — link it first, demote the
            # backlog-row link to a parenthesized `(row)` pointer (same shape as
            # the F235 Verify entries). Inline T-/B-rows keep the row link: the
            # row carries the Qs itself.
            doclink = _q_home_link(r, vault_index, backlog_file)
            if doclink:
                rowlink = re.sub(r"\|[^\]|]*\]\]$", "|row]]", link) if link.rstrip().endswith("]]") else link
                # Anchor the DOC link only. The `(row)` pointer deliberately
                # keeps aiming at the backlog row — that is what it is for.
                doclink = _with_anchor(doclink, qanchor)
                body.append(f"- {doclink}{cnt} ({rowlink})" + (f" — {txt}" if txt else ""))
            else:
                body.append(f"- {_with_anchor(link, qanchor)}{cnt}"
                            + (f" — {txt}" if txt else ""))
            body.extend(qlines)
    # F283 — the visibility ledger. Scanned, not worked: "if it's legitimately
    # blocked on something else, then I don't really want to see it, I just wanna
    # work on the thing that it's blocked by." It renders anyway so that nothing
    # silently disappears, which is the defect that produced this feature.
    # F305 D5 — `[Verify*]`/`[Watching*]` rows ride the SAME ledger. Dan's
    # ruling 2026-08-13: the bracket says "done, nothing waiting — only the
    # check remains", which is exactly the parked, safely-ignorable state;
    # when one gates something, the Blockers promotion has already lifted it
    # to the top. The old `## Verifications` section — a positionally
    # V-numbered ask pile — retires with it: the ASK now reaches the user as
    # the doc's final question (same Q numbering), never a parallel handle
    # namespace (T127).
    if blocked or verifs:
        _h2("## Blocked")
        for r in blocked + verifs:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            btxt = _bullet_bracket_display(r.bracket, name, block_ids)
            q = verify_questions.get(r.identifier)
            txt = _truncate_body(q or r.body, 160)
            body.append(f"- {link} — {btxt}" + (f" {txt}" if txt else ""))
    # The `[User]` pile — emitted right after Questions, because it is the
    # other set of rows that go nowhere until the human personally acts. Each
    # shows its `- **User:**` action, which F259 already requires the row to
    # carry, so the entry states what to DO rather than merely naming a row.
    if users:
        _h2("## User")
        # Same shape as Verifications: show the row's own `- **User:**` action
        # verbatim (F259 requires the row to carry one), so the entry says what
        # to DO. A row missing it gets a ⚠ rather than quietly showing prose.
        user_actions = _extract_labeled_subbullets(backlog_file, "User")
        # F305 D5 / T127 — the row's own durable id (the link text) is the
        # answer handle; the positional U<i> namespace is retired, so a
        # handle never renames between renders.
        for r in users:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            a = user_actions.get(r.identifier)
            atxt = (_truncate_body(a, 240) if a
                    else "⚠ no action stated — add a `- **User:** <what you must do>` sub-bullet to the row")
            body.append(f"- {link} — {atxt}")

    # F284 — the catch-all, emitted last so it never displaces the classified
    # work. Each row shows its bracket VERBATIM: a state the render doesn't know
    # (`[Designing]`), a state gated on the user (`[User]`), the bracket field
    # used as prose (`[big task]`), and the largest class of all — no bracket at
    # all — are all legible as what they are instead of vanishing.
    if other:
        _h2("## Other")
        for r in other:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            btxt = _bullet_bracket_display(r.bracket, name, block_ids) if r.bracket else "**[no state]**"
            txt = _truncate_body(r.body, 200)
            body.append(f"- {link} — {btxt}" + (f" {txt}" if txt else ""))
    body.extend(_coverage_warning(
        eligible, [blockers, ready, qs, blocked, verifs, users, other], suppressed))
    if not body:
        body.append("_Nothing pending._")
    return body


def _coverage_warning(eligible: list[Row], sections: list[list[Row]],
                      suppressed: list[Row]) -> list[str]:
    """F284's structural gate: assert every eligible row REACHES the page, and
    make a breach visible rather than silent.

    The catch-all makes coverage total by construction, so this can only fire on
    a code defect — an eligible row claimed by no section, or a new deliberate
    suppression that forgot to register itself. Either way the answer is a
    complaint in the surface the user actually reads, NOT a raised exception:
    aborting the render would delete the whole queue file and hide 100% of the
    work to protest hiding some of it.

    **Counted over DISTINCT rows, not by summing section lengths (T153).** The
    original sum-based form encoded "the sections partition eligible", and read
    any row in two sections as a `double-rendered` failure. Under F305 a bracket
    is a SET, so a `[Ready, User]` row appearing under both `## Ready` and
    `## User` is the CORRECT render — the sum would have turned the fix into a
    coverage failure on the page. What must still be asserted is the direction
    that actually loses work: a row reaching NO section at all."""
    rendered_ids: set[int] = set()
    for s in sections:
        rendered_ids |= {id(r) for r in s}
    accounted = rendered_ids | {id(r) for r in suppressed}
    missing = [r for r in eligible if id(r) not in accounted]
    if not missing:
        return []
    sys.stderr.write(
        f"COVERAGE: {len(eligible)} eligible rows, {len(accounted)} accounted "
        f"({len(rendered_ids)} rendered + {len(suppressed)} suppressed) — "
        f"missing {', '.join(r.identifier for r in missing)}\n")
    return ["", "## ⚠ Coverage failure",
            f"- {len(missing)} row(s) unrendered "
            f"({', '.join(r.identifier for r in missing)}) — the queue file is "
            f"NOT showing this anchor's full frontier. This is a bug in "
            f"queries-render.py, not in the backlog."]


def render_queries_doc(name: str, banner: Optional[str], rows: list[Row],
                       vault_index: dict, next_actions: dict[str, str],
                       verify_questions: dict[str, str], backlog_file: Path) -> bool:
    """(Re)write `{name} queries.md`: frontmatter + banner H1 (anchor-linked) + the
    canonical queries body (`build_queries_body`). The SAME body is copied into the
    anchor's Q.md section by `main()` (F231). Fully script-owned (per user direction
    2026-06-26: *"purely mechanical"*); edit the backlog rows, not this file.

    A DRAINED anchor (banner is None — every row Done, nothing in any live
    horizon) still gets its page rewritten, to the zero state. `main()` removes
    such an anchor's Q.md block, and before F282-Q2 this function returned early,
    which froze the page on its last non-empty banner forever — observed on
    Scout, whose page read `Runnable 0  User 1 | Now 1` against a backlog holding
    a single [Done] row. A script-owned page must never be able to contradict the
    backlog it is generated from, so the drained case is written, not skipped.
    Returns False only when there is no page to keep honest."""
    built = build_queries_body(name, banner, rows, vault_index, next_actions,
                               verify_questions, backlog_file)
    queries_file = audit_q.backlog_track_dir(backlog_file) / f"{name} queries.md"
    body: list[str]
    h1: str
    # Resolve the actual anchor page name — usually equals `name` (slug =
    # anchor-page basename), but for anchors where the two differ (e.g. slug
    # `VEC`, anchor page `Vector.md`), fall back to the anchor folder name
    # (backlog is at `<anchor-dir>/<name> Track/<name> Backlog.md`, so
    # backlog_file.parent.parent.name is the anchor folder name). If neither
    # exists in vault_index, stay on `name` (existing behavior; audit-q C22
    # will surface the broken link if truly unresolvable).
    anchor_page_name = name
    if name.lower() not in vault_index:
        anchor_dir_name = audit_q.backlog_track_dir(backlog_file).parent.name
        if anchor_dir_name.lower() in vault_index:
            anchor_page_name = anchor_dir_name
    if built is None or banner is None:
        # Don't conjure a page for an anchor that never had one — this path
        # exists to correct a stale page, not to populate empty anchors.
        if not queries_file.is_file():
            return False
        # `-` is the existing "nothing actionable, cold storage only" TAG from
        # derive_banner; reused here rather than minting a token, since a fully
        # drained anchor is the same signal. Counts are all zero by definition:
        # any non-zero horizon or icebox count would have produced a banner.
        # Through the one formatter, never hand-spelled. This line used to carry
        # its own copy of the banner and had drifted two renames behind it —
        # `Runnable` (renamed back to `Ready`) and a zone 3 of `Verify  Icebox`
        # (now `Parked  Waiting  Icebox`) — so a fully drained anchor was
        # published in a shape `R-query-16` no longer describes. Same defect as
        # MUX T081 at the consuming end: a second spelling of a format is a
        # second thing to forget. All counts are zero by definition here.
        h1 = audit_q.format_status_banner(
            "-", f"[[{anchor_page_name}|{name}]]",
            0, 0, 0, 0, 0, 0, 0, 0,
        )
        body = ["_Nothing pending._"]
    else:
        # The Q.md banner links the name to `{name} queries` (so the user clicks
        # over); inside queries.md that would be a self-link — retarget to the anchor.
        h1 = banner.replace(f"[[{name} queries|{name}]]", f"[[{anchor_page_name}|{name}]]")
        body = built
    # Preserve existing frontmatter; else write a default.
    # The section list must be the one `_render_body` actually emits, in its
    # order: Blockers / Ready / Questions / Blocked / Verifications / User /
    # Other. `User` was missing here while the `## User` emission shipped, so this
    # line under-reported the render by one section — found 2026-08-12 by
    # matching `templates/query.md` against a real instance for F303, where the
    # template turned out to be RIGHT and this string stale. Whenever a section
    # is added or dropped, this string moves with it; that is the whole reason
    # the refresh below exists.
    desc = (f"description: {name} queries — mechanically rendered from the backlog "
            "(Blockers / Ready+Next / Questions / Blocked / User / Other), "
            "and copied verbatim into Q.md. "
            "Do not hand-edit; edit the backlog rows.")
    fm = ["---", desc, "---"]
    if queries_file.is_file():
        try:
            existing = queries_file.read_text(encoding="utf-8").splitlines()
            if existing and existing[0].strip() == "---":
                for j in range(1, len(existing)):
                    if existing[j].strip() == "---":
                        fm = existing[:j + 1]
                        break
        except (OSError, UnicodeDecodeError):
            pass
    # The description line is machine-owned — it names the sections this render
    # emits, and the file itself says "do not hand-edit". Preserving it verbatim
    # left every queries file written before F283 advertising the old section
    # set (`Verifications / Ready+Next / Questions`) forever, since only a
    # brand-new file ever saw the default. Refresh OUR line in place; any other
    # key, and any description a human rewrote into their own words, is left
    # exactly as found.
    #
    # The tell is the CLAIM, not the exact wording: a description that says it is
    # mechanically rendered from the backlog is this function's output no matter
    # which generation wrote it. Matching the current phrasing instead missed the
    # ones that most needed refreshing — DKT still credited the retired `triage`,
    # FEX still called itself `CAE`, and both were quoted, so a prefix test
    # anchored on `description: {name}` skipped them on the quote alone.
    fm = [desc if _MACHINE_DESC_RE.match(ln) else ln for ln in fm]
    out = fm + ["", h1, ""] + body + [""]
    queries_file.write_text("\n".join(out), encoding="utf-8")
    _selffire(queries_file)
    return True


def _bullet_link(row: Row, name: str, vault_index: dict,
                 block_ids: set[str], h3_headings: set[str]) -> str:
    """Return the wiki-link form for the row's bullet.

    **Resolve-before-emit (2026-06-04 design fix):** every emitted link MUST
    have a verified target. The fallback chain is:
      1. row.arrow_link (the `→ [[X]]` link in the row) — verify the basename
         resolves in vault_index; on miss fall through.
      2. F-row title basename — verify `[[title]]` resolves in vault_index;
         on miss fall through.
      3. Backlog block-id `[[NAME Backlog#^id]]` — verify `^id` is in
         block_ids; on miss fall through.
      4. H3 heading link (for H3 rows) — verify the heading is in h3_headings.
      5. Plain text (just the identifier, no `[[ ]]` brackets) — last resort
         when nothing resolves. Better a non-link than a dead link.
    """
    # Step 1: arrow_link if it resolves. (Lower-cased test — index keys are
    # lowered per T002; the old case-sensitive test silently demoted every
    # arrow-linked row to its block-id fallback.)
    if row.arrow_link:
        bn = row.arrow_link.split("#")[0].split("|")[0].strip()
        if vault_index.get(bn.lower()):
            return f"[[{row.arrow_link}]]"
    # Step 2 (H3 rows): heading link if heading exists.
    if row.is_h3:
        m = re.match(r"^### ([^[]+?)(?:\s*\[[^\]]+\])?\s*$", row.raw_line)
        if m:
            heading = m.group(1).strip()
            if heading in h3_headings:
                return f"[[{name} Backlog#{heading}|{row.identifier}]]"
        anchor = _anchor_of(row.identifier)
        if anchor in block_ids:
            return f"[[{name} Backlog#^{anchor}|{row.identifier}]]"
        return row.identifier  # plain text fallback
    # Step 2 (F-row): try title-as-basename if it resolves.
    if row.identifier.startswith("F") and row.identifier[1:].isdigit():
        m = re.match(r"^- \*\*([^*]+)\*\*", row.raw_line)
        if m:
            title = m.group(1).strip()
            if vault_index.get(title.lower()):
                return f"[[{title}]]"
        # F-row title doesn't have a feature doc; fall through to block-id.
    # Step 3: backlog block-id if `^id` exists (dots→dashes for dotted R handles).
    anchor = _anchor_of(row.identifier)
    if anchor in block_ids:
        return f"[[{name} Backlog#^{anchor}|{row.identifier}]]"
    # Step 5: plain text — better than a dead link.
    return row.identifier


# ============================================================
# Q.md section management
# ============================================================


def find_section_bounds(q_lines: list[str], name: str) -> Optional[tuple[int, int]]:
    """Find the [start, end) line range of this anchor's section in Q.md, if present."""
    banner_re = re.compile(QMD_BANNER_RE_TEMPLATE.format(name=re.escape(name)))
    start = None
    for i, line in enumerate(q_lines):
        if banner_re.match(line):
            start = i
            break
    if start is None:
        return None
    # End: the next H1 starting with `# [` or end of file
    end = len(q_lines)
    for j in range(start + 1, len(q_lines)):
        if re.match(r"^# \[", q_lines[j]):
            end = j
            break
    return (start, end)


def find_insertion_point(q_lines: list[str]) -> int:
    """Return the line index where a new section should be inserted (top of body)."""
    # Skip past YAML frontmatter if present
    if q_lines and q_lines[0].startswith("---"):
        for j in range(1, len(q_lines)):
            if q_lines[j].startswith("---"):
                # Insertion just after this line
                insertion = j + 1
                # Skip any blank lines right after frontmatter
                while insertion < len(q_lines) and q_lines[insertion].strip() == "":
                    insertion += 1
                return insertion
    return 0


def rewrite_qmd_section(name: str, section_lines: list[str]) -> str:
    """Update Q.md: remove existing section for `name` (if any) and insert the
    new section at the top of the body. Returns a one-line summary."""
    if not Q_MD.is_file():
        sys.stderr.write(f"queries-render: error — Q.md not found at {Q_MD}\n")
        sys.exit(2)
    try:
        text = Q_MD.read_text(encoding="utf-8")
    except OSError as e:
        sys.stderr.write(f"queries-render: error reading Q.md: {e}\n")
        sys.exit(2)
    q_lines = text.splitlines()
    summary_parts: list[str] = []
    # Dedupe ALL existing sections for this anchor — not just the first match.
    # Duplicates can exist when the H1 banner template changed (e.g., the
    # fallback chain landed on different targets in past runs), leaving older
    # forms that the prior single-match dedupe missed. Loop until stable.
    removed = 0
    while True:
        bounds = find_section_bounds(q_lines, name)
        if bounds is None:
            break
        start, end = bounds
        del q_lines[start:end]
        removed += 1
    if removed > 0:
        summary_parts.append(
            "removed existing" if removed == 1
            else f"removed {removed} existing"
        )
    if section_lines:
        insertion = find_insertion_point(q_lines)
        # Ensure a blank line separating the new section from what follows
        block = list(section_lines)
        # Add a trailing blank line if next existing line isn't already blank
        if insertion < len(q_lines) and q_lines[insertion].strip() != "":
            block.append("")
        q_lines[insertion:insertion] = block
        summary_parts.append("wrote new section at top")
    else:
        summary_parts.append("no new section (anchor empty)")
    new_text = "\n".join(q_lines)
    if not new_text.endswith("\n"):
        new_text += "\n"
    try:
        Q_MD.write_text(new_text, encoding="utf-8")
        _selffire(Q_MD)
    except OSError as e:
        sys.stderr.write(f"queries-render: error writing Q.md: {e}\n")
        sys.exit(2)
    return " + ".join(summary_parts)


# ============================================================
# Mechanical staleness sweep — the cheap, script-decidable subset of
# /groom § 2a, run on the backlog BEFORE rendering so the render never shows or
# counts a stale row. ONLY date/placement-decidable cases (no agent judgment):
#   1. A `[Done]`-bracketed row sitting in a non-Done H2 → relocated to the
#      first `## Done` section (keeps the file honest; the render already hides
#      Done rows, but the backlog shouldn't accumulate them in live horizons).
#   2. A `[Verify-by YYYY-MM-DD]` row whose date is past → bracket rewritten to
#      `[Done — auto-Done …]` and relocated to `## Done` (removes the phantom
#      Verify from the display).
# Everything judgment-heavy ([Watching Nd] body-date expiry, lazy states,
# blocker-resolved, [Ready] hedging, bracket/H2 mismatch) stays in /groom.
# ============================================================

def _is_top_level_row(line: str) -> bool:
    if ROW_OPENER_H3_RE.match(line):
        return True
    if line.startswith("- **") and ROW_OPENER_BULLET_RE.match(line) and _extract_bullet_bracket(line):
        return True
    return False


def sweep_stale_brackets(backlog_file: Path) -> list[str]:
    """Apply the two mechanical staleness fixes to the backlog IN PLACE.
    Returns a list of change descriptions (empty == no-op). Conservative: only
    rewrites rows it is certain about; leaves everything else for /groom."""
    import datetime
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    today = datetime.date.today().isoformat()
    n = len(lines)

    cur_h2 = None
    row_starts: list[tuple[int, str]] = []
    for idx, l in enumerate(lines):
        m = H2_HEADING_RE.match(l)
        if m:
            cur_h2 = m.group(1).strip()
            continue
        if cur_h2 is None:
            continue
        if _is_top_level_row(l):
            row_starts.append((idx, cur_h2))
    h2_idxs = [idx for idx, l in enumerate(lines) if H2_HEADING_RE.match(l)]
    start_only = sorted(s for s, _ in row_starts)

    def next_boundary(start: int) -> int:
        cands = [s for s in start_only if s > start] + [h for h in h2_idxs if h > start] + [n]
        return min(cands)

    moves: list[tuple[int, int, Optional[str], str]] = []
    for (start, h2) in row_starts:
        if h2.startswith("Done"):
            continue
        opener = lines[start]
        bracket = _extract_bullet_bracket(opener) or _extract_h3_bracket(opener)
        end = next_boundary(start)
        if bracket.startswith("Done"):
            moves.append((start, end, None, f"moved stale [Done] row out of ## {h2} → ## Done"))
        else:
            mvb = _VERIFY_BY_RE.match(bracket)
            if mvb and mvb.group(1) < today:
                new_opener = opener.replace(
                    f"[{bracket}]",
                    f"[Done — auto-Done {today}: Verify-by {mvb.group(1)} window expired]",
                    1,
                )
                moves.append((start, end, new_opener,
                              f"auto-Done expired [Verify-by {mvb.group(1)}] from ## {h2}"))

    if not moves:
        return []

    remove: set[int] = set()
    moved_blocks: list[list[str]] = []
    descs: list[str] = []
    for (start, end, new_opener, desc) in moves:
        block = lines[start:end]
        if new_opener is not None:
            block = [new_opener] + block[1:]
        while block and block[-1].strip() == "":
            block.pop()
        moved_blocks.append(block)
        remove.update(range(start, end))
        descs.append(desc)

    out: list[str] = []
    inserted = False
    for idx, l in enumerate(lines):
        if idx in remove:
            continue
        out.append(l)
        if not inserted:
            mm = H2_HEADING_RE.match(l)
            if mm and mm.group(1).strip().startswith("Done"):
                out.append("")
                for block in moved_blocks:
                    out.extend(block)
                    out.append("")
                inserted = True
    if not inserted:
        out.append("")
        out.append("## Done")
        for block in moved_blocks:
            out.extend(block)
            out.append("")

    # Collapse any 3+ consecutive blank lines introduced at the seams.
    collapsed: list[str] = []
    blanks = 0
    for l in out:
        if l.strip() == "":
            blanks += 1
            if blanks <= 1:
                collapsed.append(l)
        else:
            blanks = 0
            collapsed.append(l)

    backlog_file.write_text("\n".join(collapsed) + "\n", encoding="utf-8")
    _selffire(backlog_file)
    return descs


# ============================================================
# Main
# ============================================================


def main() -> int:
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("name", help="backlog filename prefix (NOT the .anchor slug) — "
                                "e.g. 'Tink', 'Scout', 'LUMEN'")
    p.add_argument("--print-only", action="store_true",
                   help="print the would-be section to stdout, don't touch Q.md")
    p.add_argument("--no-sweep", action="store_true",
                   help="skip the mechanical staleness sweep (render only)")
    args = p.parse_args()
    name = args.name.strip()

    # Locate the backlog
    backlogs = audit_q.find_anchor_backlogs(VAULT_ROOT)
    backlog_file = backlogs.get(name)
    if backlog_file is None:
        sys.stderr.write(f"queries-render: error — no backlog found for anchor '{name}'\n")
        sys.stderr.write(f"  searched {VAULT_ROOT} for '* Backlog.md' under */Plan|*/Track\n")
        # The key is the backlog filename prefix, not the `.anchor` slug — they
        # diverge for any anchor whose display name isn't already all-caps.
        # Name the near-miss rather than leaving the caller to conclude the
        # anchor is unwritable (which has already happened once).
        near = sorted(k for k in backlogs if k.lower() == name.lower())
        if near:
            sys.stderr.write(
                "  did you mean '%s'? this argument is the backlog filename "
                "prefix, not the .anchor slug\n" % "' / '".join(near))
        return 1

    # Mechanical staleness sweep — conditional by nature (only rewrites rows that
    # are actually stale), run BEFORE the render so the render never surfaces stale
    # state. Skipped with --print-only (don't mutate when just previewing).
    sweep_descs: list[str] = []
    if not args.no_sweep and not args.print_only:
        sweep_descs = sweep_stale_brackets(backlog_file)

    # Parse the backlog (after the sweep, so the render reflects the fixes)
    rows = parse_backlog(backlog_file)

    # Build vault index for link resolution (needed for Q-marker counts)
    vault_index = audit_q.build_vault_index(VAULT_ROOT)

    # Derive banner
    banner = derive_banner(name, rows, backlog_file, vault_index)

    # Per-Ready/Active next-action sub-bullets (the no-user next step each
    # agent-actionable row will take) — surfaced under each such row.
    next_actions = extract_next_actions(backlog_file)
    # Per-Verify/Watching concrete-question sub-bullets — the yes/no the user answers.
    verify_questions = extract_verify_questions(backlog_file)

    # F231 (2026-07-10): the `{name} queries.md` render is now the SINGLE canonical
    # view of the anchor — the Q.md per-anchor section IS that same body, copied.
    # The query file is what goes into the queue file (per user); there is no
    # separate horizon render for Q.md. Build the queries body once (pure), copy it
    # into the Q.md section under the queue-file banner (which links to queries.md),
    # and write queries.md itself with its anchor-linked banner.
    # T551 — Q.md is Dan's screen and drops rows parked behind a pebble (and
    # anything chained to one); `{name} queries.md` below is the agent's working
    # view and keeps them. One renderer, two row sets — see
    # `pebble_suppressed_ids` for why the divergence lives here rather than
    # inside the render.
    hidden = pebble_suppressed_ids(rows, name)
    qmd_rows = [r for r in rows if r.identifier not in hidden]
    body = build_queries_body(name, banner, qmd_rows, vault_index, next_actions,
                              verify_questions, backlog_file)

    # Compose section = queue-file banner + the same queries body.
    if banner is None:
        # Empty anchor — section is removed if present
        section_lines: list[str] = []
    else:
        section_lines = [banner, ""]
        section_lines.extend(body or [])

    if args.print_only:
        print("\n".join(section_lines))
        return 0

    summary = rewrite_qmd_section(name, section_lines)
    # Write {name} queries.md (same body, anchor-linked banner) — the click-into
    # page, fully script-owned.
    rendered_q = render_queries_doc(name, banner, rows, vault_index, next_actions, verify_questions, backlog_file)
    # Lazy worktree-check refresh — only on the canonical anchor's render, never
    # blocking (mirrors the retired /triage's background rescan trigger).
    if name == WORKTREE_CANONICAL_ANCHOR:
        _fire_worktree_rescan()
    # Counts for the summary line
    eligible = [r for r in rows if _row_should_render(r)]
    sweep_note = f"; swept {len(sweep_descs)} stale row(s)" if sweep_descs else ""
    q_note = "; rendered queries.md" if rendered_q else ""
    print(f"queries-render: {name} — {summary}; rendered {len(eligible)} bullet(s){sweep_note}{q_note}")
    for d in sweep_descs:
        print(f"  sweep: {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
