# System Design

Design the technical architecture. Create `{NAME} System Design.md` following the CAB System Design spec.

## When to Use

After UX Design is written and system conversation decisions are captured. Run when the architecture needs to be specified or redesigned.

## Workflow

### 1. Review Inputs

Read the PRD (goals, constraints), UX Design (interaction model, commands), and any system conversation notes. The architecture must support every user story and respect every constraint.

### 2. Write the System Design

Create or update `{NAME} System Design.md` with:

- **Component boundaries and data flow** — what the major pieces are and how data moves between them
- **Module decomposition with responsibilities** — which component owns which concern
- **APIs and protocols** — interfaces between components, external APIs consumed
- **Data models and storage** — what is persisted, where, and in what format
- **Infrastructure decisions** — language, runtime, hosting, build system
- **Monitoring, failure handling, and configuration tiers** — how the system reports health and recovers from errors
- **Key design decisions with rationale** — in a Decisions section, document choices and why

### 3. Specification Only

The System Design doc is specification only — current design, not history. Rationale for contested decisions belongs in `{NAME} Discussion.md`.

### 4. Consistency Check

After writing, run these checks:
- Trace every PRD user story through UX Design and System Design — is every capability designed and architecturally supported?
- Check terminology — same words for same concepts across all documents
- Check for contradictions — does any document promise something another cannot deliver
- Are all open questions captured? Are any blocking?

Multiple passes are normal. Each pass tightens the design.

### 5. Cascade Rule

Updating any document may invalidate others. When a decision changes the UX, check System Design. When a constraint changes in the PRD, check both UX and System Design.
