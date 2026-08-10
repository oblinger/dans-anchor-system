# RULESET R-spine
where:: `always`
confirm:: user
description:: the routing zone every document opens with — which of the two forms a document gets, and the fixed line order that follows
import:: skills/audit/scripts/audit-plan.py

Every document opens with exactly one **spine**: a `:>>` breadcrumb or a dispatch masthead, chosen by the document's role rather than by taste. This set owns that choice and the line order that follows it. Everything below the H1 belongs to [[R-progressive]], which after this extraction mentions routing nowhere. Discipline: [[DAS spine]]; measurement and the four shapes: [[TINK308 - Spine: the routing zone every document opens with|F308]]. Format of this set: [[DAS Ruleset]].

**Extracted from [[R-progressive]] by F308 M2**, where these three lived as routing rules inside the *progressive-disclosure* set. That mislocation was the tangle F308 named: a rule about where a reader is cannot be audited from the same set as a rule about what they read next, and the two had been growing into each other for as long as both existed. The rules keep their bodies and their checkers verbatim — this is a move, verified by the vault-wide verdict set being unchanged — and only their ids and their home changed.

**The whole set carries `confirm:: user`.** There should not be many exceptions to a two-way rule, so an agent may not accept one unaided: it asks, then records the grade it is given. An ungraded proposal against any rule here fails the anchor's exception table rather than sitting there as a permanent pending ([[R-exception-discipline]] -09).

**What this set does NOT own: the masthead's internals.** [[R-dispatch-table]] keeps every rule about row order, cell escaping, row labels and the separator row, and is not folded in here. Those govern the *content* of one spine form; this set governs *which form a document gets*. Splitting them the other way would put two authorities over one table — the failure this extraction exists to end, repeated one level down.

### RULE R-spine-01 — never both a dispatch-masthead and a `:>>` breadcrumb (checked)
check:: dispatch_table_by_context
mend:: doc-navigation-form

A doc uses **one** navigation form, never two: a **dispatch-masthead** marks the page that *is* a container (the anchor page); a **`:>>` breadcrumb** is the navigation on every other doc. A doc must **never carry both**.

**Check pattern:** the masthead considered is the doc's OWN self-referential masthead — a table row whose first cell is `-[[<this doc's name>]]-` (optionally aliased), per [[DAS Dispatch Table]]; an example masthead shown in the body (linking to a *different* page) and any masthead inside a code fence are ignored. Detect a `:>>` breadcrumb top-row (outside fences). If the doc has **both** its own masthead **and** a `:>>` breadcrumb → fail.

**Why:** the two forms are redundant — an anchor page's masthead already carries the breadcrumb in its first row, so a second `:>>` line is duplicate navigation; and a leaf doc that grew a self-masthead has stopped being a leaf. Either way the tree-of-containers navigation is muddied (per [[feedback_breadcrumb_vs_dispatch_table]]). Whether a masthead is *required* on a given anchor page depends on the anchor kind — that direction is [[DAS Anchor Page]]'s (`R-anchor-page`) kind-aware job, deliberately not asserted here (a per-file checker cannot classify anchor-page-ness reliably across the vault).

### RULE R-spine-02 — Standard doc head: breadcrumb → H1 → orientation line (checked)
check:: doc_head_orientation_line
mend:: doc-head

Every markdown doc opens with the `# H1` carrying the file's name (optionally ` — <subname or explanation>`), then an **orientation line** directly under it — a single sentence stating, at the coarsest grain, what this file is / what this item is about. Navigation takes exactly one of two forms (mutually exclusive per `R-spine-01`):

