---
description: STEN inbox — raw input dropped for later processing.
---

| -[[STEN Inbox]]- |  |
| --- | --- |
| --- | |
| [[STEN Backlog]]  |  |
| [[STEN Messages]]  | agent inbox — background-process messages for this anchor; append-only. See [[DAS Messages]]. |
| [[STEN queries]]  | STEN queries — mechanically rendered from the backlog (Blockers / Ready+Next / Questions / Blocked / User / Other), and copied verbatim into Q.md. Do not hand-edit; edit the backlog rows. |

# STEN Inbox
Drop zone for raw input; an entry with no status tag is pending, and draining writes `DONE` or `MOVED → {destination}` per [[DAS Inbox]].

## 2026-08-20 — AT Mail is a prose template awaiting Stencil — a candidate…

*from: tink · tag: note*

> **A migration target for whenever Stencil lands, filed so it is on the list rather than rediscovered.**
>
> [[AT Mail]] was created 2026-08-20 — the format for a drafted message inside an `@` entry's `# LOG` (four blocks, versioned, and a no-markdown rule on the note because it is pasted verbatim into a mail client). It is stated as **prose**, and it is a textbook case for what Stencil is for: the shape that scaffolds a mail entry and the shape that would check one are currently the same paragraphs, and the only way to enforce them today is to write a ruleset beside them — two statements of one shape.
>
> Dan explicitly deferred it, 2026-08-20: *"it's okay that AT may hold the template, but when we get Stencil in place we really want to actually use the Stencil template and not do that. We'll worry about that later."* So **no action is wanted now** — this is a pointer, not a request.
>
> **Why it is worth having on your side rather than only in mine.** The format has one invariant that is *invisible when violated* — the note carries no markdown, and you find out because the recipient sees `**Chuck,**` in their inbox. That is the class of rule that most wants a matcher rather than a reader, so `AT Mail` is a good early candidate when you are picking which prose templates to convert first: small, one live instance to test against ([[@David Chee]] § 2026-08-19), and a checkable rule that nothing checks today.
>
> I have put a note in `AT Mail` itself saying the destination is a stencil and that a hand-written ruleset is the wrong interim step, so nobody closes the gap the expensive way before you get there.
>
> From Tink, 2026-08-20.
