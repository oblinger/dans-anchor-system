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

Both `.d2` source and `.svg` output land **adjacent to the target doc** (same folder). The SVG is embedded directly in the target doc and **MUST fill the reading-pane width by default** — `![[<derived-name>.svg|2400]]`. **No wrapper** — the target doc IS the iteration surface.

**🚨 Page-width is the default — an ABSOLUTE REQUIREMENT.** Every diagram embeds at a width hint that **fills the reading pane**. Obsidian caps the hint to the actual pane width, so over-specify with a large value — **`|2400`** is the standard. **Never a bare `![[x.svg]]`** — a bare embed renders as a tiny fit-to-column thumbnail (this is the recurring mistake the requirement exists to kill). A **smaller fixed width (e.g. `|500`) is allowed ONLY when the figure is explicitly an inline / thumbnail diagram** — and that intent must be stated. There is no middle default: page-wide, or deliberately-inline.

**Legibility — apply the [[R-diagram]] rules so the figure reads at the displayed (pane) width.** Body text must render **≥ ~18px at the displayed width**, and the canvas **aspect stays ~0.6–1.6** (near-square / gentle landscape) so a wide pane doesn't crush it into a short strip. The levers, in order of impact:

1. **Fewer nodes (Tufte data-ink).** A top architecture figure shows **subsystems, not their internal modules** — the module breakdown lives in the Subsystems table below, never crammed into the figure. ~6 boxes, not ~12. Cramming is the #1 cause of tiny text.
2. **Compact aspect — `grid-columns` for linear flows.** A flow graph (config→pipelines→catalog→viewer) is a *chain*; ELK stretches it to an extreme (ultra-wide with `direction: right`, ultra-tall with `direction: down`) and an extreme aspect renders tiny at page width *regardless of font size*. Force a 2-D layout: set `grid-columns: 2` (or 3) + `horizontal-gap`/`vertical-gap` at the root so the nodes tile into a near-square grid (edges drawn over it). Check the rendered `width × height` aspect after every render.
3. **Big, quantized fonts (Bringhurst).** Set explicit `style.font-size` via `classes` — at most ~4 distinct sizes (e.g. 34 box / 30 secondary / 24 edge-label). Don't rely on d2's small default; set edge-label font too (it defaults to 16 and is the usual "too small" culprit).
4. **Uniform sibling boxes (Tufte) + WCAG contrast.** Same-role boxes share one `width`/`height`; dark text on light fills (≥ 4.5:1).

Verify with the math after rendering: `text_px_at_display = font_size × (display_width / svg_width)` — if that's < ~18px, the canvas is too wide → fewer nodes or fewer grid columns, then re-render. (Worked example: HBR Architecture went 3343×805 illegible → `grid-columns: 2` + subsystem-level + 34px fonts → 1034×732, ~26px at 800px.)

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
4. **Wire the embed — fill the pane (default, absolute):** always embed with a large display width so the figure **fills the reading pane**, never the tiny fit-to-column default. Use `![[<derived-name>.svg|2400]]` (Obsidian caps the hint to the pane). A smaller width is ONLY for an explicitly-inline/thumbnail figure.
   - **Branch 1** (target doc): if `<target-doc>.md` doesn't already contain the embed, insert `![[<derived-name>.svg|2400]]` at the end (or at a `<!-- viz-d2 -->` HTML comment if one exists).
   - **Branch 2** (scratch): if the wrapper doesn't exist, write it:
     ```markdown
     # <derived-name>

     ![[<derived-name>.svg|2400]]

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
