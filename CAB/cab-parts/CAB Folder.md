# CAB Folder

Every anchor is a folder. The folder name follows the conventions of its parent anchor (e.g., PP children get a year prefix like `2026 My Project/`).

The folder must contain a **marker file** — a markdown file whose name matches the folder exactly:

```
My Project/
└── My Project.md        ← anchor marker
```

If the anchor has a TLC that differs from the folder name, the marker redirects:

```markdown
(See [[TLC]])
```

If the folder name IS the anchor name, the marker file also serves as the primary anchor page.
