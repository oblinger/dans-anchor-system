#!/usr/bin/env python3
"""backlog-edit — structured backlog row mutation tool.

Usage:
    backlog-edit.py <slug> <horizon> <row-id> <status> [title] [body]

Args:
    slug      Anchor slug (e.g., SKA, MUX, HA).
    horizon   One of: Now | Next | Later | Active | Ready | Done | Verify
              Or 'same' to keep the existing row's horizon
              (requires the row to already exist; errors otherwise).
              Leading '## ' is stripped if present.
    row-id    F<NNN> | B<n> | B-<slug> | Fnew | Bnew
              Fnew/Bnew mints the next available F or B number from the backlog.
              F-numbers are zero-padded to three digits (F001..F999).
    status    Bracket text (Ready, Questions, Verify, 'Watching 7d', Done, ...)
              Or the literal 'delete' to remove the row entirely.
    title     Row title — goes inside bold `**<row-id> — <title>**`. For
              'delete', omit. Optional for non-delete (defaults to empty,
              giving `**<row-id>** [<status>]`).
    body      Row body text — appended after the bracket as `— <body>`.
              Use for wiki-links (`→ [[F<n> — Title]]`), descriptions,
              dates, etc. Optional.

Row shape produced:
    - **<row-id> — <title>** [<status>] — <body> ^<row-id>
    (title omitted → `**<row-id>**`; body omitted → no trailing `— ...`)

Examples:
    backlog-edit.py SKA Now Fnew Designing "Feature Name" "→ [[F095 — Feature Name]]"
    backlog-edit.py SKA same F015 Done "Original Title" "Done 2026-06-02"
    backlog-edit.py SKA same F015 delete

Side effects:
    1. Mutates the anchor's backlog file.
    2. Runs `audit-backlog <slug> --fix` to refresh Q.md.
    3. Writes a per-anchor and global Messages entry recording the edit.

Q-management mode (F128):
    backlog-edit.py <slug> <row-id> -Q <add|resolve|remove|rewrite> [-n <n>] [...]
    Run `backlog-edit.py X F1 -Q add --help` for the full Q-mode help.
    Triggered by presence of the `-Q` flag anywhere in argv. The Q-mode
    does NOT take a horizon argument — it edits the feature doc's
    `## Open Questions` block, not the backlog row.
"""

from __future__ import annotations

import json
import os
import re
import sys
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------
# Config

HOME = Path.home()
VAULT_ROOT = HOME / "ob" / "kmr"
SENTINEL = HOME / ".claude" / "state" / "agent-messages"
STATE_FILE = HOME / ".config" / "ob-skills" / "backlog-edit" / "state.json"

VALID_HORIZONS = {"Now", "Next", "Later", "Active", "Ready", "Done", "Verify", "Icebox"}
ICEBOX_HORIZON = "Icebox"
ICEBOX_DEFAULT_H2 = "Iced"
SKIP_PATH_FRAGMENTS = ("/.history/", "/worktrees/", "/Yore/", "/.trash/")

# A Questions-bracket promise: the linked target must contain ≥1 of these.
Q_MARKER_RE = re.compile(r"\bQ\d+\s+—")
# Extract the basename from the first wiki-link in a body string.
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
# Statuses that assert the Questions-target promise.
QUESTIONS_STATUS_RE = re.compile(r"^(\d+\s+)?Questions?$", re.IGNORECASE)
# Statuses to nudge toward Later/Icebox.
VERIFY_WATCHING_FAMILY = ("Verify", "Watching")
NUDGE_BUCKETS = {"Now", "Next", "Active", "Ready"}


# --------------------------------------------------------------------------
# Errors

class BacklogEditError(SystemExit):
    def __init__(self, msg):
        super().__init__(f"backlog_edit: {msg}")


# --------------------------------------------------------------------------
# Anchor resolution

def find_backlog(slug):
    """Locate `<slug> Backlog.md` somewhere under VAULT_ROOT."""
    target = f"{slug} Backlog.md"
    matches = []
    for root, dirs, files in os.walk(VAULT_ROOT, followlinks=True):
        # Skip noisy paths
        if any(frag in root + "/" for frag in SKIP_PATH_FRAGMENTS):
            dirs[:] = []
            continue
        if target in files:
            matches.append(Path(root) / target)
    if not matches:
        raise BacklogEditError(f"no '{target}' found under {VAULT_ROOT}")
    if len(matches) > 1:
        raise BacklogEditError(
            f"multiple '{target}' candidates: " + ", ".join(str(m) for m in matches)
        )
    return matches[0]


def anchor_track_dir(backlog_path):
    """The `{slug} Track/` directory (where Messages.md lives)."""
    return backlog_path.parent


def find_icebox(slug):
    """Locate `<slug> Icebox.md` somewhere under VAULT_ROOT (None if absent)."""
    target = f"{slug} Icebox.md"
    matches = []
    for root, dirs, files in os.walk(VAULT_ROOT, followlinks=True):
        if any(frag in root + "/" for frag in SKIP_PATH_FRAGMENTS):
            dirs[:] = []
            continue
        if target in files:
            matches.append(Path(root) / target)
    if not matches:
        return None
    if len(matches) > 1:
        raise BacklogEditError(
            f"multiple '{target}' candidates: " + ", ".join(str(m) for m in matches)
        )
    return matches[0]


def ensure_icebox(slug, backlog_path):
    """Get the icebox path; create it (sibling of backlog) with the standard
    header + `## Iced` H2 when absent."""
    existing = find_icebox(slug)
    if existing is not None:
        return existing
    icebox = backlog_path.parent / f"{slug} Icebox.md"
    header = (
        "---\n"
        f"description: cold-storage backlog for {slug} — parked items "
        f"not in scope for the active horizons.\n"
        "---\n"
        f"\n# {slug} Icebox\n\n"
        f"## {ICEBOX_DEFAULT_H2}\n\n"
    )
    icebox.write_text(header)
    return icebox


def find_file_by_basename(basename):
    """Locate a .md file under VAULT_ROOT by basename (no extension).

    Used to verify Questions-target links. Returns the first matching path
    or None.
    """
    target = f"{basename}.md"
    for root, dirs, files in os.walk(VAULT_ROOT, followlinks=True):
        if any(frag in root + "/" for frag in SKIP_PATH_FRAGMENTS):
            dirs[:] = []
            continue
        if target in files:
            return Path(root) / target
    return None


def _scope_text_to_block_id_region(text, block_id):
    """Per F103: scope a target file's text to the region of the row carrying
    `^<block_id>`. The row's region runs from the line containing `^<block_id>`
    up to the next top-level bullet, H2, or H3 row. Returns the empty string
    when the block-id is not found in the text."""
    lines = text.splitlines()
    marker = f"^{block_id}"
    start = None
    for i, line in enumerate(lines):
        if marker in line:
            start = i
            break
    if start is None:
        return ""
    end = len(lines)
    for j in range(start + 1, len(lines)):
        s = lines[j]
        if s.startswith("## ") or s.startswith("### "):
            end = j
            break
        if re.match(r"^- \*\*", s):
            end = j
            break
    return "\n".join(lines[start:end])


