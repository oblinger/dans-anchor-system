#!/usr/bin/env python3
"""audit-q.py — Q.md constraint validator with mechanical-fix mode (F076, B16, F089).

Reusable primitives (importable by other tools):
  - links_in_file(path, vault_index) → list[LinkEntry]   (wiki + markdown links)
  - backlog_entries(path) → list[BacklogEntry]            (structured backlog rows)
  - extract_q_entries(path, container_id) → list[QEntry]  (B16 ask-format)

Checks applied to Q.md, each anchor's backlog, and each feature/Questions doc:
  C1:  every Q.md link resolves (file + optional heading/block-id).
  C2:  brackets `[N Questions]` / `[Questions]` target files containing at least
       one Q-marker (existence-check only; exact count NOT required).
  C4:  stale `[Done]` rows in horizon H2s get moved to `## Done`.
  C6:  every `**Q<n> —` bullet ends with `^<container>-Q<n>` block-ID  (auto-fix).
  C7:  external Q references use block-ID link form `[[X#^X-Q<n>|...]]` (report).
  C8:  Q header carries no options inline — ≥2 distinct `(A)`..`(D)`
       labels on the header line, ask-format or prose                   (report).
  C9:  every Q has a sibling **Recommendation** with Strong/Lean/None  (report).
  C10: **Recommendation** bullet at same indent as the Q header        (auto-fix).
  C12: every `[Verify-by YYYY-MM-DD]` row body includes
       "Naturally exercised by: …"                                     (report).
  C13: `## Ready` H2 contains only `[Ready]` rows.
       Pure-state mismatches (Watching/Waiting/Blocked) auto-move      (hybrid).
  C14: `## Active` H2 contains only `[Active]` rows.
       Pure-state mismatches (Watching/Waiting/Blocked) auto-move      (hybrid).
  C15: `[Watching]/[Waiting]` rows must be in `## Later`               (auto-fix).
  C16: `[Blocked]/[Blocked F<n>]` rows must be in `## Later`           (auto-fix).
  C18: `[Verify-by YYYY-MM-DD]` past expiry → auto-move to `## Done`   (auto-fix).
  C19: option sub-bullets each on own line, labeled `(A)/(B)/...`      (report).
  C20: blank line after Recommendation separating Q groups             (report).
  C21: `## Open Questions` H2 with zero pending Qs (Phase 2 missed)    (report).
  C22: link existence in feature docs / backlogs                       (report).
  C23: `[Designing]` brackets must resolve to `[N Questions]` (if
       linked doc has pending Qs) or `[Ready]` (if none) — `[Designing]`
       alone is a turn-ownership deadlock                              (auto-fix).
  C41: [Verify*]/[Watching*] rows declare a `- **Verify:**` yes/no question;
       [Ready]/[Active] rows declare a `- **Next:**` no-user action. Missing →
       queries render `⚠`; report-only (agent writes it or rebrackets).
  C42: an answerable queries item (Verification / Immediate Question /
       Question) that NAMES a doc/file/template the user must open MUST make
       it a live `[[wiki-link]]` — bare text (a resolvable slug-prefixed doc
       name) or a code-span filename is a violation: the user cannot follow a
       name. Fix at the SOURCE (backlog `- **Verify:**` / question body). (report).
  C24: `[Questions]` / `[N Questions]` bracket count must match the
       linked feature doc's actual pending-Q count. Bare `[Questions]`
       on a row whose linked doc has 7 Qs is stale (should be
       `[7 Questions]`); `[3 Questions]` on a doc with 0 Qs is also stale. (report).
  C47: F240 — a [Verify*]/[Watching*] row whose `- **Verify:**` question is
       phrased as a machine event ("did X mint/run/render", "does the file
       exist", command-form asks) is agent-grade: the agent runs it now or
       reclassifies [Waiting] with an agent-check plan. Heuristic shared with
       backlog-edit.py's mint-time gate (is_mechanical_verify). (report).
  C50: F257 — a pending Open Question carrying a Lean/Strong Recommendation
       but no `· *why-ask: …*` (a recommendation-bearing ask the agent could
       likely decide, F068), or an agent-territory-phrased Q (ordering /
       batching / rollback / cosmetic rename). Audit mirror of the mint-time
       question_mint_gate, over Qs that reached a doc off the `state` path. (report).
  C51: F259 — a [User] row (gated on a genuinely user-only action) must carry a
       `- **User:**` sub-bullet naming that action. Audit mirror of the mint-time
       guard. [User] rows fold into the Questions banner count (count-only). (report).
  C53: F281 — two anchor pages sharing a basename. An anchor page is the
       target of dispatch rows written from anywhere in the vault, so a
       colliding anchor name resolves by proximity to the LINKING file and is
       therefore wrong from most of the vault. Error severity: the population
       is small enough (3 today) to enforce, and enforceable rules that start
       clean stay clean. Ordinary-file collisions stay a WARNING on
       `ha --dump --format=collisions` — different in kind, not just count.
       Filenames mandated by an external format are exempt.            (report).
  C54: T154 — a Q.md banner whose label and link target are different
       anchors: `[[SONAR queries|SEEK]]` reports SONAR's counts under a name
       that owns none of them. C1 tests only that the target RESOLVES, so it
       passes this silently; Daybreak and LUMEN's starvation rule both read
       these counts. Case drift is not a mismatch (T138).              (report).
  C57: F329/T550 — a live backlog row that HOSTS a question instead of
       pointing at the doc that does. Four shapes, named on the finding:
       `inline-q` (pending `- **Q<n>` sub-bullet), `q-row` (F275 standalone
       Q-row), `lettered` (a `- **User:**`/`- **Verify:**` sub-bullet carrying
       ≥2 `(A)`..`(D)` labels — a whole ask-format question in the row), and
       `unhosted` (that sub-bullet poses a `?` on a row with no `→ [[doc]]`).
       F329's mint-time gate names only the first, which is why the other
       three accumulated unseen. Warning: this is a migration population, not
       a stop-gate.                                                  (report).
  D1:  Q.md per-anchor banners derived from each anchor's backlog
       (not validated — overwritten on every run).

Usage (per F076 v2, 2026-05-26 — scope-aware audit):
  audit-q                                  # default --scope q: Q.md + linked backlogs + linked feature docs
  audit-q --fix                            # apply mechanical repairs
  audit-q --dry                            # report-only AND refuse to write
  audit-q --scope all                      # vault-wide (every Features/F*.md, ignoring backlog reachability)
  audit-q --scope backlog --anchor SKA     # one anchor's backlog + its linked feature docs
  audit-q --scope feature-doc --feature-doc PATH    # one feature doc only

Wrapper scripts at ~/bin/audit-backlog and ~/bin/audit-feature-doc invoke the
scoped modes with terser CLI: `audit-backlog SKA`, `audit-feature-doc PATH`.

Design: F076 v2 — scoped audits (q / backlog / feature-doc / all) chained by
       reachability per user direction 2026-05-26: only audit feature docs
       the user can click into via Q.md → backlog → linked F-doc.
       F076 v1 — Q.md constraint validator with mechanical-fix mode.
       B16    — ask-format rules C6–C12.
       F089   — bracket↔H2 consistency rules C13–C18.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional
import argparse
import os
import re
import sys

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


# --- F240 shared heuristic (C47) ---------------------------------------------
# is_mechanical_verify lives in backlog-edit.py (the mint-time enforcement
# chokepoint) — single source of truth; C47 is the audit mirror over rows that
# predate the gate or were hand-edited. Load failure is a broken install (the
# two scripts ship together in dans-anchor-system) — fail loud, no fallback.
import importlib.util as _be_il

_BE_PATH = (Path(__file__).resolve().parent.parent.parent
            / "workflow" / "scripts" / "backlog-edit.py")
_be_spec = _be_il.spec_from_file_location("backlog_edit_for_audit", _BE_PATH)
if _be_spec is None or _be_spec.loader is None:
    raise ImportError(f"cannot load backlog-edit.py from {_BE_PATH}")
_be_mod = _be_il.module_from_spec(_be_spec)
_be_spec.loader.exec_module(_be_mod)
is_mechanical_verify = _be_mod.is_mechanical_verify
is_nonanswer = _be_mod.is_nonanswer  # F242 (C49) — punt detector, same sharing
# F257 (C50) — question-mint gate primitives, same single-source sharing:
# the audit mirrors question_mint_gate over Qs that reached a doc off the
# `state` path (hand-edit / legacy).
recommendation_strength = _be_mod.recommendation_strength
has_why_ask_annotation = _be_mod.has_why_ask_annotation
is_agent_territory_question = _be_mod.is_agent_territory_question
# T086 (C24) — where a row's PENDING inline questions stop and its resolved
# archive begins. Shared rather than re-expressed: `state`'s resolve verb
# writes the boundary, this counts across it, and a row whose bracket and
# contents disagree is precisely the drift C24 exists to catch.
row_pending_q_lines = _be_mod.row_pending_q_lines
# ---------------------------------------------------------------------------



# ============================================================
# Configuration
# ============================================================
#
# VAULT_ROOT is the global `vault_root` parameter documented in
# [[SKA System Design]] § Per-user parameters. Audit / hygiene scripts ALWAYS
# default to vault-wide scope — Obsidian operates on the vault, audits follow
# the same scope; single-anchor scoping defeats the purpose of cross-cutting
# drift detection. Per F080, the value comes from
# ~/.config/anchor-system/global.yaml; fallback to ~/ob/kmr if config missing.
# Do NOT add a --project flag that narrows scope by default; if a narrowing
# flag is wanted, make it explicit opt-in.


def _resolve_vault_root() -> Path:
    """Read vault_root from F080 config (~/.config/anchor-system/global.yaml),
    falling back to ~/ob/kmr if the config file or key is missing.

    `ANCHOR_VAULT_ROOT` overrides both (F269). Without it there was NO way to
    point this engine at anything but the live vault, and the consequence was
    not theoretical: `test-f244-stop-gate.sh` and `test-f241-q-stamp.sh` build
    fixture anchors in a temp dir, render them — and the render, resolving the
    real vault root, spliced their sections into the REAL `Q.md`. Teardown
    `rm -rf`s the fixture directory but cannot reach into Q.md, so every run
    left an orphan section behind (`F244FIX`, `F244FIXP`, `F241FIX`, `CTEST`
    were the four still sitting there on 2026-07-18).

    This is the actual bug. The orphan-section audit check (C56) is the net
    under it, not the fix: shipping only the net leaves a checker permanently
    cleaning up after a defect nobody closed.

    Deliberately FIRST in the chain and deliberately not validated for
    existence — an override that silently fell back to the live vault when
    mistyped would reintroduce exactly the failure it exists to prevent.
    """
    override = os.environ.get("ANCHOR_VAULT_ROOT")
    if override:
        return Path(override).expanduser()
    config_path = Path.home() / ".config" / "anchor-system" / "global.yaml"
    if config_path.is_file():
        try:
            import yaml
            with config_path.open() as f:
                data = yaml.safe_load(f) or {}
            raw = data.get("vault_root")
            if raw:
                return Path(str(raw).replace("~", str(Path.home())))
        except (ImportError, Exception):
            pass
    return Path.home() / "ob" / "kmr"


VAULT_ROOT = _resolve_vault_root()
Q_MD = VAULT_ROOT / "Q.md"

# Filesystem-walk exclusions when building the vault index.
EXCLUDED_PATH_FRAGMENTS = (".trash", "Closet", "Yore", "worktrees", ".claude")

# Horizon H2s in a per-anchor backlog. `## Done` is the archive surface for
# C4's stale-Done migration; everything else is a "live" horizon.
LIVE_HORIZON_H2S = {"Active", "Ready", "Now", "Next", "Later", "Verify", "Legwork"}

# Canonical horizon PRIORITY — the order a reader should meet these in, which is
# not necessarily the order they sit in a file. Named once here because it was
# previously implicit in a counts-dict initializer duplicated across this file and
# `queries-render.py`, and anything that needed to ORDER by it had nothing to call
# (T091). Unknown//absent horizons sort last. `Icebox` is included for ordering even
# though it is not a LIVE horizon; `Legwork` sits with the active group.
HORIZON_ORDER = ("Active", "Ready", "Now", "Next", "Legwork", "Later", "Verify", "Icebox")
HORIZON_RANK = {h: i for i, h in enumerate(HORIZON_ORDER)}
ALL_KNOWN_H2S = LIVE_HORIZON_H2S | {"Done", "Icebox", "Notes"}

# ============================================================
# Regexes
# ============================================================

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
BLOCK_ID_RE = re.compile(r"\^([A-Za-z][A-Za-z0-9_\-]*)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
# Markdown link: [text](path) — but NOT [[wiki]]. Negative lookbehind for `[`.
MARKDOWN_LINK_RE = re.compile(r"(?<!\[)\[([^\[\]]+)\]\(([^)]+)\)")
# Backlog row: starts with `- **<identifier>` or `- **[[<identifier>` (wiki-link
# identifier form used by some anchors, e.g. MUX). Identifier is F<n> or B-<name>.
ROW_OPENER_RE = re.compile(
    r"^- \*\*"
    r"(?:\[\[)?"                     # optional `[[` (wiki-link form)
    r"(?:\[[A-Z]+\]\s+)?"            # optional `[TYPE] ` prefix (e.g., `[BUG] `)
    # group(1) = identifier: F091 / T007 / B-QFix / DMUX-F034, plus dotted
    # roadmap-task handles like R-Scaffolding.5.2 (name-path + numeric sub-levels).
    r"([A-Za-z][A-Za-z0-9_\-]*(?:\.[A-Za-z0-9_\-]+)*)\b"
)
# Status bracket: `[Ready]`, `[3 Questions]`, `[Blocked F123]`, etc.
# Leading char accepts digits for the `[N Questions]` form — a letter-only
# gate made numeric brackets invisible to _detect_status, so a wrong
# `[2 Questions]` bracket could never be re-counted or fixed (T012).
BRACKET_RE = re.compile(r"\[([A-Za-z0-9][A-Za-z0-9 \-]*?)\]")
# Q-marker: `**Q<n> —`. Used by C2 for existence-check at link targets.
Q_MARKER_RE = re.compile(r"\bQ\d+\s+—")
# Q.md per-anchor section H1 banner.
QMD_BANNER_RE = re.compile(
    # Match both the new format `[[X queries|X]]` and the legacy
    # `[[Q#X Triage|X Triage]]` form so banner-rewrite works either way.
    r"^# \[(?P<tag>[^\]]*)\]\s+"
    r"\[\[(?:Q#)?(?P<name>[^\|\]]+?)(?:\s+(?:Triage|ask|queries))?(?:\|[^\]]+)?\]\]"
    r"\s+-\s+(?P<rest>.+)$"
)

# B16 (ask-format) — Q-header bullet: `- **Q<n> — ...`
Q_HEADER_RE = re.compile(r"^(\s*)- \*\*Q(\d+)\b")
# F123 — Q-header H3 form: `### Q<n> — ...` (used by DKT and possibly others)
Q_HEADER_H3_RE = re.compile(r"^### Q(\d+)\b")
# B16 — block-ID at end of Q header line: `^F089-Q3`. The `|Q\d+` alternative is
# the bare form a standalone Q ROW carries (`^Q004`, F275) — a row anchor rather
# than a container-scoped one, but a Q block-ID all the same. Without it the row's
# existing anchor read as absent and C6 demanded a second one on the same line.
Q_BLOCK_ID_TRAILING_RE = re.compile(r"\^([A-Za-z][A-Za-z0-9_\-]*-Q\d+|Q\d+)\s*$")
# F251 #9 — ANY trailing `^block-id` (used to detect a FOREIGN, non-`-Q<n>`
# id that apply_c6_fix must not strand mid-line by appending after it).
ANY_BLOCK_ID_TRAILING_RE = re.compile(r"\^([A-Za-z][A-Za-z0-9_\-]*)\s*$")
# B16 — Recommendation bullet: `- **Recommendation:** Strong (B). reason.`
RECOMMENDATION_RE = re.compile(
    r"^(\s*)- \*\*Recommendation:\*\*\s*(Strong|Lean|None)?\b",
    re.IGNORECASE,
)
# F123 — Recommendation paragraph form (H3-shape Qs): `Recommendation: **None** ...`
# Accepts strength inside or outside the bold-asterisks. Anchors `\b` *after*
# the strength capture (before any closing `**`) so `**None**` matches.
RECOMMENDATION_PARA_RE = re.compile(
    r"^Recommendation:\s*\*{0,2}(Strong|Lean|None)\b\*{0,2}",
    re.IGNORECASE,
)
# B16 (C8) — embedded alternatives: two or more DISTINCT option labels on the
# Q header line, meaning the options were written inline instead of hoisted to
# their own labeled sub-bullets. The write path already refuses this shape
# (`state._validate_ask_format_body` requires ≥2 own-line `- **(A)**` bullets),
# so C8 is what catches pre-gate docs already on disk.
#
# Superseded a proximity regex `\([aAbBcDdD]\)[^\n]{0,80}\([aAbBcDdD]\)`, which
# missed the common real shape two ways: the 80-char window is shorter than one
# option's prose (the two HA Backlog cases sat 153 and 255 chars apart), and the
# char class omitted `C` while repeating `D`, so `(A) … (C)` never matched.
# Distinct-label counting has neither limit, and requiring the labels to *differ*
# also drops the same-label repeat (`(A)` twice) the old regex counted as a hit.
# Measured over 7,453 vault files: 62 → 85 flagged pending Q headers, every one
# of the 23 additions a genuine inline-option list, 0 prior hits lost.
OPTION_LABEL_INLINE_RE = re.compile(r"\(([A-Da-d])\)")


def has_inline_alternatives(text: str) -> bool:
    """True when `text` carries ≥2 distinct option labels — `(A)`/`(a)` … `(D)`.
    Case-folded, so `(a)` and `(A)` are the same label. Callers strip inline
    code spans first: `(A)/(B)` inside backticks is describing the ask-format,
    not using it."""
    labels = {m.group(1).upper() for m in OPTION_LABEL_INLINE_RE.finditer(text)}
    return len(labels) >= 2
# B16 (C7) — Q reference in display text: `\bQ\d+\b` outside the basename
# Bare `Q<n>` in display text means the link should point to that Q via block-ID.
# Whereas `F<n> Q<m>` (an F-number immediately preceding Q<m>) means Q<m>
# references THAT F<n>, not the link's target — those are descriptive phrases,
# not Q-pointer links, and shouldn't trigger C7.
Q_REF_IN_DISPLAY_RE = re.compile(r"\bQ\d+\b")
F_REF_BEFORE_Q_RE = re.compile(r"\bF\d+\s+Q\d+\b")
# B16 (C12) — Verify-by bracket
VERIFY_BY_BRACKET_RE = re.compile(r"\[Verify-by\s+(\d{4}-\d{2}-\d{2})\]")
# B16 (C12) — "Naturally exercised by" rationale text
NATURALLY_EXERCISED_RE = re.compile(r"[Nn]aturally exercised by\b")
# B16 — F-number extraction from feature-doc stems. Three forms, all yielding
# the same bare `F089`:
#
#   F089 — Title        legacy, every doc before 2026-08-02
#   SKA F089 — Title    F298, slug-prefixed
#   SKA089 - Title      F300, current — the `F` is RECONSTRUCTED, not matched
#
# Older docs are never renamed, so all three are accepted permanently.
# Canonical copy of this grammar: `backlog_edit.feature_number`; audit-q runs
# standalone and cannot import it, so it is repeated here.
F_NUMBER_PREFIX_RE = re.compile(r"^(?:[A-Za-z][A-Za-z0-9]*\s+)?(F\d+)\s+—")
F_NUMBER_FUSED_RE = re.compile(r"^[A-Za-z]+(\d+)\s+-\s+")


def feature_number(stem, path=None):
    """Return the bare row handle a doc stem names (`F300`, `T287`), or None.

    The fused form carries no letter, so it is RECONSTRUCTED. Since 2026-08-19
    T-docs use that spelling too, and reconstructing an `F` unconditionally made
    `HA287 - Soak…` read as `F287` — a feature that does not exist — so C35/C46
    reported the row's questions as unreachable. The doc's H1 breadcrumb still
    carries the kind; `F` stays the fallback when there is no path to read.
    Canonical copy: `backlog_edit.feature_number`."""
    m = F_NUMBER_PREFIX_RE.match(stem)
    if m:
        return m.group(1)
    m = F_NUMBER_FUSED_RE.match(stem)
    if not m:
        return None
    letter = "F"
    if path is not None:
        try:
            head = Path(path).read_text(encoding="utf-8")[:4000]
        except (OSError, UnicodeDecodeError):
            head = ""
        h1 = re.search(rf"^#\s.*·\s*([A-Z])0*{int(m.group(1))}\s+—", head, re.M)
        if h1:
            letter = h1.group(1)
    return letter + m.group(1)
# F089 (C18) — Verify-by bracket date extraction (parses the date for expiry check)
VERIFY_BY_DATE_RE = re.compile(r"^Verify-by\s+(\d{4})-(\d{2})-(\d{2})\b")

# ============================================================
# Dataclasses
# ============================================================


@dataclass
class LinkEntry:
    source_file: Path
    source_line: int
    source_col_start: int
    source_col_end: int
    raw: str
    kind: str  # 'wiki' or 'markdown'
    target_basename: str
    target_heading: Optional[str] = None
    target_block_id: Optional[str] = None
    display_text: Optional[str] = None
    target_file_path: Optional[Path] = None
    target_line: int = 0
    target_resolves: bool = False
    target_anchor_resolves: Optional[bool] = None


@dataclass
class BacklogEntry:
    source_file: Path
    source_line: int
    identifier: str
    horizon: str
    status: str
    link: Optional[LinkEntry]
    raw_body: str
    links: list[LinkEntry] = field(default_factory=list)  # all links on the row line, in order (T012)


@dataclass
class Finding:
    severity: str  # 'error' or 'warning'
    surface_file: Path
    surface_line: int
    code: str  # 'C1' / 'C2' / 'C4' / 'D1' / 'stale-Q-marker' / etc.
    message: str
    mechanically_fixable: bool


@dataclass
class QEntry:
    """B16 — a single Q-header inside a ## Open Questions block.

    F123: `shape` distinguishes the two valid Q-header forms:
      - "bullet" — `- **Q<n> — ...` (canonical / ask-format default)
      - "h3"     — `### Q<n> — ...` (DKT and possibly other anchors)
    Most checks apply uniformly; per-shape divergences are documented at
    each check (C10 N/A for h3; C19 looks at top-level bullets; C20 N/A
    when shape==h3 and recommendation is paragraph-form).
    """
    source_file: Path
    source_line: int            # 1-indexed Q header line
    indent: str                 # leading whitespace on the Q header line
    q_num: int
    container_id: str           # e.g., 'F089', 'SKA', 'QFix' (B-row)
    has_block_id: bool
    block_id_value: Optional[str] = None
    inline_alternatives: bool = False
    recommendation_line: int = 0           # 0 = missing
    recommendation_indent: Optional[str] = None
    recommendation_strength: Optional[str] = None  # 'Strong' / 'Lean' / 'None'
    shape: str = "bullet"                  # F123: "bullet" | "h3"
    recommendation_is_paragraph: bool = False  # F123: paragraph-form Rec (h3 only)


# ============================================================
# Vault index (basename → list of paths; Obsidian path-proximity resolution)
# ============================================================


def build_vault_index(vault_root: Path) -> dict[str, list[Path]]:
    """Walk vault_root for *.md files; return basename → list of paths.
    Keys are lower-cased: Obsidian resolves wiki-links case-insensitively,
    so `[[Track]]` finding only `track.md` is a resolvable link (T002)."""
    index: dict[str, list[Path]] = {}
    for path in vault_root.rglob("*.md"):
        if any(frag in path.parts for frag in EXCLUDED_PATH_FRAGMENTS):
            continue
        stem = path.stem.lower()
        index.setdefault(stem, []).append(path)
    return index


def resolve_target(basename: str, source_file: Path,
                   vault_index: dict[str, list[Path]]) -> Optional[Path]:
    """Obsidian path-proximity resolution: closest match wins."""
    basename = basename.strip()
    if not basename:
        return None
    # Strip `.md` extension if explicitly written
    if basename.endswith(".md"):
        basename = basename[:-3]
    candidates = vault_index.get(basename.lower(), [])
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    def shared_depth(p: Path) -> int:
        a = source_file.parts
        b = p.parts
        i = 0
        while i < len(a) and i < len(b) and a[i] == b[i]:
            i += 1
        return i
    return max(candidates, key=shared_depth)


# ============================================================
# File scanning primitives (read once per call; no caching of contents)
# ============================================================


def headings_in(file_path: Path) -> dict[str, int]:
    """Return dict heading-text → 1-indexed line. First occurrence wins.

    Stores TWO keys per heading: (1) the raw heading text, (2) the
    code-span-stripped form. Wiki-links pointing to a heading get their
    inner backticks blanked by `_strip_code_spans` during `links_in_file`,
    so the lookup may use either form. Storing both makes the comparison
    survive backticks inside heading text like H3 'move' (in code-span form)
    followed by em-dash and prose.
    """
    if not file_path.is_file():
        return {}
    headings: dict[str, int] = {}
    try:
        with file_path.open() as f:
            for i, line in enumerate(f, start=1):
                m = HEADING_RE.match(line)
                if m:
                    raw = m.group(2)
                    headings.setdefault(raw, i)
                    stripped = _strip_code_spans(raw)
                    if stripped != raw:
                        headings.setdefault(stripped, i)
    except (OSError, UnicodeDecodeError):
        pass
    return headings


def block_ids_in(file_path: Path) -> dict[str, int]:
    """Return dict block-id → 1-indexed line. First occurrence wins."""
    if not file_path.is_file():
        return {}
    ids: dict[str, int] = {}
    try:
        with file_path.open() as f:
            for i, line in enumerate(f, start=1):
                for m in BLOCK_ID_RE.finditer(line):
                    ids.setdefault(m.group(1), i)
    except (OSError, UnicodeDecodeError):
        pass
    return ids


# ============================================================
# Link parsing — wiki + markdown
# ============================================================


def _parse_wiki_inner(inner: str) -> dict:
    """Parse the inside of a [[wiki-link]] (between [[ and ]])."""
    if "|" in inner:
        target_part, alias = inner.split("|", 1)
        # R-markdown-01 REQUIRES the alias pipe be written `\|` inside a table
        # cell, so a link that obeys that rule arrives here as
        # `Doc#^F259\` + `F259`. Without dropping the escape the block-id reads
        # as `F259\` and C22 reports a false "block-id missing in target" on
        # every correctly-escaped table link.
        target_part = target_part[:-1] if target_part.endswith("\\") else target_part
    else:
        target_part, alias = inner, None
    target_heading = None
    target_block_id = None
    if "#" in target_part:
        basename, anchor = target_part.split("#", 1)
        if anchor.startswith("^"):
            target_block_id = anchor[1:]
        else:
            target_heading = anchor
    else:
        basename = target_part
    return {
        "basename": basename.strip(),
        "target_heading": target_heading,
        "target_block_id": target_block_id,
        "display_text": alias,
    }


def _resolve_wiki(parsed: dict, source_file: Path,
                  vault_index: dict[str, list[Path]]) -> dict:
    """Given parsed wiki components, resolve target file + anchor + line."""
    target_file = resolve_target(parsed["basename"], source_file, vault_index)
    target_resolves = target_file is not None
    target_anchor_resolves: Optional[bool] = None
    target_line = 0
    if target_file and parsed["target_heading"]:
        line_num = headings_in(target_file).get(parsed["target_heading"], 0)
        target_anchor_resolves = line_num > 0
        target_line = line_num
    elif target_file and parsed["target_block_id"]:
        line_num = block_ids_in(target_file).get(parsed["target_block_id"], 0)
        target_anchor_resolves = line_num > 0
        target_line = line_num
    return {
        "target_file_path": target_file,
        "target_line": target_line,
        "target_resolves": target_resolves,
        "target_anchor_resolves": target_anchor_resolves,
    }


def _parse_markdown(text: str, path: str, source_file: Path) -> dict:
    """Parse markdown link [text](path). Resolve path relative to source_file."""
    target_heading = None
    if "#" in path:
        path_part, anchor = path.split("#", 1)
        if not anchor.startswith("^"):
            target_heading = anchor
    else:
        path_part = path
    target_file: Optional[Path] = None
    if path_part:
        if path_part.startswith("/"):
            candidate = Path(path_part)
        elif path_part.startswith("~"):
            candidate = Path(path_part).expanduser()
        else:
            candidate = (source_file.parent / path_part).resolve()
        if candidate.is_file():
            target_file = candidate
    target_resolves = target_file is not None
    target_anchor_resolves: Optional[bool] = None
    target_line = 0
    if target_file and target_heading:
        line_num = headings_in(target_file).get(target_heading, 0)
        target_anchor_resolves = line_num > 0
        target_line = line_num
    return {
        "basename": Path(path_part).stem if path_part else "",
        "target_heading": target_heading,
        "target_block_id": None,
        "display_text": text,
        "target_file_path": target_file,
        "target_line": target_line,
        "target_resolves": target_resolves,
        "target_anchor_resolves": target_anchor_resolves,
    }


def _is_placeholder_basename(basename: str) -> bool:
    """Heuristically detect 'placeholder' wiki-links that shouldn't be flagged:
    template-prose `[[<expected_anchor>]]`, `[[NAME]]`, `[[...]]`, `[[{x}]]`,
    `[[filename.ext]]`, etc. — these aren't real links, they're spec examples.

    Returns True if the basename looks like a placeholder."""
    if not basename:
        return True
    # Angle-bracket placeholders: <expected_anchor>, <Name>, etc.
    if "<" in basename or ">" in basename:
        return True
    # Curly-brace placeholders: {x}, {slug}, {}, etc.
    if "{" in basename or "}" in basename:
        return True
    # Ellipsis placeholders: `...`, `name...`, etc.
    if "..." in basename:
        return True
    # Generic-shaped placeholders: bare lowercase metavariable like `name`,
    # `filename.ext` (contains a dot suggesting a filename example).
    if basename in {"name", "NAME", "filename.ext", "RID", "TID", "SLUG", "Name", "id"}:
        return True
    return False


# Memory-file prefixes (live in ~/.claude/projects/.../memory/, OUTSIDE the
# kmr vault). Wiki-links to them are valid but the audit can't see them.
# `gotcha_` is a naming convention layered on top of `type: project` rather than
# a type of its own, which is why it was missed here: the list was built from the
# four `type:` values and the corpus uses five prefixes. 19 `gotcha_*` memories
# existed before any vault document cited one, so the omission produced no finding
# until 2026-08-09 and then produced a false C22 on the first citation.
_MEMORY_PREFIXES = ("feedback_", "user_", "project_", "reference_", "gotcha_")


def _is_out_of_vault_wiki_link(basename: str) -> bool:
    """Detect wiki-link basenames that legitimately target content the audit
    cannot see in the kmr vault:

    - Path-style refs (`../../../foo`, `A2X Skills/A2X remote`) — these are
      filesystem-relative or sub-folder refs, not basename lookups.
    - Memory-file refs (`feedback_*`, `user_*`, `project_*`, `reference_*`) —
      live in ~/.claude/projects/<proj>/memory/, outside the kmr vault.

    Returns True if the basename should be silently skipped by C22."""
    if not basename:
        return False
    # Path-style: contains a slash (forward or back) or path traversal.
    if "/" in basename or "\\" in basename or ".." in basename:
        return True
    # Memory-file prefixes.
    if basename.startswith(_MEMORY_PREFIXES):
        return True
    return False


# Markdown links with a URL scheme are external — not audit's concern.
_URL_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def _is_url_markdown_link(path: str) -> bool:
    """True if a markdown link's path is a URL (http://, https://, hook://,
    mailto:, etc.) rather than a filesystem path."""
    return bool(_URL_SCHEME_RE.match(path))


def _strip_code_spans(line: str) -> str:
    """Remove inline-code spans from a line, honoring CommonMark N-backtick
    spans. A run of N backticks opens a span; it closes only on a matching run
    of exactly N backticks. Contents between (including any shorter backtick
    runs) are blanked to whitespace to preserve column offsets. Fixes SKA F227
    bug where a naive single-backtick toggle mis-parsed ``double-backtick``
    spans and left their interior exposed to link-resolution."""
    out = list(line)
    i = 0
    n = len(out)
    while i < n:
        if out[i] == "`":
            j = i
            while j < n and out[j] == "`":
                j += 1
            open_len = j - i
            k = j
            closed = False
            while k < n:
                if out[k] == "`":
                    m = k
                    while m < n and out[m] == "`":
                        m += 1
                    close_len = m - k
                    if close_len == open_len:
                        for p in range(j, k):
                            out[p] = " "
                        i = m
                        closed = True
                        break
                    k = m
                else:
                    k += 1
            if not closed:
                i = n
        else:
            i += 1
    return "".join(out)


def links_in_file(file_path: Path,
                  vault_index: dict[str, list[Path]]) -> list[LinkEntry]:
    """Parse all wiki + markdown links in file_path; return ordered list.

    Skips: (a) lines inside fenced code blocks (``` ... ```), (b) wiki-links
    inside inline code spans (`...`), (c) wiki-links whose basename looks like
    a template placeholder (`<x>`, `{x}`, `...`, etc.). Per user direction
    2026-05-26 — these are spec-prose examples, not real links."""
    entries: list[LinkEntry] = []
    if not file_path.is_file():
        return entries
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return entries
    in_fence = False
    for line_num, line in enumerate(lines, start=1):
        # Track fenced-code-block state. Lines starting with ``` toggle.
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Strip inline-code spans before scanning links.
        scan_line = _strip_code_spans(line)
        for m in WIKI_LINK_RE.finditer(scan_line):
            parsed = _parse_wiki_inner(m.group(1))
            # Skip template-prose placeholders.
            if _is_placeholder_basename(parsed["basename"]):
                continue
            # Skip path-style refs and memory-file refs the audit can't see.
            if _is_out_of_vault_wiki_link(parsed["basename"]):
                continue
            resolved = _resolve_wiki(parsed, file_path, vault_index)
            entries.append(LinkEntry(
                source_file=file_path,
                source_line=line_num,
                source_col_start=m.start() + 1,
                source_col_end=m.end(),
                raw=m.group(0),
                kind="wiki",
                target_basename=parsed["basename"],
                target_heading=parsed["target_heading"],
                target_block_id=parsed["target_block_id"],
                display_text=parsed["display_text"],
                target_file_path=resolved["target_file_path"],
                target_line=resolved["target_line"],
                target_resolves=resolved["target_resolves"],
                target_anchor_resolves=resolved["target_anchor_resolves"],
            ))
        for m in MARKDOWN_LINK_RE.finditer(scan_line):
            # Skip URL-scheme links (http://, https://, hook://, mailto:, ...).
            if _is_url_markdown_link(m.group(2)):
                continue
            parsed = _parse_markdown(m.group(1), m.group(2), file_path)
            # Skip template-prose placeholders.
            if _is_placeholder_basename(parsed["basename"] or ""):
                continue
            entries.append(LinkEntry(
                source_file=file_path,
                source_line=line_num,
                source_col_start=m.start() + 1,
                source_col_end=m.end(),
                raw=m.group(0),
                kind="markdown",
                target_basename=parsed["basename"],
                target_heading=parsed["target_heading"],
                target_block_id=parsed["target_block_id"],
                display_text=parsed["display_text"],
                target_file_path=parsed["target_file_path"],
                target_line=parsed["target_line"],
                target_resolves=parsed["target_resolves"],
                target_anchor_resolves=parsed["target_anchor_resolves"],
            ))
    return entries


# ============================================================
# Backlog parsing — structured BacklogEntry list
# ============================================================


def _detect_status(line: str) -> str:
    """Extract the workflow-state bracket from a row's main line.

    Returns the bracket text without brackets (e.g., 'Ready', '3 Questions',
    'Blocked F123', 'Done', 'Done 2026-05-19', or '' if no bracket found).
    Only the FIRST bracket — and only when it sits in the row's *head*
    region (before the first ` — ` separator). Brackets buried in the row's
    body description (e.g., `(Phases 0 + 1 + 2a [Done] 2026-05-20)`) are NOT
    workflow-state markers and must be ignored.

    Strips `[[wiki-links]]` and inline code spans first so the inner brackets
    of `[[CAE System Design]]` or backticked code-span brackets don't get misread.
    """
    cleaned = _cleaned_line(line)
    start, end = _head_span(line)
    m = BRACKET_RE.search(cleaned, start, end)
    if not m:
        return ""
    return m.group(1).strip()


def _cleaned_line(line: str) -> str:
    """Blank inline-code spans and `[[wiki-links]]` to same-length whitespace.
    Column offsets are preserved exactly, so any position found on the cleaned
    line maps 1:1 back onto the raw line — the property the C23/C24 fixers rely
    on to splice a new bracket by offset (F251 #6)."""
    cleaned = _strip_code_spans(line)
    # Replace each `[[...]]` with same-length spaces to preserve column offsets
    # while making BRACKET_RE / the ` — ` separator scan blind to wiki inner text.
    return re.sub(r"\[\[[^\[\]]*\]\]", lambda m: " " * len(m.group(0)), cleaned)


def _head_span(line: str) -> tuple[int, int]:
    """Return the `(start, end)` column offsets of a row's *head* region — from
    the end of the `- **title**` bold to the first REAL ` — `/` - ` separator.
    Separators (and brackets) inside wiki-links or code spans are blanked first
    so they never truncate the head. Offsets are valid on the RAW line. Returns
    `(0, len)` when the row has no bold title.

    Shared by `_detect_status` (bracket detection) AND `apply_c23_fix` /
    `apply_c24_fix` (bracket replacement) so the checker and the fixer agree on
    where the status bracket lives — previously the fixers recomputed the head
    on the raw line, where a ` — ` inside a leading wiki-link truncated the head
    before the bracket, so the replace silently no-op'd and the finding flapped
    every run (F251 #6)."""
    cleaned = _cleaned_line(line)
    title_match = re.match(r"^- \*\*[^*]+\*\*", cleaned)
    if title_match:
        start = title_match.end()
        post = cleaned[start:]
        sep_match = re.search(r"\s[—-]\s", post)
        end = start + (sep_match.start() if sep_match else len(post))
    else:
        start, end = 0, len(cleaned)
    return start, end


def _fenced_line_indices(lines: list[str]) -> set[int]:
    """0-based indices of lines INSIDE a ``` / ~~~ fenced code block (the fence
    delimiter lines themselves are included). Shared fence-awareness for the
    backlog parser + placement fixers so a fenced *example* row or `## H2`
    heading is never treated as a real backlog row/horizon (F251 #3 — the
    `--fix` path used to extract fenced example rows out of their code block,
    splitting it, and let fenced `## H2` lines flip the live horizon)."""
    fenced: set[int] = set()
    in_fence = False
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fenced.add(i)
            in_fence = not in_fence
            continue
        if in_fence:
            fenced.add(i)
    return fenced


def backlog_entries(backlog_file: Path,
                    vault_index: dict[str, list[Path]]) -> list[BacklogEntry]:
    """Parse {slug} Backlog.md; return list of BacklogEntry in source order."""
    if not backlog_file.is_file():
        return []
    try:
        text = backlog_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    lines = text.splitlines()
    fenced = _fenced_line_indices(lines)  # F251 #3 — skip fenced example rows/headings
    entries: list[BacklogEntry] = []
    current_horizon = ""
    # Pre-compute all links in the file for efficient lookup by line.
    file_links = links_in_file(backlog_file, vault_index)
    links_by_line: dict[int, list[LinkEntry]] = {}
    for link in file_links:
        links_by_line.setdefault(link.source_line, []).append(link)
    for line_num, line in enumerate(lines, start=1):
        if (line_num - 1) in fenced:
            continue
        m = HEADING_RE.match(line)
        if m and m.group(1) == "##":
            current_horizon = m.group(2)
            continue
        opener = ROW_OPENER_RE.match(line)
        if opener and current_horizon:
            identifier = opener.group(1)
            status = _detect_status(line)
            link = None
            row_links = links_by_line.get(line_num, [])
            if row_links:
                link = row_links[0]
            entries.append(BacklogEntry(
                source_file=backlog_file,
                source_line=line_num,
                identifier=identifier,
                horizon=current_horizon,
                status=status,
                link=link,
                raw_body=line,
                links=row_links,
            ))
    return entries


# A row document's basename comes in three permanently-coexisting forms, and
# `_arrow_target` knew only the first (see `_basename_is_own_doc`):
#
#   F332 — Title        legacy, everything before 2026-08-02
#   TINK F332 - Title   F298, the one morning that convention lasted
#   TINK332 - Title     F300, current — the kind letter is DROPPED
#
# Both dashes appear in the wild across the middle form, so both are accepted.
_OWN_DOC_LETTERED_RE = re.compile(
    r"^(?:[A-Za-z][A-Za-z0-9]*\s+)?([A-Za-z])(\d+)\s+[—-]\s")
_OWN_DOC_FUSED_RE = re.compile(r"^[A-Za-z]+(\d+)\s+[—-]\s")
_ROW_ID_RE = re.compile(r"^([A-Za-z])(\d+)$")


def _basename_is_own_doc(link: LinkEntry, identifier: str) -> bool:
    """True when `link` targets the row's OWN document, in any of the three
    naming conventions that coexist permanently in the vault.

    `_arrow_target` decided this with `basename.startswith(f"{identifier} ")` —
    a test written against the legacy `F332 — Title` basename, which is the
    only form that puts the row's identifier at the head of the filename. F298
    moved the slug in front of it and F300 dropped the kind letter entirely, so
    every row whose doc carries either later convention read as having NO own
    doc. Callers then fall through to `_row_inline_q_count`, which is 0 on
    exactly those rows — migrating a row is what moves its questions out of it.

    Found 2026-08-19 by C57, whose `unhosted` shape fired on eight fully
    migrated TINK rows (F300 form) and on SONAR F006 (F298 form), reporting the
    migration as the thing it fixes. Behind that false positive, C24, C48 and
    C50 had been silently passing vault-wide on the same rows for the same
    reason: they were asking a question about a document they never found.

    The fused form carries no kind letter, so its number is matched first and
    the letter confirmed from the doc's H1 (`feature_number` reads it). An
    unresolved link has no H1 to read, and there the number match stands alone:
    slug+number is unique within an anchor by construction.
    """
    base = link.target_basename or ""
    want = _ROW_ID_RE.match(identifier or "")
    if not want:
        return False
    letter, number = want.group(1).upper(), int(want.group(2))
    m = _OWN_DOC_LETTERED_RE.match(base)
    if m:
        return m.group(1).upper() == letter and int(m.group(2)) == number
    m = _OWN_DOC_FUSED_RE.match(base)
    if not m or int(m.group(1)) != number:
        return False
    if link.target_file_path is None:
        return True
    got = _ROW_ID_RE.match(feature_number(base, link.target_file_path) or "")
    return bool(got) and got.group(1).upper() == letter \
        and int(got.group(2)) == number


def _arrow_target(e: BacklogEntry) -> Optional[LinkEntry]:
    """T012: resolve the row's OWN doc — the arrow-form `→ [[…]]` link.

    `e.link` is the row's FIRST wiki-link of any form, which may be an
    in-prose mention (F230's first link was `[[SKA Backlog#^F229|F229]]`;
    the arrow doc-link came later — C24 counted Qs from the wrong file and
    --fix wrote a wrong `[2 Questions]` bracket). Selection among arrow
    links: the LAST one whose basename opens with the row's own identifier
    (`F230 — …` for row F230 — the own-doc form, wherever it sits in the
    body). When no arrow is the row's own doc, return None (F251 #2 — see
    below); callers then count the row's own inline Q sub-bullets.
    Returns None when the row has no OWN-doc arrow link.
    """
    scan = _strip_code_spans(e.raw_body)
    arrows: list[LinkEntry] = []
    for link in e.links:
        start = link.source_col_start - 1
        if scan[start:start + len(link.raw)] != link.raw:
            continue  # column bookkeeping mismatch — don't guess
        if re.search(r"→\s+$", scan[:start]):
            arrows.append(link)
    if not arrows:
        return None
    own = [l for l in arrows
           if (l.target_basename or "").startswith(f"{e.identifier} ")
           or _basename_is_own_doc(l, e.identifier)]
    # F251 #2 — when NO arrow is the row's OWN doc, return None instead of
    # falling back to arrows[0] (an unrelated prose `→ [[…]]` mention or a
    # `→ [[{slug} Backlog#^id]]` self-ref). A wrong fallback made C23/C24/
    # `--fix`/banner run extract_q_entries on the wrong file — counting 0 and
    # rewriting a live [Questions] row to [Ready], or counting every inline Q
    # in the whole backlog. Callers treat None as "no own-doc" and fall through
    # to _row_inline_q_count.
    return own[-1] if own else None


def _row_inline_q_count(e: BacklogEntry) -> int:
    """Count pending inline `- **Q<n> —` sub-bullets belonging to row e ONLY.

    T012 secondary defect: `extract_q_entries(backlog, container)` scans the
    WHOLE backlog file regardless of container, so two Questions T-rows each
    counted both rows' Qs. Scope here is the row's own sub-bullet span — the
    lines after the row up to the next top-level bullet, heading, or EOF
    (same forward-scan as C44).

    T086: PENDING is now a real distinction here, and it was not before. A
    row's answered questions stay in the row, below a `- **Resolved**` zone
    head, keeping their `- **Q<n> —` header exactly as the doc-side archive
    keeps its own — so counting every header would have this check report a
    fully-answered row as still asking, and C24's `--fix` would write the
    bracket back up on every run. `be.row_pending_q_lines` is the boundary,
    shared with `state`'s resolve verb and the Questions-promise gate so the
    three cannot disagree about where pending ends."""
    try:
        lines = e.source_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return 0
    span = []
    for nxt in lines[e.source_line:]:  # e.source_line is 1-indexed; starts on the next line
        if HEADING_RE.match(nxt) or re.match(r"^- \*\*", nxt):
            break
        span.append(nxt)
    return sum(1 for l in row_pending_q_lines(span) if Q_HEADER_RE.match(l))


def _row_has_next(e: BacklogEntry) -> bool:
    """True if row e carries a `- **Next:**` companion sub-bullet (the F171
    no-user next-action). F250 #10 — the C23/C24 `--fix` promotes a zero-pending-Q
    row to [Ready], but a [Ready] row with no `Next:` is the exact state F171
    forbids (and audit-q's `--fix` writes the bracket directly, bypassing the
    state write-path's F171 gate). So the promotion to [Ready] is gated on this;
    without a Next the row stays [Designing] and the check surfaces it as
    needing a Next rather than auto-creating the forbidden state."""
    try:
        lines = e.source_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return False
    for nxt in lines[e.source_line:]:  # 1-indexed source_line → starts on next line
        if HEADING_RE.match(nxt) or re.match(r"^- \*\*", nxt):
            break
        if re.match(r"^\s+-\s+\*\*Next:\*\*", nxt):
            return True
    return False


# ============================================================
# Check C1 — link existence (against Q.md)
# ============================================================


def check_c1_link_existence(qmd_links: list[LinkEntry]) -> list[Finding]:
    findings: list[Finding] = []
    for link in qmd_links:
        if not link.target_resolves:
            findings.append(Finding(
                severity="error",
                surface_file=link.source_file,
                surface_line=link.source_line,
                code="C1",
                message=f"link {link.raw} does not resolve "
                        f"(basename '{link.target_basename}' not in vault)",
                mechanically_fixable=False,
            ))
        elif link.target_anchor_resolves is False:
            anchor_kind = "heading" if link.target_heading else "block-id"
            anchor_val = link.target_heading or link.target_block_id
            findings.append(Finding(
                severity="error",
                surface_file=link.source_file,
                surface_line=link.source_line,
                code="C1",
                message=f"link {link.raw} resolves to file but {anchor_kind} "
                        f"'{anchor_val}' missing in target",
                mechanically_fixable=False,
            ))
    return findings


# ============================================================
# Check C54 — a Q.md banner's label and its link target are the same anchor
# ============================================================

# The three shapes the render's fallback chain can land on, longest first so
# `{X} queries` is stripped before the bare-`{X}` case can claim it.
_QMD_BANNER_TARGET_SUFFIXES = (" queries", " Triage")
_QMD_BANNER_RE = re.compile(
    r"^# \[[^\]]*\]\s+\[\[([^|\]#]+)(?:#[^|\]]*)?\|([^\]]+)\]\]")


def check_c54_banner_label_matches_target(qmd_text: str) -> list[Finding]:
    """C54 (T154) — every `# [..] [[X queries|LABEL]]` block in Q.md must link
    to the anchor it is labelled with.

    C1 tests whether the target RESOLVES, and C22 extends that same existence
    test to other files — so a banner pointing at a real file belonging to a
    DIFFERENT anchor passes both silently. That is not hypothetical: `SEEK`, an
    anchor that has never existed, sat in Q.md reporting `Runnable 7` because
    its banner linked to `[[SONAR queries]]`. It did not link to nothing; it
    linked to somebody else's numbers.

    Why it earns a rule rather than a one-off repair: LUMEN T021's starvation
    logic picks which under-served anchor gets a morning Decisions slot by
    reading question counts off exactly these banners, and Daybreak's Runnable
    line reads them too. A mislabelled block does not merely look untidy — it
    lends a real anchor's numbers to a name that owns none of them, and both
    consumers believe it.

    Case is not a mismatch. Obsidian and APFS both resolve case-insensitively,
    so `[[Tink queries|TINK]]` reaches the same file TINK's own banner does;
    that is case drift, which T138 ruled cosmetic and gave its own check. This
    rule fires only when the two names are different anchors.

    Not mechanically fixable: the repair is either to relabel the block or to
    repoint it, and only the author knows which name was the typo.
    """
    findings: list[Finding] = []
    for i, line in enumerate(qmd_text.splitlines(), start=1):
        m = _QMD_BANNER_RE.match(line)
        if not m:
            continue
        target, label = m.group(1).strip(), m.group(2).strip()
        prefix = target
        for suffix in _QMD_BANNER_TARGET_SUFFIXES:
            if prefix.endswith(suffix):
                prefix = prefix[:-len(suffix)]
                break
        if prefix.casefold() == label.casefold():
            continue
        findings.append(Finding(
            severity="error",
            surface_file=Q_MD,
            surface_line=i,
            code="C54",
            message=(
                f"banner labelled '{label}' links to '{target}', which belongs "
                f"to '{prefix}' — the block reports {prefix}'s counts under "
                f"{label}'s name. C1 passes it because the target resolves. "
                f"Either relabel the block or repoint it (T154)"
            ),
            mechanically_fixable=False,
        ))
    return findings


def _scope_to_block_id_region(text: str, block_id: str) -> str:
    """Return the lines from `^<block_id>`-bearing row up to the next
    bullet-row or H2. Used by C2 (and backlog-edit's Q-marker check) to
    scope the Q-marker search to a specific row's region when the link
    carries a `#^<block-id>` anchor.

    A row's region:
      - starts at the line DEFINING `^<block_id>` (case-sensitive)
      - includes any indented sub-bullets immediately after it
      - ends at the next top-level bullet, the next H2, or EOF

    "Defining" is end-of-line, per Obsidian's block-id syntax. A bare
    `marker in line` also matched *references* — a `[[Doc#^T041|T041]]`
    wiki-link in some earlier row's prose — and since the scan takes the
    first hit, the region became that unrelated row (MUX T041, 2026-08-02:
    F250's body linked `#^T041`, so C46 scoped to F250's one-line Next and
    reported the T041 row as carrying no questions). Anchoring to the
    definition makes the reference inert.
    """
    lines = text.splitlines()
    # `^id` at end of line, not preceded by a word char (so `^T04` never
    # matches a `^T041` definition) and not inside `[[…]]`.
    define_re = re.compile(r"(?:^|(?<=\s))\^" + re.escape(block_id) + r"\s*$")
    start = None
    for i, line in enumerate(lines):
        if define_re.search(line):
            start = i
            break
    if start is None:
        return ""  # block-id not found; no scope to check
    end = len(lines)
    for j in range(start + 1, len(lines)):
        s = lines[j]
        if s.startswith("## "):
            end = j
            break
        # Top-level bullet (no leading whitespace) starting with `- **`
        if re.match(r"^- \*\*", s):
            end = j
            break
        # H3 row (HA-style)
        if s.startswith("### "):
            end = j
            break
    return "\n".join(lines[start:end])


# ============================================================
# Check C2 — Q-marker existence at target (for `[Questions]` brackets)
# ============================================================


# ============================================================
# C56 (F269) — a Q.md section whose anchor resolves to nothing.
#
# Q.md is a stack of per-anchor sections, each opened by an H1 banner and each
# a copy of that anchor's rendered `{slug} queries.md`. A section is only ever
# WRITTEN by `queries-render.py {name}`; nothing ever removed one, and the
# reaper that would has a hole by construction — it needs the backlog to know
# the anchor is gone, and the anchor being gone is exactly when there is no
# backlog to read.
#
# Four such sections (`F244FIX`, `F244FIXP`, `F241FIX`, `CTEST`) were sitting
# in the live file on 2026-07-18, every one of them a fixture anchor from a
# test run whose teardown deleted the fixture directory but could not reach
# into Q.md. THAT LEAK IS CLOSED AT ITS SOURCE by `ANCHOR_VAULT_ROOT` — a
# fixture render now resolves a throwaway vault and cannot see this file. C56
# is the net under it, not the fix. Shipping the net alone would have left a
# checker permanently sweeping up after a bug nobody closed.
#
# Which is also why the check is written against the BACKLOG UNIVERSE rather
# than the scoped set: a section survives if some anchor still renders it, and
# `--scope backlog --anchor X` must not conclude that the other 34 sections
# are orphans. Getting that backwards would delete the whole file on the first
# per-anchor `--fix`.
# ============================================================

_C56_H1_RE = re.compile(
    r"^# \[[^\]]*\]\s+(?:\[\[[^|\]]*\|([^\]]+)\]\]|([A-Za-z][^\s]*(?:\s+[A-Z][^\s]*)*))\s+-\s")


def _qmd_sections(qmd_text: str) -> list[tuple[str, int, int]]:
    """(anchor label, first line index, end line index) per H1 section.

    End is exclusive and runs to the next H1 or EOF, so a section carries
    everything the render put under it. Lines above the first H1 are the file's
    own preamble and belong to no section.
    """
    lines = qmd_text.splitlines()
    starts: list[tuple[str, int]] = []
    for i, line in enumerate(lines):
        m = _C56_H1_RE.match(line)
        if m:
            starts.append(((m.group(1) or m.group(2) or "").strip(), i))
    out = []
    for k, (label, i) in enumerate(starts):
        end = starts[k + 1][1] if k + 1 < len(starts) else len(lines)
        out.append((label, i, end))
    return out


def check_c56_qmd_orphan_section(qmd_text: str,
                                 all_backlogs: dict[str, Path]) -> list[Finding]:
    """C56 (F269): every Q.md H1 section must belong to a live anchor."""
    findings: list[Finding] = []
    known = {n.casefold() for n in all_backlogs}
    for label, start, _end in _qmd_sections(qmd_text):
        if not label or label.casefold() in known:
            continue
        findings.append(Finding(
            severity="error", surface_file=Q_MD, surface_line=start + 1,
            code="C56",
            message=(
                f"Q.md section '{label}' belongs to no anchor — no "
                f"`{label} Backlog.md` renders in the vault, so nothing will "
                f"ever refresh or remove this section and its counts are "
                f"frozen at whatever the last render left. Usually a fixture "
                f"anchor whose directory was deleted while its spliced section "
                f"stayed behind. `--fix` prunes the section."),
            mechanically_fixable=True))
    return findings


def apply_c56_fix(qmd_file: Path, all_backlogs: dict[str, Path]) -> list[str]:
    """Delete every orphan section from Q.md. Returns one log line per prune.

    Deletes bottom-up so each span stays valid as earlier ones are removed,
    and rewrites only if something actually changed — a no-op write would
    bump the mtime and re-fire the watchers for nothing.
    """
    try:
        text = qmd_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    lines = text.splitlines()
    known = {n.casefold() for n in all_backlogs}
    spans = [(label, s, e) for label, s, e in _qmd_sections(text)
             if label and label.casefold() not in known]
    if not spans:
        return []
    log = []
    for label, s, e in sorted(spans, key=lambda t: t[1], reverse=True):
        del lines[s:e]
        log.append(f"  C56 — pruned orphan Q.md section '{label}' "
                   f"({e - s} lines)")
    qmd_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    _selffire(qmd_file)
    return list(reversed(log))


def check_c2_q_marker_existence(qmd_links: list[LinkEntry],
                                qmd_text: str) -> list[Finding]:
    """For every Q.md line carrying `[N Questions]` bracket, verify the link
    target contains at least one Q-marker."""
    findings: list[Finding] = []
    lines = qmd_text.splitlines()
    links_by_line: dict[int, list[LinkEntry]] = {}
    for link in qmd_links:
        links_by_line.setdefault(link.source_line, []).append(link)
    for line_num, line in enumerate(lines, start=1):
        if "Questions" not in line:
            continue
        # Match bracket containing "Questions"
        m = re.search(r"\[(\d*\s*)Questions?\]", line)
        if not m:
            continue
        row_links = links_by_line.get(line_num, [])
        if not row_links:
            continue
        # Use the first link as the target (skip Q.md-internal heading-anchor refs)
        primary_link = None
        for link in row_links:
            if not (link.kind == "wiki" and link.target_basename == "Q"):
                primary_link = link
                break
        if not primary_link:
            # F103 — Q.md row carries [Questions] bracket but has NO non-Q-internal
            # wiki-link. The promise cannot be satisfied; that is an error.
            findings.append(Finding(
                severity="error",
                surface_file=Q_MD,
                surface_line=line_num,
                code="C2",
                message=(
                    f"[Questions] bracket at line {line_num} but row has no "
                    f"wiki-link to a Q-marker target"
                ),
                mechanically_fixable=False,
            ))
            continue
        if not primary_link.target_resolves:
            # F103 — Q.md row's link target does not resolve. Was previously
            # silently skipped (the B-roots-reconcile failure 2026-06-02).
            # Per user direction: any failure to find the questions is an error.
            findings.append(Finding(
                severity="error",
                surface_file=Q_MD,
                surface_line=line_num,
                code="C2",
                message=(
                    f"[Questions] bracket at line {line_num} but linked target "
                    f"[[{primary_link.target_basename}]] does not resolve "
                    f"(broken link = broken promise)"
                ),
                mechanically_fixable=False,
            ))
            continue
        target_file = primary_link.target_file_path
        assert target_file is not None  # target_resolves implies this
        try:
            target_text = target_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        # F103 — scope to the row's region when the link uses a block-id.
        # `[[<file>#^<row-id>|...]]` is a promise that the Q-markers live IN
        # that row, not somewhere else in the same file. Without scoping,
        # a row with zero inline Qs passes because the file has Q-markers
        # elsewhere (the B-roots-reconcile failure 2026-06-02).
        if primary_link.target_block_id:
            target_text = _scope_to_block_id_region(
                target_text, primary_link.target_block_id
            )
        # Existence-check only — count NOT required to match
        if not Q_MARKER_RE.search(target_text):
            findings.append(Finding(
                severity="error",
                surface_file=primary_link.source_file,
                surface_line=line_num,
                code="C2",
                message=f"[Questions] bracket at line {line_num} but target "
                        f"{target_file.name} contains no Q<n> markers",
                mechanically_fixable=False,
            ))
    return findings


# ============================================================
# Check C4 — stale `[Done]` rows in horizon H2s → auto-move to `## Done`
# ============================================================


def check_c4_stale_done(entries: list[BacklogEntry]) -> list[Finding]:
    findings: list[Finding] = []
    for entry in entries:
        if entry.horizon not in LIVE_HORIZON_H2S:
            continue
        # Bracket starts with 'Done' → stale
        if entry.status.startswith("Done"):
            findings.append(Finding(
                severity="warning",
                surface_file=entry.source_file,
                surface_line=entry.source_line,
                code="C4",
                message=f"row '{entry.identifier}' has [Done] bracket in "
                        f"## {entry.horizon} (stale; should be in ## Done)",
                mechanically_fixable=True,
            ))
    return findings


def _row_block_span(lines: list[str], idx: int) -> tuple[int, int]:
    """(content_end, delete_end) for the backlog row whose header is lines[idx].

    A row runs to the next indent-0 non-blank line or the next `## ` H2 — the
    same boundary `state`'s `_row_span` and `backlog-edit.py`'s `scan_backlog`
    use. It does NOT end at the first blank line.

    T080 (MUX, 2026-08-08). Both movers here used to stop at the first
    non-indented line and swallow it if it was blank. A blank line is legal
    INSIDE a row — audit-q's own **C20 requires** one between consecutive Q
    groups — so the scan split exactly the rows that were correctly formatted:
    a two-Q T073 moved to `## Later` carrying only its header and Q1, while
    Q2's five lines stayed behind under `## Now`, orphaned from any row. The
    move reported success. Nothing here noticed; C34 caught the orphan only
    because it happened to land in a horizon C34 inspects, and `--fix` would
    have re-inserted the blank if anyone deleted it to work around this.

    `content_end` is exclusive and stops after the row's last non-blank line,
    so interior blanks travel with the row and trailing ones do not.
    `delete_end` additionally swallows ONE blank so the seam left behind in the
    source section does not double up.
    """
    last = idx
    j = idx + 1
    while j < len(lines):
        line = lines[j]
        if line.startswith("## "):
            break
        if not line.strip():          # blank — legal inside a row; keep scanning
            j += 1
            continue
        if line.startswith("  ") or line.startswith("\t"):
            last = j
            j += 1
            continue
        break                          # indent-0 content — the next row starts here
    content_end = last + 1
    delete_end = content_end
    if delete_end < len(lines) and not lines[delete_end].strip():
        delete_end += 1
    return content_end, delete_end


def apply_c4_fix(backlog_file: Path,
                 entries: list[BacklogEntry]) -> tuple[bool, list[str]]:
    """Move stale [Done] rows to top of ## Done. Returns (changed, log)."""
    stale = [e for e in entries
             if e.horizon in LIVE_HORIZON_H2S and e.status.startswith("Done")]
    if not stale:
        return False, []
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines(keepends=False)
    except (OSError, UnicodeDecodeError):
        return False, []
    # Sort stale rows by source line descending so removing doesn't shift indices
    stale_sorted = sorted(stale, key=lambda e: e.source_line, reverse=True)
    extracted_rows: list[str] = []
    # Extract each stale row (and any continuation indented sub-bullets / blank-prefix-of-next)
    for entry in stale_sorted:
        idx = entry.source_line - 1
        if idx >= len(lines):
            continue
        # The row is everything through its last indented sub-bullet — interior
        # blanks included (T080); one trailing blank is deleted for separation.
        content_end, delete_end = _row_block_span(lines, idx)
        row_lines: list[str] = lines[idx:content_end]
        del lines[idx:delete_end]
        extracted_rows.insert(0, "\n".join(row_lines).rstrip("\n"))
    # Find ## Done H2 line (skip fenced example headings — F251 #3)
    fenced = _fenced_line_indices(lines)
    done_h2_idx = None
    for i, line in enumerate(lines):
        if i in fenced:
            continue
        if line.strip() == "## Done":
            done_h2_idx = i
            break
    if done_h2_idx is None:
        # No ## Done — append one at the end
        lines.extend(["", "", "## Done", ""])
        done_h2_idx = len(lines) - 2
    # Insert extracted rows at top of ## Done (just after the H2 line + blank)
    insert_at = done_h2_idx + 1
    # Skip one blank line if present
    while insert_at < len(lines) and lines[insert_at] == "":
        insert_at += 1
    log = []
    for row_block in extracted_rows:
        # Insert the row + a trailing blank line, then advance insert_at past
        # this block. F251 #8 — without the advance, every block was inserted at
        # the same fixed offset, so multiple stale rows landed in ## Done in
        # REVERSED source order; advancing preserves their original order.
        block_lines = row_block.split("\n")
        for offset, row_line in enumerate(block_lines):
            lines.insert(insert_at + offset, row_line)
        lines.insert(insert_at + len(block_lines), "")
        insert_at += len(block_lines) + 1
        log.append(f"moved to ## Done: {row_block.splitlines()[0][:80]}")
    new_text = "\n".join(lines)
    # Preserve trailing newline if original had one
    if not new_text.endswith("\n"):
        new_text += "\n"
    backlog_file.write_text(new_text, encoding="utf-8")
    _selffire(backlog_file)
    return True, log


# ============================================================
# Checks C6–C12 — ask-format compliance (B16)
# ============================================================
# C6: every Q has block-ID ^<container>-Q<n>           (auto-fix)
# C7: external Q references use block-ID link form     (report only)
# C8: no embedded prose alternatives in Q line          (report only)
# C9: every Q has Recommendation with Strong/Lean/None  (report only)
# C10: Recommendation outdented to Q's indent level     (auto-fix)
# C12: [Verify-by] rows include "Naturally exercised by:" (report only)
# C19: option sub-bullets each on own line, labeled (A)/(B)/...  (report only)
# C20: blank line after Recommendation, separating Q groups      (report only)
# C21: ## Open Questions H2 with zero pending Qs (Phase 2 missed) (report only)
def _dedupe_paths(paths: list[Path]) -> list[Path]:
    """Order-preserving de-duplication of a check's file scope.

    Scopes here are assembled by concatenating overlapping sources (ask-format
    files, anchor backlogs, queries files), and the same file reaching a check
    twice produces every finding twice. Resolve before comparing so two spellings
    of one file — a symlinked skills tree, a `..` segment — collapse to one entry
    rather than surviving as a near-duplicate that looks like a second defect."""
    seen: set[Path] = set()
    out: list[Path] = []
    for p in paths:
        try:
            key = p.resolve()
        except OSError:
            key = p
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


# C22: link existence in feature docs / backlogs (extends C1's Q.md scope) (report only)
# C23: [Designing] must resolve to [N Questions] or [Ready] — never [Designing] alone (auto-fix)
# (C11 — Verify 4-piece layout — deferred; too heuristic for v1.)


def find_ask_format_files(
    anchor_backlogs: dict[str, Path],
    vault_index: Optional[dict[str, list[Path]]] = None,
    reachable_only: bool = True,
) -> list[tuple[str, Path]]:
    """For each anchor, yield (container_id, file_path) pairs for every file
    that might contain ask-format Qs.

    Container IDs:
    - Feature doc F089-...md → 'F089'
    - Anchor queries file '<NAME> queries.md' → '<NAME>' (authored anchor-level Qs)

    By default (`reachable_only=True`, per user direction 2026-05-26): only
    audit feature docs that are *linked from the anchor's backlog*. Orphan
    feature docs in `Features/` but not reachable via backlog wiki-links are
    skipped — they aren't navigable from Q.md, so the user can't click into
    them, and their drift doesn't matter to the dashboard. Requires `vault_index`
    to resolve wiki-link basenames.

    With `reachable_only=False`, falls back to the original behavior: glob every
    `Features/F*.md`. Used by `--scope all` for vault-wide cleanup sweeps.
    """
    out: list[tuple[str, Path]] = []
    for name, backlog_file in anchor_backlogs.items():
        if reachable_only and vault_index is not None:
            # Reachability-limited: walk backlog wiki-links, pick out F<n> targets.
            # Each reachable feature doc audited once.
            seen_paths: set[Path] = set()
            for link in links_in_file(backlog_file, vault_index):
                if not link.target_resolves or link.target_file_path is None:
                    continue
                stem = link.target_file_path.stem
                # Feature doc: stem starts with `F<NNN> — `, or the fused
                # `{SLUG}<NNN> - ` form — which since 2026-08-19 a T-doc also
                # uses, so the letter must come from the file, not the name.
                fnum = feature_number(stem, link.target_file_path)
                if fnum:
                    if link.target_file_path not in seen_paths:
                        seen_paths.add(link.target_file_path)
                        out.append((fnum, link.target_file_path))
                    continue
            # Always include `{slug} queries.md` if it exists — anchor-level Qs are
            # authored directly there (there is no `{slug} Questions.md`).
            # extract_q_entries picks up only the authored `**Q<n>` bullets in
            # `## Questions`; rendered pointer lines and resolutions are ignored.
            queries_file = backlog_track_dir(backlog_file) / f"{name} queries.md"
            if queries_file.is_file() and queries_file not in seen_paths:
                out.append((name, queries_file))
        else:
            # Vault-wide: every F<n>.md in the anchor's Features/ folder.
            # F142 transition — features live in the new `{name} Design/{name}
            # Features/` location (Design is a sibling of `{name} Track/`) or the
            # legacy `{name} Features/` sibling of the backlog. Glob both.
            track_dir = backlog_track_dir(backlog_file)  # {name} Track/ (F329 folder-doc aware)
            anchor_root = track_dir.parent           # Design/Track siblings
            feature_dirs = [
                anchor_root / f"{name} Design" / f"{name} Features",  # new canonical
                track_dir / f"{name} Features",                       # legacy sibling
                anchor_root / f"{name} Features",                     # older flat variant
            ]
            seen_feat: set[Path] = set()
            for features_dir in feature_dirs:
                if not features_dir.is_dir():
                    continue
                # Flat form plus the folder-doc upgrade (`F015 — T/F015 — T.md`).
                folder_docs = [p for p in features_dir.glob("F*/F*.md")
                               if p.stem == p.parent.name]
                for feature_file in sorted(list(features_dir.glob("F*.md"))
                                           + folder_docs):
                    if feature_file in seen_feat:
                        continue
                    seen_feat.add(feature_file)
                    fnum = feature_number(feature_file.stem, feature_file)
                    if fnum:
                        out.append((fnum, feature_file))
            queries_file = backlog_track_dir(backlog_file) / f"{name} queries.md"
            if queries_file.is_file():
                out.append((name, queries_file))
        # The backlog itself carries row-scoped Qs (F275 standalone Q rows and
        # inline `- **Q<n> —` sub-bullets on a row). They go through the same
        # ask-format gate on write, so they belong under the same checks here.
        # `extract_q_entries` re-attributes each to its hosting row, so the
        # container passed in is only a fallback.
        if backlog_file.is_file():
            out.append((name, backlog_file))
    return out


def extract_q_entries(file_path: Path, container_id: str) -> list[QEntry]:
    """Parse file_path; return one QEntry per pending `**Q<n>` bullet anywhere in the file.

    **Loose detection** — a Q-bullet is "pending" unless it appears inside a
    Resolved section (`## Resolved` H2 or `### Resolved` H3, case-insensitive).
    No gating on `## Open Questions` H2 spelling: the principle is "if the file
    contains `**Q<n> —` bullets in a non-Resolved area, treat them as the
    pending questions for this file." This catches lowercase `## Open questions`
    and any other H2 variant without playing whack-a-mole on titles.

    Recommendation matching: the first bullet line whose body starts with
    `**Recommendation:**` after a Q-header and before the next Q-header is the
    Recommendation for that Q.
    """
    if not file_path.is_file():
        return []
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    out: list[QEntry] = []
    in_h2_resolved = False  # inside `## Resolved` H2 (case-insensitive)
    in_h3_resolved = False  # inside `### Resolved` H3 (case-insensitive)
    in_fence = False        # inside ``` ... ``` (or ~~~) fenced code block
    pending_q: Optional[QEntry] = None
    # A Q hosted inside a backlog row belongs to that ROW, not to the file: its
    # block-ID is `^T001-Q1`, never `^HA-Q1`. Track the label of the row whose
    # body we are inside so such a Q gets the right container. `None` outside
    # any row, which is every Q in a feature doc or a queries file.
    row_container: Optional[str] = None

    def flush():
        nonlocal pending_q
        if pending_q is not None:
            out.append(pending_q)
            pending_q = None

    # Local heading regex — tolerates up to 3 leading spaces per CommonMark
    # ATX-heading rules. The global HEADING_RE anchors at line-start without
    # leading whitespace, which is intentional for some callers but causes
    # false negatives here for inline B-row `### Resolved` subsections nested
    # under bullet rows (visually indented with 2 spaces).
    _local_heading_re = re.compile(r"^( {0,3})(#{1,6})\s+(.+?)\s*$")
    for line_num, line in enumerate(lines, start=1):
        # Track fenced-code-block state. Format-spec docs (F068, F025, F026)
        # show `**Q1 — ...**` bullets as illustrations inside ``` fences — they
        # are examples, not real pending questions. Same fence-tracking pattern
        # as link-resolution and module-doc scans elsewhere in this file.
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Track which backlog row (if any) we are inside, so a Q hosted in a
        # row is attributed to the row rather than to the file. Any top-level
        # bullet opens a new row context; a bullet that is not a row opener
        # clears it, as does any heading (handled below).
        if line.startswith("- "):
            row_m = ROW_OPENER_RE.match(line)
            row_container = row_m.group(1) if row_m else None
        # Track Resolved-section state via H2/H3. Any new H2 resets H3 context.
        # A line is in a Resolved area iff in_h2_resolved OR in_h3_resolved.
        heading_m = _local_heading_re.match(line)
        if heading_m:
            row_container = None
            level = len(heading_m.group(2))
            heading_text = heading_m.group(3).strip()
            if level == 2:
                flush()
                # Recognize the "Resolved" section and its common descriptive
                # variants ("Resolved decisions", "Resolved questions") so
                # already-decided Q-records there aren't mis-scanned as open Qs.
                # "Removed" is the soft-delete sibling (`state … remove`).
                in_h2_resolved = heading_text.lower().startswith(
                    ("resolved", "removed"))
                in_h3_resolved = False
                continue
            if level == 3:
                flush()
                # F123: detect H3-form Q-header. If matched, start a new
                # pending H3-form Q (only when not in `## Resolved` H2);
                # in_h3_resolved is set False because the Q header replaces
                # any prior `### Resolved` context. Archived headers written
                # by `state … remove`/`resolve` — `### Q5 — … (removed …)` —
                # are records, not pending Qs (T024/F239 fix, 2026-07-14).
                h3_q_m = Q_HEADER_H3_RE.match(line)
                if h3_q_m and re.search(r"\((?:removed|resolved)\b",
                                        heading_text, re.IGNORECASE):
                    in_h3_resolved = True
                    continue
                if h3_q_m and not in_h2_resolved:
                    q_num = int(h3_q_m.group(1))
                    block_id_match = Q_BLOCK_ID_TRAILING_RE.search(line)
                    has_block_id = block_id_match is not None
                    block_id_value = block_id_match.group(1) if block_id_match else None
                    inline_alt = has_inline_alternatives(_strip_code_spans(line))
                    pending_q = QEntry(
                        source_file=file_path,
                        source_line=line_num,
                        indent="",
                        q_num=q_num,
                        container_id=container_id,
                        has_block_id=has_block_id,
                        block_id_value=block_id_value,
                        inline_alternatives=inline_alt,
                        shape="h3",
                    )
                    in_h3_resolved = False
                    continue
                in_h3_resolved = heading_text.lower().startswith(
                    ("resolved", "removed"))
                continue
            # Level 1 or 4+: leave state alone (rare in feature docs)
        if in_h2_resolved or in_h3_resolved:
            continue
        # Q-header bullet
        qm = Q_HEADER_RE.match(line)
        if qm:
            flush()
            # A header stamped `(resolved …)` / `(removed …)` is the record
            # `state resolve` / `state remove` leaves behind, not a pending Q.
            # The H3-form path has always skipped these (T024/F239); the bullet
            # form did not, so a resolved row-scoped Q kept reporting as pending
            # and its whole archived body read as malformed options.
            if re.search(r"\((?:removed|resolved)\b", line, re.IGNORECASE):
                continue
            indent = qm.group(1)
            q_num = int(qm.group(2))
            block_id_match = Q_BLOCK_ID_TRAILING_RE.search(line)
            has_block_id = block_id_match is not None
            block_id_value = block_id_match.group(1) if block_id_match else None
            # Strip inline code spans before checking for prose-alternatives.
            # `(A)/(B)/(C)` inside backticks is *describing* the format, not
            # an actual inline alternative — common in feature docs that
            # discuss the ask-format spec itself.
            inline_alt = has_inline_alternatives(_strip_code_spans(line))
            pending_q = QEntry(
                source_file=file_path,
                source_line=line_num,
                indent=indent,
                q_num=q_num,
                # A row-hosted Q is `^T001-Q1`, not `^HA-Q1` — attribute it to
                # the row. `row_container` is None everywhere but a backlog,
                # so feature docs and queries files keep the file container.
                container_id=(row_container if (row_container and indent)
                              else container_id),
                has_block_id=has_block_id,
                block_id_value=block_id_value,
                inline_alternatives=inline_alt,
                shape="bullet",
            )
            continue
        # Recommendation bullet (first match wins)
        if pending_q is not None and pending_q.recommendation_line == 0:
            rm = RECOMMENDATION_RE.match(line)
            if rm:
                pending_q.recommendation_line = line_num
                pending_q.recommendation_indent = rm.group(1)
                pending_q.recommendation_strength = (
                    rm.group(2).capitalize() if rm.group(2) else None
                )
                continue
            # F123: H3-form Qs may use paragraph-form Recommendation
            if pending_q.shape == "h3":
                rm_para = RECOMMENDATION_PARA_RE.match(line)
                if rm_para:
                    pending_q.recommendation_line = line_num
                    pending_q.recommendation_indent = ""
                    pending_q.recommendation_strength = rm_para.group(1).capitalize()
                    pending_q.recommendation_is_paragraph = True
    flush()
    return out


def _q_entry_is_row(q: QEntry) -> bool:
    """Is this Q header itself a backlog ROW, rather than a Q inside a container?

    The F275 feature-less question: `state define <anchor> Backlog Q+` mints a row
    that IS the question, sibling to `F`/`T`. Top-level indent in a `* Backlog.md`,
    with a container that is the anchor rather than an `F`/`T`/`B` handle — that
    combination occurs for nothing else.

    The QEntry-shaped twin of `_is_standalone_q_row`, which answers the same question
    from a `BacklogEntry.identifier`. Two functions because the views carry different
    evidence: a BacklogEntry knows its identifier is literally `Q004`, while a QEntry
    knows only its indent and container and must infer the rest. Deliberately NOT
    named alike — the first draft was, and the later definition shadowed the earlier
    one at import, so both call sites resolved to the wrong arity.
    """
    return (q.indent == ""
            and q.source_file.name.endswith("Backlog.md")
            and not re.match(r"^[FTB]\d", q.container_id or ""))


def _expected_block_id(q: QEntry) -> str:
    """The block-ID a Q header should carry — `^<container>-Q<n>`, except for a
    standalone Q ROW, which takes the backlog ROW convention `^Q<nnn>`.

    A standalone Q row is not a question *inside* a container — it IS a backlog row,
    and every backlog row anchors on its bare identifier (`^T116`, `^F275`). The
    queries render emits `#^Q004` accordingly, so the container form `^TINK-Q4`
    points at nothing: the reader clicks through to the top of the file, and C46
    then reports the row as carrying no questions.
    """
    if _q_entry_is_row(q):
        return f"Q{q.q_num:03d}"
    return f"{q.container_id}-Q{q.q_num}"


def check_c6_block_id_present(q_entries: list[QEntry]) -> list[Finding]:
    """C6: every Q has block-ID ^<container>-Q<n> (or `^Q<nnn>` for a Q row)."""
    findings: list[Finding] = []
    for q in q_entries:
        expected = _expected_block_id(q)
        if not q.has_block_id:
            findings.append(Finding(
                severity="warning",
                surface_file=q.source_file,
                surface_line=q.source_line,
                code="C6",
                message=f"Q{q.q_num} missing block-ID; expected ^{expected}",
                mechanically_fixable=True,
            ))
        elif q.block_id_value != expected:
            findings.append(Finding(
                severity="warning",
                surface_file=q.source_file,
                surface_line=q.source_line,
                code="C6",
                message=f"Q{q.q_num} block-ID '^{q.block_id_value}' should be '^{expected}'",
                mechanically_fixable=True,
            ))
    return findings


def apply_c6_fix(q_entries: list[QEntry]) -> list[str]:
    """Append / replace block-IDs for all C6-flagged Qs. Returns log."""
    log: list[str] = []
    by_file: dict[Path, list[QEntry]] = {}
    for q in q_entries:
        expected = _expected_block_id(q)
        if q.has_block_id and q.block_id_value == expected:
            continue
        by_file.setdefault(q.source_file, []).append(q)
    for file_path, qs in by_file.items():
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        changed = False
        for q in qs:
            idx = q.source_line - 1
            if idx >= len(lines):
                continue
            line = lines[idx]
            expected = _expected_block_id(q)
            # F251 #9 — a FOREIGN trailing block-id (a `^…` that is NOT the
            # `-Q<n>` form, e.g. `^F077-note`) is a live anchor with its own
            # inbound links. Stripping it would break those links; appending
            # after it would strand it mid-line (Obsidian honors only the last
            # `^id`). Neither is mechanically safe — skip and report so a human
            # relocates the anchor before the Q block-id is added.
            foreign = ANY_BLOCK_ID_TRAILING_RE.search(line)
            if foreign and not Q_BLOCK_ID_TRAILING_RE.search(line):
                log.append(
                    f"  {file_path.name}:{q.source_line} — SKIPPED (Q{q.q_num}): "
                    f"line ends with foreign block-id ^{foreign.group(1)}; move it "
                    f"to its own block before adding ^{expected} by hand"
                )
                continue
            # Strip any existing trailing ^…-Q<n> block-ID (right form or wrong)
            stripped = Q_BLOCK_ID_TRAILING_RE.sub("", line).rstrip()
            new_line = f"{stripped} ^{expected}"
            if new_line != line:
                lines[idx] = new_line
                changed = True
                log.append(
                    f"  {file_path.name}:{q.source_line} — set ^{expected} (Q{q.q_num})"
                )
        if changed:
            new_text = "\n".join(lines)
            if not new_text.endswith("\n"):
                new_text += "\n"
            file_path.write_text(new_text, encoding="utf-8")
            _selffire(file_path)
    return log


def check_c7_link_form(
    files_to_scan: list[Path],
    vault_index: dict[str, list[Path]],
) -> list[Finding]:
    """C7: external Q refs use block-ID link form.

    Heuristic: any link whose display text contains 'Q<n>' but whose link target
    has no block-ID component is a violation. Report-only (rewriting requires
    reading destination to find the matching Q — agent task).
    """
    findings: list[Finding] = []
    for file_path in files_to_scan:
        links = links_in_file(file_path, vault_index)
        for link in links:
            display = link.display_text or ""
            if not Q_REF_IN_DISPLAY_RE.search(display):
                continue
            # Skip when every Q-ref in the display is already attached to an
            # F-number (`F074 Q4`) — those are descriptive phrases that name a
            # Q in a DIFFERENT feature, not pointers to a Q in the link target.
            q_count = len(Q_REF_IN_DISPLAY_RE.findall(display))
            fq_count = len(F_REF_BEFORE_Q_RE.findall(display))
            if q_count > 0 and q_count == fq_count:
                continue
            if link.target_block_id is not None:
                continue  # already block-ID form
            findings.append(Finding(
                severity="warning",
                surface_file=link.source_file,
                surface_line=link.source_line,
                code="C7",
                message=(
                    f"link {link.raw} references Q<n> in display but lacks "
                    f"block-ID form (expected [[<file>#^<container>-Q<n>|...]])"
                ),
                mechanically_fixable=False,
            ))
    return findings


def check_c8_inline_alternatives(q_entries: list[QEntry]) -> list[Finding]:
    """C8: Q header must not carry its options inline — every option belongs on
    its own labeled sub-bullet. Fires when the header line holds ≥2 distinct
    option labels (`(A)` … `(D)`, case-folded), whether written as ask-format
    labels or as prose alternatives ('(a) X or (b) Y')."""
    findings: list[Finding] = []
    for q in q_entries:
        if q.inline_alternatives:
            findings.append(Finding(
                severity="warning",
                surface_file=q.source_file,
                surface_line=q.source_line,
                code="C8",
                message=(
                    f"Q{q.q_num} has options inline on the header line; each option "
                    f"belongs on its own labeled sub-bullet `- **(A)** ...`"
                ),
                mechanically_fixable=False,
            ))
    return findings


def check_c9_recommendation_present(q_entries: list[QEntry]) -> list[Finding]:
    """C9: every Q has a Recommendation bullet with Strong/Lean/None."""
    findings: list[Finding] = []
    for q in q_entries:
        if q.recommendation_line == 0:
            findings.append(Finding(
                severity="warning",
                surface_file=q.source_file,
                surface_line=q.source_line,
                code="C9",
                message=(
                    f"Q{q.q_num} missing Recommendation bullet "
                    f"(expected '- **Recommendation:** Strong|Lean|None ...')"
                ),
                mechanically_fixable=False,
            ))
        elif q.recommendation_strength is None:
            findings.append(Finding(
                severity="warning",
                surface_file=q.source_file,
                surface_line=q.recommendation_line,
                code="C9",
                message=(
                    f"Q{q.q_num} Recommendation lacks strength label "
                    f"(must be Strong / Lean / None)"
                ),
                mechanically_fixable=False,
            ))
    return findings


def check_c10_recommendation_outdent(q_entries: list[QEntry]) -> list[Finding]:
    """C10: Recommendation bullet at same indent as Q header (not nested).

    F123: N/A for H3-form Qs — there is no indent semantics to enforce
    (H3 + top-level Recommendation are both at column 0).
    """
    findings: list[Finding] = []
    for q in q_entries:
        if q.shape == "h3":
            continue
        if q.recommendation_line == 0 or q.recommendation_indent is None:
            continue
        # N/A for a standalone Q ROW, where C10 and R-backlog-03 collide head-on: a
        # Q row's header sits at indent 0 *because it is a backlog row*, so "same
        # indent as the header" puts the Recommendation at indent 0 too — where the
        # backlog parser reads it as its own top-level row and R-backlog-03 fails it
        # as ungroomed. Obeying either breaks the other; the construct is
        # unrepresentable until one yields, and it is this one, because nesting is
        # what makes the bullet belong to the row (T120).
        if _q_entry_is_row(q):
            continue
        if len(q.recommendation_indent) > len(q.indent):
            findings.append(Finding(
                severity="warning",
                surface_file=q.source_file,
                surface_line=q.recommendation_line,
                code="C10",
                message=(
                    f"Q{q.q_num} Recommendation nested "
                    f"(indent {len(q.recommendation_indent)}) — outdent to Q "
                    f"header level (indent {len(q.indent)})"
                ),
                mechanically_fixable=True,
            ))
    return findings


def apply_c10_fix(q_entries: list[QEntry]) -> list[str]:
    """Rewrite indent of nested Recommendation bullets to match Q indent."""
    log: list[str] = []
    by_file: dict[Path, list[QEntry]] = {}
    for q in q_entries:
        if q.shape == "h3":
            continue  # F123: C10 N/A for H3-form Qs
        if q.recommendation_line == 0 or q.recommendation_indent is None:
            continue
        # The fixer carried its own copy of C10's predicate, so teaching only the
        # CHECKER about standalone Q rows left this actively outdenting them back to
        # column 0 on every write — where R-backlog-03 fails the Recommendation as an
        # ungroomed row. The checker merely complained; the fixer rewrote the file
        # into the rejected shape and did it again after each repair (T120).
        if _q_entry_is_row(q):
            continue
        if len(q.recommendation_indent) > len(q.indent):
            by_file.setdefault(q.source_file, []).append(q)
    for file_path, qs in by_file.items():
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        changed = False
        for q in qs:
            idx = q.recommendation_line - 1
            if idx >= len(lines):
                continue
            line = lines[idx]
            stripped = line.lstrip()
            new_line = q.indent + stripped
            if new_line != line:
                lines[idx] = new_line
                changed = True
                log.append(
                    f"  {file_path.name}:{q.recommendation_line} — outdented "
                    f"Recommendation for Q{q.q_num}"
                )
        if changed:
            new_text = "\n".join(lines)
            if not new_text.endswith("\n"):
                new_text += "\n"
            file_path.write_text(new_text, encoding="utf-8")
            _selffire(file_path)
    return log


def check_c12_verify_by_rationale(
    anchor_backlogs: dict[str, Path],
) -> list[Finding]:
    """C12: every `[Verify-by YYYY-MM-DD]` row body includes 'Naturally exercised by:'."""
    findings: list[Finding] = []
    for backlog_file in anchor_backlogs.values():
        try:
            lines = backlog_file.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_num, line in enumerate(lines, start=1):
            if not VERIFY_BY_BRACKET_RE.search(line):
                continue
            # Body = the row line + any subsequent indented continuation lines
            body_text = line
            j = line_num  # next-line index (1-based line_num == 0-based j)
            while j < len(lines):
                nxt = lines[j]
                if nxt.startswith("  ") or nxt.startswith("\t"):
                    body_text += "\n" + nxt
                    j += 1
                elif nxt == "":
                    j += 1
                    continue
                else:
                    break
            if not NATURALLY_EXERCISED_RE.search(body_text):
                findings.append(Finding(
                    severity="warning",
                    surface_file=backlog_file,
                    surface_line=line_num,
                    code="C12",
                    message=(
                        "[Verify-by] row body missing 'Naturally exercised by: …' "
                        "rationale (required per ask-format § Deferred-by-use Verify)"
                    ),
                    mechanically_fixable=False,
                ))
    return findings


# C19: each Q's option sub-bullet on its own line, labeled (A)/(B)/...
# C20: blank line after Recommendation separating Q groups

# Accepts any of these option-label conventions at the start of a sub-bullet:
#   - **(A)** text   ← canonical (Ask skill spec, uppercase parens, bold)
#   - (A) text       ← uppercase parens, unbolded
#   - **A)** text    ← bold A)
#   - A) text        ← uppercase A) form (common in legacy docs)
#   - **A.** text    ← bold A.
#   - A. text        ← uppercase A. form
#   - (a) text       ← lowercase parens variants (also seen in legacy)
#   - a) text
#   - **(a)** text
# The audit's intent is "alternatives are labeled and live on their own line."
# All variants above meet that bar; the canonical form `- **(A)** ...` is
# encouraged elsewhere (Ask skill spec) but the audit no longer flags
# well-formed legacy variants. Case (upper/lower) is accepted equally.
OPTION_BULLET_RE = re.compile(
    r"^(\s+)-\s+\*{0,2}"             # bullet, then optional opening bold
    r"(?:"
    r"\(([A-Za-z][0-9]*)\)"          # (X) — paren-wrapped
    r"|([A-Za-z][0-9]*)[.)]"         # X. / X)
    r")"
    r"\*{0,2}"                       # optional closing bold
    r"(?:\s|$)"
)
SUB_BULLET_RE = re.compile(r"^(\s+)-\s+")
# Any list bullet, indent 0 included — SUB_BULLET_RE requires leading
# whitespace, so it cannot recognise a top-level sibling. Used to find where a
# Q's option zone ends.
ANY_BULLET_RE = re.compile(r"^(\s*)[-*+]\s+")
# Two option labels on the same line — only the bolded canonical form counts
# as evidence of an attempted (and malformed) option list. Bare parens like
# `(no)` and `(yes)` in prose would over-match the loosened form, so DOUBLE
# stays strict on `**(X)**` ... `**(X)**` per F076 original intent.
DOUBLE_OPTION_INLINE_RE = re.compile(
    r"\*\*\([A-Za-z][0-9]*\)\*\*.*?\*\*\([A-Za-z][0-9]*\)\*\*"
)


def check_c19_option_bullets(q_entries: list[QEntry]) -> list[Finding]:
    """C19: every option sub-bullet between Q header and Recommendation must
    be a labeled bullet `- **(A)** ...` on its own line.

    Catches:
    - Two option labels on the same line: `- **(A)** X. **(B)** Y.` → split needed.
    - Unlabeled sub-bullets that look like alternatives but lack a `(A)` label.

    Continuation lines (further indent) are skipped — they belong to the
    enclosing option."""
    findings: list[Finding] = []
    by_file: dict[Path, list[QEntry]] = {}
    for q in q_entries:
        by_file.setdefault(q.source_file, []).append(q)
    for file_path, qs in by_file.items():
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        qs_sorted = sorted(qs, key=lambda x: x.source_line)
        for i, q in enumerate(qs_sorted):
            start_line = q.source_line
            # End of this Q's options block: the Recommendation line (1-indexed),
            # or the next Q in the same file, or EOF.
            end_line = q.recommendation_line if q.recommendation_line else (
                qs_sorted[i + 1].source_line if i + 1 < len(qs_sorted) else len(lines) + 1
            )
            q_indent_len = len(q.indent)
            # …but never past the end of the block that HOSTS the Q. A Q with no
            # Recommendation line (which C9 flags separately) otherwise runs its
            # option zone to the next Q or to EOF, swallowing unrelated content.
            # Harmless in a feature doc, where the Qs are consecutive inside one
            # H2; wrong anywhere Qs are scattered — a backlog file, where the
            # next Q can be hundreds of rows away, has every intervening row's
            # prose sub-bullets read as this Q's malformed options. Options can
            # only be *more*-indented than the Q header, so the first heading or
            # the first bullet at or above the Q's own indent ends the zone.
            # An H3-form Q hosts its options at indent 0, so only a heading can
            # close its zone; a bullet-form Q is closed by either.
            closes_on_sibling_bullet = q.shape != "h3"
            for probe in range(start_line + 1, end_line):
                probe_line = lines[probe - 1]
                if probe_line.startswith("#"):
                    end_line = probe
                    break
                bullet_m = ANY_BULLET_RE.match(probe_line)
                if (closes_on_sibling_bullet and bullet_m
                        and len(bullet_m.group(1)) <= q_indent_len):
                    end_line = probe
                    break
            # F123: for H3-form Qs, options live at top-level (indent 0)
            # rather than nested. Use indent==0 (TOP_BULLET_RE) for option
            # detection; the unlabeled-sub-bullet flag fires when a
            # top-level bullet inside the H3 body lacks an `(X)` label
            # and the body is not a known annotation.
            is_h3 = (q.shape == "h3")
            for line_num in range(start_line + 1, end_line):
                line = lines[line_num - 1]
                # Two option labels on same line:
                if DOUBLE_OPTION_INLINE_RE.search(line):
                    findings.append(Finding(
                        severity="warning",
                        surface_file=file_path,
                        surface_line=line_num,
                        code="C19",
                        message=(
                            f"Q{q.q_num} options must each be on their own labeled "
                            f"sub-bullet; two `(X)` labels found on one line"
                        ),
                        mechanically_fixable=False,
                    ))
                    continue
                if is_h3:
                    # Top-level bullet detection inside H3 body
                    m_top = re.match(r"^-\s+", line)
                    if not m_top:
                        continue
                    # Inline Recommendation bullet inside H3 body — not an option
                    if RECOMMENDATION_RE.match(line):
                        continue
                    if not OPTION_BULLET_RE.match("  " + line):
                        # Reuse OPTION_BULLET_RE (it expects leading whitespace);
                        # prepend two spaces to satisfy its leading-indent group.
                        body = line.lstrip("- *").strip()
                        if body.startswith((
                            "Note:", "Context:", "Constraint:", "Background:",
                            # Pieces 6 and 7 of the Q group (F270, F275) — the
                            # two lines `state define` REFUSES to mint a Q
                            # without. C20 already treats both as part of the
                            # group; this list had not been told. Omitting them
                            # made every well-formed standalone Q arrive with
                            # two findings that cannot be fixed without making
                            # the row unmintable.
                            "Damage:", "On answer:",
                            "Recommendation",
                        )):
                            continue
                        findings.append(Finding(
                            severity="warning",
                            surface_file=file_path,
                            surface_line=line_num,
                            code="C19",
                            message=(
                                f"Q{q.q_num} top-level bullet not labeled as option "
                                f"`- **(A)** ...`; H3-form alternatives must be "
                                f"labeled (A)/(B)/... on their own lines"
                            ),
                            mechanically_fixable=False,
                        ))
                    continue
                # Sub-bullet at Q's option indent level but not labeled
                sub_m = SUB_BULLET_RE.match(line)
                if not sub_m:
                    continue
                sub_indent = len(sub_m.group(1))
                # Must be more-indented than the Q header (a true sub-bullet)
                if sub_indent <= q_indent_len:
                    continue
                # First option-line indent sets the "alternative-row" indent;
                # only flag at that indent (deeper sub-bullets are continuations).
                # Simplification: flag any sub-bullet exactly q_indent_len+2 that
                # lacks the `(LABEL)` shape and contains words suggesting it's
                # being attempted as an alternative.
                if sub_indent == q_indent_len + 2:
                    if not OPTION_BULLET_RE.match(line):
                        # Skip if it's clearly a non-alternative annotation
                        # (e.g., starts with a known prefix like `- **Note:**`).
                        body = line.lstrip("- *").strip()
                        if body.startswith((
                            "Note:", "Context:", "Constraint:", "Background:",
                            # Pieces 6 and 7 of the Q group (F270, F275) — the
                            # two lines `state define` REFUSES to mint a Q
                            # without. C20 already treats both as part of the
                            # group; this list had not been told.
                            "Damage:", "On answer:",
                            # Inline Recommendation lines are NOT options.
                            # Legacy docs sometimes have a rich inline Rec
                            # alongside the stub-Rec terminator; skip those.
                            "Recommendation",
                        )):
                            continue
                        findings.append(Finding(
                            severity="warning",
                            surface_file=file_path,
                            surface_line=line_num,
                            code="C19",
                            message=(
                                f"Q{q.q_num} sub-bullet not labeled as option `- **(A)** ...`; "
                                f"alternatives must be labeled (A)/(B)/... on their own lines"
                            ),
                            mechanically_fixable=False,
                        ))
    return findings


def check_c20_blank_after_recommendation(q_entries: list[QEntry]) -> list[Finding]:
    """C20: every Recommendation line must be followed by a blank line (or end-of-block),
    separating one Q group from the next."""
    findings: list[Finding] = []
    by_file: dict[Path, list[QEntry]] = {}
    for q in q_entries:
        by_file.setdefault(q.source_file, []).append(q)
    for file_path, qs in by_file.items():
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        qs_sorted = sorted(qs, key=lambda x: x.source_line)
        for q in qs_sorted:
            if q.recommendation_line == 0:
                continue
            # F123: H3-form Qs with paragraph-form Recommendation have no
            # indent semantics — continuation lines are at column 0 like
            # the Rec line itself; the strict outdent rule would false-fire.
            # The H2/H3 boundary between Qs is enforced separately by C21
            # and standard markdown structure.
            if q.shape == "h3" and q.recommendation_is_paragraph:
                continue
            # The Recommendation itself may span continuation lines (more-indented).
            # Find the end of the Recommendation block: walk forward while we see
            # blank lines OR lines indented more than the Recommendation.
            rec_line_num = q.recommendation_line
            rec_indent_len = len(q.recommendation_indent or "")
            # Compute the line after the Recommendation block ends.
            j = rec_line_num  # 1-indexed; next line is lines[j]
            while j < len(lines):
                nxt = lines[j]
                if nxt == "":
                    break  # blank line — required separator present
                nxt_indent = len(nxt) - len(nxt.lstrip())
                if nxt_indent > rec_indent_len:
                    j += 1
                    continue
                # F270: the `- **Damage:**` line is piece 6 of the Q group — it
                # sits at the SAME indent right after the Recommendation; it is
                # part of the group, not the next content. Skip it; the required
                # blank separator falls after Damage, not between Rec and Damage.
                # F275 adds `- **On answer:**` as piece 7 on the same footing:
                # `state define … Q+` hard-refuses a standalone Q row without it,
                # so every row the mint produces carries one — and flagging it here
                # meant the tool rejected its own output.
                # T160 adds `- **Risk of (X):**` as piece 8, on exactly the same
                # footing and for exactly the same reason: `state define` now
                # hard-refuses a Lean/Strong Q without one, so every Q the mint
                # produces carries it, and a C20 that did not know about it would
                # fire on the tool's own output — the T137 / T120 shape, a writer
                # and a checker holding different beliefs about one construct.
                if re.match(r"^\s*-\s+\*\*(Damage|On answer"
                            r"|Risk of \([A-Za-z]\w*\)):\*\*", nxt):
                    j += 1
                    continue
                # A non-blank, non-continuation line at same-or-less indent
                # immediately following the Recommendation block — flag it.
                findings.append(Finding(
                    severity="warning",
                    surface_file=file_path,
                    surface_line=j + 1,
                    code="C20",
                    message=(
                        f"Q{q.q_num} Recommendation must be followed by a blank line "
                        f"before the next Q group / non-continuation content"
                    ),
                    mechanically_fixable=False,
                ))
                break
    return findings


def check_c21_empty_open_questions(
    ask_format_files: list[tuple[str, Path]],
    q_entries: list[QEntry],
) -> list[Finding]:
    """C21: a `## Open Questions` H2 with zero top-level pending Q bullets is
    a Phase-2-transition-missed bug. All Qs resolved → the H2 should be deleted
    and resolutions migrated to a bottom `## Resolved` H2.

    Detected: file has `## Open Questions` heading but `extract_q_entries`
    found zero Q bullets in it (because all Qs are inside `### Resolved`)."""
    findings: list[Finding] = []
    q_entries_by_file: dict[Path, list[QEntry]] = {}
    for q in q_entries:
        q_entries_by_file.setdefault(q.source_file, []).append(q)
    for _, file_path in ask_format_files:
        try:
            text = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        oq_line = 0
        in_fence = False
        for line_num, line in enumerate(lines, start=1):
            # Skip code-fenced content — feature-doc-template illustrations
            # (e.g., F015) show `## Open Questions` inside ``` blocks as the
            # canonical template; those are not real Open Questions sections.
            stripped = line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            # F305: `## Open Items` is canonical; `## Open Questions` is the
            # legacy spelling, accepted forever (the writer renames on touch).
            if line.strip() in ("## Open Items", "## Open Questions"):
                oq_line = line_num
                break
        if oq_line == 0:
            continue
        # H2 exists. Did we find any pending Q bullets under it?
        if q_entries_by_file.get(file_path):
            continue
        # F305 hosting — the block may legitimately hold only V/U items
        # (extract_q_entries is Q-only BY DESIGN: verifications never enter
        # the bracket derivation). A pending V/U in the unresolved zone keeps
        # the block alive, else a V-only block reads as "Phase 2 missed" and
        # an agent deletes a live block. NOT open_questions_is_empty — that
        # counts a `### Resolved` pen as content, which is exactly the state
        # C21 exists to flag.
        rng = _be_mod._open_questions_range(lines)
        if rng is not None:
            _s, _e = rng
            pending_vu = False
            for _ln in lines[_s + 1:_e]:
                if _ln.strip() in ("### Resolved", "### Removed"):
                    break
                _m = _be_mod._ITEM_HEADER_BULLET_RE.match(_ln)
                if _m and _m.group(2) in ("V", "U"):
                    pending_vu = True
                    break
            if pending_vu:
                continue
        # H2 with zero pending items of any kind → Phase 2 missed.
        findings.append(Finding(
            severity="warning",
            surface_file=file_path,
            surface_line=oq_line,
            code="C21",
            message=(
                "open-items H2 has zero pending Qs (all in ### Resolved). "
                "Phase 2 transition missed — delete this H2 and migrate Resolved "
                "to a bottom `## Resolved` H2."
            ),
            mechanically_fixable=False,
        ))
    return findings


def check_c22_link_existence_extended(
    scope_files: list[Path],
    vault_index: dict[str, list[Path]],
) -> list[Finding]:
    """C22: extend C1's link-existence check beyond Q.md to feature docs +
    backlogs. C1 covers Q.md; C22 covers everything else where broken
    wiki-links are user-visible (feature docs, backlogs, queries.md files).

    Callers must pass a de-duplicated scope — see `_dedupe_paths`. This check
    walks whatever it is handed, so a file listed twice yields every one of its
    findings twice."""
    findings: list[Finding] = []
    for file_path in scope_files:
        for link in links_in_file(file_path, vault_index):
            if not link.target_resolves:
                findings.append(Finding(
                    severity="error",
                    surface_file=link.source_file,
                    surface_line=link.source_line,
                    code="C22",
                    message=(
                        f"link {link.raw} does not resolve "
                        f"(basename '{link.target_basename}' not in vault)"
                    ),
                    mechanically_fixable=False,
                ))
            elif link.target_anchor_resolves is False:
                anchor_kind = "heading" if link.target_heading else "block-id"
                anchor_val = link.target_heading or link.target_block_id
                findings.append(Finding(
                    severity="error",
                    surface_file=link.source_file,
                    surface_line=link.source_line,
                    code="C22",
                    message=(
                        f"link {link.raw} resolves to file but {anchor_kind} "
                        f"'{anchor_val}' missing in target"
                    ),
                    mechanically_fixable=False,
                ))
    return findings


# ============================================================
# C53 — anchor-name collisions (F281)
# ============================================================

# Structural collisions are declared, not inferred: a basename mandated by an
# external format is exempt. Deliberately a short allowlist and NOT a
# per-instance suppression — per-instance would let real collisions be silenced
# one at a time until the check means nothing (F281 § Exemption).
ANCHOR_COLLISION_EXEMPT_STEMS = {"skill", "readme", "claude", "index"}


def _is_anchor_page(path: Path) -> bool:
    """True when `path` is a folder's anchor page: `Foo/Foo.md` beside `Foo/.anchor`."""
    return path.stem == path.parent.name and (path.parent / ".anchor").is_file()


def _anchor_root_for_backlog(backlog: Path) -> Path | None:
    """The anchor tree a backlog belongs to — nearest enclosing `.anchor`, or None."""
    for cand in (backlog.parent, *backlog.parent.parents):
        if (cand / ".anchor").is_file():
            return cand
    return None


def _scope_c53_to_anchor(findings: list[Finding], root: Path | None) -> list[Finding]:
    """Keep only the collisions that live inside `root` (F292).

    C53 is computed over the whole vault index, because a basename collision is
    only visible vault-wide — that part is correct and stays. What was wrong is
    that the findings were then reported to WHOEVER asked. `audit-q --scope
    backlog --anchor SVP` returned 4 findings, none of them in SVP's tree, and
    since the F258 worklist counts findings, `state groom-list` never emptied and
    the F244 stop-gate fired forever — for SVP and for every other anchor at once.
    An anchor could not reach a groomed frontier no matter what it did.

    Filtering here rather than inside the check keeps the vault-wide computation
    intact and matches what C53 already intends: it deliberately emits one finding
    per colliding PAGE rather than one per group, `so QFix routing lands each half
    on its own anchor` (F281 Q1 (D)). Ownership was already per-page; only the
    delivery ignored it. Same principle as T052's own-anchor scoping of the
    continuation directive — a vault-wide run must not hand an agent someone
    else's work.
    """
    if root is None:
        return findings
    return [f for f in findings
            if f.surface_file == root or root in f.surface_file.parents]


def check_c53_anchor_name_collisions(
    vault_index: dict[str, list[Path]], vault_root: Path
) -> list[Finding]:
    """C53: two or more ANCHOR PAGES share a basename (F281).

    Reads the vault index audit-q already built rather than re-walking or
    shelling out to `ha --dump --format=collisions` — the index is
    basename -> paths, which is the collision data itself.

    One finding per colliding anchor page, not one per group, so QFix routing
    lands each half on its own anchor: the owning anchor of a colliding pair
    fixes it, never a central agent (F281 Q1 (D)).

    This is the enforcement half of R-naming-01's third clause (recast
    2026-08-02). That rule makes a file prefix OPTIONAL and requires one only
    where the basename would otherwise collide; the slug prefix is the
    mechanism, and this check is the property. The two were built independently
    and neither knew it was half of the other — R-naming-01 demanded a prefix
    on every file (39% of the vault in violation) while the uniqueness it was
    protecting went unstated. Uniqueness is vault-global, so it is checked here,
    where the index lives, and nowhere else: a per-file checker cannot see it,
    and a second index would be a second source of truth for the same fact.
    """
    findings: list[Finding] = []
    for stem, paths in sorted(vault_index.items()):
        if stem in ANCHOR_COLLISION_EXEMPT_STEMS or len(paths) < 2:
            continue
        # Resolve before de-duplicating: a symlinked tree can surface the same
        # file under two walk paths, which is not a collision.
        seen: dict[Path, Path] = {}
        for path in paths:
            if _is_anchor_page(path):
                seen.setdefault(path.resolve(), path)
        anchors = sorted(seen.values())
        if len(anchors) < 2:
            continue
        for path in anchors:
            others = ", ".join(
                str(o.relative_to(vault_root)) for o in anchors if o != path
            )
            findings.append(Finding(
                severity="error",
                surface_file=path,
                surface_line=1,
                code="C53",
                message=(
                    f"anchor name '{path.stem}' collides with {others} — an "
                    f"anchor page is linked from anywhere in the vault, so "
                    f"`[[{path.stem}]]` resolves by proximity to the LINKING "
                    f"file and is wrong from most of it. Rename one anchor "
                    f"(and sweep its inbound links), or merge them if they "
                    f"are the same thing"
                ),
                mechanically_fixable=False,
            ))
    return findings


# ============================================================
# Checks C13–C18 — bracket↔H2 consistency (F089)
# ============================================================
# C13: `## Ready` H2 only contains [Ready] rows  (auto-fix pure-state only)
# C14: `## Active` H2 only contains [Active] rows (auto-fix pure-state only)
# C15: [Watching]/[Waiting] rows belong in `## Later`     (auto-fix)
# C16: [Blocked]/[Blocked F<n>] rows belong in `## Later` (auto-fix)
# C18: [Verify-by YYYY-MM-DD] past-expiry → `## Done`     (auto-fix)
# (C17 — stale [Done] in horizon H2s — covered by existing C4.)


def _is_pure_state_park_bracket(status: str) -> bool:
    """Pure-state brackets unambiguously belong in a park horizon (per F089 Q1
    hybrid + F100 Verify-horizon split):
    - Watching, Watching Nd/Nh -> ## Verify (passive observation)
    - Verify, Verify-by YYYY-MM-DD -> ## Verify
    - Waiting, Waiting Nd/Nh -> ## Later (awaiting external event)
    - Blocked, Blocked F<n> -> ## Later (external dependency)

    Ambiguous brackets (Questions / Designing) are NOT auto-fixable — they
    need /groom body-reading to decide.
    """
    s = status.strip()
    return (
        s.startswith("Watching")
        or s.startswith("Waiting")
        or s.startswith("Blocked")
        or s.startswith("Verify")  # Verify, Verify-by -> ## Verify horizon
    )


def _park_bracket_target_h2(status: str) -> str:
    """Return the canonical target H2 name for a pure-state park bracket.

    Per F100: Watching/Verify* go to `## Verify`; Waiting/Blocked stay in
    `## Later`. The split surfaces passive-observation rows separately from
    awaiting-event rows in the render.
    """
    s = status.strip()
    if s.startswith("Watching") or s.startswith("Verify"):
        return "Verify"
    return "Later"  # Waiting, Blocked


def _is_verify_by_expired(status: str, today: date) -> bool:
    """Does this status bracket match `Verify-by YYYY-MM-DD` past today?"""
    m = VERIFY_BY_DATE_RE.match(status.strip())
    if not m:
        return False
    try:
        verify_date = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return False
    return verify_date < today


def check_c13_ready_h2_purity(entries: list[BacklogEntry]) -> list[Finding]:
    """C13: every row under ## Ready H2 must have [Ready] bracket."""
    findings: list[Finding] = []
    for e in entries:
        if e.horizon != "Ready":
            continue
        # Member-aware: a `[Ready, Questions]` row is legitimately under ## Ready.
        if has_member(e.status, "Ready"):
            continue
        # Don't double-report [Done] (C4 owns it)
        if e.status.startswith("Done"):
            continue
        auto_fix = _is_pure_state_park_bracket(e.status)
        if auto_fix:
            target_h2 = _park_bracket_target_h2(e.status)
            suffix = f"; auto-moving to ## {target_h2}"
        else:
            suffix = "; needs /groom body-reading"
        findings.append(Finding(
            severity="warning",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C13",
            message=(
                f"row '{e.identifier}' has [{e.status}] bracket under ## Ready H2 "
                f"— workflow-state H2 must match bracket{suffix}"
            ),
            mechanically_fixable=auto_fix,
        ))
    return findings


def check_c14_active_h2_purity(entries: list[BacklogEntry]) -> list[Finding]:
    """C14: every row under ## Active H2 must have [Active] bracket."""
    findings: list[Finding] = []
    for e in entries:
        if e.horizon != "Active":
            continue
        if has_member(e.status, "Active"):
            continue
        if e.status.startswith("Done"):
            continue  # C4 owns
        auto_fix = _is_pure_state_park_bracket(e.status)
        if auto_fix:
            target_h2 = _park_bracket_target_h2(e.status)
            suffix = f"; auto-moving to ## {target_h2}"
        else:
            suffix = "; needs /groom body-reading"
        findings.append(Finding(
            severity="warning",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C14",
            message=(
                f"row '{e.identifier}' has [{e.status}] bracket under ## Active H2 "
                f"— workflow-state H2 must match bracket{suffix}"
            ),
            mechanically_fixable=auto_fix,
        ))
    return findings


def check_c15_watching_waiting_in_later(
    entries: list[BacklogEntry], today: date,
) -> list[Finding]:
    """C15: [Watching]/[Verify*] rows belong in ## Verify; [Waiting] in ## Later."""
    findings: list[Finding] = []
    for e in entries:
        s = e.status.strip()
        # Watching* and Verify* (Verify, Verify-by) → ## Verify horizon
        if s.startswith("Watching") or s.startswith("Verify"):
            if e.horizon == "Verify":
                continue
            # F251 #5 — C18 auto-moves an EXPIRED [Verify-by …] row to ## Done
            # (terminal) without rebracketing; C15 must yield to that precedence
            # or the two checks flag each other forever (C15 wants it back in
            # ## Verify, C18 keeps it in ## Done). A retired Verify-by in Done
            # is correct — skip it.
            if e.horizon == "Done" and _is_verify_by_expired(s, today):
                continue
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C15",
                message=(
                    f"row '{e.identifier}' has [{s}] bracket in ## {e.horizon} "
                    f"— Watching/Verify belongs in ## Verify (passive observation)"
                ),
                mechanically_fixable=True,
            ))
            continue
        # Waiting* → ## Later horizon (separate behavior — awaiting an event)
        if s.startswith("Waiting"):
            if e.horizon == "Later":
                continue
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C15",
                message=(
                    f"row '{e.identifier}' has [{s}] bracket in ## {e.horizon} "
                    f"— Waiting belongs in ## Later (awaiting external event)"
                ),
                mechanically_fixable=True,
            ))
    return findings


