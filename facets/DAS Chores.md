---
description: "the chores facet — {slug} Chores.md, the standing file of sub-surface agent work the human is neither aware of nor interested in; present when needed, empty or absent otherwise"
group: file
---

| -[[DAS Chores]]- | → [[DAS]] → [[FCT]] → [DAS Chores](hook://p/DAS%20Chores)  |
| --- | --- |
| Related | [[DAS Backlog]],  [[DAS Query]],  [[DAS Audit]],  [[DAS Track]],   |
| Examples | [[TINK Chores\|first instance]] (minted with the F332 QFix extraction) |
| Rules | [[R-chores]],   |

# DAS Chores
The anchor's sub-surface work queue — `{slug} Chores.md`, a flat bulleted list of mechanical items agents create, drain, and resolve **without the user's awareness or interest**.

**TLDR** — a **chore** is defined by its *audience*, not its source: the human is generally uninterested in, and unaware of, both its creation and its resolution. Chores flow beneath the surface of the anchor's real work — warden/audit findings to mend, render regressions, link repairs, machine hygiene — and the first population is what the retired `B-QFix` backlog row used to hold, but the boundary is the audience property, not "audit output." **The moment an item needs a user decision or a user check, it is not a chore**: promote it to a question in a doc (T-doc or feature doc) and delete it here. Chores never render to `queries.md`, `Q.md`, or any user-facing queue surface. **Cardinality: one** — at most one `{slug} Chores.md` per anchor, elective, created when first needed. Decided as [[TINK332 - Derived backlog and queries: link-lists, preambles, info boxes|TINK F332]] Q2, 2026-08-15.

**Once it exists it stays, even at zero chores** (Dan, 2026-08-18 — amends the original *"empty or absent otherwise; deleting an empty one is always legal"*). The audit clears its own `- **C…**` bullets and leaves the header standing. An anchor's facet instance that deletes itself the moment it empties cannot be found by anyone looking for it, and its disappearance reads as damage rather than as tidiness — which is exactly how it was reported. Note the failure mode this closes, because restoring the file by hand does **not** hold: deletion fired on the *C-bullets-to-zero transition*, not on emptiness, so a hand-restored empty file survived until the next chore landed and was fixed, then vanished again. TINK lost its `Chores.md` twice in one day that way. Enforced by `test-t144-qfix-lifecycle.py` case C.

## Location

`{slug} Track/{slug} Backlog/{slug} Chores.md` — inside the folder-form backlog ([[DAS Backlog]], F329), beside the T-docs: chores are backlog-shaped work, so they live with the backlog's own files. For an anchor whose backlog is still the flat file, the interim home is `{slug} Track/{slug} Chores.md`; it moves into the folder when the backlog does.

## Format

An H1 and one flat bulleted list — nothing else. Each bullet is a **self-contained instruction any agent can execute cold**: what to do, where, and how to tell it worked. No sub-bullet trees, no brackets, no Q-numbers, no horizons — an item too big or too contested for one bullet is not a chore. Agents append on discovery (audit `--fix` residue, warden mends, noticed breakage) and delete on completion; an empty list needs no ceremony.

## Draining

Chores are drained opportunistically — during `/crank` downtime, at the tail of related work, or by any agent passing through the anchor. There is no SLA and no aging alarm: nothing here is load-bearing for the user, by definition. An item that turns out to matter more than that gets promoted out (see the TLDR invariant) rather than prioritized in place.

## What is NOT a chore

- Anything the user must decide, judge, or verify — that is a question or a `[Verify]` item in a doc.
- Feature or design work of any size — that is an F/T row with its doc.
- Anything whose *absence* the user would notice — user-visible breakage is real backlog work.

## Audit

[[R-chores]] — location, flat-list format, and the no-user-facing-content invariant. All stated: the facet is new with one live instance; checkers wait for the population to show which invariants bind.

# BRIEF

- **What this is** — the sub-surface work file specified by [[TINK332 - Derived backlog and queries: link-lists, preambles, info boxes|TINK F332]] Q2. The audience property is the whole definition: if Dan would care, it does not belong here.
- **Never surface chores to the user.** Do not list them in `queries.md`, `Q.md`, status banners, or chat summaries of "what needs attention." Draining them silently is the designed behavior.
- **Promote, don't ask.** A chore that turns out to need a decision becomes a doc-hosted question via `state`; delete the bullet here in the same pass.
- **Supersedes B-QFix.** Audit's mechanical findings land here now; do not mint `B-QFix` backlog rows.
