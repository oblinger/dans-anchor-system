# RULESET R-anchor-page
include::
import:: skills/audit/scripts/audit-plan.py
where:: `anchor`
description:: the `{slug}.md` entry-page format

What `/audit anchor` checks every `{slug}.md` against. All anchor-page kinds (skill / list / grouped / project root / sub-folder) share this set; worked instances of each kind live in [[FEX]]. Audit a page by reading these rules **or** by diffing it against the matching example. Format of this set: [[DAS Ruleset]].

## Identity & frontmatter

### RULE R-anchor-page-01 — the declaration alone makes the anchor; every field is optional (stated)

The anchor's **declaration** — a `.anchor` file, or a byte-exact `{Folder}.md` — is what makes the folder an anchor. **No field is required**, `slug:` and `traits:` included ([[ANC Standard]] § Standard fields: *"an empty `.anchor` … is already a complete anchor"*; `traits` defaults to `[simple]`). An anchor with no `slug:` is addressed by its **basename**, and any consumer needing a guaranteed handle uses the **implied slug** — the explicit slug when declared, otherwise the basename verbatim (§ S2).

**This rule asserts nothing.** It is stated so the anchor-page set opens by naming what identity actually rests on; the fields it used to demand are described by [[R-anchor-page]]-04 (`traits:` names the kind) and enforced only where a *declared* field implies an obligation — e.g. [[R-code-repository]]-01 asserts `code:` **when** `traits:` contains `code`. That conditional shape is the correct one: absence of a field is a default, not a defect.

**History — both halves were wrong, and neither was ever DAS policy.** The rule ran as `check:: anchor_has slug traits` until 2026-08-02.

- **`slug:` (dropped T104).** Never enforced anywhere but here, and contradicted by DAS's own tooling: `_anchor_slug` has always fallen back to the folder name, and `_entry_page`, `chk_h1_matches_slug`, `chk_entry_page_matches_slug` and `_ancestor_anchor_slugs` all resolve through it. **1,147 of 1,332 `.anchor` files (86%) declare no slug** — a requirement violated by six anchors in seven, enforced by no consumer.
- **`traits:` (dropped T105).** Same defect, larger: **1,085 of 1,332 (81%) declare no `traits:`**, and both [[ANC Standard]] and [[DAS Dot Anchor]] say plainly that no field is required. The justification written here on 2026-08-02 — *"an empty `.anchor` makes breadcrumb inference skip the anchor and jump to its grandparent (the DAS incident)"* — was **mis-transcribed** from the [[audit-anchor]] checklist, where that incident is attached to **`slug:`**, not `traits:`. It also fails to reproduce: **720 `.anchor` files in the live vault are zero-byte**, and of the 232 child docs beneath them that carry a breadcrumb, **182 name their empty anchor correctly**. The 50 that do not are hand-written short trails (`:>> [[SVAR]]`), not inference skipping a level.

The lesson worth keeping is the shape of the error rather than either field: a rule that asserts a field **no consumer reads** produces findings the corpus can only satisfy by mass-editing 1,000 files toward no benefit. Assert a field where something breaks without it.

### RULE R-anchor-page-02 — Page filename equals the slug (checked)
check:: entry_page_matches_slug