def verify_questions_constraint(status, body):
    """Raise BacklogEditError if status asserts a Questions promise that the
    body's wiki-link target cannot honor.

    The promise: a [Questions] / [N Questions] bracket means following the
    row's link lands on a file with ≥1 `Q<n> —` marker. The script enforces
    this at write time so the agent learns immediately instead of leaving a
    broken contract for /audit q to catch later.

    Skip when:
      - status is not a Questions variant
      - body is empty (no link to check; caller responsible for soundness)
      - the wiki-link target file cannot be located in the vault
        (warn-not-fail — may be a fresh anchor or unresolvable basename)
    """
    if not QUESTIONS_STATUS_RE.match(status.strip()):
        return
    if not body or not body.strip():
        raise BacklogEditError(
            f"[{status}] requires a body with a wiki-link to a target containing "
            f"Q<n> markers; body is empty. Add the link first, then re-run."
        )
    # Prefer the canonical "→ [[F<n> ...]]" feature-doc reference at the end of
    # the body. Fall back to the last wiki-link, then the first. Picking the FIRST
    # wiki-link grabbed in-prose references like [[Topic]] and let the check
    # silently skip (the B-roots-reconcile failure 2026-06-02).
    arrow_match = list(re.finditer(r"→\s+(\[\[[^\]]+\]\])", body))
    all_links = list(WIKI_LINK_RE.finditer(body))
    if arrow_match:
        chosen = WIKI_LINK_RE.search(arrow_match[-1].group(1))
    elif all_links:
        chosen = all_links[-1]
    else:
        chosen = None
    if chosen is None:
        raise BacklogEditError(
            f"[{status}] requires a body with a wiki-link to a target containing "
            f"Q<n> markers; no wiki-link found in body. "
            f"Body: {body[:120]!r}"
        )
    basename = chosen.group(1).strip()
    target_path = find_file_by_basename(basename)
    if target_path is None:
        # F103 — strict refusal when target cannot be located. Was previously a
        # warn-and-skip, which let [[Topic]]-style in-prose references through
        # (the B-roots-reconcile failure 2026-06-02). The spec is unambiguous:
        # if we cannot find the questions, that is an error.
        raise BacklogEditError(
            f"[{status}] promise broken: wiki-link target [[{basename}]] does not "
            f"resolve to a file in the vault.\n"
            f"  A [{status}] bracket promises the linked target contains Q<n> markers.\n"
            f"  A broken link is also a broken promise. Either fix the link, hoist the\n"
            f"  questions into a real feature doc, or change the row's bracket."
        )
    try:
        text = target_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise BacklogEditError(
            f"[{status}] promise broken: cannot read target [[{basename}]] "
            f"({target_path}): {e}"
        )
    # F103 — when the link carries `#^<block-id>`, scope the Q-marker search
    # to that row's region. Without scoping, a row pointing at a backlog
    # passes because Q-markers exist elsewhere in the same file
    # (the B-roots-reconcile failure 2026-06-02).
    block_id_match = re.search(r"#\^([A-Za-z0-9_\-]+)", chosen.group(0))
    if block_id_match:
        block_id = block_id_match.group(1)
        scoped = _scope_text_to_block_id_region(text, block_id)
        if not scoped:
            raise BacklogEditError(
                f"[{status}] promise broken: block-id `^{block_id}` not found "
                f"in target [[{basename}]]. The link points at a row that does not "
                f"exist."
            )
        text = scoped
    if not Q_MARKER_RE.search(text):
        scope_note = f" (scoped to row ^{block_id_match.group(1)})" if block_id_match else ""
        raise BacklogEditError(
            f"[{status}] promise broken: target [[{basename}]]{scope_note} "
            f"contains no Q<n> markers. Inline `Q1:` (colon) does NOT count; "
            f"the canonical form is `**Q<n> — ...**` with options + Recommendation "
            f"per [[ask-format]]. Hoist the Qs to the right shape, then re-run."
        )
    # Format check — every Q must have labeled options on their own indented
    # sub-bullets and an explicit Recommendation with Strong/Lean/None. Shell
    # out to audit-q.py (single source of truth for C8/C9/C10/C19).
    violations = run_audit_q_format_check(target_path)
    if violations:
        formatted = "\n  - ".join(violations[:10])  # cap at 10 for terminal sanity
        more = "" if len(violations) <= 10 else f"\n  - ... and {len(violations) - 10} more"
        raise BacklogEditError(
            f"[{status}] promise broken: target [[{basename}]] has Q-format violations.\n"
            f"  Each Q must have labeled options on their own sub-bullets AND an explicit\n"
            f"  Recommendation bullet with Strong/Lean/None (per [[ask-format]]).\n"
            f"  - {formatted}{more}\n"
            f"  Fix the Q-block format, then re-run."
        )


