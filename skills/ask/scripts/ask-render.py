#!/usr/bin/env python3
"""ask-render.py — render `{NAME} ask.md` from canonical markdown sources.

F117 (2026-06-07): markdown IS the durable state. ask.md is a rendered
view of the anchor's reachable feature docs (their `## Open Questions`) and
the backlog's `[Verify]` rows, with two AUTHORED sections preserved verbatim
across renders: `## Agent Resolutions` (F086 accumulation) and any anchor-
level questions authored directly into `## Questions`. There is NO separate
`{NAME} Questions.md` file — anchor-level Qs live here, in the ask file.

The render scans feature docs for pending Qs → feature-pointer lines in
`## Questions`; scans the backlog for `[Verify]` / `[Verify-by ...]` rows in
active horizons → `## User Verifications`; preserves the two authored
sections (drift-checking belongs to `/ask`, not here); and writes the
three-section page atomically. Always runs (per F127's render-audit-glance
invariant), regardless of question count.

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

# Horizons bare-/ask considers when assessing what to ask. `## Later` and
# `## Icebox` are disregarded (user-parked / iced). The `## Verify` horizon
# (F100) holds user-actionable [Verify] rows and IS in scope — draining them
# is a core purpose of bare /ask.
IN_SCOPE_HORIZONS = {"Active", "Ready", "Now", "Next", "Verify"}


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


# A rendered feature-doc pointer line, e.g. `- [[F28 — Naming]] — 3 Qs (Q1, Q2).`
# These are regenerated every render; everything else in `## Questions` is an
# authored anchor-level question and must be preserved.
_FEATURE_POINTER_RE = re.compile(r"^- \[\[[^\]]+\]\] — \d+ Qs? \(.*\)\.\s*$")


def _preserve_authored_questions(ask_path: Path) -> str:
    """Read existing ask.md, return the authored anchor-level Q bullets from
    `## Questions` — everything EXCEPT the rendered feature-doc pointer lines.

    Anchor-level questions are authored directly into `## Questions` (full
    ask-format) and must survive re-renders, the same way `## Agent
    Resolutions` does. The feature-doc pointer lines are regenerated each
    render, so they're stripped here. There is no `{NAME} Questions.md` —
    the ask file IS the home for anchor-level Qs.
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
            if line.strip() == "## Questions":
                in_section = True
                continue
            if in_section:
                break
            continue
        if in_section:
            if _FEATURE_POINTER_RE.match(line):
                continue
            out.append(line)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


def _verify_rows(entries) -> list:
    """Backlog rows whose status begins with 'Verify' in in-scope horizons.

    In-scope = Active/Ready/Now/Next/Verify. Bare-/ask runbook step 1
    disregards `## Later` and `## Icebox` entirely; this script mirrors that.
    The dedicated `## Verify` horizon (F100) is where most [Verify] rows live,
    so it MUST be in scope or bare /ask surfaces nothing to verify.
    """
    out = []
    for e in entries:
        if e.horizon not in IN_SCOPE_HORIZONS:
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


_VERIFY_INSTR_RE = re.compile(r"\*\*Verify \(you\):\*\*\s*(.+)$", re.MULTILINE)


def _verify_instruction(raw_body: str) -> "str | None":
    """The user-actionable verify steps for a Verify row.

    A Verify row carries a `**Verify (you):** <do this — open X, click Y,
    confirm Z>` marker; this is what `## User Verifications` renders after the
    link. Without it the row would echo its title ("verify F125"), which gives
    the user no idea what to actually do. Returns None when the marker is
    absent (caller falls back to the title).
    """
    m = _VERIFY_INSTR_RE.search(raw_body)
    if not m:
        return None
    instr = re.sub(r"\s*\^[A-Za-z0-9_-]+\s*$", "", m.group(1))  # drop trailing block-id
    instr = " ".join(instr.split())
    return instr or None


