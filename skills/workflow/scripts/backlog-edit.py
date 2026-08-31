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

import gzip
import json
import os
import pathlib
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
# `ANCHOR_VAULT_ROOT` (F269) points the whole toolchain at a fixture vault.
# `audit-q.py _resolve_vault_root` reads the same variable and is the contract;
# this module cannot import it (audit-q imports THIS one, so the dependency
# runs the other way), which is why the read is repeated rather than shared.
#
# The variable exists because a fixture render had no way NOT to reach the real
# vault: `test-f244-stop-gate.sh` and `test-f241-q-stamp.sh` spliced their
# fixture sections into the live `Q.md`, and their teardown — which `rm -rf`s
# the fixture but only `cp`-restores a Q.md snapshot — both left orphan
# sections behind AND could revert a concurrent agent's Q.md writes.
VAULT_ROOT = Path(os.environ["ANCHOR_VAULT_ROOT"]).expanduser() \
    if os.environ.get("ANCHOR_VAULT_ROOT") else HOME / "ob" / "kmr"
SENTINEL = HOME / ".claude" / "state" / "agent-messages"
STATE_FILE = HOME / ".config" / "anchor-system" / "backlog-edit" / "state.json"

VALID_HORIZONS = {"Now", "Next", "Later", "Active", "Ready", "Done", "Verify", "Icebox"}
ICEBOX_HORIZON = "Icebox"
ICEBOX_DEFAULT_H2 = "Iced"
SKIP_PATH_FRAGMENTS = ("/.history/", "/worktrees/", "/Yore/", "/.trash/", "/Closet/")

# Closed set of canonical backlog-row status brackets (per [[SKA workflow]]).
# Write-time enforcement lives in validate_status() below. Non-canonical brackets
# ([Designed], [Foo], …) get rejected at state define/set rather than
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
    # F305 — the ABSOLUTE date is the intended form: a relative duration ages
    # into a lie (a thirty-day-old `[Watching 7d]` still reads *7d*, because the
    # bracket shows the original DURATION and a reader takes it for REMAINING),
    # while a date never needs renumbering. The relative forms are retired but
    # still accepted, because 5 live rows carry them and refusing a shape before
    # its replacement can be written would make those rows unwritable — the
    # migration has to be able to run through this gate.
    re.compile(r"^Waiting\s+\d{4}-\d{2}-\d{2}$", re.IGNORECASE),             # "Waiting 2026-09-01"
    re.compile(r"^Watching\s+\d{4}-\d{2}-\d{2}$", re.IGNORECASE),            # "Watching 2026-09-01"
    re.compile(r"^Waiting\s+\d+[dhmy]$", re.IGNORECASE),                     # "Waiting 7d" (retired)
    re.compile(r"^Watching\s+\d+[dhmy]$", re.IGNORECASE),                    # "Watching 14d" (retired)
    # ^ both retired forms stay PARSEABLE on purpose: 23 live rows carry the
    #   bare or relative shape and must remain readable and re-bracketable.
    #   `watch_grammar_gate` is what refuses them on a WRITE (F305).
    re.compile(r"^Verify(-by\s+\d{4}-\d{2}-\d{2})?$", re.IGNORECASE),        # "Verify-by 2026-06-02"
    re.compile(r"^Done(\s+\d{4}-\d{2}-\d{2})?$", re.IGNORECASE),             # "Done 2026-06-04"
    # F283 — the handle is ANY row identifier, not only a feature: "a Verify can
    # gate other work, so it can be a blocker." Same identifier shape the row
    # parser accepts (F091 / T007 / B-QFix / DMUX-F034 / R-Scaffolding.5.2).
    # Bare "Blocked" still parses here so existing rows can be READ and
    # re-bracketed; `blocked_grammar_gate` is what refuses it on a write.
    # F305 — TWO argument forms, both legal and deliberately not distinguished
    # here: the HANDLE form (`Blocked F210`, `Blocked HA-T045`, `Blocked
    # B-QFix`) names a row, and the WHAT form (`Blocked upstream API`) names a
    # change in the universe in 1-3 words. Only the handle form is a typed
    # edge — `_BLOCKED_HANDLE_RE` in queries-render.py stays single-token on
    # purpose, so a multi-word "what" is never mistaken for a row id and
    # rendered as a dead link.
    #
    # The 1-3 word cap is the spec's, and it is doing real work: it is what
    # keeps this from becoming a free-text field. The bracket is a visual
    # index scanned at a glance; a sentence there is a body, not a state.
    re.compile(r"^Blocked(\s+[A-Za-z][A-Za-z0-9_\-]*(?:\.[A-Za-z0-9_\-]+)*"
               r"(?:\s+[A-Za-z0-9][A-Za-z0-9_\-]*){0,2})?$",
               re.IGNORECASE),                                               # "Blocked F210", "Blocked upstream API"
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


def _validate_status_member(member):
    """True if ONE member of a bracket set is a canonical state."""
    if member in VALID_STATUS_BASE:
        return True
    return any(pat.match(member) for pat in VALID_STATUS_PATTERNS)


def validate_status(status):
    """Reject non-canonical brackets at write time.

    Accepts 'same' / 'delete' (control tokens used by state's row-edit
    delegation). Otherwise EVERY MEMBER of the bracket must match either
    VALID_STATUS_BASE (case-sensitive) or one of VALID_STATUS_PATTERNS
    (case-insensitive for the keyword, exact for the numeric suffix).

    F305 — THE BRACKET IS A SET. `[Ready, Questions]` and `[Ready, 3
    Questions, Verify]` are legal, and any combination is legal: there are no
    blessed pairs, because an exception is a rule to remember with no benefit
    and an audit cannot explain a refusal that rests on no principle. A row in
    two classes counts in both, so class counts may sum to more than the row
    count — intended, not a defect.

    The bracket STAYS THE SOURCE OF TRUTH; this was the alternative Dan
    rejected outright when the proposal was to derive it from other fields:
    *"I don't like the idea that the brackets stop being the source of truth.
    I don't want to lose that… this is the thing that has really gotten us in
    trouble, agent says one thing but then everything says another thing."*
    Nothing about a row's state is computed behind the user's back — the row
    says what it is, and a row that disagrees with reality can be pointed at.
    """
    if status in ("same", "delete"):
        return
    stripped = status.strip().strip("[]").strip()
    members = [m.strip() for m in stripped.split(",") if m.strip()]
    if not members:
        raise BacklogEditError(f"invalid status {status!r}: empty bracket")
    bad = [m for m in members if not _validate_status_member(m)]
    if not bad:
        return
    plural = "members" if len(bad) > 1 else "member"
    raise BacklogEditError(
        f"invalid status {status!r}; unrecognized {plural}: "
        f"{', '.join(repr(b) for b in bad)}. Expected one of "
        f"{sorted(VALID_STATUS_BASE)} or a compound form "
        f"(N Questions, N Ready, Waiting YYYY-MM-DD, Watching YYYY-MM-DD, "
        f"Verify-by YYYY-MM-DD, Done YYYY-MM-DD, Blocked <handle>). "
        f"A bracket may be a comma-separated SET of these."
    )


# --------------------------------------------------------------------------
# Errors

class BacklogEditError(SystemExit):
    def __init__(self, msg):
        super().__init__(f"backlog_edit: {msg}")


# --------------------------------------------------------------------------
# Anchor resolution

def find_backlog(slug):
    """Locate `<slug> Backlog.md` somewhere under VAULT_ROOT.

    NOTE: the argument is the backlog FILENAME PREFIX, not the `.anchor` slug.
    Those differ for every anchor whose display name isn't already all-caps
    (`Scout Backlog.md` vs `slug: SCOUT`), and for anchors whose tracking lives
    under another name entirely (`SKA` tracks in `Tink Backlog.md`). Passing the
    slug fails with a bare not-found, which has already been misread once as
    "these anchors are unwritable" — so collect near-misses and name them.
    """
    target = f"{slug} Backlog.md"
    matches = []
    near = []
    for root, dirs, files in os.walk(VAULT_ROOT, followlinks=True):
        # Skip noisy paths
        if any(frag in root + "/" for frag in SKIP_PATH_FRAGMENTS):
            dirs[:] = []
            continue
        if target in files:
            matches.append(Path(root) / target)
        else:
            for f in files:
                if f.lower() == target.lower():
                    near.append(f[: -len(" Backlog.md")])
    if not matches:
        hint = ""
        if near:
            hint = " — did you mean '%s'? (this argument is the backlog filename prefix, not the .anchor slug)" % "' / '".join(sorted(set(near)))
        raise BacklogEditError(f"no '{target}' found under {VAULT_ROOT}{hint}")
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
    """The `{slug} Track/` directory (where Messages.md lives).

    F329 — the backlog may be folder-doc form (`{slug} Track/{slug} Backlog/
    {slug} Backlog.md`, the folder holding the T-docs); the Track dir is then
    one level further up. The test is stem == parent name, same as every
    other folder-doc recognizer.
    """
    parent = backlog_path.parent
    if parent.name == backlog_path.stem:
        return parent.parent
    return parent


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
    icebox = anchor_track_dir(backlog_path) / f"{slug} Icebox.md"
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


def arrow_doc_path(row_body):
    """Vault path of the LAST arrow-linked (`→ [[doc]]`) doc in a row body or
    span, or None. The last-link rule matches sync_doc_next's historical
    behavior: prose arrows earlier in a body lose to the pointer at the end."""
    if not row_body:
        return None
    arrow_links = list(re.finditer(r"→\s+(\[\[[^\]]+\]\])", row_body))
    m = WIKI_LINK_RE.search(arrow_links[-1].group(1)) if arrow_links else None
    if not m:
        return None
    return find_file_by_basename(m.group(1).strip())


def _doc_head(doc_path):
    """(lines, h1_idx, end) for a doc — end is the first H2 (the intro block
    boundary). None on any read/shape failure."""
    if doc_path is None:
        return None
    try:
        text = doc_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    lines = text.splitlines(keepends=True)
    h1_idx = next((i for i, l in enumerate(lines) if l.startswith("# ")), None)
    if h1_idx is None:
        return None
    end = next((i for i in range(h1_idx + 1, len(lines))
                if lines[i].startswith("## ")), len(lines))
    return lines, h1_idx, end


def read_doc_next(doc_path):
    """The doc's `next::` Dataview field text (F332), or None."""
    head = _doc_head(doc_path)
    if head is None:
        return None
    lines, h1_idx, end = head
    for i in range(h1_idx + 1, end):
        if lines[i].startswith("next::"):
            txt = lines[i][len("next::"):].strip()
            return txt or None
    return None


# A struck-through pointer — `→ ~~[[Old Name|T241]]~~` — with the dash that
# joined it to what follows. Left in doc fields by the F614 renames, which
# carried the old row body (struck link included) into the doc's `next::` /
# description / Summary, so every regeneration wrote the dead pointer back
# onto the row (T632, Atticus 2026-08-30: 9 rows, all with a live pointer
# already in front). A struck pointer is never meaningful content.
_STRUCK_POINTER_RE = re.compile(r"→\s*~~\[\[[^\]]*\]\]~~\s*(?:[—–-]\s*)?")


def _strip_struck_pointers(text):
    """`text` with every struck pointer removed, or None when nothing is left."""
    if not text or "~~[[" not in text:
        return text or None
    out = _STRUCK_POINTER_RE.sub("", text).strip()
    out = re.sub(r"^[—–-]\s*", "", out).strip()
    return out or None


def doc_derived_line(doc_path):
    """F332 — the one derived line a pure-link backlog row carries: the doc's
    `next::` field, falling back to its frontmatter `description:`, falling
    back to the orientation line under the H1. None when nothing usable.
    A struck pointer inside any of the three is dropped (T632)."""
    nxt = _strip_struck_pointers(read_doc_next(doc_path))
    if nxt:
        return nxt
    head = _doc_head(doc_path)
    if head is None:
        return None
    lines, h1_idx, _ = head
    if lines and lines[0].strip() == "---":
        for l in lines[1:]:
            if l.strip() == "---":
                break
            if l.startswith("description:"):
                desc = _strip_struck_pointers(
                    l[len("description:"):].strip().strip('"').strip())
                if desc:
                    return desc
    if h1_idx + 1 < len(lines):
        orient = lines[h1_idx + 1].strip()
        if orient and not orient.startswith(("#", ">", "next::", "|", ":>>")):
            orient = _strip_struck_pointers(orient)
            if orient:
                return orient
    return None


def is_derived_row_body(body):
    """F332 — a row whose body LEADS with the arrow pointer is a pure-link
    (derived) row: everything after the pointer is regenerated from the doc."""
    return bool(body) and body.lstrip().startswith("→ [[")


