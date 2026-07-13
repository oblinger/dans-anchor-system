---
description: optional file for distant-future / someday-maybe items
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Icebox](hook://p/DAS%20Icebox)
# FCT Icebox
Optional cold-storage counterpart to the Backlog — holds distant-future / someday-maybe items the user wants to remember but is not actively considering.

**Related:** [[DAS Backlog]],  [[DAS Roadmap]],  [[DAS Backlog]],  [[DAS Track]]
**Examples:** [[FEX Icebox\|example]]

**Cardinality: one per anchor** — at most one `{slug} Icebox.md` exists per anchor (and it is optional; most anchors do not have one).

**Location:** `{slug} Docs/{slug} Plan/{slug} Icebox.md` (optional)

The icebox file (`{slug} Icebox.md`) holds items the user wants to remember but is **not** actively considering — distant-future ideas, parked features, "someday-maybe" entries. It is the cold-storage counterpart to the [[DAS Backlog]]: Backlog is the *active* deferred-work list, Icebox is the *frozen* one.

The term comes from Pivotal Tracker's three-bucket model (Current / Backlog / Icebox); the GTD equivalent is "Someday/Maybe."

**Optional.** Most anchors do not have an Icebox. Create the file only when the user first wants to park something there. If items in `{slug} Backlog.md` start to feel like clutter that's never going to be acted on, that's the cue to spin up an Icebox and move them across.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Icebox.md` — Icebox.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

# CAE Icebox

| -[[FEX Icebox]]- |  |
| --- | --- |
| --- | |

## Frozen
- **GUI dashboard** — Web interface for task monitoring (out of scope for CLI-first phase)
- **Multi-tenant support** — Not needed until enterprise tier
- **Plugin system** — Third-party task handlers; revisit only if external demand appears

## Maybe Someday
- **GraphQL API** — Considered alongside REST, parked unless a consumer asks for it
- **Distributed scheduling** — Multi-host coordination; not relevant until single-host limits hit

---

# Format Specification

## Top of doc (canonical, per F060)

When created, the Icebox file opens with the standard top-of-doc format: YAML frontmatter + `# {slug} Icebox` H1 + dispatch-table placeholder. See `[[skills/rewire/SKILL]]` § Default doc top-of-file.

## Format

Each entry is a definition-list item: bold name, em-dash, short description with the *reason* it's frozen (so a future reader knows whether the freeze still applies).

Entries are grouped under H2 sections. Suggested sections (use whichever fit; add others as needed):

- **Frozen** — Explicitly parked; out of scope for current direction
- **Maybe Someday** — Soft "we might want this" without a current driver
- **Revisit Later** — Items pinned to a future trigger (e.g. "after v2 ships")

## Location

`{slug} Icebox.md` lives in `{slug} Docs/{slug} Plan/`. The file is optional — create it only when the user first wants to park an item.

## Lifecycle

- Items move **into** Icebox from Backlog when they stop being actively considered.
- Items move **out** of Icebox back to Backlog (or directly to Roadmap) when a trigger thaws them — new requirement, customer ask, design pivot.
- Icebox entries do not get deleted just for being old; the whole point is durable parking. Delete only when the idea is genuinely no longer applicable.

## Relationship to Other Planning Docs

- **Roadmap** — milestone-based execution plan
- **Backlog** — active deferred-work list, ideas that may be picked up soon
- **Icebox** — cold-storage list, not under active consideration

The cut between Backlog and Icebox is *intent to consider*, not age. A two-year-old item that the user still expects to revisit is Backlog; a two-week-old item the user has decided is out of scope is Icebox.

# RULESET R-fct-icebox
include::
where:: `file: **/{slug} Icebox.md`
description:: Rules every `{slug} Icebox.md` instance must satisfy — location, cardinality, and entry format.

### RULE R-fct-icebox-01 — Location is inside the Plan folder (checked)
The file lives at `{slug} Docs/{slug} Plan/{slug} Icebox.md` — not at the anchor root or alongside Backlog at a different path.
**Check pattern:** path matches `*/{slug} Docs/{slug} Plan/{slug} Icebox.md`.
**Why:** the Plan folder groups all planning docs together; a misplaced Icebox is not found by skills expecting the canonical path.

### RULE R-fct-icebox-02 — At most one per anchor (checked)
No more than one `{slug} Icebox.md` exists per anchor root. The facet is **optional** — most anchors do not have one.
**Check pattern:** count of `*Icebox.md` files under `{slug} Docs/{slug} Plan/` ≤ 1.
**Why:** cardinality is one; two Icebox files under the same anchor produce split inventories that drift apart.

### RULE R-fct-icebox-03 — Entries are definition-list items under H2 sections (sampled)
Each frozen item is a definition-list bullet — `- **Name** — reason it's frozen` — grouped under an H2 section (e.g. `## Frozen`, `## Maybe Someday`, `## Revisit Later`). A bare unstructured list is non-conformant.
**Check pattern:** the file body contains at least one `## ` H2 section and at least one `- **…**` bullet with an em-dash.
**Why:** the definition-list + section structure lets a reader scan quickly and see the freeze reason, which determines whether a thaw trigger applies.

### RULE R-fct-icebox-04 — Items move by intent to consider, not age (stated)
Movement into or out of the Icebox is triggered by whether the user *intends to consider* the item, not by how old it is. An old item still under consideration belongs in the Backlog; a new item the user has decided is out of scope belongs in the Icebox.
**Check pattern:** no date-based or age-based pruning rule is declared in the file.
**Why:** age-based deletion defeats the "durable parking" purpose; the correct trigger for removal is genuine obsolescence, not elapsed time.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above; cross-facet planning distinctions live in § Relationship to Other Planning Docs.)*

- **Inclusion test** — a rule belongs here only if it describes how an *icebox file* is structured, located, or maintained; cross-facet planning cut-lines (Backlog vs Roadmap vs Icebox) belong in § Relationship, and broader planning discipline in [[FCT Facets]] or [[DAS Backlog]].
- **Optionality is load-bearing** — keep emphasizing that most anchors do NOT have an Icebox; don't soften to "every anchor should have one" (that creates empty-file clutter vault-wide).
- **Movement is by intent, not age** — preserve the Backlog ↔ Icebox "intent to consider, not age" wording (R-fct-icebox-04); an age-based deletion rule would defeat the durable-parking purpose.
- **Reference Example is illustrative, not normative** — the `# CAE Icebox` H1 collision is intentional sample content; don't "fix" it by demoting to H2. The Format Specification below the example is authoritative.
- **Keep planning vocabulary aligned** — Backlog / Roadmap / Icebox / GTD Someday-Maybe terminology must stay in sync across [[DAS Backlog]], [[DAS Roadmap]], and § Relationship here; drift between these is the most common breakage.
