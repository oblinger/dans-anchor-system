# viz-diagram — Rule-enforced SVG diagrams

Author or audit hand-written SVG diagrams against the [[R-diagram]] ruleset (22 rules over 7 methodologies — geometric correctness, graph aesthetics, C4 conventions, contrast, typography, data-ink, SVG hygiene). The sibling [[viz-svg]] action is the unguarded version; this one always loads R-diagram first and uses it as the standard for "done."

## Two modes

| Mode | When | What happens |
| --- | --- | --- |
| **Create** | `/viz diagram <subject prose>` — no existing-file argument | Load R-diagram → author a new SVG following the rules → write it next to the embedding markdown → spot-check against the rules → report. |
| **Cleanup** | `/viz diagram <path-to.svg>` — argument resolves to an existing SVG | Load R-diagram → read the SVG → audit against each rule → fix violations in-place → report what changed and which rules drove the fixes. |

The agent disambiguates from the argument: a path that resolves to an existing `.svg` file → cleanup; anything else (or no argument) → create.

## Mandatory preamble — load the rules first

Before *any* SVG is written or modified, read the umbrella + the sub-sets that govern the mode:

```
library/Rulesets/Diagram/R-diagram.md
library/Rulesets/Structural/R-diagram-geometry.md
library/Rulesets/Graph/R-sugiyama.md
library/Rulesets/Diagram/R-c4.md
library/Rulesets/Accessibility/R-wcag-contrast.md
library/Rulesets/Typography/R-bringhurst-typography.md
library/Rulesets/Visualization/R-tufte-data-ink.md
library/Rulesets/SVG/R-svg-hygiene.md
```

These paths are **relative to the ob-skills repo root**. The rulesets ship in the repo alongside the skills, so they travel with any clone — never hardcode an absolute vault path (it breaks on every other machine). Resolve them from this skill's own directory: `skills/viz/` → `../../library/Rulesets/…` (the `..` segments resolve through the `~/.claude/skills` install symlink to the real repo root).

Read the umbrella first to confirm the current sub-set list; the umbrella is canonical (don't trust this list if it's drifted). The other reads can run in parallel.

Skipping the preamble is a spec violation — you don't know what "done" is without the ruleset.

## Create mode

Default when no SVG path is in the argument.

1. **Load the rules** (preamble above).
2. **Author the SVG** with the `Write` tool. The 22 rules are constraints on the output, not a step-by-step procedure. The most load-bearing ones at authoring time:
   - **R-diagram-geometry** (6 hard-fails): no box-on-box overlap; arrow endpoints anchor to box edges; no edge tunneling through unrelated boxes; text fits inside its container; labels are visually associated with one target; no label-label collision.
   - **R-sugiyama** (4): minimize edge crossings; ≤ 2 bends per edge; monotone flow direction; grid-aligned coordinates.
   - **R-c4** (4): every arrow has a label; title or legend present; meaningful box names; one meaning per visual variable.
   - **R-wcag-contrast** (2): text contrast ≥ 4.5:1, non-text UI ≥ 3:1; color is not the sole communicator.
   - **R-bringhurst-typography** (1): font sizes quantized to a small set (≤ 4 sizes).
   - **R-tufte-data-ink** (2): sibling box-sizing consistency; chartjunk budget.
   - **R-svg-hygiene** (3): stable IDs on every element; no orphan `<defs>` entries; SVG validates as XML.
3. **Reuse the viz-svg template** (`[[viz-svg]]` § SVG template) for the boilerplate: `<defs>` arrowhead marker, role-coded box palette, italic-blue arrow labels. The template already satisfies several R-c4 / R-svg-hygiene rules.
4. **Output location** — same convention as [[viz-svg]]: SVG lives next to the embedding markdown as `{Name}/{Name}.svg`. Default to `~/ob/data/MyDesk/{slug}-{YYYY-MM-DD-HHMM}.svg` when no embedding context exists.
5. **Self-audit** — run the cleanup mode's audit (below) against the new SVG before reporting done. Fix any violations.
6. **Glance the figure in its rendering context** — see § Glance in context below. The bare `.svg` / `.png` preview is NOT the right surface to show the user.
7. **Report** — confirm rule conformance: "Diagram written at `<path>`. 22/22 rules check; no violations." If any soft-fail rule was deliberately relaxed (e.g., chartjunk budget for an exception case), name it.

