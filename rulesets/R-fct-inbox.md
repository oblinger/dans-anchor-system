# RULESET R-fct-inbox
include:: [[R-stream]]
where:: `file: **/{slug} Inbox.md`
description:: Rules every `{slug} Inbox.md` instance must satisfy — location, heading format, and status-tag vocabulary.

### RULE R-fct-inbox-01 — File exists inside the Track folder (checked)
The Inbox file lives inside the Track folder: `{slug} Track/{slug} Inbox.md`, alongside the other tracking surfaces.
**Check pattern:** file is present at `<anchor-root>/{slug} Track/{slug} Inbox.md`.
**Why:** co-location with the other tracking surfaces in `{slug} Track/` ensures consistent discoverability by agents and users. (Tier: checked)

### RULE R-fct-inbox-02 — Sections are reverse-chronological H2s with a status tag (checked)
Each entry heading follows the form `## YYYY-MM-DD — {Topic}` followed by a backtick-wrapped `{STATUS}` tag, where `{STATUS}` is one of the two sanctioned tags.
**Check pattern:** every H2 matches `^## \d{4}-\d{2}-\d{2} — .+` and carries a backtick-wrapped status tag.
**Why:** consistent heading format lets agents scan for processed vs. pending entries without parsing free-form prose. (Tier: checked)

### RULE R-fct-inbox-03 — Only sanctioned status tags are used (checked)
The only permitted status values are `DONE` (processed in place) and `MOVED → {destination}` (content relocated). No other tags may be used without updating this spec.
**Check pattern:** no H2 carries a status tag other than `DONE` or `MOVED → …`.
**Why:** downstream tooling and agent skills key off these exact strings; ad-hoc tags silently break detection. (Tier: checked)

### RULE R-fct-inbox-04 — Processed entries are retained, not deleted (stated)
After processing, entries remain in the file with their status tag intact as a permanent log of what was communicated and where it went.
**Check pattern:** no H2 entry disappears upon processing; entries only gain a status tag.
**Why:** the Inbox doubles as an audit trail; deleting processed entries destroys the history of what input arrived and where it was routed. (Tier: stated)
