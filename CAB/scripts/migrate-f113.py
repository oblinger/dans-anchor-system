#!/usr/bin/env python3
"""
F113 Phase 1b migration script — Phase A (discovery) + Phase B (per-anchor restructure).

Per [[F113 Migration Script Approach]]:
  Phase A (READ-ONLY): walk vault, build inventory, report.
  Phase B (default dry-run, --execute to write): per-anchor structural migration —
    hoist Docs/ wrapper, rename Plan→Track (where still legacy), build Decisions
    from Principles+Rules, rename Discussion→Log, surface System Design for review.

Phase C-G (cross-ref rewrites, CAB spec updates, tooling updates, verification,
single commit) — not yet implemented.

Usage:
    python3 migrate-f113.py --phase A [--vault-root <path>]
    python3 migrate-f113.py --phase B [--anchor <name>] [--execute]
    python3 migrate-f113.py --phase B --anchor CAE                # dry-run, one anchor
    python3 migrate-f113.py --phase B --anchor CAE --execute      # write
"""

import argparse
import shutil
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


# Filesystem-walk exclusions (consistent with audit-q.py).
EXCLUDED_PATH_FRAGMENTS = (".trash", "Closet", "Yore", "worktrees", ".claude", ".git", ".history")


@dataclass
class AnchorInventory:
    """Per-anchor migration inventory."""
    name: str                        # the anchor folder's basename (== slug or full name)
    path: Path                       # absolute path to the anchor folder
    has_anchor_file: bool            # `.anchor` marker present
    docs_folder: Path | None = None  # `{NAME} Docs/` if present
    plan_folder: Path | None = None  # `{NAME} Docs/{NAME} Plan/` or `{NAME} Plan/` if present
    track_folder: Path | None = None  # `{NAME} Docs/{NAME} Track/` or `{NAME} Track/` if present
    design_folder: Path | None = None  # `{NAME} Docs/{NAME} Design/` or `{NAME} Design/` if present
    user_folder: Path | None = None  # `{NAME} Docs/{NAME} User/` or `{NAME} User/` if present
    dev_folder: Path | None = None   # `{NAME} Docs/{NAME} Dev/` or `{NAME} Dev/` if present
    arch_location: str | None = None  # "design", "user", "anchor-root", "design-root", or None
    arch_path: Path | None = None    # actual Architecture folder/file
    principles_path: Path | None = None
    rules_path: Path | None = None
    system_design_path: Path | None = None
    discussion_path: Path | None = None
    log_path: Path | None = None     # informal {NAME} Log.md if present
    ux_design_path: Path | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def has_decisions_content(self) -> bool:
        return bool(self.principles_path or self.rules_path)

    @property
    def is_f113_relevant(self) -> bool:
        """Anchor has F113-relevant structure to migrate (i.e., not a personal-org leaf)."""
        return bool(
            self.docs_folder or self.plan_folder or self.track_folder or self.design_folder
            or self.principles_path or self.rules_path or self.system_design_path
            or self.discussion_path or self.ux_design_path or self.arch_path
        )


def find_anchors(vault_root: Path) -> list[Path]:
    """Walk vault_root finding every folder containing `.anchor`."""
    anchors: list[Path] = []
    for path in vault_root.rglob(".anchor"):
        # Skip excluded path fragments.
        path_str = str(path)
        if any(frag in path_str for frag in EXCLUDED_PATH_FRAGMENTS):
            continue
        if path.is_file():
            anchors.append(path.parent)
    return sorted(anchors)


def _find_first(name: str, basename: str, parents: list[Path]) -> Path | None:
    """Find `{name} {basename}` as file or directory under any of `parents`."""
    for parent in parents:
        if not parent or not parent.is_dir():
            continue
        for trial in (parent / f"{name} {basename}", parent / f"{name} {basename}.md"):
            if trial.exists():
                return trial
    return None


