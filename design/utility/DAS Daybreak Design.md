---
description: "design surface for the Daybreak morning routine"
---
# DAS Daybreak Design
How the morning routine is built — read order, the watermark, the authority model, and the reasoning behind each.

| -[[DAS Daybreak Design]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [design](hook://design) → [DAS Daybreak Design](hook://p/DAS%20Daybreak%20Design)<br>: design surface for the Daybreak morning routine |
| --- | --- |
| Related | [[DAS Daybreak PRD\|PRD]],  [[DAS Daybreak]] (user docs),  [[skills/daybreak/SKILL.md\|SKILL]],  [[MUSE]],  [[Luna]], |

## Shape

Daybreak is a **skill, not a daemon**. It runs when invoked, reads, decides, prints, and stops. No background process, no scheduler, no state beyond one timestamp.

That is deliberate. A daemon would have to decide *when* to interrupt, and interrupting well is a much harder problem than summarizing well. Making it user-invoked means the user chooses the moment they have attention to spend, which is exactly when a briefing is worth reading. The cost — Daybreak only knows what the user is doing when they ask — is acceptable for a once-a-day ritual.

## Read order and why

Ordered cheapest-and-most-decisive first, so an interrupted run still produced value.

| # | Source | Why here |
| --- | --- | --- |
| 1 | Watch messages ([[MUSE]]) | Deliberately spoken; highest signal per byte in the whole sweep |
| 2 | `~/ob/kmr/Q.md` | One file, already federates every anchor. Best value-per-read in the vault |
| 3 | Calendar | Time-bound — the only source where being late is failure |
| 4 | Watched mail | External and unpollable, but noisier than calendar |
| 5 | [[Rocks]] | The user's own declaration of what is hot |
| 6 | [[Quick]] | Capture inbox; overlaps (1) since MUSE writes here too |
| 7 | Luna backlog | Luna's own `## Now` |

Watch messages lead because they are the one channel where the user has already done the work of deciding something matters. `Q.md` is second because it is a single file that already aggregates every anchor — the highest-leverage read available.

Everything else in [[LST]] is read on demand. Sweeping the list tree every morning would be slow and would surface standing content that has not changed, which is noise.

## The watermark

**The central mechanism, and the one place a naive implementation fails.**

MUSE stamps `state: unreviewed` at ingest. It reads like a review marker. It is not — **nothing ever clears it.** Verified 2026-07-20: all 47 non-suppressed items in the archive still carry `unreviewed`, including pipeline tests from the July 13 bring-up. An implementation that filtered on that field would surface the entire archive every single morning, forever.

So Daybreak keeps its own high-water mark at `Luna Track/Daybreak Watermark.md` — a single ISO timestamp. Items with `captured:` newer than it are unseen. Items whose `state:` begins with `suppressed-` are skipped entirely; MUSE already judged those noise (too few words, or too low a words-per-second ratio).

Three properties matter:

- **Advance at end-of-run only.** If a run is interrupted, the watermark is unchanged and every item it would have covered is still pending. Advancing incrementally would lose items on any crash.
- **Advance to the newest item actually surfaced**, not to "now". Anything that arrives mid-run is caught next time rather than skipped.
- **Advancing is not remembering.** This is the sharp edge. The watermark records *seen*, not *handled*. An item discussed and deferred is past the watermark and will never resurface — so it must be written somewhere durable (backlog row, [[Quick]] line, list entry) *before* the mark moves. Anything else is a silent loss, and silent losses are exactly what the [[DAS Daybreak PRD|PRD]] exists to prevent.

**Why not flip MUSE's field instead?** Because [[MUSE]] owns its archive, and `/muse do` is its designated reviewer. If Daybreak also wrote that field, two consumers would fight over one flag with no way to tell which had acted. A Luna-side watermark keeps the ownership boundary clean and costs one small file.

## Authority model

Decided at [[F002 — Morning ritual — calendar, mail, and addressed MUSE intake|Luna F002]]-Q2. The boundary is **recoverability**, not identity:

- **In-vault and reversible → act unconfirmed.** The vault is git-backed. A wrong list entry costs one revert.
- **Outward-facing or destructive → confirm.** Mail, messages, purchases, invites to others, deletions, pushes. No undo exists.

The threat model is specific and worth stating plainly. Anyone holding the watch while it is unlocked can dictate a message; the watch re-locks off-wrist and needs a passcode, so the barrier is real, but it is **physical possession, not identity**. Once ingested, a message from someone else is byte-identical to a genuine one. Nothing in the transcript distinguishes them.

Gating on recoverability rather than on authenticity is the right call because authenticity is *unknowable* here — there is no signal to check — while recoverability is a property of the action itself and always knowable. "The watch was on his wrist" is not an authorization anyone would accept after a sent email.

**Confirmation is conversational and deferred to the morning** (user refinement, 2026-07-20), not a block at capture time. Blocking at capture would defeat the channel: the whole value of speaking into a watch is that it costs nothing in the moment.

**The time-sensitive exception** keeps that from becoming dogma. If waiting until morning defeats the purpose, having it already done was the point. So the operative rule is *ask unless the cost of asking exceeds the cost of being wrong* — and an outward action that expires overnight gets flagged as urgent in the briefing rather than silently deferred.

## Output shape

Three blocks, capped: decisions (≤3), Today (3–5, across domains), runnable-now.

Caps are the product. An uncapped briefing is a dump, and a dump already exists — it is called `Q.md`. The value Daybreak adds is *selection*, and selection that does not exclude is not selection.

The no-opening-report rule follows from the same place: a status summary spends the user's freshest attention on information that requires no action.

## Degradation

Any channel may be unavailable — the MCP server down, no network, an empty watchlist. In every case Daybreak **continues and names the gap.**

Never silently omit. The user calibrates trust on completeness; a briefing that quietly dropped the calendar teaches them that the briefing might always be dropping something, and that suspicion never fully goes away. Saying "calendar unreachable" costs one line and preserves the calibration.

## Open threads

- **Selection rule is provisional** until `Luna Prioritization.md` lands ([[F001 — Luna onboarding and charter capture|Luna F001]]-Q4). Current heuristic: max two per domain, [[Rocks]] outranks backlog, one Health item, prefer unblockers. The PRD names the counter-signal that should correct it — if the user routinely acts on something Daybreak did not surface, the rule is wrong.
- **Addressing detection** is not built. Until [[MUSE]] stamps `addressed: luna`, Daybreak reads all non-suppressed items past the watermark. Noisier, but zero new dependencies and shippable today.
- **Live delivery** is [[F003 — Live watch-to-session channel — speak to Luna from the wrist|Luna F003]]. Note the shared hazard: if an item can arrive both live and via the morning sweep, both paths must consult the same watermark or it gets acted on twice.
