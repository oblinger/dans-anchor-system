# CAB Docs Conventions

The `{NAME} Docs/` folder contains private planning and design documentation (NOT published). See also [[CAB Docs]] for the structural description.

## Standard Documents

| File | Purpose | Format |
|------|---------|--------|
| `{NAME} PRD.md` | Product requirements, design specs | Prose |
| `{NAME} Roadmap.md` | Milestones and phases | See [[CAB Roadmap]] |
| `{NAME} Backlog.md` | Deferred work, low-priority ideas | See [[CAB Backlog]] |
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
