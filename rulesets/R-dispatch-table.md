# RULESET R-dispatch-table
include::
import:: skills/audit/scripts/audit-plan.py
where:: `sentinel: ^\|\s*(?:-\[\[[^\]]+\]\]-|~~\[\[[^\]]+\]\]~~)\s*\||^\|[^\n]*hook://[^\n]*\|\s*$`
description:: The shape every dispatch table must take — masthead-placement law, member-zone mechanics, and pipe-escaped cell links.

> **The selector moved out of YAML frontmatter into the body 2026-08-11 ([[TINK Backlog#^T535|T535]]), and the delta was measured before the move rather than assumed.** `parse_ruleset_block` reads only body `field::` lines, so the frontmatter `where:` was invisible to both engines — `audit-plan` and `warden compile` each carried all **15** of these rules as `where=None`, which falls through to the `always` default. **For markdown that turned out to cost nothing**, and the reason is worth writing down: `enumerate_scope` in anchor mode enumerates `*.md` only, so `always` and `{anchor}/**/*.md` select the identical **905** files in this repo, and the on-write doc-fire routes non-markdown away from [[R-doc]] entirely (F297's `rows_for`: markdown fires the umbrella, every other kind fires only what its anchor declares by trait). **The one path where it bit is `/audit doc` named at a non-markdown file.** Measured on `skills/audit/scripts/queries-render.py`: all 15 masthead rules were in play, **15 of the 31** rule-target pairs the audit produced — half the run — and the three that carry a `check::` each answered `pass` on a Python file, a green verdict about a masthead the file cannot have. That is the whole finding delta, and it is now zero.
>
> **Then the selector moved a second time, from every-markdown to a `sentinel:`, and that one was the expensive defect ([[TINK Backlog#^T349|T349]], same day).** Every rule in this set is about the *contents* of a dispatch table — row order, cell links, the catch-all marker; **not one asserts that a page must have one**. So scoping to `{anchor}/**/*.md` asked an LLM, of every markdown file in every anchor, whether its masthead rows appeared in the fixed order. Measured on TINK's judgment manifest: **336 of 911 tasks — 37% of the entire bill — were this one set**, 12 judged rules across 28 files of which **3** carry a masthead. Vault-wide the sentinel selects **1,332 of 8,055** markdown files, a 6× reduction.
>
> **The regex is deliberately a union of two independent tests, because the failure directions are not symmetric.** Over-inclusion costs one judgment call on a feature doc that quotes a masthead; under-inclusion is a *silent green* over a real dispatch table, which is the exact defect this row exists to name. The two tests — the identity cell in either live spelling (`-[[X]]-`, 1,296 files; the struck `~~[[X]]~~` the facet describes, 49) and any table row bearing a `hook://` link (1,301) — agree on 97.5% of the corpus and are unioned rather than chosen between. Their disagreements are feature docs discussing dispatch tables, so the union keeps them and judges them rather than guessing.
>
> **Nothing mechanical is lost, and that was measured rather than argued.** Running this set's three `check::` rules over every markdown file in three anchors produced 3,774 verdicts, 12 of them non-`pass` — and **every one of the 12 sits on a file the sentinel keeps**. On the files it drops, the checkers answered `pass`: a green verdict about a masthead the file does not have.

### RULE R-dispatch-table-01 — Masthead rows appear in a fixed order (checked)
mend:: dispatch-rebuild
After the breadcrumb identity row, the masthead's optional rows appear in this **fixed order**, each present **only if it applies**: **Related** → **type row** (skill / discipline / facet leaf anchors only) → **Design** → **Track** → **User Docs** → **Dev Docs**. There is **no generic `Anchor` row** (superseded — everything is an anchor; the label conveyed nothing). Every row after the breadcrumb has the **same shape**: its **left cell is a link *down* to that sub-area** (the row's name), and its **right cell enumerates that sub-area's key parts** for one-click access. Per-row rules: R-08 (Related) … R-12 (Dev Docs). Full model: § What it is.
**Check pattern:** rows, where present, occur in the order Related, [type], Design, Track, User Docs, Dev Docs; no row labeled `Anchor`.
**Why:** a stable left-to-top-to-bottom reading order makes every anchor page scan the same way; the row *names* the sub-area and the cell jumps you into it.

### RULE R-dispatch-table-08 — Related is the first optional row and absorbs external links (checked)
mend:: dispatch-rebuild
The first optional row is **Related**. It carries links to genuinely-related anchors / siblings **and external resources** — the code repo, the published project page, a docs site — i.e. anything related that is **not already in the breadcrumb path**. There is **no separate `External` row**; repo / site URLs live in **Related**. **An anchor that has a code repo (a `code:` key in its `.anchor`) carries a `[code](hook://f/{slug}?facet=code)` link in Related** — the hook `f/` (finder) verb opens the anchor's code folder in Finder (`{slug}` = the anchor's slug). Optional and never manufactured (per R-05).
**Check pattern:** no masthead row is labeled `External`; if a `Related` row exists it precedes every sub-area row.
**Why:** "what else is near this?" is answered once, up top, before the reader descends into the anchor's own contents; one row for all not-in-breadcrumb links keeps the switchboard small.

### RULE R-dispatch-table-14 — Code anchors carry a `[code]` link in Related (checked)
mend:: dispatch-rebuild
Every anchor whose `.anchor` declares a `code:` key (equivalently, carries the `code` trait) includes, in its **Related** row, a markdown link **`[code](hook://f/{slug}?facet=code)`** where `{slug}` is the anchor's slug. The `f/` (finder) hook verb opens the anchor's code folder; one-click reach from the masthead to the code, with no hardcoded path. The link text is exactly `code`.
**Check pattern:** for every dispatch-table page whose anchor has a `code:` key, the Related row contains a `[code](hook://f/<slug>?facet=code)` link.
**Why:** the code is the point of a code anchor; a uniform, path-free `[code]` link makes it reachable from every such masthead and stays correct even if the repo moves (resolution is via the `.anchor` `code:` key, not a hardcoded path).

### RULE R-dispatch-table-09 — Design row links the sub-anchor and enumerates the design parts (checked)
check:: dispatch_area_row Design
mend:: dispatch-rebuild
When the anchor has a Design sub-area, the masthead carries a **Design** row whose **left cell is `[[{X} Design\|Design]]`** (a link down to the design sub-anchor) and whose **right cell lists the design's key parts** that exist — PRD, Architecture, Decisions, UX Design, Roadmap, Stories. It is **never a bare self-link** (`| Design | [[{X} Design]] |` with nothing else is wrong).
**Check pattern:** a row whose left cell links to `{X} Design` and whose right cell holds ≥1 design-part link, whenever a `{X} Design` folder exists.
**Why:** the design row is the entry into the design flow; surfacing its parts gives one-click reach to the architecture and the rest without opening the sub-page first.

### RULE R-dispatch-table-10 — Track row links the sub-anchor and enumerates the tracking items (checked)
check:: dispatch_area_row Track
mend:: dispatch-rebuild
When the anchor **owns its tracking**, the masthead carries a **Track** row: **left cell `[[{X} Track\|Track]]`**, **right cell the key tracking items** that exist — Backlog, Features, Roadmap, Now. Absent when tracking is unified at a parent (per [[DAS Track]] § Who owns a Track folder).
**Check pattern:** a row whose left cell links to `{X} Track` and whose right cell holds ≥1 tracking-item link, whenever the anchor owns a `{X} Track` folder.
**Why:** the track row is the direct line to the backlog and in-flight work; surfacing the items makes the anchor's status reachable in one click.

### RULE R-dispatch-table-11 — User-docs row is labeled "User Docs" (checked)
mend:: dispatch-rebuild
When the anchor has user-facing docs, the masthead carries a row **labeled `User Docs`** — never bare `User`. Left cell `[[{X} User Docs\|User Docs]]` (or `[[{X} User\|User Docs]]` where the folder is `{X} User`); right cell the user docs (Guide, …).
**Check pattern:** no masthead row is labeled bare `User`; the user-docs row's display text is `User Docs`.
**Why:** the bare word "User" reads as a person/role; "User Docs" names the artifact and keeps the four doc-area rows (Design / Track / User Docs / Dev Docs) parallel.

### RULE R-dispatch-table-12 — Dev-docs row is labeled "Dev Docs" (checked)
mend:: dispatch-rebuild
When the anchor has developer docs, the masthead carries a row **labeled `Dev Docs`** — never bare `Dev`. Left cell `[[{X} Dev Docs\|Dev Docs]]` (or `[[{X} Dev\|Dev Docs]]` where the folder is `{X} Dev`); right cell the dev docs (Files, …).
**Check pattern:** no masthead row is labeled bare `Dev`; the dev-docs row's display text is `Dev Docs`.
**Why:** parallel to R-11 — "Dev Docs" names the artifact, not a stage, and keeps the doc-area rows uniform.

### RULE R-dispatch-table-02 — Anything enumerable drops to the Member zone (stated)
Members, sub-items, and worked examples are **not** masthead rows — they live in the Member zone below, on [[Collection]] anchors.
**Why:** the masthead stays small and fixed; enumerable content grows and belongs in the auditable member zone.

### RULE R-dispatch-table-03 — Cell wiki-links escape the pipe (checked)
mend:: dispatch-escape-pipe
Inside table cells, aliased wiki-links escape the pipe: `[[Target\|Display]]`.
**Check pattern:** no unescaped `[[Target|Display]]` appears inside a table row.
**Why:** an unescaped pipe ends the table cell, breaking the row.

### RULE R-dispatch-table-04 — No breadcrumb-redundant links (checked)
mend:: dispatch-rebuild
No masthead row may link to an anchor that already appears in the **breadcrumb path**. The parent / up-edge lives **only** in the breadcrumb; re-linking it (in any sub-area row, the Related row, or anywhere) is forbidden — every anchor is trivially related to its parent, so the link adds nothing. (The sub-area rows therefore carry **down-edges only** — the anchor's own contents — never its parent catalog.)
**Check pattern:** no wiki-link target in a non-breadcrumb row matches any anchor in the breadcrumb chain.
**Why:** redundant — the breadcrumb already carries the up-edge directly above; the duplicate link only clutters the switchboard.

### RULE R-dispatch-table-05 — Related is optional; never manufactured (stated)
The **Related** row may be **empty or omitted**. List only *genuinely* related siblings/material plus any one-off links the user deliberately pinned. Do **not** invent a relation to fill the row — when nothing is truly related, the correct Related row is no row (or an empty one).
**Why:** a forced relation is noise; an honest empty is information. The table is a switchboard, not a quota to fill.

### RULE R-dispatch-table-06 — Pure link table; minimal annotation (checked)
check:: dispatch_cell_narrative
mend:: dispatch-cell-narrative
A dispatch table is the **distilled set of jump-destinations**, not an explanation of them. No meta-discussion of what a link *means* belongs in a cell. **Ideally none at all**; where a modifier is genuinely load-bearing, **at most two words in a row** — parentheses optional. A link's meaning belongs on the linked page itself — its top line (H1 + first sentence) and its `description` frontmatter — not in the table that points at it. Dan, 2026-08-22, on the cap: *"ideally 0 words. But if modifiers are critical, you can add them, but it can't be more than two words."* Restated later the same day, declining the adaptive-tuning path ([[TINK594 - Escalated Prevention Rules, declared target rates, empirically tuned enforcement|F594]]) for this rule: *"I was happy to just have a hard rule that says you can't write a spine that has more than 2 words in a row in it … it's just gonna be harsh on that point at this stage."* The cap is a flat word-run count, not a prose heuristic and not parenthesis-gated.
**A left cell that is a wiki-link is exempt — the right cell is that child's description.** A child pulled above the separator by hand ([[Disk]]'s 10T / 8T / BLACK rows, 2026-08-29) keeps the shape the machine gives it below `---`: link left, one-sentence description right. That sentence is *expected*, and the checker (`masthead_narrative_offenders`) skips any row whose left cell carries a wiki-link before counting words. The cap applies to **label** rows — `Related`, `Docs`, `Status` — where prose in the right cell explains a link that should explain itself on its own page. Dan: *"it's totally legal for there to be a sentence there. It's expected."*

**Left vs right cell — asymmetric.** The **left cell** is the row's *label* (row name, group name, sub-area name) — describing the row itself is fine there. The **right cell** is nearly pure links; the 1–2-word cap applies to the right cell. Narrative belongs on the destination page, never the right cell.
**Check pattern:** every right cell of the doc's own masthead, after the identity row and the GFM header separator, up to (not including) the first electric-marker row — replace every wiki-link, markdown link, and code span with a run-breaking separator; any remaining fragment carrying three or more words → fail. A ≤2-word tag passes with or without parentheses; punctuation neither counts nor breaks a run.

**Code spans are pointers, not prose, and are stripped before the test.** A `Ground truth` row naming `~/ob/kmr/.obsidian/` and the files under it says *where this page's facts live* — it is a jump-destination that happens to have no wiki-link, not an explanation of one. Dan blessed exactly that row on [[OBS Setup]] 2026-08-22 — *"spiritually the ground truth section here is good"* — in the same breath as rejecting the prose row beside it, so a checker that failed both would be enforcing against a standing ruling. **22 cells vault-wide** are code-span-only, and clearing them dropped the failing-doc count from 370 to 361.
**Why:** the table's value is the distilled essence of *where you can jump*; prose about each destination dilutes that and duplicates what the destination already says about itself.
**Suspended to `warn` 2026-08-29 (Dan, [[TINK623 - R-dispatch-table-06 six days on 434 of 1,604 mastheads (27%) violate|TINK T623]]), and [[R-dispatch-guard]]'s four denies return early.** Six days of `fail` + deny measured 434 of 1,604 mastheads violating, and on the worst offenders — the [[SV Proj]] fact cards, the `@` person summaries — the prose is the page's *own substance*, which the cap would destroy because the page has no heart to receive it. Dan: *"it's definitely gonna destroy content if we just leave it in place."* The path back is the spine→heart migration ([[DAS heart]] § Fact card): once a page's own facts live below the H1, its spine can be links-only and the cap re-arms without loss.

**Ships `fail` since 2026-08-22 — the flip is the experiment, and Dan called it: *"let's just change the rule so that you cannot write a table with more than 2 words … let's just see what happens when the system is forced to do that."***

**Since the same day this rule also has a hard-DENY twin, [[R-dispatch-guard]]** — the `tool:pre:Write`/`tool:pre:Edit` (and best-effort `tool:pre:Bash`) veto that refuses, before the bytes land, any write that emits or changes a spine carrying an offending cell — legacy cells included; touch means clean, and only body-only Edits pass on a dirty doc. It shares this rule's exact checker core (`masthead_narrative_offenders`) and its exception escape. This doc-rule remains the post-write surface: it names the law, sweeps the legacy corpus, and catches what the pre-hook cannot see.

It shipped `warn` from 2026-08-14, on this ruleset's own precedent for -07/-08: displaced narrative needs a judgment call about where it lands, which is not a safe automatic repair, and a fail nobody can act on cheaply is the audit-noise trap. **That reasoning deadlocked.** `execute_on_write` surfaces only `fail` — the same fact [[R-spine]]'s `_spine_rule` records against itself — so an advisory rule is invisible at the one moment it could have been obeyed for free, and the corpus it was waiting on could never clean. Eight days of `warn` changed nothing because no agent was ever told.

**The corpus, measured the day of the flip.** The 2026-08-14 note read *3 of 5 on a hand sample*; the full sweep is **1,374 hand-typed prose cells across 370 of the vault's 1,028 masthead docs** — 36%, and `kmr.md` alone contributes six. Only **2** cells vault-wide were the target's own `description:` echoed back by desc sync, so "the machine does it too" is not a defence; it is a curiosity confined to one page.

**A fail with no `fix::` is deliberate here.** The on-write path emits the message and leaves the repair to the agent, which is what -06's MEND is written for — moving the prose to the destination's own head or this doc's `## Overview` is a judgment call, and a fixer that guessed would silently destroy writing. The escape is the exception table ([[R-exception-discipline]], grades `A`–`C` suppress both `fail` and `warn`); -11's rubric is what makes an exception hard to earn here, since the honest answer to *"what would I do instead, and how bad is that?"* is **move the sentence into the target's `description:` frontmatter**, a ten-second edit that is plainly not worse.

### RULE R-dispatch-table-07 — Every dispatch table ends with a catch-all marker (checked)
mend:: dispatch-rebuild
Every dispatch table **ends with a catch-all auto-enumeration zone**, so no document sitting in the folder can be hidden from the table: **`...`** (compact — the default; one cell that surfaces anything uncovered) or **`| --- | |`** (full auto-list — each uncovered/new doc as its own row, for list containers). The other HA v2 electric separators also satisfy the rule where their ordering fits the content: **`^^^`** (reverse-alpha auto-list — dated/newest-first containers like Features folders) and **`+++`** (alpha with grandchildren). Applies to **every** dispatch table, not just list containers — a masthead gets `...` too, so a stray doc dropped in the anchor's folder still shows.
**Check pattern:** the table's final row is `...`, `| --- | |`, a trailing `+`-group row, or an electric separator (`---`/`^^^`/`+++`) followed only by its auto-emitted member rows.
**Why:** the dispatch table must be an honest index of its folder — a catch-all guarantees stray or newly-added docs surface instead of silently disappearing.
**Scope of "uncovered" — the whole page, prose included.** The catch-all surfaces children not linked **anywhere on the page**, not merely those absent from the rows above. A child named in the page's intro paragraph is already surfaced by that sentence, so the catch-all omits it and the rule's purpose is still met. Its absence from `...` is **correct**, not a defect — see R-dispatch-table-13.

### RULE R-dispatch-table-13 — Electric zones are machine-owned; hand edits are discarded (stated)
mend:: dispatch-rebuild
Everything **below** a separator marker (`...`, `| --- | |`, `+++`, `^^^`, `!!!`) is an **electric zone**: recomputed from the command store on every rebuild, ~30 s after the page stops changing. Rows **above** the separator belong to the author; rows **below** belong to the machine. **Anything typed into an electric zone is discarded** — not merged, not flagged, silently overwritten. This covers hand-***repair*** as much as hand-***authoring***: re-adding a link you believe is missing is the same violation as writing a row from scratch. To change what a zone shows, change the *source* — the file's location, its command, or a row above the separator.
**Why:** the failure this prevents is not cosmetic. A hand-added link appears to work, then vanishes ~30 s later with nothing running and no explanation, which reads exactly like corruption — it produced **three separate wrong bug reports from three different agents** (a Warden bug, an Obsidian stale-buffer bug, a daemon-cache bug) before anyone read the filter. Confirmed correct behaviour by the user, 2026-08-05. Duplicated at `~/ob/kmr/CLAUDE.md` so every vault agent loads it. Implementation: HookAnchor F081 body-mention suppression, which logs each omission (`DISPATCH catchall on '<anchor>': N child(ren) omitted`) so an absent child is explainable.

### RULE R-dispatch-table-15 — Masthead link case is cosmetic, never a failure (checked)
check:: dispatch_link_case_drift
A masthead link whose target exists under a **different case** — `[[Tink Track|Track]]` where the folder is `TINK Track/` — is reported at **warn**, never at fail. Every masthead matcher resolves case-insensitively, the way Obsidian and APFS both already do.
**Check pattern:** for each wiki-link in the doc's own masthead table, a sibling or child whose name matches case-insensitively but not exactly.
**Why:** Obsidian resolves a link's **filename** case-insensitively through its own index, so all 98 of these vault-wide (across ~40 anchors — [[SLUG]] 22, [[TINK]] 9, [[ASG]] 7) route a reader correctly and none is broken. Matching case-sensitively produced phantom *"row is missing"* findings, which is the half of [[TINK Backlog#^T422|T422]]'s misleading-message defect that T136 did not reach. The drift is still **listed** rather than dropped because case-insensitivity is Obsidian's behaviour, not the filesystem's and not every consumer's: GitHub's renderer, this vault's own checkers, and any external tool resolve exactly. Keeping the population enumerated is what keeps a canonical-spelling sweep available without re-deriving it. Note that the tolerance **stops at the `#`** — headings and block references are matched exactly, so the far larger population of `[[X Backlog#^T151|T151]]` links has none of this slack. Ruled by the agent 2026-08-08 ([[TINK Backlog#^T410-Q1|T138 Q1]] → A).

### RULE R-dispatch-table-16 — Every hand-row link resolves (checked)
check:: dispatch_hand_link_resolves
A wiki-link in a row **above** the separator names a file that exists somewhere in the vault — Obsidian's rule, basename anywhere. Reported at **warn**: the fix is an author's (write the page, or drop the row), and there is no mechanical repair.
**Check pattern:** walk the masthead after the identity row and the GFM separator, stop at the first electric marker, and resolve every `[[…]]` (alias, heading and block-id stripped) against the file names and `.md` stems under the ancestor anchor roots and the corpus root. A bare name resolves against stems, a name with an extension against file names.
**Why:** the electric zone can never hold a dead link — it is recomputed from the command store — and it can never *remove* one above the separator either, because those rows are the author's. That asymmetry is invisible from the page, and it produced a real question (Dan, 2026-08-28, on [[HBR Components]]: *"if those are dead links and that electric section is computed automatically, why didn't it remove them?"*): six links to component pages that were never written sat in hand rows for weeks, and nothing said so. Filed as [[TINK Backlog#^T615|T615]]. **Measured on arming, 2026-08-28:** 7,947 masthead pages, **138 carry a dead hand-row link, 369 links in all** — `SYS.md` 9, `SVAI.md` 8, most of them `{slug} User` / `{slug} Dev` / `{slug} Docs` rows scaffolded for pages never written. A four-second vault sweep; warn is the right tier until that number is small.

## Mend

Remediation messages for these rules — what to actually do when one fires. Reached as `warden mend R-dispatch-table-<nn>`; wired by the `mend::` line on each rule.

### MEND dispatch-rebuild

Do not hand-author the table. Run the builder:

```sh
python3 ~/.claude/skills/audit/scripts/audit-dispatch.py "<anchor path>"          # dry run, shows the proposed table
python3 ~/.claude/skills/audit/scripts/audit-dispatch.py "<anchor path>" --fix    # write it back
```

It builds the masthead in the fixed row order, emits the sub-area rows the anchor actually has, and preserves the load-bearing `→ ` prefix on the identity cell — a prefix that is easy to lose by hand and whose absence makes `ha` delete the breadcrumb outright.

Two things the builder will not do for you, by design:

- **It never drops a curated link.** A row pointing at a file you deleted survives every rebuild, because the builder cannot tell a stale row from one you pinned deliberately. Delete a dangling row yourself, then rebuild.
- **It will not invent a Related row.** An honest empty Related is information; a manufactured relation is noise.

If a rebuild leaves the rule still firing, the problem is in the folder, not the table — most often a duplicate basename forcing path-qualified links, or a member doc missing the file the row wants to point at.

For the grammar, read [[DAS Dispatch Table]].

### MEND dispatch-escape-pipe

Escape the pipe inside the wiki-link: write `[[Target\|Display]]`, not `[[Target|Display]]`.

An unescaped pipe ends the table cell, so the row silently loses everything after it — the link still looks right in the source and the table is broken in the render. This is the one dispatch-table defect worth fixing by hand, since it is a single character and the builder would only reproduce whatever it read.

For the grammar, read [[DAS Dispatch Table]].

### MEND dispatch-cell-narrative

Cut the prose out of the right cell; leave only the link(s) and, if you really want one, a ≤2-word tag (parens optional — `(historical)`, `archived`). Never more than two words in a row: links and code spans break a run, punctuation does not.

Where the prose goes depends on what it says: if it explains what the destination page *is*, it belongs on that page's own head (the H1 + orientation line, or its `description` frontmatter); if it's a fact about the anchor as a whole (provenance, a decision, a historical note), it belongs in this doc's own `## Overview` or a dedicated section — check first whether it is already said there, since a page that grew a narrative dispatch row usually already has the fuller version written out somewhere below the table.

Custom rows outside the canonical Related / Design / Track / User Docs / Dev Docs order (a `Successor` row, an `Archive` row, and the like) are not exempt — if all that survives after trimming is a bare label with nothing to link, delete the row rather than leaving an empty one.

For the grammar, read [[DAS Dispatch Table]].
