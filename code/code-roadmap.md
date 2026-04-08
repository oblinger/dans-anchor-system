# Roadmap

Build the ordered implementation plan. Create `{NAME} Roadmap.md` following the CAB Roadmap spec. The roadmap is the work queue for implementation.

## When to Use

After System Design, Module Docs, and Test Plan are complete. Run when the implementation order needs to be defined or revised.

## Workflow

### 1. Review All Design Docs

Read PRD, System Design, Files, and Module Docs to understand the full scope of work. Every capability should trace to at least one roadmap item.

### 2. Write the Roadmap

Create or update `{NAME} Roadmap.md`:

- Break work into milestones ordered by dependency (foundational first)
- Each milestone has clear acceptance criteria
- Identify which milestones can be parallelized
- The roadmap is the work queue for `/code mint`

### 3. Validate

After writing or updating the roadmap:

1. **Check task order** — are tasks in logical order? Do prerequisites come first? Are there dependency conflicts?
2. **Check for missing work** — scan Notes, Todo, and Backlog documents for work discussed but not reflected in the roadmap. Add any missing items.
3. **Surface open questions** — check `{NAME} Backlog.md`, `{NAME} Open Questions.md`, and other docs for unresolved questions. Each should either block a milestone or be deferred.
4. **Run validation script** — if `roadmap_check.py` is available:
   ```bash
   python ~/ob/kmr/prj/personal-curation/roadmap_check.py "{NAME} Roadmap.md"
   ```

### 4. Sufficiency Check

Before moving to implementation, verify:
- Could a worker start building from these documents without blocking questions?
- Do goals, stories, and constraints tell a consistent story?
- Is there a clear first milestone?
- Open questions are empty or all remaining are deferred
- User has reviewed and approved the design
