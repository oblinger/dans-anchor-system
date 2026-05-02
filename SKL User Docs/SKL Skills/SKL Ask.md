# /Ask

The **`/ask` skill** is the universal asking subroutine. Whenever an agent in any anchor has a question for you, it routes through `/ask` — which formats the question, picks the right surface (a feature doc or the project's triage file), maintains the global Open Questions page at `[[Q]]`, and (if you're engaging with the work right now) opens the file at you.

`/ask` replaces the old `ask-questions` discipline. The behavior is the same; the difference is structural — instead of "every skill should remember to follow this discipline" (which broke), parent skills *invoke* `/ask` as a subroutine, and the runbook (including the glance step) executes uniformly.


## What you'll see

**The global page at `[[Q]]`** — `~/ob/kmr/Q.md` — lists every anchor in the vault that has questions waiting on you. Bind a keyboard shortcut to it; it's the one page that surfaces everything across all your agents.

```
# Open Questions   -   Anchors waiting: 3    À la carte: 1


## Anchors

- [[SKA Triage]] — 4 Qs (F10: 3, F14: 1)
- [[HA Triage]] — 5 Qs
- [[MUX Triage]] — 2 Qs


## À la carte

- **A1 — Adopt M-numbers across all anchors?** — context. **Recommendation:** Lean (B). reason.
```

When an anchor's pending-question count drops to zero, it disappears from the page automatically. When a new question lands, the anchor reappears.

**Inside each anchor**, questions live in two places:

- **Document-attached** — questions about a specific feature/PRD/design doc live in that doc's `## Open Questions` H2 (directly below the H1).
- **À la carte** — cross-cutting questions (planning, agent-raised, no specific doc) live in `{NAME} Triage.md` § `## À la carte`, numbered `A1`, `A2`, ...

The global page links to each anchor's `{NAME} Triage.md` so you can drill in.


## How agents invoke it

You don't usually invoke `/ask` directly. Parent skills do — `/feature`, `/code plan`, `/groom`, `/triage`, `/crank`, `/fortify` — whenever they need decisions from you.

Direct invocation works too:

```
/ask [--doc <path>] <question1> [<question2> ...]
```

- `--doc <path>` — document-attached mode; questions go in that doc's `## Open Questions` block.
- No flag — à la carte mode; questions go in the project's triage file.


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
| `F5 Q4: yes` | Resolves Q4 in F5's feature doc with answer "yes". Moves the question to `### Resolved`. |
| `Q4: yes` (after sticky context "I'm in F5 now") | Same as above. |
| `A2: option A, because...` | Resolves the à la carte A2 in the project's triage. |


## Active vs Parking mode

**Active mode** — you're engaging right now ("let's design X", "let's discuss"). The agent **glances** the file (opens it at you).

**Parking mode** — you've explicitly deferred ("put it on the backlog", "for later"). The agent **does not glance**; the question still gets surfaced via the global page when you choose to engage.

Default when ambiguous is parking, since the cost of an unwanted glance (interrupting deferred work) is higher than the cost of a missed glance (you can re-engage by opening `[[Q]]`).


## Phase lifecycle of `## Open Questions` blocks

A document with questions moves through three phases:

1. **Pending exists** — `## Open Questions` H2 sits below the H1; resolved questions accumulate in a `### Resolved` H3 holding pen.
2. **All resolved** — the `## Open Questions` H2 is deleted; resolved questions migrate down to a `## Resolved` H2 at the **bottom** of the doc (permanent archive).
3. **New question arises later** — the `## Open Questions` H2 is recreated below H1; new resolutions accumulate in the temporary `### Resolved` again until all are answered.


## When you'll notice this

- A keyboard shortcut opens `[[Q]]` and you see four anchors waiting on you with question counts.
- The agent says "I've put 3 Qs in [[F12 — Foo]]" and opens the file at you — active mode.
- The agent says "I've parked the questions; see [[Q]]" without opening the file — parking mode.
- A backlog item shows `→ [[Feature Doc]]` and `[Questions]` bracket — that's the link convention marking the item as blocked on user input.


## Cross-references

- `[[SKL Triage]]` — sibling skill that surfaces what `/ask` writes.
- `[[Q]]` — the global Open Questions page, maintained by `/ask`.
