# md-file-tree — File Tree Diagrams

File tree diagrams using Unicode box-drawing characters. The standard approach is a monospace page where the tree is plain text with wiki-links inline.



## 1. MONOSPACE FILE TREE  (Default for whole-file file trees)

See these real examples:
- [[CAB All Files]] — the CAB master file tree with links to every part spec
- [[MUX Files]] — a real project file tree with `→` doc association links


The document uses `cssclasses: monospace` in its YAML frontmatter, rendering the entire page in fixed-width font. The tree is plain text with regular spaces for alignment. Wiki-links work inline because text is not inside code spans or code blocks.

Key properties:
- **Plain text** — no backtick spans, no HTML, no tables
- **Regular spaces** — monospace rendering makes them fixed-width; no figure spaces needed
- **Links work inline** — wiki-links and URL links render normally
- **Descriptions aligned** — at a consistent display column using spaces
- **Display-width alignment** — wiki-links like `[[CAB Claude|CLAUDE.md]]` collapse to `CLAUDE.md` when rendered; padding must account for the shorter display width

Use Python to compute alignment when adding or modifying tree lines, since display width differs from raw width when wiki-links are present.


### Box-Drawing Characters

Four characters form the tree structure:
- `├` (U+251C) — branch with more siblings below
- `└` (U+2514) — last branch at a level
- `│` (U+2502) — vertical continuation line
- `─` (U+2500) — horizontal connector

Entry pattern: connector + `──` + space + name. For nested items, prefix with `│` + spaces per nesting level.

Indentation: 3 regular spaces per nesting level (on monospace pages). Blank lines use `│` for vertical continuation between logical groups.



## 2. INLINE TABLE-BASED FILE TREE  (Default inline file tree format)

A markdown file-tree table with two columns.

| Structure              | Description     |
| ---------------------- | --------------- |
| [[MyProject]]/         | project root    |
| `├──` [[MyProject.md]] | identity file   |
| `├──`  [[src]]/        | source code     |
| `│ .  └──`  [[lib]]/   | library modules |
| `└──` [[docs]]/        | documentation   |


## 3. BRAILLE-BASED FILE TREE

Extended example with wiki-links and descriptions:

⡧⠤ [[empty|Cargo.toml]]					Workspace root config
⡧⠤ [[empty|CLAUDE.md]]					Claude Code configuration
⡧⠤ [[empty|justfile]]							Build, test, forge recipes
⡇
⡧⠤ core/								Domain logic crate
⡇⠀⡧⠤ [[empty|lib.rs]]							Crate root, module exports
⡇⠀⡧⠤ [[empty|command.rs]]				Command enum — typed interface
⡇⠀⡧⠤ [[empty|sys.rs]]						Runtime — command dispatch engine
⡇⠀⡧⠤ types/						Type definitions
⡇⠀⡇⠀⡧⠤ [[empty|config.rs]]				Settings and project config
⡇⠀⡇⠀⠦⠤ [[empty|session.rs]]			Session and window types
⡇⠀⠦⠤ layout/						Layout subsystem
⡇⠀⠀⠀⡧⠤ [[empty|capture.rs]]			End-to-end capture pipeline
⡇⠀⠀⠀⠦⠤ [[empty|snapshot.rs]]			Tree from pane geometry
⡧⠤ cli/									CLI client crate
⡇⠀⡧⠤ [[empty|main.rs]]						Entry point, argument parsing
⡇⠀⠦⠤ [[empty|client.rs]]					Socket client — sends to daemon
⠦⠤ [[empty|README.md]]					Project documentation

Indentation: one `⠀` (Braille blank) per nesting level, placed after the vertical continuation `⡇`.



For proportional-font pages where monospace isn't available. Uses Unicode Braille characters (U+2800 block), which are guaranteed uniform width across all 256 codepoints — including the blank.

Four characters form the tree structure:
- `⡧` (U+2867) — branch with more siblings below (tee)
- `⠦` (U+2826) — last branch at a level (corner)
- `⡇` (U+2847) — vertical continuation line
- `⠀` (U+2800) — blank spacer (same width as all other Braille characters)

No horizontal connector needed — the tee/corner character is followed directly by a regular space and the filename.

