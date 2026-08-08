---
description: durable decisions for the DAS anchor itself — what this repo may contain and why
---

# DAS Decisions
Durable decisions about `dans-anchor-system` as a published artifact, with the reasoning that produced them.

### D1 — Examples are wholly invented; nothing in this repo is drawn from the author's vault

**Decision.** Every example, specimen, worked instance, and figure in this repository is **fabricated for the purpose**. No file here may be a copy of, an excerpt from, or a paraphrase of real content in the author's knowledge repository — not a real project's design document, not a real correspondent, not a real address, path, drive, employer, or project codename. This holds regardless of how instructive the real thing is.

**Why.** This repo is public and is authored from *inside* the private vault it describes, so the nearest available example is always a real one. That is not an occasional lapse; it is the default gradient of the arrangement, and it has produced four separate leaks:

- `examples/Audited/` held eleven genuine design documents lifted from live projects — a 38 KB test strategy, an 11 KB architectural-decisions record, and the product requirements for an application being commercially distributed.
- `design/Template Examples.md` quoted real correspondence **byte-exact and on purpose**, because the corpus existed to prove a matcher survives real-world mess. The privacy cost was never weighed against the repo being public.
- The `/io` and `/viz` skill docs carried live credential paths and real addresses, because they were written while doing real work.
- A facet cited a real interview target's plan page as its worked exemplar, simply because it was the nearest live instance of the right shape.

The unifying point is that **"it's a better example because it's real" is exactly the reasoning that has to be refused.** Realism is the temptation, not the justification. An invented example that demonstrates the same structure is worth more than a real one, because it can be published, edited, and extended freely, and because a stranger cloning this repo can read it without needing context they do not have.

**Consequences.**

- A real document may be *studied* to learn what shape a facet takes in practice, but what lands in the repo is a new document written from scratch to that shape. Renaming a real file is not fabrication.
- Examples do not need to be plausible-as-the-author's-work. The established cast is deliberately unrelated to anything real: Harbor (`HBR`), the Scheduler (`FEX`), Espresso, Knots, Snap, Clarifier, Mini, Viz Bench.
- Where a facet spec previously advertised "audited real-world range", it now cites invented instances only. Losing the real range is an accepted cost.
- Enforced mechanically by [[R-examples]]. The check is a floor, not a ceiling: it catches known markers, and a marker list is by construction narrower than the rule.
- Content already published cannot be unpublished by deletion alone — see [[DAS Stone Design]]'s sibling lesson about history. Removal from the working tree is the first step, not the whole remedy.

### D2 — `_NAME_` is reserved to the logical-drive vocabulary and must not be used for in-repo folders

**Decision.** No folder in this repository may be named `_NAME_` (leading and trailing underscore). That form is reserved.

**Why.** In the author's disk conventions, `_NAME_` means *a complete copy of logical drive NAME* — see Disk Conventions, "`_NAME_` — a **complete** copy of logical drive NAME". `_ARCHIVES_` in particular names a real ~120 GB logical drive holding backups of live `~/ob/` content, mastered on the 10T drive and mirrored to BLACK.

An agent nonetheless created `examples/_ARCHIVES_/` as an ad-hoc in-repo archive folder, which asserted a completeness it did not have and collided with a real drive name. The misreading then spread: `skills/workflow/scripts/state` added `"/_ARCHIVES_/"` to a skip-list beside `/.trash/` and `/Yore/`, which made the misuse look like an established convention to the next reader — and it did, to the point where a fix was drafted teaching HookAnchor to honor it. That fix would have blessed the error in the generator *and* blinded the tool to a genuine drive copy.

**Consequences.**

- In-repo archival goes to Yore, the vault's archive anchor, not to a folder inside the published tree. The commit that created `examples/_ARCHIVES_/` said "→ Yore" in its own message.
- Superseded examples are deleted rather than parked. Git history is the archive.
- The `state` skip-list entry is a residue of the misreading and should be removed when that file is next touched.
