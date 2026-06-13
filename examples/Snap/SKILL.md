---
name: snap
description: "Capture a screenshot, file it with a generated title, and drop a transcribed note beside it. Use when the user says '/snap', 'grab a screenshot', 'snap this'."
user_invocable: true
---

# Snap — capture + file a screenshot
Grab a screenshot, name it from its content, file it under `~/ob/kmr/Log/SNAP/`.

| -[[Snapper Dapper]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [Snap](hook://p/Snap)<br>: example skill anchor — a `SKILL.md` |
| --- | --- |
| Related | [[Clarifier]] (example project),  [[FCT Skill]] (the skill facet),  [[FEX]] |

## When to Use

- User types `/snap` or says "snap this", "grab a screenshot", "capture the screen".
- **Not** for screen *recording* (video) — that's out of scope.

## Runbook

### 1. Capture

```bash
mkdir -p ~/ob/kmr/Log/SNAP
screencapture -i /tmp/snap.png      # interactive region select
```

### 2. Title from content

Read `/tmp/snap.png`; generate a 3–5 word content-bearing slug (skip filler), e.g. `dashboard-error-spike`.

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
