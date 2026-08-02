# RULESET R-roadmap
include::
where:: `file:{anchor}/**/* Roadmap.md`
description:: facet spec for the project sequencing-design doc — milestones, shapes, and numbering

Ruleset for this facet — spec: [[DAS Roadmap]] (extracted from the spec 2026-07-12). Adopted via `R-facet` umbrella.

### RULE R-roadmap-01 — Location is `{slug} Design/{slug} Roadmap.md` (checked)

The roadmap lives at `{slug} Design/{slug} Roadmap.md`. Not under Track (legacy), not at anchor root.

**Check pattern:** `ls "{anchor}/{slug} Design/{slug} Roadmap.md"` exists; no `{slug} Track/{slug} Roadmap.md` lingers alongside.

**Why:** Roadmap is sequencing-design; lives with the design facets. The 2026-06-10 restructure moved it from Track.

### RULE R-roadmap-02 — Body-only, no YAML frontmatter (checked)
check:: regex_present ^# [^-]

The first non-blank line is `# {slug} Roadmap` (H1). No `---` YAML block precedes.

**Check pattern:** first non-blank line starts with `# `; does not start with `---`.

**Why:** matches the vault-wide body-only convention. Frontmatter is invisible in Obsidian read view and drifts silently.

### RULE R-roadmap-03 — Every milestone heading carries a checkbox in its title (checked)

Every H1 marked as a top milestone, H2 marked as a milestone point, and H3 marked as a sub-point carries `[x]`, `[ ]`, or `[~]` in the heading text immediately after the H-marker.

**Check pattern:** for headings matching `^# Milestone \d+` (H1), `^## M\d+\.\d+` (H2), `^### M\d+\.\d+\w?` (H3), assert the heading text starts with `[x] `, `[ ] `, or `[~] `.

**Why:** the checkbox is the grazer's primary read of milestone state. Missing checkbox = milestone state is invisible to a quick scan.

### RULE R-roadmap-04 — Milestones with checkbox `[x]` or `[~]` carry a `**Status**:` line (sampled)
check:: milestone_status_line

Within ~5 lines of the milestone heading, a `**Status**:` line summarizes the state — *"Complete — N tests passing"* / *"Core complete — …"* / *"In progress — …"*. Required for `[x]` and `[~]`; recommended for `[ ]` once work begins.

**Check pattern:** for each `[x]` or `[~]` milestone H1/H2, scan the next 10 lines for `^\*\*Status\*\*:`; flag if absent.

**Why:** the checkbox gives binary state; the Status line gives the narrative + quantitative anchor (test counts, PR refs) that makes "Complete" mean something specific.

### RULE R-roadmap-05 — Deferred items (`[~]`) have matching revisit cross-references (checked)

Every `[~]` milestone or item includes `(Deferred - see M<n>.<m>)` in its heading or first body line. The referenced milestone in turn contains a `Revisit: M<source>` entry.

**Check pattern:** for each `[~]` milestone, extract the cited revisit target; verify the target exists and contains a Revisit entry pointing back at the source.

**Why:** one-way deferral pointers rot — the deferred item disappears from view because the revisit milestone doesn't surface it. Paired cross-refs keep both ends discoverable.

### RULE R-roadmap-06 — Shape is consistent across the file (stated)

Within a single roadmap file, all milestones use the same shape (Shape A — milestone-as-feature-group OR Shape B — milestone-as-task-checklist). Don't mix `[[F<NNN>]]` wiki-link bullets in one milestone with raw checkbox tasks in the next.

**Check pattern:** scan the body of each milestone; classify as Shape A (predominantly `[[F\d+`-prefixed bullets) or Shape B (predominantly raw checkbox tasks); assert all classifications match.

**Why:** mixed shapes confuse the reader about how to interpret milestone progress (is it "all features done" or "all tasks checked"?). Pick one shape per project; transitions between shapes are explicit (a marker note), not gradual mixing.

### RULE R-roadmap-07 — Milestone numbers are monotonic-forever (stated)

Milestone numbers are never recycled within a level. A deprecated `M1.4` stays at M1.4 (struck through or `[~]` deferred); new work takes the next unused number (`M1.15`, `M1.4b`, etc.).

**Check pattern:** git history — flag instances where a milestone-number heading was deleted and the same number reappears later with different content.

