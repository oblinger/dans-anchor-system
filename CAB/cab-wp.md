# WP — Create a Work Product

Create a new dated work product folder inside `{RID} WP/`. Work products are polished outputs of human+agent collaboration — papers, reports, analyses, presentations, spreadsheets.

## Usage

```
/cab wp <name>
```

Example: `/cab wp IP Side Work Analysis`

## Steps

### 1. Detect anchor

Read `.anchor/config.yaml` to get RID.

### 2. Gather information — MANDATORY, DO NOT SKIP

**You MUST ask the user these questions before proceeding.** Do not assume defaults. Do not skip.

1. **Name** — what is this work product called?
2. **Description** — brief description of what this work product covers
3. **Type** — what kind of deliverable? Ask: "What type of document? (markdown, paper, report, slides, spreadsheet)"

Wait for the user's answers before creating anything.

### 3. Create WP folder if it doesn't exist

If `{RID} WP/` doesn't exist at the anchor root:
- Create the folder
- Create the dispatch page `{RID} WP/{RID} WP.md`:

```markdown
---
description: work products
---

# {RID} WP

| -[[{RID} WP]]- >: | +> |
| --- |
```

- Add a **Work** row to the anchor page dispatch table (after standard rows):
  ```
  | Work | [[{RID} WP\|WP]] |
  ```

### 4. Create the work product folder

- Generate today's date: `YYYY-MM-DD`
- Create folder: `{RID} WP/{date} {name}/`
- If folder already exists, append a letter suffix: `{date} {name} b/`

### 5. Create the anchor file

Every WP gets an anchor file that describes it and links to its deliverables. This file IS the dated file:

`{RID} WP/{date} {name}/{date} {name}.md`:

```markdown
---
description: {description}
type: {type}
---

# {date} {name}

{user's description goes here}

| -[[{date} {name}]]- | +> |
| --- | --- |
| [[{date} {name}/{document-name}\|{document-name}]] | {type} |
```

The dispatch table uses a **relative path** wiki-link to the deliverable file: `[[{date} {name}/{document-name}\|{document-name}]]`. This ensures the link resolves correctly even if the document name isn't globally unique.

### 6. Create the deliverable file

Based on type:

| Type | File created | Contents |
|------|-------------|----------|
| **markdown** | `{name}.md` (no date prefix) | Empty with H1 title |
| **paper** | `{name}.md` | Template: Abstract, Introduction, sections |
| **report** | `{name}.md` | Template: Summary, Findings table, Recommendations |
| **slides** | Note in anchor: "Create via `/io slides`" | Link to Google Slides or .pptx |
| **spreadsheet** | Note in anchor: "Create via `/io sheets`" | Link to Google Sheet |

For markdown/paper/report, create the file directly. For slides/spreadsheet, add a note in the anchor file directing the user to create via the appropriate IO skill.

### 7. Update the WP dispatch page

Add a row to `{RID} WP/{RID} WP.md` (newest first):

```
| [[{date} {name}]] |
```

### 8. Glance the anchor file — MANDATORY

Open the WP anchor file so the user can see it:

```bash
open "{path to anchor file}"
```

This is the dated file (e.g., `2026-03-29 IP Side Work Analysis.md`). The user must see the result of the creation. Do not skip this step.

### 9. Return the path

Print the path to the deliverable file so the agent can open or write to it.

## Notes

- WP folder is created on first use — not pre-created with the anchor
- The anchor file (dated) always exists — it describes the WP and links to deliverables
- The deliverable file has a clean name without date prefix (the folder provides date context)
- Always use relative-path wiki-links from the anchor file to the deliverable: `[[{date} {name}/{document-name}\|display]]`
- WP is distinct from Outputs (agent-generated) and Log (informal notes)
