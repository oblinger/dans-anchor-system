# cab-tidy — Validate and Correct Anchor Structure

Scan an anchor folder and fix structural issues against the CAB spec.

## Step 1: Find the Anchor

```bash
ha -p "{NAME}"
```

Read the anchor page and identify the anchor type. Then read the type spec from `CAB Types/` in the CAB folder (`ha -p CAB`).

## Step 2: Read Reference Specs

Read `CAB Base.md` for the base file tree and `CAB Parts/CAB All Files.md` for the full reference. Also read `CAB Rules/CAB Naming Conventions.md` for the {NAME} prefix rule.

## Step 3: Tidy Checklist

Execute each item:

### 3.1 Naming Compliance
- Every markdown file and folder prefixed with `{NAME}`
- Exceptions: CLAUDE.md, README.md, code files

### 3.2 Anchor Page Links
- All docs linked directly or indirectly from the anchor page
- Link table current and no broken links
- External links (repo, docs sites) still valid

### 3.3 Roadmap Content
- Roadmap contains only high-level milestone descriptions
- Detailed discussion → move to Notes or Design Discussions
- Detailed task lists → move to Todo

### 3.4 TLC Index Entry
If the anchor has a TLC:
- Verify it appears in the TLC index table
- Check date, link, full name, and description are correct

### 3.5 File Structure
- Marker file exists and matches folder name
- Docs folder structure matches the type spec
- No orphaned docs (files in Docs/ not linked from anywhere)

### 3.6 CLAUDE.md
- If agentic project, has pilot header
- Key files and commands sections are current

## Step 4: Report

Show the user what was found and fixed. List any issues that need manual attention.
