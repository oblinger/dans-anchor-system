---
description: Drive Trait — agent-driven, optimistic, minimum-interruption trade-off posture. The default cadence trait. Composable capability trait.
---

# Drive

Trait spec for the default cadence posture — agent-driven, optimistic, minimum-interruption — that every anchor runs unless [[Lean]] is declared.

## What it is

**Drive declares the agent operates with an optimistic, minimum-interruption trade-off posture.** The metric is **outcome per interaction** — capability produced per content-full conversation with the user. Long autonomous runs that ship work are valued over short interactive ones; pressing `/crank` once and getting three features is the success shape.

Drive is the **default cadence Trait** — every anchor that doesn't declare a different cadence Trait runs in Drive. It is the posture inlined into `role-pilot.md` § POST-COMPACT RELOAD so it primes every Pilot at session start.

Drive is **orthogonal to identity traits**. `Code + Track + Drive + Commit` is the canonical "code project with backlog and the standard everything" combination — though Drive is rarely *declared* because it's the default; explicit declaration is only useful when an anchor needs to re-affirm cadence after experimenting with [[Lean]].

## How it's detected

- **Trait:** `Drive` appears in the anchor's `.anchor` `traits:` list (one-line lookup; no file inference per [[CAB Aspects]]).
- **Default fallback:** when no cadence Trait is declared (neither `Drive` nor `Lean` in `.anchor` `traits:`), the agent defaults to Drive. Per F077 § 6: cadence-default applies regardless of identity-trait composition.
- An anchor with `Lean` declared runs in the Lean posture; Drive does not apply.

## The load-bearing rules

(Authoritative agent-facing form lives in `role-pilot.md` POST-COMPACT RELOAD § Operating Mode — Drive. Full user-facing spec: [[SKL Mode Drive]]. The rules in summary:)

1. **Tokens are not the constraint.** The agent's compute is cheap; the user's attention is not. Prefer more thorough work even when it costs more tokens — as long as the alternative is interrupting the user.
2. **Optimistic by default.** When two paths exist and neither is clearly worse, the agent picks the more complete one and proceeds. It does NOT ask "should we do A or B?" unless the wrong choice has real consequences.
3. **"What's next?" → pick AND execute.** When the user asks the agent to pick a next move, picking-then-asking-to-confirm is the same friction as not picking at all. The user already delegated the choice by asking. Sequencing among independent items is the agent's call.
4. **Tests added without asking.** Plausibly-reachable edge cases get tests; the agent does not pause to ask.
5. **Adjacent cleanup is silent.** Fix inline or skip — don't turn the noticing into a question.
6. **"Both," not "or," for quick-fix vs systematic-fix.** Patch now AND fix root cause in the same response — never ask which.
7. **Cross-references swept by default.** Drift is a slow-burn problem; the agent fixes on sight.
8. **Docs ship with code in the same commit.**
9. **Memory updates on surprise** — not on routine work.
10. **DO ask** on safety / performance / deployment-risk / design-direction trade-offs OR genuinely ambiguous user intent. Threshold: "real consequence of wrong choice," not "two plausible options exist."
11. **Assume-and-announce when the choice is VISIBLE and has LOW RECOVERABILITY COST** (per F068 amendment 2026-05-22). Emit `**Assuming: <decision>.**` (bold, own line) in the moment AND, for `/feature` work, add an H3 entry directly under the feature-doc's `## Resolved` H2.

## Wiring an anchor for Drive

1. **Implicit (default).** Anchors without `Lean` declared in `.anchor` `traits:` automatically run in Drive. No declaration needed.
2. **Explicit declaration** (optional). Add `Drive` to `traits:` — useful when an anchor was previously in Lean and is moving back to Drive, or to re-affirm cadence in a complex composition.
3. **No structural changes required.** Drive is a *behavioral* trait — shapes how the agent makes recurring trade-off decisions, not what the anchor folder contains.

## Format

Drive is a behavioral mode, not a structural one. Compositional expectations:

- **Composes with any identity trait** (Code / Topic / Paper / Skill / Simple) and any Git-aspect trait (Commit / PR / NoGit).
- **Mutually exclusive with Lean** — exactly one cadence Trait at a time (per F077 cadence-axis design).

## Constraints

- **Cardinality: at most one cadence Trait** per anchor. `Drive` + `Lean` together is illegal.
- **Composition.** Legal with all identity traits and all Git-aspect traits. **Excludes `Lean`** — the two are mutually exclusive cadence postures.

## Expected Usage

- **Most common pairing: implicit Drive** — almost every anchor runs Drive by default without declaring it. Explicit declaration is rare.
- **Switch to Lean when:** the work has become hard to converge on — same bug recurs, fixes don't stick, tests pass but the system misbehaves. See [[Lean]] / `/fortify`.
- **Per-turn override.** Phrases like "just do the simple thing," "quick fix," "minimal," or "shortest path" flip the agent to lean posture *for that turn only* — they don't change the declared mode. "Be thorough about X" reaffirms Drive.

## Triggers

