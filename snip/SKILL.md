---
name: snip
description: >
  Capture rough text drops and iteratively refine them. Use when the user says `/snip <text>` (or
  the word "snip" gets auto-prefixed as `/snip` by the dictation pipeline). Three modes:
  (1) `/snip <text>` with no revise marker drops a new dated H2 entry with two versions
  stacked newest-on-top: `### version 1` (AI refinement) above `### version 0` (raw verbatim).
  (2) `/snip revise <instructions>` — or any args containing `snip <punct/ws> revise` somewhere —
  takes the current top version of the top entry, applies the instructions, and prepends the
  result as the next version. (3) Bare `/snip` re-refines the top version with a generic clean
  pass, prepending the next version. In every case the new top version is pbcopy'd to clipboard
  and the file is glanced.
tools: Read, Edit, Write, Bash
user_invocable: true
---

# snip — Rough-text Drop + Iterative Refine

Capture quick rough text and produce polished versions alongside it. Designed for dictation or hasty typing where the user wants a cleaned-up version without thinking about formatting, filenames, or whether the entry already exists. Each entry accumulates versions; the latest is always on top, and the latest is always on the clipboard ready to paste.

## File

All entries live in a single file: **`~/ob/kmr/Log/SNIP/SNIP.md`**.

Entries are H2 sections in reverse chronological order (newest at top). Each entry contains a stack of `### version N` H3 sub-sections, also in reverse chronological order (newest version on top, version 0 at the bottom):

```
## YYYY-MM-DD — short slug

### version 2 — clean it up
<refined text after the "clean it up" revision>

### version 1
<initial AI refinement of the raw>

### version 0
<raw text — exactly what the user dictated or typed>
```

Each version's H3 header carries the revision instruction in its name (`### version 2 — clean it up`). Version 0 (raw) and version 1 (default refine pass) get bare headers (`### version 0`, `### version 1`) since neither has user-supplied instructions.

## Action selection

The mode is chosen by looking at the args:

1. **Args contain the trigger pattern `snip` followed by `revise` with only punctuation/whitespace between them** — anywhere in the body. Match: `\bsnip\b[\s,.;:]*\brevise\b` (case-insensitive). Or args **begin with** `revise` (case-insensitive, the dictation pipeline already stripped the leading `snip`). → **Revise mode.**

2. **Args are empty / whitespace only.** → **Bare re-refine mode.**

3. **Any other args.** → **New-entry mode.**

For revise mode, the **instructions** are the text from after the matched `revise` word to the end of args. If multiple `snip … revise` patterns appear (rare), use the first one.

The user dictates loosely — they may say "uh, snip, revise, oh, clean it up" and the pipeline preserves the embedded `snip, revise` inside the args rather than pulling them to the front. The trigger pattern handles that. If the args also contain meta-discussion ("this isn't a real invocation", "just illustrating", etc.), the agent uses judgment — when the user is clearly in design-discussion mode about the skill itself, none of the three modes fire.

## Actions

### `/snip <raw text>` — new entry

1. Read `~/ob/kmr/Log/SNIP/SNIP.md`.
2. Generate a short slug that captures the **topic or action** of the drop, not the literal opening words. 3–5 content-bearing words, lowercase, hyphen-separated. Skip conversational openers ("okay", "yeah", "let's", "so", "hey"), hedges ("I think", "kind of", "maybe"), and filler. Name the main subject, object, or action the entry is *about*. Examples:
   - raw: "Okay, let's update the skill so it glances the file" → `update-skill-to-glance` ✓
   - raw: "Yeah, go with B and call it Skill" → `naming-go-with-b` ✓
   - raw: "Note to self on the hotel receipt thing" → `hotel-receipt-note` ✓
   If the content is too thin (e.g., just "test"), fall back to `test-drop`. Never return a slug that is purely filler words.
3. Build a new H2 header: `## YYYY-MM-DD — <slug>` using today's date in ISO format.
4. Produce a refined version of `<raw text>` per the **Refinement style** section below.
5. Assemble the new entry — note the **versions are stacked newest-on-top within the entry**:
   ```
   ## YYYY-MM-DD — <slug>

   ### version 1

   <refined text>

   ### version 0

   <raw text verbatim>
   ```
