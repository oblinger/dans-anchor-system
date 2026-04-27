---
name: snip
description: >
  Capture rough text drops and refine them inline. Use when the user says `/snip <text>` (or the
  word "snip" gets auto-prefixed as `/snip` by the dictation pipeline). With an argument: prepend a
  new dated H2 entry to `~/ob/kmr/Log/SNIP/SNIP.md` containing the raw text + an AI-refined
  version, separated by a `---refined---` marker. With no argument: re-refine the top entry — use
  this after the user has added more raw text to the top H2 section and wants another pass.
tools: Read, Edit, Write, Bash
user_invocable: true
---

# snip — Rough-text Drop + Refine

Capture quick, rough text and produce a polished version alongside it. Designed for dictation or hasty typing where the user wants a cleaned-up version without thinking about formatting, filenames, or whether the entry already exists.

## File

All entries live in a single file: **`~/ob/kmr/Log/SNIP/SNIP.md`**.

Entries are H2 sections in reverse chronological order (newest at top). Each section has this shape:

```
## YYYY-MM-DD — short slug

<raw text — what the user dictated or typed, verbatim>

---refined---

<polished version>
```

The `---refined---` marker separates raw (above) from refined (below). The marker sits on its own line.

## Actions

### `/snip <text>` — new entry (text supplied)

1. Read `~/ob/kmr/Log/SNIP/SNIP.md`.
2. Generate a short slug that captures the **topic or action** of the drop, not the literal opening words. 3–5 content-bearing words, lowercase, hyphen-separated. Skip conversational openers ("okay", "yeah", "let's", "so", "hey"), hedges ("I think", "kind of", "maybe"), and filler. Name the main subject, object, or action the entry is *about*. Examples:
   - raw: "Okay, let's update the skill so it glances the file" → `update-skill-to-glance` ✓ (not `lets-update-the-skill`)
   - raw: "Yeah, go with B and call it Skill" → `naming-go-with-b` ✓ (not `yeah-go-with-b`)
   - raw: "Let's see if it works" → `test-drop` ✓ (not `lets-see-if-works`)
   - raw: "Note to self on the hotel receipt thing" → `hotel-receipt-note` ✓
   If the content is too thin to extract a meaningful topic (e.g., just "test"), fall back to `test-drop` or a similar generic-but-informative fallback. Never return a slug that is purely filler words.
3. Build a new H2 header: `## YYYY-MM-DD — <slug>` using today's date in ISO format.
4. Produce a refined version of `<text>` per the **Refinement style** section below.
5. Assemble the new section:
   ```
   ## YYYY-MM-DD — <slug>
   
   <text verbatim>
   
   ---refined---
   
   <refined text>
   ```
6. Insert the new section at the top of the body — immediately after the dispatch table, `#log` tag, and the usage-note paragraph. Before any existing H2 sections.
7. **Copy the refined text to the clipboard** so the user can paste immediately with Cmd+V:
   `printf '%s' "<refined>" | pbcopy`
   (Use `printf '%s'` not `echo` — avoids backslash/newline mangling with multi-line refined text.)
8. Glance the file so the user can see the result: `open "$HOME/ob/kmr/Log/SNIP/SNIP.md"`.

### `/snip` — re-refine top entry (no argument)

1. Read `~/ob/kmr/Log/SNIP/SNIP.md`.
2. Find the topmost `## ` H2 section.
3. Within that section, locate the `---refined---` marker.
4. Extract everything between the H2 header and the marker — this is the current raw text (the user may have appended new material).
5. Delete everything from the marker line to the next `## ` header (or end of file if this is the only section).
6. Produce a fresh refined version from the current raw text.
7. Write back: the marker line, a blank line, then the new refined text.
8. **Copy the refined text to the clipboard** so the user can paste immediately with Cmd+V:
   `printf '%s' "<refined>" | pbcopy`
9. Glance the file so the user can see the result: `open "$HOME/ob/kmr/Log/SNIP/SNIP.md"`.

**Defensive case:** if no `---refined---` marker is found in the top entry, treat everything under the H2 header as raw, then append the marker + refined version.

## Refinement style

- Fix spelling, grammar, punctuation, and obvious transcription errors (especially homophones from voice recognition: "to"/"two"/"too", "there"/"their", "hear"/"here").
- Tighten phrasing: remove filler ("like", "you know", "kind of", "basically", "I mean").
- Preserve voice, intent, and register — don't upgrade casual prose into corporate writing.
- Approximately the same length; shorter only if there's real redundancy.
- Don't add information the user didn't include.
- If the text is a list or has clear structure in the raw, preserve that structure in the refined version.
- If the raw text is incoherent or the intent is ambiguous, produce the best-effort refinement and note the ambiguity in a short parenthetical at the end (e.g., `(ambiguous: "it" may refer to X or Y)`).

## Notes

- The file path is stable. Always `~/ob/kmr/Log/SNIP/SNIP.md`. Don't prompt the user for a file.
- Don't modify the dispatch table, `#log` tag, or the usage-note paragraph at the top of the file.
- If the file doesn't exist, something is wrong with the setup — error out with a clear message rather than creating it.
- Don't touch any section other than the top one when re-refining.
