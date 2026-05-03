---
description: anchor-level à la carte questions facet (agent-owned)
---
# CAB Questions

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Questions.md`


The Questions file is the per-anchor home for **à la carte** (slug-scoped, cross-cutting, agent-raised) questions that don't belong to any feature doc. It mirrors the `## Open Questions` block format used inside feature docs (per `[[ask]]`), but at the anchor scope.

Per F28, à la carte questions moved out of `{NAME} Triage.md § ## À la carte` into this dedicated facet file. The Triage file now carries just **one bullet line** directly under its H1, of the form `- **[N Questions]**  [[{NAME} Questions]]`, when there are pending à la carte Qs (omitted when empty).

The file is **agent-owned** — `/ask` writes new à la carte Qs here; resolutions move them to a `### Resolved` H3 inside `## Open Questions`, then (when the last pending Q resolves) migrate to a bottom `## Resolved` H2. Same Phase 1 / Phase 2 / Phase 3 lifecycle as a feature doc's `## Open Questions` block.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Questions.md`.

# Reference Example
---

```markdown
---
description: anchor-level à la carte questions (agent-owned)
---


# [[{NAME}]] Questions

## Open Questions

- **Q1 — short name** — context.
  - (A) Option A.
  - (B) Option B.
  - **Recommendation:** Lean (B). reason.

- **Q2 — another short name** — context.
  - **Recommendation:** Strong (yes). reason.

### Resolved

- **Q0 — earlier question** — **Resolution:** what was decided. Incorporated into <design / conversation>.
```

---


# Format Specification

## Location

`{NAME} Questions.md` lives in `{NAME} Docs/{NAME} Plan/`, alongside `{NAME} Triage.md`.

## H1

```
# [[{NAME}]] Questions
```

The wiki-link to the anchor is the only link in the H1. No counts, no banner — counts live on the Triage file's H1.

## Body

Identical to the `## Open Questions` block format used inside feature docs (per `[[ask]]`):

- `## Open Questions` H2 with the pending Q bullets.
- `### Resolved` H3 inside `## Open Questions` as the temporary holding pen for resolutions during an active question batch.
- When all pending Qs resolve (Phase 2 transition), delete `## Open Questions` and migrate accumulated resolved Qs to a `## Resolved` H2 at the **bottom** of the file (permanent archive).
- When a new à la carte Q arises later (Phase 3), recreate `## Open Questions` at the top.

## Q-numbering

À la carte Qs use `Q<n>` — same prefix as feature-attached Qs but in a per-anchor scope. Lowest unused integer in the file (across `## Open Questions` pending + `### Resolved` + bottom `## Resolved`). Numbers are stable references; never renumber. Same numbering policy as `[[CAB Backlog]]` § Numbering policy.

When referenced in conversation: `{NAME} Q3` (e.g., "SKA Q3"). The slug disambiguates from feature-scoped Qs (`F12 Q3`).

## Empty state

When there are zero pending and zero resolved à la carte Qs, the file is just frontmatter + the H1. Same empty-state convention as `[[CAB Triage]]` — no explanatory prose, no placeholder. The Triage file's H1 banner already shows `Questions 0` so readers know there's nothing here.

```markdown
---
description: anchor-level à la carte questions (agent-owned)
---


# [[{NAME}]] Questions
```

## Lifecycle

- **Created on first à la carte `/ask` invocation against this anchor**, if absent.
- **Updated on every `/ask`** that adds, edits, or resolves à la carte Qs.
- **Re-read by `/triage`** to count pending Qs (for the `**[N Questions]** [[{NAME} Questions]]` bullet line under the Triage H1, and for the `Questions N` count in the Triage H1 banner).

## Relationship to other planning docs

- **`[[CAB Triage]]`** — sibling facet. Triage carries the count + link bullet (`- **[N Questions]** [[{NAME} Questions]]`); the Questions facet holds the actual Q content.
- **`[[ask]]`** — `## Open Questions` block format (used here unchanged) and the routing rules that decide when a Q is à la carte vs document-attached.
- **Feature docs** — feature-attached Qs live inside their feature doc, not here. À la carte is for cross-cutting / anchor-level / planning-time / agent-raised Qs that don't belong to one document.
