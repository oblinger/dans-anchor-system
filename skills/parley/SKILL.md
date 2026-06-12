---
name: parley
description: >
  Structured discussion — talk through a topic, capture decisions, track next steps.
  Use when the user says: "parley", "let's discuss", "let's talk about",
  "I want to think through", "let's figure out", "discuss this".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Parley

Skill spec for `/parley` — structured topic discussion that lands a dated parley doc, evolves Open Questions / Next Steps / Discussion through the conversation, and weaves outcomes back into the anchor (or graduates to a feature) at close.

Structured discussion on a topic. Creates a dated document, captures the back-and-forth, records decisions, and tracks next steps until all materials are woven into their proper locations.

A parley may evolve into a `/feature` — if so, move or copy the document to the Features folder and continue there.

## Runbook

### 1. Find or create the Parley folder

Parley documents live in `{NAME} Docs/{NAME} Plan/{NAME} Parley/`.

**First time for this anchor:** Create the folder and its dispatch page:
- Create `{NAME} Parley/` inside `{NAME} Plan/`
- Create `{NAME} Parley.md` dispatch page inside it with a standard dispatch table
- Wire the Parley folder into the Plan dispatch page (add a row linking to it)

**If the folder already exists:** Just create the new document inside it.

### 2. Create the parley document

Create a dated file: `{NAME} Parley/YYYY-MM-DD <Topic>.md`

**Initial structure:**

```markdown
---
description: <one-line topic summary>
status: open
---

# <Topic>

## Next Steps

*(none yet)*

## Open Questions

*(none yet)*

## Discussion

### User Input

<paste the user's initial input here, mostly raw>

### <date> — <first discussion point>

<back and forth goes here>
```

### 3. Wire it in

- Add the new document to the `{NAME} Parley.md` dispatch table
- The dispatch page lists all parley documents, newest first

### 4. Discuss

Go back and forth with the user. As the discussion progresses:

- **Open Questions** — add questions as they arise, remove them as they're resolved
- **Next Steps** — add action items as decisions are made
- **Discussion** — append new H3 sections for each topic or sub-discussion, dated

### 5. After each round

Update the Next Steps and Open Questions sections at the top of the document. These are the living summary — anyone glancing at the document should immediately see what's unresolved and what needs doing.

### 6. Execute next steps

When the discussion reaches a natural stopping point, the agent is responsible for carrying out the next steps:

- Weave generated materials into their proper locations (skill files, spec docs, anchor pages, etc.)
- Create feature documents if a feature emerged from the discussion
- Update any referenced documentation
- Post to stat if the work is trackable

### 7. Close

A parley is **open** until:
- [ ] All Open Questions are resolved
- [ ] All Next Steps are completed
- [ ] All materials have been woven into their proper locations

When all three are true, change the frontmatter to `status: closed` and update stat.

## Converting to a Feature

If a parley evolves into a feature:
1. Move the file to `{NAME} Features/` and rename to `YYYY-MM-DD <Feature Name>.md`
2. Add the standard feature sections (Proposed Design, Status)
3. Continue with `/feature` lifecycle
4. Update the Parley dispatch page to note the move: `→ moved to [[YYYY-MM-DD Feature Name]]`