def _refuse_body_discarded_on_derived_row(lines, row_id, body, body_provided):
    """Refuse a `--body` whose prose would be thrown away (T578).

    On a pointer-led row only the LINK is the caller's; everything after the
    `—` regenerates from the doc, which `regenerate_derived_row` documents as
    deliberate electric-zone doctrine. The behaviour is right. The silence is
    not: `state` printed `updated <row>` and the prose never reached the file.

    Reported by MUX 2026-08-20 and reproduced here in a fixture — a plain row
    takes `--body`, a doc-backed row reports the same success and keeps the
    doc's text. **Why the silence is worse than the discard:** the caller is
    usually a script sweeping many rows, so a batch correction reports N
    successes and lands N-k, and the k that silently reverted are exactly the
    doc-backed — i.e. most substantial — rows. MUX caught it only by grepping
    afterwards for the string they had removed.

    It warned rather than refused from 2026-08-20 to 2026-08-28, because the
    `/feature` mint path set a row's pointer with `--body "→ [[doc|F] — F —
    Title"` and a refusal would have failed every mint. Dan ruled 2026-08-28
    that a tool must never half-succeed, so `state set --doc NAME` now writes
    the pointer alone (the mint path uses it) and this refuses outright.

    `verify_write_landed`'s F332 branch is what let this pass — for two
    derived bodies it compares only the wiki-link target and returns clean.
    That comparison is correct GIVEN this contract (the trailing text is not
    the caller's to set); it just could not be the thing that announced it.
    """
    if not body_provided:
        return
    # Read the PLACED row rather than the `--body` argument. A body with no
    # pointer does not stay pointerless: T174's carry puts the row's existing
    # `→ [[doc]]` back on, which makes it derived, which sends it through the
    # same discard — so a caller who passes plain prose to a doc-backed row
    # loses it too, and checking the raw argument would miss exactly that case
    # (found while testing the first cut of this warning).
    row_i = None
    for i, line in enumerate(lines):
        rm = ROW_HEADER_RE.match(line)
        if rm and len(rm.group(1)) == 0 and rm.group(2) == row_id:
            row_i = i
            break
    if row_i is None:
        return
    m = ROW_FULL_RE.match(lines[row_i])
    if not m:
        return
    placed = (m.group("body") or "").strip()
    if not is_derived_row_body(placed):
        return
    # Strip the pointer by SHAPE, not by splitting on one separator character.
    # Two writers produce this line and they do not agree: the canonical F332
    # form joins with an em-dash, while T174's carry joins with `·`. Splitting
    # on `—` alone silently skipped every carried body — which is the larger
    # half of the bug, since a caller passing plain prose to a doc-backed row
    # gets the pointer carried on and only then loses the prose.
    tail = re.sub(r"^→\s*\[\[[^\]]*\]\]\s*[—·-]?\s*", "", placed)
    if not tail.strip() or tail.strip() == placed:
        return                      # pointer only — nothing was discarded
    doc = arrow_doc_path(placed)
    if doc is None:
        return
    derived = (doc_derived_line(doc) or "").strip()
    if _strip_trailing_anchors(tail.strip()) == derived:
        return                      # the caller wrote what the doc already says
    # T578, Dan 2026-08-28: REFUSE, not warn. A tool that prints `updated`
    # must have done all of what it was asked; "half of what you asked for"
    # is the semantics that confuses the agent. The mint path that used to
    # need the warning now passes `--doc NAME`, which writes the pointer and
    # nothing else, so nothing legitimate reaches this raise.
    raise BacklogEditError(
        f"{row_id} is a doc-backed row, so the text after its `→ [[…]]` "
        f"pointer regenerates from the doc and the prose you passed to --body "
        f"would NOT be written. Refused — nothing was changed. To change what "
        f"the row says, use `--next \"<text>\"` (which writes both the row and "
        f"the doc's `next::`), or edit the doc directly; to set only the "
        f"pointer, use `--doc NAME`.")


def regenerate_derived_row(lines, row_id):
    """F332 — rewrite a placed derived row's body to the canonical
    `→ [[<doc>|<row_id>]] — <derived line>` form, reading the derived line
    from the doc (`next::` → description → orientation). When the doc carries
    a `next::`, the row's `- **Next:**` sub-bullet is dropped — the doc is
    the source and the derived line already shows it (electric-zone
    doctrine: hand text after the pointer is overwritten here).

    Mutates `lines` in place; returns True when the row was rewritten.
    No-op (False) for non-derived bodies and unresolvable doc links."""
    row_i = None
    for i, line in enumerate(lines):
        rm = ROW_HEADER_RE.match(line)
        if rm and len(rm.group(1)) == 0 and rm.group(2) == row_id:
            row_i = i
            break
    if row_i is None:
        return False
    m = ROW_FULL_RE.match(lines[row_i])
    if not m:
        return False
    body = (m.group("body") or "").strip()
    if not is_derived_row_body(body):
        return False
    doc = arrow_doc_path(body)
    if doc is None:
        return False
    derived = doc_derived_line(doc)
    new_body = f"→ [[{doc.stem}|{row_id}]]" + (f" — {derived}" if derived else "")
    new_line = render_row(row_id, m.group("status") or "",
                          m.group("title") or "", new_body)
    if lines[row_i] != new_line:
        lines[row_i] = new_line
    if read_doc_next(doc):
        _ensure_subbullet(lines, row_id, "Next", None)
    return True


def sync_doc_next(row_body, next_text):
    """F332 — the doc owns the Next. An explicit `--next` on a row writes the
    arrow-linked doc's `next::` Dataview field, kept in the H1's intro block
    (under the orientation line, before the first H2): create, update, or —
    for an empty flag, matching T122's removal semantics — delete it. The
    row's `- **Next:**` sub-bullet is a derived copy during the transition to
    pure link-list rows and disappears with them.

    Best effort by design: a row with no resolvable arrow-linked doc (T-rows
    pre-F329-migration, off-vault links) keeps its row-only Next and nothing
    is written. Returns the doc path written, else None.
    """
    target = arrow_doc_path(row_body)
    if target is None:
        return None
    try:
        text = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    lines = text.splitlines(keepends=True)
    h1_idx = next((i for i, l in enumerate(lines) if l.startswith("# ")), None)
    if h1_idx is None:
        return None
    end = next((i for i in range(h1_idx + 1, len(lines))
                if lines[i].startswith("## ")), len(lines))
    field_idx = next((i for i in range(h1_idx + 1, end)
                      if lines[i].startswith("next::")), None)
    new_line = f"next:: {next_text.strip()}\n"
    if not next_text.strip():
        if field_idx is None:
            return None
        del lines[field_idx]
        if (0 < field_idx < len(lines) and lines[field_idx].strip() == ""
                and lines[field_idx - 1].strip() == ""):
            del lines[field_idx]
    elif field_idx is not None:
        if lines[field_idx] == new_line:
            return None
        lines[field_idx] = new_line
    else:
        # Insert after the orientation run — the consecutive non-blank lines
        # directly under the H1 — separated by the blank line R-spine-02
        # requires there, and followed by its own blank before what comes next.
        ins = h1_idx + 1
        while ins < end and lines[ins].strip() != "":
            ins += 1
        if ins < end and lines[ins].strip() == "":
            ins += 1  # keep the orientation's trailing blank before the field
        lines[ins:ins] = [new_line, "\n"]
    target.write_text("".join(lines), encoding="utf-8")
    return target


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


# --------------------------------------------------------------------------
# Row-scoped inline questions (R-backlog-05) — the pending/resolved boundary
#
# A backlog row may host its own numbered questions as `- **Q<n> — …**`
# sub-bullets instead of linking a feature doc. F291 gave the DOC-hosted shape
# a two-zone block — unresolved questions form a prefix, a `### Resolved`
# heading ends it — so the open count is a prefix length rather than a scan. A
# row has no headings to divide with (it is one bullet and its children), so
# the zone head is a sub-bullet of its own.
#
# Three separate readers ask "how many of this row's questions are still
# open": `state`'s resolve verb, audit-q's C24 bracket-count check, and the
# Questions-promise gate below. Before T086 none of them had to, because
# nothing could resolve a row-hosted Q at all — counting every `- **Q<n> —`
# header was correct when no header could ever be answered. The moment a
# resolve verb exists that stops being true everywhere at once, so the
# boundary is defined here and imported, not re-expressed at each site.

ROW_Q_RESOLVED_HEAD = "- **Resolved**"
_ROW_Q_ZONE_HEAD_RE = re.compile(r"^\s*-\s+\*\*Resolved\*\*\s*$")
_ROW_Q_HEADER_RE = re.compile(r"^(\s*)-\s+\*\*Q(\d+)\b")


def row_pending_q_lines(sub_lines):
    """The prefix of a row's sub-bullet lines that is still PENDING.

    Everything from the `- **Resolved**` zone head onward is archive: answered
    questions kept in place with their options and lean, as the doc-side
    `### Resolved` zone keeps them. Callers that count or search for open
    questions pass their lines through here first.

    Returns lines rather than an index because the callers hold different
    things — a list of sub-bullet lines, a whole row span, a joined string —
    and a boundary expressed as a line number would need translating at each
    site, which is exactly where three readers drift back apart.
    """
    out = []
    for line in sub_lines:
        if _ROW_Q_ZONE_HEAD_RE.match(line):
            break
        out.append(line)
    return out


def _pending_q_numbers(span_lines):
    """The set of pending inline Q-numbers in a row span (F329 gate input)."""
    return {m.group(2) for l in row_pending_q_lines(span_lines)
            if (m := _ROW_Q_HEADER_RE.match(l))}


def f329_refuse_new_inline_qs(row_id, old_span, new_span, slug=None):
    """F329 — questions live in docs; the backlog hosts pointers.

    Refuse a write that ADDS a pending `- **Q<n> — …**` sub-bullet to a row.
    Editing a row that already carries legacy inline Qs is fine (they migrate
    on touch, never by force — the F305 D1 pattern), and resolving one is fine
    (the pending set shrinks); only a NEW inline question number refuses.
    """
    added = _pending_q_numbers(new_span) - _pending_q_numbers(old_span or [])
    if not added:
        return
    qs = ", ".join(f"Q{n}" for n in sorted(added, key=int))
    slug_hint = slug or "{SLUG}"
    raise BacklogEditError(
        f"{row_id}: inline row questions are retired (F329) — refusing to add "
        f"{qs}. Questions live in docs: put it in the row's arrow-linked doc "
        f"via `state define <anchor> <doc> Q+`, or for a standalone question "
        f"mint a T-doc `{slug_hint} T<n> - <Title>.md` in the folder-form "
        f"backlog (`<slug> Track/<slug> Backlog/`) holding one stamped "
        f"`## Open Questions` block, and link it from the row with `→ [[…]]`. "
        f"Existing inline Qs migrate on touch, never by sweep."
    )


def count_row_pending_qs(sub_lines):
    """How many `- **Q<n> —` headers sit in the row's pending prefix."""
    return sum(1 for l in row_pending_q_lines(sub_lines)
               if _ROW_Q_HEADER_RE.match(l))


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
    # Only the PENDING prefix counts (T086). An answered question archived in
    # the row's `- **Resolved**` zone keeps its `**Q<n> —` header, so a plain
    # search would let a row whose every question has been answered go on
    # claiming [Questions] forever — the bracket would be honored by its own
    # history.
    if any(_ROW_Q_HEADER_RE.match(l) or re.search(r"\*\*Q\d+\s+—", l)
           for l in row_pending_q_lines(body.splitlines())):
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
    # An unset row carries `[ ]`, whose status string is whitespace — truthy
    # but with no first token, so a bare `status.split()[0]` raises IndexError
    # and takes the whole edit down. Split first, then test.
    parts = status.split() if status else []
    if not parts or not parts[0].startswith("Verify"):
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


def _terminal_bracket(status):
    """True for the brackets a row does not come back from — `Done`, `Done
    YYYY-MM-DD`. Deliberately NOT folded into `_verify_family` (T123): the
    family is what the F240 ownership gate governs, and that gate exists to
    vet a question being ASKED. A terminal row is recording that the question
    was ANSWERED, which needs no ownership justification and must not be
    refused for reading like a machine event."""
    return (status or "").strip().startswith("Done")


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


def option_labels(body):
    """Every labeled option letter a Q body lists, in order: ['A', 'B', …]."""
    return re.findall(r"^\s*-\s+\*\*\(([A-Za-z]\w*)\)\*\*", body or "",
                      re.MULTILINE)


# --- T160 the risk OF THE LEAN — the fourth gate, built as a route ----------
#
# Three gates already sit on question-minting and all three ask about the
# QUESTION. F257's `--why-ask` asks why you are surfacing it — free text, and
# measured: **9 of 10 Leans passed it while the ladder said ask none**, because
# a free-text gate checks that a sentence EXISTS, not that it FITS
# ([[project_justification_gate_checks_existence_not_fit]]). F270's Damage asks
# how big the blast radius is if the question is got WRONG. `/crank`'s Gate 3
# has the best phrasing — *name the specific bad outcome of continuing* — but
# governs stopping only.
#
# What Dan's rule adds is the SUBJECT of the risk (2026-08-08): *"if there's no
# downside to one of the choices, and that's the one you lean towards, do it…
# if all agents when they have a lean must specify a downside, then as they
# write it down they'll realize this is not enough of a risk."* None of the
# three makes the writer put down *"here is what breaks if I simply do (A)"* —
# the one sentence that deflates itself as it is written.
#
# Built as a ROUTE, not a fourth prose field, for the reason the prose one
# already failed. The first word after the option letter is a closed CASUALTY
# CLASS, and the class decides the outcome — the same shape as F270's Damage,
# which is the gate that worked. `interpretation` (the only thing at stake is
# the agent's own reading of what the user asked for, not anything in the
# vault) auto-resolves to the lean and never surfaces, which is exactly the
# F217 Q4 case Dan was reading when he stated the rule.
#
#     - **Risk of (A):** file — the pass rewrites 1350 anchor pages and their
#       prose has no backup.
# `money` was added 2026-08-10 on a casualty report from [[Munger]] (CFO), and
# it is the one class here that names something OUTSIDE the vault. Munger was
# blocked minting a genuine user decision — how deep to set the floor on a real
# options collar — because every class above describes vault damage and none of
# them fits "Dan's money, via an irreversible fill at a broker". The gate then
# told it that a casualty it could not name meant the question should
# auto-resolve, which converts a missing word into an instruction to decide
# someone's money without asking. An anchor that TRANSACTS rather than writes
# had no valid casualty to name at all.
RISK_CASUALTIES = {
    "file": "a file, a document, or prose that would be damaged or lost",
    "interface": "a name, schema, path or CLI that other code hard-codes",
    "commitment": "a promise already made to a person or a downstream dependant",
    "time": "a named person's time — say WHOSE, and roughly how much",
    "money": "the user's money or another real-world asset, through an action "
             "outside the vault that cannot be recalled",
    "interpretation": "nothing in the vault — only my own reading of what you "
                      "asked for is at stake",
}
# `interpretation` never reaches the user, by the same logic F270 applies to
# waste/priority: a risk that lives entirely inside the agent's head is a
# question the agent is asking itself.
RISK_AUTO_RESOLVE = ("interpretation",)

