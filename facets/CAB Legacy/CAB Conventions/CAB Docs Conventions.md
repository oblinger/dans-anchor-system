# CAB Docs Conventions

The anchor's docs folders contain private planning and design documentation (NOT published). In Gen-3 these are **root-level folders** — `{NAME} Architecture/`, `{NAME} Design/`, `{NAME} Track/`, `{NAME} User Docs/`, `{NAME} Dev Docs/` — with **no** `{NAME} Docs/` container. See also [[CAB Docs]] for the structural description.

## Standard Documents

| File | Purpose | Format |
|------|---------|--------|
| `{NAME} PRD.md` | Product requirements, design specs | Prose |
| `{NAME} Roadmap.md` | Milestones and phases | See [[CAB Roadmap]] |
| `{NAME} Backlog.md` | Deferred work, low-priority ideas | See [[CAB Backlog]] |
| `{NAME} Icebox.md` | Cold-storage / someday-maybe (optional) | See [[CAB Icebox]] |
| `{NAME} Inbox.md` | Raw content to process | See [[CAB Inbox]] |
| `{NAME} Features/` | Feature specs | See [[CAB Features]] |
| `{NAME} Files.md` | Single-page codebase map | See [[CAB Files]] |

Not all files are required — create what's useful.

## Roadmap Format
Roadmaps contain only high-level descriptions of what needs to be done. Detailed content belongs elsewhere:
- **Detailed discussion** — Put in a design document, reference from roadmap
- **Detailed task lists** — Put in Backlog, reference from roadmap

Roadmaps use checkboxes in headings to track milestone completion:

```markdown
## Phase 1: Foundation

### [ ] M1.1 - Repository Setup

Create the repository with initial structure.

**Deliverables**:
- [ ] Git repository initialized
- [ ] Directory structure created
- [ ] pyproject.toml configured

### [x] M1.2 - Basic Configuration

Completed milestone example.
```

Key conventions:
- **PHASES** — H2 headings group related milestones
- **MILESTONES** — H3 headings with `[ ]` or `[x]` checkbox, numbered (M1.1, M1.2, etc.)
- **DELIVERABLES** — Bullet lists with checkboxes under each milestone

## Handling Milestone Deferrals
When a milestone needs to be deferred to a later phase:

1. **Mark the deferred item** with `[~]` and add "(Deferred - see Mx.y)" to the title:
   ```markdown
   ### [~] M1.11 - Documentation Sync (Deferred - see M3.14)
   ```

2. **Add a revisit milestone** at the end of the target milestone/phase:
   ```markdown
   ### [ ] M3.14 - Revisit: M1.11 Documentation Sync
   ```

3. **Cross-reference both directions**:
   - The deferred item points to where it will be revisited
   - The revisit item links back to the original deferred milestone

# BRIEF

- **This file is the convention spec for the anchor's private planning docs** (Gen-3 root-level folders — no `{NAME} Docs/` container). It defines the standard documents an anchor's docs folders MAY carry (PRD, Roadmap, Backlog, Icebox, Inbox, Features, Files) and the format conventions for roadmap-specific structures (phases, milestones, deliverables, deferrals).
- **NOT for** structural-shape facts about the docs folders themselves (which files are required, where each folder sits in the anchor tree) — that lives in [[CAB Docs]] / [[CAB Base]]. NOT for facet-specific format details (Backlog horizons, Roadmap schema, Feature lifecycle) — those live in their own `CAB <Facet>.md` files and are linked from the Standard Documents table.
- **Inclusion test:** a thing belongs here if it is a cross-document convention that spans multiple docs-folder files (e.g. the roadmap milestone/deliverable checkbox pattern, the deferral protocol). Single-facet rules go in the facet spec; whole-anchor wiring goes in [[CAB Docs]].
- **Linking convention:** the Standard Documents table is a dispatch surface — each row points to the canonical facet spec via wiki-link in the Format column. Don't inline facet rules in the Purpose column; keep that one phrase.
- **Load-bearing constraints:** the roadmap milestone numbering (`M<phase>.<n>`) and checkbox markers (`[ ]` / `[x]` / `[~]`) are referenced by tooling and by feature docs — don't change the syntax casually. The deferral protocol's bidirectional cross-reference is the audit invariant.
- **Don't pile here:** anchor-local conventions ("how WP organizes its backlog") belong in `{NAME} Decisions.md` or the anchor's own Brief, not in this CAB-wide spec.
