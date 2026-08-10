---
description: "`/image` — generate an image from a prompt; sidecar, cost, presets."
---

| -[[DAS Imgen]]- | : `/imgen` — generate an image from a prompt, into the anchor that keeps the prompt with it<br>→ [[DAS]] → [docs](hook://docs) → [DAS Imgen](hook://p/DAS%20Imgen)  |
| --- | --- |
| Related | [[skills/imgen/SKILL.md\|SKILL]],  [[IMGEN]] (where output lands),  [[DAS Viz\|Viz]] (authored counterpart), |
| ... |  |

# DAS Imgen
`/imgen` — generates an image from a prompt, files it in the IMGEN anchor with the prompt beside it, and reports what it cost.

The generative counterpart to [[DAS Viz|/viz]]. `/viz` renders what you specify exactly and can re-derive it from source; `/imgen` asks a model to invent something, so the same prompt twice gives you different pictures. Everything distinctive about this skill follows from that: a generated image can never be re-derived, only re-rolled, so the prompt has to be caught at the moment the image is written.

## Where your pictures go

All of them to [[IMGEN]], never a scratch folder. A sitting is a **shoot** — a numbered folder, `IMGEN003 — Kitchen concepts` — and the rolls inside it are named for their position, so `IMGEN003-2C` is the third roll off the second prompt of that shoot. The shoot's own page lists every prompt newest-first with the images above it, and [[IMGEN Gallery]] is the picture-book: one image per shoot, scroll to see everything ever made.

Every call has to say which one it means. `/imgen -n "Kitchen concepts" {prompt}` opens a new shoot; `/imgen -a 3 {prompt}` adds to shoot 3; `/imgen -l` lists them with their numbers. A call that names neither is refused before it spends anything — there is no "most recent" default, because rolls landing quietly in the wrong shoot is the one mistake that is expensive to undo.

## What you get

The prompt written down with the image, as plain text you can select and reuse without stripping quote marks off it. That is the point of the whole arrangement — [[IMGEN001 — Lumen portrait]] is the shoot from before this existed, and its prompts are simply gone.

Every run prints what it spent. A run over $1.00 refuses unless you confirm, so a fan-out cannot quietly burn money.

## Presets

Once a look is right, save it and reuse it: later runs reload the locked prompt and vary only the scene. This is what keeps a recurring character — an agent persona, a mascot — recognizably itself instead of drifting on every generation.

## Speaking it

The spoken trigger is **"really imgen"** — said "really im-jen". Say *"really imgen, a wide shot of the rooftop at night"*.

## Cost

FLUX via fal is $0.025 per image — a 1024×1024 roll is 2.5¢. Credentials live in the login keychain, never in a file.
