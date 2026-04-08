# Architect

Orchestrate the architecture phase — from system design to implementation-ready roadmap. Dispatches to individual architecture steps in order.

## Pipeline

| Step | Action | File | What it produces |
|------|--------|------|-----------------|
| 1 | System Design | [[code-system-design]] | Architecture doc: components, APIs, data models |
| 2 | Modules | [[code-modules]] | Files doc + per-module docs with interfaces |
| 3 | Test Plan | [[code-test-plan]] | Test design: areas, scaffolds, categories |
| 4 | Roadmap | [[code-roadmap]] | Ordered milestones with acceptance criteria |
| 5 | Audit | [[code-arch-audit]] | Completeness check before implementation |

## Consistency Checks

After steps 1-3, run consistency checks:
- Trace every PRD user story through UX Design and System Design — is every capability designed and architecturally supported?
- Check terminology — same words for same concepts across all documents
- Check for contradictions — does any document promise something another cannot deliver?
- Are all open questions captured? Are any blocking?

Multiple passes are normal. Each pass tightens the design.

**Cascade rule:** Updating any document may invalidate others. When a decision changes the UX, check System Design. When a constraint changes in the PRD, check both UX and System Design.

## Document Step

After the roadmap, create the documentation dispatch tree — placeholder pages that link the anchor's top-level folder down through every documentation page. Starting from `{NAME}.md`, a reader should reach any markdown file by following links.

## Completion

Architecture is complete when:
1. All 5 pipeline steps pass
2. Open questions are resolved or deferred
3. User has approved the design (file tree, module specs, API overviews)
4. The roadmap has a clear first milestone ready for implementation
5. The documentation dispatch tree is navigable

Transition to `/code mint` when the roadmap is ready.

## Dispatch

On `/code architect`: read each step file in order and execute its workflow. Skip steps whose output already exists and is current, unless the user requests a re-run.
