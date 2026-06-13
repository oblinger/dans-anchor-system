---
name: api-doc
description: >
  Author or revise an API documentation file conforming to [[FCT Module Doc]]
  facet. Reads source code, generates the doc skeleton (SECTIONS table,
  per-class tables with bold-identifier rows, Class Method Details zone with
  block-ID-targeted method H3s), authors the figure via the viz/excalidraw
  workflow, runs `/audit api-doc` to validate, fixes warnings to zero, does
  a subjective re-read against the facet, links in dispatch tables, commits.
  Mirrors the `/architect` skill pattern. Use when the user says "/api-doc",
  "write the API doc for X", "document this class", "document this module",
  or hands a source path or wiki-link to revise.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# /api-doc — Author and Maintain API Documentation

`/api-doc` authors or revises an API documentation file conforming to the [[FCT Module Doc]] facet. The facet is the rule source; this skill is the procedure. A companion `audit-api-doc.py` script (invoked as `/audit api-doc <file>`) performs mechanical conformance checks; the agent fixes warnings to zero, then does a subjective re-read for the rules mechanical checks can't cover (figure readability, prose clarity, layout judgment).

Feature spec: `[[F119 — api-doc skill + audit-api-doc.py — author audit iterate for CAB API Doc facet]]`. Companion spec: `[[FCT Module Doc]]` (the facet — read it before authoring).


## When to Use

- User says `/api-doc`, "write the API doc for X", "document this class", "document this module/subsystem", "API doc for ...".
- User hands a source-code path (single file or folder) or an existing API doc wiki-link.
- After significant source-code changes — to refresh the API doc against the new interface.

**Don't** invoke `/api-doc` for:
- Module-level prose updates that aren't API-doc-shaped (use direct edit).
- Architecture-level synthesis (use `/architect`).
- README / user-facing prose (different audience).
- **Generated code** — auto-generated bindings, protobuf stubs, OpenAPI-generated clients. Document the generator's contract instead, not the output.
- **Vendor-bundled libraries** in the repo for build convenience (third_party/, vendor/). The vendor owns the API doc.
- **Single throwaway scripts** — one-shot migrations, dev-loop helpers under 50 LOC with no public surface. Inline comments are sufficient.
- **Internal-only helpers** with no public API (every symbol is `_underscore`-prefixed or `private`/`internal` keyword). Document via inline comments.


## Pre-flight checks (before authoring)

Before any authoring step, validate the environment is set up:

1. **Facet readable** — `[[FCT Module Doc]]` exists at `~/ob/kmr/SYS/Bespoke/Skill Agent/CAB/CAB Facets/CAB API Doc.md`. Use `ha -p "CAB API Doc"` to confirm. If missing, STOP — surface to user.
2. **viz/excalidraw available** — `~/.claude/skills/viz/excalidraw_to_svg.py` exists. Required for figure authoring. If missing, surface to user before proceeding.
3. **audit script available** — `~/.claude/skills/audit/scripts/audit-api-doc.py` exists. Required for the iterate loop.
4. **Source exists and is readable** — the target source file/folder exists; not a broken symlink.
5. **Public API present** — does the source actually expose a public surface? If everything is `_private` / file-internal, surface to user and ask whether to proceed (likely answer is no — see "When NOT to invoke" above).
6. **Target location resolvable** — the chosen `{NAME} {ModuleName}.md` path doesn't collide with an existing doc in another anchor. If it does, ask the user before overwriting.


## Invocation

```
/api-doc <source-path>              ← author a new API doc for this source
/api-doc <existing-api-doc.md>      ← revise / refresh an existing API doc
/api-doc                            ← (bare) ask the user for the target
```

**Smart-detect:** if the target is a `.md` file matching `{NAME} {ModuleName}.md` shape, treat as revision; otherwise treat as new authoring.


## Runbook — new authoring

### 1. Read the facet
**Read `[[FCT Module Doc]]`** in full before authoring. The facet defines what an API doc IS — every formatting decision, naming convention, spacing rule, table shape lives there. The subjective re-read at the end (step 8) consults this same file again, so it must be loaded fully.

