# CAB UX Design
description:: facet spec for `{NAME} UX Design.md` — the *human* user-facing surface (CLI commands, screens, organization, naming, output shapes, error voice). Sibling peer to [[FCT API Design]] (programmatic surface).

UX Design specifies the **human user surface** of the anchor — how a person discovers, invokes, reads, and recovers from errors. It is sibling to [[FCT API Design]] (the *programmatic* user surface). The cut between them is **who the consumer is**, not where the surface lives: UX = human reading or invoking; API Design = code calling.

> [!info] Scope guard
> "UX" here is the broad sense — *user-facing surface* — not narrowly "visual interface." For a CLI scheduler the UX is the command set, output shapes, and error voice. For a GUI app it is screens + flows. For a skill repository (no pixels) it is the slash-command surface and organization. If the anchor has no human consumer, this facet is N/A; mark it `none` in [[FCT Status]] and omit the file.

The UX Design doc is the **current spec** — what the surface looks like today, not what alternatives were considered. Rationale lives in [[FCT Decisions]] or in the document's own *D-UX<n>* design-decision rows (see [[#RULESET R-ux|R-ux]]). Exhaustive flag/option reference for CLIs lives in the sibling [[FCT CLI]] doc; UX Design captures the *intent* (what commands exist, what they mean, what output they produce), CLI doc is the *reference* (every flag, every exit code).

## Location

`{NAME} Docs/{NAME} Design/{NAME} UX Design.md` — single-file form. Upgrade to anchor-folder form `{NAME} UX Design/` only when sub-surfaces grow beyond what one file holds cleanly (rare; almost always single-file).

Peer of [[FCT Architecture]] and [[FCT API Design]] under [[FCT Design Dispatch|Design]].

## Preface zone

Per [[progressive-disclosure]]:

- **TLDR** required — 3–8 short bullets covering: audience, the surface's spine (commands / screens / affordances), output-shape posture, error voice.
- **Figure** required — a representative visual of the surface. For a CLI: an annotated session transcript (one or two real commands with their output). For a GUI: a screen mockup. For a slash-command surface: a typed example with its inline result. SVG preferred; PNG acceptable.

## Required section spine

| H2 | What it carries |
|---|---|
| `## Audience` | One paragraph: who the human consumer is, what context they're in (terminal? Obsidian? browser?), what they know going in, what their goal is. Sets the frame for every following decision. |
| `## Entry-points` | The spine table. Every command / screen / affordance listed once with: name, one-line purpose, source story (US-<RID>-<N>). For CLIs: command name + one-line synopsis. For GUIs: screen name + one-line purpose. |
| `## Output shapes` | Both forms named explicitly: human-readable default (what the user sees with their eyes) AND structured opt-in (`--json`, machine-readable export, copyable payload). Realistic example for each. |
| `## Error voice` | The named error situations + the exact (or templated) message + exit code (CLI) or alert pattern (GUI). Tone is declared at the top (terse / friendly / verbose). |
| `## Discovery` | How the human finds the entry-points: `--help` text, dispatch table in `{NAME}.md`, hotkey hints, banner copy. Names the signal the user follows on first encounter. |
| `## Design decisions` | `D-UX<n>` rows: each load-bearing UX choice with rationale (why this and not the obvious alternative). Bridge to [[FCT Decisions]] for decisions that cite a rule set. |

Other H2s (e.g., `## Affordances`, `## Accessibility`, `## Telemetry`) join when applicable.

## Reference example

See [[CAE UX Design]] — the CAE scheduler shows the canonical shape for a CLI-shaped human surface. For a slash-command surface example see the future SKL UX Design (in progress).

## See also

