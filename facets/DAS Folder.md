---
description: "the anchor folder facet — the named directory + marker file that makes an anchor"
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Folder](hook://p/DAS%20Folder)
# FCT Folder
Facet spec for the anchor folder itself — the named directory containing a marker file that identifies it as an anchor.

**Related:** [[DAS Anchor Page]],  [[FCT Marker]],  [[CAB Aspects]],  [[DAS Facet]]
**Examples:** [[HBR\|marker-is-anchor-page example]],  [[HBR\|richer anchor with sub-anchors]]

**Location:** `{slug}/   (the anchor folder itself)`

**Cardinality: one** — every anchor has exactly one root folder; this facet applies once per anchor.

Every anchor is a folder. The folder name follows the conventions of its parent anchor (e.g., PP children get a year prefix like `2026 My Project/`); each parent's specific naming rule lives in that parent trait's spec, not here.

**Working example:** `~/.claude/skills/CAE/` — CAE/ itself is a canonical anchor folder.

The folder must contain a **marker file** — a markdown file whose name matches the folder exactly:

```
My Project/
└── My Project.md        ← anchor marker
```

If the anchor has a slug that differs from the folder name, the marker redirects:

```markdown
(See [[slug]])
```

If the folder name IS the anchor name, the marker file also serves as the primary anchor page.

## F060 — applies via Anchor Page

When the marker IS the anchor page (folder name = anchor name), the F060 top-of-doc format applies — see [[DAS Anchor Page]] § Format. When the marker is a redirect stub (`(See Anchor [[slug]])`), F060 doesn't apply — the stub is a one-line marker, not a documentation page.

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

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above; the anchor-page format is owned by [[DAS Anchor Page]].)*

- **Inclusion test** — the folder-and-marker contract (folder naming, marker presence, slug-vs-folder-name redirect) belongs here; anything about what goes INSIDE the anchor page belongs in [[DAS Anchor Page]] — cite, don't re-specify.
- **Don't collapse the two marker shapes** — page-marker (F060 applies) vs one-line redirect stub (F060 does not) is a load-bearing distinction.
- **Keep the naming example generic** — don't enumerate per-parent-trait naming rules here (they live in each parent trait's spec).
- **Working example is canonical** — if the contract changes, update `~/.claude/skills/CAE/`, not just this spec.