The entry page is named `{slug}.md` — the filename matches the `.anchor` slug (the H1's readable name may differ). Since 2026-09-01 (ATT T290) this is enforced in **both directions**: a missing entry page fails, and so does a **declared** slug whose folder note carries the folder name instead — `Agent Recipes/.anchor` declaring `slug: AREC` while the note is `Agent Recipes.md` fails with the rename. Dan, 2026-08-30: *"anytime a slug is defined in a folder, the folder file for that folder should be the slug name, not the full folder name."* The comparison is **byte-exact against the directory listing** — the filesystem is case-insensitive and `is_file()` would bless `muse.md` as `MUSE.md`.

**Check pattern:** `basename(page) == slug + ".md"` — **unless** the folder is a `stone` store, a **stone group**, or a **Warden corpus fixture**. Armed at zero: T289 renamed 20 notes and the vault-wide read-only scan on 2026-09-01 found no remaining violations, so the hard arm fires only on new drift.

**Exemption: a stone group's note is the kind's control file** ([[Atticus Backlog#^T289|ATT T289]] Q1, Dan 2026-08-31). `R-stone-01` names a group's control file by the kind template (`Hermes Book/Hermes Book.md`), never by a slug — renaming one to its slug broke `R-stone-01`, `-02` and `-07` at once. `_is_stone_group` keys on the control file derived from the kind table, accepting both control positions (inside the folder — the current namesake layout — and one level up) so the carve-out holds across the layout migration.

**Exemption: `warden/Warden Corpus/cases/*` fixtures** — deliberately minimal, several deliberately malformed, and they reuse slugs across cases (`FX1` three times). A rule firing on them makes Warden fail its own corpus. The exemption lives in the checker, not a suppression list, per the T290 design.

**Deliberately narrow:** an anchor with **no note at all** is the missing-entry-page arm (this rule's original finding), never the rename arm — three empty placeholder anchors (`ASR2`/`ASR3`/`ASR4`) would otherwise fail a rule about wrong *names* for having no name to be wrong about.

**Exemption: a stone store is not an anchor** ([[Tink Backlog#^T561|T561]], 2026-08-20, from [[Eli]]). `stone` writes `{slug} P####.md` into `{slug} Pebbles/` and keeps the control file **one level up** at `{slug} Pebble.md`, so the folder has no namesake by design. Measured through the real `--mode anchor --run` plan: this rule fired on **19 of 19** pebble stores — every anchor that has ever minted a pebble — and the only local remedy would have made that anchor the one deviant in the vault. Same shape as [[Tink Backlog#^T363|T363]] and [[Tink Backlog#^T556|T556]]: a rule correct on its face, unactionable in place, and permanent.

**The exemption is keyed to the control file, not to the missing namesake** — keying on "this folder has no namesake" would be circular, since that is exactly what this rule reports. `{slug} Pebble.md` beside the folder is a fact `stone` wrote and nothing acquires by accident. Both the folder suffix and the control name are derived from the kind table in [[DAS Stone]] (located by `stone_kinds_doc` in F080 config), which promises a third stone kind needs no code change; hardcoding `" Pebbles"` would break that promise.

**Rocks are matched by the same predicate and are unaffected**: 4 of 4 rock folders carry a namesake *and* an `.anchor` — a rock group is an anchor by design — so they passed before and pass now. The residual: a rock folder that **lost** its namesake would be silent here. It is small, and `R-dot-anchor` still reads that folder.

**One measurement lesson worth keeping.** The first pass at this count called `chk_entry_page_matches_slug` directly with the vault as `anchor_root`, got `pass` on every store, and concluded the rule fired on **1 of 19** — the opposite of the truth. A checker invoked outside its plan answers a different question than the plan asks. Count through `--mode anchor --run`, and with `--no-cache`, or the cache will hand back the pre-fix verdict and the fix will look inert.

### RULE R-anchor-page-03 — YAML `description:` present (checked)
check:: frontmatter_has description

The page opens with YAML frontmatter carrying a one-line `description:`.

**Check pattern:** frontmatter parses; `description` key present and non-empty. Inline `desc::` is a violation (deprecated → migrate to YAML).

### RULE R-anchor-page-04 — `traits:` declares the kind (stated)

`traits:` names the anchor kind (`[Code]`, `[skill]`, `collection`, …); the kind gates which rules below apply (design row, member zone, no-track-row).

### RULE R-anchor-page-05 — H1 is `{slug} - {Full Name}` (checked)
check:: h1_matches_slug

The H1 leads with the slug, then a dash, then the readable name — `# SVAI — Shared AI Development Skills`. Any dash form is accepted (`-`, `–`, `—`). An anchor with no short slug, or whose slug simply *is* its name, uses the bare name.

**Check pattern:** first H1 matches `^{slug}\s*[-–—]\s+\S`, or equals the slug, or equals the anchor folder name.

**Why:** the H1 does two jobs — it cements the jump-key so a reader learns the address, and it names the page in human terms. Slug-only hides the name; name-only hides the key.

## Top of page (fixed order)

### RULE R-anchor-page-06 — First sentence states the essence (stated)

A single sentence that states the **essence** — the core of what the page *is* or *does*, in one stroke. It answers "what is this, fundamentally?", not "what are its features, mechanisms, or edge cases". Lead with the essence; a little qualifying detail is fine, but a grab-bag of incidental facts is the failure. Everything that isn't the essence goes in an optional `## Overview` (or the body), never in this line and never above the dispatch table.

**Why:** this is the one line every reader — and every dispatch table that links the page — sees first; if the essence is buried under incidental detail, the reader must dig for what the thing fundamentally is. E.g. a skill page leads with the essence — *`/feature` creates a new feature document specifying work to be done* — not with a lead-in about collision-handling or status mechanics.

### RULE R-anchor-page-07 — No blank line after the H1 (checked)
check:: no_blank_after_h1

The summary sits on the line **immediately** after the H1 — no blank between them.

**Check pattern:** the line following the H1 is non-blank prose, not an empty line.

**Why:** the glue makes the summary read as part of the heading; blank lines precede only the figure and the table.

### RULE R-anchor-page-08 — Figure optional, no heading above it (stated)

A figure is optional; when present it follows the summary directly, with no heading line above it.

### RULE R-anchor-page-09 — Page order is H1 → summary → (figure) → dispatch (checked)

Those elements appear in that order with nothing else between them.

**Check pattern:** token order from the H1 down is H1, summary line, optional `!~~[[…]]~~` embed, then the dispatch table.

**Why:** progressive disclosure — broadest view first, navigation last ([[DAS progressive-disclosure]]).

## Dispatch table — masthead

### RULE R-anchor-page-10 — Table follows the Dispatch Table spec (sampled)

The dispatch table conforms to [[DAS Dispatch Table]] — a breadcrumb row then category rows.

**Check pattern:** delegate to `/audit dispatch`.

### RULE R-anchor-page-11 — First row is the breadcrumb cell (checked)
check:: breadcrumb_row

-[[This Page]]-`, then the parent-chain path ending in the page's `hook://` link + a one-line description.

**Check pattern:** row 1 matches `\| -\[\[.+\]\]- \| → .+\(hook://.+\)`.

**Why:** the breadcrumb carries the [[DAS anchor-dag]] up-edge.

### RULE R-anchor-page-12 — `Related`: lateral links only, first, omit-if-empty (checked)

`Related` is the first masthead row after the breadcrumb (when it has content), and is **omitted entirely when empty** — never left blank. It carries **only links that ordinary navigation cannot already reach**: NOT the anchor's own contents (reach those by going *in / down*), NOT its ancestors (reach those via the breadcrumb, going *up*), and NOT anything reachable from a parent anchor (you'd arrive there *through* the parent). `Related` is reserved for genuinely **lateral / cross-cutting** links none of those paths surface — e.g. a sibling project, a spec in another tree.

**Check pattern:** if present, `Related` has content and precedes other category rows; **none of its links is a breadcrumb ancestor, a member listed below, or the parent anchor** (those are redundant — drop them). Full masthead order: [[DAS Dispatch Table]] § Masthead rows.

### RULE R-anchor-page-13 — `Design` row present iff a design folder exists (checked)
check:: design_row_iff_folder

If `{slug} Design/` exists, a `Design` row is present as the second masthead row, members in the fixed order PRD → UX Design → CLI → API → Architecture → Decisions → Testing → Roadmap → Features. **Minimum form:** the row appears as soon as the `{slug} Design/` folder exists, carrying just the `~~[[{slug} Design]]~~` link with **zero member docs** (an empty design folder); members appear, in the fixed order, only as their files are created — the row lists only docs that exist, and grows over time.

**Check pattern:** `{slug} Design/` exists ⇔ a `Design` row exists. The member order above is **stated, not checked** — `chk_design_row_iff_folder` asserts only the biconditional, and the pattern claimed to "verify member order" for as long as it never did.

### RULE R-anchor-page-14 — Masthead is minimal (stated)

The masthead carries only the breadcrumb plus the fixed-order rows **Related → type → Design → Track → User Docs → Dev Docs** (each iff it applies) — no generic `Anchor` row, no `External` row (repo / site links live in Related), and no ad-hoc rows the breadcrumb already covers. Anything enumerable beyond a sub-area's key parts drops to the member zone. Full model: [[DAS Dispatch Table]] § Masthead rows.

### RULE R-anchor-page-15 — No `track` row on skill-ecosystem anchors (checked)
check:: no_track_row_if_ecosystem_traits

Wired 2026-08-11 ([[Tink Backlog#^T349|T349]]) — **2 findings across the vault's 1,395 anchors** (`examples/CSE` and [[SKD|Skill Docket App]]), against 1,395 LLM judgments before. The checker reads the fence-stripped page, so a doc explaining why these anchors carry no Track row is not failed for showing one in an example.

Wiring it also corrected the verdict it returns when an ecosystem anchor has **no entry page at all** — 20 DAS-repo skill and ruleset anchors. It answered `error`, which says the checker malfunctioned; the fault is real but belongs to `R-anchor-page-02`, whose checker names it. It now passes with a pointer there, so one absent page is reported once by the rule that owns it rather than twice in two voices.

A skill / facet / discipline / example anchor carries no `track` row.

**Check pattern:** if `traits` ∈ {skill, facet, discipline, example}, assert no `track` row.

**Why:** the skill ecosystem's tracking is one shared surface, not one per anchor — [[DAS Track]] § Who owns a Track folder.

### RULE R-anchor-page-16 — Wiki-links in cells escape the pipe (checked)

In-cell wiki-links use `~~[[target\|alias]]~~`.

**Check pattern:** no `~~[[…|…]]~~` inside a table cell with an unescaped `|`.

## Member zone — Collection anchors only

### RULE R-anchor-page-17 — Only a Collection enumerates members (stated)

Members are listed below the masthead only on a [[Collection]] anchor; every other kind is masthead-only.

### RULE R-anchor-page-18 — List = one row per member; grouped = many per row (sampled)

A **list** member zone puts **one member per row** (a `| --- | |` auto-list generates exactly that); a **grouped** zone puts **many members per row** under labeled `+` group rows. The split is **structural** (rows-per-member), not a count — though a flat list is usually grouped once it grows past ~15 ([[DAS granularity]]).

**Check pattern:** rows-per-member — one-per-row (list) vs many-per-row / `+` groups (grouped). ([[DAS granularity]])

### RULE R-anchor-page-19 — Group labels link down; `+` marks expandable (sampled)

Each group-row label is a link *down* to that group's own container page; a trailing `+` marks the label as an expandable container, not a leaf.

**Check pattern:** every group row's label cell is a wiki-link and carries `+`.

### RULE R-anchor-page-20 — Member zone ends with an electric marker (checked)

A Collection's member zone ends with `...` (compact auto), `| --- | |` (auto-list), or trailing `+` group rows.

**Check pattern:** the last member-zone row matches one of those markers.

**Why:** newly-added children need a defined place to land.

## Naming & exceptions

### RULE R-anchor-page-21 — Files and folders are `{slug}`-prefixed (checked)

Every file and folder inside the anchor is prefixed `{slug}` (`{slug} PRD.md`, `{slug} Docs/`, nested too).

**Check pattern:** list the anchor tree; assert each entry name starts with `{slug}`. (See [[DAS Naming]] / `R-naming`.)

### RULE R-anchor-page-22 — Every anchor carries a dispatch table (checked)

An anchor page is **never table-less** — it always carries a dispatch table whose first row is the breadcrumb (which carries the [[DAS anchor-dag]] up-edge, so every anchor needs it). A leaf / topic anchor with no hand-authored rows still carries **breadcrumb + a `...` auto-summary row**. Only **non-anchor** documents may omit the table.

**Check pattern:** every `{slug}.md` has a dispatch table with a breadcrumb row 1 (per R-anchor-page-11). ([[DAS Doc Structure]] § Top table states the same rule at the document layer.)

### RULE R-anchor-page-23 — Track row, and Status-triggered full scaffolding (checked)

Parallel to the Design row (R-anchor-page-13): a **`track` row** is present iff `{slug} Track/` exists — it links the track dispatch `[[{slug} Track\|Track]]`, members in the fixed order **Backlog → Status → Messages → Discussion → Inbox → Icebox → Log → ask**. (Roadmap + Features are *design* artifacts — they live in the Design row, not here, per the 2026-06-10 restructure.) **Minimum form (same as the Design row):** the row appears as soon as `{slug} Track/` exists, carrying just the `[[{slug} Track]]` link with zero members, and grows as track files are created. **SKA sub-projects (skills / facets / disciplines) have no `{slug} Track/` at all (R-anchor-page-15), so they never carry this row.**

**The status document is the full-scaffolding signal.** When `{slug} Status.md` exists, the anchor is a **fully-scaffolded** project and MUST carry the **complete** design + track doc set:

- **Every design document exists** (created even if empty), in `{slug} Design/`, listed in the `{slug} Design` dispatch, and surfaced as the **full Design row** in the PRD-first order of R-anchor-page-13: PRD → UX Design → CLI → API → Architecture → Decisions → Testing → Roadmap → Features.
- **Every track document exists** (created even if empty), in `{slug} Track/`, listed in the `{slug} Track` dispatch, and surfaced as the **full Track row** in the order above.
- **Each doc is linked in all three places** — its folder's dispatch page (the Design anchor / the Track anchor) **and** the matching masthead row. The two folders and the two masthead rows must agree.

Absent a Status doc, the Design / Track rows may be **partial** — listing only the docs that actually exist. The Status doc is what flips a project from partial to full. **This holds for most Code projects.**

**Check pattern:** `{slug} Status.md` exists ⇒ assert (a) every design doc + every track doc exists (empty allowed), (b) each is listed in its dispatch page, (c) the masthead Design + Track rows carry the full sets in the fixed orders. ([[R-anchor-page]]-13, [[DAS Design Dispatch]], [[DAS Track]])

## Kind-specific rules

Each anchor-page **kind** layers a small delta over the shared chassis (R-anchor-page-01…23) plus the [[DAS Dispatch Table]] form. The kind is read from `traits:`; a page is audited as **chassis + its kind's delta**. There are five kinds, each one-to-one with its dispatch-table shape (HookAnchor computes the table from the `.anchor`, so there is exactly one page — and one table kind — per anchor). The deltas are thin; each may graduate to its own `include::` sub-ruleset file once it grows.

### R-anchor-page-code — Code project (stated)

A code/software project anchor (`traits: [code]`).
- **Masthead roster:** breadcrumb + **Related** + **Design** (iff `{slug} Design/` — R-anchor-page-13) + **Track** (iff `{slug} Track/` — R-anchor-page-23) + **User Docs** (iff `{slug} User Docs/`) + **Dev Docs** (iff `{slug} Dev Docs/`). Each doc-area row's left cell links the sub-anchor (`~~[[{slug} Design\|Design]]~~`, …); its right cell enumerates that area's key parts.
- **Full scaffolding when a Status doc exists** — `{slug} Status.md` present ⇒ the complete design + track doc set exists (even empty) and is linked into both dispatch folders and the masthead Design + Track rows (R-anchor-page-23). True for most Code projects.
- **Member zone:** none — a switchboard masthead only.
- **Example:** [[HBR]].

### R-anchor-page-paper — Paper project (stated)

A long-form writeup anchor (`traits: [paper]`) — a paper / whitepaper that goes through revision cycles. **Signature / giveaway:** a `## Version history` **version table** of dated drafts with `s1, s2, s3 …` per-section markup (track-changes HTML per section). Full trait spec: [[Paper Anchor]].
- **Masthead roster:** breadcrumb + **Related** (incl. any published-landing link) + a **Drafts** row (dated versions, newest = Current) + **Research**; ends with `...`.
- **Member zone:** the version table under `## Version history` (the dated-draft × section-markup grid).
- **Example:** [[ABP]].

### R-anchor-page-subproject — SKA sub-project: facet / discipline / skill-doc (checked)

A single skill-ecosystem spec page — a **facet**, a **discipline**, or a **skill-doc** (the documentation page for a skill; *not* the skill folder's `SKILL.md` runbook, which is out of scope).

**SKA sub-projects are the exception to the project pattern.** A skill / facet / discipline is part of the *single* SKA project, so **SKA owns its tracking** — each is too small to merit its own backlog. But the sub-projects are too numerous to fold into one unified SKA design, so each **merits its own design**: as much design system as it needs, from nothing (just the design anchor) up to a full PRD + UX + architecture. The exception in one line: **own design (however small), no tracking, no status.**
- **Masthead roster:** breadcrumb + **Related** + the **type row** (`skill` / `Discipline` / `Facet`, carrying the runtime / user-doc links) + **Design** (**always present** — the `{slug} Design/` folder is mandatory per § Minimum shape, so every SKA sub-project carries exactly one Design row). The Design row may be **empty** — carrying just the `~~[[{slug} Design]]~~` link to the design anchor page and no member docs — and grows in the D07 order as docs are added (R-anchor-page-13).
- **Owns Design, not Track** — every SKA sub-project anchor (skill / facet / discipline / example) **owns its own design but never its own tracking**. Per [[DAS Track]] § Who owns a Track folder the ecosystem's work queue lives with the agent working it ([[Tink Backlog]] / [[Tink queries]]) while design and features stay with the subject (`SKA Design/`); a per-anchor `{slug} Track/` is forbidden for these kinds.
- **No `track` row** — follows from the above (this is R-anchor-page-15 in kind terms).
- **No `Status`** — a SKA sub-project carries **no `{slug} Status.md`**. Design-phase completeness is tracked only for SKA-the-project, never per sub-project — you can design a skill, but there is no completeness rollup for it.
- **Minimum shape** — a dispatch table + a `{slug} Design/` folder that is **present from creation with its `.anchor` even when it holds no design docs yet** — the folder stands ready so design can land later without restructuring. It grows by adding `{slug} PRD.md` and other design docs as the anchor earns them — many skills / facets need little design. The Design row (R-anchor-page-13) is present whenever the folder is, carrying zero members until docs arrive.
- **Flat layout** — `{slug} Design/` sits **directly under the anchor root**, with **no `{slug} Docs/` wrapper** (the wrapper is for large project anchors; SKA sub-projects stay flat).
- **Member zone:** none.
- **Content** differs by sub-kind (facet spec vs. discipline vs. skill-doc) but the page *structure* is shared — one ruleset, three example flavors.
- **Examples:** facet → [[DAS Anchor Page]]; discipline → [[DAS progressive-disclosure]]; skill-doc → [[DAS Mint]] *(currently a thin doc with no masthead — the bring-up target, tracked separately; do not treat as compliant).*

### R-anchor-page-container — Container: grouped / list / reverse-dated (sampled)

A [[Collection]] anchor whose body enumerates **homogeneous members** (a features folder of feature docs, a log folder of log entries, the `SKL` catalog of skill-docs).
- **Masthead roster:** breadcrumb + Related (minimal) — then the member zone.
- **Member zone required** — the generic member rules R-anchor-page-17…20 apply. The layout split is **structural — rows-per-member — not a count** (one axis, three values):
  - **list** — **one row per member** (each row is a single entry). A `| --- | |` separator auto-generates exactly this: HookAnchor emits one row per child. Count is irrelevant — a 30-entry auto-list is still a list. Examples: [[SV]], [[RR]], [[Roots]], [[SKA Access]].
  - **grouped** — **each row is a group holding many members** (a category row, often `+`-expandable, carrying several links). Typically chosen once a flat list grows past ~15 ([[DAS granularity]], R-anchor-page-18), but the defining mark is **many-members-per-row**. Examples: [[Log]], [[DAS Facets]], [[DAS Skills]].
  - **chronological (reverse-dated)** — a [[DAS stream]]; newest-first, ISO-prefixed member names. Example: [[HBR Log]].
- Member zone ends with an electric marker (R-anchor-page-20) so new children have a place to land.

### R-anchor-page-topic — Topic (stated)

A topic / domain-of-life folder page — a hub that routes to the pages within the topic.
- **Masthead roster:** breadcrumb + optional Related.
- **`...` auto-summary required** — the member zone is a single compact `...` row (`| ... |  |`) that auto-enumerates the topic's contents (HookAnchor fills it). Every topic page carries it, so the whole topic is summarized and new children have a place to land. A topic is thus a compact auto-listing container.
- **Table required** — like every anchor (R-anchor-page-22), a topic page always has a dispatch table; the minimum is breadcrumb + `...`. Never table-less.
- **Example:** [[Life]].
