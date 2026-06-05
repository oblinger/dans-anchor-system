---
description: Collaborative text-polish skill for a section of text (up to a page or two). Maintains a versioned workspace where both user and agent edit a shared `## Current` against a stack of accepted `## Version N` H2s. A paired single `.html` mirrors the .md with `## Changes for Version N` sections rendering each successive diff using the [[md-track-changes]] convention. `/redline accept` freezes Current as the next accepted version; `/redline writeback` round-trips to source.
tools: Read, Edit, Write, Bash
user_invocable: true
---

# Redline — Versioned Text Polish with Track-Changes

Collaborative polish of a section of text — up to a page or two — with visible, addressable pending changes and a navigable acceptance history. Spec: `[[F112 — Redline]]`. HTML diff convention: `[[md-track-changes]]`. Sibling to `[[snip]]` (rough-text-drop) and `[[md]]` (markdown utility skill).

## When to Use

Invoke when the user says:
- `/redline start <source>` / `redline start <source>` — open a polish session on the named source
- `/redline show [<title>]` / `redline show [<title>]` — open the most-recent or named session
- `/redline accept` / `redline accept` — freeze the current pending changes as a new accepted version
- `/redline writeback` / `redline writeback` — apply the latest accepted version back to the source
- `/redline close` / `redline close` — leave redline-mode without writeback

**When NOT to use:** rough-text-drop / one-shot refinement → `/snip`. Full-document (multi-page) revision → out of scope for v1; sketch in F112 § Out of scope.

**Conversational invocation works the same way.** The user may type the slash form OR say the same words mid-dictation ("redline start the Vision section", "redline accept"); the agent recognizes the prefix-word `redline` as the dispatch trigger and dispatches to the named sub-command. No DMUX trigger; the agent recognizes the phrase in-context.

## Files

All session files live under: **`~/ob/kmr/Log/REDLINE/`**.

Per session, two paired files share a stem:

| File | Content |
|------|---------|
| `<YYYY-MM-DD> — <title>.md` | Versions stack + Provenance footer |
| `<YYYY-MM-DD> — <title>.html` | Mirrored changes stack, one section per version + a live `Changes for Current` section |

**Title generation rules** (same discipline as `[[snip]]`):
- Generate a short slug (3-5 content-bearing words, lowercase, hyphen-separated) naming what the session is *about* — the topic / action / target of polish.
- Skip conversational openers ("okay", "yeah", "let's"), hedges ("I think", "maybe"), and filler. Name the main subject.
- Examples:
  - source description: "polish the Vision section of /Users/me/Pitch/draft.md" → `vision-section-polish` ✓
  - source description: "tighten the conclusion of this paper draft" → `tighten-paper-conclusion` ✓
  - source description: "/Users/me/email/draft.md the third paragraph" → `email-third-paragraph-polish` ✓
- If content is too thin, fall back to a generic-but-informative slug — never pure filler. Same-date collisions are unlikely if titles are content-bearing.

## Sub-commands

### `/redline start <free-form source description>` — open a session

1. **Interpret the source description.** The argument is natural language — the user may name a path, a path + section heading, paste a quoted excerpt, or gesture at something in conversation ("the Vision section of the pitch we were just discussing"). Read the source file; locate the intended region by content reasoning.
2. **Generate the title** per the title-generation rules above.
3. **Create the .md** at `~/ob/kmr/Log/REDLINE/<YYYY-MM-DD> — <title>.md` with this structure:
   ```markdown
   # Redline — <title>

   ## Current

   <extracted text>

   ## Version 0

   <extracted text — identical to Current at session start>

   ## Provenance

   Extracted from `<source_path>` on <date>; <one-sentence human context: what's being polished, why, any nuance about the boundary>.

   source_path:: <absolute path>
   source_section:: <H2/H3 heading name, if known>
   source_block_id:: <Obsidian block-ID, if applicable>
   source_line_range:: <line range at extraction time, if known>
   ```
   Recommended `::` dataview fields are written **only when known** — omit any field whose value isn't precisely known. The prose paragraph captures the rest.
4. **Create the .html** at `~/ob/kmr/Log/REDLINE/<YYYY-MM-DD> — <title>.html` per § .html file structure with just `## Changes for Current` (empty body — Current equals Version 0, no diff to show).
5. **Glance both files** so the user verifies the extraction landed on the right text:
   ```bash
   open "$HOME/ob/kmr/Log/REDLINE/<YYYY-MM-DD> — <title>.md"
   open "$HOME/ob/kmr/Log/REDLINE/<YYYY-MM-DD> — <title>.html"
   ```
