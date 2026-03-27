#!/usr/bin/env python3
"""stat — Activity status tracking across projects.

Table columns: S# | Status | Ref | Notes

Usage:
  stat add <ref> <status> <notes> [--output]       Add activity. Returns S-number.
  stat update <S#> <status> [<notes>]              Update status (and optionally notes)
  stat archive <S#>                                Archive one entry
  stat archive-all                                 Archive everything (inbox zero)
  stat list [--active] [--status <filter>]         List activities
  stat show                                        Display master stat page
  stat activate <project-path>                     Add project to active list
  stat deactivate <project-path>                   Remove project from active list
  stat projects [--all] [--inactive]               List projects (default: active only)

The <ref> is the reference document this activity is about — a wiki-link like
"[[DMUX Rules]]" or a doc name like "R22". It goes in the Ref column.

Examples:
  stat add "[[DMUX Rules]]" "Working" "Starting rule fix on R22"
  stat add "[[2026-03-21 Standard Rule Sets]]" "Proposed" "Feature doc created"
  stat update S03200917 "Working:3" "Processing EX006"
  stat update S03200917 "Done" "All approved"
  stat archive S03200917
  stat activate ~/ob/kmr/prj/ClaudiMux/DictaMUX
"""

import os
import re
import sys
from datetime import datetime

import yaml


SKL_CONFIG = os.path.expanduser("~/.config/skl/config.yaml")
SKL_STATE = os.path.expanduser("~/.config/skl/state.yaml")
QUIET = False


# ── Config & State ──────────────────────────────────────────────────

def load_skl_config():
    if os.path.exists(SKL_CONFIG):
        with open(SKL_CONFIG) as f:
            return yaml.safe_load(f) or {}
    return {}


def load_state():
    if os.path.exists(SKL_STATE):
        with open(SKL_STATE) as f:
            return yaml.safe_load(f) or {}
    return {"active": []}


def save_state(state):
    os.makedirs(os.path.dirname(SKL_STATE), exist_ok=True)
    with open(SKL_STATE, "w") as f:
        yaml.dump(state, f, default_flow_style=False)


def get_master_stat_path():
    cfg = load_skl_config()
    root = os.path.expanduser(cfg.get("root", "~"))
    stat_rel = cfg.get("stat", "./stat.md")
    if os.path.isabs(stat_rel):
        return stat_rel
    return os.path.join(root, stat_rel)


def get_active_projects():
    state = load_state()
    return state.get("active", [])


def find_project_stat_dir(project_path):
    """Return the .anchor/stat/ directory for a project."""
    expanded = os.path.expanduser(project_path)
    stat_dir = os.path.join(expanded, ".anchor", "stat")
    return stat_dir


def find_project_stat_file(project_path):
    """Return the stat file (Now file) for a project, via config."""
    expanded = os.path.expanduser(project_path)
    cfg_path = os.path.join(expanded, ".anchor", "config.yaml")
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f) or {}
        now_path = cfg.get("now")
        if now_path:
            return os.path.join(expanded, now_path)
    return None


def find_current_project():
    """Walk up from cwd to find the anchor root."""
    d = os.getcwd()
    while d != "/":
        if os.path.isdir(os.path.join(d, ".anchor")):
            return d
        d = os.path.dirname(d)
    return None


# ── S-Number Generation ─────────────────────────────────────────────

def generate_s_number():
    """Generate a globally unique S-number by scanning all active projects."""
    now = datetime.now()
    base = now.strftime("S%m%d%H%M")

    # Collect all existing S-files across active projects
    existing = set()
    for proj in get_active_projects():
        stat_dir = find_project_stat_dir(proj["path"])
        if os.path.isdir(stat_dir):
            for f in os.listdir(stat_dir):
                if f.startswith("S") and f.endswith(".md"):
                    existing.add(f.replace(".md", ""))

    # Find unique number
    if base not in existing:
        return base

    for suffix in "abcdefghijklmnopqrstuvwxyz":
        candidate = f"{base}{suffix}"
        if candidate not in existing:
            return candidate

    # Extremely unlikely
    return f"{base}_{now.strftime('%S')}"


# ── Table Parsing ────────────────────────────────────────────────────

