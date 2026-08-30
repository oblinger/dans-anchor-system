# RULESET R-template
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file: **/_* Template.md, **/_* Template/**`
description:: the Template facet — a domain-specific, folder-local structure for the items in one folder/tree

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

### RULE R-template-04 — the filename is a human label; only the ` Template` suffix is required (checked)
A template's filename carries **no mechanism**. Any semantic name the author likes is legal — `_Computer Template.md`, `_Disk Template/` — and by convention it opens with a leading `_` so it sorts to the top of the folder and reads as meta. **The one requirement is the suffix ` Template`, in title case**, and even that is a cheap **prefilter** rather than proof: what makes a file a stencil template is the declaration inside it (R-template-13).

**This rule was reversed on 2026-08-20 ([[Tink570 - Template identity moves inside the document|F570]] Q1), and the previous form is worth stating because the corpus is still full of it.** It used to read: strip the `_` and the ` Template` and what remains **is** the instance-name pattern — so the middle had to be variableized, and a *constant* middle like `_Computer Template.md` was a **defect**, on the grounds that every clone would collide on one name. That produced names like `_{{PURCHASE_DATE}} {{HOSTNAME}} Template.md` and `_{{DATE}} {{REPORT_TITLE}} Buy Survey Template.md`, unreadable in an `ls` precisely because they were carrying machinery. Dan: *"I think it generates very weird file names."* With the output path declared inside the document (R-template-14), the collision that justified the old rule cannot happen, and **the exact form the old rule flagged is now the recommended one.**

**Check pattern:** the basename ends ` Template` (`.md` for a file template) or ` Template/` for a folder template, with title-case `T`. A leading `_` is conventional and not required. No constraint on the middle — a constant middle is correct.
**Why:** a filename is read by humans in a listing far more often than it is parsed by anything, and the machinery it used to carry is now declared where it can also say things a filename cannot.

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

### RULE R-template-10 — a folder template declares a path per member; repetition is a free variable (checked)
In a **folder template**, the folder and each member declare their own `path::` (R-template-14), all binding against **one shared variable namespace** — so a single substitution fills the folder name, the marker, and every sibling member together. A member whose declared path holds a **free** variable is a **repeatable slot**: one instance per binding.

**Repetition needs no template-specific rule any more**, which is the point of the rewrite. *One instance per binding of a free variable* is [[STEN Language]]'s **many-by-variable** default, stated once for the whole language; a folder member is simply that default applied to a path. The `...`-in-a-filename glyph this rule used to forbid is still not used, and now there is nothing left for it to have meant.

**Rewritten 2026-08-20 (F570).** The previous form unified the namespace across the folder *name*, the member *filenames* and the bodies — correct while filenames were the mechanism, and describing something that no longer exists now that paths are declared.

**Check pattern:** every declared `path::` in a folder template resolves against the same variable namespace; a member path holding an unbound variable is read as repeatable; no literal `...` appears in a declared path.
**Why:** unifying the namespace is what makes *name the folder and everything in it from one value* work; and expressing repetition as a free variable means the folder case and the in-document case are the same rule rather than two.

### RULE R-template-13 — a stencil template declares itself, and declares its language version (checked)
check:: template_stencil_declared
Below the `template notes` cut-line (R-template-08), a stencil template carries

`stencil:: V1.0`

and that declaration — **not the filename** — is what makes the file a stencil template. Ruled by Dan 2026-08-20 ([[Tink570 - Template identity moves inside the document|F570]] Q1 (A)), with the `V` prefix his: *"let's put a V in front of 1.0 — so stencil, V1.0."*

**Two jobs, and the second is the one that will matter longest.** The first is disambiguation: a user file that merely happens to end in `Template` is not a stencil, and before this there was no way to say so. The second is **migration** — the token names the language version the specimen was written against, so when [[STEN Language]] changes, every template says which grammar to read it under. Nothing else in the corpus can do that, and a body of specimens with no version is a body that can only ever be migrated by hand.

**It lives below the cut-line, which is what makes it free.** That region already means *everything here is about the template and is removed on clone*, so the declaration cannot leak into an instance. Frontmatter was the obvious alternative and was rejected for exactly that reason: frontmatter **is inherited by the clone**, so every instance would carry a stray `stencil:: V1.0` unless something stripped it.

**Migration — the filename remains a fallback, deliberately.** No template in the corpus carried this declaration when the rule landed (measured 2026-08-20: **0 of 36**). If the declaration were the *sole* test from day one, every template in the vault would stop being a template at once. So detection is: **a `stencil::` declaration if present, else the ` Template` suffix** — and a template detected only by its suffix is a **finding**, never a non-template. The fallback is removed when the count reaches zero, not before.

**Check pattern:** a file detected as a template carries a `stencil::` line below the cut-line whose value matches `V\d+\.\d+`. Absent → fail, naming the file. Present but unparseable → fail.
**Why:** identity by filename cannot express a version and cannot be made unambiguous; a declaration does both, and the version is what makes a future grammar change survivable.

### RULE R-template-14 — a template declares the path it instantiates to (checked)
check:: template_path_declared
Below the cut-line, beside the variable definitions, a template declares

`path:: {{PURCHASE_DATE}} {{HOSTNAME}}.md`

naming the file it produces. This replaces the strip-the-filename derivation R-template-04 used to carry, and it is **required even when the exemplar is empty** — a blank template still has to say what it makes, which is the case that shows the declaration is doing real work rather than restating the name.

**A declared path can express what a filename structurally cannot.** A filename is one path segment, so a template could only ever produce a **sibling in its own folder**. A declared path carries structure — `{{YEAR}}/{{MONTH}}/{{SLUG}}.md` — and can place an instance into a subtree. That is a new capability rather than a tidier spelling of an old one, and it is the strongest argument for the change.

**Check pattern:** every template carries exactly one `path::` line below the cut-line; its value is non-empty; every `{{UPPER_SNAKE}}` variable in it is defined in the variables list (R-template-02). During migration a template with no `path::` is a finding, and the value derivable from its filename — strip the leading `_` and the trailing ` Template` — is what the fix writes.
**Why:** the name of the thing a template produces is a property of the template, not of where the template happens to be filed; declaring it also lets a template place its instance somewhere other than beside itself.

### RULE R-template-11 — a specimen opening below `# H1` declares its anchor (checked)
check:: template_anchor_declared
A template's **anchor** — the thing it describes the shape of — is read off the specimen, never declared in a key. Per [[STEN Language]] the two markers are `# ... NAME` (a heading matching `NAME` at **this depth or deeper**) and `# == NAME` (**exactly this depth**), and a stencil carrying **no** marker governs the **whole document** — one of the language's four defaults, which is what makes the marker free for everything already written. Depth **floats**, and anchors **nest**: a marker may sit on a heading inside a specimen, with depth below it read against that heading rather than the file. Model: [[DAS Template]] § Anchor.

**What this rule catches is the ambiguous middle:** a specimen that opens at `##` or lower with no marker. By the default it claims the whole document; by its shape it is plainly a fragment of one; and a reader cannot tell which was meant. That is the wart the explicit marker was introduced to remove.

**The spine is skipped before the first heading is read, and that is load-bearing.** A specimen is *live markdown*, so it carries what a real instance carries — and per [[DAS spine]] a real page may open with a `:>>` breadcrumb or a masthead table above its H1. Reading line one instead of the first heading would call five conformant templates defects.

**Measured at arming, 2026-08-20 — 29 file templates: 24 root-anchored, 0 marker-anchored, 2 opening below `# H1` with no marker, 3 with no heading at all.** The two failures are the interesting number and they correct an earlier claim in this ruleset: [[Tink302 - Section templates and the scope ladder|F302]] predicted section templates as a future need, and the first draft of these rules recorded *zero* instances on the strength of a filename search for `_* Section Template.md`. **Searching the name found nothing because the name is not the mechanism** — searching the *shape* finds two, both written years before any marker existed: `_{{READ_DATE}} {{PAPER_TITLE}} Template.md` opens `### !{{READ_DATE}} - …` and `_BUY {{CATEGORY}} Template.md` opens `## === {{CATEGORY_HEADER}} ===`. Each is a repeating entry inside a larger document, spelled ad hoc. They are the corpus asking for this feature, not a migration this rule invented.

**A specimen with no heading at all is LEGAL, and the reason is open world.** Ruled by Dan 2026-08-20 ([[Tink567 - Three templates open with no heading|T567]] Q1): *"a template can be blank. It just means that it's a blank file when you instantiate it… I think a blank file is legal."* This is not an exemption granted to three awkward files — it is [[STEN Language]]'s **open-world** default at its limit: *a stencil says what is present, never what is absent*, so a stencil that says nothing constrains nothing, which is a coherent thing for a stencil to do. A headingless specimen anchors at the document root by the same no-marker default that governs an `# H1`, and needs no marker for the same reason a stencil never needs an "and anything else" marker. **This paragraph replaces an earlier out-of-scope note** that called the case undecided and said refusing it would need a ruling; the ruling exists and it went the permissive way.

**Check pattern:** skip frontmatter and the spine (blank lines, `:>>` breadcrumbs, masthead table rows); read the first heading. Depth 1, or any depth carrying a `...` / `==` marker, passes. Depth >1 with no marker fails. **No heading at all passes** — the stated legal case above, not a gap in the pattern. Note the check reads the first **non-spine line**, so a specimen opening on a tag line (`#pp.`) or plain prose registers as headingless even when an `# H1` sits further down; that is correct, because the anchor is read from where the specimen *starts*.
**Why:** a template is a specimen, so its own form is the most reliable place to state what it is about — but only if the form is unambiguous, and "opens at `##`" is not. Silence is unambiguous; a fragment claiming a whole document is not.

### RULE R-template-12 — two templates over one document have disjoint anchors (stated)
More than one template may govern the same document — that is the point of anchoring — **provided their anchors are disjoint**. The same anchor claimed twice is a **defect**, not something to reconcile: there is deliberately no merge algorithm, because each template describes only what sits under its own anchor and **elides** what another owns.

Two consequences, each a defect in its own right:

- **A partial picture is worse than none.** Under a heading another template owns, the outer template shows the heading and **nothing beneath it**. Half an example there contradicts the spec that actually owns the region, and a reader cannot tell it is partial.
- **Name loses to form.** The `_{Name} Section Template.md` spelling is readability — it keeps such a file inside the `_* Template` family this ruleset selects on. **If the name says Section and the specimen anchors at the root (or the reverse), the form wins and the name is the defect.** Measured 2026-08-20: **zero** files carry that name, while **two carry the shape** (R-template-11) — which is itself the argument for the precedence, since the name was never what anybody actually wrote.

**Check pattern:** *(stated, not yet checked)* no two templates in scope for one document resolve to the same anchor. **Arming waits on a scope-ladder resolver** — deciding which templates govern a given document means walking the ladder in [[DAS Template]] § Scope from the content folder up to the packaged root, and nothing implements that walk yet. This is a genuine missing mechanism, not a missing notation: the marker syntax has been pinned in [[STEN Language]] since 2026-08-07, and R-template-11 is checked on the strength of it.
**Why:** disjointness is what lets templates conjoin the way rules already do (`R-backlog` and `R-markdown` govern one file with no merge step), and it is the property that let the section rung collapse into an ordinary anchored template ([[Tink302 - Section templates and the scope ladder|F302]] Q4). A collision is the one case that breaks it, so it has to be nameable.
