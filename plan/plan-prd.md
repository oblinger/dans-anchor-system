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
- **User Stories** — numbered (US-1, US-2, ...), each with enough detail that a worker could build against it
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