def parse_stat_file(path):
    """Parse a project stat file into (nav_lines, table_header, table_sep, rows, entries_text)."""
    if not os.path.exists(path):
        return [], None, None, [], ""

    with open(path) as f:
        content = f.read()

    lines = content.split("\n")

    # Find the table
    table_start = -1
    table_end = -1
    for i, line in enumerate(lines):
        if line.startswith("| S#") or (line.startswith("| ") and "Status" in line):
            table_start = i
        elif table_start >= 0 and line.startswith("|---"):
            continue
        elif table_start >= 0 and line.startswith("| "):
            continue
        elif table_start >= 0 and not line.startswith("|"):
            table_end = i
            break

    if table_start == -1:
        return lines, None, None, [], ""

    if table_end == -1:
        table_end = len(lines)

    nav = lines[:table_start]
    header = lines[table_start]
    sep = lines[table_start + 1] if table_start + 1 < len(lines) else ""
    rows = [l for l in lines[table_start + 2:table_end] if l.startswith("|")]
    entries = "\n".join(lines[table_end:])

    return nav, header, sep, rows, entries


def write_stat_file(path, nav, header, sep, rows, entries):
    """Write a project stat file."""
    lines = list(nav)
    # Ensure blank line before table
    if lines and lines[-1].strip() != "":
        lines.append("")
    if header:
        lines.append(header)
    if sep:
        lines.append(sep)
    for r in rows:
        lines.append(r)
    lines.append("")
    if entries and entries.strip():
        lines.append(entries.strip())
        lines.append("")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def make_table_row(s_num, status, ref, notes, has_detail=False):
    """Create a table row. S# is a link if detail file exists."""
    if has_detail:
        s_cell = f"[{s_num}](#{s_num})"
    else:
        s_cell = s_num
    return f"| {s_cell} | {status} | {ref} | {notes} |"


def parse_row(row):
    """Parse a table row into (s_num, status, ref, notes)."""
    parts = [p.strip() for p in row.split("|")[1:-1]]
    if len(parts) < 4:
        return None, None, None, None
    s_cell = parts[0]
    # Extract S-number from link or plain text
    m = re.match(r'\[?(S\w+)\]?', s_cell)
    s_num = m.group(1) if m else s_cell
    return s_num, parts[1], parts[2], parts[3]


# ── Master Page Rebuild ──────────────────────────────────────────────

def extract_nav(nav_lines):
    """Extract clean nav links from a project stat file's header."""
    nav_text = "\n".join(nav_lines).strip()
    # Remove frontmatter
    if nav_text.startswith("---"):
        end = nav_text.find("---", 3)
        if end > 0:
            nav_text = nav_text[end + 3:].strip()
    # Remove breadcrumbs and H1 headers
    lines = [l for l in nav_text.split("\n")
             if l.strip() and not l.startswith(":>>") and not l.startswith("#")]
    return lines


