---
description: "execution state for the Warden engine — feature specs and the exception register; the work itself is queued as TINK rows, never here"
---

| -[[Warden Track]]- | → [[DAS]] → [[Warden]] → [Warden Track](hook://p/Warden%20Track)  |
| --- | --- |
| [[Warden Features]]  | feature specs |
| ... | [[Design-Rules Catalog Proposal]],  [[Warden Audit 2026-07-12]],  [[Warden Dev Ruleset]],  [[Warden Exceptions]],  [[Warden Inbox]],  [[Warden Messages]],  [[Warden queries]],   |

# Warden Track
Execution state for the Warden engine — feature specs, the exception register, and the inbox. **There is no Warden backlog and there must not be one.**

## Warden has no queue of its own — and its inbox is the half that bites

**Ruled by Dan twice, 2026-08-11 and again 2026-08-28.** Warden's work is [[TINK|Tink]]'s work and always has been, so a second queue only split the view of what is live: *"You're the only person really working that backlog, and I think it really can cause things to get gummed up when there's this other backlog out there."* File Warden work as a **TINK** row.

`Warden Backlog.md` was retired 2026-08-11 and **deleted 2026-08-28**, once the file was confirmed to hold 53 rows of which every one was `[Done]`. Its only irreplaceable content was the id map below: the twelve open rows were re-minted under TINK numbers because every old id collided with an existing TINK row, so none could carry its number across.

| was | is |
|---|---|
| `WARD F236` | [[Tink Backlog#^F321\|F321]] |
| `WARD F237` | [[Tink Backlog#^F322\|F322]] |
| `WARD F230` | [[Tink Backlog#^F323\|F323]] |
| `WARD F234` | [[Tink Backlog#^F324\|F324]] |
| `WARD T002` | [[Tink Backlog#^T354\|T354]] |
| `WARD T014` | [[Tink Backlog#^T355\|T355]] |
| `WARD T016` | [[Tink Backlog#^T356\|T356]] |
| `WARD T009` | [[Tink Backlog#^T357\|T357]] |
| `WARD T018` | [[Tink Backlog#^T358\|T358]] |
| `WARD T019` | [[Tink Backlog#^T375\|T375]] |
| `WARD T022` | [[Tink Backlog#^T376\|T376]] |
| `WARD T020` | [[Tink Backlog#^T536\|T536]] |

**Removing the backlog did not remove the trap, and the inbox is what bit.** An anchor with no session still *receives*. [[Warden Inbox]] held **six undrained drops on 2026-08-28, the oldest 17 days old** — and one of them, a still-live fixer that destroys wiki-links, had grown from 14 at-risk files to 27 while it sat. Nothing surfaced it, because a backlog banner counts rows and an inbox is not rows. Drained into TINK as [[Tink Backlog#^T604\|T604]]–[[Tink Backlog#^T608\|T608]].

**The intended fix is a sweep, not a warning — ruled by Dan, 2026-08-28.** *"I don't think an inbox should exist on Warden. It shouldn't be able to be created… If you find a track folder, migrate it over to the owning agent, that way anybody can put it there. It's just gonna get swept."* So anyone may drop anywhere and the machine relocates it, rather than the sender being refused or a stale mailbox being reported: an aged-inbox warning treats the symptom, and the mailbox should not be here at all. That needs an anchor to declare **who runs it**, which nothing does today — parked as [[Tink P0022]], with one measured trap the design must not miss: `Warden Exceptions.md` sits in this folder and its path is load-bearing, so a blind sweep would silently drop 8 graded suppressions. Until then, **drain anything that lands here into TINK by hand**.
