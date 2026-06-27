---
description: Template convention — a template IS an instance, not a description of one. Live markdown exemplar above `---` divider; brief spec below, including a Variables section that defines each `{{PLACEHOLDER}}` and tells the instantiator how to handle the no-data case.
---

# CAB Template

The template convention — a template file IS a live instance of the form it teaches (no fences, bare `{{PLACEHOLDERS}}`) plus a Variables section telling the instantiator what each placeholder means and what to do when there's no data.

**Smoke test.** Copy a template file. Rename it. Replace every `{{VARIABLE}}` with real content **or delete the line/section if there's no real content to put**. If the result reads as a usable entry — no leftover placeholders, no fake-looking sections — the template is right.

A template **is** an instance of the form it teaches. Not a description of the form. Not a meta-doc *about* the form. The rendered content of the file is a working specimen with bare `{{PLACEHOLDERS}}` where live data goes, plus a definitions section below that tells the instantiator what each placeholder means and what to do when the data is missing.


## Anatomy

A template file has three parts:

1. **Exemplar** (above the `---` divider) — live markdown. Same H1, frontmatter, sections, and tables as a real entry. **Bare `{{UPPER_SNAKE_CASE}}` placeholders** for fields to fill. **No code fences around the exemplar** — fences make wiki-links inert, tables render as plain text, and headings don't appear in Obsidian's outline.

2. **About this template** (a paragraph below the divider) — naming pattern for cloned instances, any non-obvious structural rules.

3. **Variables** (a bulleted section below About) — one bullet per `{{PLACEHOLDER}}` in the exemplar, explaining what to put and, critically, *what to do when there's no data*. This is the most important addition: it lets an LLM or human instantiator honestly delete a placeholder rather than leave it in.


## Wrong vs right

**❌ Wrong** — a description of a template:

```markdown
## How to use

1. Clone this file.
2. Fill in placeholders below.

## Canonical entry shape

​```markdown
# {YYYY-MM-DD} — {Title}
…body…
​```
```

Reader can't copy this and get an entry. The form is inert inside fences.

**❌ Also wrong** — a template that bakes in speculative content that will be empty at creation:

```markdown
# LOG

### {{YYYY-MM-DD}}  {{Interaction Topic}}

{{Notes from the interaction.}}
```

At creation, there ARE no past interactions. An LLM instantiating this is likely to leave the placeholder H3 in, polluting the entry. Cumulative sections like `# LOG` should have the **header only**, no fake entries underneath.

**✅ Right** — a template that IS an entry, with variables defined and empty cumulative sections left empty:

```markdown
# {{TITLE}}

{{DESCRIPTION}}

## Section 1

{{SECTION_1_BODY}}

# LOG

---

# About this template

Clone → `{YYYY-MM-DD} {Title}.md` in `Log/General/`. See [[CAB Template]].

## Variables

- `{{TITLE}}` — One-line title of the entry.
- `{{DESCRIPTION}}` — 1–2 sentences framing what this entry covers. Delete this line if there's nothing meaningful to add at creation.
- `{{SECTION_1_BODY}}` — Body prose for Section 1. Delete the entire section if not applicable.

The `# LOG` section starts empty. Add reverse-chronological `### {YYYY-MM-DD}` entries as events occur — most recent at top.
```

Copy, rename, replace `{{VARIABLES}}` per the definitions → usable entry. Each variable definition tells the instantiator both *what to put* and *what to do if no data exists* — so leftover `{{}}` placeholders are a tooling failure, not an unavoidable artifact.

(Note: this spec doc itself uses fenced code blocks to *show* what templates look like. That's correct for a spec doc. The no-fences rule applies to the template files themselves.)


## Empty-at-creation vs structural placeholders

Two kinds of content in templates need different treatment:

| Kind | Example | Treatment |
|---|---|---|
| **Structural placeholder** — the form genuinely has this content at creation time (because the instantiator HAS the data) | A paper's title and abstract; a PHUNT's comparison-table rows | Keep with `{{VARIABLES}}`; define each in the Variables section. |
| **Cumulative section** — content accumulates *after* creation, not at it | A person's interaction log; a project's change history; a corp's recurring meeting notes | **Keep only the header** (e.g. `# LOG`); no placeholder entries underneath. Note in the spec that the section grows organically. |

