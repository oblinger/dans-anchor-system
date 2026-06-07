---
name: plan
description: >
  Federated planning orchestrator for a project anchor. Walks through the canonical planning
  phases — PRD → UX → API → Architecture → Testing Strategy → [both accepted gate] → Roadmap
  (with proactive feature docs) — detecting which artifacts are complete vs. missing, and
  dispatching to per-artifact sub-skills (`plan-prd`, `plan-ux`, `plan-architect`, `plan-testing`,
  `plan-roadmap`). Plan is to Track what crank is to Drive — the outer-loop orchestrator at the
  center of the cluster. Use when the user says: "let's plan this", "plan", "/plan", "what's the
  planning state of this anchor", "/plan prd", "/plan architect", "/plan testing", "/plan roadmap",
  or asks where in the planning sequence the project is. Initially supports Code-trait anchors only;
  generalization to Paper/Topic/Simple traits is Phase 2.
tools: Read, Write, Edit, Bash, Glob, Grep, Agent
user_invocable: true
---

# Plan — Federated Planning Orchestrator

`/plan` walks a project anchor through its planning artifacts in canonical order, detecting state, surfacing gaps, and dispatching to per-artifact sub-skills. Sibling to `/crank` (Drive cluster); the center of the Track cluster.

## Canonical phase order

The skill walks these phases in this exact order. Each phase has a primary artifact (a file the sub-skill authors) and an optional gate at the end.

| # | Phase | Sub-skill | Primary artifact | Gate after |
|---|---|---|---|---|
| 1 | PRD | `/plan prd` | `{NAME} Design/{NAME} PRD.md` | — |
| 2 | UX *(if applicable)* | `/plan ux` | `{NAME} Design/{NAME} UX.md` | — |
| 3 | API *(if applicable)* | `/plan api` | `{NAME} Design/{NAME} API.md` | — |
| 4 | Architecture | `/plan architect` | `{NAME} Design/{NAME} Architecture.md` | **Gate 1** — `status:: accepted` on Architecture |
| 5 | Testing Strategy | `/plan testing` | `{NAME} Design/{NAME} Testing Strategy.md` | **Gate 2** — `status:: accepted` on BOTH Architecture AND Testing Strategy |
| 6 | Roadmap + feature docs | `/plan roadmap` | `{NAME} Track/{NAME} Roadmap.md` + per-milestone `Features/M*.md` | — |
| 7 | Plan complete | — | — | Transition to Drive (`/crank`) |

**Gate semantics:** Gate 1 protects entry to Testing Strategy authoring. Gate 2 protects entry to Roadmapping. A gate is "passed" when the relevant artifact's top-of-file `status::` dataview field reads `accepted`. The user sets the field by saying "the architecture is accepted" / "the testing strategy is accepted" (the agent watches for that phrase and updates the field) or by editing directly. Gates are sticky: once `accepted`, no re-prompt.

The phrasing "satisfied with this as a starting architecture / testing discipline" is load-bearing: gates protect against starting *next-phase work* on visibly incomplete prior work — they do not mean "perfect." Iteration continues throughout Drive.

## State model

**Storage:** per-artifact `status::` dataview field at the top of each planning doc. Valid values for Architecture and Testing Strategy: `drafting | in-review | accepted`. PRD / UX / API may also carry `status::` but the field is not gate-gating for those.

**Resolution on bare `/plan`:**

1. **Read each artifact's `status::` field.** If declared, that's authoritative.
2. **Inference (rules-of-thumb) when `status::` is absent.** Walk the artifacts in canonical order:
   - PRD exists with at least one user story → past PRD-drafting.
   - PRD declares UI requirement AND `{NAME} UX.md` has concrete UI shape → past UX.
   - PRD declares API surface AND `{NAME} API.md` has concrete API shape → past API.
   - Architecture exists with at least one named subsystem → architecting in progress (not yet `accepted`).
   - Architecture has `status:: accepted` → Gate 1 passed; proceed to Testing Strategy.
   - Testing Strategy exists with proposed regime → testing-strategy in progress (not yet `accepted`).
   - Architecture AND Testing Strategy both `accepted` → Gate 2 passed; proceed to Roadmap.
   - Roadmap has at least one milestone → roadmapping in progress.
   - All artifacts complete + both gates `accepted` + roadmap milestones present → plan-complete.
3. **Reconcile.** If a declared `status::` disagrees with inference (e.g., `status:: accepted` but the doc has only a frontmatter and one H2), surface the discrepancy in chat: *"you set status:: accepted on Architecture but the doc has no named subsystems — confirm?"*. Declared value wins; the surface is a check on user intent.

