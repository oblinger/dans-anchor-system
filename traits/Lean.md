---
description: Lean Trait — cautious, distrust-the-foundation, minimum-thoroughness trade-off posture. The cadence sibling to Drive. Composable capability trait.
---

# Lean

The cadence Trait declaring an anchor runs in cautious, distrust-the-foundation posture — the declarative per-anchor form of `/fortify`, mutually exclusive with [[Drive]].

## What it is

**Lean declares the agent operates with a cautious, foundation-distrusting posture.** Use it when the work has stopped converging — same bug recurs, fixes don't stick, tests pass but the system misbehaves, or the agent's mental model and reality have clearly diverged. The stance is *"the obvious read of the situation is probably wrong; fortify what's already here before adding more."*

Lean is the sibling cadence trait to [[Drive]] — the two are mutually exclusive cadence postures. Lean is the per-anchor declarative form of the `/fortify` methodology (`~/.claude/skills/fortify/SKILL.md`). The `/fortify` slash command invokes the same posture for a single turn or block of work; declaring `Lean` as an anchor Trait makes that posture the default for the anchor.

Lean is **orthogonal to identity traits**. `Code + Track + Lean + PR` is the canonical "production code project being fortified" combination — the project has high enough blast radius (PR) and a current foundation-trust problem (Lean).

## How it's detected

- **Trait:** `Lean` appears in the anchor's `.anchor` `traits:` list (one-line lookup; no file inference per [[CAB Aspects]]).
- An anchor without `Lean` in its `traits:` list runs in [[Drive]] (the cadence default).
- `Lean` and `Drive` are mutually exclusive — declaring both is illegal.

## The load-bearing rules

(Authoritative agent-facing form lands in `role-pilot.md` POST-COMPACT RELOAD § Operating Mode — Lean when Lean is the resolved cadence. Full user-facing spec: [[SKA fortify]] / the `fortify` skill. The rules in summary:)

1. **Distrust four things** when entering Lean: the information feeding conclusions (logs, errors), the structure of the code (hidden coupling), the tests that pass (coverage gaps, weak assertions), and the agent's own mental model.
2. **Re-read existing evidence first.** Before adding more logs or tests, re-read what's already there for clues missed.
3. **Add coverage and rigor — silently and aggressively.** Realistic edge cases, error paths, boundary conditions. Tighten weak assertions that pass without actually verifying the property they claim. **More tests, not fewer** is the default; the user does not need to be asked.
4. **Pin invariants and replace silent fallbacks with explicit failures.** Impossible states surface early, not silently.
5. **Application-shape changes require approval.** Bug fixes, hardening, test expansion, log expansion, invariant pinning — autonomous. Anything that changes how the application behaves visibly, alters a public API, or reshapes architecture — escalate via [[query]].
6. **Wall-clock cost is irrelevant; user-interruption cost is the constraint.** Take longer; ask less. **Batch open questions, never trickle them.**
7. **Update the model, then resume cranking.** Once the foundation is fortified, re-derive the working hypothesis from the new evidence — do not re-use the old one.

## Wiring an anchor for Lean

