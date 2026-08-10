---
description: "the design pipeline — per-skill design docs + PRDs, grouped by group"
---

| -[[DAS Design]]- | : the design pipeline — per-skill design docs + PRDs, grouped by group<br>→ [[DAS]] → [design](hook://design) → [DAS Design](hook://p/DAS%20Design)  |
| --- | --- |
| Related | [[DAS Docs\|Docs]],  [[DAS Skills\|Skills]],  [[DAS Design Folder\|Design (facet)]],  [[DAS\|dans-anchor-system]],   |
|  | **SKILL GROUPS** |
| [[SKL Anchor\|Anchor]]+ | [[DAS Anchor Toolkit Design\|Anchor Toolkit]],  [[DAS Create Design\|Create]],  [[DAS Install Design\|Install]],  [[DAS Migrate Design\|Migrate]],  [[DAS Move Design\|Move]],  [[DAS Publish Design\|Publish]],  [[DAS Streams Design\|Streams]],  [[DAS WP Design\|WP]],  [[DAS Yore Design\|Yore]],   |
| [[SKL Track\|Track]]+ | [[DAS Tracking Design\|**Tracking (subsystem)**]],  [[DAS Groom Design\|Groom]],  [[DAS Groom PRD\|Groom PRD]],  [[Query PRD]],  [[DAS Backlog]],  [[DAS Messages]],  [[DAS Plan]],  [[DAS workflow]],   |
| [[SKL Drive\|Drive]]+ | [[DAS Feature Design\|Feature]],  [[DAS Feature PRD\|Feature PRD]],  [[DAS Crank Design\|Crank]],  [[DAS Crank PRD\|Crank PRD]],  [[DAS Mint Design\|Mint]],  [[DAS Mint PRD\|Mint PRD]],  [[DAS Finalize Design\|Finalize]],  [[DAS Finalize PRD\|Finalize PRD]],  [[DAS Land Design\|Land]],  [[DAS Land PRD\|Land PRD]],  [[DAS Fortify Design\|Fortify]],  [[DAS Fortify PRD\|Fortify PRD]],   |
| [[DAS Design Design\|Design]]+ | [[DAS Architect Design\|Architect]],  [[DAS Architect PRD\|Architect PRD]],   |
| [[SKL Code\|Dev]]+ | [[DAS Code Design\|Code]],  [[DAS Fix Design\|Fix]],  [[DAS Pilot Flow Design\|Pilot Flow]],  [[DAS PR Flow Design\|PR Flow]],   |
| [[SKL Doc\|Doc]]+ | [[DAS MD Design\|MD]],  [[DAS Viz Design\|Viz]],   |
| [[SKL Hygiene\|Hygiene]]+ | [[DAS Audit Design\|Audit]],  [[DAS Audit API Design\|Audit API]],  [[DAS Audit Architecture\|Audit Architecture]],  [[DAS Audit Completed Roadmap\|Audit Completed Roadmap]],  [[DAS Audit Decisions\|Audit Decisions]],  [[DAS Audit Files Architecture\|Audit Files Architecture]],  [[DAS Audit PRD\|Audit PRD]],  [[DAS Audit Roadmap\|Audit Roadmap]],  [[DAS Audit Rules Redesign\|Audit Rules Redesign]],  [[DAS Audit Stories\|Audit Stories]],  [[DAS Audit System Design\|Audit System]],  [[DAS Audit Testing\|Audit Testing]],  [[DAS Audit UX Design\|Audit UX]],  [[DAS Dupes Design\|Dupes]],  [[DAS Maintain Design\|Maintain]],  [[DAS Rewire Design\|Rewire]],  [[DAS Slug Scan Design\|Slug Scan]],  [[DAS Tidy Design\|Tidy]],   |
| [[SKL Search\|Search]]+ | [[DAS Find Design\|Find]],  [[DAS Profile Design\|Describe]],  [[DAS Purchase Design\|Purchase]],  [[DAS Survey Design\|Survey]],   |
| [[SKL Utility\|Utility]]+ | [[DAS Atlas Design\|Atlas]],  [[DAS Bridge Design\|Bridge]],  [[DAS Bridge PRD\|Bridge PRD]],  [[DAS Bridge Testing\|Bridge Testing]],  [[DAS Bridge UX Design\|Bridge UX]],  [[DAS Cook Design\|Cook]],  [[DAS Ctrl Design\|Ctrl]],  [[DAS Daybreak Design\|Daybreak]],  [[DAS Daybreak PRD\|Daybreak PRD]],  [[DAS Exp Design\|Exp]],  [[DAS MUSE Architecture\|MUSE Architecture]],  [[DAS Parley Design\|Parley]],  [[DAS Snip Design\|Snip]],   |
| --- | |
| [[DAS Anchor Design]]  | Subsystem design for the Anchor group — the folder-shape substrate every other subsystem rides on, plus the lifecycle verbs that create, restructure, relocate, publish, and archive anchors. |
| [[DAS Code Skill Design]]  | design surface for SKL Code |
| [[design/DAS Decisions]]  | durable decisions for the DAS anchor itself — what this repo may contain and why |
| [[DAS Doc Design]]  | Subsystem design for the Doc group — the authoring verbs that shape, illustrate, polish, and route documents, plus the round-trip to external document apps. |
| [[DAS Drive Design]]  | Subsystem design for the Drive group — the autonomous-execution loop that consumes Ready work (crank → mint → finalize), the feeders that mint new work, and the bounded stop. |
| [[DAS Hygiene Design]]  | Subsystem design for the Hygiene group — rules declared once, checked everywhere (Warden on-write + /audit sweeps), and repaired to zero via the 100%-fix discipline. |
| [[DAS Search Design]]  | Subsystem design for the Search group — the research verbs that answer questions about the world (find one, profile one, compare many, buy one) and file dated result docs. |
| [[DAS Stone Design]]  | the architecture of the stone system — the four surfaces, the one line that is both an ordering decision and a machine reference, and the propagation pass over the feed DAG |
| [[DAS Stone Keys]]  |  |
| [[DAS Utility Design]]  | Subsystem design for the Utility group — machine access (local, remote, GPU, GUI), capture pipelines (voice, text), and life utilities; always available, no anchor trait. |
| [[Template Examples]]  | The case corpus Stencil is derived from — a real example first, then proposed stencils, then the discussion. Every block is delimited, verbatim, and copy-pasteable. |
| [[DAS Design Design\|Design]]  | Subsystem design for the Design group — the artifact pipeline, gates, and verbs that turn an idea into an agreed, buildable specification before execution starts. |

# Design
The **design internals** — the `{skill} Design` / `{skill} PRD` pages that specify how each skill works, filed under `design/<group>/`. Only skills with real design work appear here; the user-facing counterparts live under [[DAS Docs]].
