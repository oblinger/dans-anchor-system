---
description: marker file for the anchor folder
---
# FCT Folder

Facet spec for the anchor folder itself — the named directory containing a marker file that identifies it as an anchor.

**Location:** `{NAME}/   (the anchor folder itself)`


Every anchor is a folder. The folder name follows the conventions of its parent anchor (e.g., PP children get a year prefix like `2026 My Project/`).

**Working example:** `~/.claude/skills/CAE/` — CAE/ itself is a canonical anchor folder.

Below is a condensed reference example. See the working example linked above for the real file.

# Reference Example
---

```
CAE example/
└── CAE example.md        ← marker file
```

Contents of `CAE example.md`:

```markdown
(See Anchor [[CAE]])
```

Because the slug "CAE" differs from the folder name "CAE example", the marker file redirects to the anchor page `CAE.md`.

---



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

When the marker IS the anchor page (folder name = anchor name), the F060 top-of-doc format applies — see [[FCT Anchor Page]] § Format. When the marker is a redirect stub (`(See Anchor [[slug]])`), F060 doesn't apply — the stub is a one-line marker, not a documentation page.

# BRIEF

- **This is the facet spec for the anchor folder itself** — the rule that every anchor is a named directory containing a marker file. Edits here change what counts as a valid anchor folder vault-wide.
- **NOT the place for marker-file content rules** — the marker may also be the anchor page; that format is owned by [[FCT Anchor Page]]. Cite, don't re-specify.
- **Inclusion test for content here:** does it describe the folder-and-marker contract (folder naming, marker presence, slug-vs-folder-name redirect)? If so, here. If it's about what goes INSIDE the anchor page, it belongs in [[FCT Anchor Page]] instead.
- **Two marker shapes are load-bearing** — (1) folder name == anchor name → marker IS the anchor page (F060 applies); (2) folder name != slug → marker is a one-line `(See [[slug]])` redirect stub (F060 does NOT apply). Don't collapse this distinction.
- **Parent-anchor naming conventions cascade** — e.g. PP children carry a year prefix. Keep the example generic; don't enumerate every parent-trait's naming rule here (those live in the parent trait's spec).
- **Working example is canonical** — `~/.claude/skills/CAE/` is the live reference. If the contract changes, update the working example, not just this spec.
