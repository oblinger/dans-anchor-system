# RULESET R-naming
include::
import:: skills/audit/scripts/audit-plan.py
where:: `always`
description:: file-naming facet — `{slug} <X>.md` default + explicit exception allowlist

Embedded ruleset for the Naming facet, co-located with the facet spec above per [[F133 — Rulesets folder convention + facet embedding|F133]]. Armed by [[R-anchor]]'s `include::` — the umbrella `/audit anchor` resolves. Being named by [[R-facet]] is catalog membership, not adoption — that umbrella sits outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so an `include::` there arms nothing ([[Tink Backlog#^T208|T208]]). Vault-wide application — every anchor's files are subject to this set, no explicit `include::` needed.

> **`always` is now declared rather than inherited — [[Tink Backlog#^T349|T349]], 2026-08-11.** The scope did not change: an absent `where::` already falls through to `always`, and the sentence above (*"every anchor's files are subject to this set"*) says that is intended. What changed is that a reader can no longer confuse *deliberately vault-wide* with *nobody wrote a selector* — the two looked identical, and the same ambiguity is what hid [[R-exception-discipline]]'s defect, where four rules inherited `always` because the set-level line was never written while five siblings each wrote it out. [[R-progressive]] already declared its `always` explicitly; this set now matches it. After this, the only live rules judged at `always` are these five and `R-progressive-06`, and all six were read and are honestly scoped.

### RULE R-naming-01 — A file prefix, if present, is the anchor's slug (checked)
check:: name_slug_prefixed

**The prefix is optional.** A file is a child of an anchor because it sits in the anchor's folder — never because of what it is called. A markdown file inside `{anchor}/` may be named anything; `Lumens.md`, `CLAUDE.md`, and `Notes on the redesign.md` are all perfectly well-named files.

**If a file does carry a prefix, that prefix is the anchor's slug** — the explicit `slug:` from `.anchor` when declared, otherwise its basename verbatim ([[ANC Standard]] § S2; `slug:` is optional per [[DAS Dot Anchor]]). One anchor, one slug. A nested anchor prefixes with the **root** anchor's slug, not its own folder name: `Tink Track/Tink Backlog.md`, not `TINK Track Backlog.md`. The anchor's own folder keeps the human-readable **name** — `SYS/Staff/Atticus/` holds `ATT.md`, `Atticus Persona.md`, `Atticus Track/` — because the folder is not a prefix and never participates in link resolution.

**A prefix is required only where the basename would otherwise collide** vault-wide — which in practice means the repeated structural names, and only those. Measured 2026-08-02: `Design` appears 178 times, `Roadmap` 41, `Track` 39, `Messages` 39, `Backlog` 37, `queries` 35, `Features` 22 — and **zero** of them appear unprefixed. The prefix is doing exactly one job, and doing it universally already.

**That third clause is enforced by [[F281 — Duplicate-basename rule — anchor-name collisions break wiki-link routing|F281]], not here** — deliberately, and this rule states no independent uniqueness test. Uniqueness is a *vault-global* property; a per-file checker cannot see it without a vault-wide index, and building a second index would be a second source of truth for the same fact. F281 already owns it, split by severity: **audit-q C53** raises colliding *anchor names* as an error (0 of 1,211 today), and `ha --dump --format=collisions` keeps the file-level warning as an on-demand report so the ~296 mostly-deliberate ordinary collisions stay something you consult rather than a stream you learn to ignore. R-naming-01 is the mechanism that keeps that property true going forward; C53 is the check that it *is* true.

**Check pattern:** for each `.md` file under an anchor, if the stem leads with a token that is any ancestor anchor's folder **name** or a non-root ancestor's slug, and that token is not the root anchor's slug, fail. A stem with no prefix passes. A stem prefixed with the root slug passes. R-naming-03's sanctioned patterns pass.

**Why:** the prefix exists to keep [[F281 — Duplicate-basename rule — anchor-name collisions break wiki-link routing|F281]]'s uniqueness property true for the names that repeat. Obsidian resolves `[[Some Name]]` by path proximity, so two files sharing a basename mean different things depending on where the link is written — silently. `Backlog.md` in 37 anchors would be unusable; `Tink Backlog.md` is globally unambiguous. This rule is the **mechanism**; audit-q **C53** is the enforcement of the property itself. Stating it any wider is a category error: it was previously written as "every file must carry the prefix," which put **3,047 of 7,799 files (39% of the vault) in violation** — a rule that condemns 39% of the corpus is a rule nobody can act on, and the R-naming-03 allowlist had grown into a workaround for it.

**The retired formulation had an implementation, and it outlived the rule by nine days.** `all_files_folders_prefixed_with_name` sat registered and called by nothing: *"every file/folder inside the anchor is prefixed with the anchor name"* — the exact wording this rule was narrowed away from on 2026-08-02, and prefixed with the **name** rather than the slug, which the paragraph below rejects separately. Measured before deletion 2026-08-11 ([[Tink Backlog#^T349|T349]]): it fails **990 of 1,395 anchors**, 71%, the same shape as the 39% that got the wording retired. It also `rglob`s the whole subtree, so every nested anchor's files would be re-reported from each ancestor. Deleted rather than left orphan — a checker whose docstring states a retired rule reads to the next author as a rule waiting to be wired.

**Why the prefix is the slug and not the folder name.** Both were accepted until 2026-08-02, which meant `Tink Backlog.md` and `Tink Backlog.md` were equally legal and nothing ever complained. That is how `{slug}` interpolation in a `where::` selector came to resolve to a token no file matched — see [[Tink Backlog#^T431|T431]], where the index-page term reached 0 of 22 pages. One spelling per anchor is what makes `{slug}` mean something.

### RULE R-naming-02 — Vault-global files exempt (stated)

Files at the vault root or in vault-meta folders (Atlas, MY, etc.) that are genuinely global to the whole vault can omit the slug prefix. Examples: `Atlas.md`, `Q.md`, `kmr.md`.

**Check pattern:** vault-root and vault-meta files explicitly excluded from R-naming-01's check. List of exempt locations maintained by the auditor.

**Why:** these files exist *because* they're not scoped to any single anchor. Prefixing them with a slug would be a category error.

### RULE R-naming-03 — Facet-sanctioned unique patterns exempt (checked)

Files matching a facet-sanctioned alternative pattern are exempt from the slug-prefix default. The canonical allowlist:

- `{SLUG}<NNN> - <title>.md` (per [[DAS Features]] — the current feature-doc form, F300)
- `F<NNN> — <title>.md` (per [[DAS Features]] — the legacy form, never renamed)
- `US-<slug>-<N> — <title>.md` (per [[DAS Stories]])
- `YYYY-MM-DD <topic>.<ext>` (per [[DAS Log]])
- `YYYY-MM <topic>.<ext>` (per [[DAS Log]] — year-month precision)
- `YYYY <topic>.<ext>` (per [[DAS Log]] — year-only precision)
- `SKILL.md` (the Claude Code skill entry file — every skill folder has one)
- `R-<x>.md` (ruleset / rule files, per [[F133 — Rulesets folder convention + facet embedding|F133]])

**Check pattern:** R-naming-01's check accepts files matching any of the regex shapes above as a pass.

**Why:** these patterns are unique enough on their own (F-numbers monotonic-forever, `US-<slug>-<N>` encodes the slug directly, ISO dates plus topic). Adding a slug prefix would be redundant. The parent folder (`{slug} Track/{slug} Features/`, `{slug} Design/{slug} PRD/`, `{slug}/{slug} Log/`) already encodes anchor scope.

The F300 form is the one entry that *does* carry the slug and is still allowlisted rather than passing R-naming-01 directly: it fuses the slug to the number (`TINK300`) rather than following it with a space, which is deliberate — the whole point is a single typeable token — and so it cannot satisfy a `startswith("{slug} ")` test. The three-digit requirement is what keeps the shape narrow enough to sanction: measured 2026-08-02, **zero** existing vault files match it, so admitting it exempts nothing that was previously flagged.

### RULE R-naming-04 — Slug-prefix-sufficient-by-chance allowed sparingly (stated)

Files with names so domain-specific they're unlikely to collide vault-wide (e.g., `WCAG-2.1 contrast spec.md`, `Sourcetrail 2024 article.md`) are allowed without the slug prefix. Use sparingly — the prefix-default catches more cases than the by-chance argument.

**Check pattern:** manual judgment at authoring time; not mechanically audited. If a name is ambiguous about whether it qualifies, prefix it.

**Why:** rigidly applying the slug prefix to files whose names are *already* unique would produce names like `MUX Sourcetrail 2024 article.md` which is worse than the bare name. The escape valve exists for genuine cases.

### RULE R-naming-05 — Folder-anchor files match their folder name (checked)

A folder-anchor's marker file is named `{folder name}.md` — i.e., `{slug} Design/` contains `{slug} Design.md`; `{slug} Track/{slug} Features/` contains `{slug} Features.md`. The marker file name equals the folder name verbatim. This is the simplest instance of R-naming-01.

**Check pattern:** for each folder whose `.anchor` file is present, assert `<folder>/<folder basename>.md` exists.

**Why:** matches [[DAS Folder]]'s marker-file convention; ensures the folder-anchor pattern is consistent vault-wide.

### RULE R-naming-06 — External-discovery-contract files exempt (stated)

Files whose name is fixed by an external tool / runtime / repo discovery contract are exempt from the slug-prefix default: `CLAUDE.md`, `SKILL.md`, `README.md`, `API_REFERENCE.md`, `CONFIG_REFERENCE.md`, `.anchor`, and non-markdown code files (`.py`/`.ts`/`.rs`/…). See § Exception D.

**Check pattern:** these exact names (and non-`.md` files) excluded from R-naming-01's check; the exempt set is fixed by external contracts, not author choice.

**Why:** the filename *is* the discovery key — Claude Code finds `CLAUDE.md`/`SKILL.md` by hard-coded path, GitHub renders `README.md`, HookAnchor names `.anchor`. Prefixing any of them breaks the tool that depends on the literal name.

## Adoption

Vault-wide — every anchor's files are subject to this set, no explicit `include::` required in `{slug} Decisions.md`. Listed in the catalog for completeness.

## See also

- [[DAS Naming]] — facet spec this ruleset enforces.
- [[R-facet]] — parent umbrella.
- [[R-testing]], [[R-status]], [[R-log]], [[R-stories]], [[R-prd]], [[R-design]] — sibling materialized facet rulesets.
- [[DAS Rulesets]] — top-level catalog.
- F141 (future R-anchor umbrella) — would collect R-naming + R-folder + R-anchor-page + R-files when those rulesets exist.