_RISK_LINE_RE = re.compile(
    r"^\s*-\s+\*\*Risk of \(([A-Za-z]\w*)\):\*\*\s*([A-Za-z]+)\b(.*)$",
    re.MULTILINE)   # `^\s*-`: an F275 Q-row indents its fields as sub-bullets


def parse_risk_of_lean(body):
    """(option, casualty, narrative) from a `- **Risk of (X):** <class> — <…>`
    line, or (None, None, "") when absent. Raises when the class is not one of
    RISK_CASUALTIES — a typo must not pass as a stated risk."""
    m = _RISK_LINE_RE.search(body or "")
    if not m:
        return None, None, ""
    option, casualty = m.group(1), m.group(2).lower()
    narrative = m.group(3).strip(" —–-.:")
    if casualty not in RISK_CASUALTIES:
        raise BacklogEditError(
            f"refused: risk casualty {casualty!r} is not one of "
            f"{{{', '.join(RISK_CASUALTIES)}}} — the first word after the "
            f"option letter is the class of thing that gets hurt (a single "
            f"word so it parses), then one sentence saying which one and how:\n"
            + "\n".join(f"    • {k:<15}{v}" for k, v in RISK_CASUALTIES.items())
        )
    return option, casualty, narrative


def _risk_instruction(q_num, lean):
    label = f"Q{q_num}" if q_num is not None else "Q+"
    letter = lean.strip("()") if lean and lean != "—" else "X"
    return (
        f"[{label}] refused: it carries a lean but does not state the risk OF "
        f"THAT LEAN.\n"
        f"  Add one line naming the option you lean toward and what it would "
        f"cost to just DO it:\n"
        f"    - **Risk of ({letter}):** <class> — <one sentence: which thing, "
        f"and how it gets hurt>\n"
        f"  The class is one word, and it is the route — it decides whether "
        f"this reaches the user:\n"
        + "\n".join(f"    • {k:<15}{v}" for k, v in RISK_CASUALTIES.items())
        + "\n  Write the sentence before you decide whether to ask. If the "
          "only casualty you can name\n"
          "  is `interpretation`, the machine will resolve this to your own "
          "lean and never surface it —\n"
          "  which is the answer, not a rejection."
    )


def risk_of_lean_gate(q_num, body, strength):
    """T160 — a Lean/Strong question must state the risk of ITS OWN LEAN.

    Returns (casualty, narrative) — `casualty` is None when no risk line is
    required (a `Recommendation: None` is the honest ask and is never gated,
    mirroring F257). Raises BacklogEditError on every refusal.
    """
    if strength not in ("Lean", "Strong"):
        return None, ""
    # The EXPLICIT letter on the Recommendation line, not `leaned_choice` —
    # which falls back to the first listed option when the Recommendation names
    # none. That fallback is right for auto-resolving (something must be
    # picked) and wrong here: refusing `Risk of (C)` because a GUESSED lean was
    # (A) would refuse the writer over the machine's own guess.
    rm = _RECOMMENDATION_STRENGTH_RE.search(body or "")
    cm = re.search(r"\(([A-Za-z]\w*)\)", rm.group(1)) if rm else None
    lean = f"({cm.group(1)})" if cm else None
    option, casualty, narrative = parse_risk_of_lean(body)
    if casualty is None:
        raise BacklogEditError(_risk_instruction(q_num, lean))
    label = f"Q{q_num}" if q_num is not None else "Q+"
    # The SUBJECT check — the whole point of the gate. A risk stated about some
    # OTHER option is the risk of the road not taken, and it is the one thing
    # that never deflates: of course the option you rejected is worse.
    options = option_labels(body)
    if lean:
        if f"({option})" != lean:
            raise BacklogEditError(
                f"[{label}] refused: the Recommendation leans {lean} but the "
                f"risk is stated of ({option}).\n"
                f"  The gate exists to make you write the downside of the "
                f"option you are ABOUT TO TAKE — the\n"
                f"  risk of an option you already rejected argues for the lean "
                f"instead of testing it.\n"
                f"  Restate it as `- **Risk of {lean}:** …`.")
    elif options and option not in options:
        raise BacklogEditError(
            f"[{label}] refused: `Risk of ({option})` names no option this "
            f"question lists ({', '.join('(' + o + ')' for o in options)}).")
    if not narrative:
        raise BacklogEditError(
            f"[{label}] refused: `Risk of ({option}):` names the class "
            f"`{casualty}` and then stops.\n"
            f"  The sentence is the gate — {RISK_CASUALTIES[casualty]}. Say "
            f"WHICH one and HOW it gets hurt.")
    return casualty, narrative


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


# Matches one ` · *why-user-action: …*` trailer, greedily enough to catch a run
# of them. Used to strip before re-appending so the annotation cannot double.
_WHY_USER_RE = re.compile(r"(?:\s*·\s*\*why-user:[^*]*\*)+\s*$")
_WHY_USER_ACTION_RE = re.compile(r"(?:\s*·\s*\*why-user-action:[^*]*\*)+\s*$")


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
        # T236 — STRIP BEFORE APPENDING, or the annotation doubles. `eff_user`
        # is the EXISTING sub-bullet text whenever the caller passed
        # `--why-user-action` without `--user`, and that text already carries a
        # trailer, so a bare append writes a second one. Every re-touch added
        # another; Sonar found four doubled rows on SONAR the day after they had
        # been deduped by hand, because the dedup was undone by the next touch.
        # Stripping first makes the operation idempotent, which is also what
        # lets `--why-user-action` be the supported way to FIX a doubled row.
        a_text = _WHY_USER_ACTION_RE.sub("", a_text).strip()
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
    # A row that declares itself unrunnable in its own Next is the same defect
    # as a sentinel, just written in prose. MUX F216 sat [Implementing] — and
    # so inside `Runnable N` — for three cranks while its Next opened
    # "NOTHING HERE IS AGENT-RUNNABLE — every open sub-item is gated on a named
    # user answer". This list can never be complete (that is why the crank
    # skill now makes rebracketing the agent's job), but the phrasings a row
    # actually reaches for when it gives up are worth catching for free.
    "nothing here", "nothing is", "nothing to do", "nothing agent",
    "not agent-runnable", "not runnable", "not actionable", "blocked on",
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


_RELATIVE_WATCH_RE = re.compile(r"^(?:Waiting|Watching)\s+\d+[dhmy]$", re.IGNORECASE)


def blocked_grammar_gate(status, row_id):
    """F283 — `[Blocked]` must name what it is blocked ON.

    Dan's structural claim, 2026-07-29: *"we shouldn't be able to say blocking.
    Maybe the only thing you're allowed to block on is another feature. If
    you're not blocking on another feature, you're not blocked. You have a
    question, maybe."* This converts `[Blocked]` from a mood into a typed edge,
    and the edge is what lets the render promote a blocker into its own section
    and show you the thing actually worth working on.

    Bare `[Blocked]` is the bracket four Dan-gated rows hid behind: each
    recorded its real blocker in prose, where nothing could read it, and so
    each dropped out of every surface. Three states replace it, and each names
    what it waits on — `[Blocked <handle>]` on another row, `[Questions]` on an
    answer from Dan, `[Waiting <condition>]` on time or an external state.

    `<handle>` is any row identifier, not only a feature: a Verify can gate
    other work, so it can be a blocker.

    Enforced at the write rather than audited afterwards, per the standing
    preference for a structural gate over one more rule to remember. Rows
    written before this gate keep their bare bracket until something touches
    them — measured 2026-07-30 there were 33 vault-wide, against 6 that named a
    handle.
    """
    if (status or "").strip() != "Blocked":
        return
    raise BacklogEditError(
        f"[Blocked] refused: {row_id} must name what it is blocked ON.\n"
        f"  Per F283, `[Blocked]` is a typed edge, not a mood — the render "
        f"promotes whatever\n"
        f"  other rows are blocked on into its own section, and a bare bracket "
        f"carries no edge\n"
        f"  to follow. Pick the one that is actually true:\n"
        f"    --status \"Blocked <handle>\"     waiting on another row "
        f"(e.g. \"Blocked F142\") — any row id,\n"
        f"                                    a Verify can gate work too\n"
        f"    --status Questions              waiting on an answer from the "
        f"user\n"
        f"    --status \"Waiting <YYYY-MM-DD>\"  waiting on time or an external "
        f"state — the date is\n"
        f"                                    when to look again; name the "
        f"condition in the body\n"
        f"                                    (\"Waiting on: <event>\")"
    )


def watch_grammar_gate(status, row_id):
    """F305 — `[Waiting]` and `[Watching]` must say WHEN to look again.

    The Parked class is the one Dan named as able to fester: *"everything in
    Parked is blocked, but unblocking may or may not handle itself."* A bare
    `[Waiting]` is the shape that makes that true — it records that something
    is deferred and nothing about when the deferral ends, so no surface can
    ever tell a row whose moment has come from one that is simply forgotten.
    A date can be compared to today. A mood cannot.

    THE RELATIVE FORM IS REFUSED FOR A DIFFERENT AND SHARPER REASON: it ages
    into a lie. `[Watching 7d]` written a month ago still reads *7d*, because
    the bracket shows the DURATION it was set with while every reader takes it
    for the time REMAINING. An absolute date is wrong in no way as it ages; it
    simply becomes past, which is exactly the signal wanted.

    This gate is FIRST, not last, at Dan's direction 2026-08-13. The original
    plan swept the 23 existing rows and only then closed the door. He inverted
    it: *"once we believe in this approach, I actually think we should go ahead
    and promote the mandatory refuse-at-write early — that way if it's gonna
    explode on us, because refusing is gonna cause the agents to not be able to
    do something that they need to do, we want to know that early."* Closing
    the door first also stops the list growing while the sweep runs.

    IT FIRES ONLY ON A BRACKET THE CALLER ASKED FOR, and that narrowing was
    forced by measurement rather than reasoned in advance — which is the whole
    point of promoting this step to first. The gate was written strict, matching
    its sibling `blocked_grammar_gate`, on the assumption that `--status same`
    returns before validation. IT DOES NOT: line ~2305 resolves `same` to the
    row's EXISTING bracket before any gate runs, so a strict gate re-validates a
    bracket nobody touched. A live probe on `TINK F288` — a `--next` edit,
    nothing to do with the bracket — was refused. All 23 rows vault-wide
    carrying the bare or relative shape would have become unwritable for ANY
    edit.

    That is not the cost Dan agreed to. He asked for refuse-at-write early so
    the list would STOP GROWING; blocking edits to rows that already exist is a
    different effect, and the one he named as the thing to discover early. The
    deciding argument against keeping it strict is that it would force an agent
    who only wants to update a `- **Next:**` to invent a date — and a
    manufactured date is a false claim, strictly worse than an honestly vague
    bracket. So: a NEW bare or relative bracket is refused, an existing one is
    left alone until something deliberately re-brackets it, and the 23 are
    migrated as their own step with real dates.

    The asymmetry with `blocked_grammar_gate` is therefore deliberate, not
    drift. That gate's own docstring elects the strict reading — *"rows written
    before this gate keep their bare bracket until something touches them"* —
    and it costs nothing there, because `[Blocked <handle>]` is answerable from
    the row itself: the blocker is already named in its prose. A date is not
    recoverable that way. **The rule is: force a fix on touch when the row
    already contains the answer; refuse only new writes when it does not.**
    """
    members = [m.strip() for m in (status or "").strip().strip("[]").split(",")
               if m.strip()]
    bare = [m for m in members if m.lower() in ("waiting", "watching")]
    aged = [m for m in members if _RELATIVE_WATCH_RE.match(m)]
    if not bare and not aged:
        return
    if bare:
        which = bare[0]
        why = (f"[{which}] refused: {row_id} must say WHEN to look again.\n"
               f"  A bare [{which}] records that the row is deferred and "
               f"nothing about when the\n"
               f"  deferral ends, so nothing can tell a row whose moment has "
               f"come from one that\n"
               f"  is simply forgotten. A date can be compared to today.\n")
    else:
        which = aged[0]
        why = (f"[{which}] refused: {row_id} must carry an ABSOLUTE date.\n"
               f"  A relative duration ages into a lie — [{which}] written a "
               f"month ago still reads\n"
               f"  {which.split()[-1]}, because the bracket shows the duration "
               f"it was SET with while every\n"
               f"  reader takes it for the time REMAINING.\n")
    kw = which.split()[0].capitalize()
    kw = "Waiting" if kw.lower() == "waiting" else "Watching"
    raise BacklogEditError(
        why +
        f"  Write the date you want to look again:\n"
        f"    --status \"{kw} YYYY-MM-DD\"\n"
        f"  If nothing external is pending and the wait is really on an "
        f"answer from Dan,\n"
        f"  [Questions] is the honest bracket; if it waits on another row, "
        f"[Blocked <handle>]."
    )


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


