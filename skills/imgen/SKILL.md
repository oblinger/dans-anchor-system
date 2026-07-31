---
name: imgen
description: >
  Generate images from a prompt into the IMGEN anchor — sessions kept as
  numbered batches, every prompt recorded beside the rolls it produced,
  pluggable backends (fal/FLUX today; recraft for SVG and local for offline
  are declared seams), visible per-call cost, and named presets that lock a
  character so it regenerates consistently. Use when the user says "/imgen",
  "really imgen", or asks for a picture to be generated. Not for authored
  diagrams — that is /viz.
user_invocable: true
---

# imgen — generated imagery
Generate an image from a prompt, into the anchor that keeps the prompt with it, and state the cost.

`/imgen` is the **generative** counterpart to [[skills/viz/SKILL.md|/viz]]. `/viz` renders artifacts you specify exactly (excalidraw, D2, matplotlib) and its output is re-derivable from its source; `/imgen` asks a model to invent one, so the same prompt twice gives different pictures. A generated image cannot be re-derived — only re-rolled — which is why the prompt has to be captured at the moment of writing rather than reconstructed later, and why the skill shares its name with the folder its output lives in.

## Invocation

| Form | Meaning |
|---|---|
| `/imgen {prompt}` | roll on the default backend, into the session in progress |
| `/imgen -t "{topic}" {prompt}` | open a NEW session and roll into it |
| `/imgen -n 4 {prompt}` | four rolls off the one prompt |
| `/imgen {preset} {scene}` | load a named preset, append the scene |
| *"really imgen, {prompt}"* | the spoken form — the dictation pipeline prefixes `/imgen` |

The spoken trigger is the two-word phrase **`really imgen`**. `imgen` says "im-jen".

## Where output lands

Everything goes to **[[IMGEN]]** at `~/ob/kmr/Log/IMGEN/`, alongside [[VOX]] — one anchor, no scratch tier. The naming and folder rules are the anchor's, and they live in that page's `# BRIEF`; read it before changing how this script writes. In short:

| Thing | Form |
|---|---|
| A session | `IMGEN{nnn} — {what it was about}/` — number sorts and is permanent, title reads |
| A roll | `IMGEN{nnn}-{prompt}{variant}.png` — `IMGEN002-4B` is batch 2, prompt 4, roll B |
| The record | the batch's namesake page — prompt groups newest first, prompt as plain text under its images |
| The index | [[IMGEN Gallery]] — one image per session, newest first |

**A new session writes in three places** and the script does all three: the batch folder and its page, a member row in the [[IMGEN]] masthead, and an entry at the top of [[IMGEN Gallery]]. Appending to an existing session touches only the batch page.

## Backends

| Backend | Model | Cost | Use for |
|---|---|---|---|
| `fal` (default) | FLUX.1 [dev] via fal.run | $0.025/image | photoreal and illustration; the quality default |
| `recraft` | Recraft V4 | $0.08 SVG | vector output — logos, icons, anything to be edited afterward |
| `local` | Draw Things on-device | free | offline, private; anything that should not leave the machine |

Only `fal` is wired today. `recraft` and `local` are declared seams, not implementations — adding one means a new entry in `BACKENDS` in the script.

## The three disciplines

- **The prompt is written with the image, in the same action.** Not afterwards, not by the agent remembering to. For a generated image the prompt *is* the source, and [[feedback_figure_source_alongside_output]] applies exactly as it does to a `.d2` beside an `.svg`. It goes down as a plain paragraph — no heading, no blockquote, no fence — so it copies clean. [[IMGEN001 — Lumen portrait]] is the cautionary example: real images, prompts gone, unrecoverable.
- **Cost is stated, never silent.** Every run prints rolls written and dollars spent. A run costing more than `--confirm-over` (default $1.00) refuses without `--yes`, so a fan-out cannot quietly burn real money.
- **Presets lock a character.** Once a look is right, save it (`--save-preset tink`) and later runs reload the locked prompt with only the scene varying. This is what keeps a recurring character recognizably itself instead of drifting every generation.

## Script

| Script | Usage |
|---|---|
| `imgen-gen.py` | `python3 ~/.claude/skills/imgen/imgen-gen.py "{prompt}" [-t "{new session}"] [--batch N] [-n 4] [-c "{caption}"] [-b fal] [-p {preset}] [--save-preset {name}] [--dry-run]` |

`--dry-run` resolves the batch and prints the filenames it would write without calling the API — use it to check where a roll is about to land.

Credentials come from the login keychain, never a file on disk: `security find-generic-password -s FAL_KEY -w`. A missing key fails loudly with the command to add it — no silent fallback.

## Dispatch

On invocation:
1. Parse the argument for a leading backend or preset name; everything after it is the prompt.
2. Decide the session. If the user is starting a new subject, pass `-t "{topic}"`; if they are iterating on what was just made, pass nothing and it appends to the latest batch. When unsure, `--dry-run` first and say where it will land.
3. Run `imgen-gen.py`.
4. Open the results so the user sees them — never describe an image the user has not been shown.
5. Report the cost line as printed.