## Runbook — bare `/plan`

1. **Detect anchor + trait.** Walk up to nearest `.anchor` file; read `traits:` list. If `Code` is not present, print: *"plan v1 supports Code-trait anchors only — generalization is Phase 2."* and stop.
2. **Inspect planning artifacts.** For each canonical artifact, check existence at the expected location AND parse `status::` field if present.
3. **Build gap table.** Order incomplete artifacts canonically. The first incomplete is the dispatch target.
4. **Surface state.** Print a compact gap table:
   ```
   PRD:            ✓ done           (status:: accepted)
   UX:             ✓ done           (one screen sketch + nav model)
   API:            — n/a            (PRD declares no API surface)
   Architecture:   ⚠ in progress    (status:: drafting — 3 subsystems named)
   Testing Strategy: ✗ missing
   Roadmap:        ✗ missing
   ```
5. **Auto-dispatch (Q4 = A).** Invoke the next-incomplete sub-skill: e.g., the table above auto-runs `/plan architect`. The user may redirect mid-dispatch by saying "actually let's do UX first."

## Runbook — `/plan <artifact>`

Direct invocation of a sub-skill, bypassing the bare-state-scan.

| Verb | Dispatches to |
|---|---|
| `/plan prd` | `plan-prd.md` |
| `/plan ux` | `plan-ux.md` |
| `/plan api` | `plan-architect.md` § API section (or future `plan-api.md` when commissioned) |
| `/plan architect` | `plan-architect.md` |
| `/plan testing` | `plan-testing.md` |
| `/plan roadmap` | `plan-roadmap.md` |
| `/plan gate architecture` | shortcut for *"set `status:: accepted` on `{NAME} Architecture.md`"* |
| `/plan gate testing` | shortcut for *"set `status:: accepted` on `{NAME} Testing Strategy.md`"* |

## Runbook — natural-language gate phrases

The skill watches for these phrases in user messages while a planning artifact is being authored:

- *"the architecture is accepted"* / *"I accept the architecture"* / *"architecture looks good"* → set `status:: accepted` on `{NAME} Architecture.md`.
- *"the testing strategy is accepted"* / *"testing strategy looks good"* → set `status:: accepted` on `{NAME} Testing Strategy.md`.

After updating, glance the affected file so the user can verify the field landed.

## Dispatch table

| Sub-skill | File | Authors |
|---|---|---|
| plan-prd | [[plan-prd]] | `{NAME} Design/{NAME} PRD.md` (per CAB PRD facet) |
| plan-ux | [[plan-ux]] | `{NAME} Design/{NAME} UX.md` (per CAB UX Design facet) |
| plan-architect | [[plan-architect]] | `{NAME} Design/{NAME} Architecture.md` + subsystems (per CAB Architecture facet) |
| plan-testing | [[plan-testing]] | `{NAME} Design/{NAME} Testing Strategy.md` |
| plan-roadmap | [[plan-roadmap]] | `{NAME} Track/{NAME} Roadmap.md` + per-milestone `{NAME} Features/M*.md` |

## Anti-patterns

- **Don't ask "which artifact next?"** — the canonical phase order is the answer. Bare `/plan` auto-dispatches; user redirects if they want a different order.
- **Don't gate by separate ceremony.** Gates are encoded in the doc's `status::` field, NOT in a parallel gate registry.
- **Don't write tests during `/plan testing`.** That phase writes the *strategy* (regime); tests come during Drive (`/code test` or `/mint`).
- **Don't author roadmap milestones before Gate 2.** The roadmap phase is gated on both Architecture and Testing Strategy being `accepted`.
- **Don't reorder phases silently.** If the user redirects ("let's do UX first"), comply for that session, but the canonical order remains the default for future invocations.

## When NOT to use this skill

- **Implementation work** — that's `/mint` / `/crank` / `/code <verb>`.
- **Single-feature design** — that's `/feature` (which inherits from the planning artifacts).
- **Non-Code anchors** — Phase 2; v1 only supports Code-trait.
- **Anchor creation itself** — `/code anchor` (not migrated; structural, not planning).

## Related

- Per-phase sub-skills: [[plan-prd]], [[plan-ux]], [[plan-architect]], [[plan-testing]], [[plan-roadmap]]
- CAB facets: [[CAB PRD]], [[CAB UX Design]], [[CAB Architecture]], [[CAB API Doc]]
- Track cluster: [[SKL Track]], [[backlog]], [[workflow]]
- Drive cluster (post-plan execution): [[crank]], [[mint]], [[feature]]
- Verification discipline: [[verification]]