def _pointer_provenance(body, arrow_links):
    """Explain WHICH `→ [[…]]` in the body became the row's doc pointer.

    T089 — the detector matches `→ [[…]]` anywhere in the body, last one wins,
    and an em-arrow is ordinary prose punctuation: a Done body describing a
    rename as `` `prj/Ask/` `` → `[[Ask Project]]` was read as a pointer and
    F102 refused, naming a real anchor page with a real missing `## Status` H2.
    The refusal was therefore indistinguishable from a legitimate block, and
    the natural response — go add a Status block to an unrelated doc — is
    exactly the wrong repair.

    Positionless matching is kept deliberately. The alternative is a positional
    slot, and the corpus rules it out: of 298 rows vault-wide carrying an
    arrow-link, 215 lead with it but 58 put it trailing and 25 have prose after
    it, so requiring the leading slot would silently drop the F102 gate on 83
    rows — quiet coverage loss on the very check that exists to stop drift,
    which is strictly worse than a loud refusal that explains itself. So the
    refusal explains itself instead: it names the substring it matched, and
    when more than one arrow appears it says so, because a second arrow is the
    strongest available signal that one of them is prose.
    """
    matched = arrow_links[-1].group(0).strip() if arrow_links else ""
    lines = [f"  Pointer matched from the body text: {matched!r}"]
    if len(arrow_links) > 1:
        others = ", ".join(repr(a.group(0).strip()) for a in arrow_links[:-1])
        lines.append(
            f"  This body holds {len(arrow_links)} `→ [[…]]` sequences and the LAST wins;\n"
            f"  the others were {others}."
        )
    lines.append(
        "  F102 reads `→ [[…]]` anywhere in the body, so an em-arrow used as prose\n"
        "  punctuation (`old/path/` → `[[New Name]]`) is read as a doc pointer. If that\n"
        "  is what happened here, the fix is in THIS row, not in the target doc: reword\n"
        "  the prose arrow (an em-dash or the word 'to' reads the same), or give the row\n"
        "  a real leading `→ [[F<n> — …]]` pointer so the last-wins rule lands on it."
    )
    return "\n".join(lines)


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
    provenance = _pointer_provenance(body, arrow_links)
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
            f"  Add the block to the feature doc, then re-run.\n"
            f"{provenance}"
        )
    if leading_word.strip() != status.strip():
        raise BacklogEditError(
            f"[{status}] refused: target [[{basename}]] `## Status` body begins with\n"
            f"  `**{leading_word}**` but the status being set is `**{status}**`.\n"
            f"  Update the feature doc's Status block to reflect the new status with\n"
            f"  a one-sentence justification, then re-run.\n"
            f"{provenance}"
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
    parts = status.split() if status else []          # `[ ]` → whitespace, no tokens
    if not parts or not parts[0].startswith("Done"):
        return
    prior = existing_status.split() if existing_status else []
    if prior and prior[0].startswith("Done"):
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
    parts = status.split() if status else []          # `[ ]` → whitespace, no tokens
    if not parts:
        return
    status_root = parts[0]
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
# Feature-doc filename grammar (F298, F300)

# Three stem forms are first-class, permanently:
#
#   F294 — URL validation           legacy, every doc before 2026-08-02
#   SKA F294 — URL validation       F298, the slug-prefixed morning
#   SKA294 - URL validation         F300, current — authored form
#
# The slug is in the filename because an F-number is a PER-ANCHOR namespace
# that resets at F1 in every anchor, so `F294` alone names as many files as
# there are anchors and cannot be found by search. F300 then fused the slug to
# the number and went ASCII: `SKA294` is one typeable token, and it is a
# STRONGER discriminator than `F294` ever was — it names one anchor rather than
# every anchor at once. Older docs are never renamed, so all three forms are
# accepted forever; only the newest is authored.
#
# The slug alternative is one bare token. In the F298 form it may carry digits
# (`[A-Za-z][A-Za-z0-9]*`); in the fused form it is letters only, because
# `[A-Za-z0-9]*\d+` is ambiguous — greedy matching would split `TINK300` into
# slug `TINK30` + number `0`. Deliberately NOT `[\w\s]+` in either: a greedy
# multi-token prefix would match ordinary prose stems (`Notes on F12 — foo`).
#
# This is the canonical copy. `state` reads it as `be.feature_number`; the rule
# bodies in R-pathguard / R-state-region and the audit scripts are exec'd or
# run in isolation and cannot import, so they carry the same grammar inline
# with a pointer here.
FEATURE_STEM_PREFIX_RE = re.compile(r"^(?:[A-Za-z][A-Za-z0-9]*\s+)?(F\d+)\s+—")
FEATURE_STEM_FUSED_RE = re.compile(r"^[A-Za-z]+(\d+)\s+-\s+")


def feature_number(stem, path=None):
    """Return the bare row handle a document stem names (`F300`, `T287`), or None.

    The fused form has no letter in it — `TINK300 - Title` — so this
    RECONSTRUCTS the identifier rather than matching it. Until 2026-08-19 only
    features used that spelling and reconstructing an `F` was always right.
    T-docs now use it too, and a `HA287 - Soak…` T-doc read back as `F287` sent
    audit-q hunting for a feature that does not exist and reporting the row's
    questions as missing.

    So the letter comes from the document itself when we have it: the H1
    breadcrumb (`# [[HA]] · T287 — Title`) still carries the kind, because the
    fused spelling lives in the filename and nowhere else. With no path to read,
    `F` remains the fallback — that is what every pre-2026-08-19 fused doc is.
    """
    m = FEATURE_STEM_PREFIX_RE.match(stem)
    if m:
        return m.group(1)
    m = FEATURE_STEM_FUSED_RE.match(stem)
    if not m:
        return None
    letter = "F"
    if path is not None:
        try:
            head = pathlib.Path(path).read_text(encoding="utf-8")[:4000]
        except (OSError, UnicodeDecodeError):
            head = ""
        h1 = re.search(rf"^#\s.*·\s*([A-Z])0*{int(m.group(1))}\s+—", head, re.M)
        if h1:
            letter = h1.group(1)
    return letter + m.group(1)

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
    """Highest number for `kind` across the backlog + 1.

    A doc-minting kind (`DOC_MINTING_KINDS`) shares one namespace with the
    other doc-minting kinds, for the reason recorded there: under the F329
    folder form both become `{SLUG}{NNN}` files, and two files cannot share a
    basename. Kept in step with `mint_cross_file_id` — the two allocators must
    agree, or `define` and the `F+`/`T+` path would hand out the same number.
    """
    if kind in RETIRED_KINDS:
        raise BacklogEditError(
            f"'{kind}' is a retired row kind (2026-08-19) — a B row is a task, "
            f"so it is a T. The vault's last 14 were folded into T that day. "
            f"Mint a T instead.")
    kinds = (DOC_MINTING_KINDS if kind in DOC_MINTING_KINDS else (kind,))
    pattern = re.compile(rf"^(?:{'|'.join(re.escape(k) for k in kinds)})(\d+)$")
    nums = []
    for rid in row_index.keys():
        m = pattern.match(rid)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


# --------------------------------------------------------------------------
# Row formatting

# T140 — the `+` is load-bearing. Every other block-ID pattern in this file is
# `\^[\w-]+` (`_q_header_line`, `_append_why_ask_annotation`, `ROW_FULL_RE`),
# and `+` falls outside `[\w-]` — so the mint placeholder `^T+` matched no
# cleanup path that existed, `ROW_FULL_RE` absorbed it into `body`, and it
# became permanent. `.` is admitted for the dotted R-handles (`^R-Sc.5.2`),
# which are sanitized to dashes on write but can arrive dotted. The run is
# repeatable (`(?:…)+`) so a row that already carries several — MED T002 held
# `^T+ ^T002 ^T002` — collapses to one on its next edit rather than shedding a
# single anchor per pass.
_TRAILING_ANCHORS_RE = re.compile(r"(?:\s+\^[\w.+-]+)+\s*$")


def _strip_trailing_anchors(text):
    """`text` minus any run of trailing `^block-id` anchors.

    Guards the one invariant both writers below need: the anchor is appended
    unconditionally, so whatever arrives must not already carry one. A body
    legitimately ending in a block *reference* (`… [[X#^T056]]`, `… X#^T056`)
    is untouched — the pattern requires whitespace before the caret.
    """
    return _TRAILING_ANCHORS_RE.sub("", text or "").rstrip()


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
    body = _strip_trailing_anchors((body or "").strip())
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


def verify_write_landed(lines, row_id, requested):
    """Post-condition (T050): every field the caller ASKED to set now holds it.

    Returns a list of human-readable failures; empty means the write landed.

    A mutation tool that reports success while changing nothing makes every
    "I recorded it" claim unfalsifiable, and the backlog is the project's
    memory. T046 fixed one control-flow path that silently dropped `--next`
    on a Verify-family row; this is the general guarantee, so the next such
    path is caught by the tool rather than by someone noticing months later.

    DELIBERATE DEVIATION from T050's proposed implementation, with the
    measurement that forced it. The row said to compare whole-file bytes
    before/after, and warned that the `<!-- state:backlog XX -->` stamp is
    "rewritten on every call, so whole-file bytes are never actually
    identical" — making a naive byte compare pass vacuously. **That premise
    is false, measured 2026-08-03:** the stamp is a *content hash*
    (`compute_backlog_stamp` sha1s the span with the stamp line excluded),
    so a no-op leaves it unchanged; driving `perform_edit` twice with
    identical arguments produced byte-identical files. A byte compare would
    therefore have worked — and would still have been the wrong design, for
    the row's OTHER reason: an intentional re-touch that sets a field to the
    value it already holds is legitimate and produces zero bytes of change,
    so bytes cannot separate "asked and failed" from "asked and it already
    matched". Checking the post-condition separates them by construction —
    it asks whether the file now says what the caller asked for, which is
    true in the re-touch case and false in the dropped-mutation case.

    Substring rather than equality on title/body/sub-bullets: the write path
    legitimately annotates what it stores (e.g. the `· *why-user:…*` suffix),
    and this guard exists to catch a write that VANISHED, not to police
    normalization. A tighter comparison would hard-fail on benign rewriting,
    and a false hard-error in a tool other agents depend on is worse than
    the silent no-op it replaces.
    """
    failures = []
    want_status = requested.get("status")

    span = _row_span(lines, row_id)
    if want_status == "delete":
        if span is not None:
            failures.append(f"status: asked to delete {row_id}, but the row is still present")
        return failures
    if span is None:
        return [f"{row_id}: row is absent after the write — nothing landed"]

    row_line = lines[span[0]]
    m = ROW_FULL_RE.match(row_line)

    # A row with an EMPTY bracket — `[ ]`, which several parked rows carry —
    # yields `existing_status_for_check == " "`. That is truthy, so the F147
    # `status == "same"` resolution above assigns it, and `want_status` arrives
    # here as whitespace: truthy, not "same", and `.split()[0]` raises
    # IndexError. `state migrate-t` hit this on the first anchor that had one
    # (MUX, 2026-08-28) and died mid-migration. Splitting FIRST and testing the
    # result says what the guard always meant — there is a status family to
    # compare — and skips the check when the caller asked for no bracket.
    want_family = (want_status or "").split()
    if want_family and want_status != "same":
        got = m.group("status") if m else None
        # `[Verify-by 2026-09-01]`, `[Blocked foo]`, `[Done — note]` all carry
        # the family as a prefix; the caller asked for the family.
        if not got or not got.startswith(want_family[0]):
            failures.append(f"status: asked [{want_status}], row reads [{got}]")

    for key, label in (("title", "title"), ("body", "body")):
        want = requested.get(key)
        if want is None or not str(want).strip():
            continue
        got = (m.group(label) or "") if m else ""
        # Compare against what `render_row` WRITES, not against what the caller
        # asked for. It normalizes on the way in — `_strip_trailing_anchors`
        # (T140) removes a trailing `^T+`/`^T007` run — so a raw substring test
        # sees its own writer's output as a non-match, calls a correct write a
        # failure, and reverts the file. That fires on exactly the body T140
        # exists to clean: a caller piping in a row that still carries the mint
        # placeholder gets a hard revert with no hint of why.
        if _strip_trailing_anchors(str(want).strip()) not in got:
            # F332 — a derived (pointer-led) body is normalized on write:
            # display text collapses to `|<row_id>]]` and the trailing line
            # regenerates from the doc. Same link target = the write landed.
            if label == "body" and is_derived_row_body(str(want)) \
                    and is_derived_row_body(got):
                wm = WIKI_LINK_RE.search(str(want))
                gm = WIKI_LINK_RE.search(got)
                if wm and gm and wm.group(1).strip() == gm.group(1).strip():
                    continue
            if "\n" in str(want).strip():
                # A genuine rejection, but the old message named the wrong
                # thing. A row is ONE line; a body carrying a blank line lands
                # its tail below the bullet where the row grammar can't reach
                # it. Say so, rather than "absent from the row line".
                failures.append(
                    f"{label}: multi-line text cannot live on a row line — "
                    f"the text after the first line break lands outside the "
                    f"row. Join it into one paragraph, or put the detail in a "
                    f"`- **Next:**` sub-bullet or a linked doc")
            else:
                failures.append(f"{label}: asked text is absent from the row line")

    for key, label in (("next_text", "Next"), ("verify_text", "Verify"),
                       ("user_text", "User")):
        want = requested.get(key)
        if want is None:
            continue
        got = _row_field(lines, row_id, label)
        # T122 — the landing check must be able to assert an ABSENCE. It only
        # ever asserted that requested text IS present, and skipped anything
        # falsy — so a removal the write path silently declined to perform
        # still passed here and the CLI still printed `updated`. A guard that
        # cannot see a negative cannot catch a discarded one.
        if not str(want).strip():
            if got is not None:
                failures.append(f"{label}: asked to REMOVE it, but {row_id} "
                                f"still carries `- **{label}:** {got[:40]}`")
            continue
        if got is None:
            # F332 — on a derived row the Next never lands as a sub-bullet;
            # it shows as the regenerated derived line on the row itself
            # (written to the doc's `next::` by sync_doc_next).
            if label == "Next" and str(want).strip() in lines[span[0]]:
                continue
            failures.append(f"{label}: asked to set it, but {row_id} has no "
                            f"`- **{label}:**` sub-bullet after the write")
        elif str(want).strip() not in got:
            failures.append(f"{label}: asked {str(want).strip()[:40]!r}, "
                            f"sub-bullet holds {got[:40]!r}")

    return failures


def _row_span(lines, row_id):
    """(start, end) line indices of row_id's block, or None if absent."""
    row_i = None
    for i, line in enumerate(lines):
        rm = ROW_HEADER_RE.match(line)
        if rm and len(rm.group(1)) == 0 and rm.group(2) == row_id:
            row_i = i
            break
    if row_i is None:
        return None
    end = len(lines)
    for j in range(row_i + 1, len(lines)):
        if H2_RE.match(lines[j].rstrip()):
            end = j
            break
        rm = ROW_HEADER_RE.match(lines[j])
        if rm and len(rm.group(1)) == 0:
            end = j
            break
    return (row_i, end)


def _row_field(lines, row_id, label):
    """Text of row_id's `- **<label>:**` sub-bullet, or None if it has none."""
    span = _row_span(lines, row_id)
    if span is None:
        return None
    rx = re.compile(SUBBULLET_RE_TMPL.format(label=label))
    for line in lines[span[0] + 1:span[1]]:
        m = rx.match(line)
        if m:
            return m.group(1).strip()
    return None


def _subbullets_to_write(status, eff_verify, eff_next, eff_user, next_text,
                         verify_text=None, probe_text=None, eff_probe=None,
                         user_text=None, why_user_action=None, why_user=None):
    """Which companion sub-bullets this edit attaches, as `[(label, text), …]`.

    Pure, so the dispatch is pinned by tests instead of living inline in
    `perform_edit` behind a file write (T046).

    **T046 — an EXPLICIT `--next` is honoured whatever the bracket.** This used
    to be one `elif` chain: on a Verify-family row the Verify branch matched and
    the `--next` the caller passed fell off the end, so `state set … --next "…"`
    printed `updated <row>` and changed nothing. Two live victims — F193's Next
    applied only on a retry, after an intervening `--status` had moved the row
    out of Verify; T011's stayed uncorrected, because [Verify] is the CORRECT
    bracket for it and there was no legitimate way to move it just to make an
    edit land. That made the reachable-but-uneditable set *every Verify-horizon
    row*: precisely the rows carrying the user's open verifications. The [User]
    branch had already been given this treatment for the same reason (it writes
    User AND, separately, a queued Next, per F259); this generalises it rather
    than adding a third special case.
    """
    out = []
    wrote_next = False

    # _verify_family (not _status_needs_verify) so a [Verify-by] row's
    # question / F240 why-user annotation lands too instead of being
    # silently dropped.
    if _verify_family(status) and eff_verify:
        out.append(("Verify", eff_verify.strip()))
    elif _status_needs_next(status) and eff_next:
        out.append(("Next", eff_next.strip()))
        wrote_next = True
    elif _status_needs_user(status):
        if eff_user:
            out.append(("User", eff_user.strip()))
        # A [User] row MAY carry a queued `- **Next:**` — the agent's step
        # once the user acts (documentary, not executable-now; F259).
        if eff_next and eff_next.strip():
            out.append(("Next", eff_next.strip()))
            wrote_next = True

    # T056 — a status that doesn't REQUIRE a Next ([Blocked], [Waiting],
    # [Questions], …) may still be handed one explicitly, and a parked row is
    # exactly where the note explaining how to restart it earns its keep.
    # T046 widened this from the tail of the elif chain to an unconditional
    # check, which is what lets it also cover the Verify family above.
    # Gated on `next_text`, not `eff_next`, so an ordinary re-touch does not
    # rewrite (and reorder) a sub-bullet nobody asked to change.
    if not wrote_next and next_text is not None and next_text.strip():
        out.append(("Next", next_text.strip()))

    # T123 → T560 — an EXPLICIT `--verify` is honoured whatever the bracket.
    #
    # T123 opened this for TERMINAL rows only: `_verify_family("Done")` is
    # False, so a row answered and moved to [Done] froze its question at
    # whatever it last said and every later `set --verify` was skipped — a
    # closed row went on vouching for a claim later proven false (MUX F237
    # asserted "there is no log anywhere that ever saw 13", which the agent
    # then disproved, and both lines had to be rewritten by hand outside
    # `state`).
    #
    # The gate was still too narrow, and this is the FOURTH instance of one
    # defect: T046 opened Next to any bracket, T236 opened User to any bracket,
    # and Verify kept a bracket test. [[SCOUT]] hit the remaining hole
    # 2026-08-19 on a `[Waiting 2026-09-20]` row — neither verify-family nor
    # terminal, so `--verify` matched no arm, the CLI printed `updated`, and
    # T050's landing check reverted the file with "the edit reported success
    # but the file does not reflect it". That message reads like a writer bug
    # and is really this dispatch declining to write. A parked soak row is
    # exactly where a Verify question legitimately sits before its date
    # arrives, which is why the bracket was never the right thing to test.
    #
    # Gated on the caller having TOUCHED the field — `verify_text`, or
    # `why_user`, which rewrites the trailer on it (T593, the T236 shape) —
    # never on `eff_verify`, for the T056 reason the blocks around it share: an ordinary re-touch must not rewrite — and thereby
    # reorder, since `_ensure_subbullet` re-inserts directly under the row
    # line — a sub-bullet nobody asked to change. What it WRITES is
    # `eff_verify`, never the raw text, so the `· *why-user: …*` trailer the
    # F240 gate folded in is not silently dropped (the T236 correction, which
    # T123's raw-`verify_text` write predated).
    wrote_verify = any(lbl == "Verify" for lbl, _ in out)
    verify_touched = (verify_text is not None and verify_text.strip()) or (
        why_user is not None and why_user.strip())
    if (not wrote_verify and verify_touched
            and eff_verify and eff_verify.strip()):
        out.append(("Verify", eff_verify.strip()))

    # T236 — an EXPLICIT `--user` is honoured whatever the bracket. This is the
    # THIRD instance of one defect: T046 fixed it for Next, T123 for Verify, and
    # the [User] arm above kept the original shape, so a row not bracketed
    # [User] could not have its `- **User:**` line rewritten at all. `state set`
    # printed `updated`, changed nothing, and T050's landing check then reverted
    # the file and reported "the edit reported success but the file does not
    # reflect it" — which reads like a writer bug and is really this dispatch
    # declining to write.
    #
    # A row legitimately carries a User action while parked on some other
    # bracket: Sonar hit this 2026-08-17 on `SONAR Backlog` T031, a
    # [Waiting 2026-09-01] row whose user action Dan had just given a send-by
    # date. `--status` alone landed, `--user` could not, so the row's bracket
    # and its own User line disagreed with nothing able to reconcile them.
    #
    # Fires only when the caller explicitly touched the field — via `--user` or
    # via `--why-user-action`, which rewrites the trailer on it — for the T056
    # reason the two blocks above apply: an ordinary re-touch must not rewrite
    # (and thereby reorder) a sub-bullet nobody asked to change. What it WRITES
    # is `eff_user`, never the raw `user_text`: the gate above has already
    # folded the `· *why-user-action: …*` trailer into `eff_user`, so writing
    # the raw text back would silently drop the annotation it just computed.
    wrote_user = any(lbl == "User" for lbl, _ in out)
    user_touched = (user_text is not None and user_text.strip()) or (
        why_user_action is not None and why_user_action.strip())
    if not wrote_user and user_touched and eff_user and eff_user.strip():
        out.append(("User", eff_user.strip()))

    # T122 — an explicitly EMPTY flag REMOVES the sub-bullet (text `None`).
    #
    # `perform_edit` already distinguishes the three states — `eff_x = x if x is
    # not None else existing_x` — so `""` reaches here only when the caller
    # passed an empty flag, and its comment already promised "the provided flag
    # wins". It did not: every branch above gates on `and eff_x`, so an empty
    # string fell through, the line on disk stayed, and the CLI printed
    # `updated`. That is T056's defect class (an accepted argument reported as
    # applied and discarded) in the one direction T056 did not cover.
    #
    # Unconditional rather than another arm of the chain, because the case that
    # needs it is a Verify on a bracket that does NOT require one — a WITHDRAWN
    # check, not a deferred one (F275, whose user-facing question Dan cancelled
    # while the row sat [Waiting]). `_verify_family("Waiting")` is False, so no
    # status branch would ever reach it.
    #
    # Removing a sub-bullet the bracket REQUIRES needs no guard here: the F171
    # gates in `perform_edit` raise on a falsy `eff_verify`/`eff_next`/
    # `eff_user` before this function is reached, so a removal can only ever
    # land on a bracket that does not demand the line.
    # No "don't remove what an arm just wrote" guard, deliberately: an arm
    # writes a label only when its `eff` is truthy, and a removal fires only
    # when that same `eff` is exactly `""`, so the two can never name the same
    # label. The [User] arm is the case worth checking — it writes User AND
    # Next from two different values, and `--user "step" --next ""` correctly
    # writes the one and removes the other.
    # F305 Q2 — the `- **Probe:**` field: the agent-owned deferred check and
    # its trigger. No bracket ever requires it and no bracket forbids it — the
    # bracket says only WHEN the row is parked; the field says what happens
    # when it is not. So it is written exactly when explicitly passed, on any
    # bracket (the T056 pattern), and never rewritten on a re-touch.
    if probe_text is not None and probe_text.strip():
        out.append(("Probe", probe_text.strip()))

    for label, eff in (("Verify", eff_verify), ("Next", eff_next),
                       ("User", eff_user), ("Probe", eff_probe)):
        if eff == "":
            out.append((label, None))

    return out


def _ensure_subbullet(lines, row_id, label, text):
    """Mutate `lines` in place: under row_id's line, drop any existing
    `- **<label>:**` sub-bullet and insert `  - **<label>:** <text>` directly
    after the row line (so it survives horizon-moves, which drop the span).

    **`text=None` removes it** (T122) — the drop already happened on the way to
    the re-insert, so removal is this function minus its last step rather than a
    second traversal."""
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
    if text is not None:
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


def _hosted_pending_items(backlog_path, body, letters):
    """F305 hosting — pending doc-hosted items of the given kinds (`V`/`U`)
    in the row's arrow-linked feature doc, as ['V1', …], or [].

    This is what lets a `[Verify]` row whose check lives in its DOC (the
    hosting design's home for it) satisfy the F171 companion-sub-bullet
    requirement without duplicating the question onto the row — the split
    F305 D1 exists to remove. Resolution is anchor-local: the two canonical
    Features folders under the backlog's anchor root."""
    m = re.search(r"→\s+\[\[([^\]#|]+)", body or "")
    if not m:
        return []
    stem = m.group(1).strip()
    anchor_root = anchor_track_dir(backlog_path).parent
    hits = []
    # Both the flat form (`Features/X.md`) and the folder-doc upgrade
    # (`Features/X/X.md`, optionally carrying its own `.anchor`) are one doc.
    for pat in (f"* Design/* Features/{stem}.md",
                f"* Track/* Features/{stem}.md",
                f"* Design/* Features/{stem}/{stem}.md",
                f"* Track/* Features/{stem}/{stem}.md",
                # F331/F596 proj — root-level `{slug} Proj/` (legacy `{slug} Subs/`), folder-doc form.
                f"* Proj/{stem}/{stem}.md",
                f"* Proj/{stem}.md",
                f"* Subs/{stem}/{stem}.md",
                f"* Subs/{stem}.md",
                # F329 — T-docs live directly in the folder-form backlog
                # (`{slug} Track/{slug} Backlog/{SLUG} T<n> - Title.md`).
                f"* Track/* Backlog/{stem}.md",
                f"* Plan/* Backlog/{stem}.md"):
        try:
            hits.extend(anchor_root.glob(pat))
        except (OSError, ValueError):
            pass
    if not hits:
        return []
    try:
        doc_lines = hits[0].read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    out = []
    in_block = False
    for ln in doc_lines:
        s = ln.strip()
        if s in ("## Open Items", "## Open Questions"):
            in_block = True
            continue
        if in_block and (s.startswith("## ")
                         or s in ("### Resolved", "### Removed")):
            break
        if in_block:
            mm = _ITEM_HEADER_BULLET_RE.match(ln)
            if mm and mm.group(2) in letters:
                out.append(mm.group(2) + mm.group(3))
    return out


def _refuse_multiline_subbullets(verify_text, next_text, user_text,
                                 probe_text=None):
    """T128 — a sub-bullet is ONE line; refuse a value that cannot be one.

    `_ensure_subbullet` writes `f"  - **{label}:** {text}\\n"` with no check that
    `text` is single-line. A value carrying a newline — trivially easy, since
    `--next "$(cat file)"` preserves internal newlines and any appended-to file
    has one — put its tail on an **orphan line** that belongs to no sub-bullet,
    sits inside the row's span, and is invisible to `_row_field`. audit-q
    reported 0 findings over the corrupted row, so nothing downstream caught it
    either.

    Refuse rather than repair. Silently joining would be a fallback: a caller
    who passed two paragraphs meant two paragraphs, and should be told the field
    cannot hold them rather than handed a mangled single line they did not ask
    for. The message names the fix, since the caller's next move is to collapse
    the value or put the long form in the row body.
    """
    for flag, text in (("--verify", verify_text), ("--next", next_text),
                       ("--user", user_text), ("--probe", probe_text)):
        if text is None or "\n" not in str(text):
            continue
        head = str(text).split("\n", 1)[0].strip()
        raise BacklogEditError(
            f"{flag}: the value spans {str(text).count(chr(10)) + 1} lines, and "
            f"a sub-bullet is one line by construction — the tail would land as "
            f"an orphan line inside the row that no reader can see.\n"
            f"  First line: {head[:80]}{'…' if len(head) > 80 else ''}\n"
            f"  Collapse it to a single line, or put the long form in the row "
            f"body (`--body`) and leave the sub-bullet a pointer.")


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
    probe_text=None,
):
    """Apply the edit, return a one-line summary for the Messages entry."""
    _refuse_multiline_subbullets(verify_text, next_text, user_text, probe_text)

    raw = backlog_path.read_text()
    lines, h2_index, row_index = scan_backlog(raw)

    kind, rest = parse_row_id(row_id_arg)

    # Resolve the actual row_id (mint if requested).
    if rest is None:
        # Mint a new id.
        # `T` is the default for anything that is not a feature. It used to be
        # `B`, but B rows were folded into T on 2026-08-19 and the kind is
        # retired — minting one here would quietly resurrect it.
        mint_kind = "F" if kind == "F" else "T"
        new_num = next_id_for_kind(row_index, mint_kind)
        row_id = format_row_id(mint_kind, new_num)
        existing = None
    else:
        row_id = f"{kind}{rest}"
        existing = row_index.get(row_id)

    # F171 companion-sub-bullet discipline: capture any existing Verify:/Next:
    # sub-bullet text so it survives a horizon-move (which drops the row span),
    # and so a same-status re-touch isn't forced to re-supply it.
    existing_verify = existing_next = existing_user = existing_probe = None
    old_span = None  # F329 gate input — the row's pre-edit sub-bullet span
    if existing is not None:
        _es, _ee = existing[0], existing[1]
        _span = lines[_es:_ee]
        old_span = list(_span)
        existing_verify = _extract_subbullet_text(_span, "Verify")
        existing_next = _extract_subbullet_text(_span, "Next")
        existing_user = _extract_subbullet_text(_span, "User")
        existing_probe = _extract_subbullet_text(_span, "Probe")

    # F329 — new standalone Q-rows are retired: a question is a doc (T-doc or
    # feature doc), never a backlog row. Existing F275 Q-rows stay addressable
    # (edit/resolve/delete) until they migrate on touch.
    if kind == "Q" and existing is None and status != "delete":
        raise BacklogEditError(
            "new standalone Q-rows are retired (F329) — questions live in "
            "docs. Mint a T-row plus a T-doc (`{SLUG} T<n> - <Title>.md` in "
            "the folder-form backlog `<slug> Track/<slug> Backlog/`) holding "
            "the question in its stamped `## Open Questions` block."
        )

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
        write_backlog_lines(backlog_path, lines)
        # T050 — same post-condition guarantee as the main write path below:
        # a delete that reported success must have actually removed the row.
        gone = verify_write_landed(
            backlog_path.read_text().splitlines(keepends=True),
            row_id, {"status": "delete"})
        if gone:
            # T128 — roll back, same as the main write path. A half-applied
            # delete is the worst failure this file can hold.
            backlog_path.write_text(raw, encoding="utf-8")
            raise BacklogEditError(
                f"{row_id}: delete reported success but " + "; ".join(gone)
                + ". The file was restored to its pre-edit contents.")
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
    status_unchanged = False
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
                f"[status] bracket) — refusing to edit and wipe its content. A "
                f"state-owned backlog is never hand-edited (T621): run `state remove "
                f"<anchor> Backlog {row_id}`, which prints the row's markdown, then "
                f"`state define <anchor> Backlog {row_id}` with that text in canonical "
                f"shape (`- **{row_id} — Title** [Status] — body`). Copy the printed row "
                f"before the define — a define gate refusing leaves the row removed and "
                f"not yet restored."
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
        # real status (e.g. a body-only `state set` losing [Designing]).
        if status == "same" and existing_status_for_check:
            # F305 — remember that the caller did NOT ask for a bracket change,
            # so `watch_grammar_gate` can stay off a row it is not touching.
            status_unchanged = True
            status = existing_status_for_check

    # ---- BRACKET GRAMMAR RUNS FIRST -------------------------------------
    # A structural error outranks a content error, so the shape of the bracket
    # is settled before anything asks what the row SAYS. Moved above the
    # Questions/verify constraints 2026-08-13 (F305) after `--status
    # "Watching 7d"` was refused by the F240 verify gate for *lacking a
    # concrete question* — true, but not the reason it was going to be
    # rejected, and not the error the author needed to read. Same principle as
    # F312 Q6's `topo_order`-before-collision ordering: report the error that
    # makes the others meaningless. Neither gate's verdict changes, only which
    # one an author is told about first.

    # F283 — bare `[Blocked]` is illegal; it must name the row it waits on.
    # Checked on any write that sets the bracket, so a pre-existing bare
    # [Blocked] is corrected the first time anything touches it.
    if status not in ("same", "delete"):
        blocked_grammar_gate(status, row_id)
        # F305 — a deferral must say when to look again. Same write-moment
        # placement and the same reason: a structural refusal beats one more
        # rule to remember. Unlike that gate it fires ONLY on a bracket the
        # caller actually asked for — see watch_grammar_gate's docstring for
        # the measurement that forced the narrowing.
        if not status_unchanged:
            watch_grammar_gate(status, row_id)

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
    eff_probe = probe_text if probe_text is not None else existing_probe
    # The arrow link a hosted-item check needs lives on the row's HEADER line
    # (the existing body), which `body_for_check` does not carry on a
    # flag-only `set` touch — include it.
    _host_src = body_for_check
    if existing is not None:
        _host_src = lines[existing[0]] + "\n" + _host_src

    # F332 — the doc owns the Next: an explicit --next mirrors into the
    # arrow-linked doc's `next::` field (best effort; rows without a doc
    # keep their row-only Next until the F329 migration reaches them).
    if next_text is not None and status != "delete":
        sync_doc_next(_host_src, next_text)
    # F332 — derived rows: when the row's doc carries a `next::` field, the
    # doc satisfies the Ready/Active Next requirement and no row sub-bullet
    # is materialized — the regenerated derived line shows it instead.
    next_from_doc = False
    if (status not in ("same", "delete") and _status_needs_next(status)
            and not (eff_next and eff_next.strip())):
        _doc_next = read_doc_next(arrow_doc_path(_host_src))
        if _doc_next:
            eff_next = _doc_next
            next_from_doc = True
    # T237 — a `- **Probe:**` satisfies the concrete-check requirement on a
    # [Watching*] row, for BOTH gates below. F305 Q2 and [[DAS Backlog]]
    # § "There is no bracket for an agent-owned deferred check" say a
    # [Watching {date}] row whose check is agent-runnable carries a Probe and
    # deliberately NOT a Verify — a Verify on a Watching row renders into
    # `## Verifications`, putting a check in front of the user that is by
    # design invisible to them. Two separate refusals contradicted that spec on
    # precisely the shape it exists for: the concrete-question check here, and
    # the F240 ownership gate below, which demanded `--why-user` naming the
    # human faculty a check with no human in it supposedly invokes.
    #
    # Scoped to Watching: a [Verify*] row's whole point IS the human question,
    # and a Probe must never stand in for one there.
    #
    # `define` carries the body's companion sub-bullets in `pending_subs`
    # rather than in the flags — the refusal text itself says define "reads the
    # promise from the body, not from the flag" — so a Probe written into the
    # body counts too, or the verb the spec tells you to use is the one verb
    # that cannot express the shape. (Atticus hit exactly that, 2026-08-17.)
    _probe_satisfies = (status or "").strip().startswith("Watching") and bool(
        (eff_probe and eff_probe.strip())
        or (probe_text and probe_text.strip())
        or any(re.match(r"\s*-\s+\*\*Probe:\*\*\s*\S", s or "")
               for s in (pending_subs or [])))
    if status not in ("same", "delete"):
        if (_status_needs_verify(status)
                and not (eff_verify and eff_verify.strip())
                and not _probe_satisfies
                and not _hosted_pending_items(backlog_path, _host_src, ("Q",))):
            raise BacklogEditError(
                f"[{status}] refused: {row_id} needs a concrete yes/no question. "
                f"On `set`, pass --verify \"<question>\" (e.g. \"Since <date>, has "
                f"<bad thing> recurred? no = held\"); on `define`, put it in the body "
                f"as a `- **Verify:** <question>` sub-bullet — `define` reads the "
                f"promise from the body, not from the flag. Setting a Watching/Verify "
                f"bracket without "
                f"its `- **Verify:**` sub-bullet renders `⚠ no concrete question` "
                f"and is flagged by audit-q C41. If the check is AGENT-runnable "
                f"rather than a user question, this is a [Watching {{date}}] row "
                f"with a `- **Probe:**` (F305 Q2) — pass --probe instead, and it "
                f"renders nowhere the user sees. If there is genuinely no check "
                f"at all, promote to [Done] or rebracket to [Blocked]/[Waiting]."
            )
        if _status_needs_next(status) and not (eff_next and eff_next.strip()):
            raise BacklogEditError(
                f"[{status}] refused: {row_id} needs a no-user next action. "
                f"On `set`, pass --next \"<action>\"; on `define`, put it in the body "
                f"as a `- **Next:** <action>` sub-bullet — `define` reads the promise "
                f"from the body, not from the flag. Setting a Ready/Active bracket "
                f"without "
                f"its `- **Next:**` sub-bullet renders `⚠ none declared — not really "
                f"Ready` and is flagged by audit-q C41. If the next step needs the "
                f"user, rebracket ([Verify] for a user check, [Blocked]/[Questions] "
                f"for a decision)."
            )
        if _status_needs_user(status) and not (eff_user and eff_user.strip()):
            raise BacklogEditError(
                f"[{status}] refused: {row_id} needs a `- **User:**` action. "
                f"On `set`, pass --user \"<action>\" naming exactly what YOU (the "
                f"user) must do (e.g. \"Log into Hoare at <url> so the sync token "
                f"refreshes\"); on `define`, put it in the body as a "
                f"`- **User:** <action>` sub-bullet — `define` reads the promise "
                f"from the body, not from the flag. "
                f"A [User] bracket without its `- **User:**` sub-bullet renders `⚠` "
                f"and is flagged by audit-q C51. If the action is something the "
                f"agent can do, use [Ready] with a `- **Next:**` instead."
            )

    # F240 — verification ownership gate. Fires when the row ENTERS the
    # Verify/Verify-by/Watching family or its question is (re)written; a
    # same-family re-touch keeps the vetting it got at entry.
    if (status not in ("same", "delete") and _verify_family(status)
            and not _probe_satisfies):
        entering = not _verify_family(existing_status_for_check)
        if entering or verify_text is not None or (why_user and why_user.strip()):
            # F305 hosting — a doc-hosted V was vetted at its OWN mint
            # (`define <doc> V+` runs this same F240 gate); when the row
            # carries no question of its own, demanding --why-user again at
            # the bracket would be a second vetting of a vetted check.
            _hosted_v = (not (eff_verify and eff_verify.strip())
                         and verify_text is None
                         and _hosted_pending_items(
                             backlog_path, _host_src, ("Q",)))
            if not _hosted_v:
                eff_verify = verify_ownership_gate(
                    status, row_id, eff_verify, why_user
                )
    elif (status != "delete" and eff_verify
            and why_user and why_user.strip()):
        # T593 — a row NOT in the Verify family may still carry a Verify
        # question (a parked [Waiting] soak row holds it before its date
        # arrives — the T560 shape), and its why-user trailer has to be
        # reachable. The F240 REFUSAL stays scoped to rows entering the
        # family; rewriting the annotation here is just an edit, and without
        # this branch --why-user was accepted, threaded, and dropped — wiping
        # any trailer the row already carried in the same write.
        eff_verify = (_WHY_USER_RE.sub("", eff_verify).strip()
                      + f" · *why-user: {why_user.strip()}*").strip()

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
    elif (status != "delete" and eff_user
            and why_user_action and why_user_action.strip()):
        # T236 — a row NOT bracketed [User] may still carry a User action, and
        # its trailer has to be reachable. The F259 REFUSAL stays scoped to rows
        # entering [User] (that is the gate on honest delegation), but rewriting
        # the annotation on an already-vetted row is just an edit, and without
        # this branch it was the one edit no flag combination could make.
        eff_user = (_WHY_USER_ACTION_RE.sub("", eff_user).strip()
                    + f" · *why-user-action: {why_user_action.strip()}*").strip()

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
            #
            # T122 — read "create-or-REPLACE" narrowly: it is keyed on
            # `pending_subs`, which `state define` fills with the LEFTOVER subs
            # only. It lifts `- **Next:**` / `- **Verify:**` / `- **User:**` out
            # into their own arguments first, so a row whose only sub-bullets
            # are the companion trio arrives here with `pending_subs == []` and
            # takes the preserve branch. A companion the body OMITS is therefore
            # kept, not dropped — `define` does not remove one. That is
            # deliberate, not an oversight to "fix": making omission mean
            # deletion would silently discard a Next whenever an agent
            # re-defines a row to reword its body. The sanctioned removal is
            # explicit — `state set <row> --verify ""` — which is the direction
            # `_subbullets_to_write` was taught.
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
        for label, text in _subbullets_to_write(
            status, eff_verify, eff_next, eff_user, next_text, verify_text,
            probe_text, eff_probe, user_text, why_user_action, why_user
        ):
            # F332 — a Next satisfied by the doc's `next::` never lands as a
            # row sub-bullet (removals, text=None, still apply).
            if label == "Next" and next_from_doc and text is not None:
                continue
            _ensure_subbullet(lines, row_id, label, text)

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

    # F329 — refuse a write that ADDS a pending inline `- **Q<n>` sub-bullet
    # to the row (questions live in docs; legacy inline Qs migrate on touch).
    # Compared by Q-number over the rescanned span, so reworded or resolved
    # existing questions pass and only genuinely new numbers refuse.
    if status != "delete":
        _, _, new_row_index = scan_backlog("".join(lines))
        placed = new_row_index.get(row_id)
        if placed is not None:
            f329_refuse_new_inline_qs(
                row_id, old_span, lines[placed[0]:placed[1]],
                slug=backlog_path.stem[:-len(" Backlog")],
            )

    # F332 — a pointer-led (derived) row's trailing line regenerates from its
    # doc on every touch: `→ [[doc|<id>]] — <next:: | description | orientation>`.
    # This is also the on-touch migration: any doc-backed row whose body leads
    # with the pointer collapses to the canonical pure-link form here.
    if status != "delete":
        _refuse_body_discarded_on_derived_row(lines, row_id, body, body_provided)
        regenerate_derived_row(lines, row_id)

    # T128 — hold the pre-edit bytes so a failed post-condition can be UNDONE.
    # `raw` is what `perform_edit` read at entry, before any mutation.
    before = raw

    write_backlog_lines(backlog_path, lines)

    # T050 — the write must be provably on DISK before we report success.
    # Re-read rather than re-inspect `lines`: the in-memory list is what we
    # believe we wrote, and a guard that consults our own belief cannot catch
    # a write that didn't land. Raises, so the caller exits non-zero.
    landed = verify_write_landed(
        backlog_path.read_text().splitlines(keepends=True),
        row_id,
        {
            "status": status,
            "title": title if title_provided else None,
            "body": body if body_provided else None,
            "next_text": next_text,
            "verify_text": verify_text,
            "user_text": user_text,
        },
    )
    if landed:
        # T128 — roll back before raising. The guard ran AFTER an unconditional
        # write with no undo, so `state` correctly reported failure over a file
        # it had already corrupted; the operator read "the write did not land"
        # and committed the damage. A guard that can report but not protect is
        # half a guard. The disk re-read above is kept deliberately (T050's
        # reason stands — a guard consulting our own belief cannot catch a write
        # that didn't land), so the rollback is what makes failure clean rather
        # than moving the check in-memory.
        restored = ""
        try:
            backlog_path.write_text(before, encoding="utf-8")
            restored = " The file was restored to its pre-edit contents."
        except OSError as exc:
            restored = (f" WARNING: the rollback ALSO failed ({exc}) — the file "
                        f"is left mid-edit and needs manual repair.")
        raise BacklogEditError(
            f"{row_id}: the edit reported success but the file does not "
            f"reflect it — " + "; ".join(landed) + "." + restored
        )

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

