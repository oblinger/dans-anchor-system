---
name: design
description: >
  Federated design orchestrator for a project anchor. Walks through the canonical design
  phases — PRD → UX → API → Architecture → Testing → [both accepted gate] → Roadmap
  (with proactive feature docs) — detecting which artifacts are complete vs. missing, and
  dispatching to per-artifact sub-skills (`design-prd`, `design-ux`, `design-architect`,
  `design-testing`, `design-roadmap`). Sibling to `/crank` in the Drive cluster; the outer-loop
  orchestrator at the center of the Design cluster. Use when the user says: "let's design this",
  "design", "/design", "what's the design state of this anchor", "/design prd", "/design architect",
  "/design testing", "/design roadmap", or asks where in the design sequence the project is.
  Gate is folder-presence per [[CAB Design]] — `{NAME} Design/` exists → operate; absent → offer to scaffold. Code-trait check retired 2026-06-10. Initially supports anchors with code-shaped artifacts; broader applicability (Paper / Topic / Simple) covered as those traits land.
tools: Read, Write, Edit, Bash, Glob, Grep, Agent
user_invocable: true
---

# Design — Federated Design Orchestrator

`/design` walks a project anchor through its design artifacts in canonical order, detecting state, surfacing gaps, and dispatching to per-artifact sub-skills. Sibling to `/crank` in the Drive cluster; the center of the Design cluster.

**Renamed from `/plan` 2026-06-10 per [[F136 — Plan→Design skill rename]].** The verb that best describes walking PRD → UX → API → Architecture → Testing → Roadmap is **design**, not plan. (Roadmap, the bridge to execution, is the one phase that's more "plan" than "design" — but the bulk of the skill's work is design.) All sub-skills renamed `plan-*` → `design-*` in the same pass.

## Canonical phase order

The skill walks these phases in this exact order. Each phase has a primary artifact (a file the sub-skill authors) and an optional gate at the end.

| # | Phase | Sub-skill | Primary artifact | Gate after |
|---|---|---|---|---|
| 1 | PRD | `/design prd` | `{NAME} Design/{NAME} PRD.md` | — |
| 2 | UX *(if applicable)* | `/design ux` | `{NAME} Design/{NAME} UX.md` | — |
| 3 | API *(if applicable)* | `/design api` | `{NAME} Design/{NAME} API.md` | — |
| 4 | Architecture | `/design architect` | `{NAME} Design/{NAME} Architecture.md` | **Gate 1** — `status:: accepted` on Architecture |
| 5 | Testing | `/design testing` | `{NAME} Design/{NAME} Testing.md` | **Gate 2** — `status:: accepted` on BOTH Architecture AND Testing |
| 6 | Roadmap + feature docs | `/design roadmap` | `{NAME} Track/{NAME} Roadmap.md` + per-milestone `Features/M*.md` | — |
| 7 | Design complete | — | — | Transition to Drive (`/crank`) |

**Gate semantics:** Gate 1 protects entry to Testing authoring. Gate 2 protects entry to Roadmapping. A gate is "passed" when the relevant artifact's top-of-file `status::` dataview field reads `accepted`. The user sets the field by saying "the architecture is accepted" / "the testing is accepted" (the agent watches for that phrase and updates the field) or by editing directly. Gates are sticky: once `accepted`, no re-prompt.

The phrasing "satisfied with this as a starting architecture / testing discipline" is load-bearing: gates protect against starting *next-phase work* on visibly incomplete prior work — they do not mean "perfect." Iteration continues throughout Drive.

## State model

**Storage (F130, preferred):** centralized `{NAME} Status.md` facet in the Track folder, carrying one `::` dataview line per design facet:

```
prd:: MVP-agent (2026-06-08) — covers golden path; edge cases unspecified
ux:: none
architecture:: MVP-user (2026-06-07) — services + data flow; deployment TBD
testing:: none
roadmap:: none
```

