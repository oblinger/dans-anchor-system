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



# --------------------------------------------------------------------------
# Config

HOME = Path.home()
VAULT_ROOT = HOME / "ob" / "kmr"
SENTINEL = HOME / ".claude" / "state" / "agent-messages"
STATE_FILE = HOME / ".config" / "anchor-system" / "backlog-edit" / "state.json"

VALID_HORIZONS = {"Now", "Next", "Later", "Active", "Ready", "Done", "Verify", "Icebox"}
ICEBOX_HORIZON = "Icebox"
ICEBOX_DEFAULT_H2 = "Iced"
SKIP_PATH_FRAGMENTS = ("/.history/", "/worktrees/", "/Yore/", "/.trash/", "/Closet/")

# Closed set of canonical backlog-row status brackets (per [[SKA workflow]]).
# Write-time enforcement lives in validate_status() below. Non-canonical brackets
# ([Designed], [Foo], …) get rejected at state Backlog define/set rather than
# silently written, then rendering as ⚠ with no Ready/Questions banner mapping.
VALID_STATUS_BASE = frozenset({
    "Ready", "Active", "Designing", "Questions",
    "Verify", "Blocked", "Waiting", "Watching",
    "User",  # F259 — gated on a genuinely user-only ACTION (auth / login /
             # permission-click / 2FA); body carries a `- **User:**` sub-bullet.
    "Done",
    # Feature-doc lifecycle aliases (canonical-alias, accepted)
    "Implementing",  # = Active
    "Agreed",        # = Ready
})
# Compound status forms — order matters only for readability.
VALID_STATUS_PATTERNS = (
    re.compile(r"^\d+\s+Questions?$", re.IGNORECASE),                        # "3 Questions"
    re.compile(r"^\d+\s+Ready$", re.IGNORECASE),                             # "5 Ready" (milestone)
    re.compile(r"^Waiting\s+\d+[dhmy]$", re.IGNORECASE),                     # "Waiting 7d"
    re.compile(r"^Watching\s+\d+[dhmy]$", re.IGNORECASE),                    # "Watching 14d"
    re.compile(r"^Verify(-by\s+\d{4}-\d{2}-\d{2})?$", re.IGNORECASE),        # "Verify-by 2026-06-02"
    re.compile(r"^Done(\s+\d{4}-\d{2}-\d{2})?$", re.IGNORECASE),             # "Done 2026-06-04"
    re.compile(r"^Blocked(\s+F\d+)?$", re.IGNORECASE),                       # "Blocked F210"
)

# A Questions-bracket promise: the linked target must contain ≥1 of these.
Q_MARKER_RE = re.compile(r"\bQ\d+\s+—")
# Extract the basename from the first wiki-link in a body string.
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
# Statuses that assert the Questions-target promise.
QUESTIONS_STATUS_RE = re.compile(r"^(\d+\s+)?Questions?$", re.IGNORECASE)
# Statuses to nudge toward Later/Icebox.
VERIFY_WATCHING_FAMILY = ("Verify", "Watching")
NUDGE_BUCKETS = {"Now", "Next", "Active", "Ready"}


def validate_status(status):
    """Reject non-canonical brackets at write time.

    Accepts 'same' / 'delete' (control tokens used by state's row-edit
    delegation). Otherwise the status must match either VALID_STATUS_BASE
    (case-sensitive) or one of VALID_STATUS_PATTERNS (case-insensitive for
    the keyword, exact for the numeric suffix).
    """
    if status in ("same", "delete"):
        return
    stripped = status.strip().strip("[]").strip()
    if stripped in VALID_STATUS_BASE:
        return
    for pat in VALID_STATUS_PATTERNS:
        if pat.match(stripped):
            return
    raise BacklogEditError(
        f"invalid status {status!r}; expected one of "
        f"{sorted(VALID_STATUS_BASE)} or a compound form "
        f"(N Questions, N Ready, Waiting Nd, Watching Nd, "
        f"Verify-by YYYY-MM-DD, Done YYYY-MM-DD, Blocked FNNN)"
    )


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
    # Symlink chains (e.g. ~/.claude/skills, symlinks/_.claude/skills) can register
    # one real file under several paths — collapse same-inode hits so a single real
    # backlog isn't mistaken for multiple candidates (F261).
    by_realpath = {m.resolve(): m for m in matches}
    if len(by_realpath) > 1:
        raise BacklogEditError(
            f"multiple '{target}' candidates: " + ", ".join(str(m) for m in matches)
        )
    return next(iter(by_realpath.values()))


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
    # Collapse same-inode symlink hits (F261) — see find_backlog for the rationale.
    by_realpath = {m.resolve(): m for m in matches}
    if len(by_realpath) > 1:
        raise BacklogEditError(
            f"multiple '{target}' candidates: " + ", ".join(str(m) for m in matches)
        )
    return next(iter(by_realpath.values()))


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
    _selffire(icebox)
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


def verify_questions_constraint(status, body, row_id=None):
    """Raise BacklogEditError if status asserts a Questions promise that the
    body's wiki-link target cannot honor.

    The promise: a [Questions] / [N Questions] bracket means following the
    row's link lands on a file with ≥1 `Q<n> —` marker. The script enforces
    this at write time so the agent learns immediately instead of leaving a
    broken contract for /audit q to catch later.

    Skip when:
      - status is not a Questions variant
      - the row IS a standalone `Q<n>` question row (F275) — the row itself is
        the question (self-backing), so its number lives in the header, not a
        linked doc or an inline sub-bullet
      - body is empty (no link to check; caller responsible for soundness)
      - the wiki-link target file cannot be located in the vault
        (warn-not-fail — may be a fresh anchor or unresolvable basename)
    """
    if not QUESTIONS_STATUS_RE.match(status.strip()):
        return
    if row_id and re.match(r"^Q\d+$", row_id):
        return  # F275 — a standalone Q-row is its own question
    if not body or not body.strip():
        raise BacklogEditError(
            f"[{status}] requires a body with a wiki-link to a target containing "
            f"Q<n> markers; body is empty. Add the link first, then re-run."
        )
    # B/T-row inline Qs (R-backlog-05): a row may carry its own numbered Qs as
    # `- **Q<n> — …**` sub-bullets instead of linking a feature doc — the row
    # itself is then the Q-bearing target and the promise is honored in place.
    if re.search(r"\*\*Q\d+\s+—", body):
        return
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


# F240 — verification ownership (who-is-better-positioned). A verification may
# surface to the user only when the user's answer is genuinely better than the
# agent's; a question phrased as a machine event ("did X mint/run/render",
# "does the file exist") is agent-answerable from a file/log/probe and must
# never reach the user's queue. The heuristic is deliberately narrow (favors
# false negatives): a refused legitimate taste-check erodes trust in the gate;
# a missed mechanical check is still caught by audit-q C47 on the next pass.
# Single source of truth — audit-q.py imports is_mechanical_verify from here.

_MECH_VERBS = (
    r"(?:mint|run|ran|render|pass|fail|exist|land|fire|create|"
    r"write|wrote|written|fold|commit|install|resolve)(?:s|ed|ing)?"
)
_MECH_INTERROG_RE = re.compile(
    rf"^(?:did|does|is|was)\b.*?\b{_MECH_VERBS}\b", re.IGNORECASE
)
_MECH_CMD_FORM_RE = re.compile(r"`[^`]+`|(?<!\w)--[a-z][\w-]+")
_TASTE_WORDS_RE = re.compile(
    r"\b(?:reads?|feels?|looks?|prefer|like|good|right|okay|ok|acceptable|"
    r"happy|taste|sense|clear|clean|want|better|worth|keep)\b",
    re.IGNORECASE,
)
_WHY_USER_ANNOT_RE = re.compile(r"\s*·\s*\*why-user:.*?\*\s*$")