def _is_facet_spec(path):
    """True when `path` is a facet SPEC rather than a per-anchor instance.

    A `facets/DAS <Name>.md` is the specification for the `<Name>` facet — the
    document that defines what a Backlog or a Messages file IS. It is not an
    anchor's queue or an anchor's inbox, and appending a notification to it
    edits the standard instead of recording an event against a project.

    This exemption is already declared, twice: `R-backlog` and `R-messages`
    both carry `where:: …, !**/DAS *.md` with the note "a `DAS <Name>.md` is
    the SPEC for the facet, not an instance; specs are governed by
    `R-facet-spec`". The rules honoured it; this write site did not, so
    `state`-driven edits to `facets/DAS Backlog.md` appended INFO lines into
    `facets/DAS Messages.md` — the Messages facet spec (Warden F235; SKA F243
    MS-2 had to strip 16 of them by hand, and 4 more accumulated after).
    """
    return path.parent.name == "facets" and path.name.startswith("DAS ")


# A Messages log is append-only and nothing ever drained it, so every one grew
# without bound until Obsidian started refusing to index them (TINK T234:
# "Indexing taking a long time for … Tink Messages.md", at 751 KB / ~21 KB per
# day). The cap keeps the tail and archives the head — NOT a clear. DAS Messages
# is explicit that "a cleared log nothing reads is the same dead channel,
# emptier", so the history moves to a gzip beside the file, where it is still
# readable but invisible to Obsidian's indexer.
#
# Hysteresis is the point of having two numbers: rotating at exactly KEEP would
# rewrite the whole file on every single append once it filled. Rotating only
# above HIGH means one rewrite per (HIGH - KEEP) appends.
MESSAGES_KEEP = 300      # entries retained in the live file (~31 KB, measured)
MESSAGES_HIGH = 500      # rotate only once the file exceeds this


