---
description: "F218 — Design-rules catalog: the user's recurring architectural / design rules, authored as Warden rulesets and adopted per-application by trait. Migrated from SKA F108 2026-07-02 — the catalog is *content* riding the Warden ruleset system, not a parallel store."
---

# [[Warden]] · F218 — Design-rules catalog — ship with skills, adopt per-application

## Summary

The user operates by recurring architectural patterns across applications — "every system has a single `Interfaces/` folder," "instances are created through factories," "factories live in a peg-board for central registration," "test construction is gated behind a design-sign-off milestone." These are personal-style design rules — load-bearing for the user's own code-quality bar, often invisible in any one project's docs.

F218 is the **catalog of such rules, authored as Warden rulesets**. It ships with the skill system; when a new application is created, an early `/code audit` proposes the rules that fit and the user adopts a subset — adoption being a `.anchor` **trait edit**, not a copy. Subsequent audits enforce the adopted subset through the normal Warden engine.

The value-add is the bootstrap: the catalog isn't invented from thin air — it's **mined from the user's existing applications and PRDs**. Patterns applied repeatedly (MUX, HA, SVP, DKT, SVAR, A2X, SKD) become canonical rules; one-offs don't enter.

**Migrated from SKA F108 (2026-07-02).** The design-rules catalog is a rule-corpus that ships with skills and is adopted per-application — squarely the rule-engine agent's domain. It contributes *content* into the Warden ruleset system and builds **no** parallel storage or adoption mechanism. SKA's [[F108 — Design-rules catalog — ship with skills, adopt per-application|F108]] is retired to a redirect.

## Success Criteria

**Tier:** 2 — depends on the ruleset system + trait-driven activation (M1 / [[F211 — Rule compiler and installer|F211]]) and the mining pass.
**Blocks next:** none (a content layer over the engine).

**What done looks like.** A seed set of the user's design-rule families exists as Warden rulesets (`# RULESET R-<slug>`, colocated per [[F133 — Rulesets folder convention + facet embedding|F133]]); adopting one for an app is a single `.anchor` trait entry; a `/code audit` of an app fires exactly its adopted subset and no more. The seed families below are all expressible in the frozen Warden language ([[Warden Semantics]]).

**How it will be verified.** A test app whose `.anchor` adopts the `Interfaces-folder` trait: the interfaces-folder rule fires and flags a scattered interface; an app that has *not* adopted it sees no such finding (proves per-application adoption is trait-gated, not vault-wide).

## Design

### Seed rules from the commissioning message

