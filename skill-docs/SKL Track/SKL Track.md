---
description: "The disciplines + tool that govern what's tracked."
---

| -[[SKL Track]]- | : The disciplines + tool that govern what's tracked.<br>→ [[DAS]] → [[skill-docs]] → [SKL Track](hook://p/SKL%20Track)  |
| --- | --- |
| [[DAS workflow\|Workflow]]  | The canonical state graph for any unit of work — what state it's in, what each state means, and what advances it. |
| [[DAS Backlog\|Backlog]]  | Organizes a backlog along two independent axes — *when* the user wants work to happen (horizon) and *how far* the work has progressed (workflow state). |
| --- | |

# SKL Track
The disciplines + tool that govern *what's being tracked* inside an anchor's `{slug} Track/` folder — the canonical state graph, the horizon structure, the verify-tier system, and the validator that enforces them. Distinct from [[SKL Drive]] (which *moves* work through tracking) and from [[SKL Anchor]] (which builds the anchor itself).

| Card |  |
| --- | --- |
| **Verification** | Tier system for `[Verify]` items — agent-immediate / agent-over-time / user-passive / user-explicit. Doc pending. |
| **Audit-q** | Mechanical validator for backlog + Q.md integrity (link existence, bracket validity, H2 purity, etc.). Reads CAB Backlog spec; ships in `audit/scripts/audit-q.py`. Doc pending. |