**Why:** stable identifiers across cross-references (e.g., "see M1.11", "Deferred - see M3.14") and external citations (commit messages, feature docs). Recycling breaks every back-reference silently.

### RULE R-roadmap-09 — Milestones use `M-<Name>` form, not pure numbers (checked)

Top-level milestones are named with a short acronym or word: `M-Auth`, `M-WAL`, `M-Core`. Pure-number forms (`M1`, `M2`) are legacy-only — accepted in existing roadmaps but new milestones use named form.

**Check pattern:** for each H2/H3 milestone heading, assert the milestone identifier matches `^M-[A-Za-z][A-Za-z0-9]{2,}(\.[0-9]+)*(-\w+)?$` (named form). Pure-numbered forms accepted only if the roadmap file carries a `<!-- legacy-numbered-milestones -->` marker comment.

**Why (provenance):** numbering long-running roadmaps creates renumbering nightmare on insertion. Named milestones don't have top-level ordering; you can add `M-Notifications` anywhere without touching anything else. Names are grep-able semantic anchors. Discussed and agreed in [[F144 — Completed Roadmap + named milestones]].

### RULE R-roadmap-10 — Feature title encodes M-position when commissioned from roadmap (checked)

When a feature is commissioned from a roadmap milestone sub-item, the feature doc's filename and title use:

```
F<NNN> — M-<Name>.<position>: <Title from Roadmap entry>
```

Example: `F118 — M-CLI.3.5: Implement CLI Core Statements.md`. The roadmap entry gets a `[F118]` marker (or full wiki-link) added after the bullet to point at the feature doc.

**Check pattern:** for each feature doc filename matching `F\d+ — M-`, assert the format matches `F\d+ — M-[A-Za-z][A-Za-z0-9]+(\.\d+)*: .+\.md`. For each roadmap sub-item that has a `[F\d+]` marker, assert a matching feature doc exists.

**Why (provenance):** F-numbers stay universal (monotonic-forever, never renamed). Encoding M-position in the title gives bi-directional discoverability without rename-cost. A reader on the feature doc sees `M-CLI.3.5` in the title and knows the roadmap origin; a reader on the roadmap clicks `[F118]` to reach the feature doc. Discussed and agreed in [[F144 — Completed Roadmap + named milestones]] Q1.

### RULE R-roadmap-11 — Roadmap is future + present only; completed milestones migrate to Completed Roadmap (stated)

The roadmap holds forward-looking work. Whole milestones — when `[x]` complete — migrate as units to `{slug} Design/{slug} Completed Roadmap.md` (per [[DAS Completed Roadmap]]).

**Check pattern:** roadmap should have at most one or two `[x]` top-level milestones at any time (they're awaiting migration). Stale `[x]` milestones accumulating in the roadmap = drift; flag for migration.

**Why (provenance):** long roadmaps mostly composed of completed work become hard to navigate. "Where are we now?" should be answerable by glancing at the top of the roadmap. ABIO Roadmap demonstrates the pain at scale. F145 will ship automation; until then, migration is manual.

### RULE R-roadmap-12 — Milestone names are unique within the roadmap (checked)

Every top-level milestone name (`M-<Name>`) appears at most once within a single `{slug} Roadmap.md`. The name is the milestone's stable identity — the key every sub-entry, backlog `R` task, and cross-reference resolves on — so a duplicate name is an ambiguous reference.

**Check pattern:** collect all top-level `M-<Name>` headings; assert no `<Name>` appears twice.

**Why:** identity is the name, not a stored ordinal (§ Names are identity; order is document position). A duplicate name means two milestones claim the same key, and every `R-<Name>` / `M-<Name>.<path>` reference becomes ambiguous. This uniqueness is the invariant the entire no-renumber / no-drift scheme depends on.

### RULE R-roadmap-08 — Section separator `### .` is used between milestones (stated)

After the last body item of each milestone, before the next `## ` H2, a `### .` (H3 with literal dot) serves as a visual closer.

**Check pattern:** for each H2 milestone, check that the preceding H2's body ends with a `### .` line within ~3 lines of the next H2.

**Why:** scrolling readers benefit from the visual closer to identify milestone boundaries without parsing content. Optional for very short milestones (one or two items) but encouraged.