6. **Enter redline-context.** Subsequent user messages are classified per § Conversational edit-mode.

**If extraction missed the intended region**, the user will see the wrong text in `## Current` / `## Version 0` and correct (either edit `## Current` directly in the .md, or describe the correction in conversation and the agent re-extracts).

### `/redline show [<fuzzy title>]` — open an existing session

Show works on **any** session — fresh, mid-polish, or already-closed (after `writeback` or `close`). Re-opening a closed session via `show` puts it back into redline-context for further polish, with the file state preserved exactly as it was at close time.

1. **Resolve which session.** If no argument: the currently-active session (the one the agent has been working with) OR, if none active, the most-recently-modified `.md` file in `~/ob/kmr/Log/REDLINE/`. If `<fuzzy title>` given: list session files in `~/ob/kmr/Log/REDLINE/`, fuzzy-match the title-slug portion of the stem (case-insensitive, substring or word match), pick the best fit. If multiple match closely, ask the user to disambiguate.
2. **Glance both files** of the chosen session.
3. **Enter redline-context** for the chosen session.

Bare `show` doubles as "list and open most-recent" — no separate `list` verb.

### `/redline accept` — freeze Current as the next version

Pre-condition: a session is active.

1. **Read `## Current`** from the .md.
2. **Determine the new version number** N+1: walk the .md's H2s, find the highest existing `## Version N`, increment.
3. **Insert a new `## Version N+1` H2** into the .md, placed **after** `## Current` and **before** the existing `## Version N`. Body is the text of `## Current`, verbatim.
4. **Read the current `## Changes for Current` section** from the .html (it contains the diff that's about to become this version's historical record).
5. **Insert a new `## Changes for Version N+1` H2** into the .html, placed **after** `## Changes for Current` and **before** the existing `## Changes for Version N`. Body is what was just in `## Changes for Current` (the rendered `<del>` / `<ins>` / `.comment` markup).
6. **Recompute `## Changes for Current`** — its body becomes empty (a single sentence: `<p><em>No pending changes — Current equals Version N+1.</em></p>`), because Current now equals Version N+1.
7. **Glance both files** so the user sees the new baseline.

### `/redline writeback` — round-trip to source

Pre-condition: a session is active. **No accept-first requirement** — writeback uses `## Current`'s text directly, regardless of how recently `accept` was invoked.

1. **Read the source file fresh** at the path from `## Provenance` (the `source_path::` dataview field or the prose mention).
2. **Locate the originally-extracted region** by content reasoning:
   - Start with the `source_section::` (if known) — find that H2/H3 in the current source. If found, the region is plausibly that section's body.
   - Cross-check with `## Version 0` from the .md — that's what the section's body looked like at extraction time. The source may have drifted; compare what's in the source today against V0 to confirm you're looking at the same region.
   - If the section header has moved or been renamed, search by content (grep for distinctive phrases from V0) and locate the region in the current source.
   - If the source has changed substantially in the target region (someone edited the section since extraction), surface this to the user before writing — ask whether to writeback anyway or abort.
3. **Replace that region** in the source with `## Current`'s text.
4. **Report what changed in the source** — show the diff: what was there before vs what's there now.
5. **Implicitly close the session.** Writeback is the success hard-end: redline-context ends, subsequent messages are no longer treated as edits to this session. The session files stay in `~/ob/kmr/Log/REDLINE/` as historical record. If the user wants to polish further later, `redline show <title>` reopens the session.