- **Breadcrumb form** (ordinary leaf docs) — the `:>>` breadcrumb top-row sits immediately above the H1 with **no blank line** between them; everything else (overview figure, tables, `## Overview`) follows below the orientation line. Exemplar: [[DAS Tracking Design]].
- **Masthead form** (anchor pages and spec/dispatch pages, e.g. facet specs) — no `:>>` row; a dispatch-masthead table sits directly below the orientation line, its first row `-[[<name>]]-` + the breadcrumb, followed by rows such as Related / Examples / Rules. Exemplar: [[DAS Status]].
- **Simple facet form** (a short, slug-prefixed facet page with an obvious meaning and a simple essence) — the H1 itself fuses the breadcrumb: `# [[{slug}]] {Facet}`, where `{slug}` is the filename's leading token. That one line does triple duty — it names the facet, names the file (`{slug} {Facet}.md`), and links home — so there is **no `:>>` row, no masthead, and no orientation line**. The doc's **essence** (the main thing — a checklist, a table, a figure) follows the H1 directly. Its meaning is simply *slug ⊗ facet*, which the head already states, so re-explaining it in an orientation sentence is redundant. Use it only when the facet is short, its meaning is self-evident from the slug + facet name, and it has a single essence to lead with. Full shape + when-to-use: [[DAS Doc Structure]]; exemplar: [[26ACME Plan]]. Detected mechanically by `doc_head_orientation_line` (the H1 wiki-link target equals the filename prefix → orientation line waived).

**A table of contents is never part of the spine.** No form fuses one into its navigation. A TOC addresses *this page's own sections*, where every rule in this set addresses *other pages* — and the two zones scale differently: a breadcrumb is one line and a masthead a dozen rows, but a TOC grows with the document, so merging them puts an unbounded thing inside a bounded zone and costs the spine its scannability on exactly the long documents that earn a TOC at all. It belongs directly **below the orientation line and above the heart**, identically on both forms; `md-toc.py` decides whether a doc gets one, at what depth, and puts it there. Ruled 2026-08-10, retiring a masthead-merged TOC clause this set had carried since F308 M2 and which had zero instances vault-wide.

**Three shapes never take one at all — `list`, `stream`, `external`.** Each of those spines *is* an index: its rows already answer "what is here", and its H2s are entries rather than sections, so a TOC over one either restates the index or prints a column of dates. The shapes that keep a real document in the body — a leaf under a `breadcrumb`, or an anchor page whose rows are hand-curated (`curated`, `grouped`, `two-level`) — stay eligible, and the size floor decides from there. The shape is read from the page's own geometry by `skills/audit/scripts/spine.py`, never declared: a spine states its kind by the marker it carries and the way its rows are laid out, so no `.anchor` trait and no frontmatter key has to be kept in sync with it. That one classifier is shared by `spine-check.py` and `md-toc.py` — a second copy is how two callers come to disagree about what a page is.

**No other head shapes** — a doc that seems to need a head outside these three is a design question to raise, not a local deviation to make. The live counterexample is named in [[DAS spine]] § The escape: [[Agent Purview]], [[Agent Conventions]] and [[Agent Roster]] open frontmatter → H1 → summary, which is a fourth shape this rule says should not exist, and which is therefore a graded row or a repair rather than a quiet tolerance.

**Check pattern:** the mechanical slice is the **orientation line** (the breadcrumb/masthead geometry stays with `R-spine-01`): after the first H1 (outside fences), skipping blank lines and `key:: value` inline-field lines (skill pages carry `requires::`/`subsystem::` there), the first content must be a **prose line** — not a heading, table, list, blockquote, figure embed, or fence — and it must be a **single line**: the line after it is blank or the masthead table. Fails on (a) no prose line there, (b) the prose wrapping into a second line. Docs with no H1 pass (out of scope here), as do the script-rendered query surfaces (`Q.md`, `{slug} queries.md`) — their banner-only head is [[R-query]]'s shape, ruled by the user.

**Why:** the head is the reader's first disclosure layer — breadcrumb (*where am I*), H1 (*what is this called*), orientation line (*what is this*). Two standardized shapes make every doc scannable in two seconds; the longer summary belongs in `## Overview`, not the head. Ratified on [[DAS Tracking Design]] + [[DAS Status]] (2026-07-12).