def is_mechanical_verify(text):
    """F240 — True when a `- **Verify:**` question is phrased as a machine
    event the agent can check itself. Two forms (v1, deliberately narrow):
    a leading interrogative about a machine event (`did/does/is/was … +
    mint/run/render/pass/fail/exist/land/fire/create/write/fold/commit/
    install/resolve`), or a command-form ask (backtick span / `--flag`
    token) with no taste word anywhere in the line."""
    if not text:
        return False
    line = _WHY_USER_ANNOT_RE.sub("", text.strip()).strip()
    if _MECH_INTERROG_RE.match(line):
        return True
    if _MECH_CMD_FORM_RE.search(line) and not _TASTE_WORDS_RE.search(line):
        return True
    return False


def _verify_family(status):
    """True for the brackets the F240 ownership gate governs."""
    s = (status or "").strip()
    return s.startswith("Verify") or s.startswith("Watching")


def verify_ownership_gate(status, row_id, eff_verify, why_user):
    """F240 — enforce who-is-better-positioned at the moment a Verify is
    minted. Fires when a row ENTERS the Verify/Verify-by/Watching family or
    its `- **Verify:**` question is (re)written; a same-family re-touch that
    keeps the existing question is grandfathered (already vetted at entry).

    Refusals: (1) a mechanically-phrased question is agent-grade regardless
    of --why-user — run it now or park [Waiting] with an agent-check plan;
    (2) missing --why-user (and no existing `*why-user:*` annotation) —
    the surfacing must name the human faculty it needs.

    Returns the effective verify text with the why-user annotation appended
    (the render surfaces it; audits can challenge it in place)."""
    q_text = (eff_verify or "").strip()
    if is_mechanical_verify(q_text):
        raise BacklogEditError(
            f"[{status}] refused: {row_id}'s Verify question reads as a "
            f"machine event — an agent-grade check.\n"
            f"  Per F240 (who-is-better-positioned): if the answer lives in a "
            f"file, log, or probe, the agent\n"
            f"  runs the check NOW — it never reaches the user's queue. Run "
            f"it and set [Done], or set\n"
            f"  [Waiting] naming the wake event with an agent-check plan in "
            f"the body.\n"
            f"  Question: \"{q_text[:100]}\""
        )
    has_annotation = "*why-user:" in q_text
    if not (why_user and why_user.strip()) and not has_annotation:
        raise BacklogEditError(
            f"[{status}] refused: {row_id} needs --why-user \"<one "
            f"sentence>\" naming the human faculty\n"
            f"  this check invokes (taste / preference / ratification / "
            f"passive-use observation).\n"
            f"  Per F240, a verification surfaces to the user only when "
            f"their answer is genuinely better\n"
            f"  than the agent's. If the agent can check it, run it now and "
            f"set [Done], or set [Waiting]\n"
            f"  with an agent-check plan."
        )
    if why_user and why_user.strip():
        return f"{q_text} · *why-user: {why_user.strip()}*" if q_text \
            else f"· *why-user: {why_user.strip()}*"
    return eff_verify


# --- F257 question-mint gate (the F240 sibling for Open Questions) -----------
# Keyed on the ask-format Recommendation strength instead of a verify's
# mechanical phrasing. Same three moves as verify_ownership_gate: a Tier-1
# hard-refuse (agent-territory shape, no override), a Tier-2 refuse-unless-
# justified (Lean/Strong without --why-ask), and a rendered `· *why-ask: …*`
# annotation the audit can challenge in place.
_RECOMMENDATION_STRENGTH_RE = re.compile(
    r"^\s*-\s+\*\*Recommendation:\*\*\s*(.*)$", re.MULTILINE)  # `^\s*-`: a standalone Backlog Q-row (F275) carries Recommendation as an INDENTED sub-bullet, not indent-0
# Tier-1: known agent-territory question shapes — refused regardless of
# --why-ask (ordering / batching / rollback / cosmetic rename of an existing
# thing). Deliberately NARROW (F242's lesson) so a genuine fork is never
# false-flagged; naming a NEW interface-sticky thing is NOT here (F068 keeps
# those askable).
_AGENT_TERRITORY_Q_RE = re.compile(
    r"\b(?:which\s+order|what\s+order|in\s+what\s+order|order\s+(?:should|do|to)\b"
    r"|should\s+(?:i|we)\s+batch|batch\s+(?:these|them|the\s+\w+)\s+(?:together|into)"
    r"|should\s+(?:i|we)\s+roll\s+back|roll\s+(?:it|this|these|them)\s+back"
    r"|what\s+should\s+(?:i|we)\s+(?:name|call)\s+(?:it|this|the\b)"
    r"|what\s+to\s+(?:name|call)\s+(?:it|this))\b",
    re.IGNORECASE,
)


def recommendation_strength(body):
    """Return 'Strong' | 'Lean' | 'None' parsed from the Q's indent-0
    `- **Recommendation:** …` line, or None when absent/unrecognized. The
    ask-format gate (_validate_ask_format_body) already guarantees the line
    exists on the define path; this reads its first Strong/Lean/None keyword
    (case-insensitive)."""
    m = _RECOMMENDATION_STRENGTH_RE.search(body or "")
    if not m:
        return None
    wm = re.search(r"\b(Strong|Lean|None)\b", m.group(1), re.IGNORECASE)
    return wm.group(1).capitalize() if wm else None


def has_why_ask_annotation(body):
    """True when the Q body already carries a `· *why-ask: …*` annotation —
    an already-vetted Q, grandfathered on re-touch (mirrors F240's
    `*why-user:*` short-circuit)."""
    return "*why-ask:" in (body or "")


def _q_header_line(body):
    """The Q's header line (the `**Q<n> — …**` line) minus any trailing block
    anchor — the text the Tier-1 agent-territory check runs against (title +
    elaboration live here; option/Recommendation lines are separate)."""
    for line in (body or "").splitlines():
        if re.match(r"^\s*-?\s*\*\*Q(?:\d+|\+)\s+—", line):
            return re.sub(r"\s+\^[\w-]+\s*$", "", line).strip()
    return ""


def is_agent_territory_question(body):
    """F257 Tier-1 — True when the question's shape is known agent-territory
    (ordering / batching / rollback / cosmetic rename): never the user's call,
    so refused regardless of --why-ask. Narrow by design."""
    return bool(_AGENT_TERRITORY_Q_RE.search(_q_header_line(body)))


def _append_why_ask_annotation(body, why_ask):
    """Append `· *why-ask: …*` to the Q's Recommendation line (the field the
    justification qualifies); falls back to the header line if no
    Recommendation line is present."""
    annot = f" · *why-ask: {why_ask}*"
    lines = str(body or "").splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^\s*-\s+\*\*Recommendation:\*\*", line):  # `^\s*-`: F275 Q-rows indent the Recommendation
            lines[i] = line.rstrip() + annot
            return "\n".join(lines)
    for i, line in enumerate(lines):
        if re.match(r"^\s*-?\s*\*\*Q(?:\d+|\+)\s+—", line):
            m = re.search(r"\s+\^[\w-]+\s*$", line)
            if m:
                lines[i] = line[:m.start()] + annot + line[m.start():]
            else:
                lines[i] = line.rstrip() + annot
            return "\n".join(lines)
    return (body or "").rstrip() + annot


