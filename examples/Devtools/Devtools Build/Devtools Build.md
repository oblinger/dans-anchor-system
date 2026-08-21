---
description: "Devtools Build — what turns source into a shippable artifact"
---

| -[[Devtools Build]]- | : what turns source into a shippable artifact<br>→ [[DAS]] → [[FEX]] → [[Devtools\|DVT]] → [Devtools Build](hook://p/Devtools%20Build)  |
| --- | --- |
| Related | [[Devtools]] (parent),  [[DAS spine]],  [[FEX Spine Examples]], |
| [[Devtools Compile\|Compile]]  | typechecks and emits objects; the only step allowed to fail loudly on a warning |
| [[Devtools Bundle\|Bundle]]  | links the objects into one artifact and records what went into it |
| [[Devtools Watch\|Watch]]  | the incremental loop developers actually live in; correctness is Compile's job, not its own |
| [[Devtools Cache\|Cache]]  | what makes the warm build 3 s instead of 40 s, and the first suspect when a build is wrong |
| ... |  |

# Devtools Build
What turns source into a shippable artifact — four tools, and the gate they exist to hold.

Nothing ships that does not compile clean — the gate this stage enforces, and the reason it runs first.

Reached from ~~[[Devtools]]~~ as a `+`-marked group row: the members previewed there are pinned by hand, and this page is where the full set lives. That split is the whole point of the two-level shape — a preview that drifts is a cosmetic problem, while a missing child is a real one, which is why the catch-all above is kept even though every tool is named.
