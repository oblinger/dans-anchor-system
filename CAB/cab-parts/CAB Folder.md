# CAB Folder

Every anchor is a folder. The folder name follows the conventions of its parent anchor (e.g., PP children get a year prefix like `2026 My Project/`).

Below is a reference example for a hypothetical project "TSK" (Task Runner).

# Reference Example
---

```
Task Runner/
└── Task Runner.md        ← marker file
```

Contents of `Task Runner.md`:

```markdown
(See Anchor [[TSK]])
```

Because the RID "TSK" differs from the folder name "Task Runner", the marker file redirects to the anchor page `TSK.md`.

---



The folder must contain a **marker file** — a markdown file whose name matches the folder exactly:

```
My Project/
└── My Project.md        ← anchor marker
```

If the anchor has a RID that differs from the folder name, the marker redirects:

```markdown
(See [[RID]])
```

If the folder name IS the anchor name, the marker file also serves as the primary anchor page.
