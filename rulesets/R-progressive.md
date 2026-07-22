# RULESET R-progressive
where:: `always`
description:: layout conventions of progressive disclosure — checked on every markdown doc

The mechanical, whole-document layout checks of this discipline: the **conditional dispatch-table** placement and the **section-spacing** conventions. Applies to every markdown document (`always`); each rule decides internally whether and how it constrains a given doc. These are the deliberately *conditional, multi-check* rules — one rule that both determines what kind of doc it is looking at and makes several assertions accordingly — the case that stress-tests a declarative rule engine (per the [[Warden Roadmap]] item 8). Format of this set: [[DAS Ruleset]].

### RULE R-progressive-01 — never both a dispatch-masthead and a `:>>` breadcrumb (checked)
check:: dispatch_table_by_context

A doc uses **one** navigation form, never two: a **dispatch-masthead** marks the page that *is* a container (the anchor page); a **`:>>` breadcrumb** is the navigation on every other doc. A doc must **never carry both**.

**Check pattern:** the masthead considered is the doc's OWN self-referential masthead — a table row whose first cell is `-[[<this doc's name>]]-` (optionally aliased), per [[DAS Dispatch Table]]; an example masthead shown in the body (linking to a *different* page) and any masthead inside a code fence are ignored. Detect a `:>>` breadcrumb top-row (outside fences). If the doc has **both** its own masthead **and** a `:>>` breadcrumb → fail.

**Why:** the two forms are redundant — an anchor page's masthead already carries the breadcrumb in its first row, so a second `:>>` line is duplicate navigation; and a leaf doc that grew a self-masthead has stopped being a leaf. Either way the tree-of-containers navigation is muddied (per [[feedback_breadcrumb_vs_dispatch_table]]). Whether a masthead is *required* on a given anchor page depends on the anchor kind — that direction is [[DAS Anchor Page]]'s (`R-anchor-page`) kind-aware job, deliberately not asserted here (a per-file checker cannot classify anchor-page-ness reliably across the vault).

### RULE R-progressive-02 — progressive-disclosure section spacing (checked)
check:: progressive_disclosure_layout

The blank-line conventions that keep a doc's outline scannable: every `## H2` is preceded by a blank line, and the file carries no trailing blank lines. One rule, two assertions.

