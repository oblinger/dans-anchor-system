---
name: formats
description: Discipline. The user's standard formats for pieces of information agents produce — email drafts first, more as they accrete. One H2 per format; each gives its trigger, rules, and a real example. Not markdown-layout rules (that is DAS markdown) — these are output-conformance formats, mostly about surviving the trip into an external surface.
user_invocable: false
---

# formats

The user's **standard formats for information** — the shapes an agent must use when producing a given kind of output, regardless of which skill is doing the producing. One H2 per format. Each format section carries three things: **When it applies** (the trigger), **Rules**, and **Example**.

Scope boundary: [[DAS markdown]] owns how markdown documents are laid out *inside the vault*. This discipline owns formats whose test is **what happens when the content leaves** — pasted into Mail, a form, a chat, another app. Most formats here exist because markdown decoration corrupts the destination.

Growth path: this stays one document while each format fits a screenful. If a format outgrows that, it becomes one file per format in a `formats/` folder with this page as the index — the same upgrade the Cards discipline took.

## Email draft

**When it applies** — any time an agent drafts an email for the user, whether in chat, in a doc, or handing off to `/io email`.

**Rules:**

- **Ready-to-paste plain text.** The draft is a single fenced block (an email body is literal non-markdown, so a fence is correct here). The user selects, copies, pastes into Mail — nothing to strip.
- **Header lines included.** First lines are `To:` and `Subject:`, then a blank line, then the body.
- **No markdown decoration inside.** No blockquote `>` prefixes (the historical failure: a draft presented as a blockquote cannot be cut-pasted), no bold/italics, no wiki-links, no headings.
- **No em-dashes.** Outward-facing prose; em-dashes are an AI tell. Use commas, periods, or parentheses.
- **Readable line lengths.** Wrap the body naturally; no hard-wrapped ragged lines.
- **In chat, show the block inline** — never only point at a doc holding the draft.

**Example:**

```
To: sean@example.com
Subject: XbotGo footage from Saturday

Sean,

The XbotGo clips from Saturday's game are uploaded. The second half
has the two goals, starting around 38:00.

Let me know if you want the full-field version as well.

Dan
```
