---
description: "A deep engineering-org reporting tree from CTO down to an individual contributor — six levels."
---
# 06 — Hierarchy / org tree

**Diagram kind:** Hierarchy / org tree.
**Layout challenge:** A deep tree — depth (six reporting levels) competing with breadth (a wide manager fan-out at the top). The layout engine must keep a tall chain legible without letting one deep branch stretch the canvas past a sane aspect ratio, while sibling subtrees of very different depths stay aligned to their level.
**Domain:** The Engineering reporting chain of a mid-size SaaS company, from the CTO down through directors, managers, and team leads to a single individual contributor.

## Nodes
- CTO — Priya Nair, Chief Technology Officer [root]
- VP_ENG — Marcus Webb, VP of Engineering
- VP_INFRA — Dana Olsen, VP of Infrastructure
- DIR_PLATFORM — Sofia Ruiz, Director, Platform
- DIR_PRODUCT — Liam Chen, Director, Product Engineering
- DIR_SRE — Tom Becker, Director, Site Reliability
- MGR_API — Aisha Khan, Manager, API Team
- MGR_WEB — Jordan Lee, Manager, Web Team
- MGR_DATA — Elena Petrova, Manager, Data Platform
- LEAD_API_CORE — Raj Mehta, Tech Lead, API Core
- LEAD_API_GW — Nora Sato, Tech Lead, API Gateway
- ENG_GW_1 — Carlos Diaz, Senior Engineer, API Gateway
- ENG_GW_2 — Mina Park, Engineer, API Gateway

## Edges
- CTO → VP_ENG : "reports to" [solid]
- CTO → VP_INFRA : "reports to" [solid]
- VP_ENG → DIR_PLATFORM : "reports to" [solid]
- VP_ENG → DIR_PRODUCT : "reports to" [solid]
- VP_INFRA → DIR_SRE : "reports to" [solid]
- DIR_PLATFORM → MGR_API : "reports to" [solid]
- DIR_PLATFORM → MGR_DATA : "reports to" [solid]
- DIR_PRODUCT → MGR_WEB : "reports to" [solid]
- MGR_API → LEAD_API_CORE : "reports to" [solid]
- MGR_API → LEAD_API_GW : "reports to" [solid]
- LEAD_API_GW → ENG_GW_1 : "reports to" [solid]
- LEAD_API_GW → ENG_GW_2 : "reports to" [solid]

## Groups / lanes / cardinality
- Strict single-parent tree: every node except the root CTO has exactly one incoming "reports to" edge. No node reports to two managers.
- Six levels deep along the longest branch: CTO → VP_ENG → DIR_PLATFORM → MGR_API → LEAD_API_GW → ENG_GW_1/ENG_GW_2.
- Branches are deliberately uneven in depth: the VP_INFRA → DIR_SRE branch stops at level 3 (DIR_SRE is a leaf), while the API-Gateway branch runs the full six levels. MGR_WEB, MGR_DATA, and LEAD_API_CORE are leaves at their respective levels.
- No grouping containers or swimlanes; the tree structure itself is the only grouping.

## Acceptance
- Fidelity: the render contains exactly these 13 nodes and 12 edges (count + labels match); none added or dropped.
- Legibility: text ≥ ~18px at page-width embed; aspect ~0.6–1.6; no overlaps; per [[R-diagram]].
