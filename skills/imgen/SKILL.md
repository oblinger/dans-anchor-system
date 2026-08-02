---
name: imgen
description: >
  Generate and edit images into the IMGEN anchor — each sitting is a numbered
  roll whose page carries one pending "Next render" plus every batch it has
  already produced, prompt recorded beside the images it made. Text-to-image
  (flux-dev) and instruction editing (flux-kontext) are wired; visible per-call
  cost; a pick pins the keeper. Use when the user says "/imgen", "really imgen",
  or asks for a picture to be generated or edited. Not for authored diagrams —
  that is /viz.
user_invocable: true
---

# imgen — generated imagery
Generate an image from a prompt, or edit one you already have, into the anchor that keeps the prompt with it — and state the cost.

`/imgen` is the **generative** counterpart to [[skills/viz/SKILL.md|/viz]]. `/viz` renders artifacts you specify exactly (excalidraw, D2, matplotlib) and its output is re-derivable from its source; `/imgen` asks a model to invent one, so the same prompt twice gives different pictures. A generated image cannot be re-derived — only re-rolled — which is why the prompt has to be captured at the moment of writing rather than reconstructed later, and why the skill shares its name with the folder its output lives in.

## The two nouns

| Noun | What it is | Named |
|---|---|---|
| **roll** | one sitting — a folder plus its namesake page, holding everything about one subject | `IMGEN{nnn} — {title}/` |
| **image** | one picture inside a roll | `IMGEN{nnn}-{batch}{variant}.png` — `IMGEN004-6E` is roll 4, batch 6, image E |
| **batch** | the images one command produced, recorded with the exact prompt that made them | `## Batch {n}` on the roll page |

## The roll page is the interface

Everything about a roll lives on its page, in this order under the H1:

- **`## Pick`** — the chosen keeper, shown large (2000px). Optional; set by `pick`.
- **`## Next render`** — the **one pending operation**: an `#### {command}` H4 followed by the prompt. This is the editable surface — change it and the next `render` does the new thing.
- **`## Batch {n}` …** — everything already rendered, newest first. Each is a heading, then the image grid, then the `####` command and prompt that produced it.

The command **sticks**. After any run, `Next render` holds whatever just ran — so a bare `render` repeats it, and repeating an unchanged command **appends to the existing batch** rather than opening a new one ("three more of the same" stays one section). Giving `render` a fresh prompt resets the command to a `create`.

A command line names the verb, the model, and (for edits) the source image:

    create flux-dev
    edit flux-kontext 6E

## Invocation

    imgen new    {roll} {prompt}        open a new roll, seed its Next render
    imgen get    {roll}                 print the Next render — command and prompt, separately
    imgen update {roll} [--command C] [--prompt P]    rewrite the Next render; renders nothing
    imgen render {roll} [prompt] [-n N] run the Next render N times (a prompt resets it to create)
    imgen edit   {roll} {image} {instruction} [-n N]  instruction-edit an image (flux-kontext)
    imgen pick   {roll} {image}         pin the keeper — top of the page + gallery cover; free
    imgen list   [roll]                 rolls with their numbers, or the images in one roll

`{roll}` takes the number (`4`, `004`) **or** a substring of the title (`scout`). Spend verbs also take `-s/--size` (default `square_hd`), `--confirm-over` (default $1.00), `--yes`, and `--dry-run`.

The spoken trigger is the two-word phrase **`really imgen`** — the dictation pipeline prefixes `/imgen`. `imgen` says "im-jen".

## Where output lands

Everything goes to **[[IMGEN]]** at `~/ob/kmr/Log/IMGEN/`, alongside [[VOX]] — one anchor, no scratch tier. The naming and folder rules are the anchor's and live in that page's `# BRIEF`; read it before changing how this script writes.

