---
description: "product requirements for the Daybreak morning routine"
---

| -[[DAS Daybreak PRD]]- | : product requirements for the Daybreak morning routine<br>→ [[DAS]] → [design](hook://design) → [DAS Daybreak PRD](hook://p/DAS%20Daybreak%20PRD)  |
| --- | --- |
| Related | [[DAS Daybreak Design\|Design]],  [[DAS Daybreak]] (user docs),  [[skills/daybreak/SKILL.md\|SKILL]], |

# DAS Daybreak PRD
Why the morning routine exists, who it serves, and what would make it fail.

## The problem

The user runs many agents. [[SONAR]] owns the job search, [[SV]] owns work, [[MUX]] and [[HA]] own their codebases. Each is competent inside its lane and blind outside it. Nothing owns the question *"across everything, what should I do today?"* — and that is the question a person actually wakes up with.

Two failure modes follow, and they are the ones Daybreak exists to prevent:

- **Silent drop.** Something arrives outside the vault — an appointment, a mail, a thought spoken into a watch on a walk — and no agent is watching that channel. It is not deprioritized; it is simply never seen.
- **Domain capture.** Whichever agent the user opens first sets the day's agenda. Work has the most surface area and the loudest backlog, so work wins by default. Health, which the user has written into every life-framing they have ever authored ([[Lumen Domains]]), loses by default.

## Who it serves

One user, once a day, in five to ten minutes, at the start of the day. That constraint is load-bearing and shapes everything below: **attention is the scarce resource, not agent time.** Daybreak may read for a minute if it means the user reads for ten seconds.

## What it must do

1. **Sweep every inbound channel** the user cannot be expected to poll themselves — watch dictation, calendar, watched mail — plus the vault surfaces that already federate ([[Q.md|Q]], [[Rocks]], [[Quick]], the backlog).
2. **Decide, then present.** Output a small ranked set, not a dump. The user's job is to answer, not to triage.
3. **Act within a stated authority boundary**, so that speaking a request into a watch is genuinely useful without being dangerous.
4. **Never lose a deferred item.** Something surfaced, discussed, and postponed must land somewhere durable before the run ends.

## What it must not do

- **Must not open with a report.** A status summary, an overnight-change count, or a recap of yesterday all fail the attention constraint. First line is a decision or the Today list.
- **Must not silently omit a channel.** If the calendar is unreachable, say so. A briefing that quietly dropped a source is worse than one that admits it — the user calibrates trust on completeness, and a silent gap poisons that calibration permanently.
- **Must not escalate.** An item declined three mornings running gets raised once, plainly, at the weekly review — never louder each day. Nagging trains dismissal, and a briefing the user dismisses reflexively has negative value.
- **Must not duplicate domain-agent tracking.** Work items live in their own anchors and reach Daybreak through `Q.md` federation, not by being copied into Lumen's backlog.
- **Must not invent the watchlist.** Mail filtering starts empty and earns entries from the user. An invented watchlist produces false positives on day one and teaches the user to skim past the mail section forever.

## Success criteria

**The user stops opening `Q.md` manually in the morning.** That is the honest behavioral test — it means the briefing is trusted enough to be the entry point.

Supporting signals: nothing on the calendar gets missed; watch messages get acted on within a day of being spoken; the Today list regularly contains an item from a domain the user would not have thought of unprompted.

**Counter-signal to watch for:** if the user routinely acts on something *other* than what Daybreak surfaced, the selection rule is wrong, not the user. Prioritization is provisional until [[F001 — Lumen onboarding and charter capture|Lumen F001]]-Q4 settles it, and this counter-signal is the evidence that should settle it.

## Constraints

- **Five to ten minutes**, including the user's reading and answering.
- **Three decisions maximum**, five Today items maximum. Caps are the product, not a limitation — an uncapped briefing is a dump, and a dump is what already exists.
- **Degrades rather than aborts.** Any single channel may be unavailable; the run continues and names the gap.
- **Idempotent within a day.** Re-running must not resurface handled items, and must not double-act.

## Non-goals for v1

- Live watch → session delivery. That is [[F003 — Live watch-to-session channel — speak to Lumen from the wrist|Lumen F003]]; the once-a-day sweep is the reliable floor it builds on.
- Automatic addressing detection in [[MUSE]]. Until it exists, Daybreak reads all non-suppressed items past the watermark — slightly noisier, zero new dependencies, and shippable today.
- Any evening or weekly counterpart. The weekly review is real but separate.
