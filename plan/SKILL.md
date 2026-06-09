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

**Storage (F130, preferred):** centralized `{NAME} Status.md` facet in the Track folder, carrying one `::` dataview line per planning facet:

```
prd:: MVP-agent (2026-06-08) — covers golden path; edge cases unspecified
ux:: none
architecture:: MVP-user (2026-06-07) — services + data flow; deployment TBD
testing:: none
roadmap:: none
```

Cell vocabulary, ordered low → high: `none < MVP-agent < MVP-user < Full-agent < Full-user`. All writes go through `state status set` (no hand-editing the file); reads via `state status show`.

**Storage (legacy):** per-artifact `status::` dataview field at the top of each planning doc. Valid values for Architecture and Testing Strategy: `drafting | in-review | accepted`. Retained as fallback when `{NAME} Status.md` is absent.

**Resolution on bare `/plan`:**

1. **Check `{NAME} Status.md`.** If present, it's authoritative. Run:
   ```bash
   ~/.claude/skills/workflow/scripts/state --anchor {NAME} status show
   ```
   Walk the output in declared order (`prd`, `ux`, `architecture`, `testing`, `roadmap`). Pick the **first** facet whose cell is lowest on the ladder above; dispatch to the corresponding sub-skill (`plan-prd`, `plan-ux`, etc.). Sub-skills self-promote to `*-agent` at completion via `state status set <facet> <new-cell> --note "<one-line>"`; user-stamped `*-user` comes from explicit review ("PRD looks good for MVP" → agent runs `state status set prd MVP-user --note "<...>"`).
2. **Fallback when `{NAME} Status.md` absent.** Apply the legacy per-artifact inference below.
3. **`/plan <facet>` bypasses the picker entirely** — works on already-approved facets too (that's just more planning on something).

**Legacy inference (fallback when no Status.md):**
- PRD exists with at least one user story → past PRD-drafting.
- PRD declares UI requirement AND `{NAME} UX.md` has concrete UI shape → past UX.
- PRD declares API surface AND `{NAME} API.md` has concrete API shape → past API.
- Architecture exists with at least one named subsystem → architecting in progress.
- Architecture has `status:: accepted` → Gate 1 passed; proceed to Testing Strategy.
- Testing Strategy exists with proposed regime → testing-strategy in progress.
- Architecture AND Testing Strategy both `accepted` → Gate 2 passed; proceed to Roadmap.
- Roadmap has at least one milestone → roadmapping in progress.

If a declared `Status.md` cell disagrees with inferred state on the artifact body (e.g., `prd:: Full-user` but the PRD doc has only a frontmatter and one user story), surface the discrepancy in chat. Declared cell wins; the surface is a check on user intent.

## Runbook — bare `/plan`

1. **Detect anchor + trait.** Walk up to nearest `.anchor` file; read `traits:` list. If `Code` is not present, print: *"plan v1 supports Code-trait anchors only — generalization is Phase 2."* and stop.
2. **Read planning status.** Run `state --anchor {NAME} status show` to get the per-facet cell map. If `{NAME} Status.md` is absent the script auto-creates it with all facets at `none`.
3. **Build gap table.** Render the status one line per facet:
   ```
   prd:            MVP-user (2026-06-08) — user-confirmed for v1
   ux:             MVP-agent (2026-06-07) — golden path; edges unspecified
   architecture:   none
   testing:        none
   roadmap:        none
   ```
4. **Pick the dispatch target.** Walk facets in declared order (`prd`, `ux`, `architecture`, `testing`, `roadmap`); pick the FIRST facet at the lowest cell on `none < MVP-agent < MVP-user < Full-agent < Full-user`. The table above picks `architecture` (first `none`).
5. **Auto-dispatch.** Invoke the matching sub-skill: `/plan architect` for the example above. The user may redirect mid-dispatch by saying "actually let's do UX first" or by typing `/plan ux` directly.
6. **Self-promote at completion.** When the sub-skill judges its work sufficient, it ends with:
   ```bash
   state --anchor {NAME} status set <facet> MVP-agent --note "<one-line rationale>"
   ```
   User stamps `*-user` via natural-language ("PRD looks good for MVP" → agent runs `state status set prd MVP-user --note "<...>"`).

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
