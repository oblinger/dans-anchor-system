# Architecture Audit

Verify the architecture phase produced a complete, consistent set of documents. Three lint passes ensure nothing was missed.

## When to Use

After completing System Design, Module Docs, Test Plan, and Roadmap. Run as the final gate before `/code it`.

## Workflow

### Pass 1: Capability Coverage

For every user story in the PRD and every capability in the UX Design:
- Does at least one module in the System Design own it?
- Is there a roadmap milestone that delivers it?

Report any capability with no module owner or no roadmap item.

### Pass 2: Module Justification

For every module in the Files doc:
- Does it serve at least one capability from the PRD or UX?
- Is its responsibility clearly stated in its module doc?

Report any module with no clear purpose or no connection to a user-facing capability.

### Pass 3: Cross-Document Consistency

- Terminology: same words for same concepts across PRD, UX, System Design, Files, Module Docs, Roadmap
- Interfaces: every API referenced in one module doc is defined in the providing module doc
- Dependencies: every external dependency mentioned in System Design appears in the appropriate module docs

### Report

Produce a short summary:
- Pass 1: N capabilities checked, M gaps
- Pass 2: N modules checked, M unjustified
- Pass 3: N cross-references checked, M inconsistencies

List each issue with the affected documents. The user decides whether to fix before proceeding to implementation.
