# Open Questions

Surface, track, and resolve open questions throughout the development lifecycle. Questions live in multiple places — this skill defines how to find and process all of them.

## When to Use

Invoke `/code open-questions` when the user wants to work through unresolved questions. Also invoked automatically as part of planning and implementation loops.

## Where Questions Live

Questions are not centralized in one file — they appear in context:

| Location | What lives there |
|----------|-----------------|
| `{NAME} Open Questions.md` | General project questions — architecture, scope, approach |
| `{NAME} Backlog.md` — Open Questions section | Questions about specific backlog items |
| `{NAME} Backlog.md` — Verify section | Items the agent completed that need user confirmation |
| `{NAME} Features/{feature}.md` — Open Questions section | Questions about a specific feature |
| `{NAME} Discussion.md` | Extended reasoning — questions that triggered design discussions |

## Processing Order

When `/code open-questions` is invoked:

1. **`{NAME} Open Questions.md`** — process these first. These are the most important project-level questions.
2. **Backlog Open Questions** — if the main OQ doc is empty, move to questions embedded in backlog items.
3. **Backlog Verify items** — items the agent says are done but the user hasn't confirmed. Glance each one so the user can see it in context and confirm or reject.
4. **Feature doc questions** — open questions within individual feature specs.

For each question, **glance the document** where the question lives so the user sees it in context.

## Capturing

As the agent works through any phase, it captures questions where they belong:

- **Project-level question** (scope, architecture, approach) → `{NAME} Open Questions.md`
- **Question about a backlog item** → Open Questions section within that item in `{NAME} Backlog.md`
- **Question about a feature** → Open Questions section within that feature doc
- **"Is this fixed?"** → Verify section in `{NAME} Backlog.md`

Tag each by urgency:
- **Urgent** — ready to decide now, many downstream decisions depend on the answer
- **Soon** — will become urgent as work advances
- **Deferred** — safe to decide later

## Raising Urgent Questions

When an urgent question appears, the agent opens the file and presents the question immediately — stating alternatives, what depends on the answer, and what to consider.

Occasionally mention the count of **Soon** questions available, especially once the count exceeds five.

## Batch Resolution

The user initiates batch resolution when ready. The agent presents questions one at a time with alternatives and trade-offs. After each answer, cascade the decision.

## Backlog Item Lifecycle

Backlog items move through these states:

| State | Meaning |
|-------|---------|
| **Open** | Known issue or feature, not yet worked on |
| **Open Questions** | Item has unresolved questions — listed in the item's OQ section |
| **In Progress** | Currently being implemented (agent tracks this implicitly) |
| **Verify** | Agent says it's done — awaiting user confirmation |
| **Resolved** | User has confirmed the fix works |

**Key rule:** Never move an item directly from In Progress to Resolved. The agent marks items as **Verify** after implementation. Only the user moves items to Resolved — the user must see the result.

Verify items are processed as open questions — the implicit question is "is this actually fixed?"

## Cascading Decisions

After resolving a question, trace its impact:
- If it changes the PRD → check UX and System Design
- If it changes the UX → check System Design
- If it changes the System Design → check Roadmap and specs
- Update all affected documents before moving on

## Recording Discussions

When a question involves notable back-and-forth, create a dated section in `{NAME} Discussion.md`. Design docs stay specification-only; the discussion log captures the "why."
