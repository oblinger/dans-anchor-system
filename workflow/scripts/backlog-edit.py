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
"""

from __future__ import annotations

import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------
# Config

HOME = Path.home()
VAULT_ROOT = HOME / "ob" / "kmr"
SENTINEL = HOME / ".claude" / "state" / "agent-messages"

VALID_HORIZONS = {"Now", "Next", "Later", "Active", "Ready", "Done", "Verify"}
SKIP_PATH_FRAGMENTS = ("/.history/", "/worktrees/", "/Yore/", "/.trash/")


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
    for root, dirs, files in os.walk(VAULT_ROOT):
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
        # Strip optional '## ' prefix
        h2_name = horizon.lstrip("# ").strip()
        if h2_name not in VALID_HORIZONS:
            raise BacklogEditError(
                f"invalid horizon '{horizon}' "
                f"(expected one of {sorted(VALID_HORIZONS)} or 'same')"
            )

    # Handle delete first.
    if status == "delete":
        if existing is None:
            raise BacklogEditError(f"{row_id} not found — cannot delete")
        start, end, _, _ = existing
        del lines[start:end]
        backlog_path.write_text("".join(lines))
        return f"deleted {row_id}"

    # Preserve title / body from the existing row when caller omitted them
    # OR passed an empty string. Lets callers update bracket-only without
    # re-supplying the full content, and lets the body-only-update pattern
    # `backlog-edit.py {NAME} same <row> <status> "" "<new body>"` work
    # without blowing away the title.
    if existing is not None:
        existing_title, existing_body = parse_existing_row(lines[existing[0]])
        if not title_provided or title == "":
            title = existing_title
        if not body_provided or body == "":
            body = existing_body

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
    return f"{verb} {row_id} in {h2_name} [{status}]"


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

def main(argv):
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

    backlog_path = find_backlog(slug)
    summary = perform_edit(
        backlog_path,
        horizon,
        row_id_arg,
        status,
        title,
        body,
        title_provided,
        body_provided,
    )
    append_messages(slug, summary, backlog_path)
    refresh_q_md(slug)

    print(f"{slug}: {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