_BLOCK_ID_RE = re.compile(r"\^([A-Za-z0-9_-]+)\s*$", re.MULTILINE)


def _row_block_id(raw_body: str) -> "str | None":
    ms = _BLOCK_ID_RE.findall(raw_body)
    return ms[-1] if ms else None


def _verify_link(e, backlog_stem: str) -> str:
    """Resolvable link for a Verify row, with trailing space.

    Prefer the feature-doc link when it IS the row's feature (its basename
    starts with the row identifier); else the row's backlog block-id anchor;
    else the backlog file itself (always resolves). NEVER an incidental body
    link (e.g. a `last-click.json` href) — that produced broken `[[last-click]]`
    links once B-row Verifies came into scope.
    """
    ident = (e.identifier or "").strip()
    if (
        e.link is not None
        and e.link.target_basename
        and ident
        and e.link.target_basename.startswith(ident)
    ):
        return f"[[{e.link.target_basename}]] "
    bid = _row_block_id(e.raw_body)
    if bid:
        return f"[[{backlog_stem}#^{bid}|{ident or bid}]] "
    if ident:
        return f"[[{backlog_stem}|{ident}]] "
    return f"[[{backlog_stem}]] "


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

    entries = A.backlog_entries(backlog_file, vault_index)
    verifies = _verify_rows(entries)

    # In-scope-horizon filter (per ask/SKILL.md § Bare invocation step 1):
    # ## Later and ## Icebox are disregarded; Active/Ready/Now/Next/Verify count.
    # A feature doc is in scope iff its backlog row sits in one of those horizons
    # (incl. ## Verify — e.g. a [Verify] feature with still-pending Qs).
    active_basenames: set[str] = set()
    for e in entries:
        if e.horizon not in IN_SCOPE_HORIZONS:
            continue
        if e.link is not None and e.link.target_basename:
            active_basenames.add(e.link.target_basename)

    by_file: dict[Path, list] = {}
    for container_id, path in sources:
        # Only feature docs whose stem matches an active-horizon backlog row.
        # The legacy à la carte `{NAME} Questions.md` (container_id == anchor)
        # is no longer a source — anchor-level Qs are authored directly into
        # `{NAME} ask.md` and preserved by _preserve_authored_questions().
        if container_id == anchor or path.stem not in active_basenames:
            continue
        qs = A.extract_q_entries(path, container_id)
        if qs:
            by_file[path] = qs

    agent_res_body = _preserve_agent_resolutions(ask_path)
    authored_q_body = _preserve_authored_questions(ask_path)

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
        backlog_stem = backlog_file.stem
        for e in verifies:
            instr = _verify_instruction(e.raw_body) or _row_title(e.raw_body)
            link = _verify_link(e, backlog_stem)
            out.append(f"- {link}**[{e.status}]** — {instr}")
        out.append("")

    if by_file or authored_q_body:
        out.append("## Questions")
        out.append("")
        for path in sorted(by_file.keys()):
            qs = by_file[path]
            qnums = ", ".join(f"Q{q.q_num}" for q in qs)
            count = len(qs)
            label = "Q" if count == 1 else "Qs"
            out.append(f"- [[{path.stem}]] — {count} {label} ({qnums}).")
        if authored_q_body:
            if by_file:
                out.append("")  # separate rendered pointers from authored Qs
            out.append(authored_q_body)
        out.append("")

    if not agent_res_body and not verifies and not by_file and not authored_q_body:
        out.append("_Nothing pending in scope._")
        out.append("")

    ask_path.write_text("\n".join(out), encoding="utf-8")
    total_qs = sum(len(v) for v in by_file.values())
    authored_note = " + authored anchor Qs" if authored_q_body else ""
    print(
        f"ask-render: wrote {ask_path} "
        f"({len(verifies)} Verifies, "
        f"{total_qs} Qs across {len(by_file)} sources{authored_note})."
    )
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: ask-render.py <ANCHOR>", file=sys.stderr)
        return 2
    return render(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