### RULE R-spine-03 — An index doc fronting a folder carries a dispatch table (checked)
check:: summary_present_iff_complex

A doc that is its folder's **same-named index** (`Foo/Foo.md`), or that carries a `.anchor` beside it, summarizes the *folder*, not itself — so it opens with a **dispatch table linking the members**, letting a reader reach any of them in one click. Scope is read mechanically from that structure; no declaration is needed. Deliberately **not** extended to file-scope docs: a long doc's own table of contents is already `R-doc-structure-03` (`toc_table_iff_long`, same 300-line floor), and a second rule for one constraint is the duplication this system forbids. "Leave it deliberately" stays a legitimate outcome — the rule forces the consideration, not a particular table.

**Check pattern:** a same-named index (or `.anchor` sibling) whose folder holds ≥1 other `.md` carries ≥1 member wiki-link or dispatch row.

**Why:** absence, not staleness, is the primary failure here — the rule was long stated in prose and largely unfollowed because nothing in the write path forced the check. A folder index with no member links makes the reader open the folder to learn what is in it, defeating the point of having an index at all.

## Position in the catalog

Sits under [[R-doc]], beside [[R-progressive]] and [[R-dispatch-table]] — the three that between them govern a document's opening and its body. Applies to every markdown doc (`always`); each rule decides internally whether and how it constrains a given doc.

## Mend

Remediation messages for these rules — what to actually do when one fires. Reached as `warden mend R-spine-<nn>`; wired by the `mend::` line on each rule. State the fix, point at the facet, never restate it.

### MEND doc-navigation-form

Pick one navigation form and delete the other, then re-run the write.

A doc that *is* a container (an anchor page, a spec page) carries a dispatch masthead whose first cell is its own name — the breadcrumb rides in that first row, so a separate `:>>` line is duplicate navigation. Every other doc carries the `:>>` breadcrumb top-row and no masthead of its own.

Deciding which you have: if the file is `Foo/Foo.md`, or has a `.anchor` beside it, it is a container — keep the masthead, delete the `:>>` line. Otherwise keep the `:>>` line and delete the masthead. Do not hand-author the masthead you keep; run `/audit dispatch`, which builds it in the fixed row order and preserves the load-bearing `→ ` prefix on the identity cell.

For the model, read [[DAS spine]], [[DAS Dispatch Table]] and [[feedback_breadcrumb_vs_dispatch_table]].

### MEND doc-head

Add one prose sentence directly under the H1 saying what this file is, then re-run the write.

One line, not two — the check fails on a sentence that wraps into a second line as surely as on a missing one. It goes after the H1 and after any `key:: value` field lines, and before the masthead table or the first H2. Keep it coarse: what this file *is*, not what it currently says. The longer summary belongs in `## Overview`.

Three head shapes are legal and no others: breadcrumb form (`:>>` row directly above the H1, orientation line below), masthead form (no `:>>`, dispatch table directly below the orientation line), and simple-facet form (`# [[{slug}]] {Facet}` where `{slug}` is the filename's leading token — that H1 does the orienting itself, so no orientation line is wanted). If your doc seems to need a fourth shape, that is a design question to raise, not a local deviation to make.

Machine-written stamps are skipped, so a `<!-- state:backlog XX -->` line between the H1 and the orientation line is fine and does not need moving.

For the model, read [[DAS Doc Structure]]; for worked instances see [[DAS Tracking Design]] (breadcrumb form) and [[DAS Status]] (masthead form).

## See also

- [[DAS spine]] — the discipline this ruleset enforces.
- [[R-progressive]] — the sibling it was extracted from; owns everything below the H1.
- [[R-dispatch-table]] — the masthead's internals, deliberately not folded in here.
- [[R-doc]] — cross-cutting documentation conventions umbrella.
