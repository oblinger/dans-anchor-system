# CAB Roadmap

The `{NAME} Roadmap.md` file organizes work into milestones for incremental, testable implementation. It lives in the `{NAME} Docs/` folder.

## Roadmap Structure

A roadmap is organized by **milestones** (H2 headings), each containing **deliverable items** as checkbox lists:

```markdown
## [ ] M1 — Foundation

Initial setup and core functionality.

- [ ] Create repository structure
- [ ] Set up development environment
- [ ] Implement core feature

---

## [ ] M2 — Next Milestone

Description of this milestone.

- [ ] Task 1
- [ ] Task 2

---

## Later

Features planned but not yet scheduled.

- [ ] Future feature 1
- [ ] Future feature 2
```

## Checkbox Format

All actionable items must have checkboxes:
- `[ ]` — Not started
- `[x]` — Completed
- `[~]` — Deferred (must have revisit reference)

## Deferred Items

When an item is deferred with `[~]`:

1. **Mark the deferred item** with explanation:
   `[~] Documentation Sync (Deferred - see M3.14)`

2. **Add a revisit milestone** in the target phase:
   `[ ] M3.14 - Revisit: M1.11 Documentation Sync`

3. **Cross-reference both directions** — the validation script checks this.

## Validation

A validation script checks roadmap structure:

```bash
python roadmap_check.py "{NAME} Roadmap.md"
```

It reports:
- Lines missing checkboxes where expected
- Deferred items `[~]` without "Deferred - see" reference
- Deferred items without corresponding revisit milestone
- Invalid checkbox format

Roadmap validation is part of the `/d-plan` workflow (step 7).
