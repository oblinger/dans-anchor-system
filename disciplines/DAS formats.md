---
name: formats
description: Discipline. The user's standard formats for pieces of information agents produce — email drafts first, more as they accrete. One H2 per format; each gives its trigger, rules, and a real example. Not markdown-layout rules (that is DAS markdown) — these are output-conformance formats, mostly about surviving the trip into an external surface.
user_invocable: false
group: discipline
---

# formats

The user's **standard formats for information** — the shapes an agent must use when producing a given kind of output, regardless of which skill is doing the producing. One H2 per format. Each format section carries three things: **When it applies** (the trigger), **Rules**, and **Example**.

Scope boundary: [[DAS markdown]] owns how markdown documents are laid out *inside the vault*. This discipline owns formats whose test is **what happens when the content leaves** — pasted into Mail, a form, a chat, another app. Most formats here exist because markdown decoration corrupts the destination.

Growth path: this stays one document while each format fits a screenful. If a format outgrows that, it becomes one file per format in a `formats/` folder with this page as the index — the same upgrade the Cards discipline took.

## Email draft

**When it applies** — any time an agent drafts an email for the user, whether in chat, in a doc, or handing off to `/io email`.

**Rules:**

- **Live markdown, NOT a fenced block.** The user copies the *rendered* draft (Obsidian reading view) and pastes into Mail as rich text. A fence would make `**asterisks**` paste literally — verified 2026-07-22: from rendered markdown, **bold**, *italic*, ***bold italic***, bulleted lists, numbered lists, and plain URLs all survive the paste into Mail intact.
- **Header lines always present:** `To:`, `CC:` (always shown, even when empty), `Subject:` — then a blank line, then the body.
- **Allowed in the body:** bold, italic, bold-italic, bulleted and numbered lists, plain `https://…` links.
- **Forbidden in the body:** blockquote `>` prefixes (the historical failure — corrupts the paste), headings, wiki-links (meaningless outside the vault), and em-dashes (outward-facing prose; use commas, periods, or parentheses).
- **Readable line lengths.** Wrap the body naturally; no hard-wrapped ragged lines.
- **In chat, show the draft inline** as the same live markdown — never only point at a doc holding it.

**Example** (everything below the rule line is the draft, as live markdown):

---

To: sean@example.com
CC: pat@example.com
Subject: XbotGo footage from Saturday

Sean,

The XbotGo clips from Saturday's game are uploaded. The **second half** has both goals, starting around 38:00. Quick highlights:

- Goal one at 38:12, *nice cross from the left*
- Goal two at 51:40
- Full match: https://example.com/match/0722

Let me know if you want the full-field version as well.

Dan

---
