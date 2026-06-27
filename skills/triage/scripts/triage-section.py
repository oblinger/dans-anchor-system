#!/usr/bin/env python3
"""triage-section.py — rewrite a single anchor's per-anchor section in Q.md.

Usage: triage-section.py <NAME>

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
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
ACTIVE_HORIZONS_BANNER = {"Active", "Ready", "Now", "Next", "Legwork"}
# Banner `Questions` total counts `[Questions]` rows ONLY in active horizons
# (matches ACTIVE_HORIZONS_BANNER above) — `## Later` is deferred by user
# intent and shouldn't pull weight in the headline number. Per user direction
# 2026-06-04 (final): Later [Questions] are visible in the body (rendered
# under ## Later for context) but invisible to the banner count.
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
ROW_OPENER_BULLET_RE = re.compile(
    r"^- \*\*"
    r"(?:\[\[)?"
    r"(?:\[[A-Z]+\]\s+)?"
    r"([A-Za-z][A-Za-z0-9_\-]*)\b"
)

# H3 row opener (HA-style): `### F068 — Title [Bracket]` or `### BUG — Title [Bracket]`.
ROW_OPENER_H3_RE = re.compile(
    r"^### "
    r"(?:\[[A-Z]+\]\s+)?"
    r"([A-Za-z][A-Za-z0-9_\-]*)\b"
)

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
    # the fallback chain landed on — `[[{NAME} queries|{NAME}]]`, `[[{NAME} Triage|{NAME}]]`,
    # `[[{NAME}|{NAME}]]`, or plain `{NAME}` (no link). The display label is
    # always `{NAME}`; that's what we match on. Critical for the dedupe step:
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
            arrow = ARROW_LINK_RE.search(line)
            rows.append(Row(
                line_num=line_num,
                raw_line=line,
                horizon=current_horizon,
                identifier=identifier,
                is_h3=True,
                bracket=bracket,
                body=body,
                arrow_link=arrow.group(1) if arrow else None,
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
            arrow = ARROW_LINK_RE.search(line)
            rows.append(Row(
                line_num=line_num,
                raw_line=line,
                horizon=current_horizon,
                identifier=identifier,
                is_h3=False,
                bracket=bracket,
                body=body,
                arrow_link=arrow.group(1) if arrow else None,
            ))
    return rows


# ============================================================
# Banner derivation (mirrors audit_q.derive_anchor_banner)
# ============================================================


def _read_q_marker_count(target_path: Path) -> int:
    try:
        target_text = target_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return 0
    return len(re.findall(r"\bQ\d+\s+—", target_text))


def derive_banner(name: str, rows: list[Row], backlog_file: Path,
                  vault_index: dict) -> Optional[str]:
    """Compute the H1 banner line. Returns None if anchor has zero items."""
    live = [r for r in rows
            if r.horizon in LIVE_HORIZON_H2S
            and not r.bracket.startswith("Done")]
    actionable = [r for r in live if r.horizon in ACTIVE_HORIZONS_BANNER]
    active_n = sum(1 for r in actionable if r.bracket == "Active")
    # `Agreed` is the feature-lifecycle synonym for `Ready` (per [[SKA workflow]]
    # / feature/SKILL.md) — count it as Ready so the banner doesn't drop Agreed
    # rows from the agent-actionable headline.
    ready_n = sum(1 for r in actionable if r.bracket in ("Ready", "Agreed"))
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
        # Resolve the linked feature doc
        target_basename = r.arrow_link or (f"{r.identifier}" if r.identifier.startswith("F") else None)
        if not target_basename:
            continue
        # Strip `#section` and `|alias` from the basename
        target_basename = target_basename.split("#")[0].split("|")[0].strip()
        # Resolve to a path via vault index — prefer exact basename match
        candidates = vault_index.get(target_basename) or []
        # Try with .md extension stripped
        if not candidates:
            candidates = vault_index.get(target_basename + ".md") or []
        # Try fuzzy match: any basename starting with `F<n> —` or `F<n>` prefix
        if not candidates and r.identifier.startswith("F"):
            for bn, paths in vault_index.items():
                if bn.startswith(r.identifier + " —") or bn == r.identifier:
                    candidates = paths
                    break
        if not candidates:
            # Bracket-claim but no resolvable link: count as 1
            questions_n += 1
            continue
        target_path = candidates[0]
        q_count = _read_q_marker_count(target_path)
        questions_n += q_count if q_count > 0 else 1
    # Per-horizon counts (live, non-Done)
    horizon_counts = {h: 0 for h in ("Active", "Ready", "Now", "Next", "Later", "Verify", "Icebox")}
    for r in rows:
        if r.horizon in horizon_counts and not r.bracket.startswith("Done"):
            horizon_counts[r.horizon] += 1
    # Icebox count from {NAME} Icebox.md
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
    # Per F176: H1 link target is `{NAME} queries.md` (the /query drain page where
    # the user actually answers questions). Fallback chain when files don't
    # exist yet (avoids emitting a C1-failing wiki-link in Q.md):
    #   `{NAME} queries` → `{NAME} Triage` → `{NAME}` (anchor page) → plain text
    candidates = [f"{name} queries", f"{name} Triage", name]
    h1_target = next((c for c in candidates if c in vault_index), None)
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
    # Headline numbers are the two MERGED groups (per the 2026-05-24 banner
    # simplification): agent-actionable = Active + Ready (+Agreed); user-actionable
    # = pending Questions + [Verify]-bracket rows. The per-horizon group below
    # still shows raw counts (Now/Next/Later/Verify/Icebox) for placement.
    agent_actionable_n = active_n + ready_n
    user_actionable_n = questions_n + verify_n
    banner = (
        f"# [{tag}]  {slug_label}  -  "
        f"Ready {agent_actionable_n}    Questions {user_actionable_n}   |   "
        f"Now {horizon_counts['Now']}    Next {horizon_counts['Next']}    "
        f"Later {horizon_counts['Later']}    Verify {horizon_counts['Verify']}    "
        f"Icebox {horizon_counts['Icebox']}"
        f"{qfix_suffix}"
    )
    return banner


# ============================================================
# Body rendering
# ============================================================

# Horizons we render in the body
BODY_HORIZON_ORDER = ["Active", "Ready", "Now", "Next", "Later", "Verify"]

# Brackets that DO get rendered under ## Later (everything else is hidden)
LATER_RENDERED_BRACKETS_PREFIX = ("Questions", "Verify")  # "Verify" matches "Verify" and "Verify-by ..."


def _row_should_render(row: Row) -> bool:
    """True if a row is eligible for rendering in the Q.md body."""
    if row.bracket.startswith("Done"):
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
    owning anchor's next /triage or /audit q-fix needs to drive to zero per
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
READY_ACTIVE_BRACKETS = {"Ready", "Agreed", "Active"}

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


def render_queries_doc(name: str, banner: Optional[str], rows: list[Row],
                       vault_index: dict, next_actions: dict[str, str],
                       verify_questions: dict[str, str], backlog_file: Path) -> bool:
    """Mechanically (re)write `{name} queries.md` from backlog state, as part of
    every triage — the page the user clicks into from Q.md. Fully script-owned
    (per user direction 2026-06-26: *"purely mechanical, done as part of the
    process of doing a triage"*); no agent-authored prose is preserved. To change
    what shows here, edit the backlog rows, not this file.

    Layout: banner H1 (anchor-linked) + three sections rendered from the same
    rows `_row_should_render` admits —
      ## Verifications  ← `[Verify*]` / `[Watching*]` rows (each `**V<n>**` + the
                          row's verify-plan body + `· **yes / no**`)
      ## Ready          ← `[Ready]`/`[Agreed]`/`[Active]` rows, each with its
                          declared `**Next:**` no-user action (⚠ if none)
      ## Questions      ← `[Questions]` rows, linking to the source's open Qs
    Returns False (writes nothing) when the anchor is empty (banner is None)."""
    if banner is None:
        return False
    queries_file = backlog_file.parent / f"{name} queries.md"
    # The Q.md banner links the name to `{name} queries` (so the user clicks
    # over); inside queries.md that would be a self-link — retarget to the anchor.
    h1 = banner.replace(f"[[{name} queries|{name}]]", f"[[{name}|{name}]]")
    block_ids = _extract_block_ids(backlog_file)
    h3_headings = _extract_h3_headings(backlog_file)
    eligible = [r for r in rows if _row_should_render(r)]
    verifs = [r for r in eligible if r.bracket.startswith("Verify") or r.bracket.startswith("Watching")]
    ready = [r for r in eligible if r.bracket in READY_ACTIVE_BRACKETS]
    qs = [r for r in eligible if "Questions" in r.bracket]

    body: list[str] = []
    if verifs:
        body.append("## Verifications")
        for i, r in enumerate(verifs, 1):
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            # Prefer the row's concrete `Verify:` question; fall back to a ⚠ so a
            # row with only jargon body is flagged (not silently shown vague).
            q = verify_questions.get(r.identifier)
            qtxt = (_truncate_body(q, 240) if q
                    else "⚠ no concrete question — add a `- **Verify:** <yes/no question>` sub-bullet to the row")
            body.append(f"- **V{i}** {link} — {qtxt} · **yes / no**")
    if ready:
        body.append("## Ready")
        for r in ready:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            na = next_actions.get(r.identifier)
            na_txt = (_truncate_body(na, 200) if na
                      else "⚠ none declared — not really Ready; add a no-user next-action or rebracket")
            body.append(f"- {link} — **Next:** {na_txt}")
    if qs:
        body.append("## Questions")
        for r in qs:
            link = _bullet_link(r, name, vault_index, block_ids, h3_headings)
            txt = _truncate_body(r.body, 160)
            body.append(f"- {link}" + (f" — {txt}" if txt else ""))
    if not body:
        body.append("_Nothing pending._")

    # Preserve existing frontmatter; else write a default.
    fm = ["---",
          f"description: {name} queries — mechanically rendered from the backlog by "
          "triage (Verifications / Ready+Next / Questions). Do not hand-edit; edit the backlog rows.",
          "---"]
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
    out = fm + ["", h1, ""] + body + [""]
    queries_file.write_text("\n".join(out), encoding="utf-8")
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
    # Step 1: arrow_link if it resolves.
    if row.arrow_link and row.arrow_link in vault_index:
        return f"[[{row.arrow_link}]]"
    # Step 2 (H3 rows): heading link if heading exists.
    if row.is_h3:
        m = re.match(r"^### ([^[]+?)(?:\s*\[[^\]]+\])?\s*$", row.raw_line)
        if m:
            heading = m.group(1).strip()
            if heading in h3_headings:
                return f"[[{name} Backlog#{heading}|{row.identifier}]]"
        if row.identifier in block_ids:
            return f"[[{name} Backlog#^{row.identifier}|{row.identifier}]]"
        return row.identifier  # plain text fallback
    # Step 2 (F-row): try title-as-basename if it resolves.
    if row.identifier.startswith("F") and row.identifier[1:].isdigit():
        m = re.match(r"^- \*\*([^*]+)\*\*", row.raw_line)
        if m:
            title = m.group(1).strip()
            if title in vault_index:
                return f"[[{title}]]"
        # F-row title doesn't have a feature doc; fall through to block-id.
    # Step 3: backlog block-id if `^id` exists.
    if row.identifier in block_ids:
        return f"[[{name} Backlog#^{row.identifier}|{row.identifier}]]"
    # Step 5: plain text — better than a dead link.
    return row.identifier


def _render_bullet(row: Row, name: str, vault_index: dict,
                   block_ids: set[str], h3_headings: set[str]) -> str:
    bracket = _bullet_bracket_display(row.bracket if row.bracket else "")
    link = _bullet_link(row, name, vault_index, block_ids, h3_headings)
    body = _truncate_body(row.body)
    if body:
        return f"- {bracket} {link} — {body}"
    return f"- {bracket} {link}"


def render_body(rows: list[Row], name: str, backlog_file: Path,
                vault_index: dict, next_actions: dict[str, str]) -> list[str]:
    """Render the body H2s + bullets. Returns a list of lines (no trailing
    newline). Resolves every emitted link against vault_index + the backlog's
    actual block-ids + H3 headings — no dead links emitted. For each
    [Ready]/[Active] row, renders a `  - **Next:**` sub-line with the row's
    declared autonomous next-action (or a ⚠ warning when none is declared)."""
    out: list[str] = []
    eligible = [r for r in rows if _row_should_render(r)]
    by_horizon: dict[str, list[Row]] = {}
    for r in eligible:
        by_horizon.setdefault(r.horizon, []).append(r)
    block_ids = _extract_block_ids(backlog_file)
    h3_headings = _extract_h3_headings(backlog_file)
    for h in BODY_HORIZON_ORDER:
        if h not in by_horizon:
            continue
        out.append(f"## {h}")
        for r in by_horizon[h]:
            out.append(_render_bullet(r, name, vault_index, block_ids, h3_headings))
            if r.bracket in READY_ACTIVE_BRACKETS:
                na = next_actions.get(r.identifier)
                if na:
                    out.append(f"  - **Next:** {_truncate_body(na, 200)}")
                else:
                    out.append("  - **Next:** ⚠ none declared — not really Ready; "
                               "add a no-user next-action or rebracket")
    return out


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
        sys.stderr.write(f"triage-section: error — Q.md not found at {Q_MD}\n")
        sys.exit(2)
    try:
        text = Q_MD.read_text(encoding="utf-8")
    except OSError as e:
        sys.stderr.write(f"triage-section: error reading Q.md: {e}\n")
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
    except OSError as e:
        sys.stderr.write(f"triage-section: error writing Q.md: {e}\n")
        sys.exit(2)
    return " + ".join(summary_parts)


# ============================================================
# Mechanical staleness sweep — the cheap, script-decidable subset of
# /groom § 2a, run on the backlog BEFORE rendering so /triage never shows or
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

_VERIFY_BY_RE = re.compile(r"^Verify-by\s+(\d{4}-\d{2}-\d{2})", re.I)


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
    return descs


# ============================================================
# Main
# ============================================================


def main() -> int:
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("name", help="anchor slug, e.g. 'SKA'")
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
        sys.stderr.write(f"triage-section: error — no backlog found for anchor '{name}'\n")
        sys.stderr.write(f"  searched {VAULT_ROOT} for '* Backlog.md' under */Plan|*/Track\n")
        return 1

    # Mechanical staleness sweep — conditional by nature (only rewrites rows that
    # are actually stale), run BEFORE the render so /triage never surfaces stale
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

    # Body: the backlog-derived rows (## Active / ## Ready / ## Now / ## Next /
    # ## Later / ## Verify), per triage SKILL.md § 4. The {NAME} queries.md drain
    # page is the USER-question surface and is reachable via the H1 link (F176) —
    # it is deliberately NOT pasted into the body. Pasting it (the prior F176
    # over-reach) replaced the agent-actionable rows with the queries page, so
    # the banner's Ready/Now counts pointed at an empty body ("Ready 4" with
    # nothing shown). The banner reads the backlog; the body must too.
    body = render_body(rows, name, backlog_file, vault_index, next_actions)

    # Compose section
    if banner is None and not body:
        # Empty anchor — section is removed if present
        section_lines: list[str] = []
    else:
        section_lines = []
        if banner:
            section_lines.append(banner)
            section_lines.append("")
        section_lines.extend(body)

    if args.print_only:
        print("\n".join(section_lines))
        return 0

    summary = rewrite_qmd_section(name, section_lines)
    # Mechanically render {name} queries.md from the backlog (banner +
    # Verifications/Ready+Next/Questions) — the click-into page, fully script-owned.
    rendered_q = render_queries_doc(name, banner, rows, vault_index, next_actions, verify_questions, backlog_file)
    # Counts for the summary line
    eligible = [r for r in rows if _row_should_render(r)]
    sweep_note = f"; swept {len(sweep_descs)} stale row(s)" if sweep_descs else ""
    q_note = "; rendered queries.md" if rendered_q else ""
    print(f"triage-section: {name} — {summary}; rendered {len(eligible)} bullet(s){sweep_note}{q_note}")
    for d in sweep_descs:
        print(f"  sweep: {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