Cell vocabulary, ordered low → high: `none < MVP-agent < MVP-user < Full-agent < Full-user`. All writes go through `state status set` (no hand-editing the file); reads via `state status show`.

**Storage (legacy):** per-artifact `status::` dataview field at the top of each design doc. Valid values for Architecture and Testing: `drafting | in-review | accepted`. Retained as fallback when `{NAME} Status.md` is absent.

**Resolution on bare `/design`:**

1. **Check `{NAME} Status.md`.** If present, it's authoritative. Run:
   ```bash
   ~/.claude/skills/workflow/scripts/state --anchor {NAME} status show
   ```
   Walk the output in declared order (`prd`, `ux`, `architecture`, `testing`, `roadmap`). Pick the **first** facet whose cell is lowest on the ladder above; dispatch to the corresponding sub-skill (`design-prd`, `design-ux`, etc.). Sub-skills self-promote to `*-agent` at completion via `state status set <facet> <new-cell> --note "<one-line>"`; user-stamped `*-user` comes from explicit review ("PRD looks good for MVP" → agent runs `state status set prd MVP-user --note "<...>"`).
2. **Fallback when `{NAME} Status.md` absent.** Apply the legacy per-artifact inference below.
3. **`/design <facet>` bypasses the picker entirely** — works on already-approved facets too (that's just more design on something).

**Legacy inference (fallback when no Status.md):**
- PRD exists with at least one user story → past PRD-drafting.
- PRD declares UI requirement AND `{NAME} UX.md` has concrete UI shape → past UX.
- PRD declares API surface AND `{NAME} API.md` has concrete API shape → past API.
- Architecture exists with at least one named subsystem → architecting in progress.
- Architecture has `status:: accepted` → Gate 1 passed; proceed to Testing.
- Testing exists with proposed strategy → testing in progress.
- Architecture AND Testing both `accepted` → Gate 2 passed; proceed to Roadmap.
- Roadmap has at least one milestone → roadmapping in progress.

If a declared `Status.md` cell disagrees with inferred state on the artifact body (e.g., `prd:: Full-user` but the PRD doc has only a frontmatter and one user story), surface the discrepancy in chat. Declared cell wins; the surface is a check on user intent.

## Runbook — bare `/design`

1. **Detect anchor + Design facet.** Walk up to nearest `.anchor` file. Check whether `{anchor}/{NAME} Design/` exists. **If absent**, offer to scaffold per [[CAB Design]] § Scaffolding (creates folder + .anchor + Design.md dispatch + PRD/Architecture/Testing/Decisions with required-section spines + initializes Status.md). On user confirmation, scaffold and proceed; on decline, stop with one-line explanation. **If present**, proceed to § 2. The Code trait field in `.anchor` is NOT consulted (deprecated as the gate 2026-06-10; F140 sweeps it from anchors that now have Design folders).
2. **Read design status.** Run `state --anchor {NAME} status show` to get the per-facet cell map. If `{NAME} Status.md` is absent the script auto-creates it with all facets at `none`.
3. **Build gap table.** Render the status one line per facet:
   ```
   prd:            MVP-user (2026-06-08) — user-confirmed for v1
   ux:             MVP-agent (2026-06-07) — golden path; edges unspecified
   architecture:   none
   testing:        none
   roadmap:        none
   ```
4. **Pick the dispatch target.** Walk facets in declared order (`prd`, `ux`, `architecture`, `testing`, `roadmap`); pick the FIRST facet at the lowest cell on `none < MVP-agent < MVP-user < Full-agent < Full-user`. The table above picks `architecture` (first `none`).
5. **Auto-dispatch.** Invoke the matching sub-skill: `/design architect` for the example above. The user may redirect mid-dispatch by saying "actually let's do UX first" or by typing `/design ux` directly.
6. **Self-promote at completion.** When the sub-skill judges its work sufficient, it ends with:
   ```bash
   state --anchor {NAME} status set <facet> MVP-agent --note "<one-line rationale>"
   ```
   User stamps `*-user` via natural-language ("PRD looks good for MVP" → agent runs `state status set prd MVP-user --note "<...>"`).

## Runbook — `/design <artifact>`

Direct invocation of a sub-skill, bypassing the bare-state-scan.

| Verb | Dispatches to |
|---|---|
| `/design prd` | `design-prd.md` |
| `/design ux` | `design-ux.md` |
| `/design api` | `design-architect.md` § API section (or future `design-api.md` when commissioned) |
| `/design architect` | `design-architect.md` |
| `/design testing` | `design-testing.md` |
| `/design roadmap` | `design-roadmap.md` |
| `/design gate architecture` | shortcut for *"set `status:: accepted` on `{NAME} Architecture.md`"* |
| `/design gate testing` | shortcut for *"set `status:: accepted` on `{NAME} Testing.md`"* |

## Runbook — natural-language gate phrases

The skill watches for these phrases in user messages while a design artifact is being authored:

- *"the architecture is accepted"* / *"I accept the architecture"* / *"architecture looks good"* → set `status:: accepted` on `{NAME} Architecture.md`.
- *"the testing is accepted"* / *"testing looks good"* / *"the testing strategy is accepted"* → set `status:: accepted` on `{NAME} Testing.md`.

After updating, glance the affected file so the user can verify the field landed.

## Dispatch table

| Sub-skill | File | Authors |
|---|---|---|
| design-prd | [[design-prd]] | `{NAME} Design/{NAME} PRD.md` (per CAB PRD facet) |
| design-ux | [[design-ux]] | `{NAME} Design/{NAME} UX.md` (per CAB UX Design facet) |
| design-architect | [[design-architect]] | `{NAME} Design/{NAME} Architecture.md` + subsystems (per CAB Architecture facet) |
| design-testing | [[design-testing]] | `{NAME} Design/{NAME} Testing.md` (per CAB Testing facet) |
| design-roadmap | [[design-roadmap]] | `{NAME} Track/{NAME} Roadmap.md` + per-milestone `{NAME} Features/M*.md` |

## Anti-patterns

- **Don't ask "which artifact next?"** — the canonical phase order is the answer. Bare `/design` auto-dispatches; user redirects if they want a different order.
- **Don't gate by separate ceremony.** Gates are encoded in the doc's `status::` field, NOT in a parallel gate registry.
- **Don't write tests during `/design testing`.** That phase writes the *strategy + proposed-tests overview* (the [[CAB Testing]] facet); actual test code comes during Drive (`/code test` or `/mint`).
- **Don't author roadmap milestones before Gate 2.** The roadmap phase is gated on both Architecture and Testing being `accepted`.
- **Don't reorder phases silently.** If the user redirects ("let's do UX first"), comply for that session, but the canonical order remains the default for future invocations.

## When NOT to use this skill

- **Implementation work** — that's `/mint` / `/crank` / `/code <verb>`.
- **Single-feature design** — that's `/feature` (which inherits from the design artifacts).
- **Anchors without a Design folder** — `/design` offers to scaffold one; if you don't want a designed lifecycle, decline and use other workflows (e.g., bare `/mint` for one-off scripts, anchor-page edits for static content).
- **Anchor creation itself** — `/code anchor` (not migrated; structural, not design).

## Related

- Per-phase sub-skills: [[design-prd]], [[design-ux]], [[design-architect]], [[design-testing]], [[design-roadmap]]
- CAB facets: [[CAB PRD]], [[CAB UX Design]], [[CAB Architecture]], [[CAB Testing]], [[CAB API Doc]]
- Track cluster: [[SKL Track]], [[backlog]], [[workflow]]
- Drive cluster (post-design execution): [[crank]], [[mint]], [[feature]]
- Verification discipline: [[verification]]
- Rename history: [[F136 — Plan→Design skill rename]]
