# RULESET R-log
include:: [[R-stream]] 
import:: skills/audit/scripts/audit-plan.py
where:: `{anchor}/**/* Log.md, !**/DAS *.md`
exclusion-note:: `!**/DAS *.md` exempts the facet-spec catalog (a `DAS <Name>.md` is the SPEC for the facet, not an instance; specs are governed by [[R-facet-spec]]) — added 2026-07-13, T014 follow-on.
description:: Structural rules for the {slug} Log facet — folder shape, entry filename pattern, dispatch dispatch, content scope.

Ruleset for this facet — spec: [[DAS Log]] (extracted from the spec 2026-07-12). Armed by **both** executing umbrellas: [[R-doc]], which `/audit doc` and the on-write doc-fire resolve, and [[R-anchor]], which `/audit anchor` resolves. Being named by [[R-facet]] is catalog membership, not adoption — that umbrella sits outside the `R-doc`/`R-anchor` closure `audit-plan.py` resolves, so an `include::` there arms nothing ([[TINK Backlog#^T208|T208]]).

### RULE R-log-01 — Log path is `{slug} Log/` or `{slug} Log.md` (checked)
check:: log_path_exists
mend:: log-location

The log lives at `{slug}/{slug} Log/` (folder form) or `{slug}/{slug} Log.md` (single-file form). Not under Track, not under Docs, not at the vault root.

**Check pattern:** `ls "{anchor}/{slug} Log"` resolves to a directory or `.md` file; no other location qualifies.

**Why:** Logs are anchor-scoped peers of Backlog and Roadmap; location predictability matters for the agent's discoverability and for users browsing anchor folders.

### RULE R-log-02 — Folder-form has a `{slug} Log.md` dispatch file (checked)
check:: log_dispatch_file_present

When the log is folder-form, the folder contains a `{slug} Log.md` whose H1 is `# {slug} Log`.

**Check pattern:** if `{anchor}/{slug} Log/` is a directory, then `{anchor}/{slug} Log/{slug} Log.md` exists and starts with `# {slug} Log`.

**Why:** the dispatch file is the entry point — without it, the folder is a directory listing with no index.

### RULE R-log-03 — Entry filename is ISO-date-prefixed (sampled)
check:: log_entry_filenames

Go-forward naming is `YYYY-MM-DD — <topic>` (ISO date + em-dash + title), owned by [[DAS stream]] § Dated entry-file naming (Q1 → A, 2026-07-17). The check stays permissive so legacy space-separated names grandfather cleanly — every entry file (any extension) matches one of:
- `^\d{4}-\d{2}-\d{2} .+\.(md|docx|pptx|pdf|jpeg|jpg|png|txt)$` (full date; the leading space admits both the ` — ` em-dash form and legacy ` <topic>` space form)
- `^\d{4}-\d{2} .+\.(md|...)$` (year-month only, allowed when day unknown)
- `^\d{4} .+\.(md|...)$` (year only, allowed when month unknown)

**Check pattern:** enumerate non-dispatch files in the log folder; assert each matches one of the three patterns.

**Why:** ISO-date prefix forces chronological sort; descriptive topic suffix makes the file self-identifying without opening. Logs without dates become unbrowsable as they grow.

**This narrows [[R-stream]]-03 for the Log facet's shape; it does not restate it, and deleting it as a duplicate was refused on measurement 2026-08-08.** `R-stream-03` asserts that a method-3 entry file's H1 omits its date, and it only reaches the `YYYY-MM-DD — Title.md` em-dash form — of which the corpus has zero instances, so it passes on all 125 log entry files without evaluating anything. This rule asserts the different and load-bearing thing: that an entry **carries a date prefix at all**. It also admits what a Log actually holds and a `.md`-only rule cannot — eight extensions, sub-directories, and year-only or year-month dates for entries whose exact day is unknown. It finds 5 failing anchors today.

### RULE R-log-04 — Entries don't restate spec / convention content (stated)

Log entries describe what *happened* on the day. They do not contain spec definitions, conventions, rules, or standards that belong in their own facet docs (Conventions, Spec, Backlog, etc.).

**Check pattern:** manual review. Future: heuristic flag when an entry contains an H2 like `## Convention`, `## Spec`, `## Rules`, `## Format` — those headers usually indicate displaced spec content.

**Why:** specs evolve and need to be the single source of truth. If a Log entry restates a spec, the entry becomes silently stale when the spec changes.

### RULE R-log-05 — Dispatch table is newest-first (sampled)
check:: log_dispatch_newest_first

The `{slug} Log.md` dispatch table lists entries with the **newest entry at top**, working backwards in time.

**Check pattern:** parse dispatch-row wiki-links **above the separator** to extract dates from `[[YYYY-MM-DD ...]]`; assert monotonically non-increasing. Rows below the separator are the electric zone and are not judged.

**Why:** the reader's primary query is "what happened recently?" Reverse-chronological ordering puts the answer first; chronological ordering buries it.

**This applies [[R-stream]]-01's ordering invariant to a surface `R-stream-01` cannot see.** `R-stream-01` counts `## YYYY-MM-DD —` H2 headings *inside* a document; a folder-form log keeps its entries in separate files, so its dispatch page has no dated H2s and `R-stream-01` returns *"no dated entries found"* on every one of them. This rule reads the dispatch table's wiki-links instead. One rule orders the ledger, this one orders the index to it — deleting it as a duplicate was refused on that basis 2026-08-08.

**Scoped to hand-authored rows 2026-08-11 (T209, reported by CFO), and the measurement that forced it also tells you this rule is now nearly vacuous.** It had been judging the whole table, including the `...` catch-all — the electric zone HookAnchor recomputes in **alphabetical** order. So on any log whose entries are dated files, the generator and this rule disagreed *by construction*, and the finding named links no agent is permitted to reorder. It fired on every write to `FIN Log.md`, could not be cleared by anyone who saw it, and the correct response was to do nothing — which is indistinguishable from ignoring a real warning.

The earlier justification above used to cite *"finds 4 out-of-order dispatch tables today"* as proof the rule earned its place. **That count was measuring machine-owned rows.** Re-measured across all 98 log dispatch pages in the vault: 5 failed unscoped, and **all 5 had zero or one dated link above the separator** — not one was ever agent-fixable. After scoping, the rule judges **2 pages of 98** and finds nothing.

**Two of 98 is not coverage, and this rule should not be read as providing any.** The honest reading is that its real subject was always the electric zone, which means the ordering it exists to enforce can only be delivered by the generator: teaching the catch-all to sort date-prefixed children newest-first is the fix that makes the page actually read correctly, and it belongs to HookAnchor rather than here. Filed as [[TINK Backlog#^T209|T209]]. Scoping stops the false alarm; it does not achieve the rule's purpose, and retiring the rule outright is the right move if that generator change is declined.

### RULE R-log-06 — Dispatch table is append-only (stated)

Once a row is added to the dispatch table for an entry, it stays. Don't delete rows even if the entry was wrong. Supersession is noted *inside* the entry body, not by removing the row.

**Check pattern:** git history — entries that disappear from the dispatch table without the underlying file being moved are suspect.

**Why:** Logs are historical record. Deleted rows are revisionist; they make it impossible to reconstruct what was thought when.

### RULE R-log-07 — No `Brief` carrying log-format rules (checked)
check:: regex_absent ^#\s+BRIEF

The `{slug} Log.md` dispatch page does NOT contain a ` # BRIEF` second-H1 (or `Brief` sidecar file) that restates how Logs work. The rules for how Logs work live in this facet (CAB Log), not on every per-anchor Log dispatch page.

**Check pattern:** grep `{slug} Log.md` for `^# BRIEF` or `^# Brief`. If present and its body contains general log-format prescriptions (filename pattern, body convention, "don't duplicate spec content"), flag for migration to point at [[DAS Log]] instead.

**Why:** the Brief discipline is for anchor-specific operational content, not for restating shared facet rules. Per-anchor restatement of facet rules drifts when the facet evolves.

### RULE R-log-08 — Anchor page links to `[[{slug} Log]]` (sampled)
check:: log_anchor_page_link
mend:: log-dispatch

The anchor's main page (`{slug}.md`) carries a dispatch row pointing at `[[{slug} Log]]`.

**Check pattern:** grep `{anchor}/{slug}.md` for `\[\[{slug} Log\]\]`.

**Why:** without it, the Log is one click further from anchor-page-as-router; readers miss it.

### RULE R-log-09 — Sub-anchor logs are scoped to their sub-anchor (stated)

A sub-anchor with its own Log uses the sub-anchor's name (e.g., `MED Heart Log/`, `MED Heart Log.md`), not the parent's. Logs do not cross anchor boundaries.

**Check pattern:** for each `* Log.md` found, walk up to the nearest `.anchor` file; assert the log's `{slug}` prefix matches that anchor's name (or its slug).

**Why:** Logs are anchor-scoped. A sub-anchor entry inside a parent's log loses its scoping and is harder to find later.

## Mend

Remediation messages for these rules — what to actually do when one fires. Reached as `warden mend R-log-<nn>`; wired by the `mend::` line on each rule. State the fix, point at the facet, never restate it.

### MEND log-location

Put the log where the facet expects it, then re-run the write.

The log is `{slug} Log/` (a folder of dated entries) or `{slug} Log.md` (a single file) directly under the anchor root — never under `{slug} Track/`, never under a Docs folder, never at the vault root. Pick the folder form when entries are long enough to want their own files; the single-file form otherwise. Both are equally valid and you can convert later.

If the file is already written and merely misplaced, move it rather than creating a second one — two logs for one anchor is the failure this rule exists to prevent.

For the model and the entry-naming rules, read [[DAS Log]]. For a worked example, see `SKA Log/`.

### MEND log-dispatch

Add a dispatch row on the anchor page pointing at the log, then re-run the write.

The anchor page (`{slug}.md`) must carry `[[{slug} Log]]` in its masthead so the log is reachable from the anchor's front door. A log nothing links to is a log nobody reads.

Do not hand-author the masthead — run `/audit dispatch`, which builds the row in the correct fixed position. Hand-editing a dispatch table is its own class of error, and the identity cell has a load-bearing `→ ` prefix that is easy to lose.

For the table grammar, read [[DAS Dispatch Table]].
