# /audit anchor — audit an anchor against the anchor ruleset

Takes one anchor (or folder) and checks it against the **anchor ruleset** — the rules that say what a well-formed anchor looks like. Three things get audited:

1. **The `.anchor` file is set** — the folder is a registered anchor with a slug + traits (not empty).
2. **The anchor page conforms** — the `{slug}.md` page follows [[FCT Anchor Page]] (H1, summary, optional figure, dispatch table — in order).
3. **The dispatch table conforms** — if the anchor page has (or should have) one, it follows [[DSC Dispatch Table]] (masthead + member zone).

**This skill is thin by design.** It does not invent checks — it **reads the rules from the associated ruleset and verifies each is satisfied.** As those specs evolve, the audit follows them with no edit here. (Future: the rules consolidate into an explicit `library/Rulesets/anchor` set this audit loads directly; today it reads them from the facet + discipline specs + the SKA decisions named below.)

## When to use

- `/audit anchor <anchor>` — audit one named anchor.
- `/audit anchor` (in an anchor's cwd) — audit the current anchor.
- `/audit anchor dry` — report findings without writing the backlog row (per the `/audit` `dry` convention).
- Catches exactly the failures seen in practice: an **empty `.anchor`** (breadcrumb then skips the anchor — the DAS case), a **blank line after the H1**, a **missing/ malformed dispatch masthead**.

## The ruleset it checks

### A — `.anchor` is set *(the anchor convention)*
- [ ] A `.anchor` file **exists** in the folder.
- [ ] It declares a **`slug:`** — UNLESS the anchor is in the one deliberate bare-name zone (the `ob-skills` pillars). An **empty `.anchor`** is a finding: breadcrumb inference skips the anchor and jumps to its grandparent (see the `DAS` incident).
- [ ] It declares **`traits:`** identifying the kind (e.g. `[skill]`, `[Code]`, `Collection`).

### B — anchor page conforms *([[FCT Anchor Page]] § Ruleset, + D06)*
*Reference: read the [[FCT Anchor Page]] ruleset **`R-anchor-page`**, or diff the anchor against the matching kind in [[FEX]] — [[HBR]] (project), [[HBR Components]] (grouped), [[HBR Ingest]] (sub-folder), [[FEX Snapshot]] (skill).*
- [ ] The anchor page **`{slug}.md`** exists (filename = slug; H1's readable name may differ).
- [ ] **H1 = `{slug} - {Full Name}`** (per [[SKA Decisions|D06]]) — slug leads, then the readable name. (Bare-name anchors: H1 is just the name.)
- [ ] **No blank line after the H1** — the one-sentence summary sits on the very next line. Then a blank, then the optional figure, then the dispatch table. (Top-of-page order: H1 → summary → figure? → dispatch.)
- [ ] `description:` frontmatter present.

### C — dispatch table conforms *([[DSC Dispatch Table]], + D07 / D08)* — when the page has or should have one
Delegate the table's shape to **[[audit-dispatch|/audit dispatch]]** (it already encodes the masthead + member-zone rules). The anchor-level checks layered on top:
- [ ] **Masthead is minimal** — `Related` is the **1st** row (omitted entirely if empty — never blank); no ad-hoc rows the breadcrumb already covers (no `Repo` row). (D07)
- [ ] **Design row** — if the anchor has the design facet (`{NAME} Design/`), a `Design` row is **present** as the **2nd** row, in the fixed order PRD → UX → CLI → API → Architecture → Decisions → Testing → Roadmap → Features. (D07)
- [ ] **No `Track` row** for a skill-ecosystem anchor (skill / facet / discipline / example) — tracking is centralized in SKA. (D08)
- [ ] **Container ending** — a Collection/container's table ends with an electric-list marker (`...` / `---` / `+` group rows); each group-row label links *down* to its container page. (per [[DSC Dispatch Table]] + [[DSC progressive-disclosure]])

## Mechanism — the F161 audit engine

Per [[F161 — Rule-driven audit engine — resolve, run, judge|F161]], this skill no longer hand-walks the checks above — it **drives `audit-plan`**, the resolver/runner that binds the `R-anchor` umbrella's rules to this anchor's targets, runs the mechanical ones by script, and emits the judgment residue for the agent. The A/B/C rule list above is the human-readable summary of what `R-anchor` contains; the engine is the executable form (so the two never drift — change the facet's `# RULESET` block and the audit follows).

Script: `~/.claude/skills/audit/scripts/audit-plan.py`.

```bash
P=~/.claude/skills/audit/scripts/audit-plan.py
"$P" <anchor> --report --model <model-id>   # quick combined view (mechanical + residue count)
"$P" <anchor> --run                         # mechanical verdicts only (checked rules)
"$P" <anchor> --judge --model <model-id> --json   # the agent-judgment task manifest
"$P" --record-verdict --key <K> --status pass|fail --detail "…"   # persist one judged verdict
```

## Runbook

1. **Resolve the anchor** — use the argument, else walk up from cwd to the nearest `.anchor`. If none found, report "no anchor here" and stop. (`audit-plan` accepts a path or a slug.)
2. **Mechanical pass** — run `audit-plan <anchor> --run`. Collect the fail/error verdicts. These are the deterministic findings (`.anchor` set, filename = slug, frontmatter `description:`, no-blank-after-H1, etc., as `check::` refs accrue).
3. **Judgment pass** — run `audit-plan <anchor> --judge --model <model-id> --json` for the manifest of rules needing agent judgment (the residue not covered by a `check::`). For each task: read its rule body (the `flat_file` / `check_pattern` / `why` in the manifest) and its target, decide pass/fail + a one-line reason, then persist with `audit-plan --record-verdict --key <task.key> --status <s> --detail "<reason>"`. For a large residue, dispatch the tasks to workers (Agent tool, `subagent_type=general-purpose`) the same way the bare-`/audit` orchestrator does — each worker judges a slice and records its verdicts; the cache (keyed by rule + target + model) makes re-runs free.
4. **Dispatch table** — the engine's `R-anchor-page` rules cover the masthead/Design/Track checks; for table *repair* still delegate to **[[audit-dispatch|/audit dispatch]]** (it fixes shape; the engine only diagnoses).
5. **Report + backlog row** — print the combined pass/fail summary (`audit-plan <anchor> --report` gives it directly). Per the `/audit` default (**audit reports, doesn't fix** — except `/audit dispatch`), file the findings as state-clustered backlog rows per [[audit|SKILL.md]] § Backlog entry format — **unless `dry`**:
   - **Mechanical fail-verdicts → one `[Ready]` row** (spec-clear, mechanically fixable). Sub-bullets = each failed `(rule, target)` with the verdict detail.
   - **Judgment fail-verdicts needing user input → `[Questions]` row(s)** linking a feature doc holding the parked Qs.
   - All rows minted via `state task create` (never direct-edit the backlog), default horizon `Next`.

   The `.anchor` and H1 fixes are one-line mechanical repairs — offer them, but don't auto-apply (they touch identity).

**Doc-level sibling.** The same engine audits a single document via `audit-plan <file> --mode doc` (umbrella `R-doc`). Promoting that to a first-class `/audit doc` action is the next F161 increment.

## Distinction from siblings

- **[[audit-dispatch]]** *fixes* one table's shape. `/audit anchor` *audits* the whole anchor (`.anchor` + page + table) and *delegates* the table to `/audit dispatch`.
- **[[audit-structure]]** diagnoses broad cross-anchor structural issues (orphans, broken links across the tree). `/audit anchor` is scoped to one anchor's conformance to the anchor ruleset.

## Related

- Rules read: [[FCT Anchor Page]], [[DSC Dispatch Table]], [[DSC progressive-disclosure]]; decisions [[SKA Decisions|D06 / D07 / D08]].
- Builder it calls: [[audit-dispatch]].
- Vault-wide connectivity walk: [[DSC anchor-dag]].