def rebuild_master():
    """Rebuild the master stat page from all active projects.

    Format: nav links from all projects (no gaps), then one merged table
    sorted reverse chronological, then inlined details.
    """
    master_path = get_master_stat_path()
    all_nav = []
    all_rows = []  # (s_num, row_text, project_path)
    all_details = []  # (s_num, detail_text)

    for proj in get_active_projects():
        stat_file = find_project_stat_file(proj["path"])
        if not stat_file or not os.path.exists(stat_file):
            continue

        nav, header, sep, rows, entries = parse_stat_file(stat_file)

        # Collect nav links
        nav_lines = extract_nav(nav)
        all_nav.extend(nav_lines)

        # Collect rows with RID for master page Proj column
        rid = proj.get("rid", os.path.basename(proj["path"]))
        for r in rows:
            s_num, _, _, _ = parse_row(r)
            all_rows.append((s_num or "", r, rid))

        # Collect details from S-files
        stat_dir = find_project_stat_dir(proj["path"])
        if os.path.isdir(stat_dir):
            for r in rows:
                s_num, _, _, _ = parse_row(r)
                if s_num:
                    detail_path = os.path.join(stat_dir, f"{s_num}.md")
                    if os.path.exists(detail_path):
                        with open(detail_path) as f:
                            detail = f.read().strip()
                        if detail:
                            all_details.append((s_num, detail))

    # Sort rows reverse chronological (S-numbers are timestamps, so reverse alpha works)
    all_rows.sort(key=lambda x: x[0], reverse=True)

    # Read existing master to preserve user content above "---" separator
    user_header = ""
    if os.path.exists(master_path):
        with open(master_path) as f:
            existing = f.read()
        # If the file has a "---" line, everything above it is user content
        if "\n---\n" in existing:
            user_header = existing.split("\n---\n")[0] + "\n---\n"
        elif existing.startswith("---\n"):
            # Just a separator at the very top, no user content
            user_header = "---\n"

    # Build the page
    lines = []

    # Preserve user header (notes, links, scratch space above ---)
    if user_header:
        lines.append(user_header)

    # Nav links — all projects, no gaps
    for nav_line in all_nav:
        lines.append(nav_line)

    # Blank line before table
    lines.append("")

    # Merged table with Proj column — Output instead of S#
    lines.append("| Output | Proj | Status | Ref | Notes |")
    lines.append("|--------|------|--------|-----|-------|")
    for _, row_text, rid in all_rows:
        # Insert Proj column after S# column
        parts = row_text.split("|")
        # parts[0] is empty (before first |), parts[1] is S#, parts[2..] are Status, Ref, Notes
        if len(parts) >= 5:
            lines.append(f"| {parts[1].strip()} | {rid} | {parts[2].strip()} | {parts[3].strip()} | {parts[4].strip()} |")
        else:
            lines.append(row_text)

    lines.append("")

    # Inlined details
    for s_num, detail in all_details:
        lines.append(f"## {s_num}")
        lines.append(detail)
        lines.append("")

    # Write master
    os.makedirs(os.path.dirname(master_path), exist_ok=True)
    with open(master_path, "w") as f:
        f.write("\n".join(lines) + "\n")


# ── Commands ─────────────────────────────────────────────────────────

def cmd_add(ref, status, notes, output=False):
    project = find_current_project()
    if not project:
        die("Not inside a project (no .anchor/ found)")

    stat_file = find_project_stat_file(project)
    if not stat_file:
        die("No stat file configured. Run 'cab-config init' first.")

    stat_dir = find_project_stat_dir(project)
    os.makedirs(stat_dir, exist_ok=True)

    s_num = generate_s_number()

    # Ensure project is active
    ensure_active(project)

    # Check for unfinalized Working entries (breadcrumb warning)
    nav, header, sep, rows, entries = parse_stat_file(stat_file)
    for r in rows:
        rs_num, rs_status, rs_ref, rs_notes = parse_row(r)
        if rs_status and rs_status.startswith("Working") and not QUIET:
            print(f"WARNING: Unfinalized {rs_num} — \"{rs_notes}\"", file=sys.stderr)

    # Create table row
    has_detail = output
    row = make_table_row(s_num, status, ref, notes, has_detail)

    if not header:
        header = "| S# | Status | Ref | Notes |"
        sep = "|----|--------|---------|-------|"

    rows.insert(0, row)
    write_stat_file(stat_file, nav, header, sep, rows, entries)

    # Create detail file if --output
    detail_path = None
    if output:
        detail_path = os.path.join(stat_dir, f"{s_num}.md")
        with open(detail_path, "w") as f:
            f.write("")

    rebuild_master()

    print(s_num)
    if detail_path:
        print(detail_path)


def cmd_update(s_num, status, notes=None):
    project = find_project_for_s_number(s_num)
    if not project:
        die(f"S-number {s_num} not found in any active project")

    stat_file = find_project_stat_file(project)
    nav, header, sep, rows, entries = parse_stat_file(stat_file)

    new_rows = []
    found = False
    for r in rows:
        rs_num, rs_status, rs_ref, rs_notes = parse_row(r)
        if rs_num == s_num:
            found = True
            new_notes = notes if notes is not None else rs_notes
            stat_dir = find_project_stat_dir(project)
            has_detail = os.path.exists(os.path.join(stat_dir, f"{s_num}.md"))
            new_rows.append(make_table_row(s_num, status, rs_ref, new_notes, has_detail))
        else:
            new_rows.append(r)

    if not found:
        die(f"S-number {s_num} not found in table")

    # Warn on commitment states
    commitment_states = {"Ready", "Agreed"}
    if status in commitment_states and not QUIET:
        print(f"⚠️  {status} means no more questions. Before proceeding, confirm:", file=sys.stderr)
        print(f"    - All implementation questions have been asked and answered", file=sys.stderr)
        print(f"    - No decisions will need user input during execution", file=sys.stderr)

    write_stat_file(stat_file, nav, header, sep, new_rows, entries)
    rebuild_master()
    print(f"Updated {s_num} → {status}")


