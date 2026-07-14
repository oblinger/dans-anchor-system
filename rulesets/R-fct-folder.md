# RULESET R-fct-folder
include::
where:: `file: **/.anchor`
description:: The rules every anchor folder must satisfy — a named directory containing a marker file whose name matches the folder exactly.

### RULE R-fct-folder-01 — Marker file exists and name matches folder (checked)
Every anchor folder contains a markdown file whose basename equals the folder's own name (e.g. `My Project/My Project.md`).
**Check pattern:** `{slug}/{slug}.md` exists inside the anchor root.
**Why:** the marker file is how any tool or human identifies a directory as an anchor; without it the folder is just a folder.

### RULE R-fct-folder-02 — Redirect stub is one-line only (checked)
When the marker file is a slug-redirect stub (folder name ≠ anchor name), the body is a single line `(See [[slug]])` with no additional content.
**Check pattern:** if the marker does not begin with `# `, its entire non-blank content is a single `(See [[…]])` line.
**Why:** a stub that grows content blurs the redirect form with the anchor-page form; the two shapes must remain distinct.

### RULE R-fct-folder-03 — Parent-anchor naming conventions are honored (sampled)
The folder name follows any naming convention imposed by its parent anchor (e.g., a PP child carries a `YYYY ` year prefix).
**Check pattern:** spot-check child anchors against their parent's declared naming pattern.
**Why:** naming conventions cascade so that a parent anchor can enumerate or group its children predictably.

### RULE R-fct-folder-04 — Anchor folder is the single root (checked)
There is exactly one root folder per anchor; sub-folders inside the anchor are not themselves anchor roots unless they carry their own independent marker.
**Check pattern:** only one `.anchor` or marker file at the root level of the anchor (nested anchors must have their own independent marker).
**Why:** a single unambiguous root prevents two-root anomalies where tools disagree on which folder is the anchor.
