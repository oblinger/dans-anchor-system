---
description: "`/image` — generate an image from a prompt, with the prompt kept beside it and the cost stated"
---
# DAS Image
`/image` — generates an image from a prompt, writing the prompt beside the result and reporting what it cost.

| -[[DAS Image]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [docs](hook://docs) → [DAS Image](hook://p/DAS%20Image)<br>: `/image` — generate an image from a prompt, with the prompt kept beside it and the cost stated |
| --- | --- |
| Related | [[skills/image/SKILL.md\|SKILL]],  [[DAS Viz\|Viz]] (authored counterpart), |
| ... |  |

The generative counterpart to [[DAS Viz|/viz]]. `/viz` renders what you specify exactly and can re-derive it from source; `/image` asks a model to invent something, so the same prompt twice gives you different pictures. Everything distinctive about this skill follows from that.

## What you get

Every image lands with a `.prompt.md` sidecar beside it — prompt, backend, model, seed, size, cost, date. For a generated image the prompt *is* the source, so without it a result you liked can never be reproduced.

Every run prints what it spent. A batch over $1.00 refuses unless you confirm, so a fan-out cannot quietly burn money.

## Presets

Once a look is right, save it and reuse it: later runs reload the locked prompt and vary only the scene. This is what keeps a recurring character — an agent persona, a mascot — recognizably itself instead of drifting on every generation.

## Speaking it

The spoken trigger is **"really image"**, not bare "image" — too common a word to trigger on alone. Say *"really image, a wide shot of the rooftop at night"*.

## Cost

FLUX via fal is $0.025 per megapixel — a 1024×1024 image is 2.5¢. Credentials live in the login keychain, never in a file.
