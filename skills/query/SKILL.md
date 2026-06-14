---
name: query
description: >
  Ask the user one or more questions and capture the answers. The clean asking
  skill: format each question as a self-contained, ANSWERABLE item (title +
  context + labeled options + a recommendation), write it to the right surface —
  the document the question is about, or the anchor's `{NAME} Query.md` — and
  glance it so the user can answer. A single question while the user is engaged
  may be asked inline in chat. Invoke whenever an agent needs a decision from the
  user. Slash-only — "query" is not a spoken trigger.
tools: Read, Write, Edit, Bash, Glob
user_invocable: true
---

# /query — ask the user questions

`/query` is how an agent asks the user something. Its whole job: turn a decision the agent can't make alone into a clear, answerable question in front of the user, and capture the answer. Nothing more — no dashboards, no render pipeline, no triage coupling (that scope creep is what rotted the old `/ask`).

## The one rule — every question must be ANSWERABLE

A question is valid only if **the user can answer it from what's written**, without going to read anything else. It names a concrete decision (or a concrete thing to check) and carries the options.

- ✅ "Frontmatter on design docs — YAML or body-only? (A) YAML (B) body-only. Rec: Strong (A) — matches every real doc."
- ✅ "Should `{NAME} Query.md` live at the anchor root or under `{NAME} Track/`? (A) root (B) Track/. Rec: Lean (A)."
- ❌ "Is F115 verified?" / "Did this work?" / "Should I keep going?" — the user cannot act on these from the text alone. If the agent means *"run X and tell me the result,"* it must spell out exactly what to run and what to look for.

If a question can't be made answerable, it is not a query: the agent should **decide it** (reversible → guess and record) or **do the work** that resolves it. Never park an unanswerable "question" on the user.

## Question format (five pieces)

```
- **Q<n> — <short title>** — one-line subject.
  - Context: 1–2 sentences — what's being decided and why it matters (self-contained).
  - (A) <option> — <consequence>.
  - (B) <option> — <consequence>.
  - **Recommendation:** Strong (A) | Lean (A) | None — <one-line reason>.
```

- **Options** are labeled `(A)` / `(B)` / `(C)`, one per line, each a real distinct choice.
- **Recommendation** is honest: `Strong`/`Lean` when the agent has a basis; `None — <why>` only when it genuinely doesn't. (`None` is the user's actionable inbox — don't fake a Lean, don't hide a Strong.)
- Flag **load-bearing** when the choice is sticky / expensive to reverse, so the user knows it deserves attention.
- Q-numbers are stable per surface; resolved numbers are never reused.

## Two surfaces — nowhere else

1. **The document the question is about** — when the question concerns a specific feature doc / PRD / spec, write it in that doc's `## Open Questions` H2 (directly below the H1).
2. **The anchor's `{NAME} Query.md`** — for anchor-level / cross-cutting questions not tied to one document. Create it if absent (frontmatter + `# {NAME} Query` H1 + the question list).

Chat is a dispatch *view*, never the store. A bare "Q12?" in chat with no written home is invalid — the user can't return to it.

## Threshold — one inline, two-or-more written

- **Exactly one question AND the user is engaging right now** → ask it inline in chat with all five pieces. (It still has a written home if a relevant doc exists; the inline ask is the dispatch.)
- **Two or more, OR the user isn't actively engaged** → write them to the surface, **glance** it (`open "<file>"`), and name them in one line in chat: the topics + which one is load-bearing.

## Runbook

1. **Collect** the question(s) the agent needs answered. Drop any that the agent can decide itself (reversible → decide + record) or resolve by doing the work.
2. **Make each answerable** (the one rule). Rewrite vague ones into concrete decisions/tests, or discard.
3. **Pick the surface** per question: its home document, else `{NAME} Query.md`.
4. **Write** each in the five-piece format, assigning the next stable `Q<n>` on that surface.
5. **Surface:** one + engaged → inline; otherwise glance the file + one-line chat summary.
6. **On answer** (`Q2: B`, `Q2: B because …`, or free text): record the resolution at the question's home — move it under `## Resolved` with the chosen option + a one-line note — and proceed. If a relevant section needs updating to reflect the decision, update it in the same step.

## Answering shorthand

The user answers in chat: `Q2: B`, `Q2: B — because …`, or plain prose. Sticky context: once the user names a doc ("in F167"), later bare `Q4: …` targets that doc until they switch.

## What `/query` does NOT do

- No `Q.md` dashboard maintenance, no render→audit→glance invariant, no `[Verify]`/backlog surfacing — those belong to `/triage`. `/query` only asks and records.
- It does not invent work or auto-answer — it surfaces genuine decisions and captures the user's call.
