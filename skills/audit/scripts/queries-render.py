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
# Banner derivation (mirrors audit_q.derive_anchor_banner)
# ============================================================


def _pick_arrow_link(line: str, identifier: str) -> Optional[str]:
    """T012: choose the row's OWN doc among its `→ [[…]]` links — prefer the
    LAST one whose basename opens with the row's identifier (`F230 — …` for
    row F230), else the FIRST arrow link. A plain first-match (the old
    `ARROW_LINK_RE.search`) picks a prose arrow on rows like F149 whose
    own-doc arrow trails several prose arrows; plain last-match fails on
    F220-style rows with a prose arrow after the own-doc one."""
    matches = [m.group(1) for m in ARROW_LINK_RE.finditer(line)]
    if not matches:
        return None
    own = [m for m in matches
           if m.split("#")[0].split("|")[0].strip().startswith(f"{identifier} ")]
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


def _read_open_questions(target_path: Path) -> list[tuple[str, str, str]]:
    """Pending open questions as (qid, question_text, recommendation) — mirrors
    _read_q_marker_count's pending gate but captures the human-facing text so the
    queue file can LIST the actual questions inline (user 2026-07-18: a bare
    `(NQ)` badge is unreadable — the questions themselves must be visible in
    Q.md, exactly like the Verifications section shows each verify's text)."""
    try:
        lines = target_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    out: list[tuple[str, str, str]] = []
    in_resolved = False
    cur_id = cur_text = cur_rec = ""

    def flush():
        nonlocal cur_id, cur_text, cur_rec
        if cur_id:
            out.append((cur_id, cur_text.strip(), cur_rec.strip()))
        cur_id = cur_text = cur_rec = ""

    for line in lines:
        if line.startswith("## "):
            flush()
            in_resolved = line[3:].strip().lower().startswith(("resolved", "removed"))
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
    flush()
    return out


