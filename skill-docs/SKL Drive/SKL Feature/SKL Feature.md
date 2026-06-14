---
description: "Manage a feature from idea through design, agreement, implementation, testing, and completion."
---
# Feature
`/feature` -- Creates a new feature document specifying work to be done.

| -[[SKL Feature]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Drive]] → [SKL Feature](hook://p/SKL%20Feature)<br>: the `/feature` skill |
| --- | --- |
| Related | [[skills/feature/SKILL.md\|SKILL]],   |
| [[SKL Feature Design\|Design]] |  |

A feature is a unit of work that moves through design, readiness, and implementation. The feature skill guides the system from idea to ready-to-implement.

**Cross-anchor title-collision warning.** F-numbers reset per anchor, so the same `F<n> — Title` filename can appear in multiple anchors over time. At creation time, `/feature` greps the vault for an existing feature doc with the same H1; if one is found in another anchor, the agent surfaces a single inline yes/no — proceed (and use path-qualified wiki-links per [[CAB Backlog]] § Wiki-link conventions for feature docs) or rename. Within-anchor collisions block creation outright. Implemented in F27.

- **Feature** — create a dated feature doc in the Features folder. Describe goals, approach, constraints.
- **Spec** — write the implementation spec if the feature is large enough to need one.
- **Research** — investigate approaches, prior art, tools if needed.
- **Replan** — update the plan if requirements changed during design.
- **Open-questions** — surface and resolve all questions before implementation.
- **Ready** — verify all implementation questions are answered. No questions remain for the user. The feature doc is the complete spec for what to build.

**Output:** A feature doc in `{slug} Features/` with status "Ready" in stat. The agent can proceed to Implement without asking the user anything.