def check_c16_blocked_in_later(entries: list[BacklogEntry]) -> list[Finding]:
    """C16: [Blocked]/[Blocked F<n>] rows must be in ## Later."""
    findings: list[Finding] = []
    for e in entries:
        s = e.status.strip()
        if not s.startswith("Blocked"):
            continue
        if e.horizon == "Later":
            continue
        findings.append(Finding(
            severity="warning",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C16",
            message=(
                f"row '{e.identifier}' has [{s}] bracket in ## {e.horizon} "
                f"— Blocked belongs in ## Later (external dependency)"
            ),
            mechanically_fixable=True,
        ))
    return findings


# ============================================================
# C55 (T159) — a `[Blocked X]` edge must point at a LIVE, VISIBLE row.
#
# Dan, 2026-08-08, reading his own queue: *"everything is blocked on feature 41,
# and feature 41 is not showing up in my list. That's completely illegal."*
# He had found one instance of two distinct defects, and a vault-wide scan of
# the 24 `[Blocked …]` rows found more of each:
#
#   MISSING / INVISIBLE — the blocker exists but sits where the render will not
#     surface it (`## Later`, Icebox, a `[Verify-by]` bracket). Nine ATT disk
#     rows displayed as blocked while the single user action releasing all nine
#     was hidden under Later.
#   DONE — the blocker completed and the dependants never learned. Those rows
#     read as parked when they are runnable right now, which is the more
#     expensive failure: defect 1 hides an action, defect 2 freezes work.
#
# This is a check rather than a batch of edits because the edge is written once
# and never re-examined: any hand-fix rots the next time a blocker closes.
#
# Two resolution traps, both of which made earlier attempts silently inert:
#   1. Handles are anchor-qualified (`ATT-F041`); row identifiers are bare
#      (`F041`). A raw lookup never matches, which is exactly what kept
#      `## Blockers` empty vault-wide until T161. The qualified prefix is
#      stripped ONLY when it names a real anchor, so `B-QFix` and
#      `R-Scaffolding.5.2` — identifiers that legitimately contain a dash —
#      are never mistaken for qualified handles.
#   2. A FOREIGN handle (`MUX-T068` seen from DKT) must resolve against THAT
#      anchor's backlog. Resolving it locally would report a false error on a
#      perfectly good cross-anchor edge. That is why the checker takes the full
#      backlog universe and not just the scoped set.
#
# Visibility is asked of `renders_in_body`, the same predicate the renderer and
# the banner use, rather than a fourth horizon list that agrees with the other
# three today.
# ============================================================

