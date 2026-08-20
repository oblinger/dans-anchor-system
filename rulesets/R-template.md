# RULESET R-template
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file: **/_* Template.md, **/_* Template/**`
description:: the Template facet — a live specimen whose anchor and scope are both read off the artifact

### RULE R-template-01 — the exemplar IS a live instance, never a description (checked)
The **exemplar** — everything above the `template notes` cut-line (R-template-08) — is **live markdown** (real H1, frontmatter, sections) with bare `{{PLACEHOLDERS}}`; it is **not** wrapped in code fences and is **not** a `## How to use` description of a template.
**Check pattern:** no triple-backtick fence encloses the exemplar; the file is not structured as prose *about* the form. *(Audit category: `template-is-spec`.)*
**Why:** a fenced or described "template" can't be copied into a working instance — wiki-links go inert, tables and headings don't render. A template must BE an entry.

### RULE R-template-08 — the exemplar ends at the `template notes` cut-line (checked)
A template's **exemplar** (the part that becomes the instance) ends at a **cut-line** whose anchor is the exact phrase **`template notes`**; everything from that line to end-of-file is *template metadata* (variable definitions + the notes) and is **removed on clone**. Canonical form: `✂ ──── template notes ──── ✂`. The matcher is lenient — the phrase `template notes` flanked by **≥3 dashes** of any kind, **case- and spacing-insensitive**; the `✂` scissors are an optional flourish. There is **no** bare `---` divider (ambiguous with frontmatter and horizontal rules) and **no** `# About this template` heading (superseded).
**Check pattern:** exactly one line matching `(?i)^\s*(✂\s*)?-{3,}\s*template\s+notes\s*-{3,}(\s*✂)?\s*$`; nothing below it is treated as exemplar content.
**Why:** the boundary between "copied into the record" and "instructions for whoever clones it" must be unmistakable. A cut-line carries its own metaphor (cut here; everything below is removed on clone), and a real record never contains the phrase `template notes` flanked by dashes.

### RULE R-template-02 — two placeholder forms; every variable is defined (checked)
A placeholder takes one of two forms, distinguished by **case**: an **`{{UPPER_SNAKE}}` variable** — reused across sites or structural (filename, key) — is **named and defined once** in the variable-definition list above the notes; a **`{{Mixed Case description}}`** placeholder is a **self-describing one-off**, described in place, needing **no** definition. Each definition (and each in-place description) states what to put **and what to do with no data** (fill / delete the line / delete the section). Full spec: [[DAS Template Variables]].
**Check pattern:** every distinct all-caps `{{UPPER_SNAKE}}` token appears in the definition list; `{{…}}` tokens containing a lowercase letter are self-describing and need no entry. No empty `{{}}` survives a clone.
**Why:** reuse/structure earns a named, referenceable variable with a definition; a one-off field that appears once is lighter described in place than mapped to a separate list — and forcing a definition for every field is the "scan up-and-down" overkill this rule avoids.

### RULE R-template-03 — repeating structure shows a pattern + a level-marked `...` (checked)
A section whose content repeats after creation (a LOG, a change history) ships **one variableized entry-pattern** followed by a **`...` repeat-marker at the structural level of the unit that repeats** — e.g. `### ...` beneath a `### {{date}} — …` entry means *another H3 entry* recurs, not the detail line. The pattern's fields stay `{{placeholders}}`, so it is never a fake concrete entry.
**Check pattern:** a repeating section carries a `{{…}}`-pattern + a `...`/`### ...` marker whose heading-level matches the repeating unit; no fake *filled* entry (`### 2026-06-29 — …`) appears. *(Audit category: `template-has-fake-cumulative-entries`.)*
**Why:** an empty header taught nothing about the shape; a *filled* entry invites pollution. A variableized pattern + a level-marked `...` shows the shape and what repeats without inviting a fake row.

### RULE R-template-04 — naming is `_{pattern} Template`; the middle IS the instance-name pattern (checked)
File templates are `_{pattern} Template.md`; folder templates are `_{pattern} Template/` holding a same-named marker. **Strip the leading `_` and the trailing ` Template` and what remains is the instance name** — so the `{pattern}` middle is the *instance-filename (or folder-name) pattern*, and is usually **variableized**, often **composite** (e.g. `_{{PURCHASE_DATE}} {{HOSTNAME}} Template.md` → `{{PURCHASE_DATE}} {{HOSTNAME}}.md`). The leading underscore is structural (sort-to-top + meta marker).
**Check pattern:** the basename matches `^_.+ Template(\.md)?$`; a folder template holds a same-named marker; a constant middle (`_Computer Template.md`) that would clone every instance to one name is flagged.
**Why:** the strip rule is how an instance gets its name; a constant middle produces collisions (every clone named the same), so the middle must carry the variable(s) that distinguish instances.

### RULE R-template-05 — folder templates carry a Template dispatch row (checked)
A folder that contains a `_*/` folder template has a `Template` row in its dispatch table linking the template. Detail: [[DAS Template Folders]].
**Check pattern:** for each folder holding a `_*/` template, its dispatch page contains a `Template` row. *(Audit category: `missing-folder-template-row`; [[rewire]] inserts it.)*
**Why:** the template is the folder's "start here" affordance; without the row it's invisible to anyone working in the folder.

### RULE R-template-06 — every template is reachable (sampled)
A folder-level template is reachable from its folder's dispatch (R-template-05); a template elevated up the ladder is reachable from the folders it governs (per [[DAS Template]] § Scope).
**Check pattern:** no `_*` template is unreachable from any dispatch or governed folder. *(Audit category: `orphan-template`.)*
**Why:** an unreachable template is dead meta-content — it can't be found at the moment it matters.

### RULE R-template-07 — the smoke test passes (sampled)
Copying the template, renaming it, and replacing-or-deleting every `{{VARIABLE}}` per the Variables section yields a usable instance: no leftover placeholders, no fake-looking sections.
**Check pattern:** a spot-instantiation leaves zero `{{…}}` tokens and no empty structural sections.
**Why:** the smoke test is the single end-to-end check that the template actually produces conformant instances.

### RULE R-template-09 — single-line is inline braces; multi-line is spanning braces (checked)
A placeholder holding **one line** sits in **inline braces** (`{{event title}}`); a placeholder holding a **multi-line block** uses **braces that span their own lines** — `{{` on its own line, the content between, `}}` on its own line. The spanning form is the explicit "this value is a block" signal.
**Check pattern:** multi-line values use line-spanning `{{ … }}`; single-line values use inline `{{…}}`. No positional guessing is relied on.
**Why:** an explicit brace-span removes ambiguity about whether a value is one line or a block, and survives reflow where a position-based convention (inline vs own-line) would not.

### RULE R-template-10 — folder templates share one variable namespace; an unbound filename variable repeats (checked)
In a **folder template** (`_{pattern} Template/`), every `{{VARIABLE}}` across the folder name, the member file names, and the bodies binds to **one unified value** — a single substitution fills the folder name, the marker name, sibling member names (e.g. `{{DISK_LABEL}} Manifest.md`), and the H1s together. A member file whose name carries an **unbound** variable is a **repeatable slot** — one instance per value (the inter-file analog of the intra-file `### ...`); no `...`-in-filename is used.
**Check pattern:** member names reuse the folder template's variables (one namespace); a member with an unbound-variable name is treated as repeatable; no literal `...` appears in a filename.
**Why:** unifying the namespace is what makes "name the folder and every file inside it from one value" work; and an unbound filename variable already means "one per value," so filename repetition needs no extra glyph.

