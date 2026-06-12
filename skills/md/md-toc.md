# md-toc — Tables of Contents

A format for generating indented tables of contents using figure spaces for alignment. Entries are numbered and linked.


## Form 1: Large TOC

Each line uses an HTML span for larger rendering of the spacing. Top-level entries sit at the left margin; sub-entries are indented with figure spaces.

**[1 Overview](#1-overview)** — system purpose and goals
**[2 Getting Started](#2-getting-started)** — installation and first launch
<span style="font-size:1.3em"><code>   </code></span> [2.1 Installation](#21-installation) — brew install, single binary
<span style="font-size:1.3em"><code>   </code></span> [2.2 First Launch](#22-first-launch) — GUI, CLI, config directory
**[3 Project Spec](#3-project-specification)** — anatomy of a project folder
<span style="font-size:1.3em"><code>   </code></span> [3.1 Anchor](#31-anchor) — identity file
<span style="font-size:1.3em"><code>   </code></span> [3.2 Roadmap](#33-roadmap) — milestones and tasks


## Form 2: Inline TOC

Same structure at normal size. Top-level at left margin, sub-entries indented.

**[1 Overview](#1-overview)** — system purpose and goals
**[2 Getting Started](#2-getting-started)** — installation and first launch
   [2.1 Installation](#21-installation) — brew install, single binary
   [2.2 First Launch](#22-first-launch) — GUI, CLI, config directory
**[3 Project Spec](#3-project-specification)** — anatomy of a project folder
   [3.1 Anchor](#31-anchor) — identity file
   [3.2 Roadmap](#33-roadmap) — milestones and tasks


## Form 3: Table TOC

A markdown table with indented, linked entries. Figure spaces provide indentation in the first column. The header row says "Table of Contents" — `md-toc.py` uses this to locate and replace the table.

| Table of Contents | |
|---|---|
| **[1 Overview](#1-overview)** | system purpose and goals |
| **[2 Getting Started](#2-getting-started)** | installation and first launch |
|    [2.1 Installation](#21-installation) | brew install, single binary |
|    [2.2 First Launch](#22-first-launch) | GUI, CLI, config directory |
| **[3 Project Spec](#3-project-specification)** | anatomy of a project folder |
|    [3.1 Anchor](#31-anchor) | identity file |
|    [3.2 Roadmap](#33-roadmap) | milestones and tasks |


## Rules

The purpose of a TOC is to provide a **navigable outline** of a document — every entry is a link.

1. **Top-level at left margin** — H1/H2-level entries have no indentation. They sit at the left edge and are bold.

2. **Indentation by level** — sub-entries are indented with figure spaces (U+2007) in a backtick span. Use 3 figure spaces per indent level. Top-level entries have no backtick span at all.

3. **Numbering** — optional but recommended. Dotted numbers (1, 1.1, 1.1.1) show hierarchy.

4. **Links** — every entry should be a clickable link (wiki-link, markdown anchor link, or URL). The TOC is a navigation tool.

5. **Descriptions** — optional. A brief phrase after an em-dash. Keep it short — the TOC should be scannable.

6. **Figure spaces (U+2007)** — regular spaces collapse; figure spaces do not.

7. **Blank lines around tables** — markdown tables require a blank line before them to render correctly.

8. **Edit tool limitation** — lines with figure spaces require Python string replacement via Bash.


## md-toc Script

Auto-generates a TOC from H2/H3 headings in Form 3 (Table) format with wiki-links.

```bash
md-toc.py <file.md>           # Replace existing TOC table in-place
md-toc.py <file.md> --dry-run # Print TOC to stdout
```

The script locates the first table whose header contains "Table of Contents" and replaces it. Extra columns (descriptions, notes) are preserved by matching on heading title. If no TOC table exists, it prints to stdout.

The script lives at `~/.claude/skills/md/md-toc.py`.
