---
description: optional file for distant-future / someday-maybe items
---
# FCT Icebox
Optional cold-storage counterpart to the Backlog — holds distant-future / someday-maybe items the user wants to remember but is not actively considering.

| -[[FCT Icebox]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Track]] → [FCT Icebox](hook://p/FCT%20Icebox)<br>: optional file for distant-future / someday-maybe items |
| --- | --- |
| Related | [[FCT Backlog]],  [[FCT Roadmap]],  [[CAB Backlog]],  [[FCT Track]],   |

**Cardinality: one per anchor** — at most one `{NAME} Icebox.md` exists per anchor (and it is optional; most anchors do not have one).

**Location:** `{NAME} Docs/{NAME} Plan/{NAME} Icebox.md` (optional)


The icebox file (`{NAME} Icebox.md`) holds items the user wants to remember but is **not** actively considering — distant-future ideas, parked features, "someday-maybe" entries. It is the cold-storage counterpart to the [[CAB Backlog]]: Backlog is the *active* deferred-work list, Icebox is the *frozen* one.

The term comes from Pivotal Tracker's three-bucket model (Current / Backlog / Icebox); the GTD equivalent is "Someday/Maybe."

**Optional.** Most anchors do not have an Icebox. Create the file only when the user first wants to park something there. If items in `{NAME} Backlog.md` start to feel like clutter that's never going to be acted on, that's the cue to spin up an Icebox and move them across.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE Plan/CAE Icebox.md` — Icebox.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

# CAE Icebox

| -[[CAE Icebox]]- |  |
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

When created, the Icebox file opens with the standard top-of-doc format: YAML frontmatter + `# {NAME} Icebox` H1 + dispatch-table placeholder. See `[[skills/rewire/SKILL]]` § Default doc top-of-file.

## Format

Each entry is a named-list item: bold name, em-dash, short description with the *reason* it's frozen (so a future reader knows whether the freeze still applies).

Entries are grouped under H2 sections. Suggested sections (use whichever fit; add others as needed):

- **Frozen** — Explicitly parked; out of scope for current direction
- **Maybe Someday** — Soft "we might want this" without a current driver
- **Revisit Later** — Items pinned to a future trigger (e.g. "after v2 ships")

## Location

`{NAME} Icebox.md` lives in `{NAME} Docs/{NAME} Plan/`. The file is optional — create it only when the user first wants to park an item.

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
where:: file: **/{NAME} Icebox.md
description:: Rules every `{NAME} Icebox.md` instance must satisfy — location, cardinality, and entry format.

### RULE R-fct-icebox-01 — Location is inside the Plan folder (checked)
The file lives at `{NAME} Docs/{NAME} Plan/{NAME} Icebox.md` — not at the anchor root or alongside Backlog at a different path.
**Check pattern:** path matches `*/{NAME} Docs/{NAME} Plan/{NAME} Icebox.md`.
**Why:** the Plan folder groups all planning docs together; a misplaced Icebox is not found by skills expecting the canonical path.

### RULE R-fct-icebox-02 — At most one per anchor (checked)
No more than one `{NAME} Icebox.md` exists per anchor root. The facet is **optional** — most anchors do not have one.
**Check pattern:** count of `*Icebox.md` files under `{NAME} Docs/{NAME} Plan/` ≤ 1.
**Why:** cardinality is one; two Icebox files under the same anchor produce split inventories that drift apart.

### RULE R-fct-icebox-03 — Entries are named-list items under H2 sections (sampled)
Each frozen item is a named-list bullet — `- **Name** — reason it's frozen` — grouped under an H2 section (e.g. `## Frozen`, `## Maybe Someday`, `## Revisit Later`). A bare unstructured list is non-conformant.
**Check pattern:** the file body contains at least one `## ` H2 section and at least one `- **…**` bullet with an em-dash.
**Why:** the named-list + section structure lets a reader scan quickly and see the freeze reason, which determines whether a thaw trigger applies.

### RULE R-fct-icebox-04 — Items move by intent to consider, not age (stated)
Movement into or out of the Icebox is triggered by whether the user *intends to consider* the item, not by how old it is. An old item still under consideration belongs in the Backlog; a new item the user has decided is out of scope belongs in the Icebox.
**Check pattern:** no date-based or age-based pruning rule is declared in the file.
**Why:** age-based deletion defeats the "durable parking" purpose; the correct trigger for removal is genuine obsolescence, not elapsed time.

# BRIEF

- **This is the facet spec for `{NAME} Icebox.md`**, not a real icebox — edits here change the rule, not any anchor's parked items. Per-anchor icebox content lives in each anchor's own `{NAME} Icebox.md`.
- **NOT for**: backlog-grade work (active deferred items belong in [[CAB Backlog]]), trash (genuinely dead ideas should be deleted, not iceboxed), or roadmap items (planned execution belongs in [[FCT Roadmap]]). The defining attribute is *durable parking without current intent*.
- **Inclusion test for a facet rule on this page**: does it describe how an *icebox file* is structured, located, or maintained? Cross-facet planning rules (Backlog vs Roadmap vs Icebox cut lines) belong in the § Relationship section; broader planning discipline belongs in the parent [[FCT Facets]] catalog or [[CAB Backlog]].
- **Reference Example zone is illustrative, not normative** — the H1 collision (`# CAE Icebox` inside this file) is intentional sample content. Don't "fix" it by demoting to H2; the format specification *below* the example is the authoritative shape.
- **Load-bearing constraint — optionality**: the spec must keep emphasizing that most anchors do NOT have an Icebox. Don't soften this into "every anchor should have one" — that would create empty-file clutter across the vault.
- **Lifecycle rules govern movement, not deletion** — items move Backlog ↔ Icebox by *intent to consider*, not age. Preserve that wording; an age-based deletion rule would defeat the whole "durable parking" purpose.
- **When updating planning vocabulary** (Backlog / Roadmap / Icebox / GTD Someday-Maybe), keep terminology aligned across [[CAB Backlog]], [[FCT Roadmap]], and the § Relationship section here. Drift between these three specs is the most common breakage.