### RULE R-template-11 — a specimen opening below `# H1` declares its anchor (checked)
check:: template_anchor_declared
A template's **anchor** — the thing it describes the shape of — is read off the specimen, never declared in a key. Per [[STEN Language]] the two markers are `# ... NAME` (a heading matching `NAME` at **this depth or deeper**) and `# == NAME` (**exactly this depth**), and a stencil carrying **no** marker governs the **whole document** — one of the language's four defaults, which is what makes the marker free for everything already written. Depth **floats**, and anchors **nest**: a marker may sit on a heading inside a specimen, with depth below it read against that heading rather than the file. Model: [[DAS Template]] § Anchor.

**What this rule catches is the ambiguous middle:** a specimen that opens at `##` or lower with no marker. By the default it claims the whole document; by its shape it is plainly a fragment of one; and a reader cannot tell which was meant. That is the wart the explicit marker was introduced to remove.

**The spine is skipped before the first heading is read, and that is load-bearing.** A specimen is *live markdown*, so it carries what a real instance carries — and per [[DAS spine]] a real page may open with a `:>>` breadcrumb or a masthead table above its H1. Reading line one instead of the first heading would call five conformant templates defects.

**Measured at arming, 2026-08-20 — 29 file templates: 24 root-anchored, 0 marker-anchored, 2 opening below `# H1` with no marker, 3 with no heading at all.** The two failures are the interesting number and they correct an earlier claim in this ruleset: [[TINK302 - Section templates and the scope ladder|F302]] predicted section templates as a future need, and the first draft of these rules recorded *zero* instances on the strength of a filename search for `_* Section Template.md`. **Searching the name found nothing because the name is not the mechanism** — searching the *shape* finds two, both written years before any marker existed: `_{{READ_DATE}} {{PAPER_TITLE}} Template.md` opens `### !{{READ_DATE}} - …` and `_BUY {{CATEGORY}} Template.md` opens `## === {{CATEGORY_HEADER}} ===`. Each is a repeating entry inside a larger document, spelled ad hoc. They are the corpus asking for this feature, not a migration this rule invented.