1. **Declare the trait.** Add `Lean` to `.anchor` `traits:` list — e.g., `traits: [Code, Track, Lean, PR]`. (Replace any prior `Drive` declaration — they're mutually exclusive.)
2. **No structural changes required.** Lean is a *behavioral* trait — shapes how the agent makes recurring trade-off decisions, not what the anchor folder contains.
3. **Switch back to Drive when the foundation is firm.** Lean is a transient posture for distrust-the-foundation work, not a permanent state. Once tests cover the gaps, invariants are pinned, and the working hypothesis re-derives cleanly, edit `.anchor` to put `Drive` back (or simply remove `Lean` — Drive is the default).

## Format

Lean is a behavioral mode, not a structural one. Compositional expectations:

- **Composes with any identity trait** (Code / Topic / Paper / Skill / Simple) and any Git-aspect trait (Commit / PR / NoGit).
- **Mutually exclusive with [[Drive]]** — exactly one cadence Trait at a time.

## Constraints

- **Cardinality: at most one cadence Trait** per anchor. `Lean` + `Drive` together is illegal.
- **Composition.** Legal with all identity traits and all Git-aspect traits. **Excludes `Drive`** — the two are mutually exclusive cadence postures.

## Expected Usage

- **Transient by intent.** Lean is the posture for work that's not converging. Most anchors live in [[Drive]]; an anchor declares `Lean` when it enters a fortification phase (a recurring bug, a flaky test suite, a divergent mental-model period). Once the foundation is firm, the anchor returns to Drive.
- **Per-turn invocation via `/fortify`** — even when an anchor declares `Drive`, the user can invoke `/fortify` to flip to Lean posture for a single turn / block of work without changing the declared Trait. See `~/.claude/skills/fortify/SKILL.md`.
- **NOT for "be careful"** in the general sense. Lean is "distrust-the-foundation" specifically. Anchors that just want careful work declare neither `Drive` nor `Lean` (Drive default with the user's `/fortify` as needed). Declaring `Lean` permanently is unusual.
- **Naming history.** "Lean" is the bare-noun form per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] Q7. Older docs may use "Cautious" as descriptive English for the same posture; the Trait name is canonical.

## Triggers

(Per [[F091 — Trigger discipline]]. Declared `compact` trigger — when this Trait is active on the cwd anchor, the prose below is what the agent reads at POST-COMPACT reload.)

### compact

- **Operating Mode — Lean.** Cautious, distrust-the-foundation posture. Use when work has stopped converging — same bug recurs, fixes don't stick, tests pass but system misbehaves. The stance is *"the obvious read is probably wrong; fortify the foundation."*
  - **Distrust four things:** (1) the information feeding conclusions (logs, errors — may be misleading); (2) the code structure (hidden coupling enabling fragility); (3) tests that pass (coverage gaps; weak assertions that don't verify what they claim); (4) the agent's mental model itself.
  - **Re-read existing evidence first** before adding more logs/tests. Wrong log file, wrong place in log, wrong process attribution — common misses.
  - **More tests, not fewer.** Realistic edge cases, error paths, boundary conditions get tests. Tighten weak assertions. Red-batch then drive green together. **Never ask "should I add more tests or fewer?" — the answer is always more.**
  - **Pin invariants. Replace silent fallbacks with explicit failures.** Impossible states surface early.
  - **Wall-clock cost is irrelevant; user-interruption cost is the constraint.** Take longer; ask less. **Batch open questions via [[query]] — never trickle.**
  - **Bug fixes, hardening, test expansion, log expansion, invariant pinning — autonomous.** Application-shape changes (visible behavior, public API, architectural reshape) require approval.
  - **Resume Drive when foundation is firm.** Re-derive the working hypothesis from new evidence — do not re-use the old one. When the test suite covers the gaps and the model converges, switch back.
  - Full user-facing spec: `~/.claude/skills/fortify/SKILL.md`. Mode framework: [[SKL Mode]].

## Skills and audits that attach

- **`/fortify`** is the slash-command form of Lean posture for per-turn invocation. Lean as a declared Trait makes that posture the anchor's default.
- **Affects every state-touching skill on a Lean-declared anchor** — `/feature`, `/mint`, `/groom`, `/audit`, `/ask`, etc. Each runs with the cautious posture: more tests, batch questions, fortify before adding.
- **Audit:** `/audit aspects` (proposed, F090 Phase 6) will check the Drive ⊕ Lean exclusion (only one cadence Trait).
- **Discipline:** `~/.claude/skills/fortify/SKILL.md` (the methodology); this Trait spec is the declarative anchor-level activation form.

## History

- **2026-05-XX** — "Cautious" posture introduced as the trade-off-posture sibling to Drive in [[SKL Mode]]. Initially had no SKL doc of its own — invoked solely via `/fortify`.
- **2026-06-01** — Renamed to bare-noun `Lean` per [[F077 — PR mode — mode-as-trait architecture with per-anchor opt-in|F077]] Q7. Promoted to first-class CAB Trait per F077 Q11.
- **2026-06-04** — Trait spec created (this file) with F091 `compact` trigger declaration. Codifies the existing `/fortify` methodology as a declarable per-anchor Trait.

# BRIEF

- **This file is the Trait spec for `Lean`** — the declarative authority for how the cadence posture is detected (`.anchor` `traits:` list), what rules it activates, and what its `compact` trigger surfaces at POST-COMPACT reload. Edit here when the Trait's detection, rules, or trigger payload changes.
- **NOT for the methodology itself** — the operational "how to fortify" content lives in `~/.claude/skills/fortify/SKILL.md`. Keep this file declarative (what the Trait IS, how it's wired); push procedural how-to to the skill. The § The load-bearing rules section is a *summary* with a pointer, not a re-spec.
- **The Drive ⊕ Lean mutual exclusion is load-bearing** — both the § How it's detected and § Constraints sections state it. Don't soften the rule or allow "both at once" semantics; the cadence-Trait cardinality (at most one) is what `/audit aspects` will enforce.
- **The `compact` trigger payload is what the agent actually reads at reload** — bullets under `### compact` are agent-facing operating-mode instructions, not user-facing explanation. Keep them imperative, tight, and aligned with `role-pilot.md` POST-COMPACT § Operating Mode — Lean. When the methodology evolves in `/fortify`, mirror the change here.
- **Cross-references that must stay aligned:** [[Drive]] (sibling cadence Trait — exclusion must be symmetric), [[CAB Aspects]] (Trait detection rule), [[SKL Mode]] (mode framework parent), F077 (naming + first-class promotion), F091 (trigger discipline). Breaking any of these silently desyncs the cadence-Trait subsystem.
- **Do not pile non-cadence-Trait content here** — anchor-local rules, identity-Trait content, or `/fortify` runbook details belong elsewhere (anchor `Decisions.md`, the relevant identity-Trait file, or the fortify skill respectively).