These entered the catalog as initial seeds (from the user's F108 commission):

- **Single `Interfaces/` folder.** Every system has one folder named after its purpose (literally `Interfaces`) holding all interface contracts. No interfaces scattered across module folders.
- **Factories construct instances.** Object instances are created through factory functions, never via direct constructor calls in business code.
- **Peg-board registers factories.** Factories live in a central registry (a "peg-board") so the architecture's wiring is visible in one place. Each architectural piece registers its factory at the peg-board.
- **Design sign-off gate before test construction.** A milestone gate sits between "all design docs + skeleton code written" and "test cases constructed." The user reviews and explicitly signs off; test construction is blocked until then. (SVP M15 is the canonical instance; F218 generalizes the pattern.)

### Catalog mining

A scan of the user's PRDs and architecture docs across `~/ob/kmr/` surfaces more recurring rules. Candidate targets:

- `~/ob/kmr/prj/Hook Anchor/HA Docs/` — HA's principles and architecture.
- `~/ob/kmr/SV/ww/svar-docs/sv-pipe/SVP Docs/` — SVP's Principles + System Design + PRD.
- `~/ob/kmr/prj/ClaudiMux/MuxUX/MUX Docs/` — MUX's design docs.
- `~/ob/kmr/SV/ww/svar-docs/alg2-experimental/A2X Docs/` — A2X's design.
- `~/ob/kmr/prj/ClaudiMux/Skill Docket App/SKD Docs/` — SKD's design.
- Anything matching `*Principles*.md` / `*Architecture*.md` / `*System Design*.md`.

The scan looks for recurring language — "we always", "every module", "should never", "must", "the X pattern", "single source of truth". A pattern recurring across ≥3 projects becomes a catalog candidate. Per Q2: the agent **proposes**, the user reviews and upgrades — nothing is auto-created or auto-adopted.

### How rules ship and get adopted — the Warden ruleset system (Q1)

The catalog rides the Warden ruleset system; it builds **no** parallel store:

- **Ship.** Each design-rule family is a `# RULESET R-<slug>` **named after what it governs** and **colocated** with the spec it enforces ([[F133 — Rulesets folder convention + facet embedding|F133]]), authored in Warden's rule language ([[Warden Rule]]). One canonical set per base name — never duplicated; when a skill and its facet share a base name, the single set is `include::`d by both traits, not copied. A large family gets its own `R-<slug>.md`; a small one rides the **tail of the user-facing SKL doc / FCT**, never the capital `SKILL.md` runbook (which the agent loads wholesale — rules there pollute its working context). The capital SKILL carries at most a **reference**, and only when the rules genuinely help execute the skill by hand.
- **Discover.** The Warden scan index ([[F211 — Rule compiler and installer|F211]]) is the mechanical enumerator (`# RULESET` sentinel sweep); `/rule discover` (F082) surfaces declared rulesets. F218 contributes catalog *content*, not new discovery.
- **Adopt.** Adopting a rule for an application = **adding the trait that pulls in its ruleset to the app's `.anchor`** — a trait edit, not a copy. At the first `/code audit` of a new app the agent proposes the seed families; the user picks; the picks become trait entries. The always-on rules ride the **implicit base anchor-trait** every anchor adheres to without declaring it ([[Warden Semantics]] § Activation).
- **Enforce.** Adopted rulesets fire through the Warden engine — live at their `when::` moments and at every `/audit` pass. Violations surface as steers/findings (tier per rule).

### What this doesn't try to do

- **Enforce rules across the vault without explicit per-application adoption.** Catalog presence ≠ vault-wide application. Each app opts in via its trait list.
- **Police the user's actual decisions.** The catalog surfaces; the user picks. Rejecting a "canonical" rule for a specific app is their call.
- **Replace the audit engine.** F218 is the *content* layer (which rules exist); the Warden engine + `/audit` are the *enforcement* layer (how rules get checked).

## Status

**Later** — migrated from SKA [[F108 — Design-rules catalog — ship with skills, adopt per-application|F108]] 2026-07-02 (user: "pull that feature across into your warden set of features, so you own it"). Q1 + Q2 resolved (below); the storage/adoption model is the Warden ruleset system, so no design fork remains. Parked behind M1 (the ruleset engine + trait activation) — the catalog needs the engine that fires it. Lands as *content* once the engine exists; the mining pass can begin any time.

**Next action:** when promoted, run the § Catalog mining scan over ~5 projects and propose a candidate seed-rule list (propose→review, per Q2).

## Resolved

### Q1 — Where do the rules live structurally? — RESOLVED (user, 2026-07-02): rides the Warden ruleset system — no separate catalog store ^F218-Q1

The design rules are **not** a separate store (superseding SKA F108's original A/B/C options — a `skills/design-rule/` folder, a single facet file, a new category — all of which predate the mature Warden ruleset model). They live exactly where every Warden ruleset lives: a `# RULESET R-<slug>` named after and colocated with the spec it governs, one canonical set per base name (`include::`d by both traits when a skill and facet share a name, never copied), placed at the tail of the user-doc / FCT or its own file (never the capital `SKILL.md`), and **adopted per-application by trait**. The always-on rules ride the **implicit base anchor-trait** ([[Warden Semantics]] § Activation). See § How rules ship and get adopted.

### Q2 — Catalog mining: agent-driven or interview-driven? — RESOLVED (user, 2026-07-01): (C) hybrid — agent proposes, user reviews and upgrades ^F218-Q2

The agent PROPOSES candidate rules (from the mining scan); the user reviews and upgrades; nothing is ever auto-created or auto-adopted. Carried over from SKA F108.

## See also

- [[F108 — Design-rules catalog — ship with skills, adopt per-application|SKA F108]] — the retired origin (redirect).
- [[Warden Semantics]] § Rulesets — composition, the implicit base trait, trait-driven activation.
- [[F133 — Rulesets folder convention + facet embedding|F133]] — the `R-<slug>` naming + colocation convention.
- [[F211 — Rule compiler and installer|F211]] — the scan index + engine that fires adopted rulesets.