def question_mint_gate(q_num, body, why_ask):
    """F257 — enforce who-should-decide at the moment an Open Question is
    minted (the F240 sibling). Two refusals mirroring verify_ownership_gate:

      Tier 1 (hard, no override): the question's shape is agent-territory
        (ordering / batching / rollback / cosmetic rename) — refused
        regardless of --why-ask (the `is_mechanical_verify` analog).
      Tier 2 (refuse-unless-justified): a Lean/Strong recommendation with no
        --why-ask and no existing `*why-ask:*` annotation — a recommendation
        means the agent can decide (F068), so surfacing it must be justified
        (the `--why-user` analog).

    Passes: Recommendation None (the honest ask, never blocked); an already
    `*why-ask:*`-annotated Q (grandfathered re-touch). Returns the body with
    the `· *why-ask: …*` annotation appended when --why-ask is supplied."""
    label = f"Q{q_num}" if q_num is not None else "Q+"
    if is_agent_territory_question(body):
        raise BacklogEditError(
            f"[{label}] refused: the question is agent-territory (ordering / "
            f"batching / rollback / cosmetic\n"
            f"  rename) — never the user's call (F068 / "
            f"feedback_low_stakes_ordering_auto_decide /\n"
            f"  feedback_agent_picks_order). Pick a sensible option, announce "
            f"it, and proceed. No\n"
            f"  --why-ask overrides this."
        )
    if has_why_ask_annotation(body):
        return body  # already vetted — grandfathered re-touch
    strength = recommendation_strength(body)
    if strength in ("Lean", "Strong") and not (why_ask and why_ask.strip()):
        raise BacklogEditError(
            f"[{label}] refused: carries a {strength} recommendation but no "
            f"--why-ask.\n"
            f"  Per F068, a recommendation means you can likely decide:\n"
            f"    • low-stakes + reversible → assume-and-announce\n"
            f"    • ordering / batching / rollback → you pick (never ask)\n"
            f"    • answer is in your analysis / the rules / prior chat → "
            f"answer it\n"
            f"    • mechanically checkable → verify it (F240)\n"
            f"  If it is genuinely high-stakes-irreversible despite your lean "
            f"— an irreversible external\n"
            f"  action, an interface-sticky name/schema, an architecture "
            f"lock-in, or a taste/preference\n"
            f"  only the user holds — pass --why-ask \"<one sentence>\". "
            f"Otherwise decide and announce."
        )
    if why_ask and why_ask.strip():
        return _append_why_ask_annotation(body, why_ask.strip())
    return body


# --- F270 Damage field — the downside gate as a closed enumeration -----------
# Every minted question self-declares one damage category (the first word of a
# `- **Damage:**` line). waste/priority auto-resolve (the state script resolves
# them to the agent's lean and never surfaces them); the rest surface. This is
# the F257 why-ask gate's structured successor — the category, not the agent's
# prose, decides surface-vs-auto.
DAMAGE_CATEGORIES = ("waste", "priority", "irreversible", "locking", "taste", "other")
DAMAGE_AUTO_RESOLVE = ("waste", "priority")  # never reach the user
_DAMAGE_LINE_RE = re.compile(r"^\s*-\s+\*\*Damage:\*\*\s*([A-Za-z]+)\b(.*)$", re.MULTILINE)  # `^\s*-`: F275 Q-rows indent the Damage line as a sub-bullet


def parse_damage(body):
    """F270 — parse `- **Damage:** <category> — <narrative>` from a Q body.
    Returns (category|None, narrative). `category` is the lowercased first word,
    or None when no Damage line is present (the caller warns — a soft-required
    rollout, so a legacy caller is never hard-broken). Raises when a Damage line
    IS present but its first word is not a known category — a typo must not
    silently pass as an askable question."""
    m = _DAMAGE_LINE_RE.search(body or "")
    if not m:
        return None, ""
    category = m.group(1).lower()
    narrative = m.group(2).strip(" —–-.:")
    if category not in DAMAGE_CATEGORIES:
        raise BacklogEditError(
            f"refused: damage category {category!r} is not one of "
            f"{{{', '.join(DAMAGE_CATEGORIES)}}} — the first word of the "
            "`- **Damage:**` line is the category (a single word so it parses). "
            "See [[DAS ask-format]] § The Damage field."
        )
    return category, narrative


def leaned_choice(body):
    """The option label the agent leans toward, used to auto-resolve a
    waste/priority Q: the `(X)` in the `- **Recommendation:**` line, else the
    first labeled option `- **(X)**`, else '—' (open-ended, no options)."""
    m = _RECOMMENDATION_STRENGTH_RE.search(body or "")
    if m:
        cm = re.search(r"\(([A-Za-z]\w*)\)", m.group(1))
        if cm:
            return f"({cm.group(1)})"
    om = re.search(r"^\s*-\s+\*\*\(([A-Za-z]\w*)\)\*\*", body or "", re.MULTILINE)
    if om:
        return f"({om.group(1)})"
    return "—"


# --- F259 user-action ownership gate (the F240 sibling for [User]) -----------
# [User] parks work on a genuinely user-only ACTION (a credential only the user
# holds, a GUI permission dialog, a 2FA device, a session-gated login). The
# gate mirrors verify_ownership_gate's --why-user move: it requires a
# --why-user-action justification naming the human faculty / credential that
# makes the action user-only. The requirement to ARTICULATE why the agent can't
# do it is the filter against lazy delegation. (No mechanical Tier-1 analog —
# there is no reliable phrasing heuristic for "the agent could do this"; the
# articulation requirement carries the whole load.)
def _status_needs_user(status):
    return (status or "").strip() == "User"


def user_action_gate(status, row_id, eff_user, why_user_action):
    """F259 — enforce genuine user-only-ness when a row ENTERS [User] or its
    `- **User:**` action is (re)written; a re-touch that keeps the action is
    grandfathered (vetted at entry). Refuses a missing --why-user-action (and
    no existing `*why-user-action:*` annotation). Returns the effective
    user-action text with the annotation appended."""
    a_text = (eff_user or "").strip()
    has_annotation = "*why-user-action:" in a_text
    if not (why_user_action and why_user_action.strip()) and not has_annotation:
        raise BacklogEditError(
            f"[{status}] refused: {row_id} needs --why-user-action \"<one "
            f"sentence>\" naming the\n"
            f"  credential or human-only faculty this action requires (a login "
            f"only you hold, a GUI\n"
            f"  permission dialog, a 2FA device, a physical device). Per F259, "
            f"[User] is honest only when\n"
            f"  the agent genuinely cannot do it — even via box / osascript / "
            f"bridge. If the agent CAN do\n"
            f"  it, this is [Ready] with a `- **Next:**`, not [User]."
        )
    if why_user_action and why_user_action.strip():
        return f"{a_text} · *why-user-action: {why_user_action.strip()}*" \
            if a_text else f"· *why-user-action: {why_user_action.strip()}*"
    return eff_user