def classify_anchor(anchor_path: Path) -> AnchorInventory:
    """Build the inventory record for one anchor.

    Looks for Plan/Track/Design/User/Dev as children of either:
      - `{name} Docs/` (legacy CAB shape), or
      - the anchor root itself (already-partially-migrated shape, post-F094).

    Looks for facet files (Principles/Rules/SystemDesign/Discussion/UXDesign) under
    Plan, Track, Design, or User — covering all observed pre-F113 locations.
    """
    name = anchor_path.name
    inv = AnchorInventory(name=name, path=anchor_path, has_anchor_file=True)

    # Layer 1: optional `{name} Docs/` parent
    docs = anchor_path / f"{name} Docs"
    if docs.is_dir():
        inv.docs_folder = docs

    # Layer 2: sub-folders under Docs/ OR directly under anchor root.
    # An anchor can be in any of three intermediate states:
    #   (A) legacy: everything under Docs/
    #   (B) F094-partial: Design/ moved out of Docs/User/, rest still under Docs/
    #   (C) F113-post: Track/ / Design/ / User/ all at anchor root, no Docs/
    candidates_plan = [docs, anchor_path]
    candidates_track = [docs, anchor_path]
    candidates_design = [docs, anchor_path]
    candidates_user = [docs, anchor_path]
    candidates_dev = [docs, anchor_path]

    for parent in candidates_plan:
        if parent and parent.is_dir() and (parent / f"{name} Plan").is_dir():
            inv.plan_folder = parent / f"{name} Plan"
            break
    for parent in candidates_track:
        if parent and parent.is_dir() and (parent / f"{name} Track").is_dir():
            inv.track_folder = parent / f"{name} Track"
            break
    for parent in candidates_design:
        if parent and parent.is_dir() and (parent / f"{name} Design").is_dir():
            inv.design_folder = parent / f"{name} Design"
            break
    for parent in candidates_user:
        if parent and parent.is_dir() and (parent / f"{name} User").is_dir():
            inv.user_folder = parent / f"{name} User"
            break
    for parent in candidates_dev:
        if parent and parent.is_dir() and (parent / f"{name} Dev").is_dir():
            inv.dev_folder = parent / f"{name} Dev"
            break

    # Architecture: search under Design / User / anchor root (covers F074/F094/post-F113).
    arch_candidates = [
        (inv.design_folder, "design"),
        (inv.user_folder, "user"),
        (anchor_path, "anchor-root"),
    ]
    for parent, label in arch_candidates:
        if not parent:
            continue
        if (parent / f"{name} Architecture").is_dir():
            inv.arch_location = label
            inv.arch_path = parent / f"{name} Architecture"
            break
        if (parent / f"{name} Architecture.md").is_file():
            inv.arch_location = label
            inv.arch_path = parent / f"{name} Architecture.md"
            break

    # Facet files — look under Plan, Track, Design, User (covers all observed locations).
    facet_parents = [
        inv.plan_folder, inv.track_folder, inv.design_folder, inv.user_folder,
    ]
    facet_parents = [p for p in facet_parents if p]

    inv.principles_path = _find_first(name, "Principles", facet_parents)
    inv.rules_path = _find_first(name, "Rules", facet_parents)
    inv.system_design_path = _find_first(name, "System Design", facet_parents)
    inv.discussion_path = _find_first(name, "Discussion", facet_parents)
    inv.ux_design_path = _find_first(name, "UX Design", facet_parents)

    # Informal {NAME} Log.md — at anchor root or under Design
    for parent in [anchor_path, inv.design_folder]:
        if not parent:
            continue
        log = parent / f"{name} Log.md"
        if log.is_file():
            inv.log_path = log
            break

    # Validation: warn on unusual cases.
    if inv.docs_folder and inv.arch_location not in ("design", "user", None):
        inv.warnings.append(
            f"unexpected Architecture location {inv.arch_location!r}"
        )
    if inv.plan_folder and inv.track_folder:
        inv.warnings.append(
            "both Plan/ and Track/ exist — partial migration state; needs merge"
        )

    return inv


def _rel(p: Path | None) -> str:
    """Format a path relative to VAULT_ROOT, or return empty string if None."""
    if p is None:
        return ""
    try:
        return str(p.relative_to(VAULT_ROOT))
    except ValueError:
        return str(p)


