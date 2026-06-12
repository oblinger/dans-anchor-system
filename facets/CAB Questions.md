---
description: anchor-level à la carte questions facet (agent-owned)
---
# CAB Questions

The Questions facet spec — defines the per-anchor à la carte Questions file (`{NAME} Questions.md`) where slug-scoped, cross-cutting, agent-raised questions live outside of any feature doc.

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Questions.md`


The Questions file is the per-anchor home for **à la carte** (slug-scoped, cross-cutting, agent-raised) questions that don't belong to any feature doc. It mirrors the `## Open Questions` block format used inside feature docs (per `[[SKA ask]]`), but at the anchor scope.

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

## F060 exception — no dispatch-table placeholder

Per F060, every doc inside an anchor gets an H1 + dispatch-table placeholder. **`{NAME} Questions.md` is an explicit exception:** the H1 (`# [[{NAME}]] Questions`) is the entire top-of-doc, with no dispatch table below it. Rationale: this is an agent-owned, destructively-rewritten inbox — the H1 wiki-link already provides navigation back to the anchor, and the body is exclusively question content. Adding a dispatch table here would be visual noise on a high-traffic surface. Rewire skips the placeholder check for this file; same exception applies to `{NAME} Triage.md`.

## Body

Identical to the `## Open Questions` block format used inside feature docs (per `[[SKA ask]]`):

- `## Open Questions` H2 with the pending Q bullets.
- `### Resolved` H3 inside `## Open Questions` as the temporary holding pen for resolutions during an active question batch.
- When all pending Qs resolve (Phase 2 transition), delete `## Open Questions` and migrate accumulated resolved Qs to a `## Resolved` H2 at the **bottom** of the file (permanent archive).
- When a new à la carte Q arises later (Phase 3), recreate `## Open Questions` at the top.

## Q-numbering

À la carte Qs use `Q<n>` — same prefix as feature-attached Qs but in a per-anchor scope. Lowest unused integer in the file (across `## Open Questions` pending + `### Resolved` + bottom `## Resolved`). Numbers are stable references; never renumber. Same numbering policy as `[[CAB Backlog]]` § Numbering policy.

When referenced in conversation: `{NAME} Q3` (e.g., "SKA Q3"). The slug disambiguates from feature-scoped Qs (`F012 Q3`).

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
- **`[[SKA ask]]`** — `## Open Questions` block format (used here unchanged) and the routing rules that decide when a Q is à la carte vs document-attached.
- **Feature docs** — feature-attached Qs live inside their feature doc, not here. À la carte is for cross-cutting / anchor-level / planning-time / agent-raised Qs that don't belong to one document.

# BRIEF

- **This file is the spec for the Questions facet**, not an instance of it; don't paste real à la carte Qs here — those go in a concrete `{NAME} Questions.md` under an anchor's `{NAME} Plan/` folder.
- **Authority boundary** — this facet owns the location, H1 shape, F060 dispatch-table exception, body structure (`## Open Questions` / `### Resolved` / bottom `## Resolved`), Q-numbering policy, empty-state, and lifecycle. The `## Open Questions` block format itself is owned by `[[SKA ask]]`; don't restate it here, link to it.
- **Inclusion test for content on this page** — does it describe how `{NAME} Questions.md` is structured, located, or maintained at the anchor scope? If it's a feature-doc Q rule, it belongs in `[[SKA ask]]`; if it's a Triage rule, it belongs in `[[CAB Triage]]`.
- **Load-bearing constraints** — the F060 dispatch-table exception (this is one of two facets, alongside `{NAME} Triage.md`, that legitimately omits the placeholder) and the `**[N Questions]** [[{NAME} Questions]]` bullet contract with `[[CAB Triage]]`. Changing either breaks rewire and triage.
- **Reference Example must stay in sync** with the Format Specification below it — the markdown block is the canonical visual; if the spec changes (H1 form, H2/H3 nesting, empty state), update the example in the same edit.
- **Don't pile related-facet content here** — Triage rules → `[[CAB Triage]]`; ask-routing rules → `[[SKA ask]]`; project-wide question discipline → CLAUDE.md / `[[CAB Disciplines]]`. This page is strictly about the per-anchor à la carte Questions file.
