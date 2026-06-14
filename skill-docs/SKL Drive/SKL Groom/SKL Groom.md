---
description: "Walk the current anchor's backlog and move it toward the **groomed state** — promote every item it can to **Ready**, park items that need user input in dated feature docs, repair link integrity."
---
# /Groom
Walk the current anchor's backlog and move it toward the **groomed state** — promote every item it can to **Ready**, park items that need user input in dated feature docs, repair link integrity. Convergent: safe to call anytime; never interrupts you mid-run.

| -[[SKL Groom]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Drive]] → [SKL Groom](hook://p/SKL%20Groom)<br>: the `/groom` skill |
| --- | --- |
| Related | [[skills/groom/SKILL.md\|SKILL]],   |
| [[SKL Groom Design\|Design]] |  |

DMUX trigger: **`groom`** (prefix-trigger; whatever you dictate after becomes the argument). Slash invocation: `/groom`, `/groom roadmap`, `/groom milestone {N}`, `/groom F{n}`.


## What "Ready" means

> An item is *Ready* when the agent believes it knows how to do this task without further involvement of the user.

Sharper than "questions resolved." If the task still hides any "wait, what about X?" that you'd have to answer, it's **not** Ready — it's *blocked on questions*, and the work belongs in a feature doc until those questions resolve.


## How it works

For each Unset / Upcoming backlog item, the agent investigates quietly: reads related docs, infers from context, drafts a spec, runs lightweight planning. Then decides:

- **Bullet is Ready as-is** → moves it to `## Ready`.
- **Has questions** → creates a dated feature doc in `Features/`, captures the questions there, replaces the backlog bullet with a `→ [[Feature Doc]]` link. Item is now *blocked-on-questions*.

The agent **never interrupts you mid-run**. Every question gets a home — feature doc by default, or one final inline question at the very end of the run (after the roster, pinned to the bottom of the screen so it survives scrolling).


## End of run

1. Summary table — what was promoted, what was parked, what was skipped.
2. **Open the first blocked-on-questions feature doc** so you have one concrete next action: answer those questions.
3. Run `/roster` to show the post-`/groom` state of the backlog.
4. *If* there's a single trivial deferred question, ask it now (last line of output).

After you answer the questions in the surfaced doc, re-run `/groom` to advance the next round.


## Scope arguments

| Invocation | Scope |
| --- | --- |
| `/groom` | All Unset / Upcoming items across the whole backlog. Default. |
| `/groom upcoming` | Only `## Upcoming`. |
| `/groom legwork` | Only `## Legwork`. |
| `/groom roadmap` | Roadmap's next milestone instead of the backlog. |
| `/groom roadmap <milestone>` | Named roadmap milestone. |
| `/groom <Q-number>` | Single backlog item. |
| `/groom <item name>` | Single item by name match. |


## Idempotence

Safe to run repeatedly. Items already Ready, Active, blocked-on-questions, Verify, Done, or in Legwork are skipped. Running twice with no new info should produce no diff on the second pass.


## Design principle

`/groom` follows the **Minimize User Back-and-Forth** principle from [[CAB Backlog]]: every batch operation against the backlog processes the entire batch autonomously before involving the user, then surfaces the first blocked doc as the user's single next action. Each round-trip costs scrollback context and stalls the batch — design for *one* round-trip per pass, not N.
