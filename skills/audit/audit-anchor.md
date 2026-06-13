# /audit anchor — audit an anchor against the anchor rule set

Takes one anchor (or folder) and checks it against the **anchor rule set** — the rules that say what a well-formed anchor looks like. Three things get audited:

1. **The `.anchor` file is set** — the folder is a registered anchor with a slug + traits (not empty).
2. **The anchor page conforms** — the `{slug}.md` page follows [[FCT Anchor Page]] (H1, summary, optional figure, dispatch table — in order).
3. **The dispatch table conforms** — if the anchor page has (or should have) one, it follows [[CAB Dispatch Table]] (masthead + member zone).

**This skill is thin by design.** It does not invent checks — it **reads the rules from the associated rule set and verifies each is satisfied.** As those specs evolve, the audit follows them with no edit here. (Future: the rules consolidate into an explicit `library/rule-sets/anchor` set this audit loads directly; today it reads them from the facet + discipline specs + the SKA decisions named below.)

## When to use

- `/audit anchor <anchor>` — audit one named anchor.
- `/audit anchor` (in an anchor's cwd) — audit the current anchor.
- `/audit anchor dry` — report findings without writing the backlog row (per the `/audit` `dry` convention).
- Catches exactly the failures seen in practice: an **empty `.anchor`** (breadcrumb then skips the anchor — the OBSK case), a **blank line after the H1**, a **missing/ malformed dispatch masthead**.

## The rule set it checks

### A — `.anchor` is set *(the anchor convention)*
- [ ] A `.anchor` file **exists** in the folder.
- [ ] It declares a **`slug:`** — UNLESS the anchor is in the one deliberate bare-name zone (the `ob-skills` pillars). An **empty `.anchor`** is a finding: breadcrumb inference skips the anchor and jumps to its grandparent (see the `OBSK` incident).
- [ ] It declares **`traits:`** identifying the kind (e.g. `[skill]`, `[Code]`, `Collection`).

### B — anchor page conforms *([[FCT Anchor Page]] § Rule Set, + D06)*
*Reference: read the [[FCT Anchor Page]] ruleset **`R-anchor-page`**, or diff the anchor against the matching kind in [[FEX]] — [[Snapper Dapper]] (skill), [[Bridges]] (list), [[Devtools]] (grouped), [[Clarifier]] (project), [[Clarifier Track]] (sub-folder).*
- [ ] The anchor page **`{slug}.md`** exists (filename = slug; H1's readable name may differ).
- [ ] **H1 = `{slug} - {Full Name}`** (per [[SKA Decisions|D06]]) — slug leads, then the readable name. (Bare-name anchors: H1 is just the name.)
- [ ] **No blank line after the H1** — the one-sentence summary sits on the very next line. Then a blank, then the optional figure, then the dispatch table. (Top-of-page order: H1 → summary → figure? → dispatch.)
- [ ] `description:` frontmatter present.

### C — dispatch table conforms *([[CAB Dispatch Table]], + D07 / D08)* — when the page has or should have one
Delegate the table's shape to **[[audit-dispatch|/audit dispatch]]** (it already encodes the masthead + member-zone rules). The anchor-level checks layered on top:
- [ ] **Masthead is minimal** — `Related` is the **1st** row (omitted entirely if empty — never blank); no ad-hoc rows the breadcrumb already covers (no `Repo` row). (D07)
- [ ] **Design row** — if the anchor has the design facet (`{NAME} Design/`), a `Design` row is **present** as the **2nd** row, in the fixed order PRD → UX → CLI → API → Architecture → Decisions → Testing → Roadmap → Features. (D07)
- [ ] **No `Track` row** for a skill-ecosystem anchor (skill / facet / discipline / example) — tracking is centralized in SKA. (D08)
- [ ] **Container ending** — a Collection/container's table ends with an electric-list marker (`...` / `---` / `+` group rows); each group-row label links *down* to its container page. (per [[CAB Dispatch Table]] + [[DSC progressive-disclosure]])

## Runbook

1. **Resolve the anchor** — use the argument, else walk up from cwd to the nearest `.anchor`. If none found, report "no anchor here" and stop.
2. **Check A** — read the `.anchor`; flag missing file / empty (no slug) / missing traits.
3. **Check B** — read `{slug}.md`; verify H1 form, the no-blank-after-H1 rule, frontmatter, and top-of-page order.
4. **Check C** — if a dispatch table is present or the anchor kind requires one, run `/audit dispatch <anchor> dry` and fold its findings in; add the anchor-level masthead/Design/Track checks above.
5. **Report** — print a per-check pass/fail table. Per the `/audit` default (**audit reports, doesn't fix** — except `/audit dispatch`, which fixes the table shape), file a single backlog row summarizing the failed checks, unless `dry`. The `.anchor` and H1 fixes are one-line mechanical repairs — offer them, but don't auto-apply (they touch identity).

## Distinction from siblings

- **[[audit-dispatch]]** *fixes* one table's shape. `/audit anchor` *audits* the whole anchor (`.anchor` + page + table) and *delegates* the table to `/audit dispatch`.
- **[[audit-structure]]** diagnoses broad cross-anchor structural issues (orphans, broken links across the tree). `/audit anchor` is scoped to one anchor's conformance to the anchor rule set.

## Related

- Rules read: [[FCT Anchor Page]], [[CAB Dispatch Table]], [[DSC progressive-disclosure]]; decisions [[SKA Decisions|D06 / D07 / D08]].
- Builder it calls: [[audit-dispatch]].
- Vault-wide connectivity walk: [[DSC anchor-dag]].
