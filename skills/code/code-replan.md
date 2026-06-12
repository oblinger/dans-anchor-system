# Replanning Workflow

Triggered when requirements change, user feedback arrives, or a design gap is discovered during implementation. This is lightweight — it invokes `/code plan` steps selectively rather than restarting the full planning flow.

## When to Trigger

- User says "redesign", "replan", "the requirements changed"
- User feedback during implementation reveals a design gap
- A worker reports a design problem they can't resolve
- Implementation reveals the architecture doesn't support a needed capability
- New features are requested that don't fit the current design

## Steps

### 1. Absorb the Change

Read and understand the feedback, new requirements, or gap description. Identify what specifically changed or was discovered.

### 2. Identify Affected Documents

Determine which design documents need updates:

| Change Type | Likely Affected Documents |
|---|---|
| New/changed requirements | PRD, possibly UX + System Design + Roadmap |
| UX feedback | UX Design, possibly System Design |
| Architecture issue | System Design, possibly Roadmap |
| Scope change | PRD, Roadmap |
| New feature request | PRD, UX Design, System Design, Roadmap |
| Worker-reported gap | System Design or implementation spec |

### 3. Re-execute Relevant Steps

Run the affected `/code plan` steps for those documents:

- If PRD changed → re-run step 1 (PRD) for the changed sections
- If UX changed → re-run step 3 (UX Design)
- If architecture changed → re-run step 4 (System Design)
- If file structure changed → re-run step 5 (Files) and step 6 (Module Descriptions)
- Always run a consistency pass after changes (cascade rule applies)

### 4. Update the Roadmap

If milestones changed:
- Re-run `/code plan` step 7 (Roadmap) for affected milestones
- Re-order if dependencies shifted
- Mark any in-progress work that is invalidated

### 5. Return to Execution

Resume `/code execute` with the updated design. If workers are in flight on invalidated work, notify them of the change.

## Cascade Rule

Updating any document may invalidate others:
- PRD change → check UX Design and System Design
- UX change → check System Design
- System Design change → check Roadmap and implementation specs
- Always trace affected user stories through all documents
