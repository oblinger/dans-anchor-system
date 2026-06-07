#!/usr/bin/env python3
"""ask-render.py — render `{NAME} ask.md` from canonical markdown sources.

F117 (2026-06-07): markdown IS the durable state. ask.md is a rendered
view. This script scans the anchor's reachable feature docs and the
`{NAME} Questions.md` à la carte facet for pending Qs, scans the backlog
for `[Verify]` / `[Verify-by ...]` rows in active horizons, preserves any
existing `## Agent Resolutions` body verbatim (F086 accumulation; drift-
checking belongs to `/ask`, not here), and writes the three-section page.

Invoked by `/ask` only when format-by-span (per F125) calls for the page —
the multi-feature ≥3 Qs case. For 1-2 Qs inline or single-feature ≥3 Qs
glance, `/ask` surfaces directly without invoking this script.

Usage: ask-render.py <ANCHOR>
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

AUDIT_Q_PATH = Path.home() / ".claude" / "skills" / "audit" / "scripts" / "audit-q.py"


def _load_audit_q():
    spec = importlib.util.spec_from_file_location("audit_q", AUDIT_Q_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {AUDIT_Q_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["audit_q"] = mod
    spec.loader.exec_module(mod)
    return mod


A = _load_audit_q()

ACTIVE_HORIZONS = {"Active", "Ready", "Now", "Next"}


def _preserve_agent_resolutions(ask_path: Path) -> str:
    """Read existing ask.md, return verbatim body of `## Agent Resolutions`.

    Empty string if section absent or file missing. The /ask runbook owns
    F086 carry-forward + drift-check; this script passes through.
    """
    if not ask_path.is_file():
        return ""
    try:
        lines = ask_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return ""
    out: list[str] = []
    in_section = False
    for line in lines:
        if line.startswith("## "):
            if line.strip() == "## Agent Resolutions":
                in_section = True
                continue
            if in_section:
                break
            continue
        if in_section:
            out.append(line)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


def _verify_rows(entries) -> list:
    """Backlog rows whose status begins with 'Verify' in active horizons.

    Bare-/ask runbook step 1 disregards `## Later` entirely; this script
    mirrors that scope.
    """
    out = []
    for e in entries:
        if e.horizon not in ACTIVE_HORIZONS:
            continue
        if e.status.startswith("Verify"):
            out.append(e)
    return out


_TITLE_RE = re.compile(
    r"^- \*\*(?:\[\[)?(?:\[[A-Z]+\]\s+)?([^\*\]]+?)(?:\]\])?\*\*"
)


def _row_title(raw_body: str) -> str:
    m = _TITLE_RE.match(raw_body)
    return m.group(1).strip() if m else "(no title)"


def render(anchor: str) -> int:
    vault_root = A.VAULT_ROOT
    backlogs = A.find_anchor_backlogs(vault_root)
    if anchor not in backlogs:
        print(
            f"ask-render: anchor '{anchor}' not found "
            f"(no '{anchor} Backlog.md' under {vault_root}).",
            file=sys.stderr,
        )
        return 2
    backlog_file = backlogs[anchor]
    ask_path = backlog_file.parent / f"{anchor} ask.md"

    vault_index = A.build_vault_index(vault_root)
    sources = A.find_ask_format_files(
        {anchor: backlog_file}, vault_index, reachable_only=True
    )

    by_file: dict[Path, list] = {}
    for container_id, path in sources:
        qs = A.extract_q_entries(path, container_id)
        if qs:
            by_file[path] = qs

    entries = A.backlog_entries(backlog_file, vault_index)
    verifies = _verify_rows(entries)

    agent_res_body = _preserve_agent_resolutions(ask_path)

    out: list[str] = []
    out.append("---")
    out.append(
        "description: bare `/ask` snapshot — agent resolutions and what the user still needs to verify or answer."
    )
    out.append("---")
    out.append("")
    out.append("")
    out.append(f"# [[{anchor}]] ask")
    out.append("")

    if agent_res_body:
        out.append("## Agent Resolutions")
        out.append("")
        out.append(agent_res_body)
        out.append("")

    if verifies:
        out.append("## User Verifications")
        out.append("")
        for e in verifies:
            title = _row_title(e.raw_body)
            link = ""
            if e.link is not None and e.link.target_basename:
                link = f"[[{e.link.target_basename}]] "
            out.append(f"- {link}**[{e.status}]** — {title}")
        out.append("")

    if by_file:
        out.append("## Questions")
        out.append("")
        for path in sorted(by_file.keys()):
            qs = by_file[path]
            qnums = ", ".join(f"Q{q.q_num}" for q in qs)
            count = len(qs)
            label = "Q" if count == 1 else "Qs"
            out.append(f"- [[{path.stem}]] — {count} {label} ({qnums}).")
        out.append("")

    if not agent_res_body and not verifies and not by_file:
        out.append("_Nothing pending in scope._")
        out.append("")

    ask_path.write_text("\n".join(out), encoding="utf-8")
    total_qs = sum(len(v) for v in by_file.values())
    print(
        f"ask-render: wrote {ask_path} "
        f"({len(verifies)} Verifies, "
        f"{total_qs} Qs across {len(by_file)} sources)."
    )
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: ask-render.py <ANCHOR>", file=sys.stderr)
        return 2
    return render(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