def report(inventories: list[AnchorInventory]) -> None:
    """Print a structured report of the discovered inventory."""
    relevant = [i for i in inventories if i.is_f113_relevant]
    irrelevant_count = len(inventories) - len(relevant)

    print("=" * 78)
    print("F113 Phase A — Discovery Report")
    print("=" * 78)
    print()
    print(f"Anchors discovered:    {len(inventories)}")
    print(f"  F113-relevant:       {len(relevant)}")
    print(f"  not in scope:        {irrelevant_count} (personal-org leaves with no CAB-shape content)")
    print()

    # Summary counters — over F113-relevant only.
    have_docs = sum(1 for i in relevant if i.docs_folder)
    have_plan = sum(1 for i in relevant if i.plan_folder)
    have_track = sum(1 for i in relevant if i.track_folder)
    have_design = sum(1 for i in relevant if i.design_folder)
    have_user = sum(1 for i in relevant if i.user_folder)
    have_dev = sum(1 for i in relevant if i.dev_folder)
    have_arch = sum(1 for i in relevant if i.arch_path)
    have_decisions = sum(1 for i in relevant if i.has_decisions_content)
    have_principles = sum(1 for i in relevant if i.principles_path)
    have_rules = sum(1 for i in relevant if i.rules_path)
    have_system_design = sum(1 for i in relevant if i.system_design_path)
    have_discussion = sum(1 for i in relevant if i.discussion_path)
    have_log = sum(1 for i in relevant if i.log_path)
    have_ux = sum(1 for i in relevant if i.ux_design_path)
    have_warnings = sum(1 for i in relevant if i.warnings)

    arch_locations = Counter(i.arch_location for i in relevant if i.arch_location)

    print("Structural inventory (F113-relevant anchors only):")
    print(f"  Docs/ parent present:                     {have_docs:>3}")
    print(f"  Plan/ subfolder (needs rename to Track):  {have_plan:>3}")
    print(f"  Track/ subfolder (already renamed):       {have_track:>3}")
    print(f"  Design/ subfolder:                        {have_design:>3}")
    print(f"  User/ subfolder:                          {have_user:>3}")
    print(f"  Dev/ subfolder (needs folding):           {have_dev:>3}")
    print(f"  Architecture present:                     {have_arch:>3}")
    print(f"    by location: {dict(arch_locations)}")
    print(f"  Principles.md present:                    {have_principles:>3}")
    print(f"  Rules.md present:                         {have_rules:>3}")
    print(f"  System Design.md present:                 {have_system_design:>3}")
    print(f"  Discussion.md present:                    {have_discussion:>3}")
    print(f"  Informal Log.md already present:          {have_log:>3}")
    print(f"  UX Design.md present:                     {have_ux:>3}")
    print(f"  Anchors with structural warnings:         {have_warnings:>3}")
    print()

    # Per-anchor detail — relevant only.
    print("-" * 78)
    print("Per-anchor inventory (alphabetical; F113-relevant only):")
    print("-" * 78)
    for inv in relevant:
        marks = []
        if inv.docs_folder: marks.append("Docs")
        if inv.plan_folder: marks.append("Plan")
        if inv.track_folder: marks.append("Track")
        if inv.design_folder: marks.append("Design")
        if inv.user_folder: marks.append("User")
        if inv.dev_folder: marks.append("Dev")
        if inv.arch_location:
            marks.append(f"Arch@{inv.arch_location}")
        if inv.principles_path: marks.append("Principles")
        if inv.rules_path: marks.append("Rules")
        if inv.system_design_path: marks.append("SysDesign")
        if inv.discussion_path: marks.append("Discussion")
        if inv.log_path: marks.append("Log")
        if inv.ux_design_path: marks.append("UX")

        marks_str = ", ".join(marks) if marks else "(empty)"
        print(f"  {inv.name:<{NAME_W}}  {marks_str}")
        print(f"  {'':<{NAME_W}}  → {_rel(inv.path)}")
        for w in inv.warnings:
            print(f"  {'':<{NAME_W}}  ⚠ {w}")
    print()

    # Migration impact summary.
    print("-" * 78)
    print("Migration impact summary:")
    print("-" * 78)
    print(f"  Anchors with Decisions content (Principles or Rules):  {have_decisions}")
    print(f"  Anchors with System Design to fold in (needs review):  {have_system_design}")
    print(f"  Anchors with Discussion to rename to Log:              {have_discussion}")
    print(f"  Anchors with informal Log already at anchor-root:      {have_log}")
    print(f"  Anchors with UX Design (rename to UX):                 {have_ux}")
    print(f"  Anchors with Plan/ folder (rename to Track/):          {have_plan}")
    print(f"  Anchors with Docs/ parent (remove + hoist children):   {have_docs}")
    print(f"  Anchors with warnings (review needed):                 {have_warnings}")
    print()

    # Phase B' candidates — System Design fold-in needs user judgment per anchor.
    sd_anchors = [i for i in relevant if i.system_design_path]
    if sd_anchors:
        print("-" * 78)
        print("Phase B' — System Design fold-in candidates (per-anchor user review needed):")
        print("-" * 78)
        for i in sd_anchors:
            print(f"  {i.name:<{NAME_W}}  → {_rel(i.system_design_path)}")
        print()
        print("  → For each, per-anchor agent will categorize content into Architecture / Log / drop.")
        print()

    # Conflict warning: informal Log.md + Discussion.md both present.
    conflicts = [i for i in relevant if i.discussion_path and i.log_path]
    if conflicts:
        print("-" * 78)
        print("Discussion + Log conflict (both files exist; will need merge):")
        print("-" * 78)
        for i in conflicts:
            print(f"  {i.name}")
            print(f"    Discussion: {_rel(i.discussion_path)}")
            print(f"    Log:        {_rel(i.log_path)}")
        print()

    print("=" * 78)
    print(f"END Phase A discovery. {len(relevant)} F113-relevant anchors classified, "
          f"{have_warnings} with warnings.")
    print("=" * 78)


