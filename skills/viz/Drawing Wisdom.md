---
description: Accumulated judgment about drawing pictures — when a figure earns its place, what makes one readable, and the mistakes that keep recurring. The companion to the `viz` skill's mechanical instruction.
---
# Drawing Wisdom

What has actually been learned about making figures, as opposed to how to operate the tools.

The `viz` skill and [[R-diagram]] are mechanical: this action produces that file, these 22 rules must hold. Neither says whether a figure should exist, what it should leave out, or why the same mistakes keep recurring. That is what this file is for. It grows by accretion — every figure that fails to earn its keep, and every one that surprises by working, belongs here.

## The first question is whether to draw at all

**A figure earns its place by being reached for unprompted.** That is the only test that has ever held up. A diagram that gets made, admired, and never opened again is decoration, however correct it is.

The practical form: before drawing, name the *question* someone will arrive with. "Who do I ask about this document?" "What goes stale if I change this?" "Where does this item belong?" If no such question exists, the figure has no user, and prose will serve better.

The corollary is uncomfortable and worth stating: **most things that feel diagram-shaped are better as a table.** A mapping with two columns is a table. A sequence of steps is a numbered list. Boxes-and-arrows earn their cost only when the *topology* is the content — when what matters is which things touch which other things, and a linear reading loses that.

## What a good figure leaves out

Every real figure is mostly a set of decisions about what not to draw. Two that recur:

- **Converge rather than fan out.** When eleven things all read one document, eleven arrows make the figure unreadable and communicate nothing that one arrow into a node labelled *every agent* does not. The convergence node is not a shorthand or an apology — it is more accurate, because "everyone reads this" is the actual fact.
- **Group what is structurally identical.** Five agents that each own exactly one anchor and share nothing are one grouped box, not five regions. A region per agent adds boxes without adding information. Draw the distinctions that matter and collapse the ones that repeat.

Both are instances of the same rule: **the figure's job is to make one thing obvious, and every additional element costs some of that.**

## The mistakes that keep recurring

- **ASCII art.** Forbidden outright, and the reason is not aesthetic: it renders too small to read in Obsidian, does not scale, cannot be edited except by hand-counting characters, and signals that the author did not think the picture was worth real effort. It has been corrected many times. Reach for a real artifact every time.
- **The bare embed.** `![[figure.svg]]` renders as a fit-to-column thumbnail — technically present, practically invisible. Always carry a large width hint (`|2400`). Obsidian caps it to the pane, so over-specifying is safe and under-specifying is not.
- **Orphaned output.** A figure whose source has been lost is a figure that can never be corrected, so it silently becomes wrong and stays wrong. Source sits beside output, same basename, always. Hand-written SVG is the default precisely because the `.svg` *is* the source — nothing to lose.
- **Explaining the figure in prose underneath.** If the diagram needs three paragraphs to be legible, the diagram is the wrong one. One paragraph is the budget. Anything longer is a signal to redraw, not to keep writing.
- **Figure and text drifting apart.** Every box in an architecture figure should appear in its subsystems table and vice versa. The drift is silent and the figure keeps looking authoritative long after it stopped being true.

## The rules are the floor, not the goal

[[R-diagram]]'s 22 rules — no box overlap, arrows anchored to edges, ≤2 bends, labelled arrows, contrast ratios, quantized font sizes — are all checkable, and a figure can satisfy every one of them and still be useless. They exist to catch the failures that are *mechanical*, so attention is free for the one that is not: whether the picture answers the question someone actually arrived with.

Pass the rules. Then ask whether you would open this figure yourself.

# BRIEF

- **This file is judgment, not procedure.** Operating instructions belong in the `viz` skill and the `viz-*.md` action files; machine-checkable constraints belong in [[R-diagram]]. If something here can be mechanically enforced, move it to the ruleset and delete it from here.
- **It is meant to be published.** Write for a reader outside this vault — no anchor-local shorthand, no assumed context, nothing that only makes sense to someone who knows the estate.
- **Grow it from real failures.** Every entry should trace to a figure that actually did or did not work. Generic design advice is available everywhere else and is not worth the bytes.