def _messages_header(slug):
    # The corpus decides this line, not this function. Measured 2026-08-12
    # (F303): 38 of the vault's 44 `* Messages.md` files carry the sentence
    # below, and exactly ONE carried the string this branch used to write — so
    # the creator was minting a form nothing else in the vault uses, and a
    # template mirroring it faithfully documented a corpus of one. Aligning the
    # writer costs a line; sweeping 38 append-only files that agents write to
    # constantly does not. `{slug}` is deliberately absent from the description:
    # the 38 do not name their own anchor there, and the file's H1 already does.
    return (
        "---\n"
        "description: agent inbox — background-process messages for this "
        "anchor; append-only. See [[DAS Messages]].\n"
        "---\n"
        f"\n# {slug} Messages\n"
        # The orientation line is not decoration: R-spine-02 requires a single
        # line under the H1 followed by a blank, and without it the first LOG
        # line becomes the orientation line and trips the rule against every
        # entry that follows it. Only 2 of the vault's 44 instances had one
        # (measured 2026-08-17), which is why the rest fire on every write.
        f"Agent inbox for {slug} — machine-written notices from background "
        f"processes; append-only. See [[DAS Messages]].\n\n"
    )


ENTRY_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2})[ T]")


def _rotate_messages(messages_path, slug):
    """Archive all but the last MESSAGES_KEEP entries into a gzip sibling.

    Returns silently when the file is under the high-water mark. Any failure is
    reported to stderr and swallowed: the message itself is already written, and
    losing the rotation is not worth failing the state mutation that triggered it.
    """
    try:
        lines = messages_path.read_text().splitlines(keepends=True)
        entries = [ln for ln in lines if ENTRY_RE.match(ln)]
        if len(entries) <= MESSAGES_HIGH:
            return
        cut = len(entries) - MESSAGES_KEEP
        archived, kept = entries[:cut], entries[cut:]

        def day(line):
            m = ENTRY_RE.match(line)
            return m.group(1) if m else "unknown"

        # Fold into the anchor's existing archive when there is one, so an anchor
        # accumulates ONE archive rather than a shelf of fragments. gzip members
        # concatenate legally and Python's reader spans them, so this appends
        # without decompressing what is already there; only the name widens.
        prior = sorted(messages_path.parent.glob(f"{slug} Messages * to *.md.gz"))
        target = prior[0] if prior else None
        first = day(archived[0])
        if target:
            m = re.search(r" (\d{4}-\d{2}-\d{2}) to ", target.name)
            if m:
                first = m.group(1)
        archive = messages_path.parent / f"{slug} Messages {first} to {day(archived[-1])}.md.gz"
        with gzip.GzipFile(filename=str(target or archive), mode="ab") as gz:
            gz.write("".join(archived).encode())
        if target and target != archive:
            target.rename(archive)

        # Rebuild the live file. The header is re-emitted rather than preserved:
        # the 2026-08-17 hand-rotation dropped frontmatter and H1 from the four
        # files it touched, so re-emitting heals those on their next rotation.
        head = [ln for ln in lines if not ENTRY_RE.match(ln)]
        header = "".join(head) if any(ln.startswith("# ") for ln in head) else _messages_header(slug)
        messages_path.write_text(header.rstrip("\n") + "\n\n" + "".join(kept))
    except Exception as e:                                   # noqa: BLE001
        print(f"backlog-edit: could not rotate {messages_path.name}: {e}", file=sys.stderr)