- [[FCT API Design]] — sibling facet covering the programmatic surface.
- [[FCT CLI]] — exhaustive flag/exit-code reference (downstream of UX Design's *intent*).
- [[FCT Decisions]] — load-bearing decisions citing rules; bridge from D-UX rows.
- [[FCT Architecture]] — internal organization; UX entry-points typically map to architecture components.
- [[progressive-disclosure]] — preface zone discipline.
- [[markdown]] — markdown authoring discipline.


# RULESET R-ux
include::
description:: Rules for `{NAME} UX Design.md` — human user-facing surface intent.

Embedded rule set for the UX Design facet, co-located with the facet spec above per [[F133 — Rule sets folder convention + facet embedding|F133]]. Adopted via [[R-facet]] umbrella.

### RULE R-ux-01 — Preface zone carries TLDR + figure (checked)

The doc opens with a dispatch table, then a TLDR (3–8 single-line bullets), then a representative figure (annotated session transcript, screen mockup, or interaction snippet) — in that order — before the first body H2.

**Check pattern:** read the doc; assert dispatch table → TLDR → figure precede the first non-preface H2.

**Why:** the human reading a UX spec needs an at-a-glance pitch (TLDR) and a concrete instance (figure) before paragraphs. Abstract description alone is the failure mode.

### RULE R-ux-02 — Audience declared explicitly (stated)

The first body H2 is `## Audience` and names who the human consumer is, the context they're in, and what they're trying to do. One paragraph, not a list of personas.

**Check pattern:** assert `## Audience` exists as the first body H2; body is prose (not just a bulleted persona list); body names context (terminal / GUI / Obsidian / web) + intent.

**Why:** every downstream decision (output shape, error voice, naming) depends on the audience. Leaving it implicit forces the reader to reverse-engineer it.

### RULE R-ux-03 — Entry-points table is the spine (checked)

A `## Entry-points` H2 carries a single canonical table listing every human-invocable surface entry-point: name, one-line purpose, source story (`US-<RID>-<N>`) or link to its feature doc. No entry-point lives only in prose; every one is in the table.

**Check pattern:** parse the doc; gather all command-like or screen-like identifiers from H3s + prose; assert each appears in the spine table.

**Why:** the spine table is the contract surface — what the user can do. Prose-only entries are invisible to grep, to dispatch generation, and to audits.

### RULE R-ux-04 — Output shapes named both human + structured (stated)

The `## Output shapes` H2 names both forms with a realistic example for each: (a) human-readable default (what the user sees with their eyes), (b) structured / machine-readable opt-in (`--json`, `--csv`, exportable payload). Even a single-shape surface declares the absence of the other explicitly.

**Check pattern:** assert `## Output shapes` exists; assert two named sub-shapes (default + structured) OR an explicit statement "no structured output — human only" with rationale.

**Why:** scriptability and pipe-ability are first-class affordances of a CLI; assuming the human-readable form is "the output" silently breaks every downstream `jq` / `grep` consumer. Naming the structured opt-in upfront forces the decision.

### RULE R-ux-05 — Error voice declared once at top (sampled)

The `## Error voice` H2 opens with a one-line declaration of tone (terse / friendly / instructive) + the standard error envelope (prefix, exit code or alert pattern), then enumerates the named error situations with their messages.

**Check pattern:** assert `## Error voice` exists; first paragraph names tone + envelope; subsequent rows enumerate named failures.

**Why:** consistency in error voice IS the UX — switching between terse and verbose, between "error:" and "ERROR:", between exit 1 and exit 2 fragments the user's mental model.

### RULE R-ux-06 — Discovery mechanism named (stated)

A `## Discovery` H2 (or equivalent) names how the human finds the entry-points on first encounter — `--help` text, dispatch table in `{NAME}.md`, hotkey, banner copy, web nav. Don't assume discovery is obvious.

**Check pattern:** assert `## Discovery` exists OR an inline `discovery::` line in the spine table; body names the surfacing channel.

**Why:** a surface without discovery is invisible; UX Design is incomplete without naming how the user finds the surface in the first place.

### RULE R-ux-07 — Design decisions captured as D-UX<n> rows (sampled)

Load-bearing UX choices (a chosen affordance over an obvious alternative, a chosen output shape over a sibling, a chosen naming convention) appear as `D-UX<n>` rows under `## Design decisions` with: choice, alternatives considered, rationale (one or two sentences).

**Check pattern:** sample design decisions in CAE UX Design and SKL UX Design; assert each row has Choice + Alternatives + Rationale columns.

**Why:** UX choices look obvious after the fact but were contingent at the time. Capturing them as auditable rows lets the next reviewer reverse-engineer intent without re-litigating the decision.

### RULE R-ux-08 — Distinct from API Design, CLI doc, Architecture (stated)

UX Design owns the *intent* of the human-facing surface. It is NOT:

- The programmatic surface — that's [[FCT API Design]].
- The exhaustive flag/option reference — that's [[FCT CLI]] (for CLI anchors).
- The internal organization — that's [[FCT Architecture]].

When UX Design starts listing every flag, or describing function signatures, or explaining module structure, it is leaking the wrong content. Migrate the leak to the sibling facet.

**Check pattern:** sample UX Design docs; assert no flag-by-flag reference tables (CLI scope), no function signatures (API scope), no module dependency narrative (Architecture scope).

**Why:** facet leakage erodes the cut. The reader who wants the programmatic surface goes to API Design; if it lives in UX, they don't find it where they look.

# BRIEF

- **This file is the facet spec for `{NAME} UX Design.md`** — it defines the shape of every anchor's human user-facing surface doc and embeds [[#RULESET R-ux|R-ux]] as the audited rule set. Edits here change the contract every UX Design instance must meet.
- **Not for per-anchor UX content** — concrete commands, screens, and error messages belong in each anchor's `{NAME} UX Design.md`. This file specifies the *required section spine and rules*, not exemplar entry-points or output transcripts.
- **Inclusion test** — a change belongs here only if it is a structural rule, required section, or load-bearing definition that applies to *every* UX Design doc across anchors. Anchor-specific guidance, worked examples, or one-off conventions go in [[CAE UX Design]] (canonical exemplar) or the anchor's own doc.
- **Preserve the facet-cut boundaries** — UX Design owns *human-facing intent*; [[FCT API Design]] owns *programmatic surface*, [[FCT CLI]] owns *exhaustive flag reference*, [[FCT Architecture]] owns *internal organization*. When editing, never absorb content that belongs in a sibling facet; rule R-ux-08 is the load-bearing guard.
- **Rule set is co-located, not separate** — the `# RULESET R-ux` H1 at the bottom is part of this file per F133. When adding or revising rules, update the rule block in place; do not split it into a sibling file or duplicate it in [[FCT Rules]].
- **Cross-references are load-bearing** — links to [[FCT API Design]], [[FCT CLI]], [[FCT Decisions]], [[FCT Architecture]], [[progressive-disclosure]], and [[CAE UX Design]] anchor the facet's place in the wider blueprint. Renaming or moving any of those files requires updating the wiki-links here in the same commit.
- **Preface zone discipline applies to instances, not this spec** — `R-ux-01` mandates TLDR + figure for each `{NAME} UX Design.md`. Don't import a figure or session transcript here; this is the rulebook, not an instance of the rule.