```bash
# Locate via ha (or direct path)
ha -p "CAB API Doc"
```

### 2. Resolve where the API doc lives
- **Per-module API docs** (the common case): `{NAME} Docs/{NAME} Dev/{NAME} <sub-folder>/{NAME} {ModuleName}.md`, mirroring the source repository tree under `{NAME} Dev/`.
- **Subsystem / API-surface docs**: `{NAME} Docs/{NAME} Design/{NAME} API/{NAME} <Subsystem> API.md`.
- **If the location is ambiguous**, ask the user — this is creation-time, one-question, active mode.

### 3. Read the source
Read the source file(s) directly. For a folder, walk every source file with a public API. Identify:
- **Classes** — name, fields, methods (with full signatures: arg types + return type).
- **Enums** — name, variants (with payload types where applicable).
- **Topics** — design rules, invariants, cross-cutting behaviors that don't belong to one method. Look for: queue ordering rules, retry policies, lifecycle invariants, threading guarantees.
- **Important data structures** — queues, pools, caches, registries, indexes — that aren't classes but appear in the figure.

Per F068 — don't ask the user about API content; the source IS authoritative.

### 4. Generate the doc skeleton
Author the markdown structure per [[FCT Module Doc]]. Key elements (full rules in the facet):

- **Frontmatter** — YAML with `description:` field.
- **Breadcrumb** — `:>> [[anchor]] → [[Docs]] → [[Dev]] → [[Architecture]]` line.
- **H1 + file overview prose** — `# {NAME} {ModuleName}` immediately followed (no blank line) by a 2-4 sentence overview.
- **Figure embed slot** — `![[{NAME} {ModuleName}.svg]]` (the actual SVG is authored in step 5).
- **SECTIONS table** — `| SECTIONS | Role |` header; each row is `[[#^anchor|Name]] type` linking to the section's block-ID, with a role description in column 2. Type word lowercase after the link (`class`, `enum`, `topic`, `struct`, `protocol`).
- **Per-section H2s** — `## Name Type` for code-typed sections (Type capitalized, only when there IS a code type: `## TaskScheduler Class`, `## TaskState Enum`); `## Name` bare for topics / conceptual sections (no qualifier: `## Priority and starvation`). H2 immediately followed (no blank) by description prose ending with the block-ID inline (no space): `...flows through it.^TaskScheduler`.
- **Class tables** — header first column carries the class name in `ALL CAPS WITH SPACES TYPE` form (`TASK SCHEDULER CLASS`); second column header is `Description`. Field rows use bold-identifier-only form `**\`name\`**\`: Type\``. `**Methods**` divider row between fields and methods. Method rows use `**[[#^anchor|name]]**\`(args) -> Return\`` — backticks NOT inside the wiki-link alias.
- **Topic sections** — bulleted description list (NOT a table by default): `- **Concept label** — description.` Include a `**Rule reference**` bullet pointing at the canonical rule when the topic anchors a design rule.
- **2 blank lines before each H2** (overview-zone separator). **7 blank lines** before `# Class Method Details` H1 (zone separator).
- **Class Method Details zone** — `# Class Method Details` H1, then `## ClassName` H2 per class (no type qualifier in details zone), then H3 per class-level concept (sentence case: `### Retry semantics`), then H3 per method with full signature in code span + block-ID: `### \`submit(...)\` ^TaskScheduler-submit`.
- **Method body** — brief paragraph, then `*Args:*` italic heading, then merged bullet list with bold identifiers: `- **\`task\`**: description.` Returns and Raises are bullets within the same list with italic labels: `- *Returns:* **\`TaskHandle\`** — description.` `- *Raises:* **\`Error\`** if ...`.
- **`## See Also`** at the bottom — optional bullet list of related source files / docs.

### 5. Author the figure
**Read `[[viz-excalidraw]]`** before creating any figure — every Excalidraw element needs a specific property set or ExcalidrawZ silently fails. The reference examples at `~/.claude/skills/viz/excalidraw-examples.md` are mandatory reading.

