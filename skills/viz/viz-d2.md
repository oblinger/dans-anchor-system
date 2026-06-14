# viz-d2 — D2 system diagrams

Create / update system-architecture diagrams (boxes and arrows) using **D2** with the **ELK** layout engine. Per `[[F121 — viz d2 — D2 diagrams via ELK]]`.

**Reference:** D2 syntax at https://d2lang.com. ELK layout: https://eclipse.dev/elk/

## Use when

User says: "diagram this system", "draw a system diagram", "make a D2 of X", "system architecture for Y", or any boxes-and-arrows ask for a software system. D2 is the **default for system-architecture diagrams** in the vault — supersedes `mermaid` and `dot` for this use case (per F121 trade-offs).

## File layout — two branches

Determined by whether `--into <target-doc.md>` is provided.

### Branch 1 — target doc specified

```
/viz d2 --into <target-doc.md> "<prose>"
```

Both `.d2` source and `.svg` output land **adjacent to the target doc** (same folder). The SVG is embedded directly in the target doc, **page-width**, via `![[<derived-name>.svg|800]]`. **No wrapper** — the target doc IS the iteration surface.

**Legibility — figures span the page, and read at that width.** Embed at ~800px (an 8.5×11 page width) so the figure is never a tiny fit-to-column thumbnail. Equally important: author the diagram with a **page-friendly aspect** — an ultra-wide graph (e.g. `direction: right` across many nodes) shrinks to illegible text when fit to page width, and an ultra-tall one scrolls forever. Prefer `direction: down` with each sub-pipeline/container set `direction: right` (a compact grid) so the rendered width is near page-width and the text is legible at the embedded size. If a render comes out wildly wide (≫ ~1200px) or tall, adjust direction/grouping and re-render before embedding.

```
{dirname(<target-doc>)}/<derived-name>.d2
{dirname(<target-doc>)}/<derived-name>.svg
{target-doc.md}                                 ← agent embeds ![[<derived-name>.svg]] in this
```

### Branch 2 — no target

```
/viz d2 "<prose>"
```

Files land in the vault's scratch folder under `viz/` (per the ob-skills convention). An auto-generated wrapper markdown serves as the iteration surface.

```
{scratch_root}/viz/<derived-name>.d2
{scratch_root}/viz/<derived-name>.svg
{scratch_root}/viz/<derived-name>.md            ← auto-generated wrapper that embeds the SVG
```

Resolve `scratch_root` via:

```bash
SCRATCH_ROOT=$(~/.claude/skills/ob-skills/scripts/ob-skills config scratch_root --default "$HOME/ob/kmr/scratch")
mkdir -p "$SCRATCH_ROOT/viz"
```

Currently resolves to `~/ob/kmr/_/URL/SCR/Scratch/viz/`. After writing the wrapper, surface a one-line hint to the user: *"Pass `--into <doc>` next time to land directly in a real doc."*

## Action subcommands

```bash
/viz d2 --into <target-doc.md> "<prose>"          # primary — embed in named target
/viz d2 "<prose>"                                  # fallback — scratch + wrapper
/viz d2 --update <path-to.d2> "<prose-of-edit>"    # edit existing diagram
/viz d2 --raw <path-to.d2>                         # re-render existing source only
/viz d2 --layout <dagre|elk|tala> "<prose>"        # override default ELK
```

## Phase 0 — discovery (first call only)

On invocation for a **brand-new** diagram, read the user's prose and self-check: *do I have enough to draw a clear diagram?* If the prose is ambiguous about any of:

- Whether named entities are services, actors, data stores, or external systems
- Direction of flow (data-flow LTR vs call-direction TTB)
- Granularity (one DB box vs split read/write)
- Whether async/sync edges differ in the system