def _read_row_inline_questions(backlog_file: Path, r: "Row") -> list[tuple[str, str, str]]:
    """Pending Qs hosted INLINE in a backlog row's own sub-bullets, as
    (qid, question_text, recommendation) — the same shape `_read_open_questions`
    returns for doc-backed rows.

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
    out: list[tuple[str, str, str]] = []
    # Scan the row's sub-bullets: everything indented under the opener, stopping
    # at the next H2, H3, or top-level bullet (the next row).
    for line in lines[r.line_num:]:
        if H2_HEADING_RE.match(line) or line.startswith("### ") or line.startswith("- **"):
            break
        if not line.strip():
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
        out.append((qid, text.strip(), rec))
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


def _row_q_count(r: "Row", vault_index: dict) -> int:
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
    # Bare [Questions] with no resolvable doc (T-/B-row inline form) means
    # exactly 1 pending Q by bracket discipline (C24 maintains it).
    return 1 if "Questions" in r.bracket else 0


def derive_banner(name: str, rows: list[Row], backlog_file: Path,
                  vault_index: dict) -> Optional[str]:
    """Compute the H1 banner line. Returns None if anchor has zero items."""
    live = [r for r in rows
            if r.horizon in LIVE_HORIZON_H2S
            and not r.bracket.startswith("Done")]
    actionable = [r for r in live if r.horizon in ACTIVE_HORIZONS_BANNER]
    # F260 — [Implementing] is the feature-lifecycle alias for [Active]; both
    # are in-progress and Runnable, so both count.
    active_n = sum(1 for r in actionable if r.bracket in ("Active", "Implementing"))
    # `Agreed` is the feature-lifecycle synonym for `Ready` (per [[SKA workflow]]
    # / feature/SKILL.md) — count it as Ready so the banner doesn't drop Agreed
    # rows from the agent-actionable headline.
    # Exclude an empty B-QFix (0 residuals) — it's not actionable Ready work.
    _qfix_empty = _count_qfix_subs(backlog_file) == 0
    ready_n = sum(1 for r in actionable if r.bracket in ("Ready", "Agreed")
                  and not (r.identifier == "B-QFix" and _qfix_empty))
    verify_n = sum(1 for r in actionable if r.bracket == "Verify")
    # Questions count: sum of Q-markers across linked feature docs for each
    # `[Questions]` / `[N Questions]` row, across **every rendered horizon**
    # (not just ACTIVE_HORIZONS_BANNER). The body renders `[Questions]` rows
    # under `## Later` via the LATER_RENDERED_BRACKETS_PREFIX filter — they
    # must count in the banner too, otherwise banner-vs-body disagree
    # (observed 2026-06-04 on MUX: banner said `Questions 0` while body
    # showed F037 + F011 as `[Questions]` under `## Later`).
    questions_n = 0
    for r in live:
        if r.horizon not in BODY_RENDERED_HORIZONS_FOR_QUESTIONS:
            continue
        if "Questions" not in r.bracket:
            continue
        # Count via the same resolution `_row_q_count` uses (T012 — this block
        # previously re-implemented it with case-sensitive index lookups that
        # never matched the lower-cased vault_index keys, so every row fell to
        # the count-as-1 fallback). Floor of 1: a bracket-claim never counts 0.
        questions_n += _row_q_count(r, vault_index) or 1
    # F260 — [User] rows (gated on a user ACTION) join the User bucket, counted
    # across the same rendered horizons as questions, one per row.
    user_n = sum(
        1 for r in live
        if r.horizon in BODY_RENDERED_HORIZONS_FOR_QUESTIONS
        and r.bracket == "User"
    )
    # Per-horizon counts (live, non-Done)
    horizon_counts = {h: 0 for h in ("Active", "Ready", "Now", "Next", "Later", "Verify", "Icebox")}
    for r in rows:
        if r.horizon in horizon_counts and not r.bracket.startswith("Done"):
            horizon_counts[r.horizon] += 1
    # Icebox count from {slug} Icebox.md
    icebox_file = backlog_file.parent / f"{name} Icebox.md"
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
        questions_n > 0
        or user_n > 0
        or verify_n > 0
        or horizon_counts["Verify"] > 0
    )
    has_a = active_n > 0 or ready_n > 0
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
    # F260 — the two actionable buckets are keyed on WHOSE PLATE the work is on:
    #   Runnable = [Ready]/[Agreed] + [Active]/[Implementing] — every row crank
    #     will actually run. The "Runnable" label is what makes folding [Active]
    #     in honest: it promises will-run-if-you-crank, not fresh/not-started, so
    #     it supersedes the F250 #9 / F254 C1 "Ready 3 vs frontier 2" anomaly
    #     (that was the WORD "Ready" implying not-started, not the count).
    #   User = [Questions] + [User] — everything gated on a user answer or a
    #     user action (completes F259's [User] fold, which never reached this
    #     authoritative path). [Verify] is dropped from the actionable pair (it
    #     collects junk) — it stays a horizon count and still drives the U TAG.
    runnable_n = ready_n + active_n
    user_actionable_n = questions_n + user_n
    banner = (
        f"# [{tag}]  {slug_label}  -  "
        f"Runnable {runnable_n}    User {user_actionable_n}   |   "
        f"Now {horizon_counts['Now']}    Next {horizon_counts['Next']}    "
        f"Later {horizon_counts['Later']}    Verify {horizon_counts['Verify']}    "
        f"Icebox {horizon_counts['Icebox']}"
        f"{qfix_suffix}"
    )
    return banner


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
    """True if a row is eligible for rendering in the Q.md body."""
    if row.bracket.startswith("Done"):
        return False
    # F283 — `[Verify-by <date>]` renders NOWHERE. The bracket is a promise that
    # nothing happens until the date, and `sweep_stale_brackets` auto-Dones the
    # row when the date arrives, so it is set-and-forget by construction and
    # showing it only crowds the checks that still want a look. Excluded here
    # rather than in `build_queries_body` so the coverage assertion never sees
    # it as an unclaimed row.
    if _VERIFY_BY_RE.match(row.bracket):
        return False
    if row.horizon == "Later":
        # Only Questions / Verify / Verify-by under Later
        return (
            "Questions" in row.bracket
            or row.bracket.startswith("Verify")
        )
    if row.horizon in ("Active", "Ready", "Now", "Next", "Verify"):
        return True
    # Legwork / Icebox / Done / Notes — never rendered
    return False


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
            cut = window_start + offset + 1
            return text[:cut].rstrip() + "..."
    # Fall back to word boundary near soft_cap
    cut = soft_cap
    while cut > 0 and text[cut] not in " \t":
        cut -= 1
    if cut <= 0:
        cut = soft_cap
    return text[:cut].rstrip() + "..."


def _bullet_bracket_display(bracket: str) -> str:
    """Return the bracket text as it should appear in the Q.md bullet."""
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
    gated_by: dict[str, list[str]] = {}
    for r in rows:
        m = _BLOCKED_HANDLE_RE.match(r.bracket)
        if m and r.horizon in ACTIVE_HORIZONS_BANNER:
            gated_by.setdefault(m.group(1), []).append(r.identifier)
    # `[Done]` is the one further exclusion: a resolved blocker means the WAITING
    # row is stale, which is a different finding and already /groom's.
    blockers = [r for r in rows
                if r.identifier in gated_by and not r.bracket.startswith("Done")]
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
    ready = _by_horizon([r for r in eligible if id(r) not in promoted
                         and r.bracket in READY_ACTIVE_BRACKETS
                         and not (r.identifier == "B-QFix" and qfix_empty)])
    qs = _by_horizon([r for r in eligible if id(r) not in promoted and "Questions" in r.bracket])
    # The ledger. `[Waiting]` rides with `[Blocked <handle>]` because both mean
    # "not moving, and not by the user's hand" — the difference is only who
    # eventually moves it, which the bracket itself already says.
    blocked = [r for r in eligible if id(r) not in promoted
               and (r.bracket.startswith("Blocked") or r.bracket.startswith("Waiting"))]
    verifs = [r for r in eligible if id(r) not in promoted
              and (r.bracket.startswith("Verify") or r.bracket.startswith("Watching"))]
    # F259 minted `[User]` for an action only the human can perform (log in,
    # click a permission dialog, run an experiment on a display the agent
    # cannot see), and the banner has counted them since — but no section ever
    # claimed them, so every one fell into `## Other` beside unbracketed
    # leftovers and went unread. Dan, 2026-08-05: *"I don't even see a T21. I
    # don't even see it there."* A pile the user is the ONLY possible actor for
    # is the last thing that should be in the catch-all.
    users = [r for r in eligible if id(r) not in promoted and r.bracket == "User"]
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

    # F283 — Blockers first. Computed, never authored: these rows are here only
    # because something else names them. Each bullet says WHAT it holds up, which
    # is the whole point — the `[Blocked <handle>]` edge was previously readable
    # only from the waiting end, so a blocker had no idea it was one.
    if blockers:
        _h2("## Blockers")
        for r in blockers:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            btxt = _bullet_bracket_display(r.bracket) if r.bracket else "**[no state]**"
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
            body.append(f"- {link} — {btxt} **gates {waiters}**{parked}"
                        + (f" — {txt}" if txt else ""))
    # Ready first among the working sections: it is short, it is what the agent
    # can act on with no user involvement, and it orients everything below it.
    if ready:
        _h2("## Ready")
        for r in ready:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            na = next_actions.get(r.identifier)
            na_txt = (_truncate_body(na, 200) if na
                      else "⚠ none declared — not really Ready; add a no-user next-action or rebracket")
            body.append(f"- {link} — **Next:** {na_txt}")
    # Questions — the one pile the user personally unsticks. Kept separate from
    # Blocked (F283 Q2 (A)): the axis that earns a section break is "can the user
    # act on it", not "is it stopped".
    if qs:
        _h2("## Questions")
        for r in qs:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            txt = _truncate_body(r.body, 160)
            # Pending-Q count in bold parens — the user sees how many answers the
            # feature needs at a glance (`[[F181 …]] **(5Q)**`). Per /query North Star.
            n = _row_q_count(r, vault_index)
            cnt = f" **({n}Q)**" if n else ""
            # The Q-bearing doc is the entry's home — link it first, demote the
            # backlog-row link to a parenthesized `(row)` pointer (same shape as
            # the F235 Verify entries). Inline T-/B-rows keep the row link: the
            # row carries the Qs itself.
            doclink = _q_home_link(r, vault_index, backlog_file)
            if doclink:
                rowlink = re.sub(r"\|[^\]|]*\]\]$", "|row]]", link) if link.rstrip().endswith("]]") else link
                body.append(f"- {doclink}{cnt} ({rowlink})" + (f" — {txt}" if txt else ""))
            else:
                body.append(f"- {link}{cnt}" + (f" — {txt}" if txt else ""))
            # Inline each pending question's TEXT under the row (user 2026-07-18:
            # the queue must SHOW the questions, not just a (NQ) badge). Mirrors
            # the Verifications section. A doc-backed row reads its feature doc's
            # `## Open Questions`; a doc-less T-/B-row reads its OWN sub-bullets
            # (F233 inline form) — the latter used to be skipped, which left the
            # question invisible everywhere the user looks (Dan, 2026-08-02).
            qdoc = _row_q_doc_path(r, vault_index)
            q_entries = (_read_open_questions(qdoc) if qdoc
                         else _read_row_inline_questions(backlog_file, r))
            # A doc-backed Q is a PREVIEW — the answerable form (options,
            # block-id, Recommendation) lives one click away in the feature doc,
            # so 200 chars is enough to identify it. An inline row Q has no such
            # home: this render is the only place the user will read it, so it
            # must carry its `**(A)**`/`**(B)**` options or it is unanswerable
            # (North Star 2 — everything needed to answer is in the entry).
            qlimit = 200 if qdoc else 420
            if q_entries:
                for qid, qtext, qrec in q_entries:
                    if not qtext:
                        continue
                    rec_txt = f" · *{_truncate_body(qrec, 90)}*" if qrec else ""
                    # DISPLAY PREVIEW, not a formal ask-format Q entry. The
                    # answerable Qs (block-IDs, Recommendations, option bullets)
                    # live in the source feature doc's `## Open Questions`, which
                    # audit-q enforces there. This inline copy is a dashboard
                    # preview only, so it deliberately does NOT lead with
                    # `- **Q<n>` — that shape is parsed by audit-q's Q_HEADER_RE
                    # as a formal Q and would trip C6 (block-id)/C9 (recommendation)
                    # on every render of this generated file.
                    body.append(f"    - {qid} — {_truncate_body(qtext, qlimit)}{rec_txt}")
    # F283 — the visibility ledger. Scanned, not worked: "if it's legitimately
    # blocked on something else, then I don't really want to see it, I just wanna
    # work on the thing that it's blocked by." It renders anyway so that nothing
    # silently disappears, which is the defect that produced this feature.
    if blocked:
        _h2("## Blocked")
        for r in blocked:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            btxt = _bullet_bracket_display(r.bracket)
            txt = _truncate_body(r.body, 160)
            body.append(f"- {link} — {btxt}" + (f" {txt}" if txt else ""))
    # Verifications last, deliberately below the fold: "it's not actually a
    # problem if a verification is not verified if nothing is depending on it" —
    # and when something does depend on it, Blockers has already promoted it out
    # of here to the top of the file.
    if verifs:
        _h2("## Verifications")
        for i, r in enumerate(verifs, 1):
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            # Prefer the row's concrete `Verify:` question; fall back to a ⚠ so a
            # row with only jargon body is flagged (not silently shown vague).
            q = verify_questions.get(r.identifier)
            qtxt = (_truncate_body(q, 240) if q
                    else "⚠ no concrete question — add a `- **Verify:** <yes/no question>` sub-bullet to the row")
            # F235: the feature doc is the verification's home — link it first,
            # demote the backlog-row link to a parenthesized `(row)` pointer.
            doclink = _feature_doc_link(r, vault_index, backlog_file)
            if doclink:
                rowlink = re.sub(r"\|[^\]|]*\]\]$", "|row]]", link) if link.rstrip().endswith("]]") else link
                body.append(f"- **V{i}** {doclink} ({rowlink}) — {qtxt} · **yes / no**")
            else:
                body.append(f"- **V{i}** {link} — {qtxt} · **yes / no**")
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
        for i, r in enumerate(users, 1):
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            a = user_actions.get(r.identifier)
            atxt = (_truncate_body(a, 240) if a
                    else "⚠ no action stated — add a `- **User:** <what you must do>` sub-bullet to the row")
            body.append(f"- **U{i}** {link} — {atxt}")

    # F284 — the catch-all, emitted last so it never displaces the classified
    # work. Each row shows its bracket VERBATIM: a state the render doesn't know
    # (`[Designing]`), a state gated on the user (`[User]`), the bracket field
    # used as prose (`[big task]`), and the largest class of all — no bracket at
    # all — are all legible as what they are instead of vanishing.
    if other:
        _h2("## Other")
        for r in other:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            btxt = _bullet_bracket_display(r.bracket) if r.bracket else "**[no state]**"
            txt = _truncate_body(r.body, 200)
            body.append(f"- {link} — {btxt}" + (f" {txt}" if txt else ""))
    body.extend(_coverage_warning(
        eligible, [blockers, ready, qs, blocked, verifs, users, other], suppressed))
    if not body:
        body.append("_Nothing pending._")
    return body


def _coverage_warning(eligible: list[Row], sections: list[list[Row]],
                      suppressed: list[Row]) -> list[str]:
    """F284's structural gate: assert the sections PARTITION `eligible`, and make
    a breach visible rather than silent.

    The catch-all makes coverage total by construction, so this can only fire on
    a code defect — a row claimed by two sections (sum exceeds the total) or a
    new deliberate suppression that forgot to register itself (sum falls short).
    Either way the answer is a complaint in the surface the user actually reads,
    NOT a raised exception: aborting the render would delete the whole queue file
    and hide 100% of the work to protest hiding some of it."""
    rendered = sum(len(s) for s in sections)
    total = rendered + len(suppressed)
    if total == len(eligible):
        return []
    sys.stderr.write(
        f"COVERAGE: {len(eligible)} eligible rows, {total} accounted "
        f"({rendered} rendered + {len(suppressed)} suppressed)\n")
    verb = "unrendered" if total < len(eligible) else "double-rendered"
    return ["", "## ⚠ Coverage failure",
            f"- {abs(len(eligible) - total)} row(s) {verb} — the queue file is "
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
    queries_file = backlog_file.parent / f"{name} queries.md"
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
        anchor_dir_name = backlog_file.parent.parent.name
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
        h1 = (f"# [-]  [[{anchor_page_name}|{name}]]  -  Runnable 0    User 0   |   "
              f"Now 0    Next 0    Later 0    Verify 0    Icebox 0")
        body = ["_Nothing pending._"]
    else:
        # The Q.md banner links the name to `{name} queries` (so the user clicks
        # over); inside queries.md that would be a self-link — retarget to the anchor.
        h1 = banner.replace(f"[[{name} queries|{name}]]", f"[[{anchor_page_name}|{name}]]")
        body = built
    # Preserve existing frontmatter; else write a default.
    desc = (f"description: {name} queries — mechanically rendered from the backlog "
            "(Blockers / Ready+Next / Questions / Blocked / Verifications / Other), "
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
    body = build_queries_body(name, banner, rows, vault_index, next_actions,
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
