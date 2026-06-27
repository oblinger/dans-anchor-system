---
description: Common Skill Example — reference skill demonstrating the canonical skill-anchor structure. Reference only, not invoked.
name: cse
user_invocable: false
---

# CSE — Common Skill Example

This `SKILL.md` is illustrative. It shows what `SKILL.md` looks like when it sits at the root of a CAB skill anchor. CSE is reference material, not an invokable skill — `user_invocable: false` keeps it out of the user's slash-command surface.

User docs: [[SKL CSE]]
Anchor page: [[CSE]]


## Actions

| Usage       | File           | Description                                          |
| ----------- | -------------- | ---------------------------------------------------- |
| `/cse demo` | [[cse-demo]]   | Echo a marker line back to the user (illustrative)   |


## Dispatch

On invocation:
1. Parse the argument to determine the action.
2. Look up the file from the Actions table above.
3. Read that file from this skill's directory and execute its workflow.
4. If no argument or unrecognized argument, show the dispatch table above.