# ============================================================
# Phase B — Per-anchor structural migration
# ============================================================


@dataclass
class PlannedMove:
    """One filesystem operation in Phase B's plan."""
    op: str        # 'mkdir' | 'move' | 'write' | 'delete' | 'note'
    src: Path | None = None
    dst: Path | None = None
    content: str | None = None   # for op='write'
    note: str | None = None      # human-readable annotation


def _walk_files(p: Path) -> list[Path]:
    """List all files (recursively) under p, sorted."""
    if not p.is_dir():
        return []
    return sorted(f for f in p.rglob("*") if f.is_file())


def plan_phase_b_for_anchor(inv: AnchorInventory) -> list[PlannedMove]:
    """Produce the ordered move list for migrating one anchor to F113 shape.

    Target end-state per [[F113 Migration Script Approach]] § Phase B:
        {NAME}/                          (anchor root)
            {NAME} Design/               (architecture, decisions, etc.)
                {NAME} Architecture/    (or .md)
                {NAME} Decisions.md      (merged from Principles + Rules)
                {NAME} UX.md             (renamed from UX Design.md, if existed)
                ... other Design-content
            {NAME} Track/                (was Plan/, or already Track/ post-F094)
                {NAME} Backlog.md
                {NAME} Roadmap.md
                {NAME} Features/
                ... other Track-content
            {NAME} User/                 (user-facing docs)
            {NAME} Log.md                (renamed from Discussion.md; at anchor root)

    What disappears:
        {NAME} Docs/                     (parent wrapper removed)
        {NAME} Principles.md             (folded into Decisions)
        {NAME} Rules.md                  (folded into Decisions)
        {NAME} System Design.md          (Phase B' — surface for review; not auto-folded in v1)
        {NAME} Discussion.md             (renamed to Log.md)
        {NAME} UX Design.md              (renamed to UX.md)
    """
    moves: list[PlannedMove] = []
    name = inv.name
    root = inv.path

    target_design = root / f"{name} Design"
    target_track = root / f"{name} Track"
    target_user = root / f"{name} User"
    target_dev = root / f"{name} Dev"

    # ---- Step 1: create target top-level folders if missing ----
    # Design/Track/User are always created. Dev/ only if the source has a Dev folder.
    for tgt in (target_design, target_track, target_user):
        if not tgt.exists():
            moves.append(PlannedMove(op="mkdir", dst=tgt))
    if inv.dev_folder and not target_dev.exists():
        moves.append(PlannedMove(op="mkdir", dst=target_dev))

    # ---- Step 2: hoist content out of Docs/ wrapper ----
    # If current Plan/Track/Design/User folders live under Docs/, move them out.
    src_dst_pairs = []
    if inv.plan_folder:
        # Plan/ → Track/ (with rename to Track if it was Plan)
        # If a Track/ already exists at target, that's a conflict — surface as note.
        if target_track.exists() and target_track != inv.plan_folder:
            moves.append(PlannedMove(
                op="note",
                note=f"CONFLICT: target {target_track.name}/ already exists but Plan/ also present at "
                     f"{_rel(inv.plan_folder)} — needs manual merge before Phase B can run."
            ))
        else:
            # Move every file from plan_folder to target_track
            src_dst_pairs.append((inv.plan_folder, target_track, "Plan→Track rename + hoist"))
    if inv.track_folder and inv.track_folder != target_track:
        # Track/ already exists but under Docs/ — hoist
        src_dst_pairs.append((inv.track_folder, target_track, "Track/ hoist out of Docs/"))
    if inv.design_folder and inv.design_folder != target_design:
        src_dst_pairs.append((inv.design_folder, target_design, "Design/ hoist out of Docs/"))
    if inv.user_folder and inv.user_folder != target_user:
        src_dst_pairs.append((inv.user_folder, target_user, "User/ hoist out of Docs/"))
    if inv.dev_folder and inv.dev_folder != target_dev:
        src_dst_pairs.append((inv.dev_folder, target_dev, "Dev/ hoist to anchor root"))

    for src_folder, dst_folder, label in src_dst_pairs:
        for f in _walk_files(src_folder):
            rel = f.relative_to(src_folder)
            moves.append(PlannedMove(
                op="move", src=f, dst=dst_folder / rel,
                note=label,
            ))

    # ---- Step 3: build Decisions.md (+ optional Decisions Details.md) ----
    if inv.principles_path or inv.rules_path:
        decisions_target = target_design / f"{name} Decisions.md"
        if decisions_target.exists():
            moves.append(PlannedMove(
                op="note",
                note=f"NOTE: {decisions_target.name} already exists; will OVERWRITE during execute."
            ))
        decisions_body = _build_decisions_body(name, inv)
        moves.append(PlannedMove(
            op="write", dst=decisions_target, content=decisions_body,
            note=f"Build Decisions from "
                 + (f"Principles ({_rel(inv.principles_path)})" if inv.principles_path else "")
                 + (" + " if inv.principles_path and inv.rules_path else "")
                 + (f"Rules ({_rel(inv.rules_path)})" if inv.rules_path else "")
        ))
        # Optional companion: Decisions Details.md (same facet, different file).
        details_body = _build_details_body(name, inv)
        if details_body:
            details_target = target_design / f"{name} Decisions Details.md"
            moves.append(PlannedMove(
                op="write", dst=details_target, content=details_body,
                note=f"Build optional Decisions Details (Why / rationale per D-number)",
            ))
        # Delete source Principles/Rules AFTER Decisions is written.
        # Note: after the hoist in step 2, these files live at their new locations.
        if inv.principles_path:
            new_p = _post_hoist_path(inv.principles_path, src_dst_pairs)
            moves.append(PlannedMove(op="delete", src=new_p, note="delete migrated Principles.md"))
        if inv.rules_path:
            new_r = _post_hoist_path(inv.rules_path, src_dst_pairs)
            moves.append(PlannedMove(op="delete", src=new_r, note="delete migrated Rules.md"))

    # ---- Step 4: System Design — Phase B', surface for review (no auto-fold v1) ----
    if inv.system_design_path:
        new_sd = _post_hoist_path(inv.system_design_path, src_dst_pairs)
        moves.append(PlannedMove(
            op="note",
            note=f"PHASE B' REVIEW: System Design at {_rel(new_sd)} — left in place; "
                 f"user folds content into Architecture or Log post-migration."
        ))

    # ---- Step 5: rename Discussion → Log ----
    if inv.discussion_path:
        new_disc = _post_hoist_path(inv.discussion_path, src_dst_pairs)
        log_target = root / f"{name} Log.md"
        if inv.log_path:
            # Informal Log already exists — surface as merge needed.
            moves.append(PlannedMove(
                op="note",
                note=f"MERGE: existing {inv.log_path.name} ({_rel(inv.log_path)}) + "
                     f"Discussion ({_rel(new_disc)}) — concat with separator on execute."
            ))
            moves.append(PlannedMove(
                op="write", dst=log_target, content="<MERGE-MARKER>",
                note="merged Log.md from existing Log + Discussion",
            ))
            moves.append(PlannedMove(op="delete", src=new_disc, note="delete migrated Discussion.md (merged into Log)"))
        else:
            moves.append(PlannedMove(op="move", src=new_disc, dst=log_target, note="Discussion → Log rename"))

    # ---- Step 6: rename UX Design → UX ----
    if inv.ux_design_path:
        new_ux = _post_hoist_path(inv.ux_design_path, src_dst_pairs)
        ux_target = target_design / f"{name} UX.md"
        moves.append(PlannedMove(op="move", src=new_ux, dst=ux_target, note="UX Design → UX rename"))

    # ---- Step 7: clean up empty Docs/ wrapper ----
    if inv.docs_folder:
        docs_md = inv.docs_folder / f"{name} Docs.md"
        if docs_md.is_file():
            moves.append(PlannedMove(
                op="delete", src=docs_md,
                note=f"delete {name} Docs.md (wrapper umbrella; folder being removed). "
                     f"NOTE: {name} Design.md remains as the Design folder umbrella."
            ))
        moves.append(PlannedMove(
            op="delete", src=inv.docs_folder,
            note=f"remove empty Docs/ wrapper ({_rel(inv.docs_folder)})"
        ))

    return moves


