---
description: "/ask — the clean skill for asking you questions, formatted so you can always answer from what's written."
---
:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[ASG]] → [ASG Query](hook://p/ASG%20Query)
# /ask — user guide

**Full internals & design:** [[DAS Ask]]   ·   **Runtime spec:** [[skills/ask/SKILL.md\|SKILL.md]]

`/ask` is how an agent asks you a question — and the one promise it makes is that **every question is answerable from what's written**, without opening anything else.

## What it's for

Whenever an agent hits a decision it can't make alone, it routes through `/ask`. The skill turns that decision into a clear question in front of you, with options and a recommendation, and captures your answer. It replaces the old `/ask` — same purpose, far less machinery.

## The promise — answerable questions only

The one rule: **you can answer every `/ask` question from what's written.** A question names a concrete decision (or a concrete thing to check) and carries the options.

- ✅ *"Frontmatter on design docs — YAML or body-only? (A) YAML (B) body-only. Rec: Strong (A)."*
- ❌ *"Is F115 verified?"* / *"Did this work?"* — you can't act on these from the text. If the agent needs you to test something, it spells out exactly what to run and what to look for.

If the agent can figure something out (especially when it's cheap to reverse), it decides and tells you — it doesn't park a non-question on you.

## What you'll see

Each question comes in five pieces — a short title, one or two lines of context, labeled options `(A)/(B)/(C)`, and a **Recommendation** (`Strong` / `lean` / `None — why`). Load-bearing (sticky / hard-to-reverse) choices are flagged so you know which deserve a careful look.

Where they land:

- **In the document the question is about** — a feature doc / PRD / spec gets its questions in that doc's `## Open Questions`.
- **In the anchor's `{slug} queries.md`** — for cross-cutting questions not tied to one document.

A single question, while you're engaged, is asked **inline in chat**. Two or more (or when you're not actively engaged) get **written down and the file opened** for you, with a one-line summary in chat.

## Answering

Answer in chat with the shorthand: `Q2: B`, `Q2: B — because …`, or plain prose. Once you name a doc ("in F167"), later bare `Q4: …` targets that doc until you switch. The agent records your choice under `## Resolved` and proceeds.