_C55_BLOCKED_RE = re.compile(r"^Blocked\s+(\S.*?)\s*$", re.I)

# THE ARGUMENT OF `[Blocked …]` HAS TWO LEGAL FORMS, and only one is in scope.
# `blocked_grammar_gate` (backlog-edit.py) admits both, deliberately:
#   HANDLE form  `Blocked F210` / `Blocked HA-T045` / `Blocked B-QFix`
#                — a typed edge naming another ROW.
#   WHAT form    `Blocked upstream API` / `Blocked haorui-reboot`
#                — a change in the universe, in 1–3 words. Names no row and is
#                not supposed to.
# Only the handle form can be resolved, so only it can be wrong. A first cut of
# this checker skipped the distinction and reported 67 findings vault-wide, of
# which ~50 were legal WHAT-form brackets — the checker firing on conforming
# input, which is how a guard gets disabled and then protects nothing.
#
# Identifier shapes, taken from the ones the vault actually mints:
#   `F041`, `T045`, `DMUX034`   letters + digits, no separator
#   `B-QFix`                    the B- family
#   `R-Scaffolding.5.2`         dotted roadmap-task handles
_C55_ROW_ID_RE = re.compile(
    r"^(?:[A-Za-z]{1,8}\d{1,4}"
    r"|B-[A-Za-z][A-Za-z0-9]*"
    r"|R-[A-Za-z][A-Za-z0-9_\-]*(?:\.[A-Za-z0-9_\-]+)*)$")