**Check pattern:** skip frontmatter and the spine (blank lines, `:>>` breadcrumbs, masthead table rows); read the first heading. Depth 1, or any depth carrying a `...` / `==` marker, passes. Depth >1 with no marker fails. **A specimen with no heading at all is deliberately out of scope** — one exists (a meeting-transcript template whose top is plain text) and may well be legitimate; refusing it needs a ruling, and having that argument by accident inside a rule about anchors would be the wrong place for it.
**Why:** a template is a specimen, so its own form is the most reliable place to state what it is about — but only if the form is unambiguous, and "opens at `##`" is not.

### RULE R-template-12 — two templates over one document have disjoint anchors (stated)
More than one template may govern the same document — that is the point of anchoring — **provided their anchors are disjoint**. The same anchor claimed twice is a **defect**, not something to reconcile: there is deliberately no merge algorithm, because each template describes only what sits under its own anchor and **elides** what another owns.

Two consequences, each a defect in its own right:

- **A partial picture is worse than none.** Under a heading another template owns, the outer template shows the heading and **nothing beneath it**. Half an example there contradicts the spec that actually owns the region, and a reader cannot tell it is partial.
- **Name loses to form.** The `_{Name} Section Template.md` spelling is readability — it keeps such a file inside the `_* Template` family this ruleset selects on. **If the name says Section and the specimen anchors at the root (or the reverse), the form wins and the name is the defect.** Measured 2026-08-20: **zero** files carry that name, while **two carry the shape** (R-template-11) — which is itself the argument for the precedence, since the name was never what anybody actually wrote.

**Check pattern:** *(stated, not yet checked)* no two templates in scope for one document resolve to the same anchor. **Arming waits on a scope-ladder resolver** — deciding which templates govern a given document means walking the ladder in [[DAS Template]] § Scope from the content folder up to the packaged root, and nothing implements that walk yet. This is a genuine missing mechanism, not a missing notation: the marker syntax has been pinned in [[STEN Language]] since 2026-08-07, and R-template-11 is checked on the strength of it.
**Why:** disjointness is what lets templates conjoin the way rules already do (`R-backlog` and `R-markdown` govern one file with no merge step), and it is the property that let the section rung collapse into an ordinary anchored template ([[TINK302 - Section templates and the scope ladder|F302]] Q4). A collision is the one case that breaks it, so it has to be nameable.
