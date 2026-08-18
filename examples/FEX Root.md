---
description: "the examples corpus indexed by facet"
---

| -[[FEX Root]]- | : the examples corpus indexed by facet<br>→ [[DAS]] → [[examples]] → [FEX Root](hook://p/FEX%20Root)  |
| --- | --- |
| Related | [[DAS Examples\|Examples]],  [[DAS Facets\|Facets]],  [[DAS\|dans-anchor-system]],   |

# FEX Root
Every facet's worked example, reached by facet name. This is the same corpus [[DAS Examples]] holds — indexed by **facet** rather than by **world**, so the two are parallel views and each links the other.

## By facet — where the example lives

Rows and order match [[DAS Facets]] exactly. Each entry displays the **facet name** and links to its example, so clicking the facet name lands you on the example rather than on a page about the example. Where a facet has more than one, the extra examples follow in parens. An *italic, unlinked* entry is a facet with no example yet — a gap, deliberately visible.

| | |
|---|---|
|  | **EXAMPLES BY FACET** |
| [[DAS Anchor Design\|Anchor]] | *Anchor*,  [[DAS\|Dot Anchor]] ([[OBU\|code: form]]),  [[HBR\|Anchor Page]] ([[OBU\|code anchor]]),  [[ABIO\|Project Page]] ([[DCP\|minimal]]),  [[HBR\|Folder]],  [[HBR\|Anchor Tree]],  [[HBR\|Naming]],  [[FEX Claude\|Claude]],  [[HA Interface\|Interface]] ([[MUX Interface\|fuller]]),  [[SKA move\|Move]],  [[A2X Subs\|Subs]],  *Dispatch*,  [[HBR\|Dispatch Table]] ([[FEX Dispatch Examples\|gallery]]),  *Dispatch Table Design*,  [[HBR Design\|Design Dispatch]],  [[HBR Dev Docs\|Dev Dispatch]],  [[HBR User Docs\|User Dispatch]],   |
| [[DAS Hygiene Design\|Hygiene]] | [[R-fex-manifest\|Ruleset]] ([[R-diagram\|large]], [[FEX Rules\|anchor-local]]),   |
| [[DAS Tracking Design\|Tracking]] | [[Tink Backlog\|Backlog]],  [[Tink queries\|Query]],  [[HBR Status\|Status]],  [[FEX Agenda\|Agenda]],  *Stone*,  [[HBR Rocks\|Rocks]] ([[Rocks\|root aggregator]]),  [[FEX Roadmap\|Roadmap]] ([[HBR Roadmap\|legacy-numbered]]),  [[A2X013 - Game Break Overview\|Notebook]],  [[HBR Messages\|Messages]],  [[Tink Track\|Track]],  [[FEX Icebox\|Icebox]],  [[TINK Chores\|Chores]],   |
| [[DAS Design Design\|Design]] | *Design Docs*,  [[HBR Design\|Design Folder]],  [[HBR PRD\|PRD]] ([[Mini PRD\|minimal]]),  [[FEX Stories\|Stories]] ([[HBR PRD\|inline]], [[DAS US-CAE-1 — Schedule a Task\|per-story]]),  [[FEX Architecture\|Architecture]] ([[HBR Architecture\|in-project]]),  [[FEX System Design\|System Design]],  [[SKA File Tree Architecture\|Files Architecture]],  [[HBR UX Design\|UX Design]],  [[FEX API Design\|API Design]] ([[HBR API Design\|in-project]]),  [[Mini Testing\|Testing]] ([[HBR Testing\|maximal]]),  [[OBU Testing\|Common Testing Types]],  [[Mini Architecture\|Decisions]] ([[Mini Decisions\|central]], [[HBR Decisions\|in-project]]),  [[HBR Features\|Features]],   |
| [[DAS Code Design\|Code]] | *Code*,  [[OBU\|Code Repository]] ([[HA\|linked-relative]]),  [[FEX Scheduler\|Module Doc]] ([[HBR Scanner\|leaf module]]),  [[HBR CLI\|CLI]],  *Changes*,  *Specs*,  [[FEX Files\|All Files]] ([[HBR Files\|in-project]]),  [[HBR Versions\|Versions]] ([[OBU\|live monorepo]]),   |
| [[DAS Doc Design\|Doc]] | *Doc*,  [[FEX Minimal Facet\|Doc Structure]] ([[HBR Architecture\|fuller]]),  [[SV Roots\|Brief]] ([[SV Roots Brief\|sidecar]]),  [[numpy bcast\|Cards]] ([[numpy\|index]]),  [[ABIO\|Documentation Site]] ([[DCP\|minimal]]),  *Output*,   |
| [[DAS stream\|Stream]] | [[HA Frontmatter\|Discussion]] ([[HA Design Discussions\|sibling-file]]),  [[Disk Log\|Log]] ([[SV Log\|mixed-format]]),  [[FEX Inbox\|Inbox]],  [[MUX Outputs\|Outputs]],  [[AIS WP\|WP]],  [[FEX Completed Roadmap\|Completed Roadmap]],   |
| *Meta (proposed)* | [[FEX Manifest\|Facet]] ([[FEX Pin\|many]], [[FEX Bundle\|folder]]),  [[FEX Skill\|Skill]] ([[FEX Minimal Skill\|minimal]]),  *Primitives*,  *Aspects*,  [[_{{PURCHASE_DATE}} {{HOSTNAME}} Template\|Template]] ([[_{{DISK_LABEL}} Template\|folder]]),  *skill-config*,  *skill-script*,  *skill-search-rules*,  *skill-testing*,   |

## How to read a cell

Under [[TINK327 - Every facet has a worked example, and FEX {facet} is how you reach it|F327]] Q1 **(A)**, a facet with one *à la carte* example resolves `FEX {facet}` to the example itself — `[[FEX Agenda]]` **is** the Agenda example, no index page in between. Most facets are not in that position: their example is an in-project document ([[HBR Backlog]]) or a live vault instance ([[Tink Backlog]], [[Disk Log]]), and the never-copy rule means `FEX {facet}` can only ever route to it. That is why the entries above link to a mixture of `FEX *`, `HBR *` and real anchors — the destination is wherever the example actually lives, which is the only place it should live.

When a second example arrives for a facet whose single example is à la carte, the incumbent moves to `FEX {facet} {qualifier}` and the bare name becomes the dispatch page. The bare name has become a **container**, so its contents need element names — the same rule that governs facet naming in [[DAS Facets]].

## Gaps and defects this index makes visible

The point of indexing by facet is that a missing example has nowhere to hide. What the first pass surfaced, 2026-08-18:

**Nine facets have no example at all** — `Anchor`, `Dispatch`, `Dispatch Table Design`, `Design Docs`, `Code`, `Doc`, `Output`, plus the proposed `Primitives` and `Aspects`. Seven of the nine are the *broadest* facets in their subsystem, which is a recognisable failure shape: the general spec is the hardest one to exemplify, so it gets skipped while its specialisations get covered.

**Two more are stated-pending rather than forgotten** — `Changes` and `Specs` both record *"none yet — first adoption pending"* against the OpenSpec conversion, which is a gap with an owner and needs no action here.

**The four Skill-Anchor sub-facets carry no `| Examples |` row** — `skill-config`, `skill-script`, `skill-search-rules`, `skill-testing`. [[CSE]] is the fully-wired worked skill anchor and is almost certainly the example for all four, but the specs do not say so, and inferring it here is how an index starts drifting from what it indexes. Listed as gaps until the specs name it.

**`Stone` cites Rocks documents as its examples** — [[HBR Rocks]] and [[MED Rocks]] are instances of the Rocks facet, not of Stone. Either Stone has no example, or the two facets are less distinct than their separate specs imply. Listed as a gap pending that call.

**`Move` cited its own facet spec as its example.** The row read `[[DAS Move|skill runbook]]`, which after the [[TINK Backlog#^T166|T166]] renames resolves to the facet spec itself rather than to a worked instance. This index links [[SKA move]] instead — the managing anchor, which is a real instance.

**Twelve facet specs claimed two examples where one document exists**, citing the same target twice under two labels (`[[HBR Design|minimal]], [[HBR Design|fuller]]`). Corrected at the specs 2026-08-18; the second example in each of those twelve is a genuine gap, now visible above as a facet with a single entry.

## Not done — the folder question

Dan's sketch put a folder behind each subsystem name here, with a `+` catch-all, so an example dropped into `examples/{Subsystem}/` would surface automatically. That reorganisation is **not** done, deliberately: most examples in this corpus are in-project ([[HBR]]) or live vault instances, so they would not move into those folders anyway, and the ones that would are a minority of the 55 items under `examples/`. Worth deciding on its own evidence rather than as a side effect of building the index.
