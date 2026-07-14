---
description: "Warden-native audit-rules pipeline — entry doc for the reserved /plan cycle (F132)"
---

# Audit Rules Redesign — Warden-native

Entry document for the user's reserved `/plan` cycle over the audit skill (user, 2026-06-16: *"I'm gonna run an explicit plan cycle over the whole thing and ship it at the end of that"*). It states what is already settled and real, sketches the target pipeline, and enumerates the forks the plan cycle must decide. Source feature: [[F132 — Rules Migration]] (Q6 resolved 2026-07-12).

## Settled foundation — not up for re-decision

- **Warden-native (F132 Q6 = A, 2026-07-12).** Rulesets compile into the Warden corpus; `/audit rules` becomes a `warden fire` over a target; the standalone `flatten-ruleset.py` / `lint-ruleset.py` pipeline is **retired from the plan** — building it would duplicate Warden's compile/flatten machinery and violate single-source-of-truth.
- **One rules engine, one-directional coupling.** Warden is the single rules engine ([[SKA PRD]] § Ratified structural disciplines); the audit skill consumes it, never the reverse. T008 (Warden repo extraction) makes the dependency physical and does not change this design.
- **Rules vs decisions vocabulary (2026-06-08, F132 Phases 1/6 shipped).** Rules = portable constraints in rulesets; decisions = anchor-specific applied choices in `{slug} Decisions.md` that cite rules via `**Cites:**`. Historical D-numbers stay (Q1=B).
- **Ruleset location is settled by F229, superseding F132 Q3/Q5.** The catalog now lives **flat** at `rulesets/R-<name>.md` in the dans-anchor-system repo root (F229 Q2b, rulesets promoted to a root kind). The per-domain folder scheme F132 shipped 2026-06-16 under `library/Rulesets/` was overtaken; that tree is now an **empty husk** (0 markdown files — cleanup candidate for the plan cycle, delete or leave to the daemon).

## What is already real (2026-07-13)

- **Compile** — `warden compile` scans the corpus and produces `~/.warden/rules-ir.json`: **547 rules across 126 rulesets**, including trait activation (`.anchor` `traits:` + `ANCHOR_BASE_TRAITS`), `include::` composition, and `where::` binding. Flattening exists; it is the compiler.
- **Live moments** — 5 hooks installed; the IR moment vocabulary today: `tool:pre:Bash|Edit|Write`, `tool:post:Write`, `write:*`, `write:markdown`, `prompt:submit`, `session:start`, `skill:pre:audit-q`. Doc-audit-on-write runs through the Warden dispatcher with fixer parity (F222/M4a).
- **On-demand fire** — `warden fire <anchor_root> <moment>` exists as a CLI verb (manual single-moment fire; `warden log` shows fire records with rules considered/fired + steer text).
- **Tier semantics** — rules carry `(checked | sampled | stated | tracked)` annotations per [[DAS Ruleset]]; checked/sampled rules carry `**Check pattern:**` blocks; a growing subset are executable `def body(ctx)` python rules (DENY vetoes + advisories).
- **What is stale** — `skills/audit/audit-rules.md` is the pre-Warden runbook (routes through `cab-config get rules` + `/rule check`, writes B-row backlog entries). It predates everything above and needs a ground-up rewrite in the plan cycle.

## Target pipeline (sketch to react to)

`/audit rules [target]` becomes a thin agent runbook over Warden:

1. **Resolve target** — walk up from cwd (or the named anchor) to the anchor root, exactly like other audit modes.
2. **Fire** — invoke the Warden engine over the target at an audit moment, evaluating every rule the anchor's effective traits activate (base + declared), across the files each rule's `where::` selects.
3. **Judge by tier** — `checked` rules run their executable body / check pattern mechanically; `sampled` rules run on a sample; `stated`/`tracked` rules emit agent-directed steers the auditing agent verifies by reading (the agent, not the engine, is the interpreter for non-mechanical tiers).
4. **Surface** — findings flow through the standard audit surfacing conventions (fix-by-default where a `fix::` exists, QFix rows for the rest) instead of the legacy B-row append.

## Forks for the plan cycle to decide

1. **Audit moment vocabulary.** No `audit:*` moment exists in the IR today. (A) add a first-class `audit:rules` moment rules can opt into; (B) re-fire the existing `write:`/`tool:` moments per file as-if-written; (C) audit mode ignores moments entirely and evaluates every activated rule against its `where::` set. Each has different rule-authoring implications.
2. **Batch fire surface.** `warden fire` today takes one moment and binds one event; an anchor-wide audit needs iterate-over-files semantics. Does that loop live in the engine (a `warden audit <root>` verb) or in the skill runbook (agent loops files, calls fire per file)?
3. **Non-mechanical tiers.** How do `stated`/`tracked` rules surface in an on-demand audit — as a checklist the auditing agent walks, as advisories attached to files, or suppressed unless `--deep`?
4. **Findings destination.** Legacy runbook appends a `B<n>` backlog row; current audit-q practice is fix-by-default + QFix singleton. Pick one convention for rules audits (lean: match audit-q — fix mechanical, QFix the rest, no B-rows).
5. **Check-pattern execution gap.** Many `(checked)` rules carry prose `**Check pattern:**` blocks but no executable `body(ctx)`. Does the plan cycle mandate migrating checked rules to executable bodies, accept prose patterns as agent-interpreted, or introduce a lint that flags the gap?
6. **`/audit decisions` rename leg (F132 Phase 4).** The `**Cites:**`-walking decisions audit was folded into the rules audit in the ratified design — confirm it survives the Warden-native reshape (walking `{slug} Decisions.md` cites is not a Warden fire; it may stay a bespoke checker inside the runbook).
7. **Husk cleanup.** Delete the empty `library/Rulesets/` tree (and `library/` itself if nothing genuinely-shared remains, per F229's "else dissolves").

## Pointers

- [[F132 — Rules Migration]] — the feature (Q1–Q6 resolutions, shipped phases)
- [[Warden Semantics]] — activation, moments, fire model
- [[DAS Ruleset]] — the ruleset file format (tiers, `include::`, `where::`)
- [[DAS Rulesets]] — the catalog index
- `skills/audit/audit-rules.md` — the stale legacy runbook to be replaced
