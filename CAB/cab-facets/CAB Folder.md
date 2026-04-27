---
description: marker file for the anchor folder
---
# CAB Folder

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