def run_audit_q_format_check(target_path):
    """Invoke audit-q.py --scope feature-doc against target_path; return a
    list of Q-format violation messages (C8/C9/C10/C19). Empty when clean.

    The Q-format rules check: labeled options on own sub-bullets (C19),
    explicit Recommendation with Strong/Lean/None (C9), Recommendation indent
    matches Q-header (C10), no inline prose alternatives (C8). This is the
    structural check that catches the SVP-Orch-Arch-style malformed Q-blocks
    BEFORE backlog-edit.py writes a [Questions] bracket asserting they exist.
    """
    audit_q = HOME / ".claude" / "skills" / "audit" / "scripts" / "audit-q.py"
    if not audit_q.exists():
        return []  # best-effort; if the audit skill isn't installed, skip
    try:
        result = subprocess.run(
            [str(audit_q), "--scope", "feature-doc",
             "--feature-doc", str(target_path), "--dry"],
            capture_output=True, text=True, timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    # Parse stdout for the relevant rule codes.
    relevant = ("C8", "C9", "C10", "C19")
    violations = []
    for line in result.stdout.splitlines():
        for code in relevant:
            if f"] {code} " in line:
                # Trim the leading file path; keep code + line# + message.
                idx = line.find(f"{code} ")
                tail = line[idx:] if idx >= 0 else line
                violations.append(tail)
                break
    return violations


VERIFY_IMPLEMENTATION_PATTERNS = [
    re.compile(r"\bPhase\s+(\d+)\b", re.IGNORECASE),
    re.compile(r"\bremaining\s+(?:anchors|items|files|sub-?items|tasks|work)\b", re.IGNORECASE),
    re.compile(r"\bfollow[-\s]?up\b", re.IGNORECASE),
    re.compile(r"\bsweep\s+(?:all|every|remaining)\b", re.IGNORECASE),
    re.compile(r"\bnext\s+pass\b", re.IGNORECASE),
    re.compile(r"\bsubsequent\s+(?:work|phase|migration)\b", re.IGNORECASE),
    re.compile(r"\bevery\s+(?:other|remaining)\b", re.IGNORECASE),
    re.compile(r"\bbulk\s+(?:migration|sweep|update)\b", re.IGNORECASE),
    re.compile(r"\bto\s+be\s+(?:done|implemented|migrated|written|filed)\b", re.IGNORECASE),
    re.compile(r"\bwill\s+(?:sweep|migrate|implement|file|update)\b", re.IGNORECASE),
]


def verify_no_implementation_in_verify(status, body):
    """Refuse [Verify*] when body contains language describing pending
    implementation work. The Verify-by bracket carries a structural promise:
    'nothing more happens here until the date or a failure surfaces.' If the
    body says 'Phase 2 sweeps every remaining anchor' or 'will migrate the
    rest later,' the row is misbracketed — it should be [Active], [Ready],
    or split into multiple F-rows.

    Per F096 — addresses the F094 failure mode where a [Verify-by] row hid
    ~50 anchors of remaining implementation work behind 'review the 6 done
    ones; sweep the rest if you're happy.'
    """
    if not status:
        return
    status_root = status.split()[0]
    if not status_root.startswith("Verify"):
        return
    if not body:
        return
    matches = []
    for pat in VERIFY_IMPLEMENTATION_PATTERNS:
        m = pat.search(body)
        if m:
            matches.append((m.group(0), pat.pattern))
    if not matches:
        return
    detail = "\n  - ".join(f'"{snippet}"' for snippet, _ in matches[:5])
    more = "" if len(matches) <= 5 else f"\n  - ... {len(matches) - 5} more"
    raise BacklogEditError(
        f"[{status}] body contains pending-implementation language; "
        f"refusing the write.\n"
        f"  Verify-by promises 'nothing more happens until the date or a "
        f"failure surfaces.' Pending\n"
        f"  implementation work means this row is misbracketed — use "
        f"[Active] or [Ready], or split\n"
        f"  the work into multiple F-rows. (Per F096 — addresses F094's "
        f"'Phase 1 done; Phase 2 hidden' failure.)\n"
        f"  Found:\n"
        f"  - {detail}{more}"
    )


REQUIRED_COMPLETION_SECTIONS = ("success criteria", "completion status", "verification")


def parse_status_block(text):
    """Return (status_word, block_body_text) for the `## Status` H2 of a feature doc.

    Returns (None, None) when no `## Status` H2 is found. Returns
    ('', block_body) when the H2 exists but body has no leading **bold** token.
    """
    lines = text.splitlines()
    in_status = False
    body_lines = []
    leading_word = None
    for line in lines:
        s = line.rstrip()
        if s.startswith("## "):
            if s == "## Status":
                in_status = True
                continue
            if in_status:
                break
            continue
        if not in_status:
            continue
        body_lines.append(line)
        if leading_word is None and line.strip():
            m = re.match(r"^\*\*([^*]+?)\*\*", line.strip())
            leading_word = m.group(1).strip() if m else ""
    if not in_status and not body_lines:
        return (None, None)
    return (leading_word if leading_word is not None else "", "\n".join(body_lines).strip())


def verify_status_block(status, body, existing_status):
    """Per F102 — refuse status writes when the linked feature doc's
    `## Status` H2 does not match the about-to-set status. Fires on EVERY
    transition (not just Done). Subsumes F098's Done-only Completion check.

    Skip cases (match F098's discretion):
      - status unchanged from existing (re-touch, no transition)
      - status is `delete` (the row is being removed)
      - body has no wiki-link target (no doc to check)
      - target file cannot be located in vault (broken or off-vault link)
    """
    if not status or status == "delete":
        return
    # Skip when status unchanged (re-touch is not a transition)
    if existing_status and existing_status.strip() == status.strip():
        return
    if not body or not body.strip():
        sys.stderr.write(
            f"note: [{status}] with empty body — skipping `## Status` block check (F102).\n"
        )
        return
    m = WIKI_LINK_RE.search(body)
    if not m:
        sys.stderr.write(
            f"note: [{status}] body has no wiki-link — skipping `## Status` block check (F102).\n"
        )
        return
    basename = m.group(1).strip()
    target_path = find_file_by_basename(basename)
    if target_path is None:
        sys.stderr.write(
            f"note: [{status}] target [[{basename}]] not located in vault — "
            f"skipping `## Status` block check (F102).\n"
        )
        return
    try:
        text = target_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        sys.stderr.write(
            f"note: cannot read [[{basename}]] for Status check: {e}\n"
        )
        return
    leading_word, block_body = parse_status_block(text)
    if leading_word is None:
        raise BacklogEditError(
            f"[{status}] refused: target [[{basename}]] has no `## Status` H2.\n"
            f"  Per F102, every status transition requires the feature doc's `## Status`\n"
            f"  block at the bottom to begin with `**{status}**` followed by a justification.\n"
            f"  Add the block to the feature doc, then re-run."
        )
    if leading_word.strip() != status.strip():
        raise BacklogEditError(
            f"[{status}] refused: target [[{basename}]] `## Status` body begins with\n"
            f"  `**{leading_word}**` but the status being set is `**{status}**`.\n"
            f"  Update the feature doc's Status block to reflect the new status with\n"
            f"  a one-sentence justification, then re-run."
        )
    # Designing-specific: must contain a next-action line (kills the deadlock case)
    if status.strip().lower() == "designing":
        if block_body is None or "next action" not in block_body.lower():
            raise BacklogEditError(
                f"[Designing] refused: target [[{basename}]] `## Status` block must\n"
                f"  contain a `next action:` line (or sentence containing 'next action')\n"
                f"  describing what /crank would do. Designing without a declared next\n"
                f"  action is the F102 deadlock pattern — agent files Designing, files\n"
                f"  no question, no action declared, crank exits silently. Either declare\n"
                f"  the next action or file Questions instead."
            )


def parse_completion_block(text):
    """Return dict {section_key: content_str} for the three required H3s,
    or None if no `## Completion` H2 found (case-insensitive).
    Section content is the lines between that H3 and the next H3/H2, stripped.
    """
    lines = text.splitlines()
    in_completion = False
    completion_lines = []
    for line in lines:
        h2_m = re.match(r"^##\s+(.+?)\s*$", line)
        if h2_m:
            heading = h2_m.group(1).strip().lower()
            if heading == "completion":
                in_completion = True
                continue
            if in_completion:
                break  # next H2 ends the block
        if in_completion:
            completion_lines.append(line)
    if not completion_lines and not in_completion:
        return None  # No Completion H2 at all
    sections = {k: "" for k in REQUIRED_COMPLETION_SECTIONS}
    current = None
    buf = []

    def flush():
        nonlocal current, buf
        if current is not None and current in sections:
            sections[current] = "\n".join(buf).strip()
        current = None
        buf = []

    for line in completion_lines:
        h3_m = re.match(r"^###\s+(.+?)\s*$", line)
        if h3_m:
            flush()
            current = h3_m.group(1).strip().lower()
            continue
        if current is not None:
            buf.append(line)
    flush()
    return sections


def verify_completion_block(status, body, existing_status):
    """Per F098 — refuse Done writes when the linked feature doc lacks a
    `## Completion` block with three H3 sub-sections (Success criteria,
    Completion status, Verification), each non-empty.

    Grandfathers existing Done rows: skip the check when the prior status
    was already a Done* variant. Fires only on the **transition** to Done.
    """
    if not status:
        return
    if not status.split()[0].startswith("Done"):
        return
    if existing_status and existing_status.split()[0].startswith("Done"):
        return  # already Done; allow re-touch
    if not body or not body.strip():
        sys.stderr.write(
            "note: [Done] with empty body — skipping Completion block check (per F098). "
            "If this is a feature row, add a body wiki-link to the feature doc.\n"
        )
        return
    m = WIKI_LINK_RE.search(body)
    if not m:
        sys.stderr.write(
            "note: [Done] body has no wiki-link — skipping Completion block check (per F098).\n"
        )
        return
    basename = m.group(1).strip()
    target_path = find_file_by_basename(basename)
    if target_path is None:
        sys.stderr.write(
            f"note: [Done] target [[{basename}]] not located in vault — "
            f"skipping Completion block check (per F098).\n"
        )
        return
    try:
        text = target_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        sys.stderr.write(
            f"note: cannot read [[{basename}]] for Completion check: {e}\n"
        )
        return
    sections = parse_completion_block(text)
    if sections is None:
        raise BacklogEditError(
            f"[Done] refused: target [[{basename}]] has no `## Completion` H2.\n"
            f"  Per F098, marking Done requires a `## Completion` block with three H3 sub-sections:\n"
            f"  - `### Success criteria`  — how do you know the work is done?\n"
            f"  - `### Completion status` — what has been executed? (enumerate)\n"
            f"  - `### Verification`      — how was the success criteria checked?\n"
            f"  Add the block to the feature doc, then re-run."
        )
    missing = []
    for key in REQUIRED_COMPLETION_SECTIONS:
        title_form = "### " + key[0].upper() + key[1:]
        if not sections[key]:
            missing.append(title_form)
    if missing:
        raise BacklogEditError(
            f"[Done] refused: target [[{basename}]] `## Completion` block is incomplete.\n"
            f"  Missing or empty: {', '.join(missing)}\n"
            f"  Per F098, all three sub-sections must be present and non-empty for Done."
        )


def warn_verify_watching_horizon(status, horizon_name):
    """Print a stderr nudge when Verify/Watching is set on Now/Next/Active/Ready.

    User preference: passive verification through normal use (Later horizon)
    over explicit verify-before-next-step. This is a nudge, not a refusal —
    the rare critical-verify case is legitimate and just ignores the line.
    """
    status_root = status.split()[0] if status else ""
    if not status_root:
        return
    is_verify_or_watching = any(
        status_root.startswith(prefix) for prefix in VERIFY_WATCHING_FAMILY
    )
    if not is_verify_or_watching:
        return
    if horizon_name not in NUDGE_BUCKETS:
        return
    sys.stderr.write(
        f"note: [{status}] usually belongs in Verify (passive observation through normal use).\n"
        f"      Promote to {horizon_name} only if verification MUST happen before the next step.\n"
    )


# --------------------------------------------------------------------------
# Row parsing

ROW_ID_RE = re.compile(r"^(F|B)(new|\d+|-[A-Za-z0-9][\w\-]*)$")


def parse_row_id(arg):
    """Return ('F'|'B', literal-rest-or-None).

    'Fnew' / 'Bnew'  → (kind, None)            — mint a new number
    'F015'           → ('F', '015')
    'B7'             → ('B', '7')
    'B-mode-walkup'  → ('B', '-mode-walkup')   — kebab B-row id
    """
    m = ROW_ID_RE.match(arg)
    if not m:
        raise BacklogEditError(
            f"invalid row-id '{arg}' "
            "(expected F<NNN>, B<n>, B-<slug>, Fnew, or Bnew)"
        )
    kind, rest = m.group(1), m.group(2)
    if rest == "new":
        return (kind, None)
    return (kind, rest)


def format_row_id(kind, rest_or_num):
    """For mint: pad F to 3 digits; B stays as-is."""
    if kind == "F":
        if isinstance(rest_or_num, int):
            return f"F{rest_or_num:03d}"
        return f"F{rest_or_num}"
    return f"B{rest_or_num}"


# --------------------------------------------------------------------------
# Backlog scanning

ROW_HEADER_RE = re.compile(
    r"^(\s*)-\s+\*\*(F\d+|B[\w\-]+|B\d+)\b"
)
H2_RE = re.compile(r"^##\s+(.+?)\s*$")

# Used to parse the existing row line back into title + body so the script
# can preserve them across status-only edits.
ROW_FULL_RE = re.compile(
    r"^-\s+\*\*(?P<rid>F\d+|B[\w\-]+|B\d+)"
    r"(?:\s+—\s+(?P<title>.+?))?\*\*"
    r"\s+\[(?P<status>[^\]]+)\]"
    r"(?:\s+—\s+(?P<body>.+?))?"
    r"(?:\s+\^[\w\-]+)?\s*$"
)


def parse_existing_row(line):
    """Return (title, body) extracted from an existing row line.

    Returns ('', '') if the line doesn't match the expected shape — caller
    treats that as a fresh row.
    """
    m = ROW_FULL_RE.match(line)
    if not m:
        return ("", "")
    return (m.group("title") or "", m.group("body") or "")


def scan_backlog(text):
    """Return (h2_index, row_index).

    h2_index: list of (line_idx, name) for each '## Heading'.
    row_index: dict row_id → (start_idx, end_idx, h2_name, indent)
               end_idx is exclusive (next row or next H2 or EOF).
    """
    lines = text.splitlines(keepends=True)
    h2_index = []
    row_starts = []  # (line_idx, row_id, h2_name, indent)
    current_h2 = None

    for i, line in enumerate(lines):
        h2_m = H2_RE.match(line.rstrip())
        if h2_m:
            current_h2 = h2_m.group(1).strip()
            h2_index.append((i, current_h2))
            continue
        row_m = ROW_HEADER_RE.match(line)
        if row_m and (len(row_m.group(1)) == 0):
            row_starts.append((i, row_m.group(2), current_h2, row_m.group(1)))

    # Compute end indices.
    row_index = {}
    boundary_lines = sorted(
        {ri[0] for ri in row_starts}
        | {hi[0] for hi in h2_index}
        | {len(lines)}
    )
    for start, rid, h2, indent in row_starts:
        # End at next boundary > start
        end = next(b for b in boundary_lines if b > start)
        row_index[rid] = (start, end, h2, indent)

    return lines, h2_index, row_index


def next_id_for_kind(row_index, kind):
    """Highest F<n> or B<n> across the backlog + 1."""
    pattern = re.compile(rf"^{kind}(\d+)$")
    nums = []
    for rid in row_index.keys():
        m = pattern.match(rid)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


# --------------------------------------------------------------------------
# Row formatting

def render_row(row_id, status, title, body):
    """Format a backlog row line.

    Shape: '- **<row_id> — <title>** [<status>] — <body> ^<row_id>\n'
    Title omitted -> `**<row_id>**`; body omitted -> no trailing `— ...`.

    The block-ID anchor at the end matches the existing convention so
    `[[<file>#^<row-id>|...]]` links work for the new row.
    """
    title = (title or "").strip()
    body = (body or "").strip()
    title_block = f"**{row_id} — {title}**" if title else f"**{row_id}**"
    bracket = f"[{status}]"
    suffix = f" — {body}" if body else ""
    return f"- {title_block} {bracket}{suffix} ^{row_id}\n"


# --------------------------------------------------------------------------
# Mutation

def locate_h2_insertion_point(lines, h2_index, h2_name):
    """Return the line index just before the next H2 (or EOF).

    Raises BacklogEditError if h2_name isn't in h2_index — callers must
    ensure_h2_exists() first.
    """
    found = next((i for i, name in h2_index if name == h2_name), None)
    if found is None:
        raise BacklogEditError(f"internal: H2 '{h2_name}' not in index after ensure")
    # End of this H2's body = next H2 line or EOF.
    next_h2 = next((i for i, _ in h2_index if i > found), len(lines))
    # Walk back past trailing blank lines so we insert before them.
    insert_at = next_h2
    while insert_at - 1 > found and lines[insert_at - 1].strip() == "":
        insert_at -= 1
    return insert_at


def ensure_h2_exists(lines, h2_index, h2_name):
    """If h2_name isn't in the file, append at end and return new structure."""
    for _, name in h2_index:
        if name == h2_name:
            return lines, h2_index
    # Append the H2 at end.
    if lines and not lines[-1].endswith("\n"):
        lines[-1] = lines[-1] + "\n"
    if lines and lines[-1].strip() != "":
        lines.append("\n")
    lines.append(f"## {h2_name}\n")
    lines.append("\n")
    new_h2_index = h2_index + [(len(lines) - 2, h2_name)]
    return lines, new_h2_index


def perform_edit(
    backlog_path,
    horizon,
    row_id_arg,
    status,
    title,
    body,
    title_provided,
    body_provided,
):
    """Apply the edit, return a one-line summary for the Messages entry."""
    raw = backlog_path.read_text()
    lines, h2_index, row_index = scan_backlog(raw)

    kind, rest = parse_row_id(row_id_arg)

    # Resolve the actual row_id (mint if requested).
    if rest is None:
        # Mint a new id.
        if kind == "F":
            new_num = next_id_for_kind(row_index, "F")
            row_id = format_row_id("F", new_num)
        else:
            new_num = next_id_for_kind(row_index, "B")
            row_id = format_row_id("B", new_num)
        existing = None
    else:
        row_id = f"{kind}{rest}"
        existing = row_index.get(row_id)

    # Validate horizon.
    if horizon == "same":
        if existing is None:
            raise BacklogEditError(
                f"horizon=same requires the row to already exist; "
                f"{row_id} not found in backlog"
            )
        h2_name = existing[2]
        if h2_name is None:
            raise BacklogEditError(
                f"{row_id} exists but is not under any H2 — cannot keep 'same'"
            )
    else:
        # Strip optional '## ' prefix. Validation of the user-facing horizon
        # arg happens upstream in main(); by the time we get here, this is the
        # resolved H2 name (may be 'Iced' for icebox-bound writes).
        h2_name = horizon.lstrip("# ").strip()

    # Handle delete first.
    if status == "delete":
        if existing is None:
            raise BacklogEditError(f"{row_id} not found — cannot delete")
        start, end, existing_h2, _ = existing
        del lines[start:end]
        backlog_path.write_text("".join(lines))
        return {
            "summary": f"deleted {row_id}",
            "row_id": row_id,
            "verb": "deleted",
            "h2_name": existing_h2 or "",
            "status": "delete",
        }

    # Preserve title / body from the existing row when caller omitted them
    # OR passed an empty string. Lets callers update bracket-only without
    # re-supplying the full content, and lets the body-only-update pattern
    # `backlog-edit.py {NAME} same <row> <status> "" "<new body>"` work
    # without blowing away the title.
    existing_status_for_check = ""
    if existing is not None:
        existing_title, existing_body = parse_existing_row(lines[existing[0]])
        if not title_provided or title == "":
            title = existing_title
        if not body_provided or body == "":
            body = existing_body
        # Extract the existing row's status string for F098's grandfather check.
        full_m = ROW_FULL_RE.match(lines[existing[0]])
        if full_m:
            existing_status_for_check = full_m.group("status") or ""
        # F147 — status=="same" means "keep the existing bracket". Without this,
        # render_row would write the literal `[same]`, silently clobbering the
        # real status (e.g. a body-only `state task update` losing [Designing]).
        if status == "same" and existing_status_for_check:
            status = existing_status_for_check

    # Constraint check — the Questions promise. Refuse the write if the
    # status asserts [Questions] but the body's wiki-link target has no
    # Q<n> markers. Runs AFTER the preserve-on-omit resolution so the
    # final body is what we verify.
    verify_questions_constraint(status, body)

    # F096 — refuse [Verify*] when body describes pending implementation
    # work (Phase 2, remaining, follow-up, etc.). Addresses the F094 lie
    # where the row claimed Verify-by but hid ~50 anchors of work.
    verify_no_implementation_in_verify(status, body)

    # F102 — refuse any status transition where the linked feature doc's
    # `## Status` H2 does not match the about-to-set status. Subsumes F098
    # (the Done case is now a special case of the broader Status discipline).
    # Grandfathers re-touch of same-status rows.
    verify_status_block(status, body, existing_status_for_check)

    # Build the new line.
    new_line = render_row(row_id, status, title, body)

    if existing is not None:
        start, end, existing_h2, _ = existing
        if existing_h2 == h2_name:
            # In-place replacement: swap the first line, keep any sub-bullets.
            lines[start] = new_line
        else:
            # Remove old span, then insert new in destination H2.
            del lines[start:end]
            # Re-scan; line numbers shifted.
            lines, h2_index, row_index = scan_backlog("".join(lines))
            lines, h2_index = ensure_h2_exists(lines, h2_index, h2_name)
            insert_at = locate_h2_insertion_point(lines, h2_index, h2_name)
            # Ensure a blank line before the new row.
            if insert_at > 0 and lines[insert_at - 1].strip() != "":
                lines.insert(insert_at, "\n")
                insert_at += 1
            lines.insert(insert_at, new_line)
        verb = "updated"
    else:
        # Brand new row.
        lines, h2_index = ensure_h2_exists(lines, h2_index, h2_name)
        insert_at = locate_h2_insertion_point(lines, h2_index, h2_name)
        if insert_at > 0 and lines[insert_at - 1].strip() != "":
            lines.insert(insert_at, "\n")
            insert_at += 1
        lines.insert(insert_at, new_line)
        verb = "added"

    backlog_path.write_text("".join(lines))

    # Soft nudge — Verify/Watching usually belongs in Later.
    warn_verify_watching_horizon(status, h2_name)

    return {
        "summary": f"{verb} {row_id} in {h2_name} [{status}]",
        "row_id": row_id,
        "verb": verb,
        "h2_name": h2_name,
        "status": status,
    }


# --------------------------------------------------------------------------
# Messages + Q.md refresh

def append_messages(slug, summary, backlog_path):
    """Write a global-sentinel entry and a per-anchor Messages.md entry."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rel = backlog_path.relative_to(VAULT_ROOT) if backlog_path.is_relative_to(VAULT_ROOT) else backlog_path
    line = f"[{now}] [INFO] {slug}: {summary} (at {rel})\n"

    # Global sentinel — prefixed with slug for cross-anchor disambiguation.
    SENTINEL.parent.mkdir(parents=True, exist_ok=True)
    with SENTINEL.open("a") as f:
        f.write(f"[{slug}] {line}")

    # Per-anchor messages file.
    track_dir = anchor_track_dir(backlog_path)
    messages_path = track_dir / f"{slug} Messages.md"
    if not messages_path.exists():
        header = (
            "---\n"
            f"description: agent inbox for {slug} — append-only notifications "
            "from watchers, audits, and tools.\n"
            "---\n"
            f"\n# {slug} Messages\n\n"
        )
        messages_path.write_text(header)
    with messages_path.open("a") as f:
        f.write(line)


def write_state(slug, result):
    """Persist the last-invocation timestamp + details for /audit integrity.

    State lives at ~/.config/ob-skills/backlog-edit/state.json. Each anchor
    has one entry, overwritten on every invocation — only the most recent
    write per anchor is tracked. `/audit integrity` compares the backlog
    file's mtime against this timestamp to detect script-bypassing direct
    edits.
    """
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            state = {}
    else:
        state = {}
    if "anchors" not in state:
        state["anchors"] = {}
    state["anchors"][slug] = {
        "last_run": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "row_id": result["row_id"],
        "verb": result["verb"],
        "horizon": result["h2_name"],
        "status": result["status"],
    }
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


def refresh_q_md(slug):
    """Invoke the audit skill's audit-q.py directly to regenerate Q.md.

    Skill-to-skill call by absolute path inside ~/.claude/skills/ — no ~/bin/
    dependency. Per the principle that skills must not depend on user-local
    filesystem layout outside the skills tree.
    """
    audit_q = HOME / ".claude" / "skills" / "audit" / "scripts" / "audit-q.py"
    if not audit_q.exists():
        return
    try:
        subprocess.run(
            [str(audit_q), "--scope", "backlog", "--anchor", slug, "--fix"],
            capture_output=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass


# --------------------------------------------------------------------------
# CLI

def row_in_file(file_path, row_id):
    """Scan a file for a row whose F/B-id matches row_id (exact)."""
    if not file_path.is_file():
        return False
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    # Look for `**<row_id>` at the start of any row bullet.
    pattern = re.compile(rf"^\s*-\s+\*\*{re.escape(row_id)}\b", re.MULTILINE)
    return pattern.search(text) is not None


def resolve_files_for_edit(slug, backlog_path, horizon, row_id_arg, status):
    """Decide source + destination files based on horizon and current row location.

    Returns (source_file, destination_file, destination_horizon).

    - source_file: the file we may need to delete from first (None if not needed).
    - destination_file: where the new/updated row lands.
    - destination_horizon: H2 name inside the destination file.
    """
    icebox_path = find_icebox(slug)

    # Resolve where the existing row currently lives, if known.
    src_file = None
    if row_id_arg not in (None,) and not row_id_arg.endswith("new"):
        # explicit row-id; check both files
        if row_in_file(backlog_path, row_id_arg):
            src_file = backlog_path
        elif icebox_path and row_in_file(icebox_path, row_id_arg):
            src_file = icebox_path

    # Determine destination based on horizon.
    if horizon == ICEBOX_HORIZON:
        dst_file = ensure_icebox(slug, backlog_path)
        dst_horizon = ICEBOX_DEFAULT_H2
    elif horizon == "same":
        # Stay in whichever file the row currently lives.
        if src_file is not None:
            dst_file = src_file
            dst_horizon = "same"
        else:
            # Row doesn't exist yet — `same` with no prior row is an error
            # handled downstream in perform_edit.
            dst_file = backlog_path
            dst_horizon = "same"
    else:
        # Any other horizon → backlog file
        dst_file = backlog_path
        dst_horizon = horizon

    # Cross-file move case: source and destination differ → we'll delete from
    # source then insert into destination. Doesn't apply to delete or mint.
    cross_file = (
        src_file is not None
        and src_file != dst_file
        and status != "delete"
    )
    if not cross_file:
        src_file = None  # signal "no cross-file delete needed"

    return src_file, dst_file, dst_horizon


def mint_cross_file_id(backlog_path, icebox_path, kind):
    """Compute the next F/B number across BOTH backlog and icebox.

    Per [[CAB Backlog]] § Icebox interaction: 'F-number namespace is shared
    across backlog AND icebox — no F-number collisions; an item moving
    between the two keeps its F-number.' Same for B-numbers.
    """
    nums = []
    pattern = re.compile(rf"^\s*-\s+\*\*{kind}(\d+)\b", re.MULTILINE)
    for path in (backlog_path, icebox_path):
        if path is None or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        nums.extend(int(m.group(1)) for m in pattern.finditer(text))
    return (max(nums) + 1) if nums else 1


# ============================================================
# F128 — Q-management subcommands (Phase 1)
# Verbs: add / resolve / remove / rewrite
# Triggered by presence of `-Q` flag anywhere in argv
# ============================================================


def _candidate_feature_dirs(slug, backlog_path):
    """Ordered candidate `{slug} Features/` folders (F142 transition).

    New canonical location is `{slug} Design/{slug} Features/` (Design is a
    sibling of the backlog's `{slug} Track/` folder, whatever level it sits at);
    legacy location is `{slug} Features/` as a sibling of the backlog. We return
    both, preferred-first, so callers transparently find docs in either place
    during the rollout. See F142.
    """
    track_dir = backlog_path.parent          # {slug} Track/
    anchor_root = track_dir.parent           # anchor docs root (Design/Track siblings)
    return [
        anchor_root / f"{slug} Design" / f"{slug} Features",  # new canonical
        track_dir / f"{slug} Features",                       # legacy sibling
        anchor_root / f"{slug} Features",                     # older flat variant
    ]


def _find_feature_doc(slug, row_id):
    """Find the feature doc whose filename starts with `{row_id} — ` under
    slug's Features folder — the new `{slug} Design/{slug} Features/` location
    or the legacy `{slug} Track/{slug} Features/` fallback (F142). Raises
    BacklogEditError on miss / ambiguity.
    """
    backlog_path = find_backlog(slug)
    cand_dirs = _candidate_feature_dirs(slug, backlog_path)
    existing = [d for d in cand_dirs if d.is_dir()]
    if not existing:
        tried = ", ".join(f"'{d}'" for d in cand_dirs)
        raise BacklogEditError(
            f"no Features/ folder for '{slug}' (tried {tried}) "
            f"— can't locate feature doc for {row_id}"
        )
    matches = []
    for d in existing:
        matches.extend(d.glob(f"{row_id} — *.md"))
    if not matches:
        where = ", ".join(str(d) for d in existing)
        raise BacklogEditError(
            f"no feature doc matching '{row_id} — *.md' under {where}"
        )
    if len(matches) > 1:
        names = ", ".join(p.name for p in matches)
        raise BacklogEditError(
            f"multiple feature docs match '{row_id}': {names}"
        )
    return matches[0]


def _read_q_body(args_inline, args_from_file):
    """Get body content from -m, --from-file, or stdin (in that priority)."""
    if args_inline is not None:
        return args_inline
    if args_from_file is not None:
        p = Path(args_from_file).expanduser()
        if not p.is_file():
            raise BacklogEditError(f"--from-file path not found: {p}")
        return p.read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


_Q_HEADER_BULLET_RE = re.compile(r"^(\s*)- \*\*Q(\d+)\b")
_Q_HEADER_H3_RE = re.compile(r"^(\s*)### Q(\d+)\b")


def _next_q_number(doc_text):
    """Lowest unused Q-number across pending bullets + ### Resolved + bottom
    ## Resolved + ### Removed sub-sections. Per F128 § Q-numbering policy.
    """
    used = set()
    for line in doc_text.splitlines():
        m = _Q_HEADER_BULLET_RE.match(line) or _Q_HEADER_H3_RE.match(line)
        if m:
            used.add(int(m.group(2)))
    n = 1
    while n in used:
        n += 1
    return n


def _find_h2(lines, h2_name):
    """Return (start_line, end_line) of the `## {h2_name}` H2 block, or None.

    end_line is the line index of the next H2 (or len(lines) at EOF).
    """
    start = None
    for i, line in enumerate(lines):
        if line.strip() == f"## {h2_name}":
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return (start, end)


def _find_h3_in_h2(lines, h2_start, h2_end, h3_name):
    """Return (start_line, end_line) of `### {h3_name}` H3 inside the H2
    block lines[h2_start:h2_end]. End is the next H3 or H2."""
    start = None
    for i in range(h2_start + 1, h2_end):
        if lines[i].strip() == f"### {h3_name}":
            start = i
            break
    if start is None:
        return None
    end = h2_end
    for j in range(start + 1, h2_end):
        if lines[j].startswith("## ") or lines[j].startswith("### "):
            end = j
            break
    return (start, end)


def _find_q_bullet(lines, q_num):
    """Locate Q<n> bullet in the doc. Returns (start_line, end_line, indent)
    where the bullet's body runs from start_line through end_line-1 (exclusive
    of the next top-level bullet / H2 / H3).
    """
    start = None
    indent = ""
    for i, line in enumerate(lines):
        m = _Q_HEADER_BULLET_RE.match(line)
        if m and int(m.group(2)) == q_num:
            # Skip Qs inside ## Resolved or ### Resolved or ### Removed sections.
            # Walk back to confirm we're in ## Open Questions / pending area.
            section = _section_at(lines, i)
            if section in ("Open Questions", "Open Questions:Pending"):
                start = i
                indent = m.group(1)
                break
    if start is None:
        return None
    # End at next Q-header bullet (same or shallower indent) OR any heading.
    # Sibling bullets at the same indent (e.g., `- (A)` option bullets, or
    # `- **Recommendation:** ...`) are PART of the Q's body, not a sibling Q.
    end = len(lines)
    for j in range(start + 1, len(lines)):
        line = lines[j]
        if line.startswith("#"):
            end = j
            break
        m = _Q_HEADER_BULLET_RE.match(line)
        if m and (len(line) - len(line.lstrip())) <= len(indent):
            end = j
            break
    return (start, end, indent)


def _section_at(lines, line_idx):
    """Classify which logical section line_idx falls in.

    Returns: "Open Questions:Pending" (under ## Open Questions, not in any
    ### sub), "Open Questions:Resolved" / "Open Questions:Removed", "Resolved"
    (bottom H2), or "Other".
    """
    in_open_q = False
    in_h3 = None
    last_h2 = None
    for i in range(line_idx + 1):
        line = lines[i]
        if line.startswith("## "):
            name = line.strip()[3:]
            last_h2 = name
            in_open_q = (name == "Open Questions")
            in_h3 = None
        elif line.startswith("### "):
            in_h3 = line.strip()[4:]
    if in_open_q:
        if in_h3 == "Resolved":
            return "Open Questions:Resolved"
        if in_h3 == "Removed":
            return "Open Questions:Removed"
        return "Open Questions:Pending"
    if last_h2 == "Resolved":
        return "Resolved"
    return "Other"


def _ensure_open_questions_h2(lines):
    """Ensure ## Open Questions H2 exists ABOVE the H1 — between the frontmatter
    and the H1 (per the 2026-06-29 placement rule: pending questions precede the
    document; they aren't part of it until answered, when they migrate to the
    bottom ## Resolved H2). Returns lines (possibly modified) AND the
    (h2_start, h2_end) content range after insertion.
    """
    existing = _find_h2(lines, "Open Questions")
    if existing is not None:
        return lines, existing
    # Find the H1 to insert BEFORE.
    h1_idx = None
    for i, line in enumerate(lines):
        if line.startswith("# "):
            h1_idx = i
            break
    if h1_idx is None:
        raise BacklogEditError("feature doc has no H1; cannot insert ## Open Questions")
    # Insert the block just above the H1; a trailing blank separates it from the H1.
    new_block = ["## Open Questions", "", ""]
    lines = lines[:h1_idx] + new_block + lines[h1_idx:]
    return lines, (h1_idx + 1, h1_idx + 3)


def _ensure_bottom_resolved_h2(lines):
    """Ensure a bottom ## Resolved H2 exists. Returns lines (possibly modified)
    AND (h2_start, h2_end) of the H2.
    """
    # Search for ## Resolved
    found = _find_h2(lines, "Resolved")
    if found is not None:
        return lines, found
    # Append at end
    if lines and lines[-1].strip():
        lines.append("")
    lines.append("## Resolved")
    lines.append("")
    return lines, (len(lines) - 2, len(lines))


def _container_id_for_feature(feature_path):
    """Return container ID for block-IDs (e.g., 'F128')."""
    m = re.match(r"^(F\d+)\s+—", feature_path.stem)
    if m:
        return m.group(1)
    return feature_path.stem


def _format_q_bullet(q_num, container_id, body):
    """Wrap a body into the canonical Q-bullet form with block-ID."""
    body = body.strip()
    block_id = f" ^{container_id}-Q{q_num}"
    # If body already starts with `**Q<n> —`, accept as pre-formatted; just
    # ensure block-ID at end.
    if re.match(rf"^\s*\*\*Q\d+\s+—", body):
        # Normalize the leading Q-number to the canonical bullet form
        body = re.sub(r"^\s*\*\*Q\d+", f"**Q{q_num}", body, count=1)
        # Ensure leading "- " bullet
        if not body.startswith("- "):
            body = "- " + body
    else:
        # Plain body — wrap as bullet
        body = f"- **Q{q_num} — Untitled** — {body}"
    # Append block-ID if not already present at end of first line
    first_line, sep, rest = body.partition("\n")
    if f"^{container_id}-Q{q_num}" not in first_line:
        first_line = first_line.rstrip() + block_id
    return first_line + (sep + rest if sep else "")


def _post_conditions(slug, feature_path):
    """Run the post-edit invariant check: audit-q lenient over the q scope.
    Per F176 the `{NAME} queries.md` page is built on demand by /query's
    determination logic — there is no render step.
    Returns list of warning lines (printed by caller).
    """
    warnings = []
    # Audit (lenient — surface errors but don't unwind)
    audit_q = Path.home() / ".claude" / "skills" / "audit" / "scripts" / "audit-q.py"
    if audit_q.is_file():
        try:
            r = subprocess.run(
                [sys.executable, str(audit_q), "--scope", "q", "--dry"],
                capture_output=True, text=True, timeout=120,
            )
            # Audit returns non-zero on errors. Parse for feature-doc-related
            # findings and surface only those that mention this feature_path.
            stderr = r.stderr
            for line in stderr.splitlines():
                if "[error]" in line and str(feature_path.name) in line:
                    warnings.append(line.strip())
        except Exception as e:
            warnings.append(f"audit-q failed: {e}")
    return warnings


def main_q(argv):
    """Dispatcher for `-Q` (Q-management) invocations.

    CLI: backlog-edit.py {SLUG} {ROW-ID} -Q {add|resolve|remove|rewrite}
         [Q-number] [--choice (X)] [--reason "..."] [--force]
         [--from-file path] [-m "..."]
    """
    import argparse
    p = argparse.ArgumentParser(
        prog="backlog-edit.py",
        description=(
            "F128 Q-management — add / resolve / remove / rewrite Open Questions "
            "in a feature doc. The script enforces ask-format spec (block-IDs, "
            "Q-numbering, Phase 1/2/3 lifecycle) and runs audit-q lenient as a "
            "post-condition (queries.md is built on demand by /query — no render step). "
            "Body content via stdin (primary), --from-file (fallback for long Qs), "
            "or -m (inline one-liner)."
        ),
        epilog=(
            "Examples:\n"
            "  echo '**Q5 — short** — body.' | backlog-edit.py SKA F091 -Q add\n"
            "  echo 'team picked A' | backlog-edit.py SKA F091 -Q resolve -n 5 --choice '(A)'\n"
            "  backlog-edit.py SKA F091 -Q remove -n 5 --reason 'obsoleted by F128'\n"
            "  echo '**Q5 — rewritten** — fresh body.' | backlog-edit.py SKA F091 -Q rewrite -n 5 --force\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("slug",
                   help="Anchor slug (e.g., SKA, MUX, HA, A2X)")
    p.add_argument("row_id",
                   help="F-number of the row whose feature doc holds the Qs (e.g., F128)")
    p.add_argument("-Q", dest="verb",
                   choices=["add", "resolve", "remove", "rewrite"],
                   required=True,
                   help="Q-management verb")
    p.add_argument("-n", dest="q_num", type=int, default=None,
                   help="Q-number (required for resolve/remove/rewrite; auto-minted for add)")
    p.add_argument("--choice", default=None,
                   help="For resolve: chosen option label like '(A)' or '(B)' — copied into the resolved H3's **Choice:** line")
    p.add_argument("--reason", default=None,
                   help="For remove: short reason recorded in the ### Removed H3 title (audit trail)")
    p.add_argument("--force", action="store_true",
                   help="For rewrite: required when the Q already has a **Recommendation:** line (rewrite can desync body from recommendation)")
    p.add_argument("--from-file", dest="from_file", default=None,
                   help="Read body from file (alternative to stdin; preferred for long Qs)")
    p.add_argument("-m", dest="inline", default=None,
                   help="Inline body (alternative to stdin; for short one-liner Qs)")
    args = p.parse_args(argv[1:])

    feature_path = _find_feature_doc(args.slug, args.row_id)
    text = feature_path.read_text(encoding="utf-8")
    container_id = _container_id_for_feature(feature_path)
    today = date.today().isoformat()

    if args.verb == "add":
        body = _read_q_body(args.inline, args.from_file)
        if not body.strip():
            raise BacklogEditError(
                "-Q add requires a body via stdin, --from-file, or -m"
            )
        q_num = args.q_num if args.q_num else _next_q_number(text)
        new_bullet = _format_q_bullet(q_num, container_id, body)
        lines = text.splitlines()
        lines, (h2_start, h2_end) = _ensure_open_questions_h2(lines)
        # Insert before any ### sub-section (Resolved / Removed) at the end of
        # the pending area.
        insert_at = h2_end
        for j in range(h2_start + 1, h2_end):
            if lines[j].startswith("### "):
                insert_at = j
                break
        # Trim trailing blank lines before insertion
        while insert_at > h2_start + 1 and not lines[insert_at - 1].strip():
            insert_at -= 1
        new_lines = ["", new_bullet] if lines[insert_at - 1].strip() else [new_bullet]
        # Add a trailing blank line for separation
        new_lines = new_lines + [""]
        lines = lines[:insert_at] + new_lines + lines[insert_at:]
        feature_path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""),
                                encoding="utf-8")
        summary = f"added Q{q_num} to {feature_path.name}"

    elif args.verb == "resolve":
        if args.q_num is None:
            raise BacklogEditError("-Q resolve requires Q-number positional arg")
        if not args.choice:
            raise BacklogEditError("-Q resolve requires --choice '(X)'")
        body = _read_q_body(args.inline, args.from_file)
        lines = text.splitlines()
        loc = _find_q_bullet(lines, args.q_num)
        if loc is None:
            raise BacklogEditError(
                f"Q{args.q_num} not found in pending Open Questions of "
                f"{feature_path.name}"
            )
        start, end, _ = loc
        # Extract Q title from header line
        header = lines[start]
        title_m = re.match(r"^\s*- \*\*Q\d+\s+—\s+([^*]+?)\*\*", header)
        title = title_m.group(1).strip() if title_m else "Untitled"
        # Capture original body for archive
        original_body = "\n".join(lines[start:end]).rstrip()
        # Compose resolved H3
        h3_lines = [
            "",
            f"### Q{args.q_num} — {title} (resolved {today})",
            f"**Choice:** {args.choice}",
            "",
        ]
        if body.strip():
            h3_lines.append(body.rstrip())
            h3_lines.append("")
        # Append original-body excerpt as quoted context (helps reader see what was decided)
        h3_lines.append("> Original Q context:")
        for ol in original_body.splitlines():
            h3_lines.append(f"> {ol}")
        h3_lines.append("")
        # Remove pending Q-bullet
        lines = lines[:start] + lines[end:]
        # Decide destination: ## Resolved (bottom) or `### Resolved` H3 in
        # ## Open Questions (Phase 1 in-block staging).
        # Per F127/F128 simplification: always migrate resolved Qs to the
        # bottom ## Resolved H2. The in-block ### Resolved staging is a
        # historical artifact from F125-era runbooks.
        lines, (rh2_start, rh2_end) = _ensure_bottom_resolved_h2(lines)
        insert_at = rh2_end
        # Trim trailing blanks
        while insert_at > rh2_start + 1 and not lines[insert_at - 1].strip():
            insert_at -= 1
        lines = lines[:insert_at] + h3_lines + lines[insert_at:]
        # Phase-2 transition check: if ## Open Questions is now empty (only
        # the H2 header + blank lines + no bullets + no H3 holding pen), drop
        # the whole H2.
        oq = _find_h2(lines, "Open Questions")
        if oq is not None:
            oq_start, oq_end = oq
            empty = True
            for k in range(oq_start + 1, oq_end):
                if lines[k].strip() and not lines[k].startswith("### "):
                    empty = False
                    break
                if lines[k].startswith("### "):
                    # Has a holding-pen H3 — not empty
                    empty = False
                    break
            if empty:
                # Drop the whole block including any trailing blank line
                drop_end = oq_end
                while drop_end < len(lines) and not lines[drop_end].strip():
                    drop_end += 1
                # Keep one blank for separation if we're not at EOF
                if drop_end < len(lines):
                    lines = lines[:oq_start] + lines[drop_end:]
                else:
                    lines = lines[:oq_start]
        feature_path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""),
                                encoding="utf-8")
        summary = f"resolved Q{args.q_num} (choice {args.choice}) in {feature_path.name}"

    elif args.verb == "remove":
        if args.q_num is None:
            raise BacklogEditError("-Q remove requires Q-number positional arg")
        reason = args.reason or "no reason provided"
        lines = text.splitlines()
        loc = _find_q_bullet(lines, args.q_num)
        if loc is None:
            raise BacklogEditError(
                f"Q{args.q_num} not found in pending Open Questions of "
                f"{feature_path.name}"
            )
        start, end, _ = loc
        header = lines[start]
        title_m = re.match(r"^\s*- \*\*Q\d+\s+—\s+([^*]+?)\*\*", header)
        title = title_m.group(1).strip() if title_m else "Untitled"
        original_body = "\n".join(lines[start:end]).rstrip()
        # Compose ### Removed H3 entry
        h3_lines = [
            "",
            f"### Q{args.q_num} — {title} (removed {today} — {reason})",
            "",
            "> Original Q context (preserved for audit trail):",
        ]
        for ol in original_body.splitlines():
            h3_lines.append(f"> {ol}")
        h3_lines.append("")
        # Remove pending bullet
        lines = lines[:start] + lines[end:]
        # Ensure ## Open Questions still exists; if not (no longer pending),
        # we need to re-create it because ### Removed sits inside it (audit trail).
        oq = _find_h2(lines, "Open Questions")
        if oq is None:
            lines, (oq_start, oq_end) = _ensure_open_questions_h2(lines)
        else:
            oq_start, oq_end = oq
        # Find or create ### Removed under ## Open Questions
        removed = _find_h3_in_h2(lines, oq_start, oq_end, "Removed")
        if removed is None:
            insert_at = oq_end
            # Insert at end of ## Open Questions
            while insert_at > oq_start + 1 and not lines[insert_at - 1].strip():
                insert_at -= 1
            lines = lines[:insert_at] + ["", "### Removed", ""] + h3_lines[1:] + lines[insert_at:]
        else:
            r_start, r_end = removed
            insert_at = r_end
            while insert_at > r_start + 1 and not lines[insert_at - 1].strip():
                insert_at -= 1
            lines = lines[:insert_at] + h3_lines + lines[insert_at:]
        feature_path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""),
                                encoding="utf-8")
        summary = f"removed Q{args.q_num} from {feature_path.name} (reason: {reason})"

    elif args.verb == "rewrite":
        if args.q_num is None:
            raise BacklogEditError("-Q rewrite requires Q-number positional arg")
        body = _read_q_body(args.inline, args.from_file)
        if not body.strip():
            raise BacklogEditError(
                "-Q rewrite requires a body via stdin, --from-file, or -m"
            )
        lines = text.splitlines()
        loc = _find_q_bullet(lines, args.q_num)
        if loc is None:
            raise BacklogEditError(
                f"Q{args.q_num} not found in pending Open Questions of "
                f"{feature_path.name}"
            )
        start, end, _ = loc
        # Recommendation-presence gate
        block = "\n".join(lines[start:end])
        has_recommendation = bool(
            re.search(r"^\s*-\s+\*\*Recommendation:\*\*", block, re.MULTILINE)
        )
        if has_recommendation and not args.force:
            raise BacklogEditError(
                f"Q{args.q_num} has a Recommendation — rewrites that change the "
                f"body can desync with the recommendation. Re-run with --force "
                f"to overwrite anyway."
            )
        new_bullet = _format_q_bullet(args.q_num, container_id, body)
        new_bullet_lines = new_bullet.splitlines()
        # Replace; preserve any trailing blank that was after the bullet
        lines = lines[:start] + new_bullet_lines + lines[end:]
        feature_path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""),
                                encoding="utf-8")
        summary = f"rewrote Q{args.q_num} in {feature_path.name}"
    else:
        raise BacklogEditError(f"unknown -Q verb: {args.verb}")

    # Post-conditions (F127 invariant)
    warnings = _post_conditions(args.slug, feature_path)
    print(f"{args.slug}: {summary}")
    for w in warnings:
        print(f"  warn: {w}", file=sys.stderr)
    return 0


def main(argv):
    # F128 — Q-management dispatch: detect `-Q` flag and route.
    if "-Q" in argv:
        return main_q(argv)
    if len(argv) < 5:
        print(__doc__, file=sys.stderr)
        return 2
    slug = argv[1]
    horizon = argv[2]
    row_id_arg = argv[3]
    status = argv[4]
    title_provided = len(argv) >= 6
    body_provided = len(argv) >= 7
    title = argv[5] if title_provided else ""
    body = argv[6] if body_provided else ""

    # Validate user-facing horizon arg here, before any file resolution.
    if horizon != "same":
        horizon_check = horizon.lstrip("# ").strip()
        if horizon_check not in VALID_HORIZONS:
            raise BacklogEditError(
                f"invalid horizon '{horizon}' "
                f"(expected one of {sorted(VALID_HORIZONS)} or 'same')"
            )

    backlog_path = find_backlog(slug)
    icebox_path = find_icebox(slug)  # may be None

    # If minting a new ID (Fnew/Bnew), resolve it across both files now so the
    # backlog/icebox shared namespace is respected.
    if row_id_arg in ("Fnew", "Bnew"):
        kind = row_id_arg[0]
        num = mint_cross_file_id(backlog_path, icebox_path, kind)
        row_id_arg = format_row_id(kind, num)

    src_file, dst_file, dst_horizon = resolve_files_for_edit(
        slug, backlog_path, horizon, row_id_arg, status
    )

    # Cross-file move: delete the row from its current file first. This is
    # not atomic — see Resolved decision § cross-file atomicity in F095.
    if src_file is not None:
        perform_edit(
            src_file, "same", row_id_arg, "delete",
            "", "", False, False,
        )

    result = perform_edit(
        dst_file,
        dst_horizon,
        row_id_arg,
        status,
        title,
        body,
        title_provided,
        body_provided,
    )
    append_messages(slug, result["summary"], backlog_path)
    write_state(slug, result)
    refresh_q_md(slug)

    print(f"{slug}: {result['summary']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