Forcing fake entries into a cumulative section is the failure mode this rule prevents: a template that ships with `### {{YYYY-MM-DD}}  {{Interaction Topic}}` invites the instantiator to either leave it (polluting the entry) or invent a fake interaction (also polluting). Empty header → instantiator adds real entries when real events happen.


## Two kinds of templates

| Kind | Form | Use |
|---|---|---|
| **Markdown-file template** | `_{Name} Template.md` | Canonical starting content for a new markdown document. |
| **Folder template** | `_{Name} Template/` | Canonical starting structure for a new folder; contains a marker file `_{Name} Template/_{Name} Template.md` plus optional skeleton files. |


## Naming

Always `_{Name} Template` (file: with `.md`; folder: no extension). The leading underscore sorts the template to the top of the folder listing and visually marks it as meta-content. The `{Name}` slot is the entity or folder the template describes — `_Corp Template/`, `_PRD Template.md`, `_PHUNT Template.md`.


## Two locations

| Location | What lives there | Linked from dispatch? |
|---|---|---|
| **Central library** (alongside the facet spec in `CAB/CAB Facets/`, or in a vault-wide `Templates/` directory) | Generic templates — one starter per CAB facet or general doc shape. Vault-wide; lookup is by name. | No. Reached by name; doesn't merit a row in every dispatch table. |
| **Inline** (the folder being templated) | Folder-specific templates — corp folders under `Corp/`, experiment folders under `experiments/`, etc. | Yes. The folder's own dispatch page links to its template at the top of the user zone. |

**Only folder-level templates earn a dispatch-row link.** Generic vault-wide templates are reached by name; they don't need to appear on every dispatch.


## Dispatch-table integration

When a folder has a folder template inside it, the folder's dispatch page must include a `Template` row at the top of the auto-managed zone:

```
| -[[Corp]]-     | ><br>: …                  |
| ---            | ---                       |
| Template       | [[_Corp Template]]        |
| (auto rows)    | …                         |
```

`rewire` recognizes `_*/` folders and inserts this row automatically when missing. See [[SKA rewire]] § Folder templates.


## Audit categories

- **`missing-folder-template-row`** — folder contains a `_*/` template but its dispatch lacks the Template row.
- **`orphan-template`** — `_*` template isn't reachable from any dispatch.
- **`template-is-spec`** — template file fails the smoke test: contains a `## How to use` / `## Canonical entry shape` structure with a fenced code block instead of a live exemplar above a `---` divider.
- **`template-has-fake-cumulative-entries`** — template has placeholder entries in a cumulative section (LOG, history, etc.) that would be empty at creation — should be header-only.


## Cross-references

- **[[CAB Conventions]]** — convention registry.
- **[[SKA rewire]]** — adds the Template dispatch row automatically.
- **[[CAB Anchor Page]]** — dispatch-table format.

# BRIEF

- **This is the convention spec for template files** — the authoritative rule on how `_*Template.md` and `_*Template/` artifacts are shaped. Edits here change how every template in the vault must look.
- **NOT a catalog of templates and NOT a template itself.** Don't pile per-template entries here; instances live in `CAB/CAB Facets/`, vault-wide `Templates/`, or inline alongside the folder they instantiate. Don't try to make this file pass its own smoke test — it's a spec doc, not an exemplar.
- **Inclusion test for new rules here:** does it govern the *shape* of a template file (exemplar/divider/Variables section, no-fences rule, naming, cumulative-vs-structural placeholders, dispatch-row integration, audit categories)? If yes, it belongs. Project-wide or facet-shape rules go to CLAUDE.md / `CAB <Facet>.md` instead.
- **Fenced code blocks in this file are intentional** — they *show* what (wrong/right) templates look like. The "no fences around the exemplar" rule applies to actual template files, not to this spec. Don't unfence them.
- **Audit-category names are load-bearing identifiers** — `missing-folder-template-row`, `orphan-template`, `template-is-spec`, `template-has-fake-cumulative-entries` are consumed by `SKA rewire` and audit tooling. Don't rename without updating consumers.
- **Naming pattern `_{Name} Template`** with the leading underscore is structural (sort-to-top + meta marker). Don't relax it; don't introduce a parallel pattern.
- **Two-locations rule is load-bearing**: only folder-level templates earn a dispatch-row link; generic vault-wide templates are reached by name. Don't broaden the dispatch-row obligation to generic templates — it pollutes every dispatch table.
