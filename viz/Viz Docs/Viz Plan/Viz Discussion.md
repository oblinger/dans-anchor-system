---
description: Open trade-off discussions, design questions, and round-trip experiments for the /viz skill. Where multi-agent and human deliberation happens before decisions land in PRD / Design.
---

# Viz Discussion

| -[[Viz Discussion]]- | → [ob](hook://ob) → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[skills]] → [[Viz]] → [[Viz Docs]] → [[Viz Plan]] → [Viz Discussion](hook://p/Viz%20Discussion)<br>: open trade-off discussions for /viz |
| --- | --- |
| --- | |

The home for open-ended trade-off conversations about /viz — round-trip experiments, design questions, tool-selection debates, multi-agent deliberation. **Decisions don't land here.** When a discussion resolves, the resolution moves to either:

- `Viz PRD.md` — if it's a product-shape decision (what /viz is for; what it produces)
- `Viz Design.md` — if it's an architecture decision (how the skill is structured internally)
- `viz/SKILL.md` — if it's an agent-rule change (decisive runbook update)
- `SKL Viz.md` — if it's user-facing guidance (capability matrix, decision shortcuts)

The discussion entry itself stays here as a historical record, with a one-line resolution pointer.


## Open discussions

### 2026-06-01 — Obsidian round-trip + clickability investigation

**Initiated by:** the user (delegated to another agent in parallel) — figure out how to set up viz outputs so they round-trip (edit → render → re-edit cleanly) AND are viewable inline in Obsidian AND have clickable regions both in Obsidian and outside.

**Current state of knowledge (from the capability matrix in [[SKL Viz]]):**

- **mermaid** — round-trips trivially (source IS the markdown); native Obsidian render; `click` directive partial in Obsidian, full on the web.
- **excalidraw** — round-trips with the Excalidraw plugin (edit on canvas, save back to source); SVG export for external clickability.
- The other approaches lose either round-trip OR inline view OR external clickability.

**Open sub-questions:**

1. **Excalidraw plugin install + configuration.** Which Excalidraw plugin (community / official) does the user have installed? Confirmed working with `.excalidraw` JSON files in the vault? How is the auto-export-to-SVG hook configured (if at all)?
2. **Mermaid `click` in Obsidian.** Does Obsidian's bundled Mermaid renderer respect the `click` directive for internal `[[wikilinks]]` (vs only external URLs)? Test case needed.
3. **SVG embed clickability.** When `.svg` is embedded via `![[file.svg]]`, do internal `<a href="https://...">` anchors render as clickable in Obsidian's image viewer? Test case needed (Obsidian's behavior depends on the renderer pipeline).
4. **DOT → SVG → Obsidian.** Does `dot` with `URL=...` node attributes produce SVG with `<a>` tags that survive Obsidian embed? Likely partial; needs concrete test.
5. **PDF inline clicks.** Obsidian's PDF viewer is known to NOT handle embedded hyperlinks. Confirm or refute on the current Obsidian version. If confirmed: PDF is a non-starter for clickable-in-Obsidian use cases.

**Investigation hand-off:** the other agent's findings should land back here as sub-points under each question; once each sub-question is resolved with a definitive yes/partial/no + concrete test evidence, update the matrix cell in [[SKL Viz]] and link the discussion entry to the matrix update.

**Resolution policy:** when ALL five sub-questions are resolved, replace the open-discussion entry with a one-line resolution pointer (e.g., *"Resolved 2026-06-XX → matrix in [[SKL Viz]] tightened; see commits abc1234 / def5678"*) and migrate this entry to a `## Resolved` H2 at the bottom of this doc.


## Resolved

(Empty. Resolved discussions migrate here from `## Open discussions` as one-line entries with pointers to where the decision actually lives.)
