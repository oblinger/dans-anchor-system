---
description: "the anchor folder facet — the named directory + marker file that makes an anchor"
---

# DAS Folder
Facet spec for the anchor folder itself — the named directory containing a marker file that identifies it as an anchor.

| -[[DAS Folder]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets]] → [DAS Folder](hook://p/DAS%20Folder) |
| --- | --- |
| Related | [[DAS Anchor Page]],  [[DAS Dot Anchor]],  [[DAS Aspects]],  [[DAS Facet]],   |
| Rules | [[R-fct-folder]],   |
| Examples | [[HBR\|marker-is-anchor-page example]],  [[HBR\|richer anchor with sub-anchors]],   |

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

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body above; the anchor-page format is owned by [[DAS Anchor Page]].)*

- **Inclusion test** — the folder-and-marker contract (folder naming, marker presence, slug-vs-folder-name redirect) belongs here; anything about what goes INSIDE the anchor page belongs in [[DAS Anchor Page]] — cite, don't re-specify.
- **Don't collapse the two marker shapes** — page-marker (F060 applies) vs one-line redirect stub (F060 does not) is a load-bearing distinction.
- **Keep the naming example generic** — don't enumerate per-parent-trait naming rules here (they live in each parent trait's spec).
- **Working example is canonical** — if the contract changes, update `~/.claude/skills/CAE/`, not just this spec.
