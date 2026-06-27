---
name: snap
description: "Canonical skill exemplar (SKILL.md). Capture a screenshot, file it with a generated title, and drop a transcribed note beside it. Use when the user says '/snap', 'grab a screenshot', 'snap this'. Roll this structure out to all skills."
user_invocable: true
---

# Snap — capture + file a screenshot
Grab a screenshot, name it from its content, file it under `~/ob/kmr/Log/SNAP/`.

| -[[CAE Skill]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[CAE]] → [CAE Skill](hook://p/CAE%20Skill)<br>: canonical skill exemplar |
| --- | --- |
| Related | [[CAE Facet]],  [[FCT Skill]] (the skill facet),  [[CAE Dispatch Examples]] |

> **Canonical skill exemplar.** This *is* the `SKILL.md` template every skill follows. Note: (1) **frontmatter** carries the `name` (= folder = slash command) and the front-loaded `description` (the always-loaded surface — first sentence is what it does, then *when* to invoke); (2) **H1** = `<command> — <plain gloss>`; (3) a **one-liner**; (4) a small **masthead** (just `Related`); (5) the **body** is the runbook. Worked content: a hypothetical `snap` skill.

## When to Use

- User types `/snap` or says "snap this", "grab a screenshot", "capture the screen".
- Slash-only if the bare word is too common; here `snap` is distinctive enough to be a spoken trigger.
- **Not** for screen *recording* (video) — that's out of scope.

## Runbook

### 1. Capture

```bash
mkdir -p ~/ob/kmr/Log/SNAP
screencapture -i /tmp/snap.png      # interactive region select
```

### 2. Title from content

Read `/tmp/snap.png`; generate a 3–5 word content-bearing slug (skip filler), e.g. `dashboard-error-spike`. Same discipline as `[[snip]]`.

### 3. File + sidecar note

```bash
ts=$(date +%F)
mv /tmp/snap.png "$HOME/ob/kmr/Log/SNAP/$ts — <slug>.png"
```

Write a `<same-stem>.md` sidecar with a one-line caption + any OCR'd text, and `open` the folder so the user verifies.

## Anti-patterns

- Don't capture the whole screen when the user gestured at one window — prefer interactive/region select.
- Don't invent a title from filler ("screenshot", "image") — name what the shot is *about*.

## Related

- Sibling capture skills: [[snip]] (text), [[vox]] (audio).
- The skill facet it conforms to: [[FCT Skill]].