**Why Current, not latest-accepted-version?** Writeback is itself a deliberate, collision-free verb (the user doesn't say "redline writeback" by accident — Q5). Adding an accept-before-writeback gate would be redundant ceremony. Accept's role narrows to marking milestones in the version stack for review and history navigation; it is not a writeback gate. The rare case where the user wants to writeback an earlier milestone instead of Current is handled by manually reverting Current to that version's text before writeback.

### `/redline close` — explicit close without writeback

`writeback` already implies close, so `close` is only needed when stepping away from a session **without** writing back to source. Use cases: polish is paused for an extended time, polish is abandoned, or conversational drift makes redline-context ambiguous and the user wants to be unambiguous about leaving.

Procedure:
1. End redline-context — subsequent messages are no longer treated as edits to this session.
2. Do nothing else — session files remain in `~/ob/kmr/Log/REDLINE/` unmodified.

`show <title>` reopens later if the user wants to resume. Abandoning a session without `close` is also fine (the session files sit dormant) — `close` is for when the user wants explicit confirmation that they've left redline-mode.

## Conversational edit-mode

After `start` or `show`, the agent is in **redline-context**: subsequent user messages are interpreted as relevant to the active session unless they're clearly about something else.

Classify each user message into one of three buckets:

### 1. Edit directive — make the edit + glance

Examples: "tighten the opener", "drop the third change", "make the conclusion more concrete", "back out the qualifier change", "the second paragraph reads weird — fix it".

Procedure:
1. Read `## Current` from the .md.
2. Apply the edit by writing a new version of Current. Be conservative — change only what the directive named. If the directive was vague, take the most defensible reading; the user can back it out.
3. Write the new Current back to the .md (replacing the body of `## Current`).
4. Recompute the .html's `## Changes for Current` section to show `diff(VN, new Current)`. See § Diff computation.
5. Glance BOTH the .md and the .html so the user sees what landed.

### 2. Edit suggestion — show in chat, no file change

Examples: "what would tightening look like?", "show me a version with the conclusion sharpened", "I'm thinking about something punchier — what would that be?".

Procedure:
1. Compute the suggested edit but DO NOT write it to the .md.
2. Show the diff inline in chat (markdown rendering with `~~old~~` and `**new**` is fine for chat-only display).
3. Wait for the user's call. If they confirm, treat the next turn as an edit directive (see bucket 1).

### 3. Off-topic / unrelated — fade redline-context

Examples: "what's the status of F091?", "by the way, what time is it in Tokyo?", "let me think about something else for a minute".

Procedure:
1. Answer the message normally; do not interpret as an edit.
2. Redline-context fades — the agent remembers the session exists but stops treating ambient messages as edit-directives.
3. The user re-enters via `redline show` (bare or with title) when ready.

**The line between buckets is fuzzy; that's expected.** The mitigation is the **glance discipline** — every edit to Current opens both files in front of the user, so a misinterpreted edit surfaces in the same turn. The user corrects by editing `## Current` directly in the .md or by saying "no, undo that, I meant…" and the agent edits Current back.

**Cost of a wrong-bucket classification:**
- Wrong-bucket-1 (edit when user meant suggestion): one extra change in Current; user backs it out; one wasted edit cycle. Cheap.
- Wrong-bucket-2 (suggestion when user meant edit): user says "yes, do it" → next turn edits. One extra round-trip. Cheap.
- Wrong-bucket-3 (off-topic when user meant edit): agent answers off-topic and ignores the edit. User repeats the directive. Mildly annoying but cheap.

The glance discipline catches all three.

## .html file structure

The .html uses the `[[md-track-changes]]` HTML format. Template:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Redline — <title> (Changes)</title>
  <style>
    body { font-family: Georgia, serif; max-width: 850px; margin: 40px auto; padding: 20px; line-height: 1.7; color: #333; }
    h1, h2, h3 { color: #1a1a1a; }
    h2 { border-bottom: 1px solid #ddd; padding-bottom: 4px; margin-top: 36px; }
    del { background-color: #fdd; color: #900; text-decoration: line-through; }
    ins { background-color: #dfd; color: #060; text-decoration: none; }
    .comment { background-color: #fffde7; border-left: 3px solid #ffc107; padding: 10px 14px; margin: 12px 0; font-size: 0.9em; color: #555; }
    .comment::before { content: "💬 "; }
    .empty-current { color: #888; font-style: italic; }
  </style>
</head>
<body>
<h1>Redline — <title> (Changes)</h1>

<h2>Changes for Current</h2>
<!-- live diff: V_N → Current. Empty when Current equals latest accepted version. -->
<p class="empty-current">No pending changes — Current equals Version N.</p>

<h2>Changes for Version N</h2>
<!-- frozen on accept: diff V_(N-1) → V_N -->
... rendered diff body ...

<h2>Changes for Version N-1</h2>
... rendered diff body ...

</body>
</html>
```

**H2 ordering: newest first.** `## Changes for Current` always at the top; then `## Changes for Version N`, `## Changes for Version N-1`, …, `## Changes for Version 1` descending. No `Changes for Version 0` — there's nothing before V0.

**Rendering the diff body** in each `## Changes for X` section:
- Render the markdown text of the *target* version (the one the section is about) with inline `<del>` for deletions and `<ins>` for insertions showing what changed from the previous version.
- Format the surrounding markdown as HTML (bold, italic, lists, headings) — the reader sees formatted prose, not raw markdown.
- Mark changes at the word/phrase level, not whole paragraphs. The reader should be able to see the *minimum* unit that changed.
- Add `.comment` divs after each change or group, explaining the reasoning briefly ("tightened the second clause," "removed redundant qualifier," "user's manual edit"). Comments are optional but helpful when the change isn't self-evident.

## Diff computation

For each call that triggers a diff recompute:

1. **Identify the two texts.** "Old" = the previous version's text (`## Version N` for accept; `## Version N` for live `## Changes for Current`). "New" = the new state (Current's text after the edit).
2. **Word-level diff.** Compute changes at the word / phrase boundary, not character-level (too noisy) and not paragraph-level (too coarse). Sentence-level is sometimes appropriate when a whole sentence was rewritten.
3. **Render to HTML** per the rules above (`<del>` / `<ins>` / `.comment`). Format surrounding markdown as HTML.
4. **Write back to the .html** in the appropriate `## Changes for X` section.

**For an MVP, the agent can do this inline** using Read+Edit on the .html. A Python helper script could be added later if accuracy/speed becomes a problem; word-level diff with Python's `difflib` is straightforward.

## Provenance + writeback

The `## Provenance` H2 (last H2 in the .md) is the agent's anchor for round-trip. Its body has:

1. **Human-readable paragraph** — what was extracted, from where, any nuance about the boundary (paragraph index, "skip the first sentence which is an intro," etc.).
2. **Optional `::` dataview fields** — used when the value is precisely known:
   - `source_path::` — absolute file path
   - `source_section::` — H2/H3 heading name
   - `source_block_id::` — Obsidian block-ID (`^abc123`)
   - `source_line_range::` — line range at extraction time (drifts; informational only)

**On `writeback`:** read `## Provenance`, then read the source file fresh, then locate the region by content reasoning. Dataview fields are *hints*; the agent re-locates by content if the section has moved or been renamed. Line numbers are never trusted — they drift.

If the source has been substantially edited in the target region since extraction (the V0 text isn't recognizably in the current source), surface to the user before writing.

## Glance discipline

**Every time the agent edits `## Current` or writes a new version, glance both files.** The glance is the feedback loop that catches misinterpreted edits.

```bash
open "$HOME/ob/kmr/Log/REDLINE/<stem>.md"
open "$HOME/ob/kmr/Log/REDLINE/<stem>.html"
```

Never glance the .md without the .html — they're a pair; the user needs to see both to understand what happened.

**Exception:** `/redline close` and `/redline writeback` don't glance (they're terminal actions; surface the result in chat instead).

## Anti-patterns

- **Don't auto-accept.** `redline accept` is the user's verb. The agent never advances the version number on its own.
- **Don't accept just before writeback.** Accept is not a prerequisite for writeback — writeback uses Current's text directly. Adding an automatic accept on every writeback would create empty milestones in the version stack.
- **Don't write a `## Changes for Version 0` H2.** V0 is the extracted original; there's nothing before it.
- **Don't reorder accepted versions.** Once `## Version N` and `## Changes for Version N` are written, they're immutable. Insertion is always at the top of the stack (above the current top of accepted versions).
- **Don't track who-edited-what** in the version history. The diff just shows V_N → Current; provenance of each change is not recorded. Symmetry between user-edits and agent-edits is intentional.
- **Don't ask "should I accept?"** Accept is the user's decision; the agent never asks. If the user is silent after an edit, the agent stays in redline-context and waits for the next directive.
- **Don't reformat or restructure.** When the user asks for a polish edit, change what was named. Don't take the opportunity to "also fix" things the user didn't ask about. (If the agent has a strong suggestion, frame as a suggestion — bucket 2 — not a direct edit.)
- **Don't lose the Provenance.** When editing the .md, never touch the `## Provenance` H2 or its body. It's the writeback anchor.

## Notes

- The file paths are stable: `~/ob/kmr/Log/REDLINE/<YYYY-MM-DD> — <title>.{md,html}`. Always.
- If `~/ob/kmr/Log/REDLINE/` doesn't exist, create it on first session.
- Title-slug collisions on the same date are unlikely if titles are content-bearing; if one happens, suffix with `-2` / `-3` etc. on the second / third session.
- The session files are durable — they stay in `Log/REDLINE/` after writeback or close. They're the record of how the polish unfolded; useful for review or for going back to a prior version.
- **For very long passages** (more than a page or two), point the user at the out-of-scope folder-based mode (F112 § Out of scope) — this skill ships single-file mode only.
