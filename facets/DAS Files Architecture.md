---
description: "the top-down design of a system's module & content structure — the file-tree architecture doc kind"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[DAS Design Docs]] → [FCT Files Architecture](hook://p/DAS%20Files%20Architecture)
# FCT Files Architecture
The facet spec for a **Files Architecture** document — the top-down design of how a system's files, modules, and content are laid out: every folder, what lives in it, and why the tree is shaped that way.

**Related:** [[DAS Architecture\|Architecture]] (subsystem-interaction story — the sibling design facet),  [[DAS All Files\|All Files]] (the realized source tree this designs),  [[DAS Module Doc\|Module Doc]],  [[DAS Design Docs\|Design Docs]] (parent group)
**Examples:** [[SKA File Tree Architecture]] — the worked instance: the top-down design of the `ob-skills` / SKA tree

**TLDR** — A Files Architecture doc is the top-down canonical map of where every file/module/content kind lives in a system and why the tree is shaped that way. Required parts: a folder→role structure table (the load-bearing piece) and its design rationale. Cardinality: one per anchor/repo. Sibling to [[DAS Architecture]] (subsystem interactions), not a replacement for it.

# Files Architecture Document Structure

A Files Architecture doc is a **design document**, not a catalog. It captures the *intended* shape of a system's file/module/content tree and the reasoning behind it. Typical top-to-bottom parts (materialize the ones the system needs — none is mandatory except the target structure + its rationale):

- **Masthead + one-liner** — dispatch table; one sentence naming the system whose layout this designs.
- **Target structure** — the end-state layout. A folder→role table (each top-level folder/category + what lives in it) and/or an annotated tree. This is the load-bearing part: it states *where every kind of thing goes*.
- **Design rationale / principles** — *why* the tree is shaped this way: the organizing principles, the constraints (runtime mounts, naming-collision avoidance, audience splits), the trade-offs taken.
- **Naming considerations** — the conventions that govern names in the tree (prefixes, slugs, casing) and the reasoning that produced them.
- **Supersession note** — what older doc or section this design replaces, so readers don't follow a stale map.
- **Status + open questions** — while the design is in flight: what's ratified vs still under discussion (the design agenda).

The tree/layout is **the** content; keep prose tight and let the structure table carry the weight. Distinct from [[DAS Architecture]] (which tells the *subsystem-interaction* story — how modules talk to each other) — Files Architecture is purely about *where things live and why*.

# Files Architecture Overview

**When to use.** A system has a Files Architecture doc when its tree is non-obvious enough to need a canonical, top-down map — typically a repo or anchor with many files/modules/categories where contributors (and agents) would otherwise relitigate "where does this go?" The doc is the authoritative answer; the realized tree ([[DAS All Files]]) and per-module docs ([[DAS Module Doc]]) converge to it.

**Top-down, not incremental.** It describes the *end-state* the tree is aiming toward, not the migration steps to get there. Migration sequencing may appear as an open question, but the spine of the doc is the target.

**One per system.** A given repo/anchor has at most one Files Architecture doc. Sub-trees don't each get their own; they're rows in the single doc's structure table.

**Relationship to the other facets:**
- [[DAS All Files]] — the *realized* source tree (an instance), with files linked to module docs. Files Architecture is the *design* it conforms to; when the two disagree, the architecture doc is the intended state and the tree is brought into line (or the architecture is revised deliberately).
- [[DAS Architecture]] — the *system-architecture* design (subsystems, data flow, how parts interact). Files Architecture is its file-layout sibling; the two cross-reference but don't overlap.
- [[DAS Module Doc]] — the per-module docs the realized tree links into.

# By-name hierarchies (optional pattern)

Some systems don't keep one tree — they split artifacts across **two or more by-name indexes** keyed on a shared **concept name** (e.g. a *verbs* list and a *nouns* list, plus smaller ones). When a Files Architecture uses this pattern it must state three things, because they are exactly what someone needs to place a new artifact without relitigating:

- **One-list placement** — each concept is named in **exactly one** index, chosen by **what it primarily is**, and **never** in two. The entry points at the concept's single **dispatch page**, the hub that cross-links everything else. (No dual-listing: a concept with both a verb and a noun aspect is still listed once, in its primary list, with the other aspect reached from its page.)
- **Satellites are unlisted** — a concept's sub-files (examples, a facet spec, scripts) exist freely but get **no index entry of their own**; the only place they're linked is the dispatch page, reached by direct link, not by browsing a list. Thin secondary content shouldn't even spawn a file — it lives on the dispatch page until it's substantial.
- **Absence semantics** — a missing sub-file / cross-link is a **deliberate signal** ("not governed / not applicable"), kept distinct from "forgotten" by the cross-link discipline (a page links only what exists, so a missing link reads as intentional).

[[SKA File Tree Architecture]] § *One concept, one list* is the worked instance: skills (verbs) + facets (nouns) as the two primary lists, traits + disciplines as smaller ones; each concept listed once; scripts and examples are un-listed satellites.

# RULESET R-files-architecture
description:: the file-tree / content-structure design doc kind

### RULE R-files-architecture-01 — Target structure is present and explicit (checked)
**Check pattern:** the doc contains a folder→role mapping (a table or annotated tree) that names every top-level category/folder of the system and what lives in it.
**Why:** the whole point of the doc is to be the authoritative "where does X go?" answer; without an explicit target layout it's just commentary.

### RULE R-files-architecture-02 — Top-down end-state, not a migration log (stated)
**Check pattern:** the structure section describes the *aimed-at* layout; incremental migration steps, if any, are confined to a Status / open-questions section, not mixed into the target.
**Why:** readers need the canonical destination at a glance; interleaving in-flight migration noise makes the map untrustworthy.

### RULE R-files-architecture-03 — Every structural choice carries rationale (stated)
**Check pattern:** each non-obvious folder/naming choice in the target has a *why* nearby (organizing principle, constraint, or trade-off) — not bare assertion.
**Why:** the design's durability depends on the reasoning surviving; un-justified structure gets relitigated the moment someone disagrees.

### RULE R-files-architecture-04 — Distinguished from system architecture (stated)
**Check pattern:** the doc stays about *where things live and why*; subsystem-interaction / data-flow content is delegated to [[DAS Architecture]] via a cross-link, not duplicated here.
**Why:** Files Architecture and system Architecture are sibling design facets; conflating them produces two docs that drift and contradict.

### RULE R-files-architecture-05 — Names carry their conventions (sampled)
**Check pattern:** when the tree relies on naming conventions (prefixes, slugs, casing), those conventions are stated with their rationale, not left implicit in the examples.
**Why:** a reader placing a new file needs the rule, not just a pattern to pattern-match against.

### RULE R-files-architecture-06 — Supersession is named (stated)
**Check pattern:** if this design replaces an older doc or section, it says so explicitly (which doc/section, and that it's now stale).
**Why:** stale parallel maps are worse than none; an explicit supersession note routes readers away from the dead one.

### RULE R-files-architecture-07 — Embedded trees are plain monospace, never fenced (checked)
**Check pattern:** any file-tree shown in the body renders via `cssclasses: monospace` (or equivalent), not wrapped in a ```` ``` ```` code fence — so wiki-links inside the tree stay live.
**Why:** same load-bearing rule as [[DAS All Files]]: fencing a tree kills its links and turns the page into a dead zone.

### RULE R-files-architecture-08 — By-name indexes state one-list placement, unlisted satellites, and absence (stated)
**Check pattern:** if the tree splits artifacts across two or more concept-name-keyed indexes, the doc states all three: (a) **one-list placement** — each concept named in exactly one index, never two, with a single dispatch page as the hub; (b) **satellites unlisted** — sub-files (examples, specs, scripts) carry no index entry and are reached only from the dispatch page; (c) what a missing sub-file / cross-link means.
**Why:** the value of these indexes is mechanical placement and one navigable home per concept; dual-listing, or listing satellites, reintroduces exactly the ambiguity the split was meant to remove.

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above; the `R-files-architecture` ruleset is embedded below.)*

- **This page never holds a specific system's tree** — instances (e.g. [[SKA File Tree Architecture]]) cite it as authority and carry their own trees; keep this spec system-agnostic.
- **No `module-doc` discipline yet** — the cross-cutting module-doc linking convention currently lives inside [[DAS All Files]] and [[DAS Module Doc]]; a `module-doc` discipline may be extracted later if it grows enough independent reference sites (per [[F165 — Files Architecture + Code facets (All Files, Module Doc)]] Q2).
