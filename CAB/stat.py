#!/usr/bin/env python3
"""stat — Activity status tracking across projects.

Table columns: S# | Status | Output | Activity

Usage:
  stat add <status> <output> <activity>    Add activity. Returns S-number.
  stat update <S#> <status> [<activity>]   Update status (and optionally activity)
  stat archive <S#>                        Archive one entry
  stat archive-all                         Archive everything (inbox zero)
  stat show                                Display master Ops page
  stat activate <project-path>             Add project to active list
  stat deactivate <project-path>           Remove project from active list
  stat projects [--all] [--inactive]       List projects (default: active only)

Positional args on add: status, output, activity. All three mandatory.
  status   — lifecycle state (Designing, Implementing, Review, Done, etc.)
  output   — wiki-link to output document, or - if none
  activity — free text description

Examples:
  stat add "Designing" "[[2026-03-28 Window Management]]" "menu/keyboard-driven window creation"
  stat add "Done" "-" "Docs audit: clean"
  stat update S03280830 "Implementing" "Starting phase 1"
  stat archive S03280830
  stat archive-all
  stat activate ~/ob/kmr/prj/ClaudiMux/DictaMUX
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml


# ── Config ────────────────────────────────────────────────────────────

SKL_CONFIG = os.path.expanduser("~/.config/skl/config.yaml")
SKL_STATE = os.path.expanduser("~/.config/skl/state.yaml")
QUIET = False


def load_skl_config():
    if os.path.exists(SKL_CONFIG):
        with open(SKL_CONFIG) as f:
            return yaml.safe_load(f) or {}
    return {}


def load_state():
    if os.path.exists(SKL_STATE):
        with open(SKL_STATE) as f:
            return yaml.safe_load(f) or {}
    return {}


def save_state(state):
    os.makedirs(os.path.dirname(SKL_STATE), exist_ok=True)
    with open(SKL_STATE, "w") as f:
        yaml.dump(state, f, default_flow_style=False)


def get_master_stat_path():
    cfg = load_skl_config()
    root = os.path.expanduser(cfg.get("root", "~"))
    stat_rel = cfg.get("stat", "Ops.md")
    return os.path.join(root, stat_rel)


def get_active_projects():
    state = load_state()
    return state.get("active", [])


def find_project_stat_file(project_path):
    expanded = os.path.expanduser(project_path)
    cfg_path = os.path.join(expanded, ".anchor", "config.yaml")
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f) or {}
        now_rel = cfg.get("now")
        if now_rel:
            return os.path.join(expanded, now_rel)
    return None


def find_project_stat_dir(project_path):
    expanded = os.path.expanduser(project_path)
    stat_dir = os.path.join(expanded, ".anchor", "stat")
    return stat_dir


def find_project_outputs_dir(project_path):
    """Find the outputs folder for a project. Returns absolute path."""
    expanded = os.path.expanduser(project_path)
    cfg_path = os.path.join(expanded, ".anchor", "config.yaml")
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f) or {}
        outputs_rel = cfg.get("outputs")
        if outputs_rel:
            return os.path.join(expanded, outputs_rel)
    # Default: {RID} Docs/{RID} Plan/{RID} Outputs
    rid = os.path.basename(expanded)
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f) or {}
        rid = cfg.get("rid", rid)
    return os.path.join(expanded, f"{rid} Docs", f"{rid} Plan", f"{rid} Outputs")


def find_current_project():
    cwd = os.getcwd()
    p = cwd
    while p != "/":
        if os.path.exists(os.path.join(p, ".anchor", "config.yaml")):
            return p
        p = os.path.dirname(p)
    return None


def generate_s_number():
    now = datetime.now()
    base = now.strftime("S%m%d%H%M")
    existing = set()
    for proj in get_active_projects():
        stat_file = find_project_stat_file(proj["path"])
        if stat_file and os.path.exists(stat_file):
            _, _, _, rows, _ = parse_stat_file(stat_file)
            for r in rows:
                s_num, _, _, _ = parse_row(r)
                if s_num:
                    existing.add(s_num)

    if base not in existing:
        return base
    for suffix in "abcdefghijklmnopqrstuvwxyz":
        candidate = f"{base}{suffix}"
        if candidate not in existing:
            return candidate


# ── Table Parsing ────────────────────────────────────────────────────

def parse_stat_file(path):
    """Parse a project stat file into (nav_lines, table_header, table_sep, rows, entries_text)."""
    if not os.path.exists(path):
        return [], None, None, [], ""

    with open(path) as f:
        content = f.read()

    lines = content.split("\n")

    table_start = -1
    table_end = -1
    for i, line in enumerate(lines):
        if line.startswith("| S#"):
            table_start = i
        elif table_start >= 0 and line.startswith("|"):
            continue
        elif table_start >= 0 and line.strip() == "":
            # Blank line — could be end of table or just spacing
            # Look ahead for more table rows
            has_more_rows = any(l.startswith("| ") for l in lines[i+1:i+5])
            if has_more_rows:
                continue
            table_end = i
            break
        elif table_start >= 0:
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


def make_table_row(s_num, status, output, activity):
    """Create a table row."""
    return f"| {s_num} | {status} | {output} | {activity} |"


def parse_row(row):
    """Parse a table row into (s_num, status, output, activity)."""
    parts = [p.strip() for p in row.split("|")[1:-1]]
    if len(parts) < 4:
        return None, None, None, None
    s_cell = parts[0]
    m = re.match(r'\[?(S\w+)\]?', s_cell)
    s_num = m.group(1) if m else s_cell
    return s_num, parts[1], parts[2], parts[3]


# ── Master Page Rebuild ──────────────────────────────────────────────

def extract_nav(nav_lines):
    nav_text = "\n".join(nav_lines).strip()
    if nav_text.startswith("---"):
        end = nav_text.find("---", 3)
        if end > 0:
            nav_text = nav_text[end + 3:].strip()
    lines = [l for l in nav_text.split("\n")
             if l.strip() and not l.startswith(":>>") and not l.startswith("#")]
    return lines


def rebuild_master():
    """Rebuild the master Ops page — merged table only, no inlined details."""
    master_path = get_master_stat_path()
    all_nav = []
    all_rows = []  # (s_num, row_text, rid)

    for proj in get_active_projects():
        stat_file = find_project_stat_file(proj["path"])
        if not stat_file or not os.path.exists(stat_file):
            continue

        nav, header, sep, rows, entries = parse_stat_file(stat_file)
        nav_lines = extract_nav(nav)
        all_nav.extend(nav_lines)

        rid = proj.get("rid", os.path.basename(proj["path"]))
        for r in rows:
            s_num, _, _, _ = parse_row(r)
            all_rows.append((s_num or "", r, rid))

    all_rows.sort(key=lambda x: x[0], reverse=True)

    # Preserve user content above --- separator
    user_header = ""
    if os.path.exists(master_path):
        with open(master_path) as f:
            existing = f.read()
        if "\n---\n" in existing:
            user_header = existing.split("\n---\n")[0] + "\n---\n"
        elif existing.startswith("---\n"):
            user_header = "---\n"

    lines = []

    if user_header:
        lines.append(user_header)

    for nav_line in all_nav:
        lines.append(nav_line)

    lines.append("")

    # Merged table: Proj | Status | Output | Activity
    lines.append("| Proj | Status | Output | Activity |")
    lines.append("|------|--------|--------|----------|")
    for _, row_text, rid in all_rows:
        parts = row_text.split("|")
        # parts: [empty, S#, Status, Output, Activity, empty]
        if len(parts) >= 5:
            lines.append(f"| [[{rid}]] | {parts[2].strip()} | {parts[3].strip()} | {parts[4].strip()} |")
        else:
            lines.append(row_text)

    lines.append("")

    os.makedirs(os.path.dirname(master_path), exist_ok=True)
    with open(master_path, "w") as f:
        f.write("\n".join(lines) + "\n")


# ── Commands ─────────────────────────────────────────────────────────

def cmd_add(status, output, activity):
    project = find_current_project()
    if not project:
        die("Not inside a project (no .anchor/ found)")

    stat_file = find_project_stat_file(project)
    if not stat_file:
        die("No stat file configured. Run 'cab-config init' first.")

    s_num = generate_s_number()

    ensure_active(project)

    # Check for unfinalized Working entries
    nav, header, sep, rows, entries = parse_stat_file(stat_file)
    for r in rows:
        rs_num, rs_status, _, rs_activity = parse_row(r)
        if rs_status and rs_status.startswith("Working") and not QUIET:
            print(f"WARNING: Unfinalized {rs_num} — \"{rs_activity}\"", file=sys.stderr)

    # If output is not "-", create the output file in the outputs folder
    output_path = None
    if output and output != "-" and output != "—":
        outputs_dir = find_project_outputs_dir(project)
        os.makedirs(outputs_dir, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        output_filename = f"{today} {output}.md"
        output_path = os.path.join(outputs_dir, output_filename)
        # Ensure unique name
        if os.path.exists(output_path):
            for suffix in "bcdefghijklmnopqrstuvwxyz":
                candidate = os.path.join(outputs_dir, f"{today} {output} {suffix}.md")
                if not os.path.exists(candidate):
                    output_path = candidate
                    output_filename = f"{today} {output} {suffix}.md"
                    break
        # Create empty file
        with open(output_path, "w") as f:
            f.write("")
        # Use wiki-link in the table
        output_link = f"[[{output_filename.replace('.md', '')}]]"
    else:
        output_link = output  # "-" or "—"

    row = make_table_row(s_num, status, output_link, activity)

    if not header:
        header = "| S# | Status | Output | Activity |"
        sep = "|----|--------|--------|----------|"

    rows.insert(0, row)
    write_stat_file(stat_file, nav, header, sep, rows, entries)
    rebuild_master()
    print(s_num)
    if output_path:
        print(output_path)


def cmd_update(s_num, status, activity=None):
    project = find_project_for_s_number(s_num)
    if not project:
        die(f"S-number {s_num} not found in any active project")

    stat_file = find_project_stat_file(project)
    nav, header, sep, rows, entries = parse_stat_file(stat_file)

    new_rows = []
    found = False
    for r in rows:
        rs_num, rs_status, rs_output, rs_activity = parse_row(r)
        if rs_num == s_num:
            found = True
            new_activity = activity if activity is not None else rs_activity
            new_rows.append(make_table_row(s_num, status, rs_output, new_activity))
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

    rs_num, rs_status, rs_output, rs_activity = parse_row(archived_row)
    archive_content = f"## {s_num} — {rs_activity}\n**Status:** {rs_status}\n**Output:** {rs_output}\n"

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

    for r in rows:
        s_num, _, _, _ = parse_row(r)
        if s_num:
            cmd_archive(s_num)


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

    for p in active:
        if os.path.expanduser(p["path"]) == expanded:
            print(f"Already active: {project_path}")
            return

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
            anchor_cfg = os.path.join(dirpath, ".anchor", "config.yaml")
            if os.path.exists(anchor_cfg):
                is_active = dirpath in active_paths
                if show_all or (show_inactive and not is_active):
                    marker = " (active)" if is_active else ""
                    with open(anchor_cfg) as f:
                        pcfg = yaml.safe_load(f) or {}
                    rid = pcfg.get("rid", os.path.basename(dirpath))
                    print(f"  {rid:8s} {dirpath}{marker}")


# ── Helpers ──────────────────────────────────────────────────────────

def find_project_for_s_number(s_num):
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
    state = load_state()
    active = state.get("active", [])
    expanded = os.path.expanduser(project_path)
    for p in active:
        if os.path.expanduser(p["path"]) == expanded:
            return
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

    if "--quiet" in args or "-q" in args:
        QUIET = True
        args = [a for a in args if a not in ("--quiet", "-q")]

    cmd = args[0]

    if cmd == "add" and len(args) >= 4:
        cmd_add(args[1], args[2], args[3])
    elif cmd == "add":
        die("Usage: stat add <status> <output> <activity>")

    elif cmd == "update" and len(args) >= 3:
        activity = args[3] if len(args) > 3 else None
        cmd_update(args[1], args[2], activity)

    elif cmd == "archive" and len(args) >= 2:
        cmd_archive(args[1])

    elif cmd == "archive-all":
        cmd_archive_all()

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