def _post_hoist_path(orig_path: Path, src_dst_pairs: list) -> Path:
    """Given a path that pointed at a file under Docs/X/, return where it lands post-hoist."""
    for src_folder, dst_folder, _ in src_dst_pairs:
        try:
            rel = orig_path.relative_to(src_folder)
            return dst_folder / rel
        except ValueError:
            continue
    return orig_path


def _build_decisions_body(name: str, inv: AnchorInventory) -> str:
    """Build {NAME} Decisions.md — the lean canonical list (Statement + optional
    Check pattern + Exceptions + See also). Why / Examples / Tests / Source-provenance
    live in the parallel {NAME} Decisions Details.md (built by _build_details_body).

    Both files belong to the Decisions facet (one facet, two files); Details is
    optional and only created when there's source rationale to preserve.

    v1 heuristic: pass-through concatenation under H2 groupings derived from source
    structure (CAE Rules' `## Structural Rules` + `## Code Rules`, Principles flat).
    Full topic-categorization per [[CAB Decisions]] § Migration is deferred to v2.
    """
    out: list[str] = []
    out.append("---")
    out.append(f"description: {name} Decisions — the canonical list. Statement + optional "
               f"Check pattern + Exceptions + See also. Why / Examples / Tests live in "
               f"the parallel `{name} Decisions Details.md` (same facet, optional companion).")
    out.append("---")
    out.append("")
    out.append(f"# {name} Decisions")
    out.append("")
    out.append(f"> **Migrated per F113 Phase 1b.** Lean canonical list — rationale lives "
               f"in [[{name} Decisions Details]]. Initial H2 grouping is pass-through "
               f"(by source file); refine into topic groups post-migration.")
    out.append("")

    d_counter = 1
    # Collect (D-num, lean_entry, details_entry) tuples for both files.
    all_entries: list[tuple[int, str, str]] = []

    if inv.principles_path:
        content = inv.principles_path.read_text(encoding="utf-8", errors="replace")
        out.append(f"## Principles (migrated from {name} Principles.md)")
        out.append("")
        for lean, details, dnum in _extract_decision_entries(content, "reviewed", d_counter):
            out.append(lean)
            out.append("")
            all_entries.append((dnum, lean, details))
            d_counter = dnum + 1

    if inv.rules_path:
        content = inv.rules_path.read_text(encoding="utf-8", errors="replace")
        has_ex_table = "## EX" in content or "## Excellence" in content or "EX-table" in content.lower()
        tier = "tracked" if has_ex_table else "checked"
        out.append(f"## Rules (migrated from {name} Rules.md, default tier: {tier})")
        out.append("")
        for lean, details, dnum in _extract_decision_entries(content, tier, d_counter):
            out.append(lean)
            out.append("")
            all_entries.append((dnum, lean, details))
            d_counter = dnum + 1

    out.append("## Migration")
    out.append("")
    out.append(f"Generated by `migrate-f113.py` Phase B. Source: "
               + (f"`{name} Principles.md` " if inv.principles_path else "")
               + (f"`{name} Rules.md`" if inv.rules_path else "")
               + f". Why / rationale → [[{name} Decisions Details]]. "
               + "D-numbers persist (never recycled).")
    out.append("")

    # Stash details for the caller to write.
    inv._migrated_details = all_entries  # type: ignore[attr-defined]

    return "\n".join(out)