def _c55_split_handle(arg: str, own_anchor: str,
                      all_backlogs: dict[str, Path]
                      ) -> Optional[tuple[str, str]]:
    """(anchor, identifier) for a `[Blocked <arg>]` argument, or None when the
    argument is the WHAT form and names no row.

    An anchor qualifier is stripped ONLY when what remains is itself
    identifier-shaped. Both halves of that test matter and each has its own
    live counter-example:
      - without the strip, `[Blocked ATT-F041]` looks up `ATT-F041` against a
        row called `F041` and never matches — the bug that kept `## Blockers`
        empty vault-wide until T161;
      - without the shape test on the remainder, `[Blocked mux-queue-empty]`
        and `[Blocked sv-team-inputs]` — both plain WHAT forms — get split into
        a MUX/SV anchor plus a nonexistent row and reported as broken edges.
    """
    if _C55_ROW_ID_RE.match(arg):
        return own_anchor, arg
    if "-" in arg:
        prefix, rest = arg.split("-", 1)
        if _C55_ROW_ID_RE.match(rest):
            for name in all_backlogs:
                if name.casefold() == prefix.casefold():
                    return name, rest
    return None


def check_c55_blocker_live_and_visible(
        anchor_backlogs: dict[str, Path],
        all_backlogs: dict[str, Path],
        vault_index: dict[str, list[Path]]) -> list[Finding]:
    """C55 (T159): every `[Blocked <handle>]` row's blocker must exist, be
    unfinished, and render somewhere the reader can find it."""
    findings: list[Finding] = []
    # One parse per backlog, shared across every edge that resolves into it.
    parsed: dict[str, list[BacklogEntry]] = {}

    def rows_of(name: str) -> list[BacklogEntry]:
        if name not in parsed:
            path = all_backlogs.get(name)
            parsed[name] = backlog_entries(path, vault_index) if path else []
        return parsed[name]

    for own, backlog_file in sorted(anchor_backlogs.items()):
        for e in backlog_entries(backlog_file, vault_index):
            for member in bracket_members(e.status):
                m = _C55_BLOCKED_RE.match(member.strip())
                if not m:
                    continue
                split = _c55_split_handle(m.group(1), own, all_backlogs)
                if split is None:
                    continue  # WHAT form — names no row, so nothing to resolve
                target_anchor, target_id = split
                target = next(
                    (t for t in rows_of(target_anchor)
                     if t.identifier == target_id), None)
                if target is None:
                    target = next(
                        (t for t in rows_of(target_anchor)
                         if t.identifier.casefold() == target_id.casefold()),
                        None)
                where = ("" if target_anchor == own
                         else f" in {target_anchor}")
                if target is None:
                    findings.append(Finding(
                        severity="error", surface_file=e.source_file,
                        surface_line=e.source_line, code="C55",
                        message=(
                            f"row '{e.identifier}' is [{e.status}] but no row "
                            f"'{target_id}'{where} exists — the blocker was "
                            f"renamed, archived, or never written, so nothing "
                            f"will ever unblock this row. Repoint the handle at "
                            f"the live blocker, or rebracket the row."),
                        mechanically_fixable=False))
                    continue
                if has_member(target.status, "Done") or \
                        target.status.strip().startswith("Done"):
                    findings.append(Finding(
                        severity="error", surface_file=e.source_file,
                        surface_line=e.source_line, code="C55",
                        message=(
                            f"row '{e.identifier}' waits on '{target_id}'{where}, "
                            f"which is already [{target.status}] "
                            f"({target.source_file.name}:{target.source_line}) — "
                            f"this row is runnable NOW and only its bracket says "
                            f"otherwise. Rebracket it; the fix belongs to this "
                            f"row's owner, not the blocker's."),
                        mechanically_fixable=False))
                    continue
                # This third finding is about VISIBILITY, not integrity, so it
                # needs the reader to exist: it fires only when the WAITING row
                # renders. Its own message says "the reader is told the work is
                # blocked" — if `e` is parked too, the reader is told nothing
                # and there is nothing to repair.
                #
                # The guard was absent until 2026-08-19 and could not bite,
                # because `[Blocked …]` under `## Later` used to render, so a
                # parked waiter was a visible waiter. Restoring `## Later` to
                # render nothing separated the two, and without this line the
                # check would fire on every parked blocked row in the vault —
                # 72 of them — each one demanding the reader be given a path to
                # something no reader is being shown.
                if not renders_in_body(e.horizon, e.status):
                    continue
                if not renders_in_body(target.horizon, target.status):
                    findings.append(Finding(
                        severity="error", surface_file=e.source_file,
                        surface_line=e.source_line, code="C55",
                        message=(
                            f"row '{e.identifier}' waits on '{target_id}'{where} "
                            f"[{target.status}] under ## {target.horizon} "
                            f"({target.source_file.name}:{target.source_line}), "
                            f"which renders in no queue — the reader is told the "
                            f"work is blocked and given no way to reach what "
                            f"blocks it. Move the blocker onto a rendering "
                            f"horizon, or rebracket this row."),
                        mechanically_fixable=False))
    return findings


# ============================================================
# Check C41 — soak/verify rows must declare their concrete user question, and
# Ready/Active rows their no-user next-action. Mirrors the forcing-function in
# queries-render.py: a [Verify*]/[Watching*] row with no `- **Verify:**`
# sub-bullet renders `⚠ no concrete question`; a [Ready]/[Active] row with no
# `- **Next:**` sub-bullet renders `⚠ none declared — not really Ready`. Before
# C41, such a half-authored row passed audit-q CLEAN while visibly broken in the
# queries render (the 2026-07-02 F171 incident: bracket set, question never
# written, "triage clean" falsely reported). Report-only — the agent must WRITE
# the question / next-action (or promote to [Done] / rebracket); there is no
# mechanical fix, and `⚠` is never a valid resting state.
# ============================================================

# Sub-bullet forms, mirroring queries-render.py `_subbullet_res` (bold or plain,
# optional `(...)` qualifier, non-empty content required):
def _labeled_subbullet_res(label: str) -> tuple:
    return (
        re.compile(rf"^\s+-\s+\*\*{label}(?:\s*\([^)]*\))?:\*\*\s*\S"),
        re.compile(rf"^\s+-\s+{label}(?:\s*\([^)]*\))?:\s*\S"),
    )


def _rows_with_subbullet(backlog_file: Path, label: str) -> set:
    """Identifiers of rows carrying a non-empty `**<label>:**` sub-bullet.
    Tracks the current row via ROW_OPENER_RE and resets on any heading —
    exactly as queries-render.py `_extract_labeled_subbullets` does — so C41
    flags precisely the rows the render would mark `⚠`."""
    bold_re, plain_re = _labeled_subbullet_res(label)
    have: set = set()
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return have
    current = None
    for line in lines:
        if HEADING_RE.match(line):
            current = None
            continue
        opener = ROW_OPENER_RE.match(line)
        if opener:
            current = opener.group(1)
            continue
        if current is None:
            continue
        if bold_re.match(line) or plain_re.match(line):
            have.add(current)
    return have


def _row_doc_has_pending_q(e: "BacklogEntry", backlog_file: Path) -> bool:
    """F305 D5 — does the row's arrow-linked doc hold a pending question?
    Shares the writer's own resolver (`_hosted_pending_items`), so the check
    and the F171 gate agree on what counts."""
    try:
        return bool(_be_mod._hosted_pending_items(
            backlog_file, e.raw_body or "", ("Q",)))
    except Exception:
        return False


def check_c41_soak_question_declared(
    entries: list[BacklogEntry], backlog_file: Path,
) -> list[Finding]:
    """C41: every [Verify*]/[Watching*] row declares a `- **Verify:**` yes/no
    question; every [Ready]/[Active]/[Agreed] row declares a `- **Next:**`
    no-user action. A row missing its companion sub-bullet renders `⚠` on the
    queries page — a half-authored state, never a valid resting place."""
    findings: list[Finding] = []
    have_verify = _rows_with_subbullet(backlog_file, "Verify")
    have_next = _rows_with_subbullet(backlog_file, "Next")
    # T237 — a `- **Probe:**` satisfies C41 on a [Watching*] row. F305 Q2 and
    # [[DAS Backlog]] define the agent-owned deferred check as a Probe on a
    # Watching row, and deliberately NOT a Verify: a Verify there renders into
    # `## Verifications` and puts a check in front of the user that is by
    # design invisible to them. Without this, that sanctioned shape was flagged
    # by the very checker meant to catch half-authored rows. Watching only — a
    # [Verify*] row's whole point is the human question.
    have_probe = _rows_with_subbullet(backlog_file, "Probe")
    for e in entries:
        # B-QFix is a machinery row authored by --fix itself; its sub-bullets
        # ARE the residual findings and its next-action is per-C-code (walk the
        # sub-bullets, apply audit-q § 5). write_qfix_row would clobber any
        # user-added `- **Next:**` anyway. Exempt from C41 (SKA F227, 2026-07-05).
        if e.identifier == "B-QFix":
            continue
        s = e.status.strip()
        needs_verify = (
            s.startswith("Watching")
            or (s.startswith("Verify") and not s.startswith("Verify-by"))
        )
        needs_next = s in ("Ready", "Active", "Agreed")
        if (needs_verify and e.identifier not in have_verify
                and _row_doc_has_pending_q(e, backlog_file)):
            # F305 D5 — the check may live in the doc as its FINAL question
            # (same Q numbering, minted at done-time); a row whose linked doc
            # holds a pending Q carries its verification there, not in a
            # `- **Verify:**` sub-bullet.
            continue
        if (needs_verify and e.identifier not in have_verify
                and s.startswith("Watching") and e.identifier in have_probe):
            continue
        if needs_verify and e.identifier not in have_verify:
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C41",
                message=(
                    f"row '{e.identifier}' [{s}] has no `- **Verify:**` sub-bullet "
                    f"— queries page renders '⚠ no concrete question'. Resolve one "
                    f"of: (a) write the passive / next-use yes/no question; "
                    f"(b) promote to [Done] if the soak already passed; "
                    f"(c) rebracket to [Blocked]/[Waiting] naming the event."
                ),
                mechanically_fixable=False,
            ))
        elif needs_next and e.identifier not in have_next:
            # F332 — a derived row's Next lives in its doc as `next::`; the
            # regenerated row line shows it, no sub-bullet exists or should.
            try:
                if _be_mod.read_doc_next(
                        _be_mod.arrow_doc_path(e.raw_body or "")):
                    continue
            except Exception:
                pass
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C41",
                message=(
                    f"row '{e.identifier}' [{s}] has no `- **Next:**` sub-bullet "
                    f"— queries page renders '⚠ none declared — not really Ready'. "
                    f"Declare the one no-user next action, or rebracket "
                    f"([Verify] if the next step is a user check, "
                    f"[Blocked]/[Questions] if it needs the user)."
                ),
                mechanically_fixable=False,
            ))
    return findings


def _rows_with_subbullet_text(backlog_file: Path, label: str) -> dict:
    """{row identifier: sub-bullet text} for rows carrying a `**<label>:**`
    sub-bullet — same walk as _rows_with_subbullet, but keeps the content."""
    bold_re, plain_re = _labeled_subbullet_res(label)
    text_re = re.compile(
        rf"^\s+-\s+(?:\*\*)?{label}(?:\s*\([^)]*\))?:(?:\*\*)?\s*(.+)$"
    )
    out: dict = {}
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return out
    current = None
    for line in lines:
        if HEADING_RE.match(line):
            current = None
            continue
        opener = ROW_OPENER_RE.match(line)
        if opener:
            current = opener.group(1)
            continue
        if current is None:
            continue
        if bold_re.match(line) or plain_re.match(line):
            m = text_re.match(line)
            if m and current not in out:
                out[current] = m.group(1).strip()
    return out


def check_c47_verify_ownership(
    entries: list[BacklogEntry], backlog_file: Path,
) -> list[Finding]:
    """C47 (F240): a [Verify*]/[Watching*] row whose `- **Verify:**` question
    is phrased as a machine event is agent-grade — the user's answer would be
    no better than the agent's. Catches rows that predate the mint-time gate
    or were hand-edited. Report-only: reclassification needs judgment (run the
    check and close, or park [Waiting] with an agent-check plan)."""
    findings: list[Finding] = []
    verify_texts = _rows_with_subbullet_text(backlog_file, "Verify")
    for e in entries:
        s = e.status.strip()
        if not (s.startswith("Verify") or s.startswith("Watching")):
            continue
        q = verify_texts.get(e.identifier)
        if q and is_mechanical_verify(q):
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C47",
                message=(
                    f"row '{e.identifier}' [{s}] verification is agent-grade "
                    f"(machine-event phrasing: \"{q[:80]}\") — per F240 "
                    f"who-is-better-positioned, run the check now and close "
                    f"the row, or reclassify [Waiting] naming the wake event "
                    f"with an agent-check plan. Only checks needing the "
                    f"user's taste / preference / ratification / passive-use "
                    f"observation may surface."
                ),
                mechanically_fixable=False,
            ))
    return findings


def check_c51_user_action_present(
    entries: list[BacklogEntry], backlog_file: Path,
) -> list[Finding]:
    """C51 (F259): a [User] row must carry a `- **User:**` sub-bullet naming
    the user-only action it is gated on (a login only the user holds, a GUI
    permission dialog, a 2FA tap). The audit mirror of the mint-time guard,
    over rows that predate the gate or were hand-edited. Report-only: naming
    the action (or rebracketing [Ready]) needs judgment."""
    findings: list[Finding] = []
    user_texts = _rows_with_subbullet_text(backlog_file, "User")
    for e in entries:
        if not has_member(e.status, "User"):
            continue
        if not user_texts.get(e.identifier):
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C51",
                message=(
                    f"row '{e.identifier}' [User] has no `- **User:**` action — "
                    f"per F259 a [User] row names the user-only action it waits "
                    f"on. Add `- **User:** <action>`, or rebracket [Ready] with "
                    f"a `- **Next:**` if the agent can do it itself."
                ),
                mechanically_fixable=False,
            ))
    return findings


# ============================================================
# C57 — a backlog row that HOSTS a question instead of pointing at the doc
#       that does (F329 / T550)
# ============================================================
#
# F329 shipped with exactly one gate: `state` refuses a write that ADDS a
# pending inline `- **Q<n>` sub-bullet to a row. That gate names ONE host
# shape, and naming one shape teaches the next writer to use another. SONAR
# T048 and T049 were both written AFTER F329 shipped, each carrying a full
# lettered yes/no inside a `- **User:**` sub-bullet — a surface the gate does
# not inspect and no check had ever looked at. Dan found them by eye
# (2026-08-19): *"there's a bunch of entries in Sonar's backlog that have
# questions embedded in the backlog, and I think we decided we're not gonna do
# this."*
#
# So this check does not test for a shape. It tests the INVARIANT — a row that
# asks the user something must have a doc to host the asking — and reports the
# way each row breaks it, so the population stays legible when it is migrated.
#
# Overlap with C34 is deliberate and bounded. C34 is a line-level markdown rule
# that predates F329 and still exempts T-/B-/Q-rows as "the sanctioned no-doc
# form"; that exemption is what let shape `inline-q` accumulate on exactly the
# rows F329 was written to cover. C57 is the row-level rule that now owns the
# invariant for every kind, at WARNING severity — the population is a migration
# backlog (T550), not a stop-gate, and promoting it to error before it is
# measured would hand four other anchors a red gate they did not ask for.

_C57_SUBBULLET_BREAK_RE = re.compile(
    r"^\s+-\s+\*\*(?:Next|Verify|User|Resolved|Q\d+)\b")


def _row_span_lines(e: BacklogEntry) -> list[str]:
    """The row's own sub-bullet span — lines after the row opener up to the
    next top-level bullet, heading, or EOF. Same forward-scan as
    `_row_inline_q_count` / `_row_has_next`; the three must not disagree about
    where a row ends or two of them will describe different rows."""
    try:
        lines = e.source_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    span: list[str] = []
    for nxt in lines[e.source_line:]:  # source_line is 1-indexed → next line
        if HEADING_RE.match(nxt) or re.match(r"^- \*\*", nxt):
            break
        span.append(nxt)
    return span


def _labeled_subbullet_block(span: list[str], label: str) -> str:
    """The FULL text of a `- **<label>:**` sub-bullet — its own line plus every
    continuation line and nested option bullet under it, to the next labeled
    sibling.

    `_rows_with_subbullet_text` keeps only the sub-bullet's first line, which
    is precisely where a lettered option list is invisible: C19 requires each
    `**(A)**` to sit on its OWN line, so a question written to spec has its
    entire decision shape below the line that check can see. That is why the
    SONAR rows read as ordinary one-line User asks to everything mechanical.
    """
    head = re.compile(rf"^\s+-\s+(?:\*\*)?{label}(?:\s*\([^)]*\))?:(?:\*\*)?")
    out: list[str] = []
    collecting = False
    for line in span:
        if head.match(line):
            collecting = True
            out.append(line)
            continue
        if collecting:
            if _C57_SUBBULLET_BREAK_RE.match(line):
                break
            out.append(line)
    return "\n".join(out)


def check_c57_row_hosts_question(
    entries: list[BacklogEntry], backlog_file: Path,
) -> list[Finding]:
    """C57 (F329 / T550): a live backlog row that hosts a question itself
    instead of pointing at the doc that hosts it.

    Four host shapes, reported by name on the finding so the migration can be
    counted and batched rather than eyeballed:

      `inline-q`    — ≥1 pending `- **Q<n> —` sub-bullet on the row.
      `q-row`       — an F275 standalone Q-row; the row IS the question.
                      Retired as a mintable shape by F329; legacy ones remain.
      `lettered`    — a `- **User:**` / `- **Verify:**` sub-bullet carrying ≥2
                      distinct `(A)`..`(D)` option labels. This is a full
                      ask-format question living in the row. The SONAR shape.
      `unhosted`    — a `- **User:**` / `- **Verify:**` sub-bullet that poses a
                      question (`?`) on a row with no `→ [[doc]]` of its own.
                      The weakest signal of the four, and the one that will
                      carry false positives (a one-line yes/no verification on
                      a small row is legitimate); it is here because it is the
                      only shape that catches a question with nowhere to live.

    Report-only. Migrating a row means minting its doc, moving the record and
    the fork into it, and reducing the sub-bullet to a one-line ask that links
    the doc — judgement at every step, and none of it mechanical.
    """
    findings: list[Finding] = []
    for e in entries:
        if e.horizon in ("Done", "Icebox"):
            continue
        kinds: list[str] = []
        if _is_standalone_q_row(e.identifier):
            kinds.append("q-row")
        if _row_inline_q_count(e) > 0:
            kinds.append("inline-q")
        span = _row_span_lines(e)
        has_doc = _arrow_target(e) is not None
        for label in ("User", "Verify"):
            block = _labeled_subbullet_block(span, label)
            if not block:
                continue
            scan = "\n".join(_strip_code_spans(l) for l in block.splitlines())
            if has_inline_alternatives(scan):
                kinds.append(f"lettered({label})")
            elif "?" in scan and not has_doc:
                kinds.append(f"unhosted({label})")
        if not kinds:
            continue
        findings.append(Finding(
            severity="warning",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C57",
            message=(
                f"row '{e.identifier}' [{e.status}] hosts its own question "
                f"({', '.join(kinds)}) — per F329 the backlog hosts pointers "
                f"and questions live in docs. Mint the row's doc, move the "
                f"record and the fork into it, and leave the sub-bullet as a "
                f"one-line ask that links the doc. The row keeps its id."
            ),
            mechanically_fixable=False,
        ))
    return findings


def check_c18_verify_by_expired(
    entries: list[BacklogEntry], today: date,
) -> list[Finding]:
    """C18: [Verify-by YYYY-MM-DD] past expiry → auto-move to ## Done."""
    findings: list[Finding] = []
    for e in entries:
        if not _is_verify_by_expired(e.status, today):
            continue
        if e.horizon == "Done":
            continue
        findings.append(Finding(
            severity="warning",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C18",
            message=(
                f"row '{e.identifier}' has [{e.status}] window expired "
                f"(today={today.isoformat()}); auto-Done per Verify-by deferred-by-use"
            ),
            mechanically_fixable=True,
        ))
    return findings


# ============================================================
# C23 — [Designing] is not a valid terminal bracket
# ============================================================
#
# F275 shipped the STANDALONE Q-ROW: a backlog row whose identifier is
# `Q<n>`, where the row IS the question — no feature doc, no arrow link, and
# sub-bullets that are ask-format options (`- **(A)** …`) rather than nested
# `- **Q<n> —` headers. Five checks reason about brackets and only C24 was
# taught the shape when F275 landed (T079, 2026-08-01). The other four all
# fire on every standalone Q-row, and C23's auto-fix is actively dangerous:
# it reads zero pending Qs (the options aren't Q-headers), concludes design
# is over, and promotes the row to [Ready] — bracketing a question awaiting
# the user as agent-executable work.
#
# The predicate below is the single place that recognises the shape.


def _is_standalone_q_row(identifier: str | None) -> bool:
    """True for an F275 standalone Q-row — the row that IS its own question.

    Self-backing: its number lives in the row header, so it is never counted
    against a linked doc and never owes a `→ [[F<n>]]` link. While it sits in
    a live horizon it is exactly ONE pending question.
    """
    return bool(re.match(r"^Q\d+$", identifier or ""))
# Per user direction 2026-05-26 — [Designing] alone creates a deadlock:
# nobody knows whose turn it is. Force every [Designing] row to resolve
# to one of two honest forms:
#   - linked feature doc has N pending Qs → bracket must be [N Questions]
#     (or [Questions] for N=1) — names the user as the next-action owner.
#   - linked feature doc has zero pending Qs → bracket must be [Ready] —
#     the agent can pick it up. Designing is over.


def check_c23_designing_resolves(entries: list[BacklogEntry]) -> list[Finding]:
    """C23: every [Designing] row must resolve to [N Questions] (if its
    linked feature doc has pending Qs) or [Ready] (if not). Designing alone
    creates a turn-ownership deadlock.

    Walks each [Designing] row, finds its linked feature doc, counts pending
    Qs in that doc's `## Open Questions` H2 via `extract_q_entries`, and
    emits a finding that names the correct bracket.

    Rows without a linked feature doc (B-rows with inline Qs in the backlog
    itself) are handled by extracting Qs from the backlog file scoped to the
    row's identifier as the container_id.
    """
    findings: list[Finding] = []
    for e in entries:
        if not has_member(e.status, "Designing"):
            continue
        # F275 (T079) — a standalone Q-row backs itself: it IS one pending
        # question, so the honest bracket is [Questions]. Counting it the
        # normal way yields zero (its sub-bullets are options, not Q-headers)
        # and the fixer would promote a question awaiting the user to [Ready].
        if _is_standalone_q_row(e.identifier):
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C23",
                message=(
                    f"row '{e.identifier}' is a standalone Q-row and is its "
                    f"own single pending question (F275) — bracket must be "
                    f"[Questions], not [Designing]"
                ),
                mechanically_fixable=True,
            ))
            continue
        # Resolve where to count pending Qs. The row's OWN doc is the
        # arrow-form link only (T012 — `e.link` is the first link of any
        # form and can be an in-prose mention of another row).
        arrow_link = _arrow_target(e)
        if arrow_link is not None:
            target_file = arrow_link.target_file_path
            if target_file is None or not target_file.is_file():
                # Can't count Qs — flag as ambiguous; needs user attention.
                findings.append(Finding(
                    severity="warning",
                    surface_file=e.source_file,
                    surface_line=e.source_line,
                    code="C23",
                    message=(
                        f"row '{e.identifier}' is [Designing] but has no linked "
                        f"feature doc to count Qs against — bracket must be "
                        f"[N Questions] or [Ready], not [Designing] alone"
                    ),
                    mechanically_fixable=False,
                ))
                continue
            container_id = e.identifier
            # Container_id for feature-doc Qs is the F-number from the doc stem.
            fnum = feature_number(target_file.stem, target_file)
            if fnum:
                container_id = fnum
            # extract_q_entries returns all Q-headers below ## Open Questions H2
            # before the Resolved sub-section, which IS the pending set.
            pending = len(extract_q_entries(target_file, container_id))
        else:
            # No arrow link: inline Qs live in the backlog file itself, as
            # sub-bullets under this row — count only that span (T012).
            pending = _row_inline_q_count(e)
        if pending > 0:
            correct = f"[{pending} Questions]" if pending > 1 else "[Questions]"
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C23",
                message=(
                    f"row '{e.identifier}' is [Designing] but linked doc has "
                    f"{pending} pending Q{'s' if pending != 1 else ''} — "
                    f"bracket must be {correct}, not [Designing] (so the "
                    f"user can see the open questions from the banner)"
                ),
                mechanically_fixable=True,
            ))
        elif _row_has_next(e):
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C23",
                message=(
                    f"row '{e.identifier}' is [Designing] with zero pending "
                    f"Qs in its linked doc — bracket must be [Ready], not "
                    f"[Designing] (designing is over; the agent can pick it up)"
                ),
                mechanically_fixable=True,
            ))
        else:
            # F250 #10 — 0 pending Qs but no `- **Next:**`. Auto-promoting to
            # [Ready] would create the F171-forbidden Ready-without-Next state,
            # so this is NOT mechanically fixable — the row needs a Next first.
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C23",
                message=(
                    f"row '{e.identifier}' is [Designing] with zero pending Qs "
                    f"but has no `- **Next:**` — add a no-user next action and it "
                    f"becomes [Ready] (a [Ready] row needs a Next per F171), or "
                    f"move it to [Done]"
                ),
                mechanically_fixable=False,
            ))
    return findings


def check_c24_questions_count_match(entries: list[BacklogEntry]) -> list[Finding]:
    """C24: every `[Questions]` / `[N Questions]` row's bracket count must
    match the linked feature doc's actual pending-Q count.

    Per CAB Backlog discipline (`[N Questions]` when N > 1, bare `[Questions]`
    when N = 1, no bracket at all when N = 0), the bracket must stay in sync
    with the doc state. Observed 2026-06-04 on MUX F037: row was bracketed
    `[Questions]` (bare) but linked doc had 7 pending Qs — should have been
    `[7 Questions]`. The audit banner-Q count was right (7); the row bracket
    was lying about the count. Both forms (under-claiming and over-claiming)
    are flagged.

    Reuses C23's pending-Q-counting logic. Rows with no resolvable target are
    skipped (they'd be reported by C1/C22 link-resolution checks).
    """
    findings: list[Finding] = []
    for e in entries:
        # The `[Questions]` / `[N Questions]` MEMBER of the bracket set.
        qm = questions_member(e.status)
        if not qm:
            continue
        # F275 — a standalone Q-row IS its own single pending question
        # (self-backing): no arrow link, and its sub-bullets are the ask-format
        # options, not nested `- **Q<n> —` headers. Never stale, never counted
        # against a linked doc.
        if re.match(r"^Q\d+$", e.identifier or ""):
            continue
        claimed = qm[1] if qm[1] is not None else 1
        # Resolve the Q-bearing target. The row's OWN doc is the arrow-form
        # `→ [[…]]` reference only — an in-prose link is a mention, not the
        # doc. Rows without an arrow link (T-/B-rows) carry their Qs as
        # inline sub-bullets, counted from the row's own sub-bullet span.
        # (2026-07-06: first-link resolution made C24's auto-fix follow a
        # T-row's prose mention to an unrelated doc, count 0, and rebracket
        # a genuinely-questioned row to [Ready]. T012 2026-07-13: the arrow
        # gate alone still trusted e.link — the row's FIRST link of any
        # form — so F230's count came from the wrong file; _arrow_target
        # resolves the arrow link itself.)
        arrow_link = _arrow_target(e)
        if arrow_link is not None:
            target_file = arrow_link.target_file_path
            if target_file is None or not target_file.is_file():
                continue  # link-resolution issue belongs to C1/C22, not here
            container_id = e.identifier
            fnum = feature_number(target_file.stem, target_file)
            if fnum:
                container_id = fnum
            actual = len(extract_q_entries(target_file, container_id))
        elif re.search(r"→\s+\[\[", e.raw_body):
            continue  # arrow present but unparseable (placeholder/out-of-vault) — C1/C22's territory
        else:
            actual = _row_inline_q_count(e)
        if actual == claimed:
            continue  # in sync
        if actual == 0:
            # Bracket claims questions but linked doc has none. The bracket is
            # stale — likely all Qs got resolved without the bracket being
            # updated. Most common case after Phase 2 transition. F250 #10 —
            # only mechanically promotable to [Ready] when a `- **Next:**`
            # exists (F171); without one it needs a Next first or a [Done] move.
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C24",
                message=(
                    f"row '{e.identifier}' is [{e.status}] but linked doc has "
                    f"zero pending Qs — bracket is stale (Qs likely all "
                    f"resolved; bracket should be [Ready] or [Done])"
                    + ("" if _row_has_next(e)
                       else " — add a `- **Next:**` before it can be [Ready] (F171)")
                ),
                mechanically_fixable=_row_has_next(e),
            ))
        else:
            correct = f"[{actual} Questions]" if actual > 1 else "[Questions]"
            findings.append(Finding(
                severity="warning",
                surface_file=e.source_file,
                surface_line=e.source_line,
                code="C24",
                message=(
                    f"row '{e.identifier}' is [{e.status}] (claims {claimed}) "
                    f"but linked doc has {actual} pending Q"
                    f"{'s' if actual != 1 else ''} — bracket must be {correct}"
                ),
                mechanically_fixable=True,
            ))
    return findings