## Description sidecar — `{base}.desc.md`

Every figure authored via `/viz diagram` ships with a **description sidecar** at `{base}.desc.md` next to the `.svg`. The sidecar captures the user's *stated intent* — what the figure should convey, what is deliberately included, what is deliberately omitted, layout decisions, style decisions, audit-posture relaxations. The sidecar is the durable record of editorial choices that are NOT visible in the SVG itself; without it, the next agent to touch the figure is one user-correction away from re-introducing something the user already rejected.

### When to create

Author the sidecar in the **same turn** as the first SVG write. Even a minimal first version is better than none — it can grow with subsequent rounds.

### When to update

**Edit the sidecar in place** every time the user clarifies, changes their mind, or adds a new constraint about the figure. The sidecar is a *living summary*, not a chronological log:

- Superseded preferences are **removed**, not crossed out or stacked.
- The current state of stated intent is what is in the file. Nothing more.
- Git history IS the chronological record — the sidecar answers "what does the user want right now."

When the user iterates ("actually, make it taller" / "drop the labels" / "use a script font for verbs") — update the sidecar in the same turn the SVG changes. The two move together.

### When to consult

Before any subsequent SVG edit — **read the sidecar first** to recall the user's stated constraints. Treat it as authoritative for what the figure must convey and what it must avoid. Don't re-violate something the user previously rejected ("I already said no examples in boxes" / "we agreed no caption" / "the bottom labels need to line up").

### Shape

Body-only markdown (no YAML frontmatter — vault convention). Suggested skeleton:

```markdown
# {Figure title}
description:: Stated intent for `{base}.svg`. Maintained alongside the SVG by `/viz diagram`; rewritten as the user clarifies (never appended).

## What it conveys

{One paragraph naming the figure's purpose and intended reader.}

## Layout

{Box positions, sizing intentions, any deliberate geometric choices (e.g. "Facets is deliberately shorter to let arrow X pass over its top").}

## Per-element content

{Title, each box's text rows, the caption — what each piece is and why it's there.}

## Arrows

{Which arrows exist, which are labeled, which are unlabeled — and why each choice.}

## What it does NOT contain

{The deliberate omissions. As load-bearing as the inclusions. "No example lists" / "no caption" / "no labels on the obvious arrows" — capture these so they aren't re-added on the next iteration.}

## Audit posture

{Which R-diagram rules are deliberately relaxed and why. Which are fully met.}

## Color palette

{Locked colors, if part of a figure family with shared semantics.}
```

H1 matches the figure title (not necessarily the file basename). H2 set adapts to the figure — drop empty sections, add new ones as the user's constraints accumulate. Body is tight prose + tables where they help; not bullet-lists for their own sake.

### Whether to elevate to a CAB facet

Open question. The `.desc.md` convention may eventually warrant a proper CAB facet (with embedded rules, like the other facets) once the convention proves load-bearing across many figures. For now it lives here in `/viz diagram`; if and when the pattern earns elevation, file a backlog row to extract.

## Glance the PNG preview every time