…then ask **1–3 quick clarifying questions in conversation**, batched together (per the user's batch-questions rule). Do not produce any artifact yet. Once you've judged the picture is clear, proceed to Phase 1.

Phase 0 also re-fires when the user's prose introduces a major structural addition you don't know how to draw cleanly.

## Phase 1 — main loop

For every invocation after Phase 0 (or for every edit):

1. **Derive the name** — sanitized 3–5-word slug from the prose (e.g. `auth-flow-architecture.d2`).
2. **Write/edit the `.d2` source.** D2 syntax basics inline below.
3. **Render to SVG:**
   ```bash
   d2 --layout=elk "<dirname>/<derived-name>.d2" "<dirname>/<derived-name>.svg"
   ```
4. **Wire the embed — page-width:** always embed with an explicit display width so the figure **spans the page** (an 8.5×11 page ≈ 800px of content), never the tiny fit-to-column default. Use `![[<derived-name>.svg|800]]`.
   - **Branch 1** (target doc): if `<target-doc>.md` doesn't already contain the embed, insert `![[<derived-name>.svg|800]]` at the end (or at a `<!-- viz-d2 -->` HTML comment if one exists).
   - **Branch 2** (scratch): if the wrapper doesn't exist, write it:
     ```markdown
     # <derived-name>

     ![[<derived-name>.svg|800]]

     <!-- D2 source: <derived-name>.d2 — edit via /viz d2 --update -->
     ```
5. **Glance:**
   - Branch 1: `open "<target-doc.md>"`
   - Branch 2: `open "<wrapper.md>"`
6. **Wait for user reaction.** Either "looks good" → done, or prose-edit → loop to step 2 with the new prose, or "view D2" → side door (see below).

## "View D2" side door

When the user says any variant of **"view D2"**, **"glance D2"**, **"show the D2 source"**, or just **"D2"** in inspection context, open the `.d2` source file in **Sublime** (matches the user's `sublime` trigger word):

```bash
open -a "Sublime Text" "<path>.d2"
```

This is for hand-editing — Obsidian doesn't render `.d2`, so this is the user's hand-tune side door. Resume the main loop when the user re-engages with prose; on next invocation, re-render the (possibly hand-edited) `.d2` to refresh the SVG.

## D2 syntax cheat sheet (for the agent)

```d2
# nodes — name then label
user: User {shape: person}
api: API Service
db: Postgres {shape: cylinder}

# containers — group with curly braces
backend: Backend Cluster {
  api: API Service
  worker: Worker
  cache: Redis {shape: cylinder}
}

# arrows — labeled
user -> api: HTTPS
api -> db: SQL
api -> cache: reads/writes

# arrow types
a -> b: sync call
a --> b: async / fire-and-forget   # dashed
a <-> b: bidirectional
a -- b: knows about (no arrow)

# styling
node-name.style.fill: "#f4e4c1"
node-name.style.stroke: "#b8860b"

# multi-line labels
api.label: "API\nGateway"
```

**Default render command:**

```bash
d2 --layout=elk source.d2 source.svg
```

**Alternative layouts** (only if ELK isn't producing acceptable layout):

```bash
d2 --layout=dagre source.d2 source.svg    # simpler hierarchical
d2 --layout=tala source.d2 source.svg     # paid Terrastruct TALA (best aesthetics; requires API key)
```

For TALA, the user supplies an API key via `D2_TALA_API_KEY` env var; without one, TALA exits with an error.

## Source-of-truth invariant

The `.d2` file is the source of truth. The `.svg` is derived; treat as ephemeral if missing. On any invocation that targets an existing `.d2`, re-render the `.svg` before glancing — never trust a stale render.

## Install gate

If `d2 --version` fails on the first invocation, print:

```
viz-d2: d2 is not installed. Run: brew install d2
```

and exit. Don't auto-install; the user controls when system packages land.

## Output to the user

After each successful round-trip, surface:

- Path to `.d2`
- Path to `.svg`
- Path to the glanced doc (target or wrapper)
- One line: *"Glanced. React with prose to edit, 'view D2' to open source in Sublime, or 'looks good' to finalize."*

## Cross-references

- Spec: [[F121 — viz d2 — D2 diagrams via ELK]]
- Methodology: see § "What actually makes a system diagram readable" in [[2026-06-06 system diagram tools]]
- ob-skills convention for `scratch_root`: [[ob-skills/SKILL]]
- Trigger word for hand-tune side door: `sublime` (per [[~/.claude/CLAUDE]] trigger table)
