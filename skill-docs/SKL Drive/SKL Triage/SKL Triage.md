---
description: "`/triage` (or the punctuation trigger `\"` — a single double-quote as the entire message) regenerates the current anchor's per-anchor section inside `~/ob/kmr/Q.md`, the vault-level Agent Status das…"
---
# /Triage
`/triage` (or the punctuation trigger `"` — a single double-quote as the entire message) regenerates the current anchor's per-anchor section inside `~/ob/kmr/Q.md`, the vault-level Agent Status dashboard. The section is the **status of the anchor**: it walks the backlog, counts `[Questions]`, `[Verify]`, `[Active]`, and `[Ready]` items, picks an anchor TAG (`[U]` / `[A]` / `[U+A]` / `[G]` / `[-]` / `[]`), and writes one bullet per qualifying item under workflow-state H2s (Active / Ready / Now / Next, plus user-actionable Later items). The just-touched anchor bubbles to the top of Q.md, then the file opens at you so you see where everything stands in one glance.

| -[[SKL Triage]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Drive]] → [SKL Triage](hook://p/SKL%20Triage)<br>: the `/triage` skill |
| --- | --- |
| Related | [[skills/triage/SKILL.md\|SKILL]],   |
| [[SKL Triage Design\|Design]] |  |

User responds in shorthand: **"F005 Q4: yes"** resolves question 4 in F5's feature doc; **"verified F23"** moves an item from `[Verify]` to `## Done` and updates the feature-doc Status. Sticky context works too — once you say "I'm in F11 now," plain `Q7: yes` is interpreted as F11 Q7 until you switch. `/triage` is slash-only (the spoken word is too common to be a safe trigger); the dedicated keystroke is the bare `"`. Compound usage "triage and groom" runs `/groom` first to park new items, then `/triage` to surface the updated inbox.