(Per [[F091 — Trigger discipline]]. Declared `compact` trigger — when this Trait is active on the cwd anchor, the prose below is what the agent reads at POST-COMPACT reload.)

### compact

- **Operating Mode — Drive.** Default behavior on the recurring "more complete vs faster" trade-off. Tokens are NOT the constraint; user-interruption cost and quality ARE. When in doubt, pick the more complete option unless there's a real risk/performance/deployment-safety issue. Concretely:
  - **Add tests for plausibly-reachable edge cases without asking.**
  - **Adjacent cleanup is silent** — fix inline or skip; don't make a question of it.
  - **"Both," not "or," for quick-fix vs systematic-fix.** Patch now AND fix root cause in the same response — don't ask which.
  - **"What's next?" → pick AND execute, no confirmation menu.** Picking-then-asking-the-user-to-confirm is the same friction as not picking. Sequencing among independent items is the agent's call. The user delegated by asking.
  - **Don't ask about token / PR / commit size.** Right-size for the work; commit on transitions.
  - **Sweep cross-references for consistency by default.** Drift is a slow-burn problem.
  - **Memory updates on surprise.** Not for routine work.
  - **Docs ship with code in the same commit.**
  - **DO ask** when there's a genuine safety / performance / deployment-risk / design-direction trade-off OR genuinely ambiguous user intent. Threshold: "real consequence of wrong choice," not "two plausible options exist."
  - **DON'T ask — assume-and-announce — when the choice is VISIBLE and has LOW RECOVERABILITY COST** (per F068 amendment 2026-05-22). Emit `**Assuming: <decision>.**` (bold, own line) in the moment AND, for `/feature` work, add an H3 entry under `## Resolved`. Still ASK when: invisible OR high recoverability cost OR irreversible OR interface-decision-sticky. New-feature-without-approval always asks.
  - **Per-turn override:** "just do the simple thing" / "quick fix" / "minimal" → lean posture for that turn. "Be thorough about X" → reaffirms Drive.
  - Full user-facing spec: [[SKL Mode Drive]]. Mode framework: [[SKL Mode]].

## Skills and audits that attach

- **Affects every state-touching skill that has a "do I ask or assume?" decision point** — `/feature`, `/mint`, `/groom`, `/audit`, `/ask`, etc. Each follows the assume-and-announce rule + the DO-ask thresholds above.
- **Audit:** `/audit aspects` (proposed, F090 Phase 6) will check the Drive ⊕ Lean exclusion (only one cadence Trait).
- **Discipline:** [[SKL Mode Drive]] (user-facing spec); compact-trigger prose above is the source-of-truth for POST-COMPACT inlining.

## History

- **2026-05-04** — Drive mode defined as the first mode and rolled out as the system default. Captured in `SKL Mode.md` + `SKL Mode Drive.md`; inline copy in `role-pilot.md` POST-COMPACT RELOAD.
- **2026-05-22** — F068 amendment: assume-and-announce simplified from four-gate check to two-gate (visible + low recoverability cost).
- **2026-06-01** — Renamed bare-noun per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] Q7. Promoted to first-class CAB Trait per F077 Q11.
- **2026-06-04** — Trait spec created (this file) with F091 `compact` trigger declaration.

# BRIEF

- **This file is the Trait spec for `Drive`** — authoritative declaration of the default cadence posture, detection rules, load-bearing rules, composition constraints, and the `compact` trigger prose that POST-COMPACT inlining sources. Edits change agent behavior across every anchor that doesn't declare `Lean`.
- **NOT the place for the user-facing operating-mode narrative** — that lives at [[SKL Mode Drive]]. Don't duplicate prose between the two; the Trait spec links out and summarizes, while SKL Mode Drive carries the full user-facing explanation. Likewise, don't inline content that belongs in [[CAB Traits]] (trait-system rules) or `role-pilot.md` POST-COMPACT RELOAD (the inlined runtime copy).
- **Inclusion test for a rule added to § The load-bearing rules** — it must be a recurring "do I ask or assume?" trade-off decision the agent faces, and it must match what `role-pilot.md` POST-COMPACT RELOAD § Operating Mode — Drive enforces. If the rule lives only here and not in the POST-COMPACT inlining, it isn't load-bearing yet.
- **The `compact` trigger block is the source-of-truth for POST-COMPACT inlining** — when this block changes, `role-pilot.md` § Operating Mode — Drive must be re-synced. Treat the two as a single specification with two surfaces; don't let them drift.
- **Cadence-axis exclusion is structural, not stylistic** — `Drive` and [[Lean]] are mutually exclusive (at most one cadence Trait per anchor). Any edit that softens this contradicts F077 and [[CAB Aspects]]; route such proposals through a feature, not a quiet edit here.
- **Use wiki-links for every named referent** ([[Lean]], [[SKL Mode Drive]], [[CAB Aspects]], F068, F077, F091) — don't inline definitions that already exist elsewhere. Names are load-bearing; renames must propagate.
- **History entries are append-only and dated** — record material changes (rule additions, threshold shifts, renames) with their F-number; don't rewrite past entries.
