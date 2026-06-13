---
description: "The **`/ask` skill** is the universal asking subroutine."
---
# /Ask
[[SKL ask-inline]] 

The **`/ask` skill** is the universal asking subroutine. Whenever an agent in any anchor has a question for you, it routes through `/ask` — which formats the question, picks the right surface (a feature doc, or directly in the anchor's `{NAME} ask.md` § `## Questions`), maintains the vault-level Agent Status dashboard at `[[Q]]`, and (if you're engaging with the work right now) opens the file at you.

`/ask` replaces the old `ask-questions` discipline. The behavior is the same; the difference is structural — instead of "every skill should remember to follow this discipline" (which broke), parent skills *invoke* `/ask` as a subroutine, and the runbook (including the glance step) executes uniformly.


## What you'll see

**The vault-level Agent Status dashboard at `[[Q]]`** — `~/ob/kmr/Q.md` — lists every anchor with active questions or ready work. Bind a keyboard shortcut to it; one press surfaces everything across all your agents.

The H1 banner counts anchors needing user input (Questions: N) and anchors with agent-actionable work (Ready: M). Below the banner, each anchor appears as a per-anchor section — H1 banner (with the slug as a wiki-link to the anchor's ask page via `[[Q#NAME Triage|NAME]]`), the workflow-state H2s, and one bullet per item. Most-recently-touched anchors at the top.

```
# Agent Status   -   Questions: 2    Ready: 1


# [U+A]  [[Q#CAE Triage|CAE]] Triage  -  Questions 2    Verify 1   |   Active 1    Ready 1   |   Now 2    Next 1    Later 1    Icebox 0
## Active
- **[Active]** [[F001 — Cron Syntax]] — Cron expressions for recurring task schedules.
## Ready
- **[Ready]** [[F003 — Retry Backoff Polish]] — Tune exponential-backoff caps after user feedback.
## Now
- **[4 Questions]** [[F002 Task Groups]] — Rendering of task groups.
- **[Verify]** [[F007 — Webhook Notifications]] — Webhook fires on task completion.
## Next
- **[5 Questions]** [[F004 Priority Levels]] — 2 pending Qs.
```

When an anchor has zero items anywhere (TAG `[]`), it disappears from the page automatically. When a new question or Ready item lands, the anchor reappears (move-to-front).

If `Q.md` grows too large overall, individual per-anchor sections collapse to **just the H1-equivalent line** (which contains the link to Triage). No partial paste — either the whole body, or just the link.

**Inside each anchor**, questions live in two places:

- **Document-attached** — questions about a specific feature/PRD/design doc live in that doc's `## Open Questions` H2 (directly below the H1).
- **Anchor-level** — cross-cutting questions (planning, agent-raised, no specific doc) are authored directly in `{NAME} ask.md` § `## Questions`, numbered `Q1`, `Q2`, ... There is no separate questions file.


## How agents invoke it

You don't usually invoke `/ask` directly. Parent skills do — `/feature`, `/code plan`, `/groom`, `/triage`, `/crank`, `/fortify` — whenever they need decisions from you.

Direct invocation works too:

```
/ask [--doc <path>] <question1> [<question2> ...]
```

- `--doc <path>` — document-attached mode; questions go in that doc's `## Open Questions` block.
- No flag — anchor-level mode; questions are authored directly in the anchor's `{NAME} ask.md` § `## Questions`.


## Question format

Every question carries an explicit recommendation strength so you can scan many at once and rubber-stamp the high-confidence ones.

```
- **Q3 — Short question name** — context, why we're asking.
  - (A) Option A — short description.
  - (B) Option B — short description.
  - **Recommendation:** Strong (B). One-line reason.
```

| Strength | What you should do |
|---|---|
| **Strong** | Rubber-stamp unless you disagree. |
| **Lean** | Quick read; consider before accepting. |
| **None** | Genuine uncertainty; apply your judgment. |


## How you respond

Same shorthand as `/triage`:

| You say | Agent does |
|---|---|
| `F005 Q4: yes` | Resolves Q4 in F5's feature doc with answer "yes". Moves the question to `### Resolved`. |
| `Q4: yes` (after sticky context "I'm in F5 now") | Same as above. |
| `{NAME} Q3: option A, because...` | Resolves the anchor-level Q3 authored in the anchor's `{NAME} ask.md` § `## Questions`. |


## Active vs Parking mode

**Active mode** — you're engaging right now ("let's design X", "let's discuss"). The agent **glances** the file (opens it at you).

**Parking mode** — you've explicitly deferred ("put it on the backlog", "for later"). The agent **does not glance**; the question still gets surfaced via the vault-level dashboard when you choose to engage.

Default when ambiguous is parking, since the cost of an unwanted glance (interrupting deferred work) is higher than the cost of a missed glance (you can re-engage by opening `[[Q]]`).


## Phase lifecycle of `## Open Questions` blocks

Applies to **feature docs** (anchor-level Qs in `{NAME} ask.md` use the same Q format but are a live drain — answered Qs move to `## Agent Resolutions` and the bullet is removed, with no phased `### Resolved` archive):

1. **Pending exists** — `## Open Questions` H2 sits below the H1; resolved questions accumulate in a `### Resolved` H3 holding pen.
2. **All resolved** — the `## Open Questions` H2 is deleted; resolved questions migrate down to a `## Resolved` H2 at the **bottom** (permanent archive).
3. **New question arises later** — the `## Open Questions` H2 is recreated below H1; new resolutions accumulate in the temporary `### Resolved` again until all are answered.


## When you'll notice this

- A keyboard shortcut opens `[[Q]]` and you see two anchors with TAG `[U+A]` and one with `[A]`, with the full body for each.
- The agent says "I've put 3 Qs in [[F012 — Foo]]" and opens the file at you — active mode.
- The agent says "I've parked the questions; see [[Q]]" without opening the file — parking mode.
- A backlog item shows the `**[3 Questions]**` bracket — that means the linked feature doc has 3 pending Qs in its `## Open Questions` block.


## Cross-references

- `[[Q#SKL Triage|SKL Triage]]` — sibling skill that surfaces what `/ask` writes.
- `[[Q]]` — the vault-level Agent Status dashboard, maintained by `/ask`.