Workflow:
1. Create `{NAME} {ModuleName}.excalidraw` alongside the `.md`. The JSON describes the figure: a node per section, edges showing data flow, a legend (typically at the bottom).
2. Convert: `python3 ~/.claude/skills/viz/excalidraw_to_svg.py "/path/to/file.excalidraw"` — generates `.svg` and `.png`.
3. Embed: `![[{NAME} {ModuleName}.svg]]` (Obsidian wiki-embed syntax, NOT markdown image syntax).
4. Open in ExcalidrawZ for user-editing: `open -a ExcalidrawZ "/path/to/file.excalidraw"`.

Apply the layout guidelines from `[[FCT Module Doc]]` § Layout guidelines: minimize crossings (one acceptable load-bearing crossing is OK), push secondary nodes off primary flow paths, keep text out of lines, short labels (`submit` not `submit(task, deadline)`), legend out of the way (default bottom), solid arrows for primary flow / dotted for derivation.

**Figure size: HARD RULE — spans full page width.** Author the `.excalidraw` content area ~1400-1600 px wide. In the markdown embed, use `![[{NAME} {ModuleName}.svg|1200]]` if Obsidian doesn't auto-scale to column width.

### 6. Run `/audit api-doc`
```bash
/audit api-doc "<path to .md>"
```

The script emits warnings with line numbers and rule references (C1-C26). Read the full warning list before fixing.

### 7. Fix warnings to zero
- **Mechanical fixes** (spacing, blank-line runs, normalization) — re-run with `--fix`: `/audit api-doc <file> --fix`. The script auto-fixes C3, C21, C22, C23, C24.
- **Manual fixes** — every other warning needs hand-edit. The warning's rule reference points at the specific section of `[[FCT Module Doc]]` that governs it.
- **Re-run audit after fixing.** Iterate until the script reports zero warnings.

### 8. Subjective re-read

Re-read `[[FCT Module Doc]]` and walk through this **concrete subjective checklist**:

**File-level:**
1. **One-glance gist** — could a reader who's never seen this module understand its purpose from the H1 + overview paragraph alone? If they'd need to scroll to the SECTIONS table or read prose past sentence 3, the overview is too dense or too abstract.
2. **Section names match section content** — does each H2 deliver what its name promises? `TaskScheduler Class` should contain only the TaskScheduler API; `Priority and starvation` (bare-named topic) should focus on that single rule.
3. **No redundancy** — the same fact shouldn't appear in the SECTIONS Role column, the class table description column, and the prose description. Each surface plays a different role; redundancy is a smell that the section split is wrong.

**Figure:**
4. **Figure tells the same story as the text** — every section in SECTIONS appears as a node in the figure (or is justified absent). Every meaningful data structure mentioned in the prose appears in the figure.
5. **Crossings minimized** — count line crossings in the figure. One acceptable crossing for a load-bearing relationship is OK. Two or more usually means a node should be repositioned.
6. **Labels don't overlap nodes or each other** — each arrow label has clearance. If a label collides with a box, move the label or rotate it along the arrow.
7. **Legend earns its space** — is the legend explaining 5+ distinct categories the reader couldn't infer? If the figure only uses 2 colors, the legend can be inline in the caption.

**Class tables:**
8. **Field/method ordering matches source declaration order** — readers will hunt left-to-right by source familiarity; alphabetical ordering breaks this.
9. **Description column carries net-new information** — `submit` having description "submit a task" is filler. The description should explain side effects, ownership transfer, threading constraints — what the signature alone doesn't tell you.
10. **Methods divider only appears in tables that have both fields AND methods** — a fields-only or methods-only class doesn't need the divider.

**Topic sections:**
11. **Topic content actually carries its weight** — does each topic express a design rule, invariant, or cross-cutting behavior worth elevating to top-level section? If it's just a paragraph of prose, it should be inline in the relevant class's Class Method Details concept H3 instead.
12. **Rule reference present** — when a topic anchors a project rule, the bullet list ends with `**Rule reference** — [[ProjectRules#Rn|Rn]]` pointing at the canonical rule.

