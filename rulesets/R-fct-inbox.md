# RULESET R-fct-inbox
include:: [[R-stream]] 
where:: `file:{anchor}/**/* Inbox.md, !**/DAS *.md`
description:: Rules every `{slug} Inbox.md` instance must satisfy — location, heading format, and status-tag vocabulary.

**This ruleset reached no document from its creation until 2026-08-08, and it took two independent defects to make that true.** First, **no umbrella included it** — not [[R-anchor]], not [[R-facet]], not [[R-doc]] — so it was never loaded at all. Second, and still fatal once that was fixed, its selector read `` where:: `file: **/{slug} Inbox.md` ``: the Inbox lives inside the `{slug} Track/` sub-anchor, whose own `.anchor` declares no `slug:`, so `{slug}` fell back to the folder name and the pattern hunted for `HA Track Inbox.md` — a file that cannot exist. It now uses the idiom its working siblings [[R-fct-outputs]] and [[R-log]] use, `` file:{anchor}/**/* Inbox.md ``, and is included by [[R-anchor]] beside them.

Both were found by measurement, not by reading: the audit was run against a live `HA Inbox.md`, `R-stream-01`/`-03` appeared in the verdicts and no `R-fct-inbox-*` rule did — first before the umbrella fix, then again after it, which is what exposed the second defect hiding behind the first. Re-verified across five anchors (SVW, LRN TPM, MED, KM, OBU): all four rules now reach. **Fixing only the umbrella would have looked like a fix and changed nothing** — the recurring shape catalogued as folder-shaped facet rulesets selecting nothing.

**Rules -01 through -03 said "(checked)" and carried no `check::` field**, so they were agent judgment wearing a checker's label. They now say "(stated)", which is what they are. Writing the three checkers is filed separately — the label is corrected first, because a rule that overstates its own enforcement is worse than one that admits it has none.

### RULE R-fct-inbox-01 — File exists inside the Track folder (stated)
The Inbox file lives inside the Track folder: `{slug} Track/{slug} Inbox.md`, alongside the other tracking surfaces.
**Check pattern:** file is present at `<anchor-root>/{slug} Track/{slug} Inbox.md`.
**Why:** co-location with the other tracking surfaces in `{slug} Track/` ensures consistent discoverability by agents and users. (Tier: stated)

### RULE R-fct-inbox-02 — Sections are reverse-chronological H2s; the status tag marks a processed entry (stated)
Each entry heading follows the form `## YYYY-MM-DD — {Topic}`. A **processed** entry additionally carries a backtick-wrapped `{STATUS}` tag from the sanctioned set. A **pending** entry carries no tag, and that absence is what pending means — it is the state every drop writes, and the state `Inbox N` counts.
**Check pattern:** every H2 matches `^## \d{4}-\d{2}-\d{2} — .+`; a tag, where present, sits on the heading and is backtick-wrapped. Tag *absence* is never a finding.
**Why:** consistent heading format lets agents scan for processed vs. pending entries without parsing free-form prose — which requires the two states to be distinguishable, so exactly one of them carries a tag. (Tier: stated)

**Amended 2026-08-08.** As written this rule required a tag on **every** H2, which made every pending entry a violation the moment the drop API shipped, and contradicted `-04` in this same ruleset — `-04` says processed entries "only gain a status tag", which presupposes an untagged prior state `-02` forbade. It also contradicted the implementation: `count_pending_inbox` in `audit-q.py` defines pending as the absence of a tag, and the `Inbox N` banner counts exactly those. Three sources against one, and the one was never enforced ([[TINK Backlog#^T131|T131]]).

### RULE R-fct-inbox-03 — Only sanctioned status tags are used (stated)
The only permitted status values are `DONE` (processed in place) and `MOVED → {destination}` (content relocated). No other tags may be used without updating this spec.
**Check pattern:** no H2 carries a status tag other than `DONE` or `MOVED → …`.
**Why:** downstream tooling and agent skills key off these exact strings; ad-hoc tags silently break detection. (Tier: stated)

### RULE R-fct-inbox-04 — Processed entries are retained, not deleted (stated)
After processing, entries remain in the file with their status tag intact as a permanent log of what was communicated and where it went.
**Check pattern:** no H2 entry disappears upon processing; entries only gain a status tag.
**Why:** the Inbox doubles as an audit trail; deleting processed entries destroys the history of what input arrived and where it was routed. (Tier: stated)

## Position in the catalog

Sits under [[R-anchor]], beside [[R-fct-outputs]] and [[R-wp]] — the Inbox is an anchor-scoped tracking surface, so the anchor umbrella is what must reach it. Inherits [[R-stream]] for the dated-entry ordering rules, which is how `R-stream-01` reaches an Inbox file today.

## See also

- [[DAS Inbox]] — the facet this ruleset enforces.
- [[ATT045 - Agent inbox pattern|ATT F045]] — the design.
- [[TINK Backlog#^T131|T131]] — the drop API, the `Inbox N` banner, and the `/inbox` drain.
