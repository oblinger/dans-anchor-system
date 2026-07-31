---
name: imgen
description: >
  Generate images from a prompt into the IMGEN anchor — sittings kept as
  numbered shoots, every prompt recorded beside the rolls it produced,
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

**Every call must say where the images go.** There is no default — `-n` opens a new shoot, `-a N` adds to an existing one, and a call with neither is refused before it spends anything. That is deliberate: the one failure this skill cannot tolerate is rolls landing quietly in the wrong place, and a required flag makes that unrepresentable rather than merely unlikely.

| Form | Meaning |
|---|---|
| `/imgen -n "{topic}" {prompt}` | open a NEW shoot and roll into it |
| `/imgen -a {N} {prompt}` | add to shoot N |
| `/imgen -l` | list the shoots with their numbers — how you find N |
| `/imgen -a {N} -r 4 {prompt}` | four rolls off the one prompt |
| `/imgen -n "{topic}" -p {preset} {scene}` | load a named preset, append the scene |
| *"really imgen, {prompt}"* | the spoken form — the dictation pipeline prefixes `/imgen` |

`-a` takes the number rather than defaulting to the most recent, for two reasons: an optional-argument `-a` swallows the prompt as its own value, and "the most recent" is exactly the implicit choice this flag pair exists to remove. A wrong number lists every shoot that does exist.

The spoken trigger is the two-word phrase **`really imgen`**. `imgen` says "im-jen".

## Where output lands

Everything goes to **[[IMGEN]]** at `~/ob/kmr/Log/IMGEN/`, alongside [[VOX]] — one anchor, no scratch tier. The naming and folder rules are the anchor's, and they live in that page's `# BRIEF`; read it before changing how this script writes. In short:

| Thing | Form |
|---|---|
| A shoot | `IMGEN{nnn} — {what it was about}/` — one sitting; number sorts and is permanent, title reads |
| A roll | `IMGEN{nnn}-{prompt}{variant}.png` — `IMGEN002-4B` is shoot 2, prompt 4, roll B |
| The record | the shoot's namesake page — prompt groups newest first, prompt as plain text under its images |
| The index | [[IMGEN Gallery]] — one image per shoot, newest first |

**A new shoot writes in three places** and the script does all three: the shoot folder and its page, a member row in the [[IMGEN]] masthead, and an entry at the top of [[IMGEN Gallery]]. Adding to an existing shoot touches only the shoot page.

## Backends

| Backend | Model | Cost | Use for |
|---|---|---|---|
| `fal` (default) | FLUX.1 [dev] via fal.run | $0.025/image | photoreal and illustration; the quality default |
| `recraft` | Recraft V4 | $0.08 SVG | vector output — logos, icons, anything to be edited afterward |
| `local` | Draw Things on-device | free | offline, private; anything that should not leave the machine |

Only `fal` is wired today. `recraft` and `local` are declared seams, not implementations — adding one means a new entry in `BACKENDS` in the script.

## The disciplines

- **The prompt is written with the image, in the same action.** Not afterwards, not by the agent remembering to. For a generated image the prompt *is* the source, and [[feedback_figure_source_alongside_output]] applies exactly as it does to a `.d2` beside an `.svg`. It goes down as a plain paragraph — no heading, no blockquote, no fence — so it copies clean. [[IMGEN001 — Lumen portrait]] is the cautionary example: real images, prompts gone, unrecoverable.
- **Cost is stated, never silent.** Every run prints rolls written and dollars spent. A run costing more than `--confirm-over` (default $1.00) refuses without `--yes`, so a fan-out cannot quietly burn real money.
- **Presets lock a character.** Once a look is right, save it (`--save-preset tink`) and later runs reload the locked prompt with only the scene varying. This is what keeps a recurring character recognizably itself instead of drifting every generation.
- **Never place an image into [[IMGEN]] by hand.** Copying a file in gives you a picture with no prompt, and the prompt cannot be recovered afterwards. If images already exist somewhere else and belong in the anchor, moving them in means writing their prompt group by hand in the same pass — or knowingly leaving orphans, which is what [[IMGEN001 — Lumen portrait]] is.

## Script

| Script | Usage |
|---|---|
| `imgen-gen.py` | `python3 ~/.claude/skills/imgen/imgen-gen.py (-n "{title}" \| -a {N} \| -l) "{prompt}" [-r 4] [-c "{caption}"] [-b fal] [-p {preset}] [--save-preset {name}] [--dry-run]` |

`--dry-run` resolves the shoot and prints the filenames it would write without calling the API — use it to check where a roll is about to land.

Credentials come from the login keychain, never a file on disk: `security find-generic-password -s FAL_KEY -w`. A missing key fails loudly with the command to add it — no silent fallback.

## Dispatch

On invocation:
1. Parse the argument for a leading backend or preset name; everything after it is the prompt.
2. **Pick the shoot, and say which one you picked.** If the user is asking for something new — a new subject, a fresh idea, or just "make me an image" with no reference to earlier work — open a new shoot with `-n "{topic}"`, deriving the topic from what they asked for (three or four words: *Rooftop concepts*, *Scout portrait*, *Kitchen ideas*). If they are reacting to images from this conversation — *"darker"*, *"try it at night"*, *"one more like the third"* — that is `-a {N}` on the shoot those images came from. **When genuinely unsure, open a new shoot**: an extra folder costs nothing and can be merged later, whereas rolls added to the wrong shoot are mixed into someone else's record.
3. Run `imgen-gen.py`. Use `-l` if you need the number and do not have it, and `--dry-run` if you want to confirm the destination before spending. Neither costs anything.
4. Show the images: `open "{path}"` on each roll written. Never describe an image the user has not been shown.
5. Report the cost line as printed, and name the shoot the rolls landed in so the user can ask for more of the same.
