---
name: image
description: >
  Generate images from a prompt — pluggable backends (fal/FLUX, and later
  recraft for SVG, local for offline), a mandatory prompt sidecar beside every
  output, visible per-call cost, and named presets that lock a character so it
  regenerates consistently. Use when the user says "/image", "really image",
  or asks for a picture to be generated. Not for authored diagrams — that is
  /viz.
user_invocable: true
---

# image — generated imagery
Generate an image from a prompt, with the prompt preserved beside it and the cost stated.

`/image` is the **generative** counterpart to [[skills/viz/SKILL.md|/viz]]. `/viz` renders artifacts you specify exactly (excalidraw, D2, matplotlib) and its output is re-derivable from source; `/image` asks a model to invent one, so the same prompt twice gives different pictures. That difference is why the two are separate skills, and why everything below exists.

## Invocation

| Form | Meaning |
|---|---|
| `/image {prompt}` | generate on the default backend |
| `/image fal {prompt}` | name the backend explicitly |
| `/image {preset} {scene}` | load a named preset, append the scene |
| *"really image, {prompt}"* | the spoken form — the dictation pipeline prefixes `/image` |

The spoken trigger is the two-word phrase **`really image`**, never bare "image" — the word is far too common in speech to be a trigger on its own.

## Backends

| Backend | Model | Cost | Use for |
|---|---|---|---|
| `fal` (default) | FLUX.1 [dev] via fal.run | $0.025/megapixel | photoreal and illustration; the quality default |
| `recraft` | Recraft V4 | $0.08 SVG | vector output — logos, icons, anything to be edited afterward |
| `local` | Draw Things on-device | free | offline, private; anything that should not leave the machine |

Only `fal` is wired today. `recraft` and `local` are declared seams, not implementations — adding one means a new entry in `BACKENDS` in the script.

## The three disciplines

- **Sidecar, always.** Every image writes a `{basename}.prompt.md` beside it carrying prompt, backend, model, seed, size, cost, and date. For a generated image the prompt *is* the source, and [[feedback_figure_source_alongside_output]] applies exactly as it does to a `.d2` beside an `.svg`. Without it, a good result is a lucky roll nobody can reproduce.
- **Cost is stated, never silent.** Every run prints images written and dollars spent. A batch costing more than `--confirm-over` (default $1.00) refuses without `--yes`, so a fan-out cannot quietly burn real money.
- **Presets lock a character.** Once a look is right, save it (`--save-preset luna`) and later runs reload the locked prompt with only the scene varying. This is what keeps a recurring character recognizably itself instead of drifting every generation.

## Script

| Script | Usage |
|---|---|
| `image-gen.py` | `python3 ~/.claude/skills/image/image-gen.py "{prompt}" [-n 4] [-b fal] [-p {preset}] [--save-preset {name}] [-o {dir}]` |

Credentials come from the login keychain, never a file on disk: `security find-generic-password -s FAL_KEY -w`. A missing key fails loudly with the command to add it — no silent fallback.

## Where output lands

Defaults to `~/ob/data/MyDesk/{label}/` — the exploration tier. Most generations are throwaway and should not touch the vault; a keeper gets promoted deliberately, carrying its sidecar with it. *(Pending confirmation — [[SKA Backlog#^F276|F276]] Q1.)*

## Dispatch

On invocation:
1. Parse the argument for a leading backend or preset name; everything after it is the prompt.
2. Run `image-gen.py` with the parsed arguments.
3. Open the results so the user sees them — never describe an image the user has not been shown.
4. Report the cost line as printed.