**A new roll writes in three places** and `new` does all three: the roll folder and its page, a member row in the [[IMGEN]] masthead, and an entry at the top of [[IMGEN Gallery]] (added on the roll's first successful render, using its first image as the cover). Rendering into an existing roll touches only that roll's page.

A roll page is a **regular file, so its head is a `:>>` breadcrumb, not a dispatch table** — only anchor pages ([[IMGEN]] itself) get tables.

## Backends

| Model | Verb | Cost | What it does |
|---|---|---|---|
| `flux-dev` | `create` | $0.025/image | text → image. The quality default for a fresh picture. |
| `flux-kontext` | `edit` | $0.040/image | image + instruction → image. Changes what you name and holds the rest — face, style, composition. |

Both run on fal.run. The source image is sent **inline as a base64 data URI**, so editing needs no upload step and works on a file that has never left the machine. Vector output (Recraft) and on-device generation (Draw Things) are declared seams, not implementations — adding one means a new entry in `BACKENDS` in the script.

**Editing is instruction-based, not region-based.** You say *what to change* in words; there is no mask. Masked inpainting (FLUX Fill) would need a mask image and a way to paint it — deferred deliberately, not forgotten.

## The disciplines

- **The prompt is written with the image, in the same action.** Not afterwards, not by the agent remembering to. For a generated image the prompt *is* the source, and [[feedback_figure_source_alongside_output]] applies exactly as it does to a `.d2` beside an `.svg`. The script guarantees this — a batch is only written together with the command and prompt that made it. [[IMGEN001 — Lumen portrait]] is the cautionary example: real images, prompts gone, unrecoverable.
- **By default the prompt goes down as a sequence of bullets** — a short lead line naming medium + subject, then one attribute per bullet (dress, hair, expression, setting, style). Bullets make the prompt a **mix-and-match kit**: swap or re-roll a single attribute without rewriting the whole thing. Keep the lead line dash-free so a leading `-` is not read as a CLI flag.
- **Never rewrite a past batch's prompt.** A batch records what actually produced those images. A revised wording is the *next* render, not a correction of the last one — put it in `## Next render` and run it.
- **Cost is stated, never silent.** Every run prints the images written and the dollars spent. A run over `--confirm-over` (default $1.00) refuses without `--yes`, so a fan-out cannot quietly burn real money.
- **A pick pins the keeper.** `pick {roll} {image}` lifts it to a `## Pick` block at the top of the page, shown at 2000px, and repoints the [[IMGEN Gallery]] cover. No API call, no cost, changeable any time — re-pick and both surfaces update. New batches still land below the pick, so the keeper stays pinned as the roll grows.
- **Never place an image into [[IMGEN]] by hand.** Copying a file in gives you a picture with no prompt, and the prompt cannot be recovered afterwards. If images already exist elsewhere and belong here, moving them in means writing their batch by hand in the same pass — or knowingly leaving orphans, which is what [[IMGEN001 — Lumen portrait]] is.

## Script

| Script | Usage |
|---|---|
| `imgen-gen.py` | `python3 ~/.claude/skills/imgen/imgen-gen.py {verb} …` — see § Invocation |

All logic lives in the script; this file is dispatch and discipline only. `--dry-run` resolves the roll and prints the batch, filenames, and cost it *would* write without calling the API — use it to confirm where images are about to land. Credentials come from the login keychain, never a file on disk: `security find-generic-password -s FAL_KEY -w`. A missing key fails loudly with the command to add it — no silent fallback.

## Dispatch

On invocation:

1. **Pick the roll, and say which one you picked.** Something new — a new subject, a fresh idea, "make me an image" with no reference to earlier work — is `new "{topic}"`, deriving a three-or-four-word topic (*Rooftop concepts*, *Scout portrait*, *Kitchen ideas*). A reaction to images from this conversation — *"darker"*, *"try it at night"*, *"one more like the third"* — is `render {roll}` on the roll those images came from. **When genuinely unsure, open a new roll**: an extra folder costs nothing and can be merged later, whereas images added to the wrong roll are mixed into someone else's record.
2. **Decide create vs edit.** A different picture of the same idea is `render` (re-roll the prompt). A change to *this specific image* — keeping the face, the style, the composition — is `edit {roll} {image} "{instruction}"`. When the user points at one image and asks for a change to it, that is `edit`.
3. **Write the prompt as bullets** (§ The disciplines) unless the user asked otherwise.
4. Run the script. `list` gets you the number if you do not have it; `--dry-run` confirms the destination. Neither costs anything.
5. **Show the images**: `open "{path}"` on each one written. Never describe an image the user has not been shown.
6. Report the cost line as printed, and name the roll so the user can ask for more of the same.
7. **When the user picks a keeper**, run `pick {roll} {image}` — then, for a recurring character, write the settled appearance bullets into that character's persona doc.