6. Insert the new entry at the top of the body — immediately after the dispatch table, `#log` tag, and the usage-note paragraph. Before any existing H2 sections.
7. **Copy the latest version (version 1) to the clipboard:**
   `printf '%s' "<refined text>" | pbcopy`
   (Use `printf '%s'` not `echo` — avoids backslash/newline mangling with multi-line text.)
8. Glance the file: `open "$HOME/ob/kmr/Log/SNIP/SNIP.md"`.

### `/snip revise <instructions>` — revise the top entry's top version

1. Read `~/ob/kmr/Log/SNIP/SNIP.md`.
2. Find the topmost `## ` H2 entry.
3. Inside that entry, find the highest `### version N` H3 header (the topmost version, which is the current latest). Call its number `N_top` and its body text `text_top`.
4. Apply `<instructions>` to `text_top`, producing `text_new`. The instructions take precedence over the default refinement style — if the user says "make it longer" or "rephrase as a question," do that even if it diverges from the default style guidance.
5. Prepend a new H3 sub-section directly below the H2 header (above the current top version):
   ```
   ### version <N_top + 1> — <instructions, truncated to one line if long>

   <text_new>

   ```
6. **Copy `text_new` to the clipboard:**
   `printf '%s' "<text_new>" | pbcopy`
7. Glance the file: `open "$HOME/ob/kmr/Log/SNIP/SNIP.md"`.

**Important: the user may have edited the previous top version in place before invoking revise.** Always read the file fresh and operate on whatever's currently there, not on what the agent last produced.

### `/snip` (bare) — re-refine the top entry's top version

Same as revise mode but with no specific instructions. The new version's H3 header is bare (`### version <N_top + 1>`, no instruction phrase). Use the generic refinement style. The user's intent is "another polish pass on whatever I just edited."

1. Read the file.
2. Find the top H2 entry and its top version (`N_top`, `text_top`).
3. Produce a fresh refined version using the generic refinement style — assume the user wants tighter, cleaner, no-new-information.
4. Prepend:
   ```
   ### version <N_top + 1>

   <new text>

   ```
5. Pbcopy and glance.

## Refinement style

- Fix spelling, grammar, punctuation, and obvious transcription errors (especially homophones from voice recognition: "to"/"two"/"too", "there"/"their", "hear"/"here").
- Tighten phrasing: remove filler ("like", "you know", "kind of", "basically", "I mean").
- Preserve voice, intent, and register — don't upgrade casual prose into corporate writing.
- Approximately the same length; shorter only if there's real redundancy.
- Don't add information the user didn't include.
- If the text is a list or has clear structure in the raw, preserve that structure in the refined version.
- Per durable feedback memory: **drop em-dashes** when refining content destined for external authorship-mattering use (interviews, public prose, polished bios). Substitute commas, semicolons, periods, or parentheses. Keep em-dashes in casual or internal drops.
- If the raw text is incoherent or the intent is ambiguous, produce the best-effort refinement and note the ambiguity in a short parenthetical at the end (e.g., `(ambiguous: "it" may refer to X or Y)`).

For **revise mode**, the user's instructions override the defaults. If they say "make it punchier" or "reorder the paragraphs" or "translate to French," do that. The refinement style above is only the fallback when no instructions are given.

## Notes

- The file path is stable. Always `~/ob/kmr/Log/SNIP/SNIP.md`. Don't prompt the user for a file.
- Don't modify the dispatch table, `#log` tag, or the usage-note paragraph at the top of the file.
- If the file doesn't exist, something is wrong with the setup — error out with a clear message rather than creating it.
- Don't touch any entry other than the top one when revising or re-refining.
- **Legacy entries** (the older `---refined---` marker form, before F109) are left as-is. If the user happens to invoke revise or bare-snip when the top entry is in the legacy format, treat the body below `---refined---` as the current top version, produce a new version, and just prepend it in the new H3 format above everything else — no migration of the existing content.
- **Always pbcopy the new top version after writing.** Always glance the file after writing. No exceptions for any mode.
