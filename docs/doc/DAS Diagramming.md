---
description: "The **diagramming discipline** — the judgement half of making figures: when a picture earns its place, why the editable source ships beside the export, and what the description sidecar is for."
---

| -[[DAS Diagramming]]- | : The **diagramming discipline** — the judgement half of making figures: when a picture earns its place, why the editable source ships beside the export, and what the description sidecar is for.<br>→ [[DAS]] → [docs](hook://docs) → [DAS Diagramming](hook://p/DAS%20Diagramming)  |
| --- | --- |
| Related | [[skills/diagramming/SKILL.md\|SKILL]] (runtime),  [[DAS Viz]] (the tools),  [[R-diagram]] (the checks) |
| ... |  |

# DAS Diagramming
The concept dossier for the **diagramming discipline** — the standing judgement about figures, as distinct from the tools that draw them and the rules that check them.

## What it is

Three separate things govern a figure in this system, and knowing which one you are asking about saves a lot of hunting:

- **[[DAS Viz]]** — the *tools*. Which renderer to reach for, what round-trips in Obsidian, what stays clickable after export.
- **[[R-diagram]]** — the *checks*. 22 rules across seven sub-sets: geometry, graph aesthetics, C4 semantics, contrast, typography, data-ink, SVG hygiene. Every one asks whether a figure is **correct**.
- **This discipline** — the *judgement*. Whether the figure should exist, what ships with it, and what the next person needs to know before changing it.

Nothing in the first two answers *should I draw this*, which is what makes the third a separate thing rather than a section of either.

## What it asks of you

**A picture earns its place, or it does not get made.** The default is prose. A figure is worth its ongoing cost — re-rendering, re-auditing, re-reading — when it carries a relation you have to hold several of at once: a topology, a branching flow, a containment hierarchy, a before-and-after. It is *not* worth it when it re-states a list. The tell is that you can read the figure aloud as a sentence and lose nothing.

A figure that is **wrong** is worse than one that is absent, because a picture reads as authoritative in a way a sentence does not — a reader who catches prose and figure disagreeing will usually believe the figure.

**The editable source ships beside the export.** `.d2` / `.excalidraw` / `.py` next to the `.svg` / `.png`; for a generated image, the prompt is the source. An export on its own is a dead end: hand-patch it once and nobody can tell any more whether the source or the export is authoritative, and the drift is silent because both still render.

**A figure carries a `{base}.desc.md` sidecar** recording what it must convey and — the part that matters — what it **deliberately leaves out**. Omissions are invisible in the figure itself, so without the sidecar the next person to improve it is one reasonable-looking change away from re-adding something you already said no to. The sidecar is a living summary rather than a log: superseded preferences get removed, not struck through.

## When you notice it

Mostly you will not, and that is the intent — it shapes what an agent proposes rather than producing output of its own. Three moments where it surfaces:

- **You ask for a diagram and get a sentence instead**, with a line saying why a figure would not have earned its place. That is § 1 doing its job; overrule it if you disagree and the figure gets made.
- **You get two files where you expected one** — an `.svg` and the `.d2` that produced it, plus a `.desc.md`. That is § 2 and § 3.
- **You correct a figure once and it stays corrected** across later edits by a different agent. That is the sidecar; the alternative is re-explaining the same preference.

## Why it exists

Dan, 2026-08-02: *"all this stuff that you're banking about drawing pictures, I feel like it should be somewhere. Maybe it's like an addendum file to the skill that just is, you know, wisdom that's going to get published to other people. I feel like it's different than the skill itself, which is kind of very mechanical."*

The observation was exact. The mechanical half was written down in two places and the judgement half in none — and the source-alongside-output rule was being cited in the published standard as settled policy while existing nowhere a reader could reach. A discipline is the shape the system already had for *"a methodology other skills follow, published outward"*, so this is an instance of an existing kind rather than a new one.

Commissioned by [[TINK Backlog#^T566|T566]]; the slot was settled by [[TINK Backlog#^T558|T558]].
