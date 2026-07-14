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