**Always glance the rendered `.png` via macOS Preview, not the embedding markdown doc.** In theory the embedding doc is the better feedback channel — it shows the figure at the actual rendered width with real surrounding context. In practice **Obsidian does not refresh an embedded image when the underlying file changes** — once Obsidian has the doc open, subsequent SVG/PNG updates are invisible until the user closes and reopens the file. That breaks the in-context glance loop in the most common iteration mode (the user is iterating with the agent on a figure that's already embedded in a doc Obsidian has open).

The PNG preview is the second-best feedback channel but is the **most-best-available** channel — Preview reliably re-renders on every update, so the user sees the current version. The trade-off — Preview shows the figure standalone, with no surrounding markdown context — is the cost.

The procedure:

1. **Render PNG via `rsvg-convert`** after every SVG write:
   ```bash
   rsvg-convert -w 1800 "<path>.svg" -o "<path>.png"
   ```
   The `.png` lives next to the `.svg` (figure-source-alongside-output convention).
2. **`open` the PNG** so Preview shows it:
   ```bash
   open "<path>.png"
   ```
   Preview re-renders on every `open` invocation; the user sees the current version.
3. **Do NOT open the embedding markdown doc** as a substitute. Obsidian's stale-image problem will show the user the previous version even though the file on disk is current; the user can't tell agent's update landed.

**Exception — first-time figure (no embedding doc yet).** When the figure has not yet been embedded in any markdown, glancing the PNG is the only option. Same procedure; no special-casing.

**Once-only in-context check (optional, at the user's request).** If the user explicitly asks "how does it look in context?" or similar, then open the embedding doc — but warn: "Obsidian may show the previous version due to the refresh issue; close + reopen the doc to force a refresh." Default mode is PNG preview.

This applies to BOTH modes — create AND cleanup.

## Cleanup mode

Triggered when the argument resolves to an existing SVG.

1. **Load the rules** (preamble above).
2. **Read the SVG** at the given path.
3. **Audit pass — walk every rule.** For each of the 22 rules, perform the rule's `**Check pattern:**` (each rule file documents how to check). Group findings by sub-set so the report mirrors the ruleset structure.
4. **Fix-in-place** for each violation. Default posture: fix mechanically when the rule has a clear remediation (e.g., overlap → nudge boxes apart; tunneling → reroute through a bend; orphan `<defs>` → drop; XML validation → repair tag mismatch). Skip fixes only when the rule's intended interpretation is ambiguous in context (label-association proximity-ratio borderline cases, chartjunk subjective calls) — surface those as findings instead of fixes.
5. **Re-audit** after fixes to confirm the violation count went down without introducing new ones.
6. **Report** — emit a short table: `Rule | Before | After | What changed`. Group by sub-set. Close with the residual violation count.

## SVG conventions

Same as [[viz-svg]]:
- Font: `Helvetica, Arial, sans-serif`.
- Box stroke: `#1e1e1e` at width 2; arrow stroke at width 3.
- Box rounding: `rx="10"`.
- Role-coded palette: `#fff3f3` (boundary), `#bac8ff` (compute), `#fff9db` (storage), `#ebfbee` (policy).
- Arrow-label color: `#1971c2` (italic, font-size 14, just above the arrow).
- One `<marker id="arrowhead">` in `<defs>`, referenced via `marker-end="url(#arrowhead)"`.

These satisfy R-c4-04 (one meaning per visual variable), R-bringhurst-typography-01 (font-size quantization), R-wcag-contrast-01 (the palette colors pass against `#1e1e1e` body text).

## Optional PNG companion

Same as [[viz-svg]]:

```bash
rsvg-convert -w 1800 "Name.svg" -o "Name.png"
```

## Failure modes

- **Skipped the preamble.** Don't author or modify the SVG without first reading the ruleset. The agent's intuitions about "what a clean diagram looks like" aren't the same as the 22 rules.
- **Audit but no fix in cleanup mode.** The whole point of cleanup is to land the fixes. Surface findings only for genuinely ambiguous cases.
- **Fix introduces a new violation.** Always re-audit after fixes. Common trap: nudging boxes apart to fix overlap creates new edge tunneling.
- **Used `/viz svg` instead of `/viz diagram` when the user said "diagram".** `/viz svg` is the unguarded hand-write action; `/viz diagram` is the rule-enforced one. When the user invokes `/viz diagram`, the R-diagram rules ARE the contract.

## See also

- [[viz-svg]] — sibling unguarded SVG authoring action.
- [[R-diagram]] — umbrella ruleset (22 rules, 7 methodologies).
- [[R-diagram-geometry]] — the 6 hard-fail geometric rules.
- `feedback_figure_source_alongside_output` — source-alongside-output convention.
- `feedback_no_ascii_in_architecture_diagrams` — ASCII forbidden in architecture docs.