def _build_details_body(name: str, inv: AnchorInventory) -> str | None:
    """Build {NAME} Decisions Details.md — optional companion to Decisions.md.

    Contains Why / Examples / Tests / Source-provenance per D-number. Built from
    the `_migrated_details` stash that `_build_decisions_body` populated.

    Returns None if no details content was extracted (no need for a Details file).
    """
    pairs = getattr(inv, "_migrated_details", None)
    if not pairs:
        return None
    # Skip if all details are empty.
    nonempty = [(dnum, det) for (dnum, _, det) in pairs if det.strip()]
    if not nonempty:
        return None

    out: list[str] = []
    out.append("---")
    out.append(f"description: {name} Decisions Details — companion to `{name} Decisions.md`. "
               f"Why / rationale / examples / tests / source-provenance per D-number. "
               f"Optional: only present when there's detail worth recording.")
    out.append("---")
    out.append("")
    out.append(f"# {name} Decisions Details")
    out.append("")
    out.append(f"> Companion to [[{name} Decisions]]. Each H2 below mirrors a D-entry in "
               f"the canonical list and carries its rationale + supplementary detail. "
               f"Decisions.md is the operational reference; this file is the contextual depth.")
    out.append("")
    for dnum, details in nonempty:
        out.append(f"## D{dnum:02d}")
        out.append("")
        out.append(details.strip())
        out.append("")
    return "\n".join(out)


import re as _re

_PREFIX_RE = _re.compile(r"^[A-Z]{1,3}\d+\s*[—-]\s*")


# Bold-label sections that route to the **Details** file (rationale, provenance).
_DETAILS_LABELS = ("why", "rationale", "encoded by", "encodes")
# Bold-label sections that stay in the **Decisions** file (operational content).
_LEAN_LABELS = ("check pattern", "exceptions", "see also", "rule")
_LABEL_RE = _re.compile(r"^\*\*([^*:]+):\*\*\s*(.*)$")


