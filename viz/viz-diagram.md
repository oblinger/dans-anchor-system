# viz-diagram — Rule-enforced SVG diagrams

Author or audit hand-written SVG diagrams against the [[R-diagram]] rule set (22 rules over 7 methodologies — geometric correctness, graph aesthetics, C4 conventions, contrast, typography, data-ink, SVG hygiene). The sibling [[viz-svg]] action is the unguarded version; this one always loads R-diagram first and uses it as the standard for "done."

## Two modes

| Mode | When | What happens |
| --- | --- | --- |
| **Create** | `/viz diagram <subject prose>` — no existing-file argument | Load R-diagram → author a new SVG following the rules → write it next to the embedding markdown → spot-check against the rules → report. |
| **Cleanup** | `/viz diagram <path-to.svg>` — argument resolves to an existing SVG | Load R-diagram → read the SVG → audit against each rule → fix violations in-place → report what changed and which rules drove the fixes. |

The agent disambiguates from the argument: a path that resolves to an existing `.svg` file → cleanup; anything else (or no argument) → create.

## Mandatory preamble — load the rules first

Before *any* SVG is written or modified, read the umbrella + the sub-sets that govern the mode:

```
~/ob/kmr/SYS/Bespoke/Skill Agent/skills/SKL User Docs/SKL/SKL Library/Rule Sets/R-diagram/R-diagram.md
~/ob/kmr/SYS/Bespoke/Skill Agent/skills/SKL User Docs/SKL/SKL Library/Rule Sets/R-diagram/R-diagram-geometry.md
~/ob/kmr/SYS/Bespoke/Skill Agent/skills/SKL User Docs/SKL/SKL Library/Rule Sets/R-diagram/R-sugiyama.md
~/ob/kmr/SYS/Bespoke/Skill Agent/skills/SKL User Docs/SKL/SKL Library/Rule Sets/R-diagram/R-c4.md
~/ob/kmr/SYS/Bespoke/Skill Agent/skills/SKL User Docs/SKL/SKL Library/Rule Sets/R-diagram/R-wcag-contrast.md
~/ob/kmr/SYS/Bespoke/Skill Agent/skills/SKL User Docs/SKL/SKL Library/Rule Sets/R-diagram/R-bringhurst-typography.md
~/ob/kmr/SYS/Bespoke/Skill Agent/skills/SKL User Docs/SKL/SKL Library/Rule Sets/R-diagram/R-tufte-data-ink.md
~/ob/kmr/SYS/Bespoke/Skill Agent/skills/SKL User Docs/SKL/SKL Library/Rule Sets/R-diagram/R-svg-hygiene.md
```

Read the umbrella first to confirm the current sub-set list; the umbrella is canonical (don't trust this list if it's drifted). The other reads can run in parallel.

Skipping the preamble is a spec violation — you don't know what "done" is without the rule set.

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
6. **Report** — confirm rule conformance: "Diagram written at `<path>`. 22/22 rules check; no violations." If any soft-fail rule was deliberately relaxed (e.g., chartjunk budget for an exception case), name it.

## Cleanup mode

Triggered when the argument resolves to an existing SVG.

1. **Load the rules** (preamble above).
2. **Read the SVG** at the given path.
3. **Audit pass — walk every rule.** For each of the 22 rules, perform the rule's `**Check pattern:**` (each rule file documents how to check). Group findings by sub-set so the report mirrors the rule-set structure.
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

- **Skipped the preamble.** Don't author or modify the SVG without first reading the rule set. The agent's intuitions about "what a clean diagram looks like" aren't the same as the 22 rules.
- **Audit but no fix in cleanup mode.** The whole point of cleanup is to land the fixes. Surface findings only for genuinely ambiguous cases.
- **Fix introduces a new violation.** Always re-audit after fixes. Common trap: nudging boxes apart to fix overlap creates new edge tunneling.
- **Used `/viz svg` instead of `/viz diagram` when the user said "diagram".** `/viz svg` is the unguarded hand-write action; `/viz diagram` is the rule-enforced one. When the user invokes `/viz diagram`, the R-diagram rules ARE the contract.

## See also

- [[viz-svg]] — sibling unguarded SVG authoring action.
- [[R-diagram]] — umbrella rule set (22 rules, 7 methodologies).
- [[R-diagram-geometry]] — the 6 hard-fail geometric rules.
- `feedback_figure_source_alongside_output` — source-alongside-output convention.
- `feedback_no_ascii_in_architecture_diagrams` — ASCII forbidden in architecture docs.