# --- F242 non-answer (punt) detector -----------------------------------------
# A required Next/question value is a "non-answer" when the agent left the field
# empty or filled it with a placeholder instead of doing the groom. v1 set,
# deliberately narrow so a real Next like "Remove the none-check in X" is safe.
_NONANSWER_WHOLE = frozenset({"?", "-", "—", "(none)"})
_NONANSWER_LEADING = (
    "there is no next action", "no next action", "no next step", "none declared",
    "n/a", "na", "tbd", "todo", "none", "pending", "unknown",
)


def is_nonanswer(text):
    """F242 — True when `text` is a non-answer placeholder: empty; contains the
    ⚠ glyph (U+26A0) anywhere (the render's own 'not really Ready' marker echoed
    back); a whole-value sentinel (?, -, —, (none)); or begins with a non-answer
    phrase on a word boundary (so 'none' matches 'none' / 'N/A — blocked' but not
    'nonexistent' / 'none-check'). Whole-value/leading only — never substring."""
    if text is None:
        return True
    raw = text.strip()
    if not raw:
        return True
    if "⚠" in raw:
        return True
    norm = raw.strip("*`_ ").strip()
    if not norm:
        return True
    low = norm.lower()
    if low in _NONANSWER_WHOLE:
        return True
    for phrase in _NONANSWER_LEADING:
        if low == phrase:
            return True
        if low.startswith(phrase):
            nxt = low[len(phrase)]
            if not (nxt.isalnum() or nxt in "-_"):
                return True
    return False