def _extract_decision_entries(
    content: str, source_tier: str, counter_start: int
) -> list[tuple[str, str, int]]:
    """Walk markdown content, extract each decision (Principle or Rule).

    Returns a list of `(lean_entry, details_entry, d_num)` tuples:
      - lean_entry: formatted `### D<n> — Title (tier)` + Statement + Check pattern
        + Exceptions + See also. Goes into Decisions.md.
      - details_entry: Why + Rationale + Encoded by + any other rationale-flavored
        content. Goes into Decisions Details.md (under `## D<n>`).
      - d_num: the assigned D-number.

    Auto-detects title heading level (H2 in CAE Principles, H3 in CAE Rules).
    Sub-headings (e.g. `### Exceptions`) fold into body as `**Label:**` bold prefix.
    Strips source prefix (`P01 — `, `R03 — `) — new D-number replaces it.
    """
    lines = content.split("\n")

    title_level = "### "
    for line in lines:
        if _re.match(r"^## [A-Z]{1,3}\d+\s*[—-]", line):
            title_level = "## "
            break
        if _re.match(r"^### [A-Z]{1,3}\d+\s*[—-]", line):
            title_level = "### "
            break

    entries: list[tuple[str, str, int]] = []
    current_lean: list[str] = []
    current_details: list[str] = []
    current_title: str | None = None
    routing: str = "lean"  # 'lean' (Statement/Check pattern/Exceptions) or 'details' (Why/etc.)
    d_num = counter_start

    _heading_re = _re.compile(r"^(#+)\s+(.*)$")
    _decision_re = _re.compile(rf"^{title_level}[A-Z]{{1,3}}\d+\s*[—-]")

    def _route_for(label_text: str) -> str:
        low = label_text.strip().lower()
        if any(low.startswith(d) for d in _DETAILS_LABELS):
            return "details"
        if any(low.startswith(L) for L in _LEAN_LABELS):
            return "lean"
        # Default: stay in lean (preserves unknown labels in the canonical doc).
        return "lean"

    def flush():
        nonlocal d_num
        if current_title is not None:
            stripped_title = _PREFIX_RE.sub("", current_title).strip()
            lean_body = "\n".join(current_lean).strip()
            details_body = "\n".join(current_details).strip()
            lean_entry = f"### D{d_num:02d} — {stripped_title} ({source_tier})\n\n{lean_body}"
            entries.append((lean_entry, details_body, d_num))
            d_num += 1

    for line in lines:
        if _decision_re.match(line):
            flush()
            current_title = line[len(title_level):].strip()
            current_lean = []
            current_details = []
            routing = "lean"
            continue
        if current_title is None:
            continue  # pre-first-decision content (frontmatter, H1)

        hm = _heading_re.match(line)
        if hm:
            # Sub-heading folds into body as `**Label:**`. May switch routing.
            label_text = hm.group(2).strip()
            routing = _route_for(label_text)
            target = current_details if routing == "details" else current_lean
            target.append(f"**{label_text}:**")
            continue

        lm = _LABEL_RE.match(line)
        if lm:
            # Inline bold-label like `**Why:** body...` — switch routing for this line + body.
            label_text = lm.group(1).strip()
            tail = lm.group(2)
            routing = _route_for(label_text)
            target = current_details if routing == "details" else current_lean
            # Preserve the label + inline tail; subsequent unlabeled lines route to same target.
            if routing == "lean" and label_text.lower() == "rule":
                # Drop the redundant `**RULE:**` prefix per user direction — statement stands alone.
                if tail:
                    target.append(tail)
            else:
                if tail:
                    target.append(f"**{label_text}:** {tail}")
                else:
                    target.append(f"**{label_text}:**")
            continue

        # Continuation line — append to current routing's body.
        target = current_details if routing == "details" else current_lean
        target.append(line)

    flush()
    return entries


def execute_moves(moves: list[PlannedMove], dry_run: bool) -> tuple[int, int]:
    """Apply (or print) the planned moves. Returns (applied, errors)."""
    applied = 0
    errors = 0

    for m in moves:
        label = m.op.upper()
        try:
            if m.op == "note":
                print(f"  [note] {m.note}")
            elif m.op == "mkdir":
                assert m.dst is not None
                print(f"  [mkdir] {_rel(m.dst)}" + (f"  ({m.note})" if m.note else ""))
                if not dry_run:
                    m.dst.mkdir(parents=True, exist_ok=True)
                applied += 1
            elif m.op == "move":
                assert m.src is not None and m.dst is not None
                print(f"  [move] {_rel(m.src)}  →  {_rel(m.dst)}"
                      + (f"  ({m.note})" if m.note else ""))
                if not dry_run:
                    m.dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(m.src), str(m.dst))
                applied += 1
            elif m.op == "write":
                assert m.dst is not None
                size = len(m.content) if m.content else 0
                marker = ""
                if m.content == "<MERGE-MARKER>":
                    marker = "  [MERGE-DEFERRED]"
                print(f"  [write] {_rel(m.dst)}  ({size} bytes){marker}"
                      + (f"  ({m.note})" if m.note else ""))
                if not dry_run:
                    if m.content == "<MERGE-MARKER>":
                        # Defer merge logic to a v2 — for now, skip write so user notices.
                        print(f"    SKIPPED: <MERGE-MARKER> not yet implemented; "
                              f"resolve manually after dry-run review.")
                    elif m.content is not None:
                        m.dst.parent.mkdir(parents=True, exist_ok=True)
                        m.dst.write_text(m.content, encoding="utf-8")
                applied += 1
            elif m.op == "delete":
                if m.src and m.src.is_dir():
                    print(f"  [rmdir] {_rel(m.src)}"
                          + (f"  ({m.note})" if m.note else ""))
                    if not dry_run:
                        # Only remove if empty.
                        try:
                            m.src.rmdir()
                        except OSError as e:
                            print(f"    WARN: cannot rmdir (not empty?): {e}")
                            errors += 1
                            continue
                else:
                    print(f"  [delete] {_rel(m.src)}"
                          + (f"  ({m.note})" if m.note else ""))
                    if not dry_run and m.src and m.src.exists():
                        m.src.unlink()
                applied += 1
        except Exception as e:
            print(f"  [ERROR] {label} failed: {e}")
            errors += 1

    return applied, errors


