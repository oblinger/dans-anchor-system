# /ready

Walk the current anchor's backlog and promote every item it can to **Ready**. Items it can't ready autonomously get parked in dated feature docs with their open questions captured. Never interrupts you mid-run.

DMUX trigger: **`make ready`** (two words). Slash invocation: `/ready`.


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
3. Run `/roster` to show the post-`/ready` state of the backlog.
4. *If* there's a single trivial deferred question, ask it now (last line of output).

After you answer the questions in the surfaced doc, re-run `/ready` to advance the next round.


## Scope arguments

| Invocation | Scope |
| --- | --- |
| `/ready` | All Unset / Upcoming items across the whole backlog. Default. |
| `/ready upcoming` | Only `## Upcoming`. |
| `/ready legwork` | Only `## Legwork`. |
| `/ready roadmap` | Roadmap's next milestone instead of the backlog. |
| `/ready roadmap <milestone>` | Named roadmap milestone. |
| `/ready <Q-number>` | Single backlog item. |
| `/ready <item name>` | Single item by name match. |


## Idempotence

Safe to run repeatedly. Items already Ready, In Progress, blocked-on-questions, Testing, Completed, or in Legwork are skipped. Running twice with no new info should produce no diff on the second pass.


## Design principle

`/ready` follows the **Minimize User Back-and-Forth** principle from [[CAB Backlog]]: every batch operation against the backlog processes the entire batch autonomously before involving the user, then surfaces the first blocked doc as the user's single next action. Each round-trip costs scrollback context and stalls the batch — design for *one* round-trip per pass, not N.
