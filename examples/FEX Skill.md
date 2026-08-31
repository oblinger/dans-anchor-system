---
name: snap
description: "canonical skill exemplar"
user_invocable: true
---

| -[[FEX Skill]]- | : canonical skill exemplar<br>→ [[DAS]] → [[FEX]] → [FEX Skill](hook://p/FEX%20Skill)  |
| --- | --- |
| Related | [[FEX Facet\|Facet]],  [[FEX Dispatch Examples\|Dispatch Examples]],   |
| [[DAS Skill]]  | the skill facet |
| ... | [[_{{DISK_LABEL}} Template]],  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template]],  [[BRDG]],  [[Clarifier]],  [[CSE]],  [[DAS US-CAE-1 — Schedule a Task]],  [[DAS US-CAE-2 — Monitor Task Status]],  [[DAS US-CAE-3 — Retry Failed Tasks]],  [[DVT]],  [[ESP]],  [[Espresso]],  [[FEX Agenda\|Agenda]],  [[FEX API\|API]],  [[FEX API Design\|API Design]],  [[FEX Architecture\|Architecture]],  [[FEX At Entity\|At Entity]],  [[FEX Claude\|Claude]],  [[FEX Completed Roadmap\|Completed Roadmap]],  [[FEX CSE\|CSE]],  [[FEX Decisions\|Decisions]],  [[FEX Decisions Details\|Decisions Details]],  [[FEX Empty\|Empty]],  [[FEX Figure Page\|Figure Page]],  [[FEX Files\|Files]],  [[FEX Icebox\|Icebox]],  [[FEX Inbox\|Inbox]],  [[FEX Minimal Facet\|Minimal Facet]],  [[FEX Minimal Skill\|Minimal Skill]],  [[FEX Project Root\|Project Root]],  [[FEX Repo\|Repo]],  [[FEX Roadmap\|Roadmap]],  [[FEX Rules\|Rules]],  [[FEX Scheduler\|Scheduler]],  [[FEX Spine Examples\|Spine Examples]],  [[FEX Stories\|Stories]],  [[FEX System Design\|System Design]],  [[Forum Stories]],  [[Harbor Account Northwind]],  [[Harbor Integrations]],  [[Harbor Latency Budget]],  [[Harbor Releases]],  [[Harbor Tenancy Model]],  [[Harbor Upgrade Guide]],  [[HBR]],  [[HBR PRD User Stories]],  [[HHOP]],  [[HRUN]],  [[HWP]],  [[Knots]],  [[Mini]],  [[Snap]],  [[Viz Bench]],   |

# Snap — capture + file a screenshot
Grab a screenshot, name it from its content, file it under `~/notes/log/snap/`.

> **Canonical skill exemplar.** This *is* the `SKILL.md` template every skill follows. Note: (1) **frontmatter** carries the `name` (= folder = slash command) and the front-loaded `description` (the always-loaded surface — first sentence is what it does, then *when* to invoke); (2) **H1** = `<command> — <plain gloss>`; (3) a **one-liner**; (4) a small **masthead** (just `Related`); (5) the **body** is the runbook. Worked content: a hypothetical `snap` skill.

## When to Use

- User types `/snap` or says "snap this", "grab a screenshot", "capture the screen".
- Slash-only if the bare word is too common; here `snap` is distinctive enough to be a spoken trigger.
- **Not** for screen *recording* (video) — that's out of scope.

## Runbook

### 1. Capture

```bash
mkdir -p ~/notes/log/snap
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
- The skill facet it conforms to: [[DAS Skill]].