**Method body:**
13. **Arg descriptions explain WHY, not just what** — `task: Callable. The function to run.` is filler. `task: Callable with no arguments. Side effects are the caller's responsibility.` says something the signature doesn't.
14. **Returns and Raises actually exist** — if the method has a return type or declared exceptions, the corresponding bullets must be present. Missing them is silent under the mechanical script but a real defect.

If any subjective check fails, fix the doc, then re-run `/audit api-doc` to confirm no mechanical regressions, then re-do the subjective check.

### 9. Link in dispatch tables
Per the facet's CRITICAL linking rule:
1. Add a row to the `{NAME} Dev.md` dispatch table linking the new doc with a one-line description.
2. Add the file to the `{NAME} Files.md` tree in the correct location.

Don't skip this — an unlinked API doc is invisible.

### 10. Commit + glance

Single commit containing:
- The `.md` API doc.
- The `.excalidraw` source.
- The generated `.svg` and `.png`.
- The `{NAME} Dev.md` and `{NAME} Files.md` updates.

Commit message: `<NAME> {ModuleName}: API doc shipped (per F119)`.

**After commit, glance the file** so the user sees the result:

```bash
open "<path to {NAME} {ModuleName}.md>"
```

Also glance the figure source if the user might want to refine it:

```bash
open -a ExcalidrawZ "<path to {NAME} {ModuleName}.excalidraw>"
```


## Worked example — `CAE Scheduler`

Reference example showing the full flow. Source: `CAE/src/execution/scheduler.py` (hypothetical). Target API doc: `~/ob/kmr/SYS/Bespoke/Skill Agent/CAE/CAE Docs/CAE Dev/CAE Scheduler.md`.

**Pre-flight:**
```bash
ha -p "CAB API Doc"                              # facet readable ✓
ls ~/.claude/skills/viz/excalidraw_to_svg.py     # converter present ✓
ls ~/.claude/skills/audit/scripts/audit-api-doc.py  # auditor present ✓
```

**Step 1-3 — Read facet, resolve location, read source:**
- Facet: `CAB API Doc.md` loaded.
- Location: `CAE Docs/CAE Dev/CAE Scheduler.md` (mirrors `src/execution/scheduler.py`).
- Source: identified `TaskScheduler` (class), `TaskHandle` (class), `TaskState` (enum), `SchedulerStatus` (class), plus a `Priority and starvation` topic (the queue's aging-promotion rule, justified as a top-level section because it's a load-bearing scheduling invariant).

**Step 4 — Skeleton.** Author the four section H2s + SECTIONS table + class tables. Class table headers:

```markdown
| TASK SCHEDULER CLASS | Description |
| --- | --- |
| **`queue`**`: PriorityQueue` | Pending tasks ordered by deadline |
| **Methods** | |
| **[[#^TaskScheduler-submit|submit]]**`(task: Callable, deadline: datetime) -> TaskHandle` | Enqueue a task with a deadline |
```

Note: bold-name-only fields, methods bold-wrap-link with no backticks in alias, code-tail outside link.

**Step 5 — Figure.** Author `CAE Scheduler.excalidraw` with 7 nodes (Caller, TaskScheduler, PriorityQueue, Worker pool, TaskHandle, TaskState, SchedulerStatus), arrows showing the data flow (submit → enqueue → next due → on done/fail → carries; status() returns; await/cancel curve). Apply layout: Worker pool to right of TaskScheduler (clears TS→TaskHandle path), legend bottom, PriorityQueue styled as topic-governed (yellow fill). Convert:

```bash
python3 ~/.claude/skills/viz/excalidraw_to_svg.py "CAE Scheduler.excalidraw"
# → CAE Scheduler.svg + CAE Scheduler.png
```