def check_c25_designing_justification(backlog_files: list[Path],
                                      vault_index: dict[str, list[Path]]) -> list[Finding]:
    """C25 (per F106): every [Designing] row must carry a justification.

    F102 says any row bracketed [Designing] must declare what's next — without
    this, designing-state creates a turn-ownership deadlock. C25 is the
    present-time invariant check (C23 was the auto-rewrite escape; F106 keeps
    [Designing] as a valid state that requires justification rather than
    forcing rewrite).

    For each [Designing] row found in any backlog (bullet or H3 form):

    - **Bullet with resolvable feature-doc link** — the linked doc's ## Status
      H2 must lead with `**Designing**` (bolded token per F102) AND the body
      must contain `next action` or `next step` (case-insensitive). Anything
      missing → finding.
    - **Bullet without resolvable link** — must have an inline sub-bullet
      directly below the row matching `- **Status:** Designing —` with `next`
      in the body. Missing → finding.
    - **H3 row** (HA-style) — must have the same inline sub-bullet anywhere
      between the H3 line and the next H3/H2/EOF. Missing → finding.

    Severity: error. No auto-fix — content gap, not mechanical.
    """
    findings: list[Finding] = []
    designing_bracket_re = re.compile(r"\[Designing\b[^\]]*\]")
    h3_row_opener_re = re.compile(
        r"^### "
        r"(?:\[[A-Z]+\]\s+)?"
        r"([A-Za-z][A-Za-z0-9_\-]*)\b"
    )
    bullet_row_opener_re = re.compile(
        r"^- \*\*"
        r"(?:\[\[)?"
        r"(?:\[[A-Z]+\]\s+)?"
        r"([A-Za-z][A-Za-z0-9_\-]*)\b"
    )
    status_subbullet_re = re.compile(
        r"^\s+- \*\*Status:\*\*\s+Designing\s+[—-]\s+(.+)$"
    )
    for backlog_file in backlog_files:
        try:
            text = backlog_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        current_horizon = ""
        for i, line in enumerate(lines):
            m = HEADING_RE.match(line)
            if m and m.group(1) == "##":
                current_horizon = m.group(2)
                continue
            # Skip Done / Icebox; only live horizons.
            if current_horizon in ("Done", "Icebox", ""):
                continue
            # Scope the bracket search to the row's HEAD region, the way
            # _detect_status and the C23/C24 fixers already do. Searching the
            # whole line makes any row whose BODY discusses `[Designing]` —
            # a bug report about bracket handling, say — read as a [Designing]
            # row and get flagged for a justification it does not owe. Live
            # false positive on Tink T079, which is a bug report about exactly
            # this bracket. `_head_span` blanks code spans and wiki-links first.
            h_start, h_end = _head_span(line)
            if not designing_bracket_re.search(_cleaned_line(line)[h_start:h_end]):
                continue
            # Identify row type.
            mh3 = h3_row_opener_re.match(line)
            mb = bullet_row_opener_re.match(line)
            row_match = mh3 or mb
            if row_match is None:
                # Not a row opener — bracketed text inside a sub-bullet or body.
                continue
            identifier = row_match.group(1)
            # F275 (T079) — a standalone Q-row's justification IS the question
            # in its header. F102's "declare what happens next" is a rule about
            # rows that delegate their design to a linked doc.
            if _is_standalone_q_row(identifier):
                continue
            is_h3 = bool(mh3)
            # Look for the row's body span (lines until the next row/heading).
            # Track code-fence state so a YAML/Python comment like `# Before`
            # inside a ``` fence isn't mistaken for an H1 heading.
            #
            # H3-style rows (HA convention) can contain `- **Q1 — ...`-style
            # sub-bullets in the body that look like bullet row openers but
            # aren't separate rows. When the current row is H3, break only on
            # the next ##/### heading. When the current row is a bullet,
            # break on the next bullet row opener too (adjacent bullet rows
            # are genuinely separate).
            body_lines: list[str] = []
            j = i + 1
            in_fence = False
            while j < len(lines):
                nxt = lines[j]
                if re.match(r"^\s*```", nxt):
                    in_fence = not in_fence
                    body_lines.append(nxt)
                    j += 1
                    continue
                if not in_fence and HEADING_RE.match(nxt):
                    break
                if not in_fence and h3_row_opener_re.match(nxt):
                    break
                if not is_h3 and not in_fence and bullet_row_opener_re.match(nxt):
                    break
                body_lines.append(nxt)
                j += 1
            # Try inline status sub-bullet first (works for any row class).
            inline_ok = False
            for bl in body_lines:
                sm = status_subbullet_re.match(bl)
                if sm and re.search(r"\bnext\b", sm.group(1), re.IGNORECASE):
                    inline_ok = True
                    break
            if inline_ok:
                continue
            # No inline status — for bullet rows with a feature-doc link, fall
            # back to checking the linked doc's ## Status H2.
            doc_ok = False
            if not is_h3:
                # Resolve the row's primary link via `links_in_file`.
                row_links = [
                    lk for lk in links_in_file(backlog_file, vault_index)
                    if lk.source_line == i + 1
                ]
                # Prefer an arrow-trailing link if present, else last wiki-link.
                arrow_link = None
                for lk in row_links:
                    col_text = line[max(0, lk.source_col_start - 4):lk.source_col_start]
                    if "→" in col_text or "->" in col_text:
                        arrow_link = lk
                        break
                target_link = arrow_link or (row_links[-1] if row_links else None)
                if (target_link is not None
                        and target_link.target_resolves
                        and target_link.target_file_path is not None):
                    try:
                        doc_text = target_link.target_file_path.read_text(encoding="utf-8")
                    except (OSError, UnicodeDecodeError):
                        doc_text = ""
                    # Find ## Status H2 and read its body until next H2 / EOF.
                    status_match = re.search(
                        r"^## Status\b.*$", doc_text, re.MULTILINE,
                    )
                    if status_match:
                        body_start = status_match.end()
                        next_h2 = re.search(
                            r"^## ", doc_text[body_start:], re.MULTILINE,
                        )
                        status_body = (
                            doc_text[body_start:body_start + next_h2.start()]
                            if next_h2 else doc_text[body_start:]
                        )
                        # Leading bold token must be **Designing**
                        first_nonblank = next(
                            (s.strip() for s in status_body.splitlines() if s.strip()),
                            "",
                        )
                        leads_designing = first_nonblank.startswith("**Designing**")
                        has_next = bool(re.search(
                            r"\bnext (action|step|move)\b",
                            status_body, re.IGNORECASE,
                        ))
                        if leads_designing and has_next:
                            doc_ok = True
            if doc_ok:
                continue
            # Emit the finding.
            row_kind = "H3 row" if is_h3 else "bullet row"
            findings.append(Finding(
                severity="error",
                surface_file=backlog_file,
                surface_line=i + 1,
                code="C25",
                # Both accepted forms are matched LEXICALLY, and saying so is the
                # whole job of this message: a well-written justification that
                # happens not to use the word "next" fails, and the old wording
                # gave the author no way to see why. Name the token.
                message=(
                    f"{row_kind} '{identifier}' [Designing] has no "
                    f"justification — per F102 every [Designing] row must "
                    f"declare what happens next, in ONE of two places. "
                    f"(a) An inline sub-bullet directly under the row: "
                    f"`- **Status:** Designing — <next-action>`, whose text "
                    f"must contain the word `next` (that word is the marker "
                    f"this check looks for, not a stylistic preference). "
                    f"(b) The linked feature doc's `## Status` H2, whose first "
                    f"non-blank line must begin `**Designing**` and whose body "
                    f"must contain `next action`, `next step`, or `next move`. "
                    f"Form (b) applies only when the row carries a resolvable "
                    f"`→ [[…]]` link; without one, only (a) is available."
                ),
                mechanically_fixable=False,
            ))
    return findings


# ============================================================
# C32 — H3-form rows in backlog horizons are forbidden
# C33 — [Designing] rows must have a → [[F<n>]] link to a feature doc
# C34 — Inline Q<n> bullets in backlog row bodies are forbidden
# All three: severity error, no auto-fix (content judgment required).
# ============================================================


_LIVE_HORIZONS = ("Now", "Next", "Later", "Ready", "Active")