def append_messages(slug, summary, backlog_path):
    """Write a global-sentinel entry and a per-anchor Messages.md entry."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rel = backlog_path.relative_to(VAULT_ROOT) if backlog_path.is_relative_to(VAULT_ROOT) else backlog_path
    line = f"[{now}] [INFO] {slug}: {summary} (at {rel})\n"

    # Global sentinel — prefixed with slug for cross-anchor disambiguation.
    # The sentinel is a flat event log, not a governed document, so a facet-spec
    # edit is still recorded here; only the document append is suppressed.
    SENTINEL.parent.mkdir(parents=True, exist_ok=True)
    with SENTINEL.open("a") as f:
        f.write(f"[{slug}] {line}")

    # Per-anchor messages file.
    track_dir = anchor_track_dir(backlog_path)
    messages_path = track_dir / f"{slug} Messages.md"
    if _is_facet_spec(backlog_path) or _is_facet_spec(messages_path):
        return
    if not messages_path.exists():
        messages_path.write_text(_messages_header(slug))
        _selffire(messages_path)
    with messages_path.open("a") as f:
        f.write(line)
    _rotate_messages(messages_path, slug)


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


# The kinds whose rows become a FILE named `{SLUG}{NNN}` under the F329 folder
# form. They share ONE number namespace, because two files cannot carry the
# same basename in this vault and `{SLUG}{NNN}` drops the letter that used to
# tell them apart — so `F010` and `T010` in one anchor would both want
# `SV010.md`. Dan, 2026-08-19: *"both of them should just have the slug
# followed by the number, without the letter F or T. So we need to keep those
# distinct."*
#
# `B` is deliberately NOT here, but not because it is safe — because it is
# RETIRED. Dan, 2026-08-19: *"B really gets renamed to T, because those are
# tasks, and Qs get renamed to T."* All 14 B rows and 7 standalone Q rows in the
# vault were folded into T that day and none remain, so the only thing a fresh
# B mint could do is reintroduce a kind the model no longer has. `RETIRED_KINDS`
# below refuses it. `Q`/`V`/`U` survive as doc-HOSTED items numbered inside
# their host (see `_next_item_number`) — the retirement is of the standalone
# ROW, not of questions.
DOC_MINTING_KINDS = ("F", "T")
# `Q` is NOT listed here even though standalone Q rows are equally retired: the
# F329 gate already refuses `Backlog Q+` with a message that says WHY (questions
# live in documents) and names where to put it instead. A second, vaguer refusal
# firing first would replace a good error with a worse one.
RETIRED_KINDS = ("B",)


def mint_cross_file_id(backlog_path, icebox_path, kind):
    """Compute the next number for `kind` across BOTH backlog and icebox.

    Per [[DAS Backlog]] § Icebox interaction: 'F-number namespace is shared
    across backlog AND icebox — no F-number collisions; an item moving
    between the two keeps its F-number.' Same for B-numbers.

    **And for a doc-minting kind the namespace is shared across KINDS too**
    (`DOC_MINTING_KINDS` above), so an anchor's F and T numbers interleave
    rather than running as two independent sequences that collide the moment
    both become `{SLUG}{NNN}` files. The high-water is taken over every
    doc-minting kind at once; a non-doc kind keeps its own counter.
    """
    # F250 #3 — recognize rows via scan_backlog (ROW_HEADER_RE), which sees
    # TITLE-LESS rows (`- **T002** [Done]`) as well as titled ones. The old
    # em-dash-anchored regex (`\*\*{kind}(\d+)\s+—`) skipped title-less rows, so
    # the max-scan could return an already-in-use number and `define`'s
    # create-or-replace would then OVERWRITE that live row. Aligns the mint with
    # next_id_for_kind / ROW_HEADER_RE.
    if kind in RETIRED_KINDS:
        raise BacklogEditError(
            f"'{kind}' is a retired row kind (2026-08-19) — a B row is a task, "
            f"so it is a T. The vault's last 14 were folded into T that day. "
            f"Mint a T instead.")
    kinds = (DOC_MINTING_KINDS if kind in DOC_MINTING_KINDS else (kind,))
    id_re = re.compile(rf"^(?:{'|'.join(re.escape(k) for k in kinds)})(\d+)$")
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
            f"full line can't be parsed — usually a missing `[status]` bracket) — "
            f"refusing to move it and lose its content. A state-owned backlog is "
            f"never hand-edited (T621): run `state remove <anchor> Backlog {row_id}`, "
            f"which prints the row's markdown, then `state define <anchor> Backlog "
            f"{row_id}` with that text in canonical shape (`- **{row_id} — Title** "
            f"[Status] — body`). Copy the printed row before the define — a define "
            f"gate refusing leaves the row removed and not yet restored."
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
    track_dir = anchor_track_dir(backlog_path)  # {slug} Track/ (folder-doc aware, F329)
    anchor_root = track_dir.parent           # anchor docs root (Design/Track siblings)
    return [
        anchor_root / f"{slug} Design" / f"{slug} Features",  # new canonical
        track_dir / f"{slug} Features",                       # legacy sibling
        anchor_root / f"{slug} Features",                     # older flat variant
        anchor_root / f"{slug} Proj",                          # F596 proj
        anchor_root / f"{slug} Subs",                          # F331 subs (legacy)
        track_dir / f"{slug} Backlog",                         # F329 T-docs
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
        # Folder-doc form: `F015 — Title/F015 — Title.md`.
        matches.extend(p for p in d.glob(f"{row_id} — */{row_id} — *.md")
                       if p.stem == p.parent.name)
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

# F305 hosting pass — the open-items block hosts three answer shapes, keyed by
# letter: Q (choose), V (observe, yes/no), U (perform, done). One lifecycle,
# one block, per-letter monotonic numbering. These kind-blind forms match any
# hosted item; the Q-named regexes above stay for the Q-specific paths.
ITEM_KINDS = ("Q",)
_ITEM_HEADER_BULLET_RE = re.compile(r"^(\s*)- \*\*(Q)(\d+)\b")
_ITEM_HEADER_H3_RE = re.compile(r"^(\s*)### (Q)(\d+)\b")


def _item_bullet_re(letter):
    """Header-bullet regex for one item kind — group(1) indent, group(2) num."""
    return re.compile(rf"^(\s*)- \*\*{letter}(\d+)\b")


def _item_h3_re(letter):
    return re.compile(rf"^(\s*)### {letter}(\d+)\b")


def _next_q_number(doc_text):
    """One above the HIGH-WATER Q-number across pending bullets + ### Resolved
    + bottom ## Resolved + ### Removed sub-sections. Per F128 § Q-numbering
    policy, tightened to monotonic-per-document by F291.

    Was lowest-unused, which recycles a number as soon as its block migrates.
    That is unsafe now that a migrated entry keeps its `^F<n>-Q<n>` block-ID
    (F291 § Migration): a recycled Q1 puts that anchor in the file TWICE, and
    Obsidian block-IDs are unique per file — `[[F283#^F283-Q1]]` then resolves
    to whichever one it picks. Nothing would catch it; there is no duplicate-
    block-ID check anywhere in audit, so the collision is silent and surfaces
    later as a link landing on the wrong decision. Monotonic also aligns
    Q-numbers with the F-number policy in [[DAS Backlog]] § Numbering policy —
    two rules for two identifiers that behave identically is a trap.

    The scan is already document-wide: `_Q_HEADER_H3_RE` matches the `### Q<n>`
    entries in the bottom `## Resolved`, so a migrated round raises the mark.
    """
    return _next_item_number(doc_text, "Q")


def _next_item_number(doc_text, letter):
    """Per-letter high-water + 1 — the F291 monotonic policy, one namespace
    per item kind (Q/V/U), so `V1` and `Q1` coexist in one doc without either
    recycling the other's block-ID."""
    bullet_re, h3_re = _item_bullet_re(letter), _item_h3_re(letter)
    used = {0}
    for line in doc_text.splitlines():
        m = bullet_re.match(line) or h3_re.match(line)
        if m:
            used.add(int(m.group(2)))
    return max(used) + 1