def cmd_archive(s_num):
    project = find_project_for_s_number(s_num)
    if not project:
        die(f"S-number {s_num} not found in any active project")

    stat_file = find_project_stat_file(project)
    stat_dir = find_project_stat_dir(project)
    nav, header, sep, rows, entries = parse_stat_file(stat_file)

    # Remove row from table
    archived_row = None
    new_rows = []
    for r in rows:
        rs_num, _, _, _ = parse_row(r)
        if rs_num == s_num:
            archived_row = r
        else:
            new_rows.append(r)

    if not archived_row:
        die(f"S-number {s_num} not found in table")

    # Build archive content
    rs_num, rs_status, rs_ref, rs_notes = parse_row(archived_row)
    archive_content = f"## {s_num} — {rs_ref}\n**Status:** {rs_status}\n**Notes:** {rs_notes}\n"

    # Include detail file if exists
    detail_path = os.path.join(stat_dir, f"{s_num}.md")
    if os.path.exists(detail_path):
        with open(detail_path) as f:
            detail = f.read().strip()
        if detail:
            archive_content += "\n" + detail + "\n"
        os.remove(detail_path)

    # Append to daily archive
    archive_dir = os.path.join(stat_dir, "archive")
    os.makedirs(archive_dir, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    archive_file = os.path.join(archive_dir, f"stat-{today}.md")

    existing = ""
    if os.path.exists(archive_file):
        with open(archive_file) as f:
            existing = f.read()

    with open(archive_file, "a") as f:
        if existing and not existing.endswith("\n\n"):
            f.write("\n")
        f.write(archive_content + "\n")

    # Update stat file
    write_stat_file(stat_file, nav, header, sep, new_rows, entries)
    rebuild_master()
    print(f"Archived {s_num} → {archive_file}")


def cmd_archive_all():
    project = find_current_project()
    if not project:
        die("Not inside a project")

    stat_file = find_project_stat_file(project)
    if not stat_file:
        die("No stat file configured")

    nav, header, sep, rows, entries = parse_stat_file(stat_file)

    # Archive each row
    for r in rows:
        s_num, _, _, _ = parse_row(r)
        if s_num:
            cmd_archive(s_num)


def cmd_list(active_only=False, status_filter=None):
    for proj in get_active_projects():
        stat_file = find_project_stat_file(proj["path"])
        if not stat_file or not os.path.exists(stat_file):
            continue

        _, _, _, rows, _ = parse_stat_file(stat_file)
        rid = proj.get("rid", "?")

        for r in rows:
            s_num, s_status, s_ref, s_notes = parse_row(r)
            if not s_num:
                continue
            if active_only and s_status in ("Done", "—"):
                continue
            if status_filter and s_status != status_filter:
                continue
            print(f"{rid:8s} {s_num:12s} {s_status:12s} {s_ref}")


def cmd_show():
    master_path = get_master_stat_path()
    if not os.path.exists(master_path):
        rebuild_master()
    with open(master_path) as f:
        print(f.read())


def cmd_activate(project_path):
    expanded = os.path.expanduser(project_path)
    if not os.path.isdir(os.path.join(expanded, ".anchor")):
        die(f"Not a configured project: {expanded}")

    state = load_state()
    active = state.get("active", [])

    # Check if already active
    for p in active:
        if os.path.expanduser(p["path"]) == expanded:
            print(f"Already active: {project_path}")
            return

    # Get RID
    cfg_path = os.path.join(expanded, ".anchor", "config.yaml")
    rid = os.path.basename(expanded)
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f) or {}
        rid = cfg.get("rid", rid)

    active.append({"path": project_path, "rid": rid})
    state["active"] = active
    save_state(state)
    rebuild_master()
    print(f"Activated: {rid} ({project_path})")