def run_phase_b(inventories: list[AnchorInventory], target_anchor: str | None, dry_run: bool) -> int:
    """Run Phase B over all (or one named) anchor. Returns exit code."""
    relevant = [i for i in inventories if i.is_f113_relevant]
    if target_anchor:
        relevant = [i for i in relevant if i.name == target_anchor]
        if not relevant:
            print(f"error: no F113-relevant anchor named {target_anchor!r}", file=sys.stderr)
            return 2

    mode = "DRY-RUN" if dry_run else "EXECUTE"
    print("=" * 78)
    print(f"F113 Phase B — Per-anchor restructure ({mode})")
    print("=" * 78)
    print(f"Anchors to process: {len(relevant)}")
    print()

    total_applied = 0
    total_errors = 0

    for inv in relevant:
        if inv.warnings:
            print(f"--- {inv.name} (SKIPPED: has structural warnings) ---")
            for w in inv.warnings:
                print(f"  ⚠ {w}")
            print()
            continue
        print(f"--- {inv.name} ({_rel(inv.path)}) ---")
        moves = plan_phase_b_for_anchor(inv)
        if not moves:
            print("  (no migration steps needed — already in F113 shape)")
            print()
            continue
        applied, errors = execute_moves(moves, dry_run)
        total_applied += applied
        total_errors += errors
        print()

    print("=" * 78)
    if dry_run:
        print(f"END Phase B {mode}. {total_applied} operations planned, {total_errors} errors.")
        print("Re-run with --execute to apply changes.")
    else:
        print(f"END Phase B {mode}. {total_applied} operations applied, {total_errors} errors.")
    print("=" * 78)

    return 0 if total_errors == 0 else 1


# Constants set after arg-parse.
VAULT_ROOT: Path
NAME_W: int = 30  # width for the anchor-name column in the report


def main() -> int:
    global VAULT_ROOT, NAME_W

    parser = argparse.ArgumentParser(
        description="F113 Phase 1b migration script — Phase A discovery + Phase B per-anchor restructure."
    )
    parser.add_argument(
        "--phase", choices=("A", "B"), default="A",
        help="A = read-only discovery report; B = per-anchor restructure (default dry-run).",
    )
    parser.add_argument(
        "--vault-root", type=Path, default=Path.home() / "ob" / "kmr",
        help="Vault root (default: ~/ob/kmr)",
    )
    parser.add_argument(
        "--anchor", default=None,
        help="(Phase B) scope to one anchor by name (e.g. CAE).",
    )
    parser.add_argument(
        "--execute", action="store_true",
        help="(Phase B) actually apply moves; default is dry-run.",
    )
    args = parser.parse_args()

    VAULT_ROOT = args.vault_root.resolve()
    if not VAULT_ROOT.is_dir():
        print(f"error: vault root {VAULT_ROOT} is not a directory", file=sys.stderr)
        return 2

    print(f"Walking vault: {VAULT_ROOT}", file=sys.stderr)
    anchor_paths = find_anchors(VAULT_ROOT)
    print(f"  found {len(anchor_paths)} anchors", file=sys.stderr)

    if not anchor_paths:
        print("error: no anchors found (expected `.anchor` marker files)", file=sys.stderr)
        return 1

    NAME_W = max(NAME_W, max(len(p.name) for p in anchor_paths) + 2)

    print(f"Classifying anchors...", file=sys.stderr)
    inventories = [classify_anchor(p) for p in anchor_paths]

    if args.phase == "A":
        report(inventories)
        return 0
    else:  # Phase B
        return run_phase_b(inventories, args.anchor, dry_run=not args.execute)


if __name__ == "__main__":
    sys.exit(main())