# F305 D1 — the shared open-items block. `## Open Items` is the canonical
# heading (ratified 2026-08-13: the block hosts questions, verifications, and
# user actions, so "Open Questions" becomes false the moment a non-question
# lives there); `## Open Questions` is the legacy spelling, accepted on read
# forever. The writer renames on touch (restamp_open_questions), so the corpus
# migrates one doc at a time with no sweep — only the writer ever produces the
# new heading.
ITEMS_HEADINGS = ("Open Items", "Open Questions")


def _find_items_h2(lines):
    """The open-items block under either spelling — canonical name first."""
    for name in ITEMS_HEADINGS:
        found = _find_h2(lines, name)
        if found is not None:
            return found
    return None


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


def _find_q_bullet(lines, q_num):
    return _find_item_bullet(lines, "Q", q_num)


def _find_item_bullet(lines, letter, num):
    """Locate the {letter}{num} bullet in the doc. Returns (start_line,
    end_line, indent) where the bullet's body runs from start_line through
    end_line-1 (exclusive of the next top-level bullet / H2 / H3).
    """
    head_re = _item_bullet_re(letter)
    start = None
    indent = ""
    for i, line in enumerate(lines):
        m = head_re.match(line)
        if m and int(m.group(2)) == num:
            # Skip items inside ## Resolved or ### Resolved or ### Removed.
            # Walk back to confirm we're in the pending area.
            section = _section_at(lines, i)
            if section in ("Open Questions", "Open Questions:Pending"):
                start = i
                indent = m.group(1)
                break
    if start is None:
        return None
    # End at the next item-header bullet of ANY kind (same or shallower
    # indent) OR any heading — in a mixed block a V bullet ends the Q above
    # it just as a sibling Q would. Sibling bullets at the same indent
    # (e.g., `- (A)` option bullets, or `- **Recommendation:** ...`) are
    # PART of the item's body, not a sibling item.
    end = len(lines)
    for j in range(start + 1, len(lines)):
        line = lines[j]
        if line.startswith("#"):
            end = j
            break
        m = _ITEM_HEADER_BULLET_RE.match(line)
        if m and (len(line) - len(line.lstrip())) <= len(indent):
            end = j
            break
    return (start, end, indent)


def open_questions_is_empty(lines, h2_start, h2_end):
    """Does the ## Open Questions block still hold anything pending?

    Only two things count as content: a pending item header bullet of ANY
    kind (`- **Q<n>` / `- **V<n>` / `- **U<n>` — the F305 hosting contract:
    the block is deleted when it is empty of all three kinds, not when the
    last question resolves), and a `### ` holding pen. Everything else — the
    integrity stamp, blank lines, and any leftover placeholder prose — is not
    a pending item.

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
        if _ITEM_HEADER_BULLET_RE.match(line):
            return False
    return True


def drop_open_questions_if_empty(lines):
    """Phase 2 — retire a spent ## Open Questions block. Idempotent.

    Removes ONLY the block itself: `_find_h2` ends at the next H2, so a resolved
    archive living further down the doc is never in the removed span.
    """
    oq = _find_items_h2(lines)
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
            in_open_q = (name in ITEMS_HEADINGS)
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
    existing = _find_items_h2(lines)
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
        raise BacklogEditError("feature doc has no H1; cannot insert ## Open Items")
    insert_at = len(lines)
    for j in range(h1_idx + 1, len(lines)):
        if lines[j].startswith("## "):
            insert_at = j
            break
    if insert_at == len(lines) and lines and lines[-1].strip():
        lines = lines + [""]
        insert_at = len(lines)
    new_block = ["## Open Items", "", ""]
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
# `state revalidate <anchor> <doc>` (validate-then-stamp, never bless-blind).

_Q_STAMP_RE = re.compile(r"^<!--\s*state:q\s+([0-9a-z]{2})\s*-->$")
_BASE36 = "0123456789abcdefghijklmnopqrstuvwxyz"


def _open_questions_range(lines):
    """(heading_idx, end_exclusive) of the ## Open Questions block, clamped
    to the H1 when the block sits above it (legacy placement); None if the
    doc has no block. Hash scope per F241: heading through the next H2."""
    found = _find_items_h2(lines)
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


def write_backlog_lines(backlog_path, lines):
    """Write a backlog's lines back with exactly one terminating newline.

    The keepends-list sibling of `_write_feature_lines` (T080). T067 fixed this
    for feature docs but every backlog writer joins a `splitlines(keepends=True)`
    list with `""`, so a trailing blank entry — which row insertion and deletion
    both routinely leave behind — reached disk verbatim and the on-write hook
    fired `R-progressive-02` on the file `state` had just written. It fired on
    EVERY `state <verb> <anchor> Backlog …` call, which is what made it worth a second fix
    rather than a second exemption.
    """
    while lines and not lines[-1].strip():
        lines.pop()
    text = "".join(lines)
    if text and not text.endswith("\n"):
        text += "\n"
    backlog_path.write_text(text, encoding="utf-8")


def _write_feature_lines(feature_path, lines):
    """Write a feature doc's lines back with exactly one terminating newline.

    Every Q verb inserts around blank-line separators, so `lines` routinely
    ends in one or more empty strings; joining those verbatim left trailing
    blank lines at EOF and the on-write hook then fired R-progressive-02 on a
    file `state` had just written (T067, reproduced 3/3). Normalizing here —
    rather than at each call site — keeps the four Q verbs from drifting apart.
    """
    while lines and not lines[-1].strip():
        lines.pop()
    feature_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def restamp_open_questions(lines):
    """Insert-or-update the integrity stamp on the line under the
    ## Open Questions heading. No block → lines returned unchanged. Call
    this LAST, immediately before writing the doc."""
    rng = _open_questions_range(lines)
    if rng is None:
        return lines
    start, end = rng
    # F305 rename-on-touch: every managed write migrates this doc's block to
    # the canonical heading. This is the ONLY place the corpus migrates — an
    # untouched doc keeps the legacy spelling and every reader accepts both.
    if lines[start].strip() == "## Open Questions":
        lines = lines[:start] + ["## Open Items"] + lines[start + 1:]
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
        write_backlog_lines(backlog_path, stamped)
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
    """Return container ID for block-IDs (e.g., 'F128').

    All three filename forms yield the same bare `F298`: the legacy
    `F298 — Title.md`, the F298 `Tink F298 — Title.md`, and the F300
    `TINK298 - Title.md` (where the `F` is reconstructed, not matched). That
    equality is the whole point: block-IDs are permanent deep-link targets and
    `queries.md` / `Q.md` address questions as `^F<n>-Q<n>` — minting
    `^TINK298---Title-Q1` instead would strand every link into the doc while
    looking like it worked.
    """
    return feature_number(feature_path.stem, feature_path) or feature_path.stem


def _format_q_bullet(q_num, container_id, body):
    """Wrap a body into the canonical Q-bullet form with block-ID."""
    return _format_item_bullet("Q", q_num, container_id, body)


def _format_item_bullet(letter, num, container_id, body):
    """Wrap a body into the canonical item-bullet form with block-ID —
    `- **{L}{n} — Title** … ^{container}-{L}{n}` for any hosted kind."""
    body = body.strip()
    block_id = f" ^{container_id}-{letter}{num}"
    # If body already starts with `**Q<n> —`, accept as pre-formatted; just
    # ensure block-ID at end.
    #
    # T140 — this test used to be `^\s*\*\*Q\d+\s+—`, which recognized neither
    # of the two shapes agents actually pipe in: a body already carrying its
    # `- ` bullet (the form every skill template shows), and `Q+`, the mint
    # placeholder. Either fell through to the plain-body branch and was wrapped
    # a SECOND time, yielding `**Q1 — Untitled** — - **Q1 — <the real title>**`
    # — so the header line, which is what `_q_header_line` and queries-render
    # read, said *Untitled* while the question itself sat stranded behind a
    # stray `— - `. Live on SKA F234 Q1/Q2 and HA F112 Q6. `_q_header_line`
    # already admitted both shapes (`^\s*-?\s*\*\*Q(?:\d+|\+)\s+—`); the two
    # patterns simply disagreed, and this one was the stricter.
    if re.match(rf"^\s*-?\s*\*\*{letter}(?:\d+|\+)\s+—", body):
        # Normalize the leading item number to the canonical bullet form. The
        # leading `- ` goes with it and is restored just below, so a bulleted
        # and an unbulleted body converge on the same output.
        body = re.sub(rf"^\s*-?\s*\*\*{letter}(?:\d+|\+)", f"**{letter}{num}",
                      body, count=1)
        # Ensure leading "- " bullet
        if not body.startswith("- "):
            body = "- " + body
    else:
        # T239 — a plain body that OPENS with its own question line titles
        # itself from that line, rather than being stamped `Untitled`. The
        # shape [[DAS ask-format]] invites — question sentence, blank line,
        # then prose — landed in the Resolved zone as `Q2 — Untitled` with the
        # real question stranded on the next line (A2X, 2026-08-16, A2X011 Q2).
        # A Resolved zone full of `Untitled` is unscannable, which is that
        # zone's only job, and there is no retitle verb, so the reporter had to
        # hand-edit against the hook's advice.
        #
        # Only the FIRST line is eligible, and only when it looks like a title
        # rather than a paragraph: no option bullets, no field labels, and
        # short enough to read as a heading. Anything else keeps `Untitled`,
        # which is honest — a wrapped paragraph is not a title.
        head, _, rest = body.partition("\n")
        head = head.strip().lstrip("-").strip()
        looks_like_title = (
            head
            and len(head) <= 120
            and not head.startswith(("**(", "- ", "|", ">", "#"))
            and not re.match(r"^\*\*(?:Recommendation|Damage|Risk|Lean)\b", head)
        )
        if looks_like_title:
            title = f"{head.rstrip('?').strip()}?" if head.endswith("?") else head
            # T245 — omit the ` — ` when the title WAS the whole body. Appending
            # it unconditionally left a dangling em-dash with nothing after it
            # (`- **Q1 — Which relationships carry an ask?** — ^T017-Q1`), which
            # reads as a body that went missing rather than one that was never
            # written, and is what a title-only self-title always produces.
            tail = rest.strip()
            body = (f"- **{letter}{num} — {title}** — {tail}" if tail
                    else f"- **{letter}{num} — {title}**")
        else:
            body = f"- **{letter}{num} — Untitled** — {body}"
    # T140 — the old guard was `if f"^{container_id}-Q{q_num}" not in first_line`,
    # which asked only whether the CORRECT anchor was present and never removed a
    # wrong one. A Q minted while its host row was still `T+` kept `^T+-Q1` and
    # gained `^T017-Q1` beside it — and since the stale anchor sits FIRST,
    # queries-render read that one, putting `^T+-Q1` (a handle resolving to no
    # row) onto the vault-root Q.md. Strip, then append unconditionally.
    first_line, sep, rest = body.partition("\n")
    first_line = _strip_trailing_anchors(first_line) + block_id
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
            "Q-numbering, the two-zone block lifecycle) and runs audit-q lenient as a "
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
        _write_feature_lines(feature_path, lines)
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
        _write_feature_lines(feature_path, lines)
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
            f"**Removed:** {reason}",
            "",
            "> Original Q context (preserved for audit trail):",
        ]
        for ol in original_body.splitlines():
            h3_lines.append(f"> {ol}")
        h3_lines.append("")
        # Remove pending bullet
        lines = lines[:start] + lines[end:]
        # Archive to the BOTTOM `## Resolved` H2, exactly as `resolve` does, then
        # fire phase 2 (T146).
        #
        # This used to write the entry to a `### Removed` H3 *inside* ## Open
        # Questions, and re-create that H2 if the removal had emptied it. That
        # left a block nothing could ever clear: `open_questions_is_empty`
        # counts any `### ` as content (correctly — a holding pen may carry
        # unmigrated decisions), `remove` never called `drop_open_questions_if_empty`,
        # and so a doc whose LAST pending Q was removed kept an Open Questions
        # H2 with zero pending questions. audit-q C21/C35/C46 then fired on it
        # with no sanctioned verb able to fix it — the same unclearable-state
        # shape T042 fixed for placeholder prose.
        #
        # The audit trail is not weakened by the move, it is strengthened: the
        # bottom ## Resolved is the doc's permanent decision record, whereas
        # ## Open Questions is by construction transient. It also makes remove
        # symmetric with resolve, which F127/F128 already ruled must archive to
        # the bottom H2 ("the in-block ### Resolved staging is a historical
        # artifact").
        lines, (rh2_start, rh2_end) = _ensure_bottom_resolved_h2(lines)
        insert_at = rh2_end
        while insert_at > rh2_start + 1 and not lines[insert_at - 1].strip():
            insert_at -= 1
        lines = lines[:insert_at] + h3_lines + lines[insert_at:]
        lines, _dropped = drop_open_questions_if_empty(lines)
        lines = restamp_open_questions(lines)
        _write_feature_lines(feature_path, lines)
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
        _write_feature_lines(feature_path, lines)
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
