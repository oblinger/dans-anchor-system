---
description: "How to ask the user a question inline — ONE crisp, bold, `[question]`-tagged line they can answer immediately, with the context inside it. The style that finally worked after the user struggled for a long time to get agents to ask answerable questions."
---
# SKL ask-inline
**Quick summary for another agent:** When you need a decision from the user, ask **one immediate question** — a single **bold** line, set off by blank lines, tagged **`[question]`**, that they can answer in a word (yes/no or a short pick). Put any must-know context *inside that line*. **Never bury the question under paragraphs of explanation** — if the user has to hunt for what you're asking, you've failed. One line; two at most.

| -[[SKL ask-inline]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Drive]] → [SKL ask-inline](hook://p/SKL%20ask-inline)<br>: the SKL ask-inline doc |
| --- | --- |

## The format

> **[question] <the actual question, with any must-know context in parens>?** Yes/no.

- **`[question]` tag** — a square-bracket prefix so the ask is instantly findable in a wall of agent text. *(When you drive more than one machine — e.g. the bridge — replace it with `[local]` / `[remote]` so the user knows **which machine** the question is about. Most agents aren't on the bridge → just use `[question]`.)*
- **Bold + blank lines around it** — visually separated; the eye lands on it without scanning.
- **One line, two at most.** If it runs longer, you're explaining, not asking — cut it.
- **Self-contained.** The decision-relevant context goes *in the line* (e.g. "(~3 min build, then a ~5-sec restart)"), not in paragraphs above it.
- **Directly answerable** — yes/no or a short labeled pick. The user should reply in one word.

## Multiple questions

Prefer one. If you genuinely have several, list them with a dash — one crisp line each — under a single `[question]` tag:

> **[question]** — pick any:
> - Rebuild now? (~3 min)
> - Keep the folder-name list, or switch to anchor slugs?

But default to a single question. Two is already a lot; more is a wall.

## Examples that worked

- **[question] Want me to rebuild your local app now so you can test the new fixes? (~3 min build, then a ~5-second restart.)** Yes/no.
- **[local] Did macOS pop a permission dialog during the relaunch?** Yes/no.
- **[question] Folder-name list good enough, or do you want the true anchor slug?**

## Anti-patterns (what the user was fighting)

- **Fake questions** — "standing by for your go" / "let me know" / "say the word." The user can't tell *what* they're saying go to. Either ask a real question or just act.
- **Buried questions** — the ask trailing a long multi-paragraph explanation. The user reads the wall and can't find the question. Keep context minimal and inside/after the one line.
- **Vague questions** — "did it work?" Name the specific thing to confirm.
- **Option-soup** — don't dump four sub-options when a yes/no does. If it's a real fork, give 2–3 labeled picks, still on crisp lines.

## Why this exists

The user spent a long time unable to get agents to ask answerable questions. The failure mode is always the same: the question is real but **unfindable or unanswerable** because it's buried or vague. The fix is mechanical — one bold, tagged, blank-line-delimited, one-line question with the context inside it. Confirmed by the user: *"that was an amazingly good question. It's in bold, it's separated away. It's very clear. I can answer it."*

Related: [[DSC ask-format]] (the full asking discipline — recommendation strengths, block-IDs, Phase 1/2/3 lifecycle), [[SKL Ask]] (the `/ask` skill).