def next_answer_gate(status, row_id, eff_next):
    """F242 — refuse a [Ready]/[Active]/[Agreed] row whose `- **Next:**` value
    is a non-answer placeholder. Empty-Next is already refused by the F171
    needs-next check; this catches a field filled with a sentinel to slip past
    it (the agent punting the groom instead of doing it)."""
    if not _status_needs_next(status):
        return
    val = (eff_next or "").strip()
    if not val or not is_nonanswer(val):
        return
    raise BacklogEditError(
        f"[{status}] refused: {row_id}'s Next is a non-answer "
        f"(\"{val[:60]}\").\n"
        f"  Per F242 (mechanical groom gate): a [Ready] row must carry the "
        f"concrete first step the\n"
        f"  agent takes with zero user involvement — not a placeholder. Write "
        f"that step, or rebracket\n"
        f"  honestly: [Questions] if it needs the user, [Blocked]/[Waiting] if "
        f"it is blocked."
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
    # The row's OWN doc is the arrow-form `→ [[F<n> — …]]` reference (last one
    # wins), never an in-prose mention of some other doc — the same
    # arrow-preferred rule verify_questions_constraint adopted after the
    # B-roots-reconcile failure (2026-06-02); F102 had kept first-link and so
    # wrongly bound a T-row's status to a doc it merely referenced (2026-07-06).
    arrow_links = list(re.finditer(r"→\s+(\[\[[^\]]+\]\])", body))
    m = WIKI_LINK_RE.search(arrow_links[-1].group(1)) if arrow_links else None
    if not m:
        sys.stderr.write(
            f"note: [{status}] body has no `→ [[…]]` doc reference — "
            f"skipping `## Status` block check (F102).\n"
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

# Optional `<ANCHOR>-` prefix (e.g. `DMUX-F034`) for cross-anchor rows migrated
# into another anchor's backlog that keep their origin id so wiki-links resolve.
# 2+ uppercase letters + dash, so it never collides with the single-letter F/B.
# Row-id kinds: F (feature) / T (backlog task) / C (OpenSpec change, F230) /
# Q (standalone feature-less question, F275 M2) / B (legacy backlog item) — all
# minted as monotonic numbers; R (roadmap task) — a name-path handle
# `R-<Name>.<path>` (dots allowed), never a minted counter.
ROW_ID_RE = re.compile(r"^(?:([A-Z]{2,})-)?(F|B|T|R|C|Q)(new|\d+|-[A-Za-z0-9][\w\-.]*)$")


def parse_row_id(arg):
    """Return ('F'|'B'|'T'|'<PREFIX>-F'|..., literal-rest-or-None).

    'Fnew' / 'Tnew' / 'Bnew'  → (kind, None)     — mint a new number
    'F015'                    → ('F', '015')
    'T007'                    → ('T', '007')
    'B7'                      → ('B', '7')
    'B-mode-walkup'           → ('B', '-mode-walkup')     — kebab B-row id
    'R-Scaffolding.5.2'       → ('R', '-Scaffolding.5.2')  — roadmap-task name-path
    'DMUX-F034'               → ('DMUX-F', '034')          — cross-anchor migrated row;
                       the prefix is folded into `kind` so f"{kind}{rest}"
                       reconstructs the full id.
    """
    m = ROW_ID_RE.match(arg)
    if not m:
        raise BacklogEditError(
            f"invalid row-id '{arg}' "
            "(expected F<NNN>, T<NNN>, B<n>, B-<slug>, R-<Name>.<path>, "
            "<ANCHOR>-F<NNN>, Fnew, Tnew, or Bnew)"
        )
    prefix, kind, rest = m.group(1), m.group(2), m.group(3)
    if rest == "new":
        if prefix:
            raise BacklogEditError(f"cannot mint a prefixed row-id '{arg}'")
        return (kind, None)
    if prefix:
        return (f"{prefix}-{kind}", rest)
    return (kind, rest)


def format_row_id(kind, rest_or_num):
    """For mint: pad F/T/C/Q to 3 digits; others (B) stay as-is. R is never minted
    here — its handle is a name-path formed by the caller."""
    if kind in ("F", "T", "C", "Q"):
        if isinstance(rest_or_num, int):
            return f"{kind}{rest_or_num:03d}"
        return f"{kind}{rest_or_num}"
    return f"{kind}{rest_or_num}"


# --------------------------------------------------------------------------
# Backlog scanning

ROW_HEADER_RE = re.compile(
    r"^(\s*)-\s+\*\*((?:[A-Z]{2,}-)?F\d+|T\d+|C\d+(?=\s+—)|Q\d+(?=\s+—)|R-[A-Za-z0-9][\w\-.]*|B[\w\-]+|B\d+)\b"
)
H2_RE = re.compile(r"^##\s+(.+?)\s*$")

# Used to parse the existing row line back into title + body so the script
# can preserve them across status-only edits.
ROW_FULL_RE = re.compile(
    r"^-\s+\*\*(?P<rid>(?:[A-Z]{2,}-)?F\d+|T\d+|C\d+(?=\s+—)|Q\d+(?=\s+—)|R-[A-Za-z0-9][\w\-.]*|B[\w\-]+|B\d+)"
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
    # F250 #1 — never render the literal `[same]` sentinel. It reaches here only
    # via a bug (e.g. a cross-file insert that failed to resolve `same` against
    # the source row); writing `[same]` silently clobbers the real status.
    if (status or "").strip() == "same":
        raise BacklogEditError(
            f"internal: render_row({row_id}) called with the literal 'same' "
            f"status — the caller must resolve 'same' to the existing bracket "
            f"before rendering (refusing to write '[same]')."
        )
    title = (title or "").strip()
    body = (body or "").strip()
    title_block = f"**{row_id} — {title}**" if title else f"**{row_id}**"
    bracket = f"[{status}]"
    suffix = f" — {body}" if body else ""
    # Obsidian block-ids (`^id`) allow only [\w-]; R roadmap-task handles carry
    # dots (`R-Scaffolding.5.2`), so sanitize dots→dashes for the anchor while the
    # visible handle keeps its dotted form. No-op for F/T/B ids.
    anchor = re.sub(r"[^\w\-]", "-", row_id)
    return f"- {title_block} {bracket}{suffix} ^{anchor}\n"


# --------------------------------------------------------------------------
# Verify:/Next: companion sub-bullets (per the 2026-07-02 F171 incident): a
# [Verify*]/[Watching*] bracket is only half-set until its `- **Verify:**`
# yes/no question exists; [Ready]/[Active]/[Agreed] needs a `- **Next:**`
# no-user action. Setting the bracket and writing its question is ONE atomic
# act — the render marks a missing one `⚠` and audit-q C41 flags it.

SUBBULLET_RE_TMPL = r"^\s+-\s+\*\*{label}(?:\s*\([^)]*\))?:\*\*\s*(.+?)\s*$"


def _status_needs_verify(status):
    s = (status or "").strip()
    return s.startswith("Watching") or (
        s.startswith("Verify") and not s.startswith("Verify-by")
    )


def _status_needs_next(status):
    return (status or "").strip() in ("Ready", "Active", "Agreed")


def _extract_subbullet_text(span_lines, label):
    """Text of the first `- **<label>:**` sub-bullet in span_lines, or None."""
    rx = re.compile(SUBBULLET_RE_TMPL.format(label=label))
    for line in span_lines:
        m = rx.match(line)
        if m:
            return m.group(1).strip()
    return None


def _ensure_subbullet(lines, row_id, label, text):
    """Mutate `lines` in place: under row_id's line, drop any existing
    `- **<label>:**` sub-bullet and insert `  - **<label>:** <text>` directly
    after the row line (so it survives horizon-moves, which drop the span)."""
    rx = re.compile(SUBBULLET_RE_TMPL.format(label=label))
    row_i = None
    for i, line in enumerate(lines):
        rm = ROW_HEADER_RE.match(line)
        if rm and len(rm.group(1)) == 0 and rm.group(2) == row_id:
            row_i = i
            break
    if row_i is None:
        return
    end = len(lines)
    for j in range(row_i + 1, len(lines)):
        if H2_RE.match(lines[j].rstrip()):
            end = j
            break
        rm = ROW_HEADER_RE.match(lines[j])
        if rm and len(rm.group(1)) == 0:
            end = j
            break
    keep = [lines[row_i]]
    keep.extend(l for l in lines[row_i + 1:end] if not rx.match(l))
    keep.insert(1, f"  - **{label}:** {text}\n")
    lines[row_i:end] = keep


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
    verify_text=None,
    next_text=None,
    pending_subs=None,
    why_user=None,
    user_text=None,
    why_user_action=None,
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

    # F171 companion-sub-bullet discipline: capture any existing Verify:/Next:
    # sub-bullet text so it survives a horizon-move (which drops the row span),
    # and so a same-status re-touch isn't forced to re-supply it.
    existing_verify = existing_next = existing_user = None
    if existing is not None:
        _es, _ee = existing[0], existing[1]
        _span = lines[_es:_ee]
        existing_verify = _extract_subbullet_text(_span, "Verify")
        existing_next = _extract_subbullet_text(_span, "Next")
        existing_user = _extract_subbullet_text(_span, "User")

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
        _selffire(backlog_path)
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
    # `backlog-edit.py {slug} same <row> <status> "" "<new body>"` work
    # without blowing away the title.
    existing_status_for_check = ""
    if existing is not None:
        # F250 #4 — the row's header is recognized (it's in row_index via
        # ROW_HEADER_RE) but if the FULL line can't be parsed (ROW_FULL_RE) —
        # e.g. an en-dash instead of em-dash, or a missing `[status]` bracket —
        # the old code fell through to parse_existing_row's ("","") and treated
        # it as a FRESH row: title/body were wiped and the literal `[same]`
        # bracket written. Refuse instead, so a malformed row is fixed by hand
        # rather than silently destroyed. (The `delete` verb above already ran,
        # so a malformed row can still be deleted.)
        if not ROW_FULL_RE.match(lines[existing[0]]):
            raise BacklogEditError(
                f"{row_id} is malformed (recognized as a row but the full line "
                f"can't be parsed — check for an en-dash vs em-dash or a missing "
                f"[status] bracket) — refusing to edit and wipe its content. Fix "
                f"the row by hand or re-`define` it."
            )
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
        # real status (e.g. a body-only `state Backlog set` losing [Designing]).
        if status == "same" and existing_status_for_check:
            status = existing_status_for_check

    # Constraint check — the Questions promise. Refuse the write if the
    # status asserts [Questions] but the body's wiki-link target has no
    # Q<n> markers. Runs AFTER the preserve-on-omit resolution so the
    # final body is what we verify. The check-body includes the existing
    # row's sub-bullets: a T-/B-row's inline `- **Q<n> —` sub-bullets are a
    # sanctioned Q home (R-backlog-05), and parse_existing_row only sees the
    # opening line — without this, a bracket-only update on such a row
    # wrongly failed its own promise.
    body_for_check = body
    if existing is not None:
        j = existing[0] + 1
        while j < len(lines) and re.match(r"^\s+- ", lines[j]):
            body_for_check += "\n" + lines[j]
            j += 1
    # A v2 `define` carries its sub-bullets separately (attached after this
    # edit lands) — include them here so a new T-/B-row's inline Q<n>
    # sub-bullets can honor a [Questions] promise the same way an existing
    # row's do.
    if pending_subs:
        body_for_check += "\n" + "\n".join(pending_subs)
    verify_questions_constraint(status, body_for_check, row_id=row_id_arg)

    # F096 — refuse [Verify*] when body describes pending implementation
    # work (Phase 2, remaining, follow-up, etc.). Addresses the F094 lie
    # where the row claimed Verify-by but hid ~50 anchors of work.
    verify_no_implementation_in_verify(status, body)

    # F102 — refuse any status transition where the linked feature doc's
    # `## Status` H2 does not match the about-to-set status. Subsumes F098
    # (the Done case is now a special case of the broader Status discipline).
    # Grandfathers re-touch of same-status rows.
    verify_status_block(status, body, existing_status_for_check)

    # F171 companion-sub-bullet enforcement + resolution. A [Verify*]/[Watching*]
    # row must carry a `- **Verify:**` yes/no question; a [Ready]/[Active]/
    # [Agreed] row a `- **Next:**` no-user action. The provided flag wins; else
    # preserve the existing sub-bullet; else — for a status that needs one —
    # REFUSE (the render would show `⚠`, and audit-q C41 would flag it).
    eff_verify = verify_text if verify_text is not None else existing_verify
    eff_next = next_text if next_text is not None else existing_next
    eff_user = user_text if user_text is not None else existing_user
    if status not in ("same", "delete"):
        if _status_needs_verify(status) and not (eff_verify and eff_verify.strip()):
            raise BacklogEditError(
                f"[{status}] refused: {row_id} needs a concrete yes/no question. "
                f"Pass --verify \"<question>\" (e.g. \"Since <date>, has <bad thing> "
                f"recurred? no = held\"). Setting a Watching/Verify bracket without "
                f"its `- **Verify:**` sub-bullet renders `⚠ no concrete question` "
                f"and is flagged by audit-q C41. If there is genuinely no user "
                f"check, promote to [Done] or rebracket to [Blocked]/[Waiting]."
            )
        if _status_needs_next(status) and not (eff_next and eff_next.strip()):
            raise BacklogEditError(
                f"[{status}] refused: {row_id} needs a no-user next action. "
                f"Pass --next \"<action>\". Setting a Ready/Active bracket without "
                f"its `- **Next:**` sub-bullet renders `⚠ none declared — not really "
                f"Ready` and is flagged by audit-q C41. If the next step needs the "
                f"user, rebracket ([Verify] for a user check, [Blocked]/[Questions] "
                f"for a decision)."
            )
        if _status_needs_user(status) and not (eff_user and eff_user.strip()):
            raise BacklogEditError(
                f"[{status}] refused: {row_id} needs a `- **User:**` action. "
                f"Pass --user \"<action>\" naming exactly what YOU (the user) must "
                f"do (e.g. \"Log into Hoare at <url> so the sync token refreshes\"). "
                f"A [User] bracket without its `- **User:**` sub-bullet renders `⚠` "
                f"and is flagged by audit-q C51. If the action is something the "
                f"agent can do, use [Ready] with a `- **Next:**` instead."
            )

    # F240 — verification ownership gate. Fires when the row ENTERS the
    # Verify/Verify-by/Watching family or its question is (re)written; a
    # same-family re-touch keeps the vetting it got at entry.
    if status not in ("same", "delete") and _verify_family(status):
        entering = not _verify_family(existing_status_for_check)
        if entering or verify_text is not None or (why_user and why_user.strip()):
            eff_verify = verify_ownership_gate(
                status, row_id, eff_verify, why_user
            )

    # F259 — user-action ownership gate. Fires when the row ENTERS [User] or
    # its `- **User:**` action is (re)written; a same-status re-touch keeps the
    # vetting it got at entry.
    if status not in ("same", "delete") and _status_needs_user(status):
        entering_user = (existing_status_for_check or "").strip() != "User"
        if entering_user or user_text is not None or (
                why_user_action and why_user_action.strip()):
            eff_user = user_action_gate(
                status, row_id, eff_user, why_user_action
            )

    # F242 — mechanical groom gate: a Ready/Active/Agreed row's Next must be a
    # real first step, not a non-answer placeholder (empty is caught above).
    if status not in ("same", "delete"):
        next_answer_gate(status, row_id, eff_next)

    # Build the new line.
    new_line = render_row(row_id, status, title, body)

    if existing is not None:
        start, end, existing_h2, _ = existing
        if existing_h2 == h2_name:
            # In-place replacement: swap the first line, keep any sub-bullets.
            # EXCEPT a v2 `define` on an existing row (pending_subs present) is a
            # create-or-REPLACE — drop the old sub-bullet span so the new subs
            # replace it instead of duplicating (F250 #7). The F171 companion +
            # pending_subs blocks below re-attach the fresh subs by row-id.
            if pending_subs:
                del lines[start:end]
                lines.insert(start, new_line)
            else:
                lines[start] = new_line
        else:
            # Remove old span, then insert new in destination H2. Carry the
            # row's sub-bullet block through the move — re-inserting only the
            # opening line silently dropped inline Qs / plan sub-bullets
            # (found 2026-07-06: a horizon move erased a T-row's Q1, and the
            # follow-on audit-fix then rebracketed the now-Qless row).
            # A `define` that also moves horizon (pending_subs present) is a
            # replace — drop the old subs; the new ones ride via pending_subs.
            sub_block = [] if pending_subs else [
                sl for sl in lines[start + 1:end] if sl.strip() != ""
            ]
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
            for k, sl in enumerate(sub_block, start=1):
                lines.insert(insert_at + k, sl)
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

    # F171 — (re)attach the companion sub-bullet under the just-placed row, so it
    # survives horizon-moves (which delete the old span) and same-status re-touch.
    if status not in ("same", "delete"):
        # _verify_family (not _status_needs_verify) so a [Verify-by] row's
        # question / F240 why-user annotation lands too instead of being
        # silently dropped.
        if _verify_family(status) and eff_verify:
            _ensure_subbullet(lines, row_id, "Verify", eff_verify.strip())
        elif _status_needs_next(status) and eff_next:
            _ensure_subbullet(lines, row_id, "Next", eff_next.strip())
        elif _status_needs_user(status):
            if eff_user:
                _ensure_subbullet(lines, row_id, "User", eff_user.strip())
            # A [User] row MAY carry a queued `- **Next:**` — the agent's step
            # once the user acts (documentary, not executable-now; F259).
            if eff_next and eff_next.strip():
                _ensure_subbullet(lines, row_id, "Next", eff_next.strip())
        elif next_text is not None and next_text.strip():
            # T056 — a status that doesn't REQUIRE a Next ([Blocked], [Waiting],
            # [Questions], …) may still be handed one explicitly, and a parked
            # row is exactly where the note explaining how to restart it earns
            # its keep. Before this branch the value was computed into eff_next
            # and then dropped on the floor while the command still printed
            # "updated" — a silent discard the caller had no way to notice.
            # Gated on `next_text`, not `eff_next`, so an ordinary re-touch does
            # not rewrite (and reorder) a sub-bullet nobody asked to change.
            _ensure_subbullet(lines, row_id, "Next", next_text.strip())

    # v2 `define` sub-bullets land in the SAME edit, before the post-edit
    # refresh_q_md — attaching them afterwards let audit-q's C24 --fix see a
    # [Questions] row with zero Qs on disk and rebracket it to [Ready] before
    # its inline Qs existed (bit T010, 2026-07-13).
    if pending_subs and status != "delete":
        for idx, ln in enumerate(lines):
            if re.match(rf"^- \*\*{re.escape(row_id)}\b", ln):
                j = idx + 1
                while j < len(lines) and re.match(r"^\s+- ", lines[j]):
                    j += 1
                for k, sl in enumerate(pending_subs):
                    sl = sl if sl.startswith(" ") else "  " + sl
                    lines.insert(j + k, sl if sl.endswith("\n") else sl + "\n")
                break

    backlog_path.write_text("".join(lines))
    _selffire(backlog_path)

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
        _selffire(messages_path)
    with messages_path.open("a") as f:
        f.write(line)


def write_state(slug, result):
    """Persist the last-invocation timestamp + details for /audit integrity.

    State lives at ~/.config/anchor-system/backlog-edit/state.json. Each anchor
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

    Per [[DAS Backlog]] § Icebox interaction: 'F-number namespace is shared
    across backlog AND icebox — no F-number collisions; an item moving
    between the two keeps its F-number.' Same for B-numbers.
    """
    # F250 #3 — recognize rows via scan_backlog (ROW_HEADER_RE), which sees
    # TITLE-LESS rows (`- **T002** [Done]`) as well as titled ones. The old
    # em-dash-anchored regex (`\*\*{kind}(\d+)\s+—`) skipped title-less rows, so
    # the max-scan could return an already-in-use number and `define`'s
    # create-or-replace would then OVERWRITE that live row. Aligns the mint with
    # next_id_for_kind / ROW_HEADER_RE.
    id_re = re.compile(rf"^{kind}(\d+)$")
    highest = 0
    for path in (backlog_path, icebox_path):
        if path is None or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        _lines, _h2, row_index = scan_backlog(text)
        for rid in row_index:
            m = id_re.match(rid)
            if m:
                highest = max(highest, int(m.group(1)))
    return highest + 1


def read_full_row(path, row_id_arg):
    """F250 #1/#4 — read an existing row's FULL content before a cross-file move.

    A cross-file horizon move (Backlog↔Icebox) deletes the row from the source
    and re-inserts it into the destination. Historically the destination insert
    received only the caller's explicit args, so a bare `set --horizon Icebox`
    (no --title/--body) rebuilt the row from nothing — title, body, real status,
    and sub-bullets were all lost and the literal `[same]` bracket was written
    (F250 #1). This helper lets the orchestrator read the source row first and
    carry its content across.

    Returns a dict {title, body, status, verify, next, other_subs} for the row,
    or None if the row is not in this file. Raises BacklogEditError if the row's
    header IS present (ROW_HEADER_RE) but the full line can't be parsed
    (ROW_FULL_RE) — refusing to move a malformed row rather than silently wiping
    it (F250 #4).
    """
    kind, rest = parse_row_id(row_id_arg)
    if rest is None:
        return None
    row_id = f"{kind}{rest}"
    lines, _h2, row_index = scan_backlog(path.read_text())
    existing = row_index.get(row_id)
    if existing is None:
        return None
    start, end, _h2name, _indent = existing
    m = ROW_FULL_RE.match(lines[start])
    if not m:
        raise BacklogEditError(
            f"{row_id} in {path.name} is malformed (recognized as a row but the "
            f"full line can't be parsed) — refusing to move it and lose its "
            f"content. Fix the row by hand or re-`define` it."
        )
    span = lines[start + 1:end]
    verify_rx = re.compile(SUBBULLET_RE_TMPL.format(label="Verify"))
    next_rx = re.compile(SUBBULLET_RE_TMPL.format(label="Next"))
    user_rx = re.compile(SUBBULLET_RE_TMPL.format(label="User"))
    other_subs = [
        sl for sl in span
        if sl.strip() != "" and not verify_rx.match(sl)
        and not next_rx.match(sl) and not user_rx.match(sl)
    ]
    return {
        "title": m.group("title") or "",
        "body": m.group("body") or "",
        "status": m.group("status") or "",
        "verify": _extract_subbullet_text(span, "Verify"),
        "next": _extract_subbullet_text(span, "Next"),
        "user": _extract_subbullet_text(span, "User"),
        "other_subs": other_subs,
    }


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


def open_questions_is_empty(lines, h2_start, h2_end):
    """Does the ## Open Questions block still hold anything pending?

    Only two things count as content: a pending `- **Q<n>` header bullet, and a
    `### ` holding pen. Everything else — the integrity stamp, blank lines, and
    any leftover placeholder prose — is not a pending question.

    The old test asked "is there any non-blank line", so a single stale
    placeholder line kept the block alive forever: Phase 2 never fired, audit-q
    C21 flagged the empty H2, groom-list counted it, the stop-gate blocked on it,
    and no sanctioned verb could clear it — an anchor stuck in a groomed state it
    could not leave (T042).
    """
    for k in range(h2_start + 1, h2_end):
        line = lines[k]
        if line.startswith("### "):
            return False
        if _Q_HEADER_BULLET_RE.match(line):
            return False
    return True


def drop_open_questions_if_empty(lines):
    """Phase 2 — retire a spent ## Open Questions block. Idempotent.

    Removes ONLY the block itself: `_find_h2` ends at the next H2, so a resolved
    archive living further down the doc is never in the removed span.
    """
    oq = _find_h2(lines, "Open Questions")
    if oq is None:
        return lines, False
    oq_start, oq_end = oq
    if not open_questions_is_empty(lines, oq_start, oq_end):
        return lines, False
    drop_end = oq_end
    while drop_end < len(lines) and not lines[drop_end].strip():
        drop_end += 1
    if drop_end < len(lines):
        return lines[:oq_start] + lines[drop_end:], True
    return lines[:oq_start], True


def replace_q_bullet(lines, start, end, new_bullet_lines):
    """Splice a rewritten Q bullet over [start, end), keeping the separator.

    `end` from _find_q_bullet points at the NEXT Q-header / heading, so the span
    swallows the blank line between this Q and the next. The replacement bullet
    carries no trailing blank, so a naive splice deletes that separator and
    audit-q C20 fires on every redefine of a non-terminal Q (T038). Carrying the
    original blank run across keeps spacing stable under repeated rewrites.
    """
    trailing = 0
    while end - trailing - 1 > start and not lines[end - trailing - 1].strip():
        trailing += 1
    return lines[:start] + list(new_bullet_lines) + [""] * trailing + lines[end:]


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
    """Ensure ## Open Questions H2 exists — the FIRST H2 below the H1, after
    the H1's orientation prose (per F241, 2026-07-15; supersedes the
    2026-06-29 above-the-H1 rule: same prominence, structurally normal file).
    Returns lines (possibly modified) AND the (h2_start, h2_end) content
    range after insertion.
    """
    existing = _find_h2(lines, "Open Questions")
    if existing is not None:
        return lines, existing
    # Find the H1, then the first H2 after it — the block inserts there so it
    # is the file's first H2.
    h1_idx = None
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            h1_idx = i
            break
    if h1_idx is None:
        raise BacklogEditError("feature doc has no H1; cannot insert ## Open Questions")
    insert_at = len(lines)
    for j in range(h1_idx + 1, len(lines)):
        if lines[j].startswith("## "):
            insert_at = j
            break
    if insert_at == len(lines) and lines and lines[-1].strip():
        lines = lines + [""]
        insert_at = len(lines)
    new_block = ["## Open Questions", "", ""]
    lines = lines[:insert_at] + new_block + lines[insert_at:]
    return lines, (insert_at + 1, insert_at + 3)


# --- F241 — Open Questions integrity stamp ---------------------------------
#
# Every script write of a managed `## Open Questions` block re-stamps it with
# a 2-char base-36 hash stored as an HTML comment on the line under the
# heading: `<!-- state:q 7k -->` (invisible in Obsidian reading view / GitHub
# render). A hand-edit inside the block breaks the stamp; the on-write check
# + audit-q drift check then route the agent back through `state`. Stampless
# legacy blocks are grandfathered (no stamp → no warning). Recovery:
# `state <doc> revalidate` (validate-then-stamp, never bless-blind).

_Q_STAMP_RE = re.compile(r"^<!--\s*state:q\s+([0-9a-z]{2})\s*-->$")
_BASE36 = "0123456789abcdefghijklmnopqrstuvwxyz"


def _open_questions_range(lines):
    """(heading_idx, end_exclusive) of the ## Open Questions block, clamped
    to the H1 when the block sits above it (legacy placement); None if the
    doc has no block. Hash scope per F241: heading through the next H2."""
    found = _find_h2(lines, "Open Questions")
    if found is None:
        return None
    start, end = found
    for k in range(start + 1, end):
        if lines[k].startswith("# ") and not lines[k].startswith("## "):
            end = k
            break
    return start, end


def compute_q_stamp(lines, start, end):
    """2-char base-36 stamp of the block text lines[start:end] — heading
    included, stamp line excluded, trailing whitespace normalized."""
    import hashlib
    content = [ln.rstrip() for ln in lines[start:end]
               if not _Q_STAMP_RE.match(ln.strip())]
    digest = hashlib.sha1("\n".join(content).encode("utf-8")).hexdigest()
    n = int(digest, 16) % (36 * 36)
    return _BASE36[n // 36] + _BASE36[n % 36]


def read_q_stamp(lines, start, end):
    """The stored stamp value in lines[start:end], or None if unstamped."""
    for k in range(start + 1, end):
        m = _Q_STAMP_RE.match(lines[k].strip())
        if m:
            return m.group(1)
    return None


def restamp_open_questions(lines):
    """Insert-or-update the integrity stamp on the line under the
    ## Open Questions heading. No block → lines returned unchanged. Call
    this LAST, immediately before writing the doc."""
    rng = _open_questions_range(lines)
    if rng is None:
        return lines
    start, end = rng
    stamp_line = f"<!-- state:q {compute_q_stamp(lines, start, end)} -->"
    for k in range(start + 1, end):
        if _Q_STAMP_RE.match(lines[k].strip()):
            lines = lines[:k] + [stamp_line] + lines[k + 1:]
            return lines
    return lines[:start + 1] + [stamp_line] + lines[start + 1:]


# --- F247 — Backlog integrity stamp + self-heal ----------------------------
#
# Mirrors the F241 Open-Questions stamp, but covers the backlog's state-bearing
# body so a raw hand-edit (bracket flip / row move made outside `state`) is
# detected and healed. The stamp is a 2-char base-36 hash over the backlog body
# (H1 through EOF, the stamp line itself excluded), stored on the line under the
# H1 as `<!-- state:backlog XX -->` (invisible in Obsidian / GitHub render).
#
# Difference from the C48 Open-Questions check (flag-only): the backlog banner
# is a *deterministic* function of the backlog, so a mismatch is HEALED, not
# merely flagged — `heal_backlog_if_stale` runs the idempotent `refresh_q_md`
# re-derivation (banner + Q.md) and re-stamps. It complains only on a genuine
# stored-stamp mismatch (a real hand-edit); an unstamped backlog is
# grandfathered — healed + stamped silently on first sight, no accusation.
# The heal never reverts the edit (the hand-edit may be legitimate work); it
# only re-derives the downstream views so they can never stay one-link stale.

_BACKLOG_STAMP_RE = re.compile(r"^<!--\s*state:backlog\s+([0-9a-z]{2})\s*-->$")


def _backlog_stamp_range(lines):
    """(h1_idx, end_exclusive=len) — the H1 line through EOF; None if the file
    has no H1. `lines` are keepends=True (the backlog's native format). The
    whole body after the H1 is state-bearing: row brackets across every horizon
    feed the banner counts, so any of them changing must invalidate the stamp."""
    for i, ln in enumerate(lines):
        s = ln.lstrip()
        if s.startswith("# ") and not s.startswith("## "):
            return i, len(lines)
    return None


def compute_backlog_stamp(lines, start, end):
    """2-char base-36 stamp of lines[start:end] — H1 included, stamp line
    excluded, trailing whitespace normalized. Same hash shape as
    compute_q_stamp so the two stamps read identically."""
    import hashlib
    content = [ln.rstrip() for ln in lines[start:end]
               if not _BACKLOG_STAMP_RE.match(ln.strip())]
    digest = hashlib.sha1("\n".join(content).encode("utf-8")).hexdigest()
    n = int(digest, 16) % (36 * 36)
    return _BASE36[n // 36] + _BASE36[n % 36]


def read_backlog_stamp(lines, start, end):
    """The stored backlog stamp value in lines[start:end], or None if unstamped."""
    for k in range(start + 1, end):
        m = _BACKLOG_STAMP_RE.match(lines[k].strip())
        if m:
            return m.group(1)
    return None


def restamp_backlog(lines):
    """Insert-or-update the backlog integrity stamp on the line under the H1.
    keepends lines in, keepends lines out. No H1 → lines returned unchanged.
    Call this LAST, after the full state cascade (perform_edit + refresh_q_md),
    immediately before writing the backlog, so the stamp reflects final content."""
    rng = _backlog_stamp_range(lines)
    if rng is None:
        return lines
    start, end = rng
    stamp_line = f"<!-- state:backlog {compute_backlog_stamp(lines, start, end)} -->\n"
    for k in range(start + 1, end):
        if _BACKLOG_STAMP_RE.match(lines[k].strip()):
            return lines[:k] + [stamp_line] + lines[k + 1:]
    return lines[:start + 1] + [stamp_line] + lines[start + 1:]


def heal_backlog_if_stale(slug, backlog_path):
    """F247 — detect a raw (non-`state`) backlog hand-edit via the integrity
    stamp; on mismatch, HEAL (idempotent `refresh_q_md` re-derivation of banner
    + Q.md, then re-stamp) and return an educational complaint. Never reverts.

    Returns a complaint string on a genuine detected hand-edit, else None:
      - stamp matches computed  -> consistent, no-op, None.
      - stamp present, mismatch -> real hand-edit: heal + restamp + complaint.
      - no stamp (grandfathered) -> silent heal + stamp, None.

    Idempotent: on a consistent backlog it does nothing, so it is safe to call
    at the start of every `state` invocation.
    """
    if backlog_path is None or not Path(backlog_path).is_file():
        return None
    backlog_path = Path(backlog_path)
    raw = backlog_path.read_text(encoding="utf-8")
    lines = raw.splitlines(keepends=True)
    rng = _backlog_stamp_range(lines)
    if rng is None:
        return None
    stored = read_backlog_stamp(lines, *rng)
    computed = compute_backlog_stamp(lines, *rng)
    if stored is not None and stored == computed:
        return None  # consistent — nothing to heal
    # Drift (or first-sight). Heal the derived views first — refresh_q_md may
    # itself repair the backlog (stale [Done] rows, bracket normalization), so
    # re-read afterward before stamping the final content.
    refresh_q_md(slug)
    raw2 = backlog_path.read_text(encoding="utf-8")
    lines2 = raw2.splitlines(keepends=True)
    stamped = restamp_backlog(lines2)
    if stamped != lines2:
        backlog_path.write_text("".join(stamped), encoding="utf-8")
        _selffire(backlog_path)
    if stored is None:
        return None  # grandfathered — silent heal + first stamp
    return (
        f"[state] backlog hand-edit detected in {backlog_path.name} "
        f"(state:backlog stamp {stored}→{computed}) — the derived banner "
        f"and Q.md were re-healed. Change backlog state through `state`, not by "
        f"hand, so the queue can never go stale (F247)."
    )


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
    Per F176 the `{slug} queries.md` page is built on demand by /query's
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

    CLI: backlog-edit.py {slug} {ROW-ID} -Q {add|resolve|remove|rewrite}
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
        lines = restamp_open_questions(lines)
        feature_path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""),
                                encoding="utf-8")
        _selffire(feature_path)
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
        # Phase-2 transition: retire the block once nothing pending remains.
        lines, _dropped = drop_open_questions_if_empty(lines)
        lines = restamp_open_questions(lines)
        feature_path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""),
                                encoding="utf-8")
        _selffire(feature_path)
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
        lines = restamp_open_questions(lines)
        feature_path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""),
                                encoding="utf-8")
        _selffire(feature_path)
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
        lines = replace_q_bullet(lines, start, end, new_bullet_lines)
        lines = restamp_open_questions(lines)
        feature_path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""),
                                encoding="utf-8")
        _selffire(feature_path)
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