Key rules:
- **All-Braille structure** — never mix Braille with box-drawing or other Unicode blocks; widths won't match
- **Braille blank for indentation** — use `⠀` (U+2800), not regular spaces, for nesting depth
- **Regular space before filenames** — the transition from Braille structure to text uses a regular space
- **Links work inline** — wiki-links render normally since text is not in code spans
- **Edit tool safe** — Claude Code's Edit tool reads and writes Braille characters without corruption



## 4. LARGE TABLE FILE TREE
Table-based file tree using H3 rows for larger, more scannable display. Wiki-links work inside table cells.

|                                                                               |                                   |
| ----------------------------------------------------------------------------- | --------------------------------- |
| <span style="font-size:1.5em"><code>├─</code></span> [[empty\|Cargo.toml]]    | Workspace root config             |
| <span style="font-size:1.5em"><code>├─</code></span> [[empty\|CLAUDE.md]]     | Claude Code configuration         |
| <span style="font-size:1.5em"><code>├─</code></span> [[empty\|justfile]]      | Build, test, forge recipes        |
| <span style="font-size:1.5em"><code>├─</code></span> core/                    | Domain logic crate                |
| <span style="font-size:1.5em"><code>│⠀ ├─</code></span> [[empty\|lib.rs]]     | Crate root, module exports        |
| <span style="font-size:1.5em"><code>│⠀⠀├─</code></span> [[empty\|command.rs]] | Command enum — typed interface    |
| <span style="font-size:1.5em"><code>│⠀⠀└─</code></span> [[empty\|sys.rs]]     | Runtime — command dispatch engine |
| <span style="font-size:1.5em"><code>└─</code></span> [[empty\|README.md]]     | Project documentation             |

Construction notes:

- **Two-column table** — first column is tree structure + filename, second column is description
- **Tree characters in a span** — `<span style="font-size:1.5em"><code>├─</code></span>` wraps only the box-drawing characters. The span enlarges them; the code tag makes them monospace
- **Short connectors** — use `├─` and `└─` (single horizontal), not `├──` (double). Keeps lines compact
- **Wiki-links outside the span** — links go after the closing `</span>`, not inside `<code>`. Markdown links don't render inside HTML tags
- **Nesting with Braille blanks** — indent nested lines inside the `<code>` using `⠀` (U+2800) between `│` and `├`/`└`. Two Braille blanks per nesting level
- **Vertical continuation** — `│` stays inside the `<code>` span so it renders monospace and enlarged, matching the branch characters
- **Pipe escaping** — wiki-links in table cells need escaped pipes: `[[empty\|filename]]` not `[[empty|filename]]`
- **No header row text** — use empty header cells (`| | |`) so the table has no visible header




# LEGACY FILE TREE FORMATS

These older forms embed monospace formatting per-line. They work in documents that are NOT whole-page monospace, but are more complex to maintain. Links must go outside the code spans since markdown formatting doesn't render inside backticks.


## Form 1: Large Inline

Each line has the tree portion in an HTML span with larger font. The right side is plain markdown.

<span style="font-size:1.3em"><code>MyProject/             </code></span> **Project** — project root
<span style="font-size:1.3em"><code>├── MyProject.md       </code></span> **Anchor** — identity file
<span style="font-size:1.3em"><code>├── src/               </code></span> **Source** — source code
<span style="font-size:1.3em"><code>│     └── lib/           </code></span> library modules
<span style="font-size:1.3em"><code>└── docs/              </code></span> **Docs** — documentation


## Form 2: Inline

Same structure at normal size. Each line is a backtick span followed by a description.

`MyProject/             ` **Project** — project root
`├── MyProject.md       ` **Anchor** — identity file
`├── src/               ` **Source** — source code
`│   └── lib/           ` library modules
`└── docs/              ` **Docs** — documentation



### Legacy Form Notes

- **Figure spaces (U+2007)** — Forms 1–3 need figure spaces for indentation because regular spaces collapse in markdown. Not needed on monospace pages.
- **Edit tool limitation** — Claude Code's Edit tool cannot distinguish figure spaces from regular spaces. Edits to lines containing figure spaces require Python string replacement via Bash.
- **Producing figure spaces** — Insert with Python: `fig = '\u2007'`; verify with `xxd` (byte sequence `e2 80 87`).
