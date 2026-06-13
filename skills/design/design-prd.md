# Design PRD — Author or assess `{NAME} PRD.md`

Phase 1 of the canonical `/design` sequence (PRD → UX → API → Architecture → Testing → Roadmap). Authors `{NAME} Design/{NAME} PRD.md` per the [[FCT PRD]] facet.

**Two modes** — the same skill drives both:

- **Bootstrap mode** — no PRD exists. Agent gathers context, drafts the standard section spine, glances the file, iterates with the user.
- **Assess mode** — PRD already exists. Agent surveys it against the [[FCT PRD#RULESET R-prd|R-prd]] rules + section spine + depth heuristics, glances the file, reports findings in chat, and waits for direction (drive end-to-end / one-move-at-a-time / converse).

The mode is detected, not invoked — `/design prd` does the right thing based on what's on disk.

## When to Use

- User invoked `/design prd` directly.
- Bare `/design` auto-dispatched here (canonical phase 1 — `{NAME} Status.md` shows `prd:: none` or `prd:: MVP-agent` and the user is iterating).
- User said "let's design the PRD" / "let's flesh out what this product is" / "is the PRD done?"

## Runbook

### 1. Locate the PRD

1. Walk up from `cwd` to nearest `.anchor`. Check whether `{anchor}/{NAME} Design/` exists (the gate per [[FCT Design]]). If absent, `/design` (the orchestrator) will have already offered to scaffold — this sub-skill assumes the folder exists when invoked.
2. Look for the PRD at, in priority order:
   - `{anchor}/{NAME} Design/{NAME} PRD/{NAME} PRD.md` (folder form per [[FCT Stories]])
   - `{anchor}/{NAME} Design/{NAME} PRD.md` (single-file form)
   - Legacy: `{anchor}/{NAME} Docs/{NAME} Plan/{NAME} PRD.md` — flag for migration but read as input
3. Branch:
   - **Found** → § 2 (Assess mode)
   - **Not found** → § 3 (Bootstrap mode)

### 2. Assess mode (existing PRD)

The whole point: don't silently edit. Survey first, report, glance, wait.

#### 2a. Silent survey

Read the PRD, then evaluate against three dimensions:

**Rule check — `R-prd` (per [[FCT PRD#RULESET R-prd|the embedded ruleset]]):**

| Rule | What it checks |
|---|---|
| R-prd-01 | Location is `{NAME} Design/{NAME} PRD.md` or folder form |
| R-prd-02 | Body-only, no YAML frontmatter (first non-blank line is `# `) |
| R-prd-03 | `description::` is the second non-blank line, no `::` tokens in value |
| R-prd-04 | Required sections present in declared order |
| R-prd-05 | User stories use `US-<RID>-<N>` numbering |
| R-prd-06 | No legacy `{NAME} Open Questions.md` file alongside |
| R-prd-07 | Design Workflow references modern phase names (Architecture, Testing, Decisions) |
| R-prd-08 | No per-doc `status::` field (centralized in `{NAME} Status.md`) |
| R-prd-09 | No legacy `## Design Constraints` (DC-N) section |

**Section spine** — for each required section, note presence + a rough size signal:

- Overview — present? word count?
- Design Workflow — present? row count?
- Goals — present? bullet count?
- Non-Goals — present? bullet count?
- User Stories — present? story count? matches `US-<RID>-<N>`?

**Depth heuristics** — flag thin sections:

- **Overview**: < 2 sentences = thin; doesn't name the user role = ambiguous.
- **Goals / Non-Goals**: < 2 bullets = thin; phrased as features (verbs) vs outcomes (nouns) = ambiguous.
- **User Stories**: bare canonical sentence with no acceptance criteria and the product clearly has more behavior to spec = candidate for [[FCT Stories]] folder-form extraction.
- **Design Workflow**: doesn't link to all five downstream phases (PRD → Architecture → Testing → Decisions → Track) = incomplete.

#### 2b. Glance the file

Open the PRD so the user can read along while the survey lands in chat:

```bash
open "{anchor}/{NAME} Design/{NAME} PRD.md"
```

(Or the folder-form path if applicable.)

#### 2c. Report — structured, in chat

The canonical report shape:

```
/design prd — {NAME} PRD survey

Rules (R-prd): N/9 pass.{ violations list, or "all pass."}

Section spine:
  • Overview        — present, <one-line signal>     {✓|thin|missing}
  • Design Workflow — present, N rows                {✓|thin|missing}
  • Goals           — present, N bullets             {✓|thin|missing}
  • Non-Goals       — present, N bullets             {✓|thin|missing}
  • User Stories    — N stories (US-{RID}-1..N)      {✓|thin|missing}

Status (per {NAME} Status.md): prd:: <current cell>

Suggested next moves:
  (A) <specific small thing — e.g. "draft 3 Non-Goal bullets from the existing CLI-only / no-distributed framing">
  (B) <another small thing>
  (C) <"PRD is at a clean MVP — propose state status set prd MVP-agent" if no violations + sections substantive>
```

End the report by asking the user how to proceed: drive end-to-end, pick one move, or just discuss.

#### 2d. Iterate

Based on the user's response:

- **"go" / "drive" / `'` / `/crank`** — execute all the suggested moves end-to-end. For each move, edit the PRD, glance (only when user-facing review needed), surface genuine questions via `/ask --doc` per § 5.
- **Pick one** ("do A") — execute that one move, re-survey, re-report.
- **Discuss** — answer the user's questions; iterate the report; no edits until directed.

### 3. Bootstrap mode (no PRD)

Used when § 1 found no PRD at any of the candidate paths.

#### 3a. Gather context

Read in this order; stop when you have enough to draft:

1. `{anchor}/.anchor` — `traits:`, `description:` if present
2. `{anchor}/{NAME}.md` — the anchor page (often has framing prose)
3. `{anchor}/CLAUDE.md` — project mission, scope hints
4. `{anchor}/README.md` if present
5. `{anchor}/{NAME} Design/{NAME} Architecture.md` if it pre-dates the PRD (rare; usually PRD comes first, but it happens)

#### 3b. Draft the initial PRD

Create `{anchor}/{NAME} Design/{NAME} PRD.md` (single-file form by default) with the standard section spine per [[FCT PRD]] § Standard section order:

```markdown
# {NAME} PRD
description:: <one-line tagline — product type + intent + key trait>

| -[[{NAME} PRD]]- | : <description><br>→ <breadcrumb> |
| --- | --- |
| [[{NAME} Architecture]] | system-architecture story (peer Design facet) |
| [[{NAME} Testing]] | testing strategy + proposed-tests overview |
| [[{NAME} Decisions]] | load-bearing decisions citing rules |
| [[FCT PRD]] | facet spec this doc follows |
| --- | |

## Overview

<1-2 paragraphs synthesized from context>

## Design Workflow

| Step | Document | Purpose |
|---|---|---|
| 1 | [[{NAME} PRD]] | Clarify requirements and scope |
| 2 | [[{NAME} Architecture]] | Design the technical architecture |
| 3 | [[{NAME} Testing]] | Strategy + proposed-tests overview |
| 4 | [[{NAME} Decisions]] | Encode load-bearing decisions citing R-rules |
| 5 | [[{NAME} Track]] | Roadmap + features implementing the stories below |

## Goals

- <draft from context>

## Non-Goals

- <draft from context — be explicit about what's out of scope>

## User Stories

### US-{RID}-1: <Title from context>
As a <role>, I want <goal> so that <reason>.

### US-{RID}-2: ...

## See also

- [[FCT PRD]] — facet spec
- [[FCT Stories]] — stories sub-facet (activates if stories grow)
- [[{NAME} Architecture]], [[{NAME} Testing]], [[{NAME} Decisions]] — peer Design facets
```

Body-only — **no YAML frontmatter**. Use `description::` inline (per R-prd-02 and R-prd-03).

#### 3c. Glance and report

Open the new PRD and tell the user it's a first draft to react to:

```
/design prd — {NAME} PRD bootstrap

Drafted from: {anchor}/.anchor, {NAME}.md, CLAUDE.md.

Spine populated:
  • Overview — 1 paragraph
  • Design Workflow — 5 rows
  • Goals — N bullets
  • Non-Goals — N bullets
  • User Stories — N stories (US-{RID}-1..N)

Genuine guesses I made (worth your eye):
  • <thing 1 — what was inferred and why>
  • <thing 2>

Suggested next moves:
  (A) Review Overview — does the framing match what you wanted?
  (B) Walk § User Stories — confirm or refine each
  (C) "Looks good for an MVP draft" → `state status set prd MVP-agent`
```

#### 3d. Iterate

Same as § 2d above.

### 4. Fleshing-out checklist (used during iteration)

Use these as internal questions when surveying or refining a section. They become user-facing `/ask` questions only when genuinely undecidable from context.

- Can the Overview explain what this is and why in two sentences? If not, frame is unclear.
- What's the smallest version that would be useful? That's the v1 scope.
- For every goal, what would you cut with half the time? That separates core from nice-to-have.
- Have you named every role that interacts with the system — not just primary users?
- Could a worker read each story and start building without coming back to ask? If not, story needs more.
- Do stories cover the full lifecycle — setup, daily use, error recovery, maintenance?

### 5. Surface open questions OR agent-resolutions (when iteration hits a decision)

When iteration surfaces a decision, route it through [[ask]]:

```bash
/ask --doc "{anchor}/{NAME} Design/{NAME} PRD.md" "<question>"
```

The decide-vs-ask judgment **belongs to the /ask discipline**, not this skill. The short version of what /ask enforces: if the choice is **reversible AND the user will see the wrong call and easily redirect**, the agent should decide and log under `## Resolved` as an agent-made-this-call entry — not as a question. Only when the decision is irreversible, invisible, or genuinely undecidable from context does it become a `## Open Questions` Q.

See [[ask]] and [[DSC ask-format]] for the full lifecycle (Q-numbering, recommendation strength, Resolved migration, Q.md dashboard sync).

### 6. Promote status

Status lives in `{NAME} Track/{NAME} Status.md` per [[FCT Status]]. When the PRD survives the rule check AND the section spine is substantive:

```bash
~/.claude/skills/workflow/scripts/state --anchor {NAME} status set prd MVP-agent --note "<one-line — what's covered>"
```

User stamps `MVP-user` via natural-language confirmation ("PRD looks good"); this lets the `/design` picker advance to the next phase.

## File location

`{anchor}/{NAME} Design/{NAME} PRD.md` (single-file form, default) or `{anchor}/{NAME} Design/{NAME} PRD/{NAME} PRD.md` (folder form, when stories migrate to [[FCT Stories]]).

Legacy `{anchor}/{NAME} Docs/{NAME} Plan/{NAME} PRD.md` is deprecated per F094. If found at the legacy path, flag for migration but read as input during assessment.

## File shape

**Read [[FCT PRD]] before authoring.** The facet spec is the canonical recipe — required sections, dataview fields, preface zone (TLDR explicitly NOT required for PRDs), section spine. This sub-skill owns the *process*; the facet owns the *shape*. If anything in this skill conflicts with the facet, the facet wins.

Worked example to crib from: [[CAE PRD]].
Audit rules to honor: [[FCT PRD#RULESET R-prd|R-prd]] (9 rules).

## Anti-patterns

- **Don't bypass survey-and-report on an existing PRD.** Assess first, share findings in chat, then drive edits with consent. Mechanical normalization (fixing a stale link target, renaming `US-1` → `US-<RID>-1`, rewriting frontmatter to body-only) is fine to apply silently as part of driving — those are facet-rule applications. Editorial changes to user-authored content (rewriting an Overview paragraph, adding or dropping a Goal, restructuring User Stories) need to be surfaced before they land.
- **Don't gate by separate ceremony.** Promotion to `MVP-agent` is a `state status set` call, not a Verify row or a banner. The user-grade `MVP-user` comes from natural-language confirmation.
- **Don't ask "should we have a PRD?"** — `/design prd` was invoked. Author it (bootstrap) or assess it (existing).

(For the decide-vs-ask judgment on open questions, defer to [[ask]] — that discipline owns the lifecycle, not this skill. For shape rules — body-only, no DC-N, no per-doc `status::`, no separate Open Questions file — defer to [[FCT PRD#RULESET R-prd|R-prd]]; the audit catches them mechanically.)

## Related

- Facet spec: [[FCT PRD]] (with embedded [[FCT PRD#RULESET R-prd|R-prd]])
- Worked example: [[CAE PRD]]
- Stories sub-facet: [[FCT Stories]] (activates if stories grow)
- Parent orchestrator: [[design]]
- Sibling sub-skills: [[design-ux]], [[design-architect]], [[design-testing]], [[design-roadmap]]
- Status tracking: [[FCT Status]]
- Open-question discipline: [[DSC ask-format]]
- Question authoring skill: `/ask --doc`
- F130 (state script + central Status), F094 (Design folder restructure)