**Check pattern:** scanning outside fenced code blocks — (1) each `## H2` has a blank line immediately before it (no H2 glued to the prose above); (2) the last line is non-blank. Two conventions deliberately **excluded** as too noisy on ordinary docs: the anchor-page-only "no blank after the H1" glue rule (that is `R-anchor-page-07`'s job — an ordinary doc may have a blank after its H1) and the "no doubled blank line" rule (widely tolerated in practice).

**Why:** consistent section breaks let a navigator's eye find the structure at a glance — the second layer of progressive disclosure. An H2 glued to the prose above it hides where one section ends and the next begins.

### RULE R-progressive-03 — Standard doc head: breadcrumb → H1 → orientation line (checked)
check:: doc_head_orientation_line

Every markdown doc opens with the `# H1` carrying the file's name (optionally ` — <subname or explanation>`), then an **orientation line** directly under it — a single sentence stating, at the coarsest grain, what this file is / what this item is about. Navigation takes exactly one of two forms (mutually exclusive per `R-progressive-01`):

- **Breadcrumb form** (ordinary leaf docs) — the `:>>` breadcrumb top-row sits immediately above the H1 with **no blank line** between them; everything else (overview figure, tables, `## Overview`) follows below the orientation line. Exemplar: [[DAS Tracking Design]].
- **Masthead form** (anchor pages and spec/dispatch pages, e.g. facet specs) — no `:>>` row; a dispatch-masthead table sits directly below the orientation line, its first row `-[[<name>]]-` + the breadcrumb, followed by rows such as Related / Examples / Rules, and — when the doc is long enough to need one — a merged **Table of Contents** section inside the same table (blank row, bold `**Table of Contents**` row, then the entry rows). Exemplar: [[DAS Status]].
- **Simple facet form** (a short, slug-prefixed facet page with an obvious meaning and a simple essence) — the H1 itself fuses the breadcrumb: `# [[{slug}]] {Facet}`, where `{slug}` is the filename's leading token. That one line does triple duty — it names the facet, names the file (`{slug} {Facet}.md`), and links home — so there is **no `:>>` row, no masthead, and no orientation line**. The doc's **essence** (the main thing — a checklist, a table, a figure) follows the H1 directly. Its meaning is simply *slug ⊗ facet*, which the head already states, so re-explaining it in an orientation sentence is redundant. Use it only when the facet is short, its meaning is self-evident from the slug + facet name, and it has a single essence to lead with. Full shape + when-to-use: [[DAS Doc Structure]]; exemplar: [[26OMNI Plan]]. Detected mechanically by `doc_head_orientation_line` (the H1 wiki-link target equals the filename prefix → orientation line waived).

**No other head shapes** — a doc that seems to need a head outside these three is a design question to raise, not a local deviation to make.

**Check pattern:** the mechanical slice is the **orientation line** (the breadcrumb/masthead geometry stays with `R-progressive-01`): after the first H1 (outside fences), skipping blank lines and `key:: value` inline-field lines (skill pages carry `requires::`/`subsystem::` there), the first content must be a **prose line** — not a heading, table, list, blockquote, figure embed, or fence — and it must be a **single line**: the line after it is blank or the masthead table. Fails on (a) no prose line there, (b) the prose wrapping into a second line. Docs with no H1 pass (out of scope here), as do the script-rendered query surfaces (`Q.md`, `{slug} queries.md`) — their banner-only head is [[R-query]]'s shape, ruled by the user.

**Why:** the head is the reader's first disclosure layer — breadcrumb (*where am I*), H1 (*what is this called*), orientation line (*what is this*). Two standardized shapes make every doc scannable in two seconds; the longer summary belongs in `## Overview`, not the head. Ratified on [[DAS Tracking Design]] + [[DAS Status]] (2026-07-12).

## Position in the catalog

Sits under [[R-doc]] (cross-cutting documentation conventions umbrella), beside [[R-markdown]]. Applies to every markdown doc (`always`) — each rule decides internally whether/how it constrains a given doc.

## See also

- [[DAS progressive-disclosure]] — discipline spec this ruleset enforces.
- [[R-doc]] — cross-cutting documentation conventions umbrella.
- [[R-markdown]] — sibling always-applies ruleset (mechanical + authoring markdown rules).

### RULE R-progressive-04 — An index doc fronting a folder carries a dispatch table (checked)
check:: summary_present_iff_complex
A doc that is its folder's **same-named index** (`Foo/Foo.md`), or that carries a `.anchor` beside it, summarizes the *folder*, not itself — so it opens with a **dispatch table linking the members**, letting a reader reach any of them in one click. Scope is read mechanically from that structure; no declaration is needed. Deliberately **not** extended to file-scope docs: a long doc's own table of contents is already `R-doc-structure-03` (`toc_table_iff_long`, same 300-line floor), and a second rule for one constraint is the duplication this system forbids. "Leave it deliberately" stays a legitimate outcome — the rule forces the consideration, not a particular table.
**Check pattern:** a same-named index (or `.anchor` sibling) whose folder holds ≥1 other `.md` carries ≥1 member wiki-link or dispatch row.
**Why:** absence, not staleness, is the primary progressive-disclosure failure — the rule was long stated in prose and largely unfollowed because nothing in the write path forced the check. A folder index with no member links makes the reader open the folder to learn what is in it, defeating the point of having an index at all.

### RULE R-progressive-05 — Re-consider the summary when the covered content moves (checked)
check:: summary_fresh
A summary covers a **set of units** — its own `##` sections for a file-scope doc, the folder's member files for a container or tree. When a quarter of those units have changed, or **any** unit has been added or removed, since the summary was last written, the doc is flagged for re-consideration. Blessing is **observed, never self-reported**: when the summary region's own hash changes the agent has evidently rewritten it, so the current unit set is re-blessed automatically — there is no completion handshake for an agent to forget or overstate. Advisory only; it never blocks a write.
**Check pattern:** against the blessing registry (`~/.warden/disclosure.json`), changed-units ÷ total ≥ 0.25, or ≥1 unit added or removed.
**Why:** counting changed units is what "big chunks moved" means mechanically. File-size delta fires on typo fixes; hashing only the heading set misses a section rewritten wholesale under an unchanged heading — which is exactly when a summary goes stale.

