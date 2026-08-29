# RULESET R-spine
include::
where:: `always, !mirror`
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

**Why:** the two forms are redundant — an anchor page's masthead already carries the breadcrumb in its first row, so a second `:>>` line is duplicate navigation; and a leaf doc that grew a self-masthead has stopped being a leaf. Either way the tree-of-containers navigation is muddied. Whether a masthead is *required* on a given anchor page depends on the anchor kind — that direction is [[DAS Anchor Page]]'s (`R-anchor-page`) kind-aware job, deliberately not asserted here (a per-file checker cannot classify anchor-page-ness reliably across the vault).

### RULE R-spine-02 — Standard doc head: breadcrumb → H1 → orientation line (checked)
check:: doc_head_orientation_line
mend:: doc-head

Every markdown doc opens with the `# H1` carrying the file's name (optionally ` — <subname or explanation>`), then an **orientation line** directly under it — a single sentence stating, at the coarsest grain, what this file is / what this item is about. Navigation takes exactly one of two forms (mutually exclusive per `R-spine-01`):

- **Breadcrumb form** (ordinary leaf docs) — the `:>>` breadcrumb top-row sits immediately above the H1 with **no blank line** between them; everything else (overview figure, tables, `## Overview`) follows below the orientation line. Exemplar: [[DAS Tracking Design]].
- **Masthead form** (anchor pages and spec/dispatch pages, e.g. facet specs) — no `:>>` row; a dispatch-masthead table sits **above the H1**, in the position the breadcrumb occupies on a leaf, its first row `-[[<name>]]-` + `: description` + breadcrumb, followed by rows such as Related / Examples / Rules and closing on an electric marker when it fronts a folder. The H1 and its orientation line follow beneath it. Exemplar: [[HBR]]. *(This bullet said "directly below the orientation line" until 2026-08-10; `R-spine-04` moved it, and the 921 pages still carrying the old order are that rule's advisory population, not a second reading of this one.)*
- **Simple facet form** (a short, slug-prefixed facet page with an obvious meaning and a simple essence) — the H1 itself fuses the breadcrumb: `# [[{slug}]] {Facet}`, where `{slug}` is the filename's leading token. That one line does triple duty — it names the facet, names the file (`{slug} {Facet}.md`), and links home — so there is **no `:>>` row, no masthead, and no orientation line**. The doc's **essence** (the main thing — a checklist, a table, a figure) follows the H1 directly. Its meaning is simply *slug ⊗ facet*, which the head already states, so re-explaining it in an orientation sentence is redundant. Use it only when the facet is short, its meaning is self-evident from the slug + facet name, and it has a single essence to lead with. Full shape + when-to-use: [[DAS Doc Structure]]; exemplar: [[26ACME Plan]]. Detected mechanically by `doc_head_orientation_line` (the H1 wiki-link target equals the filename prefix → orientation line waived).

**A table of contents is never part of the spine.** No form fuses one into its navigation. A TOC addresses *this page's own sections*, where every rule in this set addresses *other pages* — and the two zones scale differently: a breadcrumb is one line and a masthead a dozen rows, but a TOC grows with the document, so merging them puts an unbounded thing inside a bounded zone and costs the spine its scannability on exactly the long documents that earn a TOC at all. It belongs directly **below the orientation line and above the heart**, identically on both forms; `md-toc.py` decides whether a doc gets one, at what depth, and puts it there. Ruled 2026-08-10, retiring a masthead-merged TOC clause this set had carried since F308 M2 and which had zero instances vault-wide.

**Three shapes never take one at all — `list`, `stream`, `external`.** Each of those spines *is* an index: its rows already answer "what is here", and its H2s are entries rather than sections, so a TOC over one either restates the index or prints a column of dates. The shapes that keep a real document in the body — a leaf under a `breadcrumb`, or an anchor page whose rows are hand-curated (`curated`, `grouped`, `two-level`) — stay eligible, and the size floor decides from there. The shape is read from the page's own geometry by `skills/audit/scripts/spine.py`, never declared: a spine states its kind by the marker it carries and the way its rows are laid out, so no `.anchor` trait and no frontmatter key has to be kept in sync with it. That one classifier is shared by `spine_check.py` and `md-toc.py` — a second copy is how two callers come to disagree about what a page is.

**No other head shapes** — a doc that seems to need a head outside these three is a design question to raise, not a local deviation to make. The live counterexample is named in [[DAS spine]] § The escape: [[Agent Purview]], [[Agent Conventions]] and [[Agent Roster]] open frontmatter → H1 → summary, which is a fourth shape this rule says should not exist, and which is therefore a graded row or a repair rather than a quiet tolerance.

**Check pattern:** the mechanical slice is the **orientation line** (the breadcrumb/masthead geometry stays with `R-spine-01`): after the first H1 (outside fences), skipping blank lines and `key:: value` inline-field lines (skill pages carry `requires::`/`subsystem::` there), the first content must be a **prose line** — not a heading, table, list, blockquote, figure embed, or fence — and it must be a **single line**: the line after it is blank or the masthead table. Fails on (a) no prose line there, (b) the prose wrapping into a second line. Docs with no H1 pass (out of scope here), as do the script-rendered query surfaces (`Q.md`, `{slug} queries.md`) — their banner-only head is [[R-query]]'s shape, ruled by the user.

**Why:** the head is the reader's first disclosure layer — breadcrumb (*where am I*), H1 (*what is this called*), orientation line (*what is this*). Two standardized shapes make every doc scannable in two seconds; the longer summary belongs in `## Overview`, not the head. Ratified on [[DAS Tracking Design]] + [[DAS Status]] (2026-07-12).

### RULE R-spine-03 — An index doc fronting a folder carries a dispatch table (checked)
check:: summary_present_iff_complex

A doc that is its folder's **same-named index** (`Foo/Foo.md`), or that carries a `.anchor` beside it, summarizes the *folder*, not itself — so it opens with a **dispatch table linking the members**, letting a reader reach any of them in one click. Scope is read mechanically from that structure; no declaration is needed. Deliberately **not** extended to file-scope docs: a long doc's own table of contents is already `R-doc-structure-03` (`toc_table_iff_long`, same 300-line floor), and a second rule for one constraint is the duplication this system forbids. "Leave it deliberately" stays a legitimate outcome — the rule forces the consideration, not a particular table.

**Check pattern:** a same-named index (or `.anchor` sibling) whose folder holds ≥1 other `.md` carries ≥1 member wiki-link or dispatch row — **unless** it carries the machine `<!-- state:backlog -->` stamp or the machine `<!-- notebook -->` marker.

**First exemption: a folder-form backlog** (`{slug} Track/{slug} Backlog/{slug} Backlog.md`, [[TINK329 - Backlog hosts pointers; questions live in docs|F329]]). It fronts a folder and it *does* link its members — as derived pointer rows in `## Now` / `## Next` / `## Later`, which carry status and horizon a masthead link-list could not. Ruled [[TINK Backlog#^T363|T363]] Q1 = (A), 2026-08-19, after the rule fired on **every `state` mutation** to 13 folders across 9 anchors and three sessions logged it as known noise: a rule that is correct, unactionable and permanent trains agents to skim the whole warning tier.

The exemption is keyed to the **machine stamp**, not to "the body has links" — the narrow key is what stops a future index doc claiming the same licence for prose that happens to link a sibling. And the one thing a horizon body genuinely cannot show is a member doc whose row **retired**: `SONAR017` was an open question to Dan, orphaned by the F329 hoist and unreferenced anywhere in the vault for three days. That gap is real, and it is closed by `audit-q` **C58** rather than by a masthead — which is what makes this exemption safe to state, and why the alternative (a machine-maintained dispatch table above the file `state` parses and rewrites) buys nothing this does not.

**Second exemption: a notebook narrative** (`{PREFIX} - {Title}/{PREFIX} - {Title}.md`, [[TINK334 - Notebook facet - append-only experiment notebooks|F334]]). [[DAS Notebook]] had already ruled it — *"a notebook folder is **not** a sub-anchor — it takes no functional `.anchor` and no dispatch table; the `<!-- notebook -->` marker on the namesake is the machine-readable discriminator"* — and the narrative already carries one H2 per cell, each linking that cell's doc, so a masthead would restate every link in the body. Landed [[TINK Backlog#^T556|T556]], 2026-08-20, after the rule fired on **every `nb append`** ([[A2X]] reported it at 16 cells and declined to fix it locally, correctly: restructuring a notebook index is a facet decision and guessing would put a table on every notebook in the vault).

**Both exemptions are keyed to a marker a script writes**, never to the folder's shape or the presence of links in the body — the narrow key is what stops a future index doc claiming the same licence for prose that happens to link a sibling. Each carries a residual worth stating: for a backlog, a member doc whose row **retired** (closed by `audit-q` **C58**); for a notebook, a cell doc the narrative does not link, which is the smaller hole because `nb append` is the facet's only sanctioned write surface and writes the block and the doc in one act.

**Why:** absence, not staleness, is the primary failure here — the rule was long stated in prose and largely unfollowed because nothing in the write path forced the check. A folder index with no member links makes the reader open the folder to learn what is in it, defeating the point of having an index at all.

### RULE R-spine-09 — an anchor entry page opens with a spine at all (checked)
check:: valid_spine
mend:: spine-absent

Every other rule here asks *which* shape the spine is and whether its parts are in order. This one asks the prior question: **is there anything above the H1 to orient from** — a `:>>` breadcrumb, or a dispatch table's identity row. A page with neither has no answer to *where am I*, and no shape rule applies to it.

**Check pattern:** the page fronts its own folder (it is that folder's `{slug}.md` entry page, read from `.anchor`, not by basename) and carries neither a `:>>` breadcrumb nor an identity row → fail — **unless** it carries the machine `<!-- notebook -->` marker.

**Exemption: a notebook narrative** ([[TINK334 - Notebook facet - append-only experiment notebooks|F334]], landed [[TINK Backlog#^T556|T556]] 2026-08-20). [[DAS Notebook]] already ruled it — *"a notebook folder is **not** a sub-anchor — it takes no functional `.anchor` and no dispatch table"* — so a notebook narrative is not an anchor entry page and this rule's scope does not reach it.

**Why the exemption has to be written rather than falling out of the scope.** The scope above reads *"an anchor entry page, read from `.anchor`"*, which suggests declaring no `.anchor` would be enough to stay outside it. It is not, for two independent reasons, and both were measured rather than assumed. First, `entry_names` is a **union** seeded unconditionally with the folder's own basename — `.anchor` only *adds* a declared `slug`/`title` to it — so any `X/X.md` fronts its folder on basename alone, with no `.anchor` anywhere; a fixture built both ways returns `fronts_folder=True` in both. Second, `.anchor` is not the facet's to withhold: HookAnchor's scanner auto-mints a zero-byte one in every namesake folder on its 10-minute rescan, and `A2X013 - Game Break Overview/.anchor` duly exists on disk despite the facet declaring the folder is not an anchor. So the facet's *no* is recorded **only** in the marker, and the checker has to be told to read it. Keyed to the marker `nb` writes, for the same reason `R-spine-03`'s two exemptions are — a folder shape can be acquired by accident and a machine-written marker cannot.

**Why:** this is the rule that would have caught [[Stones]]. It was created 2026-08-10 with its H1 above the spine and a breadcrumb-first identity cell, and **nothing said a word** — four separate failures stacked, each on its own enough to keep the writer in the dark (§ Why this set was silent). Asking one blunt question first, and asking it where the answer is unambiguous, is what makes the check survivable at write time.

**Scope is entry pages only, deliberately.** For a folder's front door a spine is unambiguously required. For everything else the scope is a live question — [[TINK308 - Spine: the routing zone every document opens with|F308]] Q6, 4,941 files — and a write-time fail on an unsettled scope would land on every agent who touched any of them, which is how a rule teaches people to ignore it. 153 of 1,275 entry pages fail this today.

### RULE R-spine-10 — a spine is followed by an H1 (checked)
check:: spine_h1_present
fix:: spine_h1
mend:: spine-position

The spine says *where you are*; the `# H1` says *what this is called*. A page carrying one without the other has published half a head.

**Check pattern:** the page has a spine (breadcrumb or masthead) and no H1 anywhere → fail, auto-fixed.

**Why:** every other rule in this set keys off the H1 — its position, the line under it, the blank between them — so **none of them could see a page that has no H1 at all**. 417 vault pages were in that state when this rule was written, and the whole set had been reporting them clean. Auto-fixing is safe here because the title is not a guess: it is the file's own stem, which is already what every `[[wiki-link]]` to the page displays.

### RULE R-spine-04 — the spine sits above the H1, never below it (checked)
check:: spine_above_h1
fix:: spine_position
mend:: spine-position

A masthead is the **spine**: it states where the page sits before the page says what it is. So it goes *above* the `# H1`, in the same position the `:>>` breadcrumb occupies on a leaf. A page whose H1 comes first has put its title above its position, which reads as content-then-routing and breaks the head's disclosure order.

**Check pattern:** the doc's own identity-row masthead exists and the first H1 precedes it → warn.

**Why:** the two spine forms should be interchangeable in position, so a reader's eye lands in the same place on every page. Measured 2026-08-09: **921 vault pages** put the H1 above the spine, which is why this rule ships advisory (§ The grade, below).

### RULE R-spine-05 — the identity cell leads with its description (checked)
check:: identity_cell_description_first
fix:: spine_position
mend:: spine-position

The identity row's right-hand cell carries `<br>`-delimited segments. The **description** — the `: `-led one — comes first, and the `→ ` breadcrumb sits beneath it, so the first line reads *name + what this is*. User direction 2026-08-09: *"that's the way I want to do all of the tables."*

**Check pattern:** in the identity row's third cell, a `→ ` appears before a `: ` → fail (`fix:: spine_position` flips it on the write).

**Why:** the name alone does not say what a thing is, and the breadcrumb repeats what the page's location already tells you. Leading with the description makes the row answer the reader's actual question first.

**What the daemon does, read out of `sections.rs` rather than inferred from a sample** (2026-08-10, [[TINK Backlog#^T192|T192]]). `merge_desc_into_header_right` splits the cell on `<br>` and looks for the `: `-led segment. When it finds one it replaces that segment **in place**, so a cell that already pairs description and breadcrumb keeps whatever order it has — which is why a description-first cell survives a rebuild byte-identical, and equally why the 712 legacy breadcrumb-first cells are not self-healing: the daemon preserves them just as faithfully. Flipping those is the sweep's job, not the daemon's.

The one branch that **chose** an order is the one nobody sampled: a cell holding a breadcrumb and no description yet. There the merge appended, minting `→ breadcrumb<br>: description` — breadcrumb-first, against this rule, on a page the daemon had just touched. **254 vault cells are in that state**, so a sweep run before this was fixed would have been re-seeded page by page as descriptions landed, and would have read as a sweep that silently failed on a quarter of its work. Corrected in HookAnchor 2026-08-10 to emit the description first; pinned by `t017_merge_desc_preserves_breadcrumb_segment`, which now also asserts that a `→` breadcrumb rides along untouched — the reorder must not depend on recognising a marker `breadcrumb_marker_pos` deliberately does not match.

### RULE R-spine-06 — no blank line between the H1 and its orientation line (checked)
check:: orientation_line_adjoins_h1
fix:: spine_position
mend:: spine-position

The orientation line sits **directly** under the H1. A blank line between them separates the title from the sentence that explains it, and lets the two drift apart as the page grows.

**Check pattern:** a blank line follows the H1 and the next non-blank line is prose (not a heading or a table) → warn. This is the shape `R-spine-02`'s own checker skips past, which is why it needs its own rule rather than a tightening of that one.

**Why:** the H1 and its orientation line are one unit — the reader's second and third disclosure layers. 850 vault pages currently split them.

### RULE R-spine-07 — a masthead over a folder ends in an electric marker (checked)
check:: masthead_over_folder_has_marker
mend:: spine-marker

A page that fronts a folder with children **must** end its masthead with an electric marker (`...`, `---`, `^^^`). Without one, a child added to that folder never surfaces and the page silently goes stale.

**Check pattern:** the page is its folder's anchor entry page, the folder holds ≥1 other member, and the masthead carries no marker row → warn, naming the hidden-child count.

**Why:** absence is the failure mode here, exactly as in `R-spine-03` — nothing in the write path forces the check, so the omission is invisible until someone wonders where a file went. Note that **"fronts a folder" is not basename equality**: an anchor's entry page is `{slug}.md`, and a declared `slug:` or `title:` renames it away from the folder name. Testing `parent.name == stem` misses 45 anchor pages vault-wide; the checker reads `.anchor`. The rule deliberately says *every masthead **over a folder***, not *every masthead* — an [[DAS spine#External spine|external spine]] gathers members by a property rather than by location and has no folder to sweep, so a marker there would add wrong entries and still miss every real one.

### RULE R-spine-08 — a marker with nothing below it is degenerate (checked)
check:: marker_has_rows_below
mend:: spine-marker

A `---` or `^^^` marker declares that the machine writes the rows beneath it. When no rows appear, either the folder is empty or the page is claiming a régime it has no members for.

**Check pattern:** the marker is `---` or `^^^` and zero rows follow it inside the table → warn. `...` is excluded: an empty catch-all is the normal, correct state of a folder whose children are all already linked in the body (F081 body-mention suppression), and flagging it would manufacture 100+ false findings.

**Why:** a degenerate list or stream reads as "there is nothing here" when the truth is usually "this page has the wrong shape". 103 vault instances.

### RULE R-spine-11 — a mirrored doc carries no spine (checked)
where:: `mirror`
check:: mirrored_doc_has_no_spine
mend:: spine-mirrored

A doc inside a declared `here:` mirror route is copied into an external repo, where a `:>>` breadcrumb and a dispatch masthead are wiki-links and `hook://` URIs that render as literal noise. So it must carry **no spine at all** — not merely go ungraded.

**Check pattern:** the file sits under a `here:` route in `~/.config/anchor-system/mirror-routes.json` and carries a `:>>` breadcrumb or a dispatch identity row → fail.

**Why the prohibition rather than an exemption.** The two fail in opposite directions. An exemption says *do not look*, so a mirrored doc that acquires a breadcrumb — someone runs `spine fix` against a route not yet declared, or a doc is moved into a route carrying its vault masthead with it — is invisible forever, and the noise arrives on GitHub instead of in the audit. A prohibition says *look, and expect nothing*, so the same doc is a finding on the next pass. Ruled by Dan 2026-08-28: *"the rule should be mirrored docs cannot have a spine, because it just doesn't mean anything in the receiver's environment. I think it's probably the better rule."*

**It also removes an asymmetry.** `spine fix --vault` had already been taught to skip these routes, so without this rule two mechanisms encoded *do not repair* and nothing at all encoded *do not carry*. One rule, read by both, is the smaller surface.

**Adoption is nearly free, measured 2026-08-28.** Across the 4 resolvable routes there are 184 markdown docs; **zero** carry a breadcrumb and **one** carries a masthead — `prj/Alien Biology/Alien Biology Framework/ABIO Docs/ABIO Docs.md`. The rule starts at one finding, not at the 138 the old direction was suppressing.

**No `fix::`, deliberately.** Stripping a spine deletes authored rows, and which of them belong on the vault side of the route is a judgement; a fixer that guessed would destroy writing that has nowhere else to live. The `where:: mirror` selector is the exact inverse of the `, !mirror` this set now carries at ruleset level, so the two cannot drift: a doc is governed by -01…-10 or by -11, never by both and never by neither.

## Why this set was silent, and what changed on 2026-08-10

**A rule nobody hears is not a rule.** [[Stones]] was created on 2026-08-10 with its H1 above the spine and a breadcrumb-first identity cell — the exact two shapes `R-spine-04` and `-05` exist to catch — and the write hook said nothing. Four failures were stacked, each on its own sufficient:

- **Warden had never been recompiled** after this ruleset gained `-04` … `-08`, so those rules were not in the compiled set at all. `warden mend R-spine-04` answered *"no such rule"* while the remediation text sat finished on disk.
- **Four of the five `check::` names resolved to no registered checker.** They were written and left out of `audit-plan.py`'s `CHECKERS` dict, so they reported `error` — and `error` means *the rule's plumbing is broken*, which the write hook deliberately never shows the writer. Silent in both directions: the rules looked shipped, the writes looked clean.
- **The one checker that was registered graded `warn`**, and `execute_on_write` surfaces only `fail`. Advisory is invisible at the moment of writing, which is the one moment the page could have been fixed for free.
- **And no rule asked the blunt question** — *is there a spine at all* — so a page could be malformed in a way none of the shape rules matched.

**The fix is auto-repair, not a louder warning.** `R-spine-04`, `-05` and `-06` now carry `fix:: spine_position` and grade `fail`. A fail *with* a `fix::` is repaired in place by the write hook and reported as `✓ fixed`, so the cost to the writer is zero and the corpus converges on every touch instead of on a campaign. The fixer delegates to `spine_fix`, which keeps its own per-file proof — link multiset, H1 text, row multiset, description text, no lost line, and the sibling `.anchor` — and **refuses rather than writing** when any of them fails; a refusal falls through to a message for a human, which is the correct outcome for a page that needed judgment.

**`R-spine-07` and `-08` stay `warn`**, because neither has a safe automatic repair — choosing a marker and diagnosing a degenerate one are judgment calls. Promotion is [[TINK319 - Spine Agenda|F319]] M6, gated on the corpus being clean rather than on anyone's confidence. **A `fail` nobody can act on cheaply is the audit-noise trap**; a `fail` that fixes itself is not.

**Two codes stay deliberately absent.** `S09` (a marker on a page that fronts no folder, 581 files) has no rule because whether sweeping siblings is legitimate has not been decided. `S10` (a breadcrumb over a folder whose members the page hides, 84 files — [[TINK320 - Spine fitness: infer the spine a page SHOULD have, not just grade the one it has|F320]], armed 2026-08-11) reports without a rule for a different reason: it is a **fitness** finding, and its remedy is to invent dispatch rows, which is authoring rather than repair. It nominates a migration for a human to accept — the same posture the heart takes and for the same reason, that a wrong automatic fix is invisible afterward because the page then looks migrated. `R-spine-03` already states the rule `S10` measures against; what it lacks is a checker strict enough to see the failure, since `summary_present_iff_complex` is satisfied by **one** member link and `Corp.md` links 18 of its 132. `S01` (no spine at all) is now `R-spine-09`, but **scoped to anchor entry pages only** — 153 files, where the requirement is unambiguous — leaving the other 4,941 to [[TINK308 - Spine: the routing zone every document opens with|F308]] Q6. **Shipping a rule against an unsettled number is how a checker teaches the wrong thing.**

## Position in the catalog

Sits under [[R-doc]], beside [[R-progressive]] and [[R-dispatch-table]] — the three that between them govern a document's opening and its body. Applies to every markdown doc (`always`); each rule decides internally whether and how it constrains a given doc.

## Mend

### MEND spine-mirrored

This file is copied into an external repository, so its spine is noise there rather than routing. Delete the `:>>` breadcrumb or the dispatch masthead from this file.

If the routing is genuinely wanted, it belongs on a vault-side page that is **not** inside the route — sv-pipe's own `SVP.md` is the worked example: it sits outside all four routes and keeps its spine, which is Dan's ruling working in both directions (*"anything that is going to get mapped to the repository should be exempt. If it is not getting mapped to repository, then it should not be exempt."*).

Do not add the route to the exemption list to silence this. The routes are read from `~/.config/anchor-system/mirror-routes.json`, which `code sync` generates; if this file is not actually mirrored, the index is what is wrong.


Remediation messages for these rules — what to actually do when one fires. Reached as `warden mend R-spine-<nn>`; wired by the `mend::` line on each rule. State the fix, point at the facet, never restate it.

### MEND doc-navigation-form

Pick one navigation form and delete the other, then re-run the write.

A doc that *is* a container (an anchor page, a spec page) carries a dispatch masthead whose first cell is its own name — the breadcrumb rides in that first row, so a separate `:>>` line is duplicate navigation. Every other doc carries the `:>>` breadcrumb top-row and no masthead of its own.

Deciding which you have: if the file is `Foo/Foo.md`, or has a `.anchor` beside it, it is a container — keep the masthead, delete the `:>>` line. Otherwise keep the `:>>` line and delete the masthead. Do not hand-author the masthead you keep; run `/audit dispatch`, which builds it in the fixed row order and preserves the load-bearing `→ ` prefix on the identity cell.

For the model, read [[DAS spine]] and [[DAS Dispatch Table]].

### MEND doc-head

Add one prose sentence directly under the H1 saying what this file is, then re-run the write.

One line, not two — the check fails on a sentence that wraps into a second line as surely as on a missing one. It goes after the H1 and after any `key:: value` field lines, and before the masthead table or the first H2. Keep it coarse: what this file *is*, not what it currently says. The longer summary belongs in `## Overview`.

Three head shapes are legal and no others: breadcrumb form (`:>>` row directly above the H1, orientation line below), masthead form (no `:>>`, dispatch table directly below the orientation line), and simple-facet form (`# [[{slug}]] {Facet}` where `{slug}` is the filename's leading token — that H1 does the orienting itself, so no orientation line is wanted). If your doc seems to need a fourth shape, that is a design question to raise, not a local deviation to make.

Machine-written stamps are skipped, so a `<!-- state:backlog XX -->` line between the H1 and the orientation line is fine and does not need moving.

For the model, read [[DAS Doc Structure]]; for worked instances see [[DAS Tracking Design]] (breadcrumb form) and [[DAS Status]] (masthead form).

### MEND spine-position

Move the piece into its place, then re-run the write. Three rearrangements, all byte-level — nothing is invented and nothing is lost.

**Spine above the H1** (`R-spine-04`): cut the whole masthead table — identity row, separator, every row including everything below the electric marker — and paste it above the `# H1`, keeping the frontmatter above it. Move the block opaquely; never parse or rewrite the rows below the marker.

**Description first** (`R-spine-05`): in the identity row's right-hand cell, the segments are `<br>`-delimited. Put the `: <description>` segment first and the `→ <breadcrumb>` after it. **Split the row on unescaped pipes with a character scanner, not a regex** — wiki-links inside cells are written `[[Target\|Display]]`, and every regex of the form `[^|]*` either stops early or captures the backslash. That bug silently skipped 17 files on the first pass through this repo.

**Orientation line adjoining** (`R-spine-06`): delete the blank line between the H1 and the sentence under it. Machine-written stamps (`<!-- state:backlog XX -->`) legitimately sit between the two and stay where they are.

For the model, read [[DAS spine]]; exemplar: [[HBR]] carries all three.

### MEND spine-absent

The page fronts a folder but opens with nothing above its `# H1`, so a reader lands with no idea where they are. Give it one of the two spines — this is not auto-fixed, because which one it wants is a real choice.

**A dispatch table** is right when the page is a front door with children to route to. Four parts in order: an **identity row** whose left cell is the page's own name in initiator form (`-`, `[[Name]]`, `-`) and whose right cell holds a `: ` description then a `<br>` then the `→ ` breadcrumb; the **separator row**; any **hand-curated rows**; and last the **electric marker** row, `...` in the left cell and the right cell empty.

Description first, breadcrumb beneath (`R-spine-05`). The `...` catch-all sweeps whatever is in the folder and is not already linked in the body; everything below it is an electric zone HookAnchor recomputes, so never hand-author those rows.

*A live specimen is deliberately not printed here.* A masthead written out on this page would be read as **this ruleset's own** identity row — by the spine classifier, which reported it as an `S03` within a minute of being written, and by HookAnchor's harvest, which would take the specimen's description as this file's and sync it into a sibling `.anchor`. Copy the shape from [[HBR]] instead, which is a real one.

**A `:>>` breadcrumb** is right when the page is a leaf that happens to sit in its own folder — one row directly above the H1, orientation line below it.

Both go **above** the H1 and below the frontmatter. For the model read [[DAS spine]]; the worked instance is [[HBR]].

### MEND spine-marker

Give the masthead the row it is missing, then re-run the write.

**No marker over a folder** (`R-spine-07`): add a `| ... |  |` row as the table's last row. The catch-all is the valve — it sweeps whatever is in the folder and is not already linked in the page body. Do not hand-author its contents: everything below the marker is an electric zone that HookAnchor recomputes, and anything typed there is discarded on the next rebuild. If the folder holds so many files that the swept row would be noise, that is usually a sign the folder wants splitting, not that the marker wants suppressing.

**Degenerate marker** (`R-spine-08`): a `---` or `^^^` with nothing beneath it means the page is claiming a machine-written régime with no members. Either the folder is genuinely empty — in which case the page probably wants a curated `...` instead — or the page has the wrong shape. Check which before adding rows.

For the model, read [[DAS spine]] § The catchall is not optional and [[DAS Dispatch Table]] § Electric zones.

## See also

- [[DAS spine]] — the discipline this ruleset enforces.
- [[R-progressive]] — the sibling it was extracted from; owns everything below the H1.
- [[R-dispatch-table]] — the masthead's internals, deliberately not folded in here.
- [[R-doc]] — cross-cutting documentation conventions umbrella.
