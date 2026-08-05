# RULESET R-fct-system-design
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file:{anchor}/**/* System Design.md, !**/DAS *.md, !**/FEX *.md`
exclusion-note:: `!**/DAS *.md` exempts the facet SPEC (a `DAS <Name>.md` is governed by [[R-facet-spec]], not by the rules for instances). `!**/FEX *.md` exempts the standalone teaching exemplar: per [[R-facet-spec]]-27 a `FEX <Name>.md` lives in the example gallery by design, so R-01's location rule would fail it for being exactly where it belongs — the same exemption [[R-facet-spec]]-25 grants worked examples that ARE the instance.
where-note:: **Deliberately location-independent** (repaired 2026-08-05, [[TINK Backlog#^T116|T116]]). This selector previously encoded the location — `**/{slug} Docs/{slug} Plan/{slug} System Design.md` — which is the shape that made the whole ruleset inert when `{slug} Docs/` was retired: it matched **0** files vault-wide while 16 real instances stood ungoverned. A location rule whose selector already requires the correct location can never fail. The selector's job is to *find* the doc; R-01's job is to *judge* where it sits.
description:: Rules every `{slug} System Design.md` instance must satisfy — location, top-of-doc shape, the Architecture boundary, and currency discipline.

**Re-derived from instances 2026-08-05** ([[TINK Backlog#^Q004|Q004]], ruled by Dan). The previous set required four H2s — `Architecture Overview` / `Components` / `Data Model` / `Decisions` — and **not one of the 14 instances in the vault carried them.** It had never fired, so nobody found out. What the corpus actually shows is that section names are *domain-shaped* (`Protocol Module`, `Frame-interval computation`, `Day boundary — the 05:00 rule`, `Numpad Controls`) across documents running 41 to 1,790 lines. A fixed section spine is therefore not a rule this facet can carry, and pretending otherwise is what produced a ruleset that could only ever be wrong.

So the checked rules here are the ones that are actually true of the corpus, and the shape guidance is `stated`. The one genuinely new constraint is R-05, which is Dan's ruling rather than an observation.

### RULE R-fct-system-design-01 — Location is `{slug} Design/` (checked)
check:: doc_in_design_folder
The System Design file lives at `{slug} Design/{slug} System Design.md` — a design artifact, filed with its siblings ([[DAS PRD]], [[DAS Roadmap]], [[DAS Architecture]]), not at the anchor root.
**Check pattern:** some ancestor folder, up to the anchor root, ends in ` Design` — walked rather than testing the immediate parent, because a subsystem's design doc nests a level deeper (`MUX Design/DMUX Subsystem/`) and is correctly filed.
**Why:** consistent location lets skills and audits find and link the doc without per-anchor config. Instances still under `{slug} Track/` are pre-F142 and migrate on the next `/design` touch — the same grace [[DAS Roadmap]] and [[DAS Features]] extend, which is why this reports rather than blocks.

### RULE R-fct-system-design-02 — Top-of-doc shape: frontmatter → H1 → dispatch table (stated)
The file opens with YAML frontmatter, then `# {slug} System Design`, then the dispatch-table placeholder — in that order, before any topic tables.
**Why:** F060 top-of-doc convention; topic tables sit below the dispatch table per F060 § Q5. **Carries no `check::` on purpose** — [[R-doc-structure]] is `where:: always` and already runs `doc_top_order` over every authored document, so a checker here would report the same five failing instances twice under two rule ids. Stated so the shape is documented where an author looks for it; enforced once, upstream.

### RULE R-fct-system-design-03 — Opens with an orientation section (sampled)
The document's first body H2 orients the reader before the detail starts — `## Overview`, `## Architecture Overview`, `## Problem Statement`, `## What the anchor system is` are all live instances of it. The *name* is free; the position and the job are not.
**Check pattern:** the first H2 after the masthead is orientation rather than a detail section.
**Why:** 9 of the 12 substantive instances already do this, which is why it is stated as a shape rather than a required heading — it is the one section the corpus genuinely agrees on. Naming it is not, so this stays `sampled`: a document whose first section is `## Protocol Module` is harder to enter, but it is not malformed.

### RULE R-fct-system-design-04 — Sections are domain-shaped, not a fixed spine (stated)
There is no required section list. A System Design names its sections after the *system it describes* — modules, flows, protocols, boundaries, configuration — and the right set differs per project.
**Why:** the retired four-H2 requirement matched zero of 14 instances. The facet's job is to say what kind of document this is and where it lives, not to impose an outline on domains it has never seen.

### RULE R-fct-system-design-05 — Decisions live in `{slug} Decisions.md`, not in a section here (checked)
check:: no_decisions_section
The document carries no `## Decisions` H2. Durable rulings and their rationale belong in the anchor's own [[DAS Decisions]] file, which exists for exactly this and is where readers and audits look for them.
**Check pattern:** no `## Decisions` heading in the body.
**Why:** ruled by Dan 2026-08-05 (Q004) as the general model — *"when we have specialized things like decisions, we just put them in their own file."* A decision inlined in a design doc is invisible to anything that reads the decision log, and it makes the design doc the second place a reader must check. The corpus was already most of the way here: only 2 of 12 instances carried the section.

### RULE R-fct-system-design-06 — The high-level decomposition belongs to `{slug} Architecture` (stated)
[[DAS Architecture]] carries the **high-level** view — subsystem decomposition, the figure, the principles. System Design carries the **detailed technical spec** that sits under it: module structure, data flows, protocols, configuration. When both exist, System Design links Architecture rather than restating it.
**Why:** ruled by Dan 2026-08-05 alongside Q004 — *"we're trying to keep the architecture document at a high level."* The two facets overlapped badly enough that retiring System Design into Architecture was a live option; this boundary is what makes keeping both coherent.

### RULE R-fct-system-design-07 — Current-spec-only discipline (stated)
The document records the *current* design, not a changelog. Rationale and alternatives belong in [[DAS Discussion]]; rulings belong in [[DAS Decisions]] (R-05).
**Check pattern:** no `## History` or changelog section.
**Why:** mixing current spec with historical narrative makes the doc unreliable as a reference for the active design — a reader cannot tell which paragraph is in force.