def check_c32_h3_rows_forbidden(backlog_files: list[Path]) -> list[Finding]:
    """C32: H3-form rows in backlog horizon H2s are invalid.

    Backlog rows must be bullets per [[DAS Backlog]]. H3-style rows (e.g.
    `### BUG — Title [Designing]`) sail past most row-based checks because
    the canonical parser (ROW_OPENER_RE) is bullet-only. Forbid the form
    entirely so the render and audit see the same shape.
    """
    findings: list[Finding] = []
    h3_re = re.compile(
        r"^### "
        r"(?:\[[A-Z]+\]\s+)?"
        r"([A-Za-z][A-Za-z0-9_\-]*)\b"
    )
    for backlog_file in backlog_files:
        try:
            text = backlog_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        current_h2 = ""
        in_fence = False
        for i, line in enumerate(lines, start=1):
            if re.match(r"^\s*```", line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEADING_RE.match(line)
            if m and m.group(1) == "##":
                current_h2 = m.group(2).strip()
                continue
            if current_h2 not in _LIVE_HORIZONS:
                continue
            mh3 = h3_re.match(line)
            if mh3:
                identifier = mh3.group(1)
                findings.append(Finding(
                    severity="error",
                    surface_file=backlog_file,
                    surface_line=i,
                    code="C32",
                    message=(
                        f"H3-form row '{identifier}' in `## {current_h2}` H2 — "
                        f"backlog rows must be bullets per [[DAS Backlog]]; "
                        f"rewrite as `- **{identifier} — Title** [Status] — body... "
                        f"→ [[F<n> — Title]]`. H3 form escapes the canonical row "
                        f"parser, so most state-purity checks silently skip it."
                    ),
                    mechanically_fixable=False,
                ))
    return findings


def check_c33_designing_needs_link(entries: list[BacklogEntry]) -> list[Finding]:
    """C33: every [Designing] row must have a `→ [[F<n>]]` link.

    [Designing] implies active design work in a linked feature doc. A row
    bracketed [Designing] with no link is in a self-contradictory state —
    no design doc means there's nothing being designed. Honest brackets:
      - [Waiting]  — parked, awaiting external trigger
      - [Ready]    — design resolved, ready to implement
      - [Questions] — has open Qs (which then live in a feature doc, with a link)
    """
    findings: list[Finding] = []
    for e in entries:
        if not has_member(e.status, "Designing"):
            continue
        if e.link is not None:
            continue
        # F275 (T079) — a standalone Q-row by definition has no feature doc:
        # it IS the question. Demanding a `→ [[F<n>]]` link asks for a doc the
        # shape exists to avoid. C23 corrects its bracket to [Questions].
        if _is_standalone_q_row(e.identifier):
            continue
        # Skip Done/Icebox horizons.
        if e.horizon in ("Done", "Icebox"):
            continue
        findings.append(Finding(
            severity="error",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C33",
            message=(
                f"row '{e.identifier}' [Designing] has no `→ [[F<n>]]` link "
                f"to a feature doc — [Designing] implies active design work "
                f"in a linked doc. If parked, use [Waiting]; if ready to "
                f"implement, [Ready]; if Qs remain, [N Questions] + link to "
                f"the feature doc holding them."
            ),
            mechanically_fixable=False,
        ))
    return findings


def check_c43_row_links_existing_doc(entries: list[BacklogEntry]) -> list[Finding]:
    """C43: an F-row whose feature doc EXISTS must carry a `→ [[F<n> — …]]` link.

    Per F235 (user, 2026-07-13, F157 review): a backlog row referencing a feature
    the user can't click through to is a navigation dead-end — "I can't go see
    what that feature's about." The doc is searched under the backlog's Docs tree
    (covers both `{slug} Docs/{slug} Track/{slug} Features/` and legacy
    `{slug} Track/{slug} Features/` layouts). T-rows and doc-less F-rows are
    exempt (the row IS the spec); Done/Icebox horizons are skipped.

    F-numbers are per-anchor namespaces (per DAS Backlog § Numbering policy), so
    the search MUST stop at nested-anchor boundaries — otherwise a SYS backlog
    row for `F015` false-positive-matches on `SKA/…/F015 — F-numbering Migration.md`
    under `SYS/Bespoke/Skill Agent/`, and every anchor that nests another anchor
    produces spurious C43 findings (observed 2026-07-14 on SYS).
    """
    def _find_doc_within_anchor(root: Path, identifier: str) -> bool:
        # Manual walk that skips any subdirectory carrying a `.anchor` marker
        # (that's a nested anchor's own F-namespace, not ours).
        stack = [root]
        pattern_prefix = f"{identifier} — "
        while stack:
            d = stack.pop()
            try:
                entries_iter = list(d.iterdir())
            except (OSError, PermissionError):
                continue
            for child in entries_iter:
                if child.is_dir():
                    # Don't descend into nested anchors OR .git/venv/etc dot-dirs.
                    if child.name.startswith(".") or child.name in ("node_modules", "__pycache__", "venv", ".venv"):
                        continue
                    # Folder-doc upgrade: `F015 — Title/F015 — Title.md` is THIS
                    # anchor's feature even when the folder carries its own
                    # `.anchor` — the boundary skip must not hide it.
                    if (child.name.startswith(pattern_prefix)
                            and (child / f"{child.name}.md").is_file()):
                        return True
                    if (child / ".anchor").exists():
                        continue
                    stack.append(child)
                elif child.is_file() and child.suffix == ".md" and child.name.startswith(pattern_prefix):
                    return True
        return False

    findings: list[Finding] = []
    doc_cache: dict[tuple[Path, str], bool] = {}
    for e in entries:
        if not re.fullmatch(r"F\d+", e.identifier or ""):
            continue
        if e.horizon in ("Done", "Icebox") or has_member(e.status, "Done"):
            continue
        if e.link is not None or f"[[{e.identifier} — " in e.raw_body:
            continue
        root = e.source_file.parents[1] if len(e.source_file.parents) > 1 else e.source_file.parent
        key = (root, e.identifier)
        if key not in doc_cache:
            doc_cache[key] = _find_doc_within_anchor(root, e.identifier)
        if not doc_cache[key]:
            continue
        findings.append(Finding(
            severity="error",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C43",
            message=(
                f"row '{e.identifier}' has a feature doc but no `→ [[{e.identifier} — …]]` "
                f"link in the row — the user cannot click through to see what the feature "
                f"is (F235). Add the wiki-link to the row body."
            ),
            mechanically_fixable=False,
        ))
    return findings


# ============================================================
# C44 + C45 — [Questions] task→doc assertions (F233)
# ============================================================


def check_c44_questions_row_has_target(entries: list[BacklogEntry]) -> list[Finding]:
    """C44: every `[Questions]` / `[N Questions]` row must name a Q-bearing target.

    A row bracketed [Questions] with nowhere for the reader to actually find
    the questions is a navigation dead end — same failure mode C43 catches
    for plain F-row links, but for the Questions bracket specifically. Two
    sanctioned forms (F233):
      - **Arrow-linked rows** (typically F-rows) — `→ [[F<n> — Title]]` to a
        doc that resolves. C1/C22 own broken-link reporting, so an arrow
        present with an unresolved link is skipped here, not double-flagged.
      - **T-/B-rows with no feature doc** — inline `- **Q<n> —` sub-bullets
        directly under the row are the sanctioned no-doc form (row IS the Q
        target; see C34's docstring). `BacklogEntry.raw_body` holds only the
        row's own line (single-line by construction — see `backlog_entries`),
        so the sub-bullets live on the FOLLOWING lines; this scans forward
        from the row to the next top-level bullet/heading to find them.
    """
    findings: list[Finding] = []
    file_lines_cache: dict[Path, list[str]] = {}
    inline_q_re = re.compile(r"^\s*- \*\*Q\d+\s+[—-]")
    for e in entries:
        if not questions_member(e.status):
            continue
        if e.horizon in ("Done", "Icebox"):
            continue
        # A standalone Q row is self-backing: its number is in the header and its
        # body IS the question, so there is no doc to link and no sub-bullet to
        # find. C34 took this alignment under T079; C44 never did, so the construct
        # `state` mints was accepted by one sibling check and rejected by the other.
        if _is_standalone_q_row(e.identifier):
            continue
        if _arrow_target(e) is not None or re.search(r"→\s+\[\[", e.raw_body):
            continue  # has an arrow target — resolvable, or C1/C22's broken-link territory
        if re.match(r"[TB]", e.identifier or ""):
            if e.source_file not in file_lines_cache:
                try:
                    file_lines_cache[e.source_file] = e.source_file.read_text(
                        encoding="utf-8").splitlines()
                except (OSError, UnicodeDecodeError):
                    file_lines_cache[e.source_file] = []
            lines = file_lines_cache[e.source_file]
            has_inline = False
            for nxt in lines[e.source_line:]:  # e.source_line is 1-indexed; start on next line
                if HEADING_RE.match(nxt) or re.match(r"^- \*\*", nxt):
                    break
                if inline_q_re.match(nxt):
                    has_inline = True
                    break
            if has_inline:
                continue
        findings.append(Finding(
            severity="error",
            surface_file=e.source_file,
            surface_line=e.source_line,
            code="C44",
            message=(
                f"row '{e.identifier}' is [{e.status}] but names no Q-bearing "
                f"target — a task asserting questions must link the doc that "
                f"carries them (→ [[F<n> — Title]]), or for T-/B-rows carry "
                f"inline Q<n> sub-bullets (F233)."
            ),
            mechanically_fixable=False,
        ))
    return findings


def check_c45_open_questions_above_h1(entries: list[BacklogEntry]) -> list[Finding]:
    """C45: a linked doc's `## Open Questions` must sit BELOW the H1 — the
    file's first H2 (F241, 2026-07-15; inverts the F233 above-the-H1 rule).

    The block keeps its prominence (first H2, right after the H1's
    orientation prose) while the file stays structurally normal (Obsidian
    outline, masthead convention, heading tree). Only checked for rows
    that already have a resolved arrow link (unresolved links are C1/C22's
    territory; a doc with no `## Open Questions` heading at all is C24/C2's
    "no Qs" case, not a placement violation). Flag-only — moving a block is
    a content edit, not mechanical; `state revalidate <anchor> <doc>` relocates it.

    Dedups per target file: multiple rows linking the same doc emit one
    finding, not one per row.
    """
    findings: list[Finding] = []
    seen: set[Path] = set()
    h1_re = re.compile(r"^# ")
    # F305: both spellings — `## Open Items` canonical, `## Open Questions`
    # legacy, accepted forever (the writer renames on touch).
    oq_re = re.compile(r"^## Open (?:Items|Questions)\s*$")
    for e in entries:
        if not questions_member(e.status):
            continue
        if e.horizon in ("Done", "Icebox"):
            continue
        arrow_link = _arrow_target(e)
        if arrow_link is None or arrow_link.target_file_path is None:
            continue
        target = arrow_link.target_file_path
        if not target.is_file() or target in seen:
            continue
        seen.add(target)
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        in_fence = False
        in_frontmatter = False
        h1_line = 0
        oq_line = 0
        for i, line in enumerate(lines, start=1):
            if i == 1 and line.strip() == "---":
                in_frontmatter = True
                continue
            if in_frontmatter:
                if line.strip() == "---":
                    in_frontmatter = False
                continue
            if re.match(r"^\s*```", line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if h1_line == 0 and h1_re.match(line):
                h1_line = i
            if oq_line == 0 and oq_re.match(line):
                oq_line = i
            if h1_line and oq_line:
                break
        if oq_line == 0:
            continue  # no Open Questions heading — C24/C2's territory
        if h1_line == 0:
            continue  # no H1 — nothing to be below
        if oq_line < h1_line:
            findings.append(Finding(
                severity="error",
                surface_file=target,
                surface_line=oq_line,
                code="C45",
                message=(
                    f"open-items H2 sits above the H1 (H1 at line "
                    f"{h1_line}) — per F241 the block belongs immediately "
                    f"below the H1, as the file's first H2. Run "
                    f"`state \"{target.stem}\" revalidate` to relocate + "
                    f"re-stamp it. Linked from [Questions] row "
                    f"'{e.identifier}' in {e.source_file.stem}."
                ),
                mechanically_fixable=False,
            ))
    return findings


def check_c48_q_stamp_drift(entries: list[BacklogEntry]) -> list[Finding]:
    """C48 (F241): a linked doc whose `## Open Questions` block carries an
    integrity stamp (`<!-- state:q XX -->`) must hash-match its content.

    The state script re-stamps the block on every write; a mismatch means a
    hand-edit bypassed the script's ask-format gates. Stampless blocks are
    grandfathered (legacy docs — no stamp, no finding). Hash impl is
    backlog-edit.py's compute_q_stamp — single source of truth, same shape
    as the C47/is_mechanical_verify sharing. Flag-only: recovery needs the
    format gates re-run (`state revalidate <anchor> <doc>`), never a blind re-bless.
    """
    findings: list[Finding] = []
    seen: set[Path] = set()
    for e in entries:
        if e.horizon in ("Done", "Icebox"):
            continue
        arrow_link = _arrow_target(e)
        if arrow_link is None or arrow_link.target_file_path is None:
            continue
        target = arrow_link.target_file_path
        if not target.is_file() or target in seen:
            continue
        seen.add(target)
        try:
            lines = target.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        rng = _be_mod._open_questions_range(lines)
        if rng is None:
            continue
        stored = _be_mod.read_q_stamp(lines, *rng)
        if stored is None:
            continue  # grandfathered — stampless legacy block
        computed = _be_mod.compute_q_stamp(lines, *rng)
        if computed != stored:
            findings.append(Finding(
                severity="error",
                surface_file=target,
                surface_line=rng[0] + 1,
                code="C48",
                message=(
                    f"open-items block integrity stamp mismatch (stored "
                    f"`{stored}`, computed `{computed}`) — the block was "
                    f"hand-edited past the state script's ask-format gates. "
                    f"Re-issue the change through `state`, or run "
                    f"`state \"{target.stem}\" revalidate` to "
                    f"validate-then-restamp (F241)."
                ),
                mechanically_fixable=False,
            ))
    return findings


def _pending_q_blocks(lines: list[str]):
    """Yield (q_num, start_line_1indexed, block_text) for each pending Q in a
    doc's `## Open Questions` — top-level bullets, outside any ### Resolved /
    ### Removed sub-section. Mirrors state's revalidate slicing over the same
    _be_mod primitives (single source of truth)."""
    rng = _be_mod._open_questions_range(lines)
    if rng is None:
        return
    start, end = rng
    in_h3 = False
    k = start + 1
    while k < end:
        line = lines[k]
        if line.startswith("### "):
            in_h3 = True
            k += 1
            continue
        mm = _be_mod._Q_HEADER_BULLET_RE.match(line)
        if mm and not in_h3:
            indent = mm.group(1)
            j = k + 1
            while j < end:
                nxt = lines[j]
                if nxt.startswith("#"):
                    break
                mh = _be_mod._Q_HEADER_BULLET_RE.match(nxt)
                if mh and (len(nxt) - len(nxt.lstrip())) <= len(indent):
                    break
                j += 1
            yield (int(mm.group(2)), k + 1, "\n".join(lines[k:j]))
            k = j
            continue
        k += 1


def check_c50_question_why_ask(entries: list[BacklogEntry]) -> list[Finding]:
    """C50 (F257): a pending Open Question carrying a Lean/Strong
    Recommendation but no `· *why-ask: …*` annotation is a recommendation-
    bearing ask the agent could likely have decided (F068); the mint-time
    gate (question_mint_gate) refuses these, and C50 is the audit mirror over
    Qs that reached the doc off the `state` path (hand-edit / legacy). Also
    flags an agent-territory-phrased Q (ordering / batching / rollback /
    cosmetic rename) — never the user's call regardless of justification.
    Report-only: deciding or rewriting the Q needs judgment. Dedups per target
    file (multiple rows linking the same doc walk it once)."""
    findings: list[Finding] = []
    seen: set[Path] = set()
    for e in entries:
        if not questions_member(e.status):
            continue
        if e.horizon in ("Done", "Icebox"):
            continue
        arrow_link = _arrow_target(e)
        if arrow_link is None or arrow_link.target_file_path is None:
            continue
        target = arrow_link.target_file_path
        if not target.is_file() or target in seen:
            continue
        seen.add(target)
        try:
            lines = target.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for q_num, q_line, block in _pending_q_blocks(lines):
            if is_agent_territory_question(block):
                findings.append(Finding(
                    severity="warning", surface_file=target,
                    surface_line=q_line, code="C50",
                    message=(
                        f"Q{q_num} is agent-territory (ordering / batching / "
                        f"rollback / cosmetic rename) — per F257/F068 the agent "
                        f"decides these, never the user. Pick + announce, then "
                        f"resolve or remove the Q. Linked from [Questions] row "
                        f"'{e.identifier}' in {e.source_file.stem}."
                    ),
                    mechanically_fixable=False))
                continue
            if has_why_ask_annotation(block):
                continue
            strength = recommendation_strength(block)
            if strength in ("Lean", "Strong"):
                findings.append(Finding(
                    severity="warning", surface_file=target,
                    surface_line=q_line, code="C50",
                    message=(
                        f"Q{q_num} carries a {strength} recommendation but no "
                        f"`· *why-ask: …*` — per F257 a recommendation means you "
                        f"can likely decide (F068); surface it only with a "
                        f"justification. Decide + announce, or re-issue via "
                        f"`state \"{target.stem}\" Q{q_num} define --why-ask "
                        f"\"<reason>\"`. Linked from [Questions] row "
                        f"'{e.identifier}' in {e.source_file.stem}."
                    ),
                    mechanically_fixable=False))
    return findings


def _inline_q_question_texts(backlog_file: Path, entry: "BacklogEntry") -> list[str]:
    """Question segments of inline `- **Q<n> — <title>** — <question>` sub-bullets
    within an entry's row span (up to the next row opener / heading)."""
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    start = entry.source_line - 1  # source_line is 1-indexed
    if start < 0 or start >= len(lines):
        return []
    out: list[str] = []
    q_re = re.compile(r"^\s+-\s+\*\*Q\d+\b.*?\*\*\s*(?:—|-)?\s*(.*)$")
    for i in range(start + 1, len(lines)):
        ln = lines[i]
        if HEADING_RE.match(ln) or ROW_OPENER_RE.match(ln):
            break
        m = q_re.match(ln)
        if m:
            out.append(m.group(1).strip())
    return out


def check_c49_next_nonanswer(
    entries: list[BacklogEntry], backlog_file: Path,
) -> list[Finding]:
    """C49 (F242): the mechanical groom gate's audit twin. A [Ready]/[Active]/
    [Agreed] row whose `- **Next:**` is a non-answer placeholder — or a
    [Questions] row whose inline `- **Q<n>` question text is a sentinel — means
    the agent punted the groom instead of doing it. Mirrors the state write
    refusal + triage gate (same is_nonanswer chokepoint in backlog-edit.py).
    Report-only → routes to the QFix worklist."""
    findings: list[Finding] = []
    next_texts = _rows_with_subbullet_text(backlog_file, "Next")
    for e in entries:
        s = e.status.strip()
        if s in ("Ready", "Active", "Agreed") and e.identifier != "B-QFix":
            nxt = next_texts.get(e.identifier)
            if nxt and is_nonanswer(nxt):
                findings.append(Finding(
                    severity="warning",
                    surface_file=e.source_file,
                    surface_line=e.source_line,
                    code="C49",
                    message=(
                        f"row '{e.identifier}' [{s}] Next is a non-answer "
                        f"(\"{nxt[:80]}\") — per F242 the agent punted the "
                        f"groom; write the concrete first step it takes with "
                        f"zero user involvement, or rebracket honestly "
                        f"([Questions]/[Blocked]/[Waiting])."
                    ),
                    mechanically_fixable=False,
                ))
    for e in entries:
        if not has_member(e.status, "Questions"):
            continue
        for qtext in _inline_q_question_texts(backlog_file, e):
            if is_nonanswer(qtext):
                findings.append(Finding(
                    severity="warning",
                    surface_file=e.source_file,
                    surface_line=e.source_line,
                    code="C49",
                    message=(
                        f"row '{e.identifier}' [Questions] inline question is a "
                        f"placeholder (\"{qtext[:60]}\") — per F242 the agent "
                        f"punted; write a real, answerable question or "
                        f"rebracket honestly."
                    ),
                    mechanically_fixable=False,
                ))
                break
    return findings


def check_c46_queries_q_link_lands_on_qs(
        anchor_backlogs: dict[str, Path],
        vault_index: dict[str, list[Path]]) -> list[Finding]:
    """C46: every `## Questions` entry in a `{slug} queries.md` must lead the
    reader TO the questions — its FIRST wiki-link resolves to either (a) a
    doc that has ≥1 pending Q, or (b) the anchor's own backlog row (block-
    anchor link) carrying inline `- **Q<n> —` sub-bullets.

    Per user 2026-07-13 (F230 render defect): clicking a Questions entry
    landed on the backlog row while the actual question lived in the feature
    doc — a navigation dead end the C44/C45 source-side checks can't see,
    because the queries surface is a separate script-owned render. A finding
    means the render regressed or the surface was hand-edited; the fix is
    re-running queries-render (flag-only here). Q-block placement inside the
    target doc stays C45's job — C46 asserts reachability, not position.
    """
    findings: list[Finding] = []
    inline_q_re = re.compile(r"^\s*- \*\*Q\d+\s+[—-]")
    for name, backlog_file in sorted(anchor_backlogs.items()):
        queries_file = backlog_track_dir(backlog_file) / f"{name} queries.md"
        if not queries_file.is_file():
            continue
        try:
            q_lines = queries_file.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        try:
            backlog_lines = backlog_file.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            backlog_lines = []
        in_questions = False
        for line_num, line in enumerate(q_lines, start=1):
            if line.startswith("## "):
                in_questions = line.strip() == "## Questions"
                continue
            if not in_questions or not line.startswith("- "):
                continue
            m = WIKI_LINK_RE.search(_strip_code_spans(line))
            if m is None:
                findings.append(Finding(
                    severity="error",
                    surface_file=queries_file,
                    surface_line=line_num,
                    code="C46",
                    message=(
                        "Questions entry carries no wiki-link at all — the "
                        "reader has no path to the questions; re-run the "
                        "queries render"
                    ),
                    mechanically_fixable=False,
                ))
                continue
            parsed = _parse_wiki_inner(m.group(1))
            target = resolve_target(parsed["basename"], queries_file, vault_index)
            if target is None:
                continue  # unresolved link — C1/C22's territory
            if target == backlog_file:
                # Row link: the row itself must carry inline Q sub-bullets.
                block_id = parsed["target_block_id"]
                region = (_scope_to_block_id_region("\n".join(backlog_lines), block_id)
                          if block_id else "")
                # Scan the WHOLE region including its first line — a misplaced
                # block-id can sit on the Q sub-bullet itself, making that the
                # region opener; the row-opener form can't false-match Q\d+.
                has_inline = any(inline_q_re.match(rl)
                                 for rl in region.splitlines())
                # A standalone Q row IS the question, so a reader following the link
                # lands exactly on it; demanding sub-bullets asks the row to nest a
                # copy of itself. Third surface carrying the F233-era assumption
                # that only F-rows can host questions (T120).
                if re.match(r"^- \*\*Q\d+\b", region.lstrip("\n")):
                    has_inline = True
                if not has_inline:
                    findings.append(Finding(
                        severity="error",
                        surface_file=queries_file,
                        surface_line=line_num,
                        code="C46",
                        message=(
                            f"Questions entry links the backlog row "
                            f"('{parsed['basename']}') but the row carries no "
                            f"inline Q sub-bullets — the reader lands somewhere "
                            f"without the questions; the entry must link the "
                            f"Q-bearing doc (re-run the queries render)"
                        ),
                        mechanically_fixable=False,
                    ))
            else:
                if not extract_q_entries(target, parsed["basename"]):
                    findings.append(Finding(
                        severity="error",
                        surface_file=queries_file,
                        surface_line=line_num,
                        code="C46",
                        message=(
                            f"Questions entry links '{target.stem}' but that "
                            f"doc has zero pending Qs — the reader lands on a "
                            f"document with nothing to answer (stale render or "
                            f"stale bracket; re-run the queries render / audit "
                            f"--fix)"
                        ),
                        mechanically_fixable=False,
                    ))
    return findings


def check_c34_inline_q_in_row_body(backlog_files: list[Path]) -> list[Finding]:
    """C34: inline `Q<n>` bullets inside backlog row bodies are forbidden.

    For **F-rows** Qs belong in the feature doc (`{slug} Features/F<n> —
    Title.md` § `## Open Questions`) — the doc is the Q home and the row links
    it. **T-/B-rows had no feature doc** when this check was aligned
    (2026-07-06), so the row ITSELF was the sanctioned Q-bearing target and
    well-formed `- **Q<n> —` sub-bullets on a T-/B-row are exempt here.

    **F329 retired that premise** — every row kind mints a doc now, so the
    exemption below no longer describes a sanctioned form, only a legacy
    population. It is kept because C34 is an ERROR: promoting several anchors'
    unmigrated rows to a red stop-gate is not this check's call to make. The
    invariant those rows break is owned by **C57**, at warning severity, which
    sees all four host shapes rather than only this one.
    """
    findings: list[Finding] = []
    # Match `- **Q<n> —` or `  - **Q<n> —` (indented or not — any bullet form).
    inline_q_re = re.compile(r"^\s*- \*\*Q\d+\s+[—-]")
    row_open_re = re.compile(r"^- \*\*([A-Za-z]+)[-]?\d*")
    for backlog_file in backlog_files:
        try:
            text = backlog_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        current_h2 = ""
        row_kind = ""
        in_fence = False
        for i, line in enumerate(lines, start=1):
            if re.match(r"^\s*```", line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEADING_RE.match(line)
            if m and m.group(1) == "##":
                current_h2 = m.group(2).strip()
                row_kind = ""
                continue
            rm = row_open_re.match(line)
            if rm:
                row_kind = rm.group(1)
            # Skip Done/Icebox/Verify (Verify rows reference Qs legitimately).
            if current_h2 in ("Done", "Icebox", "Verify", ""):
                continue
            # T-/B-row inline Qs are the sanctioned no-doc form (see docstring).
            # `Q` joins them per F275 (T079): a standalone Q-row's own header
            # matches `inline_q_re`, so without this the shape the mint writes
            # is flagged the instant it exists.
            if row_kind in ("T", "B", "Q"):
                continue
            if inline_q_re.match(line):
                findings.append(Finding(
                    severity="error",
                    surface_file=backlog_file,
                    surface_line=i,
                    code="C34",
                    message=(
                        f"inline `Q<n>` bullet in backlog row body (`## {current_h2}`) "
                        f"— Qs belong in a feature doc's `## Open Questions` H2 or in "
                        f"`{{slug}} queries.md` § `## Questions` per [[ask-format]]. Move the Q to "
                        f"the appropriate surface and replace this row's body with "
                        f"a `→ [[F<n> — Title]]` link."
                    ),
                    mechanically_fixable=False,
                ))
    return findings


def check_c35_ask_md_drift(
    anchor_backlogs: dict[str, Path],
    vault_index: dict[str, list[Path]],
) -> list[Finding]:
    """C35 (F124; queries-surface per F176): each Q<n> reference in
    `{slug} queries.md` § Questions must correspond to a pending Q in the
    linked feature doc.

    Surfacing case (F077 Q7, 2026-06-06): the carried-forward 'F077 ... (Q1, Q7)'
    listed Q7 as pending while F077's doc had Q7 in `### Resolved` (choice A).
    `/query` rebuilds from current state, but a stale view can persist between
    runs — this check mechanizes the drift catch.

    Walks each anchor backlog's sibling `{slug} queries.md` file, parses the
    `## Questions` H2 region, extracts wiki-linked feature docs + the
    Q-numbers each bullet claims pending, then cross-checks against the
    linked doc's actual pending-Q set via `extract_q_entries` (which is
    now H3-aware thanks to F123).
    """
    findings: list[Finding] = []
    q_ref_re = re.compile(r"\bQ(\d+)\b")
    # A claim of pendingness, not a mention: `- Q5 — ...` at the head of an
    # enumeration sub-bullet. See the note at its use site below.
    q_claim_re = re.compile(r"-\s*\*{0,2}Q(\d+)\b")
    wiki_link_re = re.compile(r"\[\[([^|\]]+?)(?:\|[^\]]+)?\]\]")
    for name, backlog_file in anchor_backlogs.items():
        queries_file = backlog_track_dir(backlog_file) / f"{name} queries.md"
        if not queries_file.is_file():
            continue
        try:
            text = queries_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        # Find ## Questions H2 region
        q_start = -1
        q_end = len(lines)
        for i, line in enumerate(lines):
            if line.strip() == "## Questions":
                q_start = i + 1
            elif q_start >= 0 and re.match(r"^## ", line):
                q_end = i
                break
        if q_start < 0:
            continue
        # Parse bullets in the Questions region.
        #
        # Only TOP-LEVEL bullets are entries. An indented bullet is a rendered
        # Q body belonging to the entry above it, and it is already consumed as
        # a continuation line below — so matching it here reads it a second
        # time, as an entry in its own right. When such a Q body happens to
        # *link* another feature doc, that doc gets reported as wrongly listed
        # under `## Questions`, which it never was. Observed 2026-07-30: F288's
        # Q1 links F287 to explain where the question came from, and C35
        # flagged F287 — whose Qs are all resolved — as drifted.
        for line_num in range(q_start, q_end):
            line = lines[line_num]
            if not re.match(r"^-\s+", line):
                continue
            link_m = wiki_link_re.search(line)
            if not link_m:
                continue
            target_name = link_m.group(1).strip()
            # Strip any block-ID fragment from target name
            if "#" in target_name:
                target_name = target_name.split("#", 1)[0]
            target_file = resolve_target(target_name, queries_file, vault_index)
            if target_file is None or not target_file.is_file():
                continue  # link resolution belongs to C1/C22
            # Only feature docs participate (skip non-F<n> targets like
            # `[[DAS ...]]` references inside descriptive text).
            fnum = feature_number(target_file.stem, target_file)
            if not fnum:
                continue
            container_id = fnum
            # Extract claimed Q-numbers from the bullet line (and any
            # immediately-following indented continuation lines).
            bullet_lines = [line]
            j = line_num + 1
            while j < q_end:
                nxt = lines[j]
                if nxt.startswith("  ") or nxt.startswith("\t"):
                    bullet_lines.append(nxt)
                    j += 1
                elif nxt == "":
                    break
                else:
                    break
            # Only an ENUMERATION position counts as a claim. Scanning the
            # whole bullet for \bQ<n>\b makes any Q whose TITLE names another
            # question ("Q6 — Q3's scope ruling selects the whole vault") read
            # as a claim that Q3 is pending, and report drift against a
            # correctly-rendered file. queries-render only ever enumerates as
            # `- Q<n> — <title>`, and the file is machine-written, so anchoring
            # to that position loses nothing.
            claimed = sorted({int(m.group(1))
                              for ln in bullet_lines
                              for m in [q_claim_re.match(ln.strip())] if m})
            pending_qs = {q.q_num for q in extract_q_entries(target_file, container_id)}
            # Core drift (F176 fix): a feature listed under `## Questions` whose
            # linked doc has ZERO pending Qs is wrong regardless of whether the
            # bullet enumerates specific `Q<n>` numbers. The earlier logic only
            # fired when explicit Q-numbers were claimed, so a prose pendingness
            # claim ("4 design Qs pending", no Q<n> token) against an all-resolved
            # doc slipped through (observed: MUX F125, 2026-06-16).
            if not pending_qs:
                findings.append(Finding(
                    severity="warning",
                    surface_file=queries_file,
                    surface_line=line_num + 1,
                    code="C35",
                    message=(
                        f"queries.md lists {container_id} under `## Questions` but "
                        f"its linked doc has no pending Qs (all resolved or absent). "
                        f"Remove the entry / re-run /query to rebuild from current state."
                    ),
                    mechanically_fixable=False,
                ))
                continue
            if not claimed:
                continue
            stale = [q for q in claimed if q not in pending_qs]
            if not stale:
                continue
            pending_str = (
                ", ".join(f"Q{n}" for n in sorted(pending_qs))
                if pending_qs else "none"
            )
            stale_str = ", ".join(f"Q{n}" for n in stale)
            findings.append(Finding(
                severity="warning",
                surface_file=queries_file,
                surface_line=line_num + 1,
                code="C35",
                message=(
                    f"queries.md claims {stale_str} pending in {container_id} "
                    f"but linked doc has those resolved or absent "
                    f"(actual pending: {pending_str}). Re-run /query to rebuild "
                    f"from current state; drift carried forward."
                ),
                mechanically_fixable=False,
            ))
    return findings


################################################################
# C37–C40, C42 — {slug} queries.md answer-section format
# (C41 is NOT here — it is the soak/Verify-question check above; F251 #10
#  removed a phantom "C41" row this section's docstring once claimed.)
# (user direction 2026-06-16): the items a user answers must be
# referenceable + well-formed so an answer like "Q2: A" / "V1: yes"
# is unambiguous, and every decision forces the agent to state a
# recommendation (even "None").
################################################################

_Q_WIKILINK_RE = re.compile(r"\[\[[^\]]*\]\]")
_Q_FNUM_RE = re.compile(r"\bF\d{1,4}\b")
# Status brackets are machine syntax written and parsed by `state` — the blocker
# token in `[Blocked ATT-F041]` can never be a wiki-link, so C37 must not see it.
# Without this, `[Blocked DKT-T001]` passes while `[Blocked DKT-F098]` errors:
# same grammar, opposite verdict, decided only by task-vs-feature (ATT 2026-08-08).
_Q_STATUS_RE = re.compile(r"\[(?:Blocked|Waiting)[^\]]*\]")
_Q_VHANDLE_RE = re.compile(r"^\s*-\s+\*\*V\d+\b")
_Q_QHANDLE_RE = re.compile(r"^\s*-\s+\*\*Q\d+\b")
_Q_YESNO_RE = re.compile(r"\*\*[^*]*yes\s*/\s*no[^*]*\*\*", re.IGNORECASE)
_Q_OPTION_RE = re.compile(r"\*\*\([A-Za-z]\)\*\*")
# C42 — every artifact a surfaced item names must be a live wiki-link.
_Q_MDLINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")        # [text](url) md-links
_Q_BACKTICK_RE = re.compile(r"`([^`\n]+)`")              # `code span`
# A slug-prefixed doc name: a Capitalized token + ≥1 more Capitalized token,
# e.g. "DAS PRD", "DAS Decisions", "SKA Backlog", "US CAE". Matches whole phrase
# (no capturing group → findall returns the full match).
_Q_SLUGDOC_RE = re.compile(r"\b[A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]+)+\b")
_Q_ARTIFACT_EXT_RE = re.compile(
    r"\.(md|py|svg|png|d2|sh|yaml|yml|json|txt|rs|ts|js)$", re.IGNORECASE)

# ---- T163: the renderer's own bullet-label fallback is not prose ----------
# `{slug} queries.md` is machine-rendered ("Do not hand-edit; edit the backlog
# rows"). Its bullets have two halves with two different authors:
#   LABEL  — written by queries-render.py `_bullet_link`, whose resolve-before-
#            emit chain ends at a PLAIN-TEXT last resort (step 5) when nothing
#            resolves: no `→ [[…]]` arrow link, no feature-doc basename, no
#            `^{id}` block anchor in the backlog. It emits the bare identifier
#            deliberately — "better a non-link than a dead link".
#   BODY   — carried verbatim from the backlog row, i.e. authored prose.
# C37 is a prose check. Firing it on the label makes the audit report its own
# writer's output as a defect (the T137 / T120 shape), and the "fix" it names —
# hand-write a wiki-link into a rendered file — is one the next render erases.
# So the label position is exempt, but ONLY when the fallback condition still
# holds. If a target has since appeared, the bare label is a STALE RENDER, not
# a last resort, and C37 keeps speaking up.
#
# Label position, matching every `_bullet_link` call site in queries-render.py:
#   `- {ID} — …`            (Blockers / Ready / Blocked / Verifications / Other)
#   `- **U{n}** {ID} — …`   (User)
#   `- {ID} **(3Q)** …`     (Questions)
_Q_RENDER_LABEL_RE = re.compile(
    r"^-\s+(?:\*\*U\d+\*\*\s+)?(F\d{1,4})\b(?=\s*(?:—|\*\*|$))")
# The row's own bold run, read exactly as `_bullet_link` step 2 reads it:
# `^- \*\*([^*]+)\*\*`. On a well-formed row that is `F020 — Title`; on the
# malformed LRN TPM shape it is `F020 [Ready]`, which resolves to nothing —
# which is precisely why the renderer fell through to plain text there.
_Q_ROW_BOLD_RE = re.compile(r"^- \*\*([^*]+)\*\*")
_Q_ARROW_RE = re.compile(r"→\s*\[\[([^\]]+)\]\]")


def _render_fallback_rows(backlog_file: Path) -> dict[str, str]:
    """identifier → raw backlog line, for every top-level bullet whose bold run
    opens with an `F<n>` token. Deliberately permissive about the rest of the
    header: the rows this matters for are the ones the canonical parser
    REFUSES (T163's malformed headers), so keying off the canonical parse
    would skip exactly the population being measured. Read once per anchor.
    """
    rows: dict[str, str] = {}
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return rows
    for line in lines:
        m = _Q_ROW_BOLD_RE.match(line)
        if not m:
            continue
        head = re.match(r"(F\d{1,4})\b", m.group(1).strip())
        if head:
            rows.setdefault(head.group(1), line)
    return rows


def _render_label_fallback(identifier: str, rows: dict[str, str],
                           backlog_block_ids: dict[str, int],
                           vault_index: dict[str, list[Path]]) -> bool:
    """True when `_bullet_link` would legitimately emit `identifier` bare.

    Replays the resolve-before-emit chain of `queries-render.py _bullet_link`
    against the same three inputs it uses — the row's `→ [[…]]` arrow link,
    the row's bold-run title as a doc basename, and the `^{id}` block anchor
    in the anchor's own Backlog. If ANY of them resolves, the renderer had a
    link available and a bare label is stale output, not the last resort — so
    C37 keeps reporting it. Only a chain that falls all the way through earns
    the exemption.

    This mirrors logic that lives in the renderer; `test-t163-c37-render-
    fallback.py` pins the two together, exercising both a resolving row (C37
    fires) and a fall-through row (C37 silent).
    """
    raw = rows.get(identifier)
    if raw is None:
        # No such row in this backlog — the label did not come from a row here,
        # so it is not this renderer's fallback. Let C37 speak.
        return False
    # Step 1 — the row's own arrow link.
    arrow = _Q_ARROW_RE.search(raw)
    if arrow:
        bn = arrow.group(1).split("#")[0].split("|")[0].strip()
        if vault_index.get(bn.lower()):
            return False
    # Step 2 — the row's bold run as a doc basename.
    bold = _Q_ROW_BOLD_RE.match(raw)
    if bold and vault_index.get(bold.group(1).strip().lower()):
        return False
    # Step 3 — the backlog block anchor.
    if identifier in backlog_block_ids:
        return False
    return True


def check_c37_queries_item_format(
        anchor_backlogs: dict[str, Path],
        vault_index: dict[str, list[Path]]) -> list[Finding]:
    """Format rules for the answer-requiring sections of `{slug} queries.md`:

      C37 — bare F-number must be a wiki-link (any bullet, any section).
      C38 — `## Verifications` bullets begin with a bold `**V<n>` handle.
      C39 — `## Immediate Questions` bullets begin with a bold `**Q<n>` handle.
      C40 — `## Verifications` + `## Immediate Questions` bullets carry an answer
            shape: bold `**yes/no**`, or bold labeled options `**(A)** / **(B)**`.
      C42 — an answerable item (Verifications / Immediate Questions / Questions)
            that NAMES a doc/file/template the user must open must make it a live
            `[[wiki-link]]` — a bare resolvable slug-prefixed doc name (e.g.
            `DAS PRD`) or a code-span filename (e.g. `` `_Disk {{LABEL}}
            Template.md` ``) is a violation: the user cannot follow a name.
    """
    findings: list[Finding] = []
    for name, backlog_file in anchor_backlogs.items():
        qf = backlog_track_dir(backlog_file) / f"{name} queries.md"
        if not qf.is_file():
            continue
        try:
            lines = qf.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        section: Optional[str] = None
        toplevel = re.compile(r"^-\s+")
        reco_bullet = re.compile(r"^-\s+\*\*Recommendation\b")
        # Read once per anchor (T163) — the label exemption needs both per bullet.
        backlog_block_ids = block_ids_in(backlog_file)
        backlog_rows = _render_fallback_rows(backlog_file)
        for i, line in enumerate(lines):
            h = re.match(r"^##\s+(.+?)\s*$", line)
            if h:
                section = h.group(1).strip()
                continue
            # Only a TOP-LEVEL bullet opens an item. Indented bullets (option
            # sub-bullets in the standard expanded format) and the
            # `- **Recommendation:**` bullet are PART of the item they follow,
            # not new items — they must not be checked as standalone handles.
            if not toplevel.match(line):
                continue
            if reco_bullet.match(line):
                continue
            ln = i + 1
            # Gather the whole item: opener + following indented lines (options)
            # + a following top-level `**Recommendation` bullet.
            item = line
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if nxt.startswith("  ") or nxt.startswith("\t"):
                    item += " " + nxt.strip()
                    j += 1
                elif reco_bullet.match(nxt):
                    item += " " + nxt.strip()
                    j += 1
                else:
                    break
            is_verif = (section == "Verifications")
            is_imm = (section == "Immediate Questions")
            is_ques = (section == "Questions")

            # C37 — bare F-number anywhere in the item (wiki-links AND
            # code-spans blanked first). Without the _strip_code_spans compose,
            # bare F-numbers inside filenames like `~/F006-status.md` false-fire
            # (SKA F227 fix, 2026-07-05).
            # T163: blank the renderer's own plain-text bullet label first —
            # it is `_bullet_link`'s step-5 last resort, not authored prose.
            # Only the label token is blanked; the body it introduces is still
            # scanned, which is how the one genuine prose reference in the
            # vault (LRN TPM's `per SKA F062`) keeps being reported.
            scanned = item
            lab = _Q_RENDER_LABEL_RE.match(scanned)
            if lab and _render_label_fallback(
                    lab.group(1), backlog_rows, backlog_block_ids, vault_index):
                scanned = (scanned[:lab.start(1)] + " " * len(lab.group(1))
                           + scanned[lab.end(1):])
            bare = sorted(set(_Q_FNUM_RE.findall(
                _strip_code_spans(_Q_STATUS_RE.sub("",
                    _Q_WIKILINK_RE.sub("", scanned)))
            )))
            for fn in bare:
                findings.append(Finding(
                    severity="error", surface_file=qf, surface_line=ln, code="C37",
                    message=(
                        f"bare F-number `{fn}` must be a wiki-link — to its feature "
                        f"doc `[[{fn} — Title|{fn}]]` if one exists, else to the "
                        f"backlog row `[[{{slug}} Backlog#^{fn}|{fn}]]` (many items "
                        f"are bare backlog rows with no feature doc)."),
                    mechanically_fixable=False))

            if is_verif and not _Q_VHANDLE_RE.match(line):
                findings.append(Finding(
                    severity="error", surface_file=qf, surface_line=ln, code="C38",
                    message=("Verifications item must begin with a bold `**V<n>` "
                             "handle (e.g. `- **V1 — …`) so you can answer it by "
                             "reference (`V1: yes`)."),
                    mechanically_fixable=False))
            if is_imm and not _Q_QHANDLE_RE.match(line):
                findings.append(Finding(
                    severity="error", surface_file=qf, surface_line=ln, code="C39",
                    message=("Immediate Questions item must begin with a bold "
                             "`**Q<n>` handle (e.g. `- **Q1 — …`) so you can answer "
                             "it by reference (`Q1: A`)."),
                    mechanically_fixable=False))
            if is_verif or is_imm:
                if not (_Q_YESNO_RE.search(item) or _Q_OPTION_RE.search(item)):
                    findings.append(Finding(
                        severity="error", surface_file=qf, surface_line=ln, code="C40",
                        message=("no answer shape — a user-answered item needs a "
                                 "bold `**yes/no**` (Verifications) or bold labeled "
                                 "options `**(A)** / **(B)** / …` (Immediate "
                                 "Questions). The Recommendation line + option "
                                 "format are enforced by C9 / C19."),
                        mechanically_fixable=False))

            # C42 — every artifact the item names must be a live wiki-link.
            # An answerable item that tells the user to open a doc/file/template
            # must LINK it; a bare name or a code-span filename leaves the user
            # hunting. Fixed at the SOURCE (the backlog `- **Verify:**` /
            # question body), so mechanically_fixable=False.
            if is_verif or is_imm or is_ques:
                offenders: list[str] = []
                # (a) code-span filenames that C36 skips (templated / multi-word):
                #     `_Disk {{LABEL}} Template.md`, `DAS PRD.md`.
                for span in _Q_BACKTICK_RE.findall(item):
                    s = span.strip()
                    if _Q_ARTIFACT_EXT_RE.search(s) and (
                            "{" in s or "}" in s or " " in s):
                        offenders.append(f"`{s}`")
                # (b) bare slug-prefixed doc names that resolve in the vault —
                #     wiki-links / md-links / code spans blanked first so only
                #     genuinely-BARE references remain.
                plain = _Q_BACKTICK_RE.sub(
                    "", _Q_MDLINK_RE.sub("", _Q_WIKILINK_RE.sub("", item)))
                for phrase in _Q_SLUGDOC_RE.findall(plain):
                    if _is_placeholder_basename(phrase):
                        continue
                    if phrase in vault_index:
                        offenders.append(phrase)
                for off in dict.fromkeys(offenders):  # dedupe, preserve order
                    bare = off.strip("`")
                    # strip a trailing .md so the suggested link is the stem
                    link = _Q_ARTIFACT_EXT_RE.sub("", bare)
                    findings.append(Finding(
                        severity="error", surface_file=qf, surface_line=ln, code="C42",
                        message=(
                            f"names an artifact in bare text — {off} — but every "
                            f"doc/file a question or verification tells the user to "
                            f"open MUST be a live wiki-link `[[{link}]]`. Fix at the "
                            f"source (the backlog row's `- **Verify:**` line or the "
                            f"question body), never in the rendered queries.md."),
                        mechanically_fixable=False))
    return findings


################################################################
# C36 (F126) — backtick-quoted file-paths must be links
################################################################

# Recognized file extensions for bare-filename detection
_C36_EXTENSIONS = (
    "md", "py", "sh", "yaml", "yml", "toml", "json", "txt",
    "html", "css", "rs", "ts", "tsx", "js", "jsx",
)
_C36_EXT_RE = re.compile(
    r"\.(" + "|".join(_C36_EXTENSIONS) + r")$"
)

# Capture every backtick-quoted token on a line that doesn't already
# straddle a line boundary. We restrict to single-backtick spans so we
# don't accidentally pick up ``code with `nested` `` fragments.
_BACKTICK_SPAN_RE = re.compile(r"`([^`\n]+)`")

# Inside a backtick token, the path-like content. Either:
#  - starts with `/`, `~/`, `./`, `../`
#  - bare filename ending in a recognized extension
_C36_PATH_LEAD_RE = re.compile(r"^(/|~/|\./|\.\./)")


def _c36_is_path_like(token: str) -> bool:
    """Heuristic: token inside backticks looks like a single file-path.

    Rejects:
    - whitespace (command-line)
    - code shapes (parens, equals, braces)
    - glob/regex metacharacters
    - directory references ending in `/`
    - templated paths containing `<...>` placeholders or `{...}` or YYYY/NNN
      style placeholders
    - slash-commands (single segment after `/`, all lowercase a-z0-9-)
    """
    t = token.strip()
    if not t:
        return False
    # Reject obvious non-path shapes
    if any(c in t for c in " \t"):
        return False  # command-line / multi-word
    if any(c in t for c in "()=<>|&;{}"):
        return False  # code / templated
    if any(c in t for c in "*?"):
        return False  # glob
    if "[" in t or "]" in t:
        return False  # regex/glob class
    # Reject directory references ending in `/`
    if t.endswith("/"):
        return False
    # Reject placeholder paths
    if "YYYY" in t or "MM-DD" in t or "NNN" in t:
        return False
    # Reject bare-extension mentions like `.md` / `.html` (no stem)
    if t.startswith(".") and _C36_EXT_RE.fullmatch(t):
        return False
    # Reject slash-commands: leading `/` followed by a single segment of
    # lowercase letters / digits / hyphens — these are `/query`, `/groom`,
    # `/audit foo`, etc., NOT file paths.
    if t.startswith("/"):
        rest = t[1:]
        if "/" not in rest and not _C36_EXT_RE.search(rest):
            # single-segment after leading slash, no extension → command
            return False
    # Reject `.app` directory bundles (macOS) — they aren't text files
    if t.endswith(".app"):
        return False
    # Accept absolute / home / relative paths
    if _C36_PATH_LEAD_RE.match(t):
        return True
    # Accept bare basenames ending in a recognized extension
    if _C36_EXT_RE.search(t):
        # But require it look like a filename (no `/` already counted by the
        # absolute case; bare-basename means no `/` at all)
        return "/" not in t
    return False


def _c36_resolve_replacement(
    token: str, vault_index: dict[str, list[Path]]
) -> Optional[str]:
    """Compute the replacement link for a path-like backtick token.

    Returns the replacement string (without surrounding backticks) or
    None if no clean replacement exists — caller leaves the backticks
    intact and routes to QFix for manual review.

    Discipline (post-shipping-bug 2026-06-07): NEVER emit a markdown link
    `[name](path)` whose path doesn't actually resolve. A non-resolving
    link breaks C1/C22 link-existence checks downstream. The valid
    replacements are:
      - `[[stem]]`     — only when stem is in the vault index (.md files)
      - `[name](path)` — only when the path resolves on disk (absolute,
                         `~/`-expanded, or relative-to-vault-root)
      - None           — otherwise; caller leaves the backticks intact
    """
    raw = token.strip()
    name = raw.rsplit("/", 1)[-1]
    if "." in name:
        stem = name.rsplit(".", 1)[0]
        ext = name.rsplit(".", 1)[1].lower()
    else:
        stem = name
        ext = ""
    # Safe automatic replacements (in priority order):
    #
    # 1. Wiki-link `[[stem]]` — when basename is `.md` AND uniquely resolvable
    #    in the vault index. Ambiguous basenames (SKILL.md, README.md, ...)
    #    are skipped: the resulting `[[SKILL]]` would silently resolve
    #    "somewhere" via path-proximity, worse affordance than the backticks.
    if ext == "md" and stem.lower() in vault_index and len(vault_index[stem.lower()]) == 1:
        return f"[[{stem}]]"
    # 2. Markdown link `[name](path)` — when the path is ABSOLUTE (starts
    #    with `/` or `~/`) AND the file actually exists on disk. Absolute
    #    paths are unambiguous; the existing `_parse_markdown` resolver
    #    accepts them correctly (no C1/C22 false positive). Relative paths
    #    are deliberately skipped — they'd resolve to "source_file/path"
    #    which is almost never what the author meant, and would trigger
    #    C22 link-existence errors downstream.
    if raw.startswith(("/", "~/")):
        expanded = Path(raw).expanduser()
        if expanded.is_file():
            return f"[{name}]({raw})"
    return None


def _c36_is_inside_existing_link(line: str, span_start: int) -> bool:
    """Crude check: is the column inside an existing [..](..) or [[..]]?

    Looks at the prefix of the line. If an unmatched `[` precedes the span
    without a closing `]` between it and the span, we're inside a markdown
    or wiki link target/text and should NOT flag this backtick.
    """
    prefix = line[:span_start]
    # Count unbalanced `[` vs `]` to the left of the span.
    open_brackets = prefix.count("[") - prefix.count("]")
    return open_brackets > 0


def check_c36_backtick_filepath(
    file_path: Path, vault_index: dict[str, list[Path]]
) -> list[Finding]:
    """C36: backtick-quoted file-paths on Q.md / queries.md should be wiki-links
    or markdown-links so they're clickable.

    Surfacing case (F126, 2026-06-07): the user observed that bare backtick
    file-path tokens in `Q.md` / `{slug} queries.md` aren't navigable from
    Obsidian — they look like links but aren't, forcing the user to manually
    copy the path. C36 forbids them and `--fix` mechanically replaces them.
    """
    findings: list[Finding] = []
    if not file_path.is_file():
        return findings
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return findings
    in_fence = False
    for line_num, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Skip audit-q residual sub-bullets — these are findings rendered as
        # `- **C<NN>** ...` on a B-QFix row; the backticks in their bodies are
        # quoting the original finding's offending token, not a real path the
        # author wrote. Re-flagging them creates a recursion where every audit
        # pass surfaces residuals as new findings.
        if re.match(r"^\s*-\s+\*\*[CD]\d+\*\*\s", line):
            continue
        for m in _BACKTICK_SPAN_RE.finditer(line):
            token = m.group(1)
            if not _c36_is_path_like(token):
                continue
            if _c36_is_inside_existing_link(line, m.start()):
                continue
            replacement = _c36_resolve_replacement(token, vault_index)
            if replacement is None:
                # No resolvable link target exists — a code-source file
                # (`lib.rs`, `cocoa.rs`), a config/runtime file with no vault
                # doc (`config.yaml`, `mux-targets.json`), or a non-existent
                # absolute path (`/tmp/hidmove`). Backticks are the CORRECT
                # rendering for these; C36's premise ("should be a link") only
                # holds when the path CAN become one. Skip — never file an
                # unfixable "manual review" residual that can never be cleared
                # (the QFix-never-clears bug). Genuinely-broken doc references
                # are C1/C22's job, not C36's. 2026-06-14.
                continue
            findings.append(Finding(
                severity="warning",
                surface_file=file_path,
                surface_line=line_num,
                code="C36",
                message=f"backtick file-path `{token}` should be a link — suggested: `{replacement}`",
                mechanically_fixable=True,
            ))
    return findings


def apply_c36_fix(
    file_path: Path,
    findings: list[Finding],
    vault_index: dict[str, list[Path]],
) -> int:
    """Apply mechanical replacements for C36 findings on file_path.

    Processes findings descending by (line, span-start) so earlier offsets
    on the same line aren't invalidated by later edits. Idempotent: a
    second pass on the cleaned file produces 0 changes.
    Returns the number of replacements actually applied.
    """
    relevant = [
        f for f in findings
        if f.code == "C36"
        and f.surface_file == file_path
        and f.mechanically_fixable
    ]
    if not relevant:
        return 0
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    except (OSError, UnicodeDecodeError):
        return 0
    # F251 #4 — do NOT gate on the findings' stored `surface_line`: check_c36
    # runs BEFORE apply_placement_fixes shifts backlog rows, so those numbers
    # are stale by the time we get here and would land the sub on the wrong
    # line (worst case: turning an inert backtick in a B-QFix residual into a
    # live link). Instead re-derive the fix from the CURRENT file with the
    # exact same predicate check_c36 uses (fence-skip + residual-row skip +
    # path-like + resolvable), so the fixer is line-shift-immune and stays
    # consistent with the checker. `relevant` is used only to early-out.
    applied = 0

    def _sub(m: re.Match) -> str:
        nonlocal applied
        token = m.group(1)
        if not _c36_is_path_like(token):
            return m.group(0)
        # Check column-context guard (existing-link)
        prefix = m.string[:m.start()]
        if (prefix.count("[") - prefix.count("]")) > 0:
            return m.group(0)
        replacement = _c36_resolve_replacement(token, vault_index)
        if replacement is None:
            return m.group(0)
        applied += 1
        return replacement

    in_fence = False
    for idx in range(len(lines)):
        line = lines[idx]
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # F251 #4 — mirror check_c36's residual-row skip: a `- **C<NN>** …`
        # audit residual sub-bullet quotes a prior finding's token in backticks,
        # not a real path; converting it to a link is the exact cascade the
        # checker's guard prevents.
        if re.match(r"^\s*-\s+\*\*[CD]\d+\*\*\s", line):
            continue
        lines[idx] = _BACKTICK_SPAN_RE.sub(_sub, line)
    if applied:
        file_path.write_text("".join(lines), encoding="utf-8")
        _selffire(file_path)
    return applied


def apply_c23_fix(backlog_file: Path,
                  entries: list[BacklogEntry]) -> tuple[bool, list[str]]:
    """Rewrite [Designing] brackets to [N Questions] or [Ready] based on
    pending Q-count in linked feature docs. Returns (changed, log)."""
    fix_log: list[str] = []
    designing = [e for e in entries if has_member(e.status, "Designing")]
    if not designing:
        return False, []
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines(keepends=False)
    except (OSError, UnicodeDecodeError):
        return False, []
    changed = False
    for e in designing:
        # F275 (T079) — a standalone Q-row IS one pending question; counting
        # it the normal way yields zero and would promote it to [Ready].
        if _is_standalone_q_row(e.identifier):
            pending = 1
            new_bracket = "[Questions]"
            line_idx = e.source_line - 1
            if line_idx < 0 or line_idx >= len(lines):
                continue
            old_line = lines[line_idx]
            h_start, h_end = _head_span(old_line)
            head = old_line[h_start:h_end]
            new_head = head.replace("[Designing]", new_bracket, 1)
            if new_head == head:
                continue
            lines[line_idx] = old_line[:h_start] + new_head + old_line[h_end:]
            changed = True
            fix_log.append(
                f"row '{e.identifier}' [Designing] → {new_bracket} "
                f"(standalone Q-row — self-backing, F275)"
            )
            continue
        # Arrow-form link only (T012 — mirrors check_c23's target selection).
        arrow_link = _arrow_target(e)
        if arrow_link is not None:
            target_file = arrow_link.target_file_path
            if target_file is None or not target_file.is_file():
                continue
            container_id = e.identifier
            fnum = feature_number(target_file.stem, target_file)
            if fnum:
                container_id = fnum
            pending = len(extract_q_entries(target_file, container_id))
        else:
            pending = _row_inline_q_count(e)
        if pending > 0:
            new_bracket = (
                f"[{pending} Questions]" if pending > 1 else "[Questions]"
            )
        elif _row_has_next(e):
            new_bracket = "[Ready]"
        else:
            # F250 #10 — 0 pending Qs but no `- **Next:**` → can't be [Ready]
            # (F171). Leave [Designing] (no-op rewrite below); check_c23 surfaces
            # it as needing a Next.
            new_bracket = "[Designing]"
        # 0-indexed line
        line_idx = e.source_line - 1
        if line_idx < 0 or line_idx >= len(lines):
            continue
        old_line = lines[line_idx]
        # Replace [Designing] with new_bracket only within the row's head region
        # (between **Title** and the first REAL ` — `). F251 #6 — head offsets
        # come from the SAME cleaned-line computation _detect_status uses, so a
        # ` — ` inside a leading wiki-link can't truncate the head before the
        # bracket (which would silently no-op and flap the finding).
        h_start, h_end = _head_span(old_line)
        head = old_line[h_start:h_end]
        new_head = head.replace("[Designing]", new_bracket, 1)
        if new_head == head:
            continue
        new_line = old_line[:h_start] + new_head + old_line[h_end:]
        lines[line_idx] = new_line
        changed = True
        fix_log.append(
            f"row '{e.identifier}' [Designing] → {new_bracket} "
            f"(pending Qs: {pending})"
        )
    if changed:
        backlog_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        _selffire(backlog_file)
    return changed, fix_log


def apply_c24_fix(backlog_file: Path,
                  entries: list[BacklogEntry]) -> tuple[bool, list[str]]:
    """Rewrite `[Questions]` / `[N Questions]` brackets to match the linked
    feature doc's actual pending-Q count. Mirrors apply_c23_fix's mechanics.
    Returns (changed, log). Bare `[Questions]` on a row whose linked doc has
    7 Qs becomes `[7 Questions]`; `[3 Questions]` on a doc with 0 Qs becomes
    `[Ready]` (the bracket-promise is stale, downstream of all Qs being
    resolved without the bracket being updated)."""
    fix_log: list[str] = []
    questions_rows: list[tuple[BacklogEntry, str]] = []
    for e in entries:
        if not e.status:
            continue
        if questions_member(e.status):
            questions_rows.append((e, e.status))
    if not questions_rows:
        return False, []
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines(keepends=False)
    except (OSError, UnicodeDecodeError):
        return False, []
    changed = False
    for e, old_status in questions_rows:
        # F275 (T079) — a standalone Q-row is self-backing: its bracket is
        # never counted against anything. THIS was the silent revert behind
        # T079 — `state … Q001 set --status Questions` wrote [Questions], then
        # this fixer counted zero inline Qs (the sub-bullets are ask-format
        # options, not `- **Q<n> —` headers) and rewrote it straight back.
        if _is_standalone_q_row(e.identifier):
            continue
        # Arrow-form only (mirrors check_c24, 2026-07-06 + T012 2026-07-13):
        # an in-prose link is a mention, not the row's doc; _arrow_target
        # resolves the arrow link itself (not the row's first link of any
        # form); T-/B-rows count their inline Qs from the row's own span.
        arrow_link = _arrow_target(e)
        if arrow_link is not None:
            target_file = arrow_link.target_file_path
            if target_file is None or not target_file.is_file():
                continue
            container_id = e.identifier
            fnum = feature_number(target_file.stem, target_file)
            if fnum:
                container_id = fnum
            actual = len(extract_q_entries(target_file, container_id))
        elif re.search(r"→\s+\[\[", e.raw_body):
            continue  # arrow present but unparseable — C1/C22's territory
        else:
            actual = _row_inline_q_count(e)
        qm = questions_member(old_status)
        claimed = (qm[1] if qm and qm[1] is not None else 1)
        if actual == claimed:
            continue
        if actual == 0:
            # F250 #10 — promote to [Ready] only when a `- **Next:**` exists
            # (F171 forbids a [Ready] row without one, and this `--fix` writes
            # the bracket directly, bypassing state's write-path gate). Without
            # a Next, drop to [Designing]; check_c24/C23 surfaces the needs-Next.
            new_bracket = "[Ready]" if _row_has_next(e) else "[Designing]"
        else:
            new_bracket = (
                f"[{actual} Questions]" if actual > 1 else "[Questions]"
            )
        old_bracket = f"[{old_status}]"
        line_idx = e.source_line - 1
        if line_idx < 0 or line_idx >= len(lines):
            continue
        old_line = lines[line_idx]
        # Same head-region replacement as apply_c23_fix — head offsets from the
        # shared cleaned-line computation so a leading wiki-link's internal ` — `
        # can't truncate the head before the bracket (F251 #6).
        h_start, h_end = _head_span(old_line)
        head = old_line[h_start:h_end]
        new_head = head.replace(old_bracket, new_bracket, 1)
        if new_head == head:
            continue
        new_line = old_line[:h_start] + new_head + old_line[h_end:]
        lines[line_idx] = new_line
        changed = True
        fix_log.append(
            f"row '{e.identifier}' {old_bracket} → {new_bracket} "
            f"(pending Qs: {actual})"
        )
    if changed:
        backlog_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        _selffire(backlog_file)
    return changed, fix_log


def _resolve_owning_anchor(
    surface_file: Path, anchor_backlogs: dict[str, Path]
) -> Optional[str]:
    """Return the anchor name whose tree (anchor_root = backlog.parents[1])
    contains surface_file. Sorts anchors by anchor-root path length, longest
    first, so sub-anchors (e.g., A2X inside SVAR's tree) match before
    parents. Returns None when surface_file is outside every anchor tree
    (e.g., Q.md itself, or vault-level files).

    Was `backlog.parents[2]`, which assumed the 3-level {slug} Docs/{slug}
    Track/ layout; after the Docs-folder collapse the backlog is 2-level
    ({anchor}/{slug} Track/{slug} Backlog.md), so parents[2] overshot to the
    anchor's PARENT and QFix findings routed to the wrong anchor. parents[1]
    is the {anchor} root. (A `.anchor`-marker walk is NOT usable here: this
    vault nests `.anchor` markers at group/sub-anchor level, so the nearest
    marker is often an inner folder, not the backlog's own anchor.) (F251#1)"""
    candidates: list[tuple[int, str, Path]] = []
    for name, backlog in anchor_backlogs.items():
        try:
            root = backlog_track_dir(backlog).parent  # F329 folder-doc aware
        except IndexError:
            continue
        candidates.append((len(root.parts), name, root))
    # Longest-path first → most-specific anchor wins.
    candidates.sort(key=lambda t: t[0], reverse=True)
    for _, name, root in candidates:
        try:
            surface_file.relative_to(root)
            return name
        except ValueError:
            continue
    return None


def chores_path_for(backlog_file: Path) -> Path:
    """The anchor's `{slug} Chores.md` per R-chores-01: inside the folder-form
    backlog when the anchor has one, else beside the backlog in Track."""
    slug = backlog_file.stem[:-len(" Backlog")]
    if backlog_file.parent.name == backlog_file.stem:
        return backlog_file.parent / f"{slug} Chores.md"
    return backlog_track_dir(backlog_file) / f"{slug} Chores.md"


def file_qfix_row(
    backlog_file: Path, anchor_name: str, findings: list[Finding]
) -> tuple[bool, str]:
    """Route --fix residuals to `{slug} Chores.md` ([[DAS Chores]], F332 Q2 —
    supersedes the `B-QFix [Ready]` backlog row: mechanical audit debris is
    sub-surface work the user is neither aware of nor interested in, so it
    leaves the human queue). The audit-owned bullets (`- **C…**`) are
    rewritten wholesale each run; hand-added chores below them survive. A
    legacy B-QFix row found in the backlog is removed in the same pass.

    Idempotent: subsequent runs with the same findings produce an identical
    file; zero findings shouldn't happen here (the caller filters empties
    before calling).

    Returns (changed, summary_msg)."""
    try:
        text = backlog_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False, f"couldn't read {backlog_file.name}"

    lines = text.splitlines()
    # Format new sub-bullets — relative path to VAULT_ROOT for compactness.
    # Wrap any `[[X]]` wiki-link OR `[name](path)` markdown-link patterns in
    # the message text in backticks so `_strip_code_spans` makes them invisible
    # to C1/C22 link-resolution on subsequent runs. Without this guard,
    # sub-bullets containing finding messages with link forms are themselves
    # flagged as broken links → routing-induced cascade (observed 2026-06-04
    # for wiki-links and 2026-06-07 for markdown-links when F126 surfaced
    # markdown-link findings).
    def _backtick_wiki_links(msg: str) -> str:
        # Skip links that are ALREADY inside a code span — double-wrapping
        # produces broken nested-backtick output like `` `→ `[[X]]`` `` that
        # re-exposes the link to link-resolution on the next pass (observed
        # 2026-07-14: C43's message template pre-wraps `→ [[…]]` in one span,
        # and naive re-wrapping broke the span into two).
        stripped = _strip_code_spans(msg)
        def _wrap_if_outside_span(m: re.Match, wrap_fmt: str) -> str:
            if stripped[m.start():m.end()].strip() == "":
                return m.group(0)  # already inside a code span
            return wrap_fmt.format(m.group(0))
        msg = re.sub(
            r"\[\[[^\[\]]*\]\]",
            lambda m: _wrap_if_outside_span(m, "`{}`"),
            msg,
        )
        # Wrap markdown links: [name](path) — same guard.
        msg = re.sub(
            r"\[[^\[\]]+\]\([^)]+\)",
            lambda m: _wrap_if_outside_span(m, "`{}`"),
            msg,
        )
        return msg

    new_subs: list[str] = []
    for f in findings:
        try:
            rel = f.surface_file.relative_to(VAULT_ROOT)
        except ValueError:
            rel = f.surface_file
        safe_msg = _backtick_wiki_links(f.message)
        new_subs.append(
            f"  - **{f.code}** {rel}:{f.surface_line} — {safe_msg}"
        )

    # Chores bullets are flat (R-chores-02) — the sub-bullet indent goes.
    new_bullets = [s[2:] if s.startswith("  - ") else s for s in new_subs]

    chores_file = chores_path_for(backlog_file)
    slug = backlog_file.stem[:-len(" Backlog")]
    header = [
        "---",
        f"description: sub-surface chores for {anchor_name} — audit residuals "
        f"and other items the user is neither aware of nor interested in "
        f"([[DAS Chores]]).",
        "---",
        "",
        f"# {slug} Chores",
        "Fix each item at its source and delete its bullet; the `- **C…**` "
        "bullets are rewritten by every `/audit q --fix` run.",
        "",
    ]
    if chores_file.exists():
        try:
            old = chores_file.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            old = []
        # Preserve hand-added chores; the audit-owned `- **C…**` bullets are
        # replaced wholesale.
        hand = [l for l in old
                if l.startswith("- ") and not re.match(r"- \*\*C\d+\*\*", l)]
    else:
        hand = []
    chores_file.parent.mkdir(parents=True, exist_ok=True)
    chores_file.write_text(
        "\n".join(header + new_bullets + hand) + "\n", encoding="utf-8")
    _selffire(chores_file)
    result = (f"routed {len(findings)} residual(s) to {chores_file.name}")

    # Remove a legacy B-QFix row (plus its sub-bullets) from the backlog —
    # the extraction half of "QFix moves out" (F332), applied on touch.
    qfix_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("- **B-QFix"):
            qfix_idx = i
            break
    if qfix_idx is not None:
        end = qfix_idx + 1
        while end < len(lines):
            stripped = lines[end]
            if stripped.startswith("  - "):
                end += 1
                continue
            if not stripped.strip() and end + 1 < len(lines) \
                    and lines[end + 1].startswith("  - "):
                end += 1
                continue
            break
        if end < len(lines) and not lines[end].strip():
            end += 1
        del lines[qfix_idx:end]
        backlog_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        _selffire(backlog_file)
        result += " + removed legacy B-QFix row"

    return True, result


def clear_qfix_row(backlog_file: Path) -> tuple[bool, str]:
    """Clear stale audit residue when an anchor's findings drop to zero:
    the audit-owned `- **C…**` bullets in `{slug} Chores.md` (F332 — the
    file itself is deleted when no hand-added chores remain), plus any
    legacy singleton `B-QFix` row still in the backlog. Returns
    (changed, msg).
    """
    cleared: list[str] = []
    chores_file = chores_path_for(backlog_file)
    if chores_file.exists():
        try:
            old = chores_file.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            old = []
        if any(re.match(r"- \*\*C\d+\*\*", l) for l in old):
            # Drop the audit-owned bullets and KEEP the file, even when nothing
            # hand-added remains.  This used to unlink an emptied Chores.md,
            # which DAS Chores permits ("empty or absent"), but Dan asked
            # 2026-08-18 that the file stay put: an anchor's facet instance
            # that deletes itself the moment it empties cannot be found by
            # someone looking for it, and the disappearance reads as damage.
            # Observed twice the same day on TINK -- restoring the file by
            # hand did not hold, because deletion fires on the
            # C-bullets-to-zero transition rather than on emptiness, so the
            # next chore that landed and was fixed removed it again.
            kept = [l for l in old if not re.match(r"- \*\*C\d+\*\*", l)]
            while kept and not kept[-1].strip():
                kept.pop()
            chores_file.write_text("\n".join(kept) + "\n", encoding="utf-8")
            _selffire(chores_file)
            cleared.append("stale audit chores")
    try:
        text = backlog_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return bool(cleared), (
            "cleared " + ", ".join(cleared) if cleared
            else f"couldn't read {backlog_file.name}")
    lines = text.splitlines()
    qfix_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("- **B-QFix"):
            qfix_idx = i
            break
    if qfix_idx is None:
        return bool(cleared), (
            "cleared " + ", ".join(cleared) if cleared
            else "no QFix residue to clear")
    end = qfix_idx + 1
    while end < len(lines):
        stripped = lines[end]
        if stripped.startswith("  - "):
            end += 1
            continue
        if not stripped.strip() and end + 1 < len(lines) \
                and lines[end + 1].startswith("  - "):
            end += 1
            continue
        break
    del lines[qfix_idx:end]
    while qfix_idx < len(lines) and not lines[qfix_idx].strip():
        del lines[qfix_idx]
        if qfix_idx > 0 and not lines[qfix_idx - 1].strip():
            break
    backlog_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    _selffire(backlog_file)
    cleared.append("legacy B-QFix row")
    return True, "cleared " + ", ".join(cleared)


def route_findings_to_qfix(
    findings: list[Finding], anchor_backlogs: dict[str, Path]
) -> list[str]:
    """For each non-mechanically-fixable finding, file it as a sub-bullet on
    the owning anchor's `B-QFix` `[Ready]` row. Mechanically-fixable findings
    are excluded (they've already been auto-fixed in this run; they won't
    survive to the next audit pass).

    Per audit § Governing principle (2026-06-04): every residual the script
    can't fix gets routed to an anchor-local backlog row where the owning
    Pilot's next /ask or /groom drives it to zero under the 100%-fix rule.

    When residual findings for an anchor drop to zero, the stale B-QFix row
    is deleted so the anchor's banner reflects the current state.

    Returns a per-anchor log of routing actions."""
    residual = [f for f in findings if not f.mechanically_fixable]
    # Build per-anchor groups; every anchor in scope gets an entry (possibly
    # empty) so anchors whose residual dropped to zero get their stale QFix
    # cleared rather than left to inflate the banner.
    groups: dict[str, list[Finding]] = {a: [] for a in anchor_backlogs}
    for f in residual:
        owner = _resolve_owning_anchor(f.surface_file, anchor_backlogs)
        if owner is None:
            continue
        groups[owner].append(f)
    log: list[str] = []
    for anchor in sorted(groups):
        backlog_file = anchor_backlogs[anchor]
        if groups[anchor]:
            changed, msg = file_qfix_row(backlog_file, anchor, groups[anchor])
        else:
            changed, msg = clear_qfix_row(backlog_file)
        if changed:
            log.append(f"  {anchor}: {msg}")
    return log


def report_stale_qfix_rows(
    findings: list[Finding], anchor_backlogs: dict[str, Path]
) -> list[str]:
    """Read-only counterpart to `route_findings_to_qfix` (TINK T144).

    `--fix` reconciles the B-QFix row correctly: an anchor whose residuals drop
    to zero takes the `clear_qfix_row` branch. The gap was never the reconcile,
    it was the TRIGGER — most findings are fixed by editing the offending docs,
    which runs nothing, so the row survives `[Ready]` until the anchor's next
    `state` mutation. In between, the banner reports Ready work that does not
    exist, which is exactly what the crank hard-continuation rule keys on.

    A read-only pass must not mutate a backlog, so this reports rather than
    clears. Naming the stale row is enough: `--fix` is one command away and the
    agent now knows to run it.
    """
    residual = [f for f in findings if not f.mechanically_fixable]
    owners = {
        _resolve_owning_anchor(f.surface_file, anchor_backlogs) for f in residual
    }
    log: list[str] = []
    for anchor in sorted(anchor_backlogs):
        if anchor in owners:
            continue
        backlog_file = anchor_backlogs[anchor]
        try:
            lines = backlog_file.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        if any(ln.lstrip().startswith("- **B-QFix") for ln in lines):
            log.append(
                f"  {anchor}: stale B-QFix row — 0 residuals reproduce, but the "
                f"row is still [Ready] and inflating the banner. Re-run with "
                f"--fix to clear it."
            )
        # F332 — same staleness check against the chores file's audit bullets.
        chores_file = chores_path_for(backlog_file)
        if chores_file.exists():
            try:
                chores_lines = chores_file.read_text(
                    encoding="utf-8").splitlines()
            except OSError:
                continue
            if any(re.match(r"- \*\*C\d+\*\*", l) for l in chores_lines):
                log.append(
                    f"  {anchor}: stale audit chores — 0 residuals reproduce, "
                    f"but {chores_file.name} still carries `- **C…**` bullets. "
                    f"Re-run with --fix to clear them."
                )
    return log


def _find_or_create_h2(lines: list[str], h2_name: str) -> int:
    """Return index of `## <h2_name>` line; append (and return new index) if absent.
    Skips fenced example headings (F251 #3) so a placement move never targets a
    `## H2` sitting inside a code block."""
    target = f"## {h2_name}"
    fenced = _fenced_line_indices(lines)
    for i, line in enumerate(lines):
        if i in fenced:
            continue
        if line.strip() == target:
            return i
    # Append at end with leading blank-separation
    if lines and lines[-1] != "":
        lines.append("")
    lines.append(target)
    lines.append("")
    return len(lines) - 2


def apply_placement_fixes(
    backlog_file: Path,
    entries: list[BacklogEntry],
    today: date,
) -> list[str]:
    """F089 — apply C13/C14/C15/C16/C18 mechanical moves on this backlog.

    Conservative: only moves rows whose bracket has an unambiguous canonical
    target H2 (pure-state Watching/Waiting/Blocked → Later; Verify-by expired
    → Done). Ambiguous cases (Questions/Designing/Verify in wrong H2) are
    flagged by the C13/C14 checks but NOT moved here — /groom handles those
    with body-reading judgment.
    """
    # Decide moves
    moves: list[tuple[BacklogEntry, str]] = []  # (entry, target_h2_name)
    for e in entries:
        s = e.status.strip()
        # C18 first — Verify-by expired wins over any other classification
        if _is_verify_by_expired(s, today):
            if e.horizon != "Done":
                moves.append((e, "Done"))
            continue
        # C15/C16 — pure-state park brackets in wrong horizon
        if _is_pure_state_park_bracket(s):
            target_h2 = _park_bracket_target_h2(s)
            if e.horizon != target_h2:
                moves.append((e, target_h2))
            continue
    if not moves:
        return []
    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    # Sort by source_line DESC so deletions don't shift earlier line numbers
    moves_sorted = sorted(moves, key=lambda x: x[0].source_line, reverse=True)
    # Extract each row block (the bullet line + any indented sub-bullets + 1 blank)
    extracted: list[tuple[str, str, str]] = []  # (target_h2, block_text, identifier)
    for entry, target in moves_sorted:
        idx = entry.source_line - 1
        if idx >= len(lines):
            continue
        # Same span rule as apply_c4_fix — a blank line does NOT end a row
        # (T080: C15/C16 parking a two-Q row left Q2 behind under its old H2).
        content_end, delete_end = _row_block_span(lines, idx)
        row_lines: list[str] = lines[idx:content_end]
        del lines[idx:delete_end]
        extracted.append((target, "\n".join(row_lines).rstrip("\n"), entry.identifier))
    # Group by target H2
    by_target: dict[str, list[tuple[str, str]]] = {}
    for target, block, identifier in extracted:
        by_target.setdefault(target, []).append((block, identifier))
    log: list[str] = []
    # For each target H2, find or create, insert rows at top
    for target_h2_name, row_blocks in by_target.items():
        h2_idx = _find_or_create_h2(lines, target_h2_name)
        insert_at = h2_idx + 1
        # Skip one blank line below the H2 header if present
        while insert_at < len(lines) and lines[insert_at] == "":
            insert_at += 1
        # row_blocks are in source-line-descending order; insert each at insert_at
        # (so the relative ordering within the target H2 ends up matching the
        # original source order from bottom-up, which after multiple inserts at
        # the same position yields top-of-section in original-order).
        for row_block, identifier in row_blocks:
            block_lines = row_block.split("\n")
            for offset, row_line in enumerate(block_lines):
                lines.insert(insert_at + offset, row_line)
            # Trailing blank for separation
            lines.insert(insert_at + len(block_lines), "")
            log.append(f"  moved to ## {target_h2_name}: {block_lines[0][:80]}")
    new_text = "\n".join(lines)
    if not new_text.endswith("\n"):
        new_text += "\n"
    backlog_file.write_text(new_text, encoding="utf-8")
    _selffire(backlog_file)
    return log


# ============================================================
# D1 — Banner derivation
# ============================================================


def classify_backlog(path: Path) -> tuple[str, Optional[str]]:
    """F287 — classify one `* Backlog.md`. Returns `(verdict, reason)`.

    Verdict is one of:
      "render"       — an anchor that opted into queue tracking; reaches Q.md.
      "exclude"      — opted in, but deliberately suppressed; `reason` says why.
      "malformed"    — opted in, but the file does not parse as a backlog.
      "unclassified" — never opted in. Used to be a bare `continue`; C52 now
                       reports it.

    **The opt-in is the signal** (Q1, Dan 2026-07-30). Creating
    `{slug} Track/{slug} Backlog.md` IS the act of opting into queue tracking —
    the structure is the declaration of intent, not a hint that correlates with
    one. So the parent folder must be exactly `{slug} Track` (or the legacy
    `{slug} Plan`) for the SAME slug the backlog names.

    That strictness is what makes the taxonomy small. The looser predicate this
    replaces — any folder whose name merely *ended* in `Track`/`Plan` — is the
    mechanism that erased Disk's twelve rows, and it forced four separate
    hand-maintained exclusions to keep non-queues out. Measured against the
    live vault, the strict form loses none of the 30 rendered anchors and
    dissolves 6 of those 8 exclusions on its own: the corpus fixtures sit under
    `fixture/`, the backlog facet spec under `facets/`, the EXP sub-skill under
    `docs/` — none of which is a `{slug} Track`. It also retires the F107
    depth rule and the hardcoded `SUBPROJECT_QUEUES` allowlist entirely, since
    warden and muse now render because they hold `Warden Track/Warden
    Backlog.md`, not because someone remembered to add them to a set. That
    allowlist is what had to be hand-edited to rescue MUSE under F284.

    One suppression survives, and it is a real judgment rather than a
    structural fact: `examples/` holds DAS's shipped example anchors, which
    genuinely opt in and are genuinely complete, but are documentation and do
    not belong in the user's queue.
    """
    parts = path.parts
    if any(frag in parts for frag in EXCLUDED_PATH_FRAGMENTS):
        return "exclude", "path-fragment"
    slug = path.stem[:-len(" Backlog")]
    # F329 — the folder-doc form (`{slug} Track/{slug} Backlog/{slug}
    # Backlog.md`) opts in exactly like the flat form; the parent to test is
    # then one level up. Same recognizer as backlog_track_dir.
    opt_in_parent = path.parent
    if opt_in_parent.name == path.stem:
        opt_in_parent = opt_in_parent.parent
    if opt_in_parent.name not in (f"{slug} Track", f"{slug} Plan"):
        # Never opted in. Most such files are obviously not queues; naming why
        # keeps C52 quiet about them, so the complaint stays meaningful. These
        # reasons gate only the COMPLAINT, never the render — a wrong entry
        # here costs a missing warning, not an invisible anchor.
        if "Warden Corpus" in parts and "fixture" in parts:
            return "not-a-queue", "fixture"
        if path.parent.name == "facets":
            return "not-a-queue", "facet-spec"
        if "Skill Agent" in parts:
            return "not-a-queue", "sub-skill"
        return "unclassified", None
    # Opted in — so it renders, full stop. There is deliberately NO suppression
    # list here (Dan 2026-07-30). "It's documentation" is not a basis: a backlog
    # just means there is stuff to do, and plenty of documentation anchors carry
    # real ones (ABIO; DCP is a paper with a genuine work queue). The DAS example
    # anchors under `examples/` opted in like anything else and render like
    # anything else.
    #
    # The real concern behind such an exception — content that is stale or no
    # longer active — is a different and more general feature: ANY backlog might
    # want to declare itself or some of its rows inactive. That belongs in a
    # masking mechanism every anchor can reach, not a two-folder carve-out here.
    # Until it exists, HBR's and CSE's illustrative rows do appear in Q.md,
    # which is the honest failure direction: visible-and-wrong beats hidden.
    bad = _backlog_structure_fault(path)
    if bad:
        return "malformed", bad
    return "render", None


def _backlog_structure_fault(path: Path) -> Optional[str]:
    """Confirm an opted-in file really is a backlog. Returns a fault, or None.

    Per Dan 2026-07-30: glob for the signal, then verify — and say something
    when the verification fails rather than dropping the file. Near-free, since
    the file is opened and parsed for rows anyway.

    Deliberately narrow. It flags a file with no H1, and a file carrying rows
    that sit under no recognised horizon (those rows render nowhere, which is
    the F284 failure one level down). It stays SILENT on a freshly scaffolded
    empty backlog — H1, no horizons, no rows — because that is a legitimate
    state, not breakage: `derive_anchor_banner` already returns None for an
    anchor with no items, so an empty queue was never rendering anything to
    lose. SVW is in exactly that state today, and complaining about it would
    be the noise that trains you to skim past C52.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"unreadable ({exc.__class__.__name__})"
    has_h1 = False
    has_horizon = False
    rows = 0
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            level, title = len(m.group(1)), m.group(2).strip()
            if level == 1:
                has_h1 = True
            elif level == 2 and title in ALL_KNOWN_H2S:
                has_horizon = True
        elif ROW_OPENER_RE.match(line):
            rows += 1
    if not has_h1:
        return "no H1"
    if rows and not has_horizon:
        return f"{rows} row(s) under no recognised horizon H2"
    return None


def backlog_track_dir(backlog_path: Path) -> Path:
    """The `{slug} Track/` (or `Plan/`) directory a backlog belongs to.

    F329 — the backlog may be folder-doc form (`{slug} Track/{slug} Backlog/
    {slug} Backlog.md`, the folder holding the T-docs); the Track dir is then
    one level further up. Mirrors `backlog_edit.anchor_track_dir` — the two
    scripts cannot import each other, so the recognizer (stem == parent name)
    is carried in both with a pointer here.
    """
    parent = backlog_path.parent
    if parent.name == backlog_path.stem:
        return parent.parent
    return parent


def find_anchor_backlogs(vault_root: Path) -> dict[str, Path]:
    """Find every {slug} Backlog.md in the vault. Return name → path.

    Membership is decided by `classify_backlog` (F287) — this returns exactly
    the files it verdicts "render". Everything else is either excluded for a
    named reason or reported by C52; nothing is dropped silently.
    """
    out: dict[str, Path] = {}
    for path in vault_root.rglob("* Backlog.md"):
        if classify_backlog(path)[0] == "render":
            out[path.stem.replace(" Backlog", "")] = path
    return out


def check_c52_unclassified_backlog(vault_root: Path) -> list[Finding]:
    """C52 (F287) — every `* Backlog.md` must render or carry a named reason.

    This is F284's totality argument one level up. F284 made the render total
    over the ROWS inside an anchor: no bracket is silently discarded, every
    frontier row reaches the queue file or trips a coverage assertion. The set
    of ANCHORS was still chosen by a folder-name heuristic whose non-matches
    vanished without a trace, so an anchor could go missing whole — which is
    precisely how Disk's twelve drive-consolidation rows were lost.

    The finding fires when a backlog file matches neither the render test nor
    any declared exclusion. Today that residue is empty, which is what makes
    the rule adoptable now: like F281's anchor-name rule at two violations, a
    property that is currently true is cheap to lock in, and enforceable rules
    that start clean stay clean.

    Not mechanically fixable, deliberately. The remedy is a judgement call —
    either the file belongs to a real anchor and wants moving under `Plan/`
    or `Track/`, or it is a new kind of non-queue and wants a named exclusion
    in `classify_backlog`. Auto-picking either one would re-hide the thing the
    check exists to surface.
    """
    findings: list[Finding] = []
    for path in sorted(vault_root.rglob("* Backlog.md")):
        verdict, reason = classify_backlog(path)
        if verdict not in ("unclassified", "malformed"):
            continue
        rel = path.relative_to(vault_root)
        slug = path.stem[:-len(" Backlog")]
        if verdict == "unclassified":
            msg = (
                f"backlog never opted in: {rel} — its parent folder is "
                f"`{path.parent.name}/`, not `{slug} Track/`, so it renders "
                f"nowhere. If this is {slug}'s queue, move it to "
                f"`{slug} Track/{slug} Backlog.md` — that placement IS the "
                f"opt-in. If it is not a queue, it should not be named "
                f"`{path.name}` (F287)"
            )
        else:
            horizons = ", ".join(sorted(LIVE_HORIZON_H2S))
            msg = (
                f"opted in but does not parse as a backlog: {rel} — it sits in "
                f"`{slug} Track/`, which declares it a queue, but {reason}. "
                f"Recognised horizons: {horizons}. Either give it the structure "
                f"of a backlog, or move it out of `{slug} Track/` so the name "
                f"stops claiming to be one (F287)"
            )
        findings.append(Finding(
            severity="error",
            surface_file=path,
            surface_line=1,
            code="C52",
            message=msg,
            mechanically_fixable=False,
        ))
    return findings


# ============================================================
# F305 visibility classes — THE canonical definition
# ============================================================
# These live here, in the lower module, because `queries-render.py` already
# imports `audit_q` (LIVE_HORIZON_H2S and friends) and the reverse would be
# circular. Before F305 each file carried its own copy of the class logic AND
# its own copy of the banner format string, with `queries-render.py:331`
# admitting the arrangement in a comment — *"Banner derivation (mirrors
# audit_q.derive_anchor_banner)"*. A mirror is not a design; the two drifted in
# exactly the way F305 exists to describe, and the drift was invisible because
# each file was self-consistent.
#
# A bracket is a SET: `[Ready, Questions]` is legal and puts its row in BOTH
# classes, so class counts may sum to more than the row count. That is intended
# — see [[DAS Backlog]] § The state table. Membership is tested on each MEMBER,
# never on the whole bracket string, so a date argument can never collide with
# a class name.

def bracket_members(bracket: str) -> list[str]:
    """Split a bracket into its member states. `Ready, 3 Questions` -> both."""
    return [m.strip() for m in bracket.split(",") if m.strip()]


def has_member(bracket: str, *names: str) -> bool:
    """True if the bracket SET contains any of `names` as a member.

    Use this anywhere the old code wrote `e.status == "Designing"` or
    `e.status.startswith("Verify")`. A whole-string compare is correct only
    while every bracket is a single state; the moment a row is written
    `[Ready, Questions]` the compare silently returns False and the check
    SKIPS the row rather than failing loudly. That is the worst shape a guard
    can take — it reports success by saying nothing.

    Matching is exact per member, except that a member may carry an argument
    (`Blocked F237`, `Waiting 2026-09-01`, `3 Questions`), so the member's
    KEYWORD is compared: leading count, then the first word.
    """
    for m in bracket_members(bracket):
        # `3 Questions` -> `Questions`; `Blocked F237` -> `Blocked`;
        # `Verify-by 2026-09-01` -> `Verify-by`.
        w = m.split(None, 1)
        kw = w[1] if len(w) == 2 and w[0].isdigit() else m.split(None, 1)[0]
        if kw in names or m in names:
            return True
    return False


_QUESTIONS_MEMBER_RE = re.compile(r"^\s*(\d+)?\s*Questions?\s*$", re.IGNORECASE)


def questions_member(bracket: str):
    """The `[Questions]` / `[N Questions]` member of a bracket set, as
    `(member_text, claimed_count_or_None)` — or None when absent.

    Replaces five copies of `re.match(r"^\\s*(\\d+)\\s+Questions?\\s*$", status)`,
    each of which anchored on the WHOLE bracket and so would stop seeing the
    row the moment it became a set."""
    for m in bracket_members(bracket or ""):
        hit = _QUESTIONS_MEMBER_RE.match(m)
        if hit:
            return m, (int(hit.group(1)) if hit.group(1) else None)
    return None


def in_class_ready(bracket: str) -> bool:
    """Class Ready — the agent acts next. `Agreed`/`Implementing` are aliases."""
    return any(m in ("Ready", "Agreed", "Active", "Implementing")
               for m in bracket_members(bracket))


def in_class_user(bracket: str) -> bool:
    """Class User — the user is blocking. `[N Questions]` matched by containment."""
    return any(m in ("User", "Designing") or "Questions" in m
               for m in bracket_members(bracket))


def in_class_parked(bracket: str) -> bool:
    """Class Parked — nothing blocked, but nothing undoes it either."""
    return any((m.startswith("Verify") and not _VERIFY_BY_BRACKET_RE.match(m))
               or m.startswith("Blocked")
               for m in bracket_members(bracket))


def in_class_hidden(bracket: str) -> bool:
    """Class Hidden — parked AND self-unwinding. The undo-itself test.

    `[Verify-by {date}]` lands HERE, not in Parked, and the test is what puts
    it here: `sweep_stale_brackets` auto-Dones the row when the date arrives,
    so it leaves its own state with nobody acting — which is the definition of
    Hidden and exactly why F283 renders it nowhere. Classing it Parked made it
    the one row in the vault that was counted in a class promising visibility
    while rendering in no list. [[DAS Backlog]] already says as much in prose:
    the form is *"a `[Waiting]` whose outcome happens to be a Verify"*. The
    bracket is retired; it is classed correctly for as long as rows carry it."""
    return any(m.startswith("Waiting") or m.startswith("Watching")
               or _VERIFY_BY_BRACKET_RE.match(m)
               for m in bracket_members(bracket))


_VERIFY_BY_BRACKET_RE = re.compile(r"^Verify-by\s+\d{4}-\d{2}-\d{2}", re.I)


def renders_in_body(horizon: str, bracket: str) -> bool:
    """True if a row is listed in the rendered `{slug} queries.md` body.

    THIS IS THE SCOPE FOR ZONE 1. The banner counts what the body lists, so
    the two cannot disagree; deriving zone 1 from a horizon set instead is
    what produced the MUX 2026-06-04 defect (banner `Questions 0` while the
    body listed two rows under `## Later`). That fix was written as a widened
    constant which was then aliased straight back to the narrow one, so the
    comment promised the wide scope while the code kept the narrow — and two
    live rows (Anchorage F029, Docket F054) were still rendered-but-uncounted
    when F305 measured it on 2026-08-07.

    THE BODY IS THE ACTIVE HORIZONS. `## Later` renders nothing, whatever its
    bracket. Restored 2026-08-19 on Dan's direction; the design always said so
    and the code had drifted off it in three steps, which is worth recording
    because each step looked local and correct:

    1. **2026-06-02, primary-sourced** — user direction, carried in this
       function's ancestor as a comment: *"only count from ACTIVE horizons.
       Rows parked in ## Later or ## Verify are passive observation, not
       active questions."*
    2. **2026-06-04, MUX** — banner said `Questions 0` while the body listed
       two `## Later` rows. Two repairs were available: narrow the BODY to
       match the banner, or widen the BANNER to match the body. F305 took the
       second and DELETED the 2026-06-02 direction in the same commit
       (c9980485), so the disagreement was resolved against the design.
    3. **Afterwards** — `Blocked` was admitted on the "37 rows vanishing"
       evidence (7771917d), and a quote attributed to Dan 2026-08-07 —
       *"Ready, User and Parked are all shown"* — was added by a later commit
       (dbd4eabb) to justify the branch. That quote has NO primary source
       anywhere in the vault: it occurs only here and in documents citing
       this comment. It also enumerates BANNER ZONE LABELS (zone 1's Ready /
       User, zone 3's Parked / Waiting), so even at face value it rules on
       what the banner COUNTS, not on what the body RENDERS.

    The design, in three places that all agree: [[DAS Query]] § the banner —
    *"Zone 1 is scoped to the active horizons (## Now, ## Next)"*; F284
    § Scope note — *"Later and Icebox are deliberately out of scope… a total
    render over every horizon would bury the frontier it exists to surface"*;
    and this repo's own zone-3 comment in `queries-render.py` — Parked and
    Waiting are counted *"precisely BECAUSE they are omitted from the body."*

    NOTHING VANISHES, and that is what makes this safe. The 37-rows-vanishing
    finding is real, but its answer is zone 3, not a body listing: `parked_n`
    and `waiting_n` are computed from every live row unscoped by horizon, so a
    `[Blocked …]` row parked in Later still lands in `Parked N`, and zone 2
    counts it again in `Later N`. Measured at the restore: 86 rows across 11
    backlogs left the body (72 `Blocked`, 14 `Questions`); every one is still
    on its banner twice."""
    if bracket.startswith("Done"):
        return False
    # `[Verify-by <date>]` renders NOWHERE (F283): the bracket promises nothing
    # happens until the date and `sweep_stale_brackets` auto-Dones it on
    # arrival, so it is set-and-forget by construction.
    if _VERIFY_BY_BRACKET_RE.match(bracket):
        return False
    if horizon == "Later":
        # `## Later` renders NOTHING. Parking a row is a statement that nobody
        # is acting on it, and the body is the act-on-it surface.
        #
        # Three brackets used to be admitted here (`Questions`, `Verify*`,
        # `Blocked …`) and the docstring above records how each arrived. The
        # short version: none of them was a decision to widen the body — the
        # first two came from resolving a banner/body DISAGREEMENT in the
        # banner's favour, and the third from a real vanishing-rows finding
        # whose actual answer is zone 3.
        #
        # Two arguments that read as objections and are not:
        #
        # - *"F283's ledger loses 37 `[Blocked …]` rows."* It does not. Zone 3
        #   counts `Parked` across every live horizon, and its own comment in
        #   `queries-render.py` says it is counted "precisely BECAUSE they are
        #   omitted from the body." Zone 2 counts the row again under
        #   `Later N`. A parked blocker is on the banner twice and in the
        #   backlog file; it is deferred, not disappeared.
        # - *"A `[User]` row parked in Later is hidden from the only person who
        #   can act on it"* (T157/T158). True, and it stays true — but that is
        #   the POINT of `[User]` + `## Later`, which is the vault's only way
        #   to say "the user owns this AND the user has deferred it." SKA F271
        #   is the live proof: its Status reads "two Dan actions and his
        #   judgment call" while its row reads "do not surface it until he
        #   opens it." Widening the body overrides that instruction silently.
        #
        # If a parked row should be acted on, PROMOTE ITS HORIZON. [[DAS Query]]
        # says this in as many words: "the fix is to promote its horizon, not
        # to widen zone 1 — widening zone 1 would put work in the *act on it*
        # zone that the backlog has explicitly deferred, which is the reverse
        # of the reading order the whole layout exists to produce."
        return False
    return horizon in ("Active", "Ready", "Now", "Next", "Verify")


# ============================================================
# T131 leg 2 — the Inbox awareness signal.
#
# WHY THIS DOES NOT READ `R-fct-inbox-02`, and is therefore not blocked on it.
#
# `-02` says every Inbox H2 carries a backtick-wrapped status tag. `state drop`
# writes PENDING entries with no tag — absence of a tag IS the pending signal —
# so on its face every pending entry violates `-02`, and a counter written as
# "H2s lacking a tag" would be built on the exact sentence in dispute.
#
# It is worth saying that `-02` is also already in tension with its own
# ruleset: `R-fct-inbox-04` says processed entries "only gain a status tag",
# which presupposes the untagged pending state `-02`'s check pattern forbids.
# That inconsistency is SKA's to resolve — this module does not touch it, and
# does not need it resolved.
#
# The counter instead reads `R-fct-inbox-03`, which is NOT in dispute and which
# ATT F045 correctly said needs no vocabulary change: the sanctioned tags are
# `DONE` and `MOVED → {destination}`, and no others may be used without
# updating the spec. So PROCESSED is defined positively, against the
# vocabulary, and PENDING is everything else:
#
#     an entry is PROCESSED iff its section carries a sanctioned tag
#     Inbox N = the dated entries that do not
#
# That test is indifferent to WHERE the tag sits — H2 line, attribution line,
# sub-bullet — so however SKA settles `-02`'s placement-and-presence question,
# this count stays correct without an edit here. It asserts neither that an H2
# must carry a tag nor that it must not.
# ============================================================

_INBOX_ENTRY_RE = re.compile(r"^## \d{4}-\d{2}-\d{2} — .+")
# R-fct-inbox-03's two sanctioned values, backtick-wrapped as the rule spells
# them. Backticks are required: without them the word `DONE` in an entry's
# prose would mark it processed.
_INBOX_DONE_RE = re.compile(r"`(?:DONE|MOVED\s*→[^`]*)`")


def count_pending_inbox(name: str, backlog_file: Path) -> int:
    """Pending (untagged) entries in `{name} Inbox.md`, or 0 if there is none.

    The file prefix comes off the BACKLOG FILENAME, not the `.anchor` slug —
    the same decision `state drop` made in leg 1, because `Scout Backlog.md`
    beside `slug: SCOUT` would otherwise put the count and the file in two
    different Track folders and the banner would read 0 forever.
    """
    inbox = backlog_track_dir(backlog_file) / f"{name} Inbox.md"
    if not inbox.is_file():
        return 0
    try:
        lines = inbox.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return 0
    pending = 0
    open_entry = False
    for line in lines:
        if line.startswith("## "):
            # A new H2 closes the previous entry; if nothing in it carried a
            # sanctioned tag, that entry was pending.
            if open_entry:
                pending += 1
            open_entry = bool(_INBOX_ENTRY_RE.match(line))
            if open_entry and _INBOX_DONE_RE.search(line):
                open_entry = False
            continue
        if open_entry and _INBOX_DONE_RE.search(line):
            open_entry = False
    if open_entry:
        pending += 1
    return pending


def format_status_banner(tag: str, slug_label: str, ready: int, user: int,
                         now: int, nxt: int, later: int,
                         parked: int, waiting: int, icebox: int,
                         suffix: str = "", inbox: int = 0) -> str:
    """THE status-banner format string. `R-query-16` locks this exact spacing
    and must move in the same pass as any edit here — it has lagged once
    already (F260), failing on 26 of 32 live pages while the renderer was
    correct.

    Three zones ordered by ATTENTION, not by kind: what do I act on | what is
    coming | what am I not looking at. Zone 3 deliberately mixes a horizon
    (Icebox) in with two classes; regularizing that destroys the design.

    `Inbox N` (T131 leg 2) joins ZONE 1, beside Ready and User, because an
    undrained inbox entry is something to act on and the zone is chosen by
    attention rather than by kind. It is emitted ONLY WHEN N > 0 — the same
    show-only-when-nonzero discipline Dan set for the trailing `{N}` residual
    count on 2026-06-04: *the signal is noise-only-when-there's-noise.* That
    is not merely tidiness here. It keeps all 35 live banners byte-identical
    on a vault with nothing pending, so nothing re-renders, no page sits in a
    failing interval, and `R-query-16` does not have to catch up to a form
    that changed under every file at once — which is exactly how that lock
    lagged for the whole F260 interval and failed on 26 of 32 correct pages.
    `R-query-16` and [[DAS Query]] § Spacing move WITH this string, in the
    same pass, and admit the field as optional."""
    inbox_txt = f"    Inbox {inbox}" if inbox else ""
    return (
        f"# [{tag}]  {slug_label}  -  "
        f"Ready {ready}    User {user}{inbox_txt}   |   "
        f"Now {now}    Next {nxt}    Later {later}   |   "
        f"Parked {parked}    Waiting {waiting}    Icebox {icebox}"
        f"{suffix}"
    )


def derive_anchor_banner(name: str, backlog_file: Path,
                         vault_index: dict[str, list[Path]]) -> Optional[str]:
    """Return the H1 banner line for an anchor's Q.md section.

    Returns None if the anchor has no items in any active horizon (TAG `[]`)."""
    entries = backlog_entries(backlog_file, vault_index)
    if not entries:
        return None
    # Filter out [Done]-bracketed rows from active horizons (stale; C4 may not
    # have run yet, but we don't want them counted toward live state).
    live = [e for e in entries
            if e.horizon in LIVE_HORIZON_H2S
            and not e.status.startswith("Done")]
    # Zone 1 — class counts, scoped to WHAT THE BODY RENDERS (`renders_in_body`).
    # Rows parked in ## Later are mostly passive observation and stay out, per
    # user direction 2026-06-02 after a MUX banner showed "Questions 13" with
    # Now/Next at 0 — but the `[Questions]` and `[Verify]` rows under Later ARE
    # listed in the body, so they must count here too or banner and body
    # disagree. Sharing the predicate is what makes them agree by construction.
    actionable = [e for e in live if renders_in_body(e.horizon, e.status)]
    # F305 — EVERY COUNT IS A COUNT OF ROWS, including User. Dan, 2026-08-07:
    # *"if I have 10 items that each have one question, I'm much more motivated
    # to answer a bunch of questions since I'm going to unblock a tremendous
    # amount of work. If I had one ticket that had 10 questions, I'm not really
    # very motivated."* The number that drives action is how many things are
    # blocked on the user, not how much answering work is queued.
    #
    # This retired a substantial machine: the old count resolved each row's
    # arrow-link, opened the target feature doc, and summed its pending
    # `Q<n>` entries (with a floor of 1 for an unresolvable link). All of that
    # existed to produce a number Dan does not index off. `extract_q_entries`
    # is still the authority for the per-feature `**(nQ)**` counts inside the
    # rendered body — it just no longer feeds the banner.
    ready_n = sum(1 for e in actionable if in_class_ready(e.status))
    user_n = sum(1 for e in actionable if in_class_user(e.status))
    verify_n = sum(1 for e in actionable if in_class_parked(e.status))
    # Zone 3 — the quiet classes, unscoped by horizon. Counted precisely
    # BECAUSE they are omitted from the rendered body: a class that appears in
    # no list and no count is invisible everywhere but the raw backlog file.
    parked_n = sum(1 for e in live if in_class_parked(e.status))
    waiting_n = sum(1 for e in live if in_class_hidden(e.status))
    # Per-horizon counts (every entry, even with [Done] would count toward Now
    # in original spec, but C4 will move them out; here we count live only).
    horizon_counts = {h: 0 for h in ("Active", "Ready", "Now", "Next", "Later", "Verify", "Icebox")}
    for e in entries:  # all entries including potentially-stale-Done
        if e.horizon in horizon_counts and not e.status.startswith("Done"):
            horizon_counts[e.horizon] += 1
    # Icebox count: from {slug} Icebox.md if it exists
    icebox_file = backlog_track_dir(backlog_file) / f"{name} Icebox.md"
    if icebox_file.is_file():
        try:
            icebox_text = icebox_file.read_text(encoding="utf-8")
            horizon_counts["Icebox"] = sum(
                1 for line in icebox_text.splitlines() if ROW_OPENER_RE.match(line)
            )
        except (OSError, UnicodeDecodeError):
            pass
    # TAG cascade
    has_u = user_n > 0 or verify_n > 0
    has_a = ready_n > 0
    has_g = (horizon_counts["Now"] > 0 or horizon_counts["Next"] > 0)
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
    else:
        tag = ""
    if not tag and horizon_counts["Icebox"] == 0:
        return None
    return format_status_banner(
        tag, f"[[{name} queries|{name}]]",
        ready_n, user_n,
        horizon_counts["Now"], horizon_counts["Next"], horizon_counts["Later"],
        parked_n, waiting_n, horizon_counts["Icebox"],
        inbox=count_pending_inbox(name, backlog_file),
    )


# ============================================================
# F180 — when:: action-triggered executable rules
# ============================================================


def _rulesets_roots() -> list[Path]:
    """Roots under the dans-anchor-system repo that hold rulesets (standalone catalog +
    facet/discipline-embedded RULESET blocks)."""
    base = Path(__file__).resolve().parents[3]  # …/dans-anchor-system
    return [base / "library" / "Rulesets", base / "facets", base / "disciplines"]


def _discover_when_rules() -> list[dict]:
    """Walk the ruleset roots for rules carrying a `when::` clause. Returns a list
    of {events, rule_id, source, code} — code is the rule's adjacent embedded
    ```python block (its trigger), or None."""
    out: list[dict] = []
    for root in _rulesets_roots():
        if not root.is_dir():
            continue
        for md in root.rglob("*.md"):
            try:
                lines = md.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            cur_rule: Optional[str] = None
            for i, ln in enumerate(lines):
                rm = re.match(r"^###\s+RULE\s+(R-[\w-]+)", ln)
                if rm:
                    cur_rule = rm.group(1)
                    continue
                wm = re.match(r"^when::\s*(.+?)\s*$", ln)
                if not wm:
                    continue
                events = [e.strip() for e in wm.group(1).split(",") if e.strip()]
                code: Optional[str] = None
                for j in range(i + 1, min(i + 80, len(lines))):
                    if re.match(r"^###\s+RULE", lines[j]):
                        break
                    if lines[j].strip().startswith("```python"):
                        buf = []
                        for k in range(j + 1, len(lines)):
                            if lines[k].strip().startswith("```"):
                                break
                            buf.append(lines[k])
                        code = "\n".join(buf)
                        break
                out.append({"events": events, "rule_id": cur_rule or "?",
                            "source": md, "code": code})
    return out


def list_when_rules() -> int:
    rules = _discover_when_rules()
    if not rules:
        print("audit-q: no when-triggered rules found.")
        return 0
    print(f"audit-q: {len(rules)} when-triggered rule(s):")
    for r in rules:
        tag = "py" if r["code"] else "no-code"
        print(f"  {r['rule_id']:26s} when:: {', '.join(r['events']):18s} "
              f"[{tag}]  {r['source'].name}")
    return 0


def _anchor_git_aspect(anchor: str) -> tuple[Optional[str], Optional[Path]]:
    """Resolve an anchor's Git aspect (PR / Push / Commit / NoGit) from its
    `.anchor` traits, walking up from its backlog. The Git aspect **inherits**:
    a sub-anchor that declares no aspect falls through to its parent, so the walk
    continues past intermediate `.anchor` markers until one declares an aspect
    (the nearest declaration wins). Returns (aspect, anchor_dir)."""
    bl = find_anchor_backlogs(VAULT_ROOT).get(anchor)
    if not bl:
        return None, None
    d = bl.parent
    for _ in range(12):
        a = d / ".anchor"
        if a.is_file():
            try:
                t = a.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                t = ""
            for asp in ("PR", "Push", "Commit", "NoGit"):
                if re.search(rf"(?im)^\s*-\s*{asp}\b", t):
                    return asp, d
            # this `.anchor` declares no Git aspect — inherit from the parent
        if d.parent == d:
            break
        d = d.parent
    return None, None


def _build_when_ctx(anchor: Optional[str]):
    """Build the `ctx` passed to a when-rule's trigger(): anchor name, Git aspect
    (from .anchor traits), anchor path, and the anchor's queries.md text."""
    git_aspect, anchor_path = (_anchor_git_aspect(anchor) if anchor else (None, None))
    queries_text = ""
    if anchor:
        bl = find_anchor_backlogs(VAULT_ROOT).get(anchor)
        if bl:
            qf = bl.parent / f"{anchor} queries.md"
            if qf.is_file():
                try:
                    queries_text = qf.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    queries_text = ""

    class Ctx:
        pass
    ctx = Ctx()
    ctx.anchor = anchor          # type: ignore[attr-defined]
    ctx.git_aspect = git_aspect  # type: ignore[attr-defined]
    ctx.anchor_path = anchor_path  # type: ignore[attr-defined]
    ctx.queries_text = queries_text  # type: ignore[attr-defined]
    return ctx


def _fire_when_rules(rules: list[dict], event: str, anchor: Optional[str]) -> int:
    """Run each rule's trigger(ctx) and print its agent-directed steer messages.
    Returns the number of messages emitted."""
    ctx = _build_when_ctx(anchor)
    fired = 0
    for r in rules:
        if not r["code"]:
            continue
        ns: dict = {}
        try:
            exec(r["code"], ns)  # rules are first-party content
            trig = ns.get("trigger")
            if not callable(trig):
                continue
            msgs = trig(ctx) or []
        except Exception as e:  # noqa: BLE001 — a bad rule shouldn't crash the run
            print(f"audit-q: when-rule {r['rule_id']} errored: {e}", file=sys.stderr)
            continue
        for m in (msgs if isinstance(msgs, list) else [msgs]):
            print(f"[when:{event}] {r['rule_id']}: {m}")
            fired += 1
    return fired


def run_when_rules(event: str, anchor: Optional[str]) -> int:
    """Explicit `--when EVENT`: fire all matching when-rules for one anchor."""
    rules = [r for r in _discover_when_rules() if event in r["events"]]
    if not rules:
        print(f"audit-q: no when-triggered rules for event '{event}'.")
        return 0
    if _fire_when_rules(rules, event, anchor) == 0:
        print(f"audit-q: {len(rules)} when-rule(s) matched '{event}'; "
              f"none emitted a message.")
    return 0


def autofire_audit_q(anchor: Optional[str],
                     anchor_backlogs: dict[str, Path]) -> None:
    """F180 — at the END of a normal audit-q run, automatically fire the
    `when:: skill:audit-q` rules (e.g. R-query-14 push/commit interception) for
    the audited anchor(s) — so they trigger without an explicit `--when` flag
    (this is what makes `/query` building a queries.md → audit-q run → steer).
    Single-anchor run fires for that anchor; vault-scope run fires for every
    anchor that has a queries.md."""
    rules = [r for r in _discover_when_rules()
             if "skill:audit-q" in r["events"] and r["code"]]
    if not rules:
        return
    if anchor:
        targets = [anchor]
    else:
        targets = [a for a, bl in anchor_backlogs.items()
                   if (bl.parent / f"{a} queries.md").is_file()]
    for a in targets:
        _fire_when_rules(rules, "skill:audit-q", a)


# ============================================================
# Main + CLI
# ============================================================


def main() -> int:
    desc = (__doc__ or "").split("\n")[0]
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--fix", action="store_true",
                        help="apply mechanical repairs to Q.md + backlogs")
    parser.add_argument("--dry", action="store_true",
                        help="report-only AND refuse to write anywhere")
    parser.add_argument(
        "--scope",
        choices=["q", "backlog", "feature-doc", "all"],
        default="q",
        help=(
            "Audit scope. Default `q` (reachability-limited from Q.md): "
            "audits Q.md + each anchor's backlog listed in Q.md + each feature "
            "doc linked from those backlogs. `backlog` audits one anchor's "
            "backlog + linked feature docs (requires --anchor). `feature-doc` "
            "audits one feature doc (requires --feature-doc). `all` is the "
            "vault-wide pre-2026-05-26 behavior — audits every F<n>.md in every "
            "Features/ folder regardless of reachability."
        ),
    )
    parser.add_argument("--anchor", type=str, default=None,
                        help="(scope=backlog) anchor name, e.g. 'SKA'")
    parser.add_argument("--feature-doc", type=str, default=None,
                        help="(scope=feature-doc) path to a feature doc")
    parser.add_argument("--when", metavar="EVENT", default=None,
                        help="[F180] fire WHEN-triggered rules for EVENT: discover "
                             "ruleset rules whose `when:: EVENT` clause matches, run "
                             "each rule's embedded trigger(ctx), and print its "
                             "agent-directed steer messages. EVENT is an action "
                             "name — `skill:<name>` (a skill executing, e.g. "
                             "`skill:audit-q`), `compact`, or `markdown-write`. "
                             "Use with --anchor to bind ctx to an anchor.")
    parser.add_argument("--list-when", action="store_true",
                        help="[F180] list discovered when-triggered rules (event + "
                             "rule id + source ruleset) without running them.")
    args = parser.parse_args()
    if args.list_when:
        return list_when_rules()
    if args.when is not None:
        return run_when_rules(args.when, args.anchor)
    if args.scope == "backlog" and not args.anchor:
        print("error: --scope backlog requires --anchor NAME", file=sys.stderr)
        return 2
    if args.scope == "feature-doc" and not args.feature_doc:
        print("error: --scope feature-doc requires --feature-doc PATH", file=sys.stderr)
        return 2
    if args.fix and args.dry:
        print("error: --fix and --dry are mutually exclusive", file=sys.stderr)
        return 2
    if not Q_MD.is_file():
        print(f"error: {Q_MD} not found", file=sys.stderr)
        return 2
    print(f"audit-q: building vault index from {VAULT_ROOT}...", file=sys.stderr)
    vault_index = build_vault_index(VAULT_ROOT)
    print(f"  vault index: {sum(len(v) for v in vault_index.values())} files, "
          f"{len(vault_index)} unique basenames", file=sys.stderr)
    findings: list[Finding] = []
    c4_fixes_applied: list[str] = []
    derived_banners: dict[str, str] = {}
    all_backlogs = find_anchor_backlogs(VAULT_ROOT)

    # Compute scoped backlog dict per --scope:
    if args.scope == "feature-doc":
        # Skip Q.md + backlog entirely; audit only the one feature doc.
        anchor_backlogs: dict[str, Path] = {}
    elif args.scope == "backlog":
        if args.anchor not in all_backlogs:
            print(f"error: anchor '{args.anchor}' has no backlog in {VAULT_ROOT}", file=sys.stderr)
            return 2
        anchor_backlogs = {args.anchor: all_backlogs[args.anchor]}
    else:
        # scope=q or scope=all → all anchor backlogs
        anchor_backlogs = all_backlogs

    # C1 + C2 on Q.md — only when auditing Q.md itself (scope=q or scope=all).
    if args.scope in ("q", "all"):
        qmd_links = links_in_file(Q_MD, vault_index)
        qmd_text = Q_MD.read_text(encoding="utf-8")
        findings.extend(check_c1_link_existence(qmd_links))
        findings.extend(check_c54_banner_label_matches_target(qmd_text))
        # C56 (F269) — against `all_backlogs`, never the scoped set: a section
        # is an orphan only if NO anchor renders it.
        findings.extend(check_c56_qmd_orphan_section(qmd_text, all_backlogs))
        findings.extend(check_c2_q_marker_existence(qmd_links, qmd_text))
        # C52 (F287) — vault-wide, so it runs with Q.md rather than per anchor:
        # an anchor that renders nowhere has no per-anchor pass to be found by.
        findings.extend(check_c52_unclassified_backlog(VAULT_ROOT))
    # C4 + D1 require walking each anchor's backlog (in the scoped set).
    for name, backlog_file in sorted(anchor_backlogs.items()):
        entries = backlog_entries(backlog_file, vault_index)
        findings.extend(check_c4_stale_done(entries))
        if args.fix:
            changed, fix_log = apply_c4_fix(backlog_file, entries)
            if changed:
                c4_fixes_applied.extend(f"  {name}: {msg}" for msg in fix_log)
        banner = derive_anchor_banner(name, backlog_file, vault_index)
        if banner:
            derived_banners[name] = banner
    # B16 — C6 / C8 / C9 / C10 walk feature docs + the anchor queries file per anchor.
    # Default (scope=q or scope=backlog): reachability-limited via backlog wiki-links.
    # `--scope all` gives the original vault-wide behavior.
    if args.scope == "feature-doc":
        # Audit just one feature doc.
        fd_path = Path(args.feature_doc).expanduser().resolve()
        if not fd_path.is_file():
            print(f"error: feature doc not found: {fd_path}", file=sys.stderr)
            return 2
        cid = feature_number(fd_path.stem, fd_path) or fd_path.stem
        ask_format_files = [(cid, fd_path)]
    else:
        reachable = args.scope != "all"
        ask_format_files = find_ask_format_files(
            anchor_backlogs, vault_index=vault_index, reachable_only=reachable
        )
    all_q_entries: list[QEntry] = []
    for container_id, file_path in ask_format_files:
        all_q_entries.extend(extract_q_entries(file_path, container_id))
    # `{slug} queries.md` Immediate Questions use the SAME standard expanded
    # format as feature-doc `## Open Questions` (option per own-line `**(A)**`
    # sub-bullet + a `- **Recommendation:**` line) — one format vault-wide
    # (user direction 2026-06-16). So the shared checks apply to queries.md too:
    # C6 block-IDs, C8 no-inline, C9 recommendation, C10 outdent, C19 option
    # bullets, C20 blank-after. (Verifications are `**V<n>` yes/no and aren't
    # Q-entries, so these don't touch them; queries-specific shape lives in
    # C37/C38/C39/C40.)
    findings.extend(check_c6_block_id_present(all_q_entries))
    findings.extend(check_c8_inline_alternatives(all_q_entries))
    findings.extend(check_c9_recommendation_present(all_q_entries))
    findings.extend(check_c10_recommendation_outdent(all_q_entries))
    findings.extend(check_c19_option_bullets(all_q_entries))
    findings.extend(check_c20_blank_after_recommendation(all_q_entries))
    findings.extend(check_c21_empty_open_questions(ask_format_files, all_q_entries))
    # C22 — link existence across feature docs + backlogs + queries.md files
    c22_scope: list[Path] = []
    c22_scope.extend(p for _, p in ask_format_files)
    c22_scope.extend(anchor_backlogs.values())
    for backlog_file in anchor_backlogs.values():
        queries_md = backlog_track_dir(backlog_file) / f"{backlog_file.stem.replace(' Backlog', ' queries')}.md"
        if queries_md.is_file():
            c22_scope.append(queries_md)
    # These three sources OVERLAP, and a scope that lists a file twice reports
    # each of its broken links twice. `find_ask_format_files` ends by appending
    # the backlog itself (row-scoped Qs live there), so every backlog arrives
    # here already in `ask_format_files` and is then added again above; it also
    # yields `{slug} queries.md`, which the loop re-adds. Duplicates are not
    # cosmetic — they inflate the finding count a caller uses to decide whether
    # the tree is clean, and they make one broken link look like two problems.
    c22_scope = _dedupe_paths(c22_scope)
    findings.extend(check_c22_link_existence_extended(c22_scope, vault_index))
    # C53 — vault-wide, index-driven; runs once per invocation, not per anchor.
    # Computed vault-wide, REPORTED per-anchor: an explicit --anchor means the
    # caller asked about one tree, and another anchor's collision is not its work
    # to do or its stop-gate to inherit (F292).
    c53 = check_c53_anchor_name_collisions(vault_index, VAULT_ROOT)
    if args.anchor and args.anchor in all_backlogs:
        c53 = _scope_c53_to_anchor(c53, _anchor_root_for_backlog(all_backlogs[args.anchor]))
    findings.extend(c53)
    # B16 — C7 walks the same ask-format files + backlogs + Q.md (when in scope)
    c7_scope: list[Path] = []
    if args.scope in ("q", "all"):
        c7_scope.append(Q_MD)
    c7_scope.extend(p for _, p in ask_format_files)
    c7_scope.extend(anchor_backlogs.values())
    c7_scope = _dedupe_paths(c7_scope)  # same backlog double-add as C22 above
    findings.extend(check_c7_link_form(c7_scope, vault_index))
    # B16 — C12 walks anchor backlogs only (Verify-by lives on backlog rows)
    findings.extend(check_c12_verify_by_rationale(anchor_backlogs))
    # F089 — C13/C14/C15/C16/C18 walk each anchor's backlog entries
    today = date.today()
    f089_fixes_applied: list[str] = []
    for name, backlog_file in sorted(anchor_backlogs.items()):
        entries = backlog_entries(backlog_file, vault_index)
        findings.extend(check_c13_ready_h2_purity(entries))
        findings.extend(check_c14_active_h2_purity(entries))
        findings.extend(check_c15_watching_waiting_in_later(entries, today))
        findings.extend(check_c16_blocked_in_later(entries))
        findings.extend(check_c41_soak_question_declared(entries, backlog_file))
        findings.extend(check_c47_verify_ownership(entries, backlog_file))
        findings.extend(check_c51_user_action_present(entries, backlog_file))
        findings.extend(check_c57_row_hosts_question(entries, backlog_file))
        findings.extend(check_c18_verify_by_expired(entries, today))
        findings.extend(check_c23_designing_resolves(entries))
        findings.extend(check_c24_questions_count_match(entries))
        findings.extend(check_c25_designing_justification([backlog_file], vault_index))
        findings.extend(check_c32_h3_rows_forbidden([backlog_file]))
        findings.extend(check_c33_designing_needs_link(entries))
        findings.extend(check_c43_row_links_existing_doc(entries))
        findings.extend(check_c44_questions_row_has_target(entries))
        findings.extend(check_c45_open_questions_above_h1(entries))
        findings.extend(check_c48_q_stamp_drift(entries))
        findings.extend(check_c50_question_why_ask(entries))
        findings.extend(check_c49_next_nonanswer(entries, backlog_file))
        findings.extend(check_c34_inline_q_in_row_body([backlog_file]))
    # F124 — C35 queries.md drift check walks every anchor backlog's sibling
    # `{slug} queries.md` (per F176). Runs once after the per-anchor loop (not
    # per anchor), since each queries file is keyed by its sibling backlog's name.
    findings.extend(check_c35_ask_md_drift(anchor_backlogs, vault_index))
    # C55 (T159) — after the per-anchor loop, because a `[Blocked MUX-T068]`
    # edge written in DKT resolves against MUX's backlog: the checker needs the
    # whole universe (`all_backlogs`), not the scoped surface it reports on.
    findings.extend(check_c55_blocker_live_and_visible(
        anchor_backlogs, all_backlogs, vault_index))
    findings.extend(check_c37_queries_item_format(anchor_backlogs, vault_index))
    findings.extend(check_c46_queries_q_link_lands_on_qs(anchor_backlogs, vault_index))
    # F126 — C36 backtick-filepath check. Runs on Q.md (when in scope),
    # every per-anchor `{slug} queries.md`, AND every anchor backlog —
    # backlog rows are the source content that queries-render.py copies
    # into Q.md, so fixing the surface alone gets overwritten by the
    # next D1 banner-rewrite. Source-fix is durable.
    c36_surfaces: list[Path] = []
    if args.scope in ("q", "all"):
        c36_surfaces.append(Q_MD)
    for name, backlog_file in anchor_backlogs.items():
        c36_surfaces.append(backlog_file)
        queries_md = backlog_track_dir(backlog_file) / f"{name} queries.md"
        if queries_md.is_file():
            c36_surfaces.append(queries_md)
    for surface in c36_surfaces:
        findings.extend(check_c36_backtick_filepath(surface, vault_index))
    for name, backlog_file in sorted(anchor_backlogs.items()):
        entries = backlog_entries(backlog_file, vault_index)
        if args.fix:
            fix_log = apply_placement_fixes(backlog_file, entries, today)
            if fix_log:
                f089_fixes_applied.extend(f"  {name}: {msg}" for msg in fix_log)
                # apply_placement_fixes moves rows between H2 sections, which
                # shifts source-line numbers. Re-parse before apply_c23_fix so
                # its in-memory line indices match the on-disk file.
                entries = backlog_entries(backlog_file, vault_index)
            c23_changed, c23_log = apply_c23_fix(backlog_file, entries)
            if c23_changed:
                f089_fixes_applied.extend(f"  {name}: {msg}" for msg in c23_log)
                # C23 fix rewrites brackets, so re-parse before C24 sees them.
                entries = backlog_entries(backlog_file, vault_index)
            c24_changed, c24_log = apply_c24_fix(backlog_file, entries)
            if c24_changed:
                f089_fixes_applied.extend(f"  {name}: {msg}" for msg in c24_log)
    # B16 — apply mechanical fixes for C6 + C10 if --fix
    c6_fixes_applied: list[str] = []
    c10_fixes_applied: list[str] = []
    c36_fixes_applied: list[str] = []
    if args.fix:
        c6_fixes_applied = apply_c6_fix(all_q_entries)
        c10_fixes_applied = apply_c10_fix(all_q_entries)
        # F126 C36 — replace backtick file-paths with links on each surface
        for surface in c36_surfaces:
            n = apply_c36_fix(surface, findings, vault_index)
            if n:
                try:
                    rel = surface.relative_to(VAULT_ROOT)
                except ValueError:
                    rel = surface
                c36_fixes_applied.append(f"  {rel}: {n} replacement(s)")
    # QFix routing — file every non-mechanically-fixable residual on the
    # owning anchor's `B-QFix [Ready]` row. Per audit § Governing principle
    # (2026-06-04): every check has an agent-side fix path; routing puts the
    # residual where the owning Pilot's next /ask or /groom will see it
    # and drive it to zero under the 100%-fix rule.
    qfix_routing_log: list[str] = []
    if args.fix:
        qfix_routing_log = route_findings_to_qfix(findings, anchor_backlogs)
    else:
        qfix_routing_log = report_stale_qfix_rows(findings, anchor_backlogs)
    # Print findings + summary
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    print(f"\naudit-q: {len(findings)} findings ({len(errors)} errors, "
          f"{len(warnings)} warnings)", file=sys.stderr)
    for f in findings:
        rel = f.surface_file.relative_to(VAULT_ROOT) if VAULT_ROOT in f.surface_file.parents else f.surface_file
        print(f"  [{f.severity}] {f.code} {rel}:{f.surface_line} — {f.message}")
    if c4_fixes_applied:
        print(f"\naudit-q: C4 mechanical moves applied:")
        for line in c4_fixes_applied:
            print(line)
    if c6_fixes_applied:
        print(f"\naudit-q: C6 block-IDs appended:")
        for line in c6_fixes_applied:
            print(line)
    if c10_fixes_applied:
        print(f"\naudit-q: C10 Recommendations outdented:")
        for line in c10_fixes_applied:
            print(line)
    if c36_fixes_applied:
        print(f"\naudit-q: C36 backtick file-paths replaced with links:")
        for line in c36_fixes_applied:
            print(line)
    if f089_fixes_applied:
        print(f"\naudit-q: F089 placement fixes (C15/C16/C18 auto-moves):")
        for line in f089_fixes_applied:
            print(line)
    if qfix_routing_log:
        if args.fix:
            print(f"\naudit-q: QFix routing — non-mechanically-fixable residuals "
                  f"filed on owning anchors' B-QFix rows (per 100%-fix discipline):")
        else:
            print(f"\naudit-q: QFix staleness — a read-only pass reports, it does "
                  f"not clear (T144):")
        for line in qfix_routing_log:
            print(line)
    print(f"\naudit-q: derived banners for {len(derived_banners)} anchors")
    if args.fix and not args.dry and args.scope in ("q", "all", "backlog"):
        # D1: write derived banners back to Q.md (replace H1 lines for each
        # existing per-anchor section). Runs for backlog scope too so per-anchor
        # invocations (`--scope backlog --anchor X --fix` from backlog-edit.py)
        # actually update the Q.md banner.
        d1_changes = apply_d1_banner_write(Q_MD, derived_banners)
        if d1_changes:
            print(f"\naudit-q: D1 — {d1_changes} per-anchor section(s) regenerated in Q.md (via queries-render.py)")
        # C56 (F269) — prune orphan sections AFTER D1, so a section that D1
        # just refreshed is judged on what it is now, not what it was.
        # Q.md-scoped runs only: `--scope backlog` sees one anchor and must
        # never be the pass that decides the other 34 sections are dead.
        if args.scope in ("q", "all"):
            for _line in apply_c56_fix(Q_MD, all_backlogs):
                print(_line)
        # F247 — this run may have rewritten the backlog (C4/C23/C24 fixes) and
        # re-derived the banner; re-stamp each scoped backlog so its
        # state:backlog integrity stamp reflects the final content. Without this,
        # a standalone `audit-q --fix` would leave the stamp stale and the next
        # `state` call would mis-read it as an out-of-band hand-edit.
        for _bl in anchor_backlogs.values():
            try:
                _bl_lines = _bl.read_text(encoding="utf-8").splitlines(keepends=True)
                _bl_stamped = _be_mod.restamp_backlog(_bl_lines)
                if _bl_stamped != _bl_lines:
                    _bl.write_text("".join(_bl_stamped), encoding="utf-8")
            except OSError:
                pass
    # Hard-continuation directive — print whenever ANY anchor has Ready > 0.
    # Per user direction 2026-05-26 — the agent reads audit-q's output at the
    # moment they're tempted to stop; embedding the rule into that output is
    # the structural defense against lazy stops ("loop exited cleanly" with
    # Ready > 0). Phrase-patching the chat-summary loses to paraphrases;
    # status-line embedding doesn't, because it IS the status the agent reads.
    # Scope the push to the agent's OWN anchor (T052): an explicit --anchor
    # names it; otherwise resolve the cwd's containing anchor. A vault-wide
    # run must NOT tell the running agent to continue on someone else's
    # anchor (the failure that pushed Lumen onto MUX) — per crank § Hard
    # continuation, other anchors count only when the user names cross-anchor
    # scope, which this reminder cannot detect. Unresolvable cwd → suppress.
    own_slug = args.anchor or _owning_slug_for_cwd(all_backlogs)
    _print_hard_continuation_directive(derived_banners, own_slug)
    # F180 — auto-fire `when:: skill:audit-q` rules (e.g. the push/commit steer)
    # for the audited anchor(s), so they trigger on every normal run.
    autofire_audit_q(args.anchor, anchor_backlogs)
    return 1 if errors else 0


# Regex to extract the zone-1 class counts (Ready N, User N) from a derived
# banner line. F260 renamed the pair Ready/Questions -> Runnable/User; F305
# reverted the first half to `Ready` on brevity, so the word is back where it
# started while the MEANING is F260's (class Ready folds in `[Active]`, not
# just fresh rows). Anchored on `-  ` so the `Ready` here can only be zone 1's
# label and never a bracket name appearing later in the line.
_BANNER_COUNTS_RE = re.compile(
    r"-  Ready\s+(\d+)\s+User\s+(\d+)"
)


def _owning_slug_for_cwd(all_backlogs: dict[str, Path]) -> Optional[str]:
    """The slug of the anchor whose root contains the current working
    directory — the agent's OWN anchor. Deepest (longest-path) containing
    anchor root wins, so a cwd inside a sub-anchor that rolls up to its
    parent (its own backlog excluded from `all_backlogs`) resolves to the
    parent whose banner actually exists. None when cwd is outside every
    anchor. Used to scope the hard-continuation push to the agent's anchor
    (T052)."""
    try:
        cwd = Path.cwd().resolve()
    except OSError:
        return None
    best: Optional[str] = None
    best_len = -1
    for slug, backlog_file in all_backlogs.items():
        # {anchor}/{slug} Track/{slug} Backlog.md → anchor root is Track's parent
        root = backlog_track_dir(backlog_file).parent.resolve()
        try:
            cwd.relative_to(root)
        except ValueError:
            continue
        if len(str(root)) > best_len:
            best, best_len = slug, len(str(root))
    return best


def _print_hard_continuation_directive(
        derived_banners: dict[str, str],
        own_slug: Optional[str] = None) -> None:
    """When the agent's OWN anchor has Ready > 0, surface the crank hard-rule
    to the agent in audit-q's stderr-style output. The directive cites the
    rule's home, names the failure mode by name, and lists the exit
    requirement (3-gate argument). Silent when the own anchor is at Ready 0.

    `own_slug` scopes the push to the agent's anchor (T052). When None (cwd
    outside every anchor, and no --anchor given) the directive is suppressed
    entirely — pushing an agent onto anchors it does not own is exactly the
    failure this guard exists to prevent (crank § Hard continuation: other
    anchors count only when the user explicitly names cross-anchor scope)."""
    if own_slug is None:
        return
    actionable: list[tuple[str, int, int]] = []  # (name, ready_n, user_n)
    for name, banner in derived_banners.items():
        if name != own_slug:
            continue
        m = _BANNER_COUNTS_RE.search(banner)
        if not m:
            continue
        ready_n = int(m.group(1))
        user_n = int(m.group(2))
        if ready_n > 0:
            actionable.append((name, ready_n, user_n))
    if not actionable:
        return
    print()
    print("Agent requirement:  (skills/crank/SKILL.md § Hard continuation rule)")
    print("  Anchors with Ready > 0 — you MUST continue while context > 40%:")
    for name, r, q in sorted(actionable):
        print(f"    - {name}: Ready {r}, User {q}")
    print(
        "  To stop, print the 3-gate exit argument in chat:\n"
        "    Gate 1 (uncertain): I'd be guessing from <specific info gap>.\n"
        "    Gate 2 (high downside): wrong choice would <concrete consequence>.\n"
        "    Gate 3 (continuing IS the risk): the specific bad outcome of\n"
        "      continuing is <which file gets corrupted / which interface gets\n"
        "      locked in / which downstream commit becomes load-bearing on a\n"
        "      wrong choice>. Cost of stopping < that risk because <one sentence>.\n"
        "  If you can't fill any blank with concrete content, the rule's\n"
        "  diagnosis is: CONTINUE. 'Loop exited cleanly' / 'natural pause' /\n"
        "  'handoff to user' with Ready > 0 are spec violations — they look\n"
        "  like exit messages but don't satisfy Gate 3.")


def apply_d1_banner_write(qmd_file: Path, derived_banners: dict[str, str]) -> int:
    """Regenerate the per-anchor section in Q.md for each anchor with a derived
    banner — delegates the actual write to `queries-render.py {slug}` (per F104;
    engine re-homed from the retired triage skill by F231).

    Each subprocess call rewrites the entire per-anchor section (which is the
    anchor's `{slug} queries.md` body, copied) and bubbles it to the top of Q.md.
    Returns the count of sections rewritten.

    Falls back to in-process banner-only rewrite if queries-render.py is
    unreachable — preserves the original D1 behavior so audit-q can still fix
    banner-only drift even if the script went missing."""
    import subprocess
    render_script = (Path.home() / ".claude" / "skills" / "audit"
                     / "scripts" / "queries-render.py")
    if not render_script.is_file():
        # Fallback — original banner-only rewrite (preserves pre-F104 behavior)
        try:
            lines = qmd_file.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            return 0
        changed = 0
        for i, line in enumerate(lines):
            m = QMD_BANNER_RE.match(line)
            if not m:
                continue
            name = m.group("name")
            derived = derived_banners.get(name)
            if derived and derived != line:
                lines[i] = derived
                changed += 1
        if changed:
            qmd_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
            _selffire(qmd_file)
        return changed
    rewrites = 0
    for name in derived_banners.keys():
        result = subprocess.run(
            ["python3", str(render_script), name],
            capture_output=True, text=True, check=False,
        )
        if result.returncode == 0:
            rewrites += 1
    return rewrites


if __name__ == "__main__":
    sys.exit(main())