Embed in the markdown: `![[CAE Scheduler.svg]]` (or `![[CAE Scheduler.svg|1200]]` if Obsidian doesn't auto-scale).

**Step 6 — Audit:**
```bash
/audit api-doc "CAE/CAE Docs/CAE Dev/CAE Scheduler.md"
# Sample output:
# [C22] line 39: expected 2 blank lines before H2, found 3
#       fix: Remove 1 blank line before this H2 to match the 2-blank-line separator rule.
# [C21] line 87: blank line after `## TaskScheduler`; spec says compact
#       fix: Delete the blank line — heading is immediately followed by content.
# 6 findings (5 fixable via --fix)
```

**Step 7 — Fix:**
```bash
/audit api-doc "CAE/CAE Docs/CAE Dev/CAE Scheduler.md" --fix
# 5 of 6 fixed automatically; re-run to see the 1 remaining.
```
The remaining C30 (SVG older than excalidraw) means a manual re-convert: `python3 ~/.claude/skills/viz/excalidraw_to_svg.py "CAE Scheduler.excalidraw"`. Re-run audit: zero findings.

**Step 8 — Subjective re-read.** Walk the 14-item checklist above against `CAE Scheduler.md`. The figure passes (clean layout, all sections represented), prose orients cold, method descriptions are non-trivial, the topic carries weight (anchors `[[CAE Decisions#D07 — One Queue, One Clock (checked)]]`).

**Step 9 — Link in dispatch tables.** Add a row to `CAE Docs/CAE Dev/CAE Dev.md`:
```markdown
| [[CAE-Scheduler]] | Priority queue engine + worker pool for deferred task execution |
```
Add the file to `CAE Docs/CAE Dev/CAE Files.md` tree at the appropriate node.

**Step 10 — Commit + glance:**
```bash
git add "CAE Docs/CAE Dev/CAE Scheduler.md" "CAE Docs/CAE Dev/CAE Scheduler.excalidraw" "CAE Docs/CAE Dev/CAE Scheduler.svg" "CAE Docs/CAE Dev/CAE Scheduler.png" "CAE Docs/CAE Dev/CAE Dev.md" "CAE Docs/CAE Dev/CAE Files.md"
git commit -m "CAE Scheduler: API doc shipped (per F119)"
open "CAE Docs/CAE Dev/CAE Scheduler.md"
```

Done.


## Runbook — revise existing

Same as new authoring with adjustments:

1. **Read the facet** (always — the spec evolves; don't trust your prior reading).
2. **Read the existing doc.** Identify what's missing or stale.
3. **Read the source.** Identify drift between source and existing doc.
4. **Refresh content.** Update class tables, add new methods, mark deleted methods, refresh prose. Don't wipe user-authored prose without confirmation (conservative-edit posture).
5. **Refresh figure if needed.** If sections changed, re-author the `.excalidraw`; re-run the converter.
6. **`/audit api-doc <file>`.** Same loop as new authoring.
7-10. Same as new authoring (subjective re-read, link in dispatch, commit).


## Failure modes

- **User invokes without a target** — bare `/api-doc`. Ask which source/doc to work on; don't guess.
- **Source is too large for one API doc** — propose splitting per source file (one API doc per source file is the convention). Confirm with user before authoring multiple docs.
- **Existing API doc was hand-authored under the old format** — treat as new authoring (re-skeleton from scratch) with conservative-edit preservation of any custom prose. Run `/audit api-doc` to verify conformance.
- **Audit warnings won't go to zero** — if a check fires that the agent can't satisfy (e.g. block-ID resolution failing because the SECTIONS table refs don't match the H2s), STOP and surface to user. Don't ship a partially-conforming doc; the facet's rules are the contract.


## Notes

- This skill is the consumer of `[[FCT Module Doc]]`. If the facet rules change, the skill stays the same; only the verifier (`audit-api-doc.py`) and the agent's behavior need to track the spec.
- Mirrors the existing `/architect` + `audit-architecture.py` pattern. Same split: facet owns rules, skill owns procedure, script owns mechanical checks.
- Two queued user consumers were the motivation for shipping (per F119). After this lands, exercise on those consumers and iterate any rough edges.
