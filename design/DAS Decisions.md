---
description: durable decisions for the DAS anchor itself — what this repo may contain and why
---

# DAS Decisions
Durable decisions about `dans-anchor-system` as a published artifact, with the reasoning that produced them.

### D1 — Nothing vault-specific enters this repo, anywhere

**Decision.** This repository contains **the system, never the author's use of it**. No file here — spec, skill, discipline, ruleset, template, example, figure, test, or comment — may carry content specific to the author's own knowledge repository. Not a real project's design document, not a real anchor slug, not a person, address, path, drive, employer, or codename.

The single exception is content that is **deliberately designed into a facet, skill, or discipline** — the vocabulary the system itself defines. `{slug} Backlog.md`, the `...` catch-all, the `_NAME_` disk grammar where a facet genuinely needs to name it: these are the system's own terms and belong here. The test is *"is this part of the design, or is it an artifact of who happens to be running it?"*

**Why.** This repo is public and is authored from *inside* the private vault it describes, so the nearest available example, path, or worked instance is always a real one. That is not an occasional lapse — it is the default gradient of the arrangement, and following it has produced four separate leaks:

- `examples/Audited/` held eleven genuine design documents lifted from live projects — a 38 KB test strategy, an 11 KB architectural-decisions record, and the product requirements for an application being commercially distributed.
- `design/Template Examples.md` quoted real correspondence **byte-exact and on purpose**, because the corpus existed to prove a matcher survives real-world mess. The privacy cost was never weighed against the repo being public.
- The `/io` and `/viz` skill docs carried live credential paths and real addresses, because they were written while doing real work. **This is the case that proves the rule has to be broader than examples**: a skill definition is not an example, and it leaked anyway.
- A facet cited a real interview target's plan page as its worked exemplar, simply because it was the nearest live instance of the right shape.

The unifying point is that **"it's better because it's real" is exactly the reasoning to refuse.** Realism is the temptation, not the justification.

**Consequences.**

- A real document may be *studied* to learn what shape a facet takes in practice; what lands in the repo is written from scratch to that shape. Renaming a real file is not invention.
- The rule reaches skill definitions, rulesets and their rationale, not only `examples/`. A ruleset that justifies itself by quoting a real project's `CLAUDE.md` is in scope.
- It reaches references to *this repo's own* vault anchor too — `[[SKA ctrl]]`, "the **SKA tree**", `~/ob/...`. Dan, 2026-08-08: the rule "should apply to everything related to skills". The host anchor is no more publishable than any other.
- Content already published cannot be unpublished by deletion alone. Removal from the working tree is the first step, not the remedy.

### D2 — Examples in particular are wholly invented

**Decision.** Stated separately for the avoidance of doubt, because `examples/` is where D1 is hardest to hold: every example, specimen, worked instance and figure is **fabricated for the purpose** or drawn from a **genuinely public source**. Never from the vault.

**Why.** D1 governs the whole repo, but the gallery is the one place whose entire job is to be *illustrative* — and the most illustrative document is always the real one sitting right there. The pull is strongest exactly where the rule matters most, so it gets its own decision rather than living as a clause inside D1.

**Consequences.**

- Public sources are allowed. Invention is the default, but a genuinely public specification, a published standard, or an open-source project's real document is fine — the prohibition is on *the vault*, not on reality as such.
- Examples need not be plausible-as-the-author's-work. The established cast is deliberately unrelated: Harbor (`HBR`), the Scheduler (`FEX`), Espresso, Knots, Snap, Clarifier, Mini, Viz Bench.
- Where a facet spec previously advertised an "audited real-world range", it cites invented instances only. Losing the real range is an accepted cost.
- Enforced mechanically by [[R-examples]]. The check is a floor, not a ceiling: it catches known markers, and a marker list is by construction narrower than the rule it serves.

### D3 — The `:>>` breadcrumb roots at the DAS anchor, not at the vault

**Decision.** Documents in this repo carry a breadcrumb rooted at this anchor. They must not chain up through the enclosing vault.

**Why.** Every document under `examples/` currently opens with a breadcrumb naming each ancestor from the vault root down. It is machine-derived from where the file physically sits, and required by `R-doc-structure-01`, so it is one systemic fact rather than N content defects — but it makes every page in a public repo recite a private directory path. Dan, 2026-08-08, ruled the concern is **naming rather than disclosure**: *"I'm not worried about the info leak. It's just not the right naming"* — a breadcrumb should orient a reader inside the artifact they are reading, and ancestors outside the repo orient nobody.

**Consequences.**

- The existing breadcrumbs stand until the rooting is fixed; they are a known counterexample, not a violation to sweep file-by-file.
- [[R-examples]] deliberately skips `:>>` lines, with that reasoning recorded in the checker itself, so the breadcrumb does not bury the authored leaks the checker exists to surface.
- Fixing this belongs to whoever owns breadcrumb generation, not to the gallery.
