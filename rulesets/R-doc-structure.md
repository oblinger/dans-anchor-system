# RULESET R-doc-structure
include::
import:: skills/audit/scripts/audit-plan.py
where:: always
description:: the canonical document layering — progressive disclosure for a document. Scope: every authored document — any `.md` the system owns, identified by a leading `# ` H1 (the checkers skip H1-less files as out of scope).

Embedded ruleset for the Doc Structure facet. One compact ordering rule; per-element rules can be split out later if finer-grained auditing is wanted.

### RULE R-doc-structure-01 — Canonical top-to-bottom order (checked)
check:: doc_top_order
fix:: breadcrumb_position

A document's top is laid out in this fixed order — each element optional unless noted, none out of sequence:

**[breadcrumb] → H1 → summary line → [central figure] → [top table] → [TLDR] → [Overview] → body (→ bottom `# BRIEF`)**

Embedded constraints:
- **Breadcrumb (non-anchor docs only):** a non-anchor page with no dispatch table opens with a `:>>` breadcrumb line directly above the H1 (no blank line between). An anchor page's breadcrumb lives in its dispatch-table masthead instead — never both.
- **H1 (required):** `# {slug} - {Name}` for an anchor page, `# {Name}` otherwise; optionally suffixed ` — {phrase}`.
- **Summary line:** one sentence on the line **immediately after the H1, with no blank line between** — UNLESS the H1 already carries the ` — {phrase}` (one or the other carries the "what this is", not both).
- **Central figure:** optional; if present, sits before the table.
- **Top table (the document table):** governed by two independent rules — `R-doc-structure-02` (dispatch table iff anchor) and `R-doc-structure-03` (TOC table iff long); placed before the first body section. See those rules for the must / must-not conditions.
- **TLDR, then Overview:** optional, in that order, after the table and before the body.

**Check pattern:** line 1 matches `^# `; the line immediately after the H1 is non-blank (the summary) OR the H1 contains ` — `; the document table, when present, sits before the first body `^## `; no element appears out of the order above. (Table presence itself is checked by `R-doc-structure-02` / `-03`.)

**Why:** progressive disclosure — each layer down serves a more-committed reader, and a fixed order means a glance-reader and the audit both know exactly where to look.

### RULE R-doc-structure-02 — Dispatch table iff the document is an anchor (checked)
check:: dispatch_table_iff_anchor

The breadcrumb-masthead **dispatch table** appears on a document **if and only if** that document is an anchor (its file is the `{slug}.md` / anchor file of an anchor folder, marked by a sibling `.anchor` or by being the folder's namesake page).

- **Anchor document → MUST carry a dispatch table** (per [[DAS Dispatch Table]] / [[DAS Anchor Page]]).
- **Non-anchor document → MUST NOT carry a dispatch table.** User-story files, feature docs, individual design docs, and plain content pages are not anchors; a breadcrumb masthead on them is a violation. Parent / sibling back-links belong in a `## Related` or `## See also` section instead.

**Check pattern:** detect a dispatch masthead by `^\| -\[\[.+\]\]- \|` as the first table row. Assert it is present when the file is an anchor file and absent otherwise. Anchor-ness: the file is named `{folder} .md` matching its enclosing folder **and that folder carries a `.anchor` marker**, or a sibling `.anchor` declares the file's stem as its slug. A namesake alone proves nothing since F329 (2026-08-15): the folder-doc form — `X/X.md`, e.g. a folder-form `{slug} Backlog/` or a feature doc grown into a folder — is a *document* in folder form, keeps its `:>>` breadcrumb, and must not be asked for a masthead. Nor does a sibling `.anchor` alone settle it: HookAnchor's scanner auto-mints `.anchor` in every namesake folder on its 10-minute rescan (observed 2026-08-15, re-mint 2 minutes after deletion), so a namesake whose file carries the machine `<!-- state:backlog -->` stamp is a folder-form backlog — never an anchor page — whatever marker sits beside it. (Whether the scanner should skip these folders is HA's open policy question.)

**Why:** the dispatch table is the *anchor* navigation surface — breadcrumb up the tree plus the anchor's member links. On a non-anchor it is noise that falsely implies the document roots a subtree, and it pushes the real content below the fold. This is the rule that makes a story file with a masthead (e.g. a `US-<slug>-<N>` file) fail.

### RULE R-doc-structure-03 — TOC table iff the document is long (checked)
check:: toc_table_iff_long

A **table-of-contents table** (content-outline table — left column links the document's own `[[#Heading]]` sections, right column describes each in one line) appears **if and only if** the document runs more than roughly three pages of content.

- **Long document (more than ~3 pages) → MUST carry a TOC table.**
- **Short document (about 3 pages or fewer) → MUST NOT carry a TOC table** — it is navigation overhead for a document a reader can simply scroll.
- **Specialized exception:** a document may carry *another kind of table* at the top (a stories index, a status board, a glossary) that is neither a dispatch table nor a TOC table. Such content tables are permitted regardless of length and are not the subject of this rule.
- **Script-owned projections are exempt:** `Q.md` and `{slug} queries.md` are rewritten whole on every render, so a TOC would be erased on the next write and cannot be added by hand ([[R-pathguard]] denies the edit). The rule asks an author to help a reader navigate; a generated page has no author. Backlogs are not exempt — `state` edits rows in place, so a TOC survives there.
- **Append-only logs are exempt, on different grounds:** `{slug} Inbox.md` and `{slug} Messages.md`. The projection argument above does *not* apply to them — they are appended to rather than rewritten, so a hand-authored TOC would survive. They are exempt because the rule has nothing to bite on: an Inbox's content outline **is** its list of dated `##` entries, in the order they already appear, so a TOC would restate the document; a Messages log carries no headings at all, so its TOC would be empty. Added 2026-08-17 ([[TINK Backlog#^T545|TINK T545]]) after the advisory was measured firing on every `state` write to every Inbox and Messages file in the fleet — nine times in a single inbox drain, which is how a warning tier stops being read.

**Check pattern:** estimate length by content (heading count + body lines as a page proxy). If long, assert a content-outline table (in-document `[[#...]]` links) precedes the first body section. If short, assert no such TOC table is present. A specialized content table (neither dispatch masthead nor in-document-heading TOC) does not count either way.

**Why:** the TOC earns its space only when the document is too long to scan; on a short document it is friction. Tying presence to length keeps every document's top as light as it can be while still navigable.
