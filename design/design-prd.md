# PRD

Capture what the system is, what it does, and why. Create `{NAME} PRD.md` following the CAB PRD spec.

## When to Use

First planning step after the anchor exists. Run when starting a new project or when requirements need a full rewrite.

## Workflow

### 1. Gather Context

Read existing materials — README, CLAUDE.md, prior discussion, user input. Understand the problem space before writing.

### 2. Write the PRD

Create or update `{NAME} PRD.md` with these sections:

- **Overview** — what it does and why it needs to exist (two sentences)
- **Goals** — concrete, verifiable outcomes; explicit non-goals
- **User Stories** — numbered `US-<RID>-<N>` per anchor (e.g. `US-MUX-1`, `US-CAE-1`), each with enough detail that a worker could build against it. **Two forms** per [[CAB Stories]]:
    - **Inline (default)** — bullet under `## User Stories` in `{NAME} PRD.md`, one sentence each. Right for small PRDs whose stories compress cleanly.
    - **Extracted to Stories sub-facet** — when a story needs multi-paragraph rationale, acceptance criteria spelled out, mockups, or decision history. PRD migrates to folder form `{NAME} PRD/` containing `{NAME} PRD.md` + `{NAME} Stories.md` (dispatch index) + one file per story. Migration extracts ALL stories for consistency — never mix inline and extracted in the same PRD. See [[CAB Stories]] for the file shape and naming rules.
- **Design Constraints** — numbered (DC-1, DC-2, ...), each with rule AND reasoning
- **Prior Art** — existing tools, patterns, codebases to draw from or avoid

### 3. Fleshing-Out Checklist

Verify completeness by asking:

- Can you explain what this does and why in two sentences? If not, Overview is not clear.
- What is the smallest version that would be useful? Start there.
- For every goal: what would you cut with half the time? That reveals core vs. nice-to-have.
- Have you covered every role that interacts with the system — not just primary users?
- Could a worker read each story and start building without coming back to ask? If not, add detail.
- Do stories cover the full lifecycle — setup, daily use, error recovery, maintenance?
- For each constraint, have you explained reasoning, not just the rule?

### 4. Surface Open Questions

Any unresolved decisions go to `{NAME} Open Questions.md` tagged by urgency (Urgent / Soon / Deferred). Urgent questions are presented to the user immediately.