def cmd_deactivate(project_path):
    expanded = os.path.expanduser(project_path)
    state = load_state()
    active = state.get("active", [])

    new_active = [p for p in active if os.path.expanduser(p["path"]) != expanded]
    if len(new_active) == len(active):
        die(f"Not active: {project_path}")

    state["active"] = new_active
    save_state(state)
    rebuild_master()
    print(f"Deactivated: {project_path}")


def cmd_projects(show_all=False, show_inactive=False):
    state = load_state()
    active = state.get("active", [])

    if not show_inactive:
        print("Active projects:")
        for p in active:
            print(f"  {p.get('rid', '?'):8s} {p['path']}")

    if show_all or show_inactive:
        # Scan for all configured projects
        cfg = load_skl_config()
        root = os.path.expanduser(cfg.get("root", "~"))
        active_paths = {os.path.expanduser(p["path"]) for p in active}

        if show_all:
            print("\nAll projects:")
        elif show_inactive:
            print("Inactive projects:")

        for dirpath, dirnames, _ in os.walk(root):
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in {
                "node_modules", "__pycache__", "target", "build", "Library"
            }]
            skl_cfg = os.path.join(dirpath, ".anchor", "config.yaml")
            if os.path.exists(skl_cfg):
                is_active = dirpath in active_paths
                if show_all or (show_inactive and not is_active):
                    marker = " (active)" if is_active else ""
                    with open(skl_cfg) as f:
                        pcfg = yaml.safe_load(f) or {}
                    rid = pcfg.get("rid", os.path.basename(dirpath))
                    print(f"  {rid:8s} {dirpath}{marker}")


# ── Helpers ──────────────────────────────────────────────────────────

def find_project_for_s_number(s_num):
    """Find which active project contains this S-number."""
    for proj in get_active_projects():
        stat_file = find_project_stat_file(proj["path"])
        if not stat_file or not os.path.exists(stat_file):
            continue
        _, _, _, rows, _ = parse_stat_file(stat_file)
        for r in rows:
            rs_num, _, _, _ = parse_row(r)
            if rs_num == s_num:
                return proj["path"]
    return None


def ensure_active(project_path):
    """Make sure the current project is in the active list."""
    state = load_state()
    active = state.get("active", [])
    expanded = os.path.expanduser(project_path)
    for p in active:
        if os.path.expanduser(p["path"]) == expanded:
            return
    # Auto-activate
    cfg_path = os.path.join(expanded, ".anchor", "config.yaml")
    rid = os.path.basename(expanded)
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f) or {}
        rid = cfg.get("rid", rid)
    active.append({"path": project_path, "rid": rid})
    state["active"] = active
    save_state(state)


def die(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


# ── Main ─────────────────────────────────────────────────────────────

def main():
    global QUIET
    args = sys.argv[1:]
    if not args:
        print(__doc__.strip())
        sys.exit(1)

    # Handle --quiet / -q flag
    if "--quiet" in args or "-q" in args:
        QUIET = True
        args = [a for a in args if a not in ("--quiet", "-q")]

    cmd = args[0]

    if cmd == "add" and len(args) >= 4:
        output = "--output" in args
        # Remove --output from args for positional parsing
        positional = [a for a in args[1:] if a != "--output"]
        if len(positional) >= 3:
            cmd_add(positional[0], positional[1], positional[2], output)
        else:
            die("Usage: stat add <ref> <status> <notes> [--output]")

    elif cmd == "update" and len(args) >= 3:
        notes = args[3] if len(args) > 3 else None
        cmd_update(args[1], args[2], notes)

    elif cmd == "archive" and len(args) >= 2:
        cmd_archive(args[1])

    elif cmd == "archive-all":
        cmd_archive_all()

    elif cmd == "list":
        active_only = "--active" in args
        status_filter = None
        if "--status" in args:
            idx = args.index("--status")
            if idx + 1 < len(args):
                status_filter = args[idx + 1]
        cmd_list(active_only, status_filter)

    elif cmd == "show":
        cmd_show()

    elif cmd == "activate" and len(args) >= 2:
        cmd_activate(args[1])

    elif cmd == "deactivate" and len(args) >= 2:
        cmd_deactivate(args[1])

    elif cmd == "projects":
        show_all = "--all" in args
        show_inactive = "--inactive" in args
        cmd_projects(show_all, show_inactive)

    else:
        print(__doc__.strip())
        sys.exit(1)


if __name__ == "__main__":
    main()
