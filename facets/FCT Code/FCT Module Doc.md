---
description: "per-module source code documentation — one doc per source module mirroring the repo tree"
---
# FCT Module Doc
Facet spec for per-module documentation — the auto-generatable, source-code-grounded reference doc that mirrors one source module under `{NAME} Dev/`.

| -[[FCT Module Doc]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Code]] → [FCT Module Doc](hook://p/FCT%20Module%20Doc)<br>: per-module source code documentation — one doc per source module mirroring the repo tree |
| --- | --- |
| Related | [[FCT Interface]],  [[FCT Architecture]],  [[FCT Dev]],  [[FCT Code]],   |
| Examples | [[CAE-Scheduler\|fuller (two-zone, SVG figure)]],  [[HBR Scanner\|minimal (leaf module)]],   |

**TLDR** — Each source module gets a `{NAME} {ModuleName}.md` doc under `{NAME} Dev/` mirroring the repo's folder structure. Docs have two zones: an Overview zone (SECTIONS table + per-class overview + figure) and a Class Method Details zone. SVG figures only (via `[[viz-excalidraw]]`); bold-identifier-outside-code-span for all table links; block-ID format `^ClassName-methodname`. **Cardinality: many** — one doc per source module.

**Location:** `{NAME} Docs/{NAME} Dev/{NAME} {ModuleName}.md` (one per module).

module docs describe the classes and interfaces in a software project's source code. Each source module (a file or logical grouping of files) gets its own markdown document. The docs mirror the source tree structure under `{NAME} Dev/`.

**Related:** [[FCT Interface]] — the required top-level human-authored layer contract that groups modules into a vocabulary callers above the layer use. A module doc is auto-generated ground-truth reference for one module in isolation; the Interface is the human-validated contract for the whole layer. Every `code`-trait anchor has one Interface and one module doc per source module.

**Working example:** `~/ob/kmr/SYS/Bespoke/Skill Agent/CAE/CAE Docs/CAE Dev/CAE Scheduler.md` — the canonical instance. Every rule below is demonstrated there. When in doubt, read the example.


# Format Specification

This spec was rewritten 2026-06-06 based on extended iteration on the CAE Scheduler example. The rules below supersede earlier 3-column / ALL-CAPS / per-class-prose conventions.


## Location — mirroring the source tree

module docs live under `{NAME} Dev/` in a subfolder structure that **mirrors the repository's source tree**. Every source directory that contains modules gets a parallel documentation directory.

```
Repository (source)                    Documentation (vault)
─────────────────                      ────────────────────
src/                                   {NAME} Docs/{NAME} Dev/
├── execution/                         ├── {NAME} execution/
│   ├── scheduler.py                   │   ├── {NAME} Scheduler.md
│   └── worker.py                      │   └── {NAME} Worker.md
├── agent/                             ├── {NAME} agent/
│   ├── session.py                     │   ├── {NAME} Session.md
│   └── trace.py                       │   └── {NAME} Trace.md
└── infra/                             └── {NAME} infra/
    └── entity.py                          └── {NAME} Entity.md
```

### Mirroring rules

- Every source directory gets a parallel `{NAME} {dir}/` folder in Dev.
- Every source file with public API gets a `{NAME} {ClassName}.md` doc.
- The doc file is named after the **primary class** in the source file, not the filename.
- All files and folders carry the `{NAME}` prefix to avoid Obsidian namespace collisions.
- Each doc subfolder can have a `{NAME} {dir}.md` dispatch page listing its module docs.


## Document structure

A module doc has two zones:

- **Overview zone** at the top — frontmatter, breadcrumb, H1+brief, SECTIONS table, one per-class overview section per class. Every per-class section has the prose description + the class table. **No method-body prose in this zone.**
- **Class Method Details zone** at the bottom under a `# Class Method Details` H1 — per-class deep-dive H2 sections, each containing class-level concept H3s (design discussions) and per-method H3s (Args / Returns / Raises bodies).

The overview zone is everything a reader needs to see the API surface at a glance. The details zone is where they jump when they want the per-method specifics.


### Top of doc

```markdown
---
description: <one-line module summary>
---
:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Code]] → [FCT Module Doc](hook://p/FCT%20Module%20Doc)

# {NAME} {ModuleName}
<file-level overview paragraph — no blank line after H1, description prose immediately follows>
```

Rules:

- YAML frontmatter with `description:` field. Optional — present when the module doc carries machine-readable metadata.
- Breadcrumb line in the `:>>` form pointing back through the anchor hierarchy.
- H1 = `# {NAME} {ModuleName}` where `{NAME}` is the anchor prefix and `{ModuleName}` matches the file name.
- **No blank line between the H1 and the file overview prose** — text starts on the next line. This is the compact-H2/H1 rule applied to the file H1.
- One paragraph (2-4 sentences) immediately after the H1. Describes the module's purpose, role in the system, and any cross-references to rules / standards documents.


### Figure (between overview prose and SECTIONS table)

Every major module doc carries a **figure** at the top — a single diagram that gives the reader the gist of the whole document in one glance. Position: after the file overview paragraph, before the SECTIONS table.

The figure's job is to show **how the sections fit together as a whole**:

- Each named section (class / topic / enum) appears as a node, labeled with its name and type.
- Edges show data flow, call sequences, or composition relationships between sections.
- Key data structures the document discusses (queues, caches, pools, registries) appear as their own nodes.
- Topics that govern a structural relationship (e.g. a queue's ordering rule) are highlighted via styling or annotation so the reader sees which topic anchors which structural feature.

**Format: SVG always. Mermaid is forbidden. ASCII art in code fences is forbidden.** Figures are SVG files co-located with the module doc (`{NAME} {ModuleName}.svg` next to `{NAME} {ModuleName}.md`), referenced via Obsidian wiki-embed syntax: `![[{NAME} {ModuleName}.svg]]`.

Why SVG only:

- **Renders identically in every Markdown viewer** — Obsidian, GitHub, VS Code preview, browsers. Mermaid only renders in environments with a mermaid plugin; ASCII art breaks the moment a font changes width.
- **Editable as a real diagram** — opens in Excalidraw / ExcalidrawZ, Figma, Inkscape, or any vector editor; text remains text (selectable, searchable).
- **Stable across format iterations** — when the SECTIONS table conventions change again, mermaid figures rot because their syntax mixes with the docs convention. SVG stays valid as a graphic.

### Authoring workflow — use `[[viz-excalidraw]]`

**Do NOT hand-code the SVG.** Hand-coded SVG is hard to edit, gets messy at scale, and loses the structured semantics that real diagram tools preserve.

The canonical authoring workflow is the `[[viz-excalidraw]]` sub-skill of `[[viz]]` (file at `~/.claude/skills/viz/viz-excalidraw.md`, with reference examples at `~/.claude/skills/viz/excalidraw-examples.md`):

1. **Create / edit** a `.excalidraw` JSON file co-located with the module doc: `{NAME} {ModuleName}.excalidraw`.
2. **Convert to SVG** via the viz skill's converter: `python3 ~/.claude/skills/viz/excalidraw_to_svg.py "/path/to/file.excalidraw"`. Produces `.svg` and `.png` alongside the source file (~200 ms).
3. **Embed in markdown**: `![[{NAME} {ModuleName}.svg]]` (wiki-embed, not markdown image syntax — Obsidian resolves the wiki-link by basename and renders the SVG inline).
4. **Open in ExcalidrawZ** so the user can edit interactively: `open -a ExcalidrawZ "/path/to/file.excalidraw"`.

**Every time the `.excalidraw` source changes, you MUST re-run the SVG conversion** (the embedded image won't update otherwise). Both files are committed to the vault — `.excalidraw` is the source-of-truth (editable), `.svg` is the derived artifact (rendered).

When an agent is authoring or revising a figure, it MUST read `[[viz-excalidraw]]` and the linked examples before writing the JSON — every element requires a specific set of properties or ExcalidrawZ silently fails. The viz skill owns those details.

Reference (canonical example from `CAE Scheduler.md`):

```markdown
![[CAE Scheduler.svg]]

*Priority and starvation* is the topic that governs the queue's ordering rule (deadline + aging promotion).
```

### Size and aspect ratio

- **HARD RULE — figures span the full width of the page.** When rendered in Obsidian, the SVG fills the available column width. Author the `.excalidraw` content area wide enough that the natural rendered scale fills the column (typically ~1400-1600 px wide source). If a figure renders smaller than column width, explicitly set width via `![[file.svg|1200]]` or re-author the source wider. Tiny figures break the "one-glance gist of the whole document" purpose of the convention.
- **GUIDELINE — prefer landscape aspect ratio** (wider than tall). Module-doc diagrams tend to have lateral data flow; landscape matches that shape and renders cleanly inline. This is a preference, not a hard rule — a figure that's genuinely portrait-shaped (a deep call stack, a vertical pipeline) should stay portrait. The hard rule is full-page-width; the layout direction is the agent's choice if portrait reads better.


### Layout guidelines (not hard rules)

Construction patterns that produce readable figures. Each is a guideline — break it when the alternative reads worse.

- **Avoid crisscrossing lines.** When two arrows cross, the reader pauses to disambiguate which line goes where. Lay out nodes so that the primary data-flow arrows can route without intersection.
- **One acceptable crossing is OK** — a single load-bearing arrow (e.g. the `enqueue` arrow from `TaskScheduler` to `PriorityQueue` going up-right while the `returns` arrow goes horizontally to `TaskHandle`) can cross other lines without hurting readability. The rule is "minimize crossings," not "zero crossings."
- **Push secondary nodes off the primary flow path.** If two nodes need a clean direct arrow between them (e.g. `Caller → TaskHandle` for `await_result()`), move other nodes out from between them. In the CAE Scheduler figure, this is why `Worker pool` lives far-right — pulling it out of the middle keeps the `TaskScheduler → TaskHandle` and `Caller → TaskHandle` paths unobstructed.
- **Keep text out of lines.** Position arrow labels above, below, or beside the arrow with clearance — never on top of the line. Where an arrow is diagonal, rotating the label to align with the line (Excalidraw `angle` property in radians) sometimes reads better than a horizontal label crossing the line. Same rule for node-name and node-description text: leave breathing room around boxes so labels from other arrows don't intrude.
- **Short labels beat long ones.** If "submit(task, deadline)" wraps awkwardly or runs into other elements, drop it to just `submit` — the table below the figure carries the full signature; the label only needs to identify which arrow is which.
- **Legend goes where it stays out of the way.** Bottom of the figure is the default — it doesn't compete with the data-flow nodes. Top is acceptable when the data flow is bottom-heavy (a vertical pipeline that fills the lower portion). The rule is "out of the way," not a fixed position.
- **Solid arrows for primary flow; dotted arrows for derivation / reference / data carriage** (returns, carries, enqueue-as-side-effect). The convention helps the reader scan the main path vs the supporting relationships.

Rules:

- **Label each section node with its type** in parentheses or as a sub-label: `TaskScheduler (class)`, `TaskState (enum)`. Matches the SECTIONS-table type-naming rule.
- **Show data structures the doc discusses** even when they aren't sections — e.g. `PriorityQueue` is a data structure governed by the `Priority and starvation` topic but isn't its own SECTIONS entry. Including it makes the structural relationship visible.
- **Topics often appear as edge labels or annotations**, not as nodes — topics describe *rules*, not *things*. If a topic governs a structural feature (the PriorityQueue's ordering, in the example), annotate the affected node and cite the topic in a one-line caption below the figure.
- **One-line caption below the figure** is allowed — italicized — to call out which topic anchors which structural element. Example: *Priority and starvation is the topic that governs the queue's ordering rule (deadline + aging promotion).*
- **Keep it readable** — 5-15 nodes is the sweet spot. If the diagram is too dense, split into two figures (one per zone of concern). If it's too sparse, drop it (the SECTIONS table already covers low-density modules).
- **Solid arrows** for the primary data/control flow; **dotted arrows** for secondary relationships (returns, enqueue/dequeue, contains, derives-from). Convention helps the reader scan.


### SECTIONS table

After the file overview, a 2-column SECTIONS table indexes the classes (and any other sections) the document covers.

```markdown
| SECTIONS                                                   | Role                                                            |
| ---------------------------------------------------------- | --------------------------------------------------------------- |
| [[#^TaskScheduler\|TaskScheduler]] class                   | Priority queue engine that orchestrates deferred task execution |
| [[#^PriorityAndStarvation\|Priority and starvation]] topic | Aging-promotion rule that prevents low-priority tasks from being permanently delayed |
| [[#^TaskHandle\|TaskHandle]] class                         | Async result handle returned by `submit()`                      |
| [[#^TaskState\|TaskState]] enum                            | Lifecycle states for a task                                     |
| [[#^SchedulerStatus\|SchedulerStatus]] class               | Immutable snapshot of the scheduler's current state             |
```

Rules:

- **Header is `SECTIONS` not `CLASSES`** — sections most often are classes, but sometimes a module has non-class sections (a topic, a Protocol block, a configuration record, an enum group). The neutral term covers both.
- **Column 1 is a wiki-link to the section's block-ID followed by the section type** — `[[#^anchor\|Name]] type`. The type appears lowercase outside the link (`class`, `topic`, `enum`, `struct`, `protocol`, `record`, etc.). The type word is what tells the reader at a glance whether the section documents an API surface or a conceptual rule.
- **Column 2 is the section's role** — a one-line orientation telling the reader what they'll find. Short.
- Class / enum / struct names in PascalCase (matches source code identifiers); topic names in sentence case (they're concepts, not code identifiers).


### Section H2 indicates the type — only when there IS a type

**The H2 title indicates what KIND of thing the section documents — if there's a code type** (Class, Enum, Struct, Protocol, Interface, Trait, Record). If the section is a topic (a concept, a design rule, a cross-cutting invariant — not an API surface), the H2 carries no type qualifier; it's just the name of the thing.

Code-typed sections (Class / Enum / Struct / etc.) — the type qualifier appears in three places:

- **SECTIONS row link alias + trailing lowercase type word**: `[[#^TaskScheduler\|TaskScheduler]] class`.
- **Overview-zone H2**: `## TaskScheduler Class` (Type capitalized).
- **Class table header (first column)**: `TASK SCHEDULER CLASS` (ALL CAPS with spaces; type word appended ALL CAPS too).

Non-code sections (topics, conceptual rules, cross-cutting invariants) — bare names, no qualifier anywhere:

- **SECTIONS row link alias, no trailing word**: `[[#^PriorityAndStarvation\|Priority and starvation]]`.
- **Overview-zone H2**: `## Priority and starvation`.
- **No class table** — topics use a bulleted concept-label list instead (see § Topic section below).

Type vocabulary (used only when applicable):

- **Class** — object type with fields and methods. Most common.
- **Enum** — sum type with variants (e.g., TaskState).
- **Struct** — plain data record without behavior (sometimes used instead of class for immutable data; pick by language convention).
- **Protocol** / **Interface** / **Trait** — abstract API contract.
- **Record** — alternative for plain-data when struct doesn't fit (e.g. Python dataclass).

If none of these apply, the section documents a concept rather than an API surface. Don't say "Topic" in the H2 — just give it its name. Pick the language-idiomatic word when there IS a type; consistency within one anchor matters more than across anchors.

**Audit detection rule:** if the H2's last word is one of `{Class, Enum, Struct, Protocol, Interface, Trait, Record}`, treat as code-typed (expect class-table form); otherwise treat as a topic (expect bulleted concept-list form). No "Topic" sentinel word.


### Topic section

A **topic** is a top-level non-code section in the overview zone. It documents a concept that's important enough to deserve prominent placement at the same level as classes — typically a design rule, an invariant, or a cross-cutting behavior — but isn't an API surface.

**Topics do NOT require a table.** Class sections need tables because they enumerate identifiers (fields and methods). Topic sections enumerate concepts, and concepts are usually fine as a **bulleted description list** with bold concept-labels. Use a table only when the topic genuinely has tabular structure (e.g. a state-transition matrix). The default shape is the bullet list — it's cleaner and signals "this is conceptual content, not an API table."

Canonical shape (the default — bullet list):

```markdown


## Priority and starvation
<one or two sentences naming what the rule is, why it exists, and what it gates>^PriorityAndStarvation

- **Concept one** — One-sentence explanation.
- **Concept two** — One-sentence explanation.
- **Concept three** — One-sentence explanation.
- **Rule reference** — [[CAE Decisions#D07 — One Queue, One Clock (checked)\|D07]] is the canonical rule that anchors this topic.
```

Rules:

- **Topic block-IDs use PascalCase** with spaces removed: `^PriorityAndStarvation`, `^ThreadPoolSizing`. Stable identifier despite the multi-word topic name.
- **Bullet items use bold concept-labels** followed by an em-dash and a one-sentence explanation: `- **Aging promotion** — Tasks waiting longer than 2× cycles get promoted.` The bold makes labels scannable; the prose carries the substance.
- **Topics frequently reference rules** — when a topic anchors a design rule documented in `{NAME} Rules.md` or elsewhere, include a `**Rule reference**` bullet pointing at the canonical rule. This keeps the topic discoverable from the rule and vice versa.
- **Topics live in the overview zone alongside classes** — they don't have a corresponding section in the Class Method Details zone (no methods to detail). If a topic is large enough to need expansion, add H3 subsections directly after its bullet list, before the next top-level H2.
- **Sentence case for topic names**: "Priority and starvation", not "Priority And Starvation". Topics are concepts, not code identifiers.
- **Use a table instead of a bullet list ONLY when the content genuinely has tabular shape** — e.g. a state-transition table, a decision matrix, side-by-side comparisons. Otherwise default to the bullet list.


### Per-class overview section

Each class gets a section in the overview zone consisting of an H2 + description + class table. The detail prose (method bodies, design discussions) goes in the Class Method Details zone at the bottom, not here.

```markdown


## TaskScheduler
Priority queue engine that orchestrates deferred task execution. Owns the worker pool, the queue, and the retry policy — callers submit, get a handle back, and either await or cancel. Single instance per process; all timed work flows through it.^TaskScheduler

| TaskScheduler                                                                                | Description                            |
| -------------------------------------------------------------------------------------------- | -------------------------------------- |
| **`queue`**`: PriorityQueue`                                                                 | Pending tasks ordered by deadline      |
| **`pool_size`**`: int`                                                                       | Number of worker threads               |
| **Methods**                                                                                  |                                        |
| **[[#^TaskScheduler-submit\|submit]]**`(task: Callable, deadline: datetime) -> TaskHandle`   | Enqueue a task with a deadline         |
| **[[#^TaskScheduler-cancel\|cancel]]**`(handle: TaskHandle) -> bool`                         | Cancel a pending task by handle        |
```

Rules for the H2:

- **Two blank lines before each H2** (visual separator between same-level sections). Updated 2026-06-06 — was 3 lines; 2 is sufficient.
- **No blank line after the H2** — class description prose starts on the next line immediately.
- Class description = one paragraph (2-4 sentences) explaining what the class IS, its role, ownership, and any constraints (single-instance, thread-safe, etc.).
- **Block-ID is appended inline at the end of the description**, with no space: `...all timed work flows through it.^TaskScheduler`. This is what the SECTIONS table links to.

Rules for the class table:

- **2 columns: class name | description**. The TABLE HEADER ROW carries the class identification — first cell is the class name (Title Case / PascalCase, matching source code), second cell is `Description` (literal header word OR the class summary repeated; in current style the header word stays as the literal `Description`).
- **Fields listed first**, then a bold-only `**Methods**` divider row (column 2 empty), then methods.
- **Bold only the identifier** in each row, not the whole signature: `**\`queue\`**\`: PriorityQueue\`` renders as a bold name + plain monospace type. Same for methods: `**\`submit\`**\`(task: Callable, deadline: datetime) -> TaskHandle\``.
- **Field rows are NOT wiki-linked** — fields have no per-row detail to jump to.
- **Method rows ARE wiki-linked** — the link goes to the method's detail H3 in the Class Method Details zone. **CRITICAL — backticks inside wiki-link aliases do NOT render.** The correct shape is: bold wraps the link, the alias is the plain method name (NO backticks inside), the tail is a separate code span. Form: `**[[#^TaskScheduler-submit\|submit]]**\`(task: Callable, deadline: datetime) -> TaskHandle\``. This renders as a bold-linked name flowing into a monospace tail. Putting backticks inside the alias (e.g. `[[#^anchor\|**\`name\`**]]`) makes Obsidian display the literal text including the asterisks and backticks — broken render.
- **Enum variants follow the same 2-column shape** — variant name in the first column with its parameters (e.g. `**\`Pending\`**\`(deadline: datetime)\``), description in the second. No `**Methods**` divider needed for enums.
- **No blank line between H2 / description / table** in the overview zone — this entire per-class block is one tight cluster. The 3-blank-lines rule provides the visual separation between clusters.


### Class Method Details zone

After the last per-class overview section, the deep-dive content lives under a `# Class Method Details` H1.

```markdown



# Class Method Details



## TaskScheduler

### Priority and starvation
<design-discussion prose>

### Retry semantics
<design-discussion prose>

### `submit(task: Callable, deadline: datetime) -> TaskHandle` ^TaskScheduler-submit
<args / returns / raises body>

### `cancel(handle: TaskHandle) -> bool` ^TaskScheduler-cancel
<body>
```

Rules:

- **Two H1s in the document** — `# {NAME} {ModuleName}` at the top, `# Class Method Details` introducing the details zone. Markdown allows this; Obsidian renders both.
- **H1 `# Class Method Details`** acts as a disambiguation parent for the H2 class headings (which repeat names from the overview zone). Wiki-links from the overview-zone class tables target block-IDs in this zone, NOT raw heading text, so the H2-name collision between overview-zone H2 and details-zone H2 is harmless (block-IDs are unique).
- **Per-class H2** — same name as the overview H2 (e.g. `## TaskScheduler`). The H2 itself doesn't need a block-ID — the per-method H3s underneath carry the block-IDs targeted by the overview-table method links.
- **H3 per class-level concept first** (Priority and starvation, Retry semantics, Thread pool sizing, etc.) — these are the design / invariant / behavior discussions that don't belong to a single method.
- **H3 per method second**, in declaration order. Each method H3 is the **full signature in a code span** with the block-ID inline at end: `### \`submit(task: Callable, deadline: datetime) -> TaskHandle\` ^TaskScheduler-submit`.
- **Method block-ID format: `^ClassName-methodname`** — class-prefixed to avoid collisions across classes (e.g. `^TaskHandle-await_result` vs `^TaskScheduler-submit`). Underscores in method names are preserved in the block-ID.
- **Method H3 body — merged bullet form** (per 2026-06-06 format iteration). One brief paragraph describes the method, then an italic `*Args:*` heading followed by a single bullet list that carries args, returns, and raises together. Bold the identifiers (arg names, return type, raised exception types) — these are what the reader scans for. Italic the section labels (`*Returns:*`, `*Raises:*`) on their bullets so they're visible but recede.
   - Canonical example:
     ```markdown
     ### `submit(task: Callable, deadline: datetime) -> TaskHandle` ^TaskScheduler-submit
     Enqueue a task for execution at or after `deadline`.

     *Args:*
     - **`task`**: A callable with no arguments. Side effects are the caller's responsibility.
     - **`deadline`**: Earliest time the task should run. The scheduler may run it later under load.
     - *Returns:* **`TaskHandle`** — can be awaited for the result or passed to `cancel()`.
     - *Raises:* **`SchedulerShutdownError`** if called after `drain()` has been invoked.
     ```
   - Trivial methods (no behavior beyond the signature) can be one-line under the H3 — no bullet list needed. Example: `Cancel a pending task by its handle. Returns false if the task is already running or completed.`
   - Methods with many args (5+) where the bullet list strains can split `*Returns:*` and `*Raises:*` onto their own non-bullet paragraphs below the args list. Common case (1-4 args) uses the merged form.
   - Why bold-the-identifier and italic-the-label: when scanning method specs, the reader is hunting for arg names, return types, and exception classes. Putting bold on those puts the eye on the right thing immediately; italic section labels stay scannable without dominating. Consistent with the overall "bold = identifier" convention used in the class tables.
- **Sentence-case for H3 concept headings** — `### Priority and starvation`, not `### Priority and Starvation`. Method-signature H3s preserve the exact source-code casing.
- **No blank line after `# Class Method Details`** — the first H2 follows directly (or with the 3-blank-line separator if the H2 starts a new class section after preamble).


### See Also (optional, at bottom)

After the Class Method Details zone, an optional `## See Also` H2 lists related source files / docs.

```markdown


## See Also

- `src/execution/worker.rs` — worker thread lifecycle
- `src/retry.rs` — backoff logic called by the scheduler
- `src/clock.rs` — injectable time source for testing
```

File-level concern, not class-scoped. Uses normal H2 (single, not duplicated like class H2s).


## Naming and casing summary

| Where                                    | Casing                                  | Example                                |
| ---------------------------------------- | --------------------------------------- | -------------------------------------- |
| File H1                                  | `{NAME} {ModuleName}`                   | `# CAE Scheduler`                      |
| SECTIONS row, column 1                   | `[[link\|Name]] type`                   | `[[#^TaskScheduler\|TaskScheduler]] class` |
| Overview-zone H2                         | `Name Type` (Type capitalized)          | `## TaskScheduler Class`               |
| Class table first-column header          | `NAME TYPE` (ALL CAPS with spaces)      | `TASK SCHEDULER CLASS`                 |
| Class table field rows                   | exact source identifier                 | `**\`queue\`**\`: PriorityQueue\``     |
| Class table method rows                  | exact source signature, link form       | `**[[#^anchor\|submit]]**\`(...)\``    |
| Details-zone class H2                    | PascalCase (source code)                | `## TaskScheduler`                     |
| Details-zone concept H3                  | sentence case                           | `### Retry semantics`                  |
| Details-zone method H3                   | exact source signature in code span     | `### \`submit(...)\` ^TaskScheduler-submit` |
| Block-ID                                 | `^ClassName-methodname`                 | `^TaskScheduler-submit`                |
| Topic block-ID                           | `^PascalCaseTopicName` (spaces removed) | `^PriorityAndStarvation`               |


## Bold and code conventions

- **Identifiers bolded inside code spans.** Bold wraps the code span containing only the name; the rest of the signature is a separate code span (no bold). Markdown form: `**\`name\`**\`: Type\`` or `**\`method\`**\`(args) -> Return\``.
- **Identifier-only variants** (enum cases with no payload, methods with no args) stay as `**\`Name\`**` — no second code span needed.
- **Plain `**Methods**` divider** — a bold-text row label, NOT a code span. It's a section marker, not an identifier.
- **No backticks around method H3 names in Details zone? No — keep them.** Method H3s ARE code; the H3 is `### \`submit(...)\` ^block-id`.


## Spacing summary

| Between                                                        | Blank lines |
| -------------------------------------------------------------- | ----------- |
| H1 and file overview prose                                     | 0 (compact) |
| File overview prose and SECTIONS table                         | 1           |
| SECTIONS table and first per-class H2                          | 2           |
| Class H2 and description prose                                 | 0 (compact) |
| Description prose and class table                              | 1           |
| Between same-zone H2s (class → class, in overview)             | 2           |
| Last overview class table and `# Class Method Details` H1      | **7**       |
| `# Class Method Details` H1 and first H2                       | 2           |
| Between Details-zone class H2s                                  | 2           |
| Between H3s inside one class                                   | 1           |
| Details zone and `## See Also`                                 | 2           |

The "2 blank lines before H2" rule is the visual separator that makes the zone-level structure readable even without the H1 label. Apply consistently. (Updated 2026-06-06 from 3 to 2.)


## Linking conventions

- **SECTIONS table → class anchors.** Use block-ID links: `[[#^TaskScheduler\|TaskScheduler]]`. The block-ID lives at the end of the class description prose in the overview zone (concatenated, no space).
- **Class table → method details.** Bold wraps the wiki-link, the alias is plain text (NO backticks), the tail is a separate code span: `**[[#^TaskScheduler-submit\|submit]]**\`(args) -> Return\``. Backticks inside the alias don't render — Obsidian shows the literal asterisks and backticks. The name segment ends up bold-regular (not monospace) while the tail is monospace; this visual asymmetry is the cost of using a working link form.
- **Method H3 in Details zone.** Block-ID at end of the H3, no space: `### \`submit(...)\` ^TaskScheduler-submit`. This is what the class-table link targets.
- **No raw heading-text links.** Because class names appear as H2 in both zones, raw `[[#TaskScheduler]]` resolves to the FIRST occurrence (overview zone). Always use block-IDs for cross-zone navigation.


## Folder docs

Every source folder that contains modules should have a **folder doc** — a module doc for the folder itself. Named `{NAME} {FolderName}.md` (e.g., `DMUX Speech.md`, `HA core.md`).

### Purpose

The folder doc describes the folder as a **coherent subsystem**: what it does, how the modules within it relate, and what API it presents to the rest of the system. This is often the most valuable documentation because it captures the architectural thinking that individual module docs can't.

### Structure

```markdown
---
description: <one-line subsystem summary>
---
# {NAME} {FolderName}
<1-2 sentences: what this subsystem does and why it exists>

| MODULES                     | Description       |
| --------------------------- | ----------------- |
| [[{NAME} ModuleA\|ModuleA]] | What ModuleA does |
| [[{NAME} ModuleB\|ModuleB]] | What ModuleB does |
| [[{NAME} ModuleC\|ModuleC]] | What ModuleC does |



## Overview
<How the modules work together. Data flow, responsibilities, key interactions. This is the high-value content — the folder-level architecture you can't see by reading individual module docs.>
```

Same H1-no-blank-after and 3-blank-line-before-H2 rules apply.

### When the folder IS an API

When the folder presents a coherent API (e.g., a Rust `mod.rs` that re-exports selected items, or a Swift folder that together implements a subsystem like "Speech"), the folder doc should describe:

- What the API offers to callers outside this folder.
- Which module is the entry point.
- The typical call sequence.

### When the folder is just a grouping

When the folder is just organizational (e.g., `utils/`), the folder doc is just the MODULES table with one-line descriptions. No Overview section needed.

### Location

Folder docs live alongside the module docs they describe:

```
{NAME} Dev/
├── {NAME} core/
│   ├── {NAME} core.md              ← folder doc
│   ├── {NAME} Command.md           module doc
│   └── {NAME} Config.md            module doc
```


## Proposed API convention

During planning, module docs describe the **proposed** design before code exists. Mark each property, method, and type description with **(proposed)** inline — e.g., `Priority queue engine **(proposed)**`. Remove **(proposed)** from each item once the implementation matches.


## Linking rule — CRITICAL

**Before writing a module doc, first add its entry to `{NAME} Dev.md` and `{NAME} Files.md`.** Do the linking first so you don't forget. An unlinked module doc is invisible — no one will find it.

- Add a row to the **Dev dispatch table** (`{NAME} Dev.md`) with a wiki-link and one-line description.
- Add the file to the **Files tree** (`{NAME} Files.md`) in the correct location.
- When creating multiple module docs in a batch, link ALL of them before writing any content. Then verify the Dev dispatch table has an entry for every module doc in the Dev folder.


## Lifecycle

module docs are **living documents** — they must stay current with the code:

- **Create** when a new module is added — link to Dev and Files FIRST.
- **Update** when the public interface or architecture changes.
- **Outdated docs are worse than no docs** — if a module doc can't be kept current, delete it.


## `{NAME} Dev.md` frontmatter — `module_docs_audited:` contract (per F074, 2026-05-19)

`{NAME} Dev.md` (the Dev folder's dispatch page) carries a YAML frontmatter field that records when module docs were last audited against source code:

```yaml
---
description: dispatch — Dev module docs
module_docs_audited: 2026-05-19
---
```

**Writer.** `[[audit-docs]]` (and any successor API-doc audit/refresh skill) writes this field to today's date at the end of every pass. No other skill writes it.

**Readers.** `[[skills/architect/SKILL\|/architect]]` reads this field as its staleness precondition — runs `git log <audited-date>..HEAD -- <source-tree>` to count commits in source since the audit. Other architecture/spec-consuming skills may read it similarly.

**Format.** ISO date `YYYY-MM-DD`. If the field is absent, the contract is "never audited under this discipline" — readers treat as fully stale and recommend an audit pass.


## Reserved `Arch` row (per F074, 2026-05-19)

Every module doc's dispatch table (when present) carries an **`Arch` row** maintained by `[[skills/architect/SKILL\|/architect]]`:

```
| Arch | [[{NAME} <Subsystem> Arch]] |       ← architect-managed
```

The `Arch` row points to the **most-specific** architecture destination — the per-module arch doc if one exists, otherwise the subsystem arch doc, otherwise the top-level `{NAME} Architecture.md` (single-subsystem case). Every module doc has exactly one such row. See `[[FCT Architecture]]` § Bidirectional cross-linking.

(In the new format demonstrated by `CAE Scheduler.md`, the breadcrumb `:>>` line carries the cross-references explicitly and the dispatch-table `Arch` row is optional. Use whichever shape matches the rest of the anchor.)

# BRIEF

- **This is the facet spec for one module doc per source module** — the rules below govern the file shape, structure, naming, and linking of `{NAME} {ModuleName}.md` files under `{NAME} Dev/`. The canonical worked example is `[[CAE Scheduler]]`; read it before authoring or revising.
- **Not for layer-wide contracts** — those belong in `[[FCT Interface]]` (the human-authored layer contract that groups modules). Don't pile architecture-level discussion here either; that goes in `[[FCT Architecture]]` and the per-anchor `Arch` row points to it.
- **Inclusion test** — a rule belongs in this spec only when it constrains how a single module doc is shaped (sections, tables, casing, block-ID format, figure workflow, frontmatter contract). Cross-module rules go in the trait or anchor-level spec; rendering rules belong in `[[R-markdown]]`.
- **Load-bearing conventions** — the SECTIONS / per-class-table / Class Method Details two-zone structure, the bold-identifier-outside-code-span linking form (backticks inside wiki-link aliases do NOT render), the block-ID format `^ClassName-methodname`, the `module_docs_audited:` frontmatter contract on `{NAME} Dev.md` (per F074), and SVG-only figures via the `[[viz-excalidraw]]` workflow. Breaking any of these breaks downstream readers (`[[skills/architect/SKILL\|/architect]]`, `[[audit-docs]]`, Obsidian rendering).
- **Cite this spec, don't inline it** — the `[[module-doc]]` skill, `[[audit-docs]]`, and the `architect` skill all read this file as authority. When updating a rule, update it here once; consumers pick it up automatically. Don't restate format rules in the skills.
- **When format conventions evolve** (as in the 2026-06-06 rewrite), update the dated working-example pointer at the top AND make sure the "Naming and casing summary" + "Spacing summary" tables stay in sync with the prose above — those tables are what auditors check against.
- **Don't pad the body upward from this brief** — the format spec is the canonical body content; user-facing orientation is the one-sentence TLDR under the H1. Detail that only an editing agent needs (e.g. why backticks inside aliases break) lives here, not in the body.
