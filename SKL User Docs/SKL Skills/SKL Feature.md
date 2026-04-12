# Feature

`/feature` -- Creates, plans, and readies a new feature document.
- Designs and plans feature
- `/ready` -- ensures all open questions are resolved and ready for build



A feature is a unit of work that moves through design, readiness, and implementation. The feature skill guides the system from idea to ready-to-implement.

- **Feature** — create a dated feature doc in the Features folder. Describe goals, approach, constraints.
- **Spec** — write the implementation spec if the feature is large enough to need one.
- **Research** — investigate approaches, prior art, tools if needed.
- **Replan** — update the plan if requirements changed during design.
- **Open-questions** — surface and resolve all questions before implementation.
- **Ready** — verify all implementation questions are answered. No questions remain for the user. The feature doc is the complete spec for what to build.

**Output:** A feature doc in `{RID} Features/` with status "Ready" in stat. The agent can proceed to Implement without asking the user anything.
