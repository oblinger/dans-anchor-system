---
name: granularity
description: Discipline. The rule for how coarse or fine a capability/concept should be — when it lives as a subcomponent vs earns its own named unit vs spawns a grouping. Governed by the cost of the ALWAYS-LOADED surface: for skills, every top-level skill's name+description loads into every environment (subcommands are free until invoked); for facets, every facet's dispatch row carries context weight. Names the levels (subcommand → coarse skill → top-level skill → grouping; subsection → facet → folder-facet → grouping) and the two graduation triggers (coarsen-by-default; graduate-on-shared-shape or earned-independence). Cited by [[Access PRD]], [[SKA Design]], [[SKL]], and any facet/skill deciding where a new capability lands.
user_invocable: false
---

# Granularity Discipline

Granularity is *how coarse or fine a named unit should be.* Every capability or concept can be expressed at several grains — as a subcomponent of something larger, as its own named unit, or as a grouping over many units. This discipline says **which grain to pick, and when to graduate between grains** — driven by one economy: the cost of the **always-loaded surface**.

- **The cost is the always-loaded surface, not the depth behind it.** For **skills**: every *top-level* skill's `name` + `description` loads into the catalog in *every* environment — but a **subcommand** costs nothing until its parent is invoked. For **facets**: every facet that appears in a dispatch table carries context weight; a subsection of an existing facet does not.
- **Default coarse; graduate on evidence.** A new capability starts at the *finest* grain that's free (a subcommand; a subsection). It graduates to its own named unit only when it earns the slot.
- **Two graduation triggers** — (1) **shared shape**: when ≥2 fine-grained units share a real domain shape, promote them out into a coarse skill / named bucket (the *cull rule*); (2) **earned independence**: when one unit grows big or distinct enough to justify its own always-loaded slot, promote it to top-level.
- **The governing trade-off** is always-loaded cost vs. cohesion/discoverability. More top-level units = easier to discover, heavier catalog. Fewer = leaner catalog, detail hidden behind invocation. Pick the coarsest grain that still keeps each unit discoverable and coherent.

This is a discipline, not a user-invocable skill — facets and skills cite it via `[[granularity]]` when deciding where a new capability lands.

## Why this exists — the problem it solves

The skill catalog is loaded into context in **every** environment, all the time. If every fine-grained capability (read email, read calendar, read contacts, send a WhatsApp) becomes its own top-level skill, the always-loaded catalog bloats linearly — paying tokens in every session for capabilities used in almost none. The instinct to "just make a skill for it" is the failure mode. The fix is to recognize that **capability depth is free; catalog breadth is not** — so push depth behind a coarse entry point and keep the breadth small.

The same pressure exists for facets: a CAB dispatch table with 60 facets is harder to hold in context than one with 20 coarse facets each covering a family. The graduation logic is identical.

## The levels

### Skill axis

| Grain | Form | Always-loaded cost | Use when |
| --- | --- | --- | --- |
| **Subcommand** | `/io email`, `/bridge sync` | **0** (rides the parent) | a capability within a coherent family already owned by a coarse skill |
| **Coarse skill** | `io` (cloud docs), `bridge` (remote), a future `messaging` | **1** description | a *family* of related capabilities sharing a domain shape |
| **Top-level skill** | `bridge`, `ctrl` | **1** description | a capability big or distinct enough to earn its own slot |
| **Grouping** | the Access bucket | **0** in the runtime catalog (org-only) | an organizational category over several skills; lives in the design hierarchy, not the loaded catalog |

A **grouping** is org structure, not a runtime entry — it costs nothing in the always-loaded catalog. So `bridge` sits *in* the Access grouping but is its own top-level skill, **not** a subskill of anything. Don't create a skill whose name collides with a grouping (e.g. an `access` skill alongside an Access grouping) — two umbrellas-of-the-same-things is a discoverability tax.

### Facet axis (parallel)

| Grain | Form |
| --- | --- |
| **Subsection** | an H2 within an existing facet doc |
| **Own facet** | a `{NAME} <Facet>.md` with a dispatch row |
| **Folder-facet** | a facet that grew into a folder of docs |
| **Grouping** | a category of facets (e.g. the design-pipeline facets) |

## Graduation triggers

- **Coarsen by default (promote IN).** A new accessor/capability is a *subcommand* of the coarse skill owning its family — never a new top-level skill — until a trigger fires. Email is a subcommand of the messaging/io accessor, not its own skill.
- **Shared shape (the cull rule, promote OUT).** When ≥2 units in a catch-all share a real shape, graduate them into a named coarse skill or bucket. *(This is exactly why the Access bucket was promoted out of Utility, and why a `messaging` skill would form once email + chat + iMessage co-exist.)*
- **Earned independence (promote OUT to top-level).** When one unit is large or distinct enough that hiding it as a subcommand hurts discoverability more than its catalog cost hurts, give it its own slot. *(`bridge` earned this — three sub-bridges, its own config, a deep runbook.)*
- **Never graduate on speculation.** A single future capability is not a family. Wait for the second member before spawning a coarse skill; wait for real heft before spawning a top-level skill.

## Worked examples

- **`io`** — a coarse accessor skill for the cloud-docs family. `gsheet` / `gdoc` / `gdrive` / `email` are subcommands: **1** catalog slot for the whole family, depth free until `/io` is invoked.
- **A future `messaging` skill** — when email outgrows Apple Mail (WhatsApp, iMessage, Signal), those become `/messaging <provider>` subcommands under **one** new coarse skill. Email is "its own category" expressed as a coarse skill, **not** N top-level skills.
- **`bridge`** — graduated to top-level (earned independence). Sits in the Access grouping but is nobody's subskill.
- **Access grouping** — org-only category over `ctrl` / `io` / `bridge` / `exp`; costs nothing in the runtime catalog. Promoted those four out of Utility/Doc per the cull rule.

## Anti-patterns

- **A skill per micro-capability.** "Read email" and "read calendar" as two top-level skills — both should be subcommands of one coarse accessor. Catalog breadth for capability depth is a bad trade.
- **A grouping masquerading as a skill.** Naming a skill the same as a grouping (`access` skill + Access grouping) — pick one role per name.
- **Premature coarse skill.** Spinning up a `messaging` skill when only email exists — that's just `io email` with extra steps. Wait for the second member.
- **Premature top-level promotion.** Pulling a subcommand out to top-level "because it feels important" — importance to *you* this week isn't catalog-slot-worthy; distinct shape and heft are.

## Related

- [[Access PRD]] — applies this discipline to the accessor family (surface-organized; email as subcommand; bridge as earned top-level).
- The *cull rule* originates in the Utility bucket PRD (promote out when ≥2 share a shape); this discipline generalizes it across all grains.
- [[progressive-disclosure]] — sibling discipline: that one layers *information within a doc*; this one layers *capability across the catalog*. Same "as much as needed at this depth, no more" spirit, different axis.
