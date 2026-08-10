---
description: "the anchor folder facet — the named directory + marker file that makes an anchor"
---

| -[[DAS Folder]]- | → [[DAS]] → [[FCT]] → [DAS Folder](hook://p/DAS%20Folder)  |
| --- | --- |
| Related | [[DAS Anchor Page]],  [[DAS Dot Anchor]],  [[DAS Aspects]],  [[DAS Facet]],   |
| Rules | [[R-fct-folder]],   |
| Examples | [[HBR\|marker-is-anchor-page example]],  [[HBR\|richer anchor with sub-anchors]],   |
| ... | [[anchor-page]],  [[DAS Agenda]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Backlog]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[facets/DAS Move]],  [[DAS Naming]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[facets/DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stone]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[facets/DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Folder
Facet spec for the anchor folder itself — the named directory containing a marker file that identifies it as an anchor.

**Location:** `{slug}/   (the anchor folder itself)`

**Cardinality: one** — every anchor has exactly one root folder; this facet applies once per anchor.

Every anchor is a folder. The folder name follows the conventions of its parent anchor (e.g., PP children get a year prefix like `2026 My Project/`); each parent's specific naming rule lives in that parent trait's spec, not here.

**Working example:** [[FEX Project Root]] — a canonical anchor folder root.

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
- **Working example is canonical** — if the contract changes, update [[FEX Project Root]], not just this spec.
