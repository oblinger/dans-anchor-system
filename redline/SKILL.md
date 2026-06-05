---
description: Collaborative text-polish skill — two modes. **Section mode** (F112): polish a passage (up to a page or two) extracted from a source location, with round-trip writeback. **File mode** (F114): polish a whole document in-place inside an anchor folder, with versioned dated copies + per-section diff HTMLs + no writeback.
tools: Read, Edit, Write, Bash
user_invocable: true
---

# Redline — Versioned Text Polish with Track-Changes

Collaborative polish of text with visible, addressable pending changes and a navigable acceptance history. Two modes:

| Mode | Spec | What it polishes | Workspace |
|---|---|---|---|
| **Section** | `[[F112 — Redline]]` | A passage extracted from a source (up to a page or two) | `~/ob/kmr/Log/REDLINE/` (then writeback to source) |
| **File** | `[[F114 — Redline file mode — versioned in-place polish of a whole document]]` | A whole document (multi-page) | The document's anchor folder (in-place; no writeback) |

HTML diff convention for both: `[[md-track-changes]]`. Sibling to `[[snip]]` (rough-text-drop) and `[[md]]` (markdown utility skill).

## When to Use

Invoke when the user says:

**Section mode (F112):**
- `/redline start <source>` — open a polish session on the named source passage
- `/redline writeback` — apply the latest accepted version back to the source
- `/redline close` — leave redline-mode without writeback

**File mode (F114):**
- `/redline file <path> [<slug>]` — open or resume a whole-document polish session in an anchor folder
- `/redline resplit` — re-propose the section split structure

**Both modes:**
- `/redline show [<arg>]` — open the most-recent or named session
- `/redline accept` — snapshot Current as a new accepted version

**When NOT to use:** rough-text-drop / one-shot refinement → `/snip`.

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
- **For whole-document polish** (multi-page paper, proposal, long memo) — switch to **file mode** below (`/redline file <path> [<slug>]`).

---

# File mode (F114)

Whole-document polish in-place inside an anchor folder. Distinct from section mode above — different invocation, different layout, **no writeback** (the document IS the canonical artifact). Spec: `[[F114 — Redline file mode — versioned in-place polish of a whole document]]`.

## When to Use (file mode)

When the user wants to polish a multi-page document (a paper, a long memo, a proposal draft) inside its anchor folder. Triggers:

- `/redline file <path> [<slug>]` — start or resume a file-redline session
- `/redline accept` (when a file session is active) — snapshot Current as a new dated version + per-section HTMLs
- `/redline resplit` — re-propose the section split structure
- `/redline show [<slug>]` — open / re-enter a file-redline session by anchor

**Mode disambiguation.** If the user says `/redline file …`, it's file mode. If they say `/redline start …`, it's section mode. For `/redline accept` and `/redline show`, look at the active session context: if a `{slug} Current.md` exists in an anchor and is the most-recently-touched session, that's the active file-mode session.

## Files (file mode)

Per session, files live **inside the anchor folder** named for the slug:

| File | Content |
|---|---|
| `{slug} Current.md` | Live workspace (always-editable) |
| `{slug} YYYY-MM-DD.md` | Original (V0) — copied from source on first invocation |
| `{slug} YYYY-MM-DD [SUFFIX].md` | Subsequent accepted versions; same-day suffix B/C/… |
| `{slug} YYYY-MM-DD [SUFFIX] s{N}.html` | Per-section diff HTML for that version |

The **split structure** (what each `s{N}` represents) lives in the **Notes column of the anchor page's `## Version history` table**. The Notes column is the source of truth for the split. User can edit it anytime to change the split; agent reads it on every operation and regenerates affected HTMLs.

## Sub-commands (file mode)

### `/redline file <path> [<slug>]` — open or resume a session

1. **Resolve the file path.** Natural language is fine — agent interprets a path, a tilde-prefixed path, a quoted excerpt referencing a file, or a gestural reference.
2. **Resolve the slug.**
   - If `<slug>` is given explicitly → use it. Slug must resolve to an existing anchor (look for a folder with `.anchor` marker whose anchor page name is `{slug}.md`). If the slug doesn't resolve, error.
   - If no slug given → fall back to the slug of the anchor folder containing the file (walk up from the file's directory looking for `.anchor`). If the file is not in any anchor, error: "no slug given and file is not inside an anchor folder."
3. **Detect resume vs fresh.**
   - If `{anchor folder}/{slug} Current.md` already exists → **resume**. Glance the anchor page (which carries the version-history table) and `{slug} Current.md`. Enter redline-context for this file-mode session. Stop here.
   - Otherwise → **fresh start.** Continue to step 4.
4. **Copy the file into the anchor folder** as `{slug} <today's date>.md` (today's date = current local date in `YYYY-MM-DD` format, e.g., `2026-06-05`). If a file with that exact name already exists, append a same-day suffix (`B`, `C`, …). This is V0.
5. **Propose a section split (auto-apply, no confirmation).** Read the file. Identify H2 (and optionally H3) heading structure. Choose a split:
   - If H2 headings exist and sections are reasonably sized (half-page to 2 pages each) → use H2 boundaries.
   - If some H2 sections are too short → merge adjacent ones inline. Name the merged section with a hyphen-joined name (`s5: Parametric Generation through Realism`).
   - If no H2 headings or some sections too long → inject HTML-comment markers (`<!-- S1 -->`, `<!-- S2 -->`, …) at natural paragraph boundaries. Target ~1-page sections. Agent-generates descriptive section names.
6. **Create `{slug} Current.md`** in the same folder, identical content to V0 (including any HTML-comment markers added in step 5).
7. **Update the anchor page's `## Version history` table.**
   - If no `## Version history` H2 exists in the anchor page → create one near the bottom (after the dispatch table, before any other H2s).
   - Insert a new row at the **top** of the version-history table (reverse-chronological order):
     ```
     | [[{slug} YYYY-MM-DD]] | (original) | s1: <Name 1><br>s2: <Name 2><br>… s{N}: <Name N> |
     ```
   - The Notes column carries the split. This is now the source of truth for what each `s{N}` represents.
8. **Glance the anchor page + `{slug} Current.md`.** The user sees the version timeline (with the split in Notes) and the live document.
9. **Enter redline-context for this file-mode session.**

### `/redline accept` — snapshot Current as a new dated version

Pre-condition: a file-mode session is active (i.e., `{slug} Current.md` exists in the active anchor).

1. **Read the active session state:**
   - Read `{slug} Current.md` (the new text being accepted).
   - Read the latest accepted version `{slug} <prev-date>[<prev-suffix>].md` (the comparison baseline).
   - Read the latest split from the anchor page's `## Version history` table (the Notes column of the latest row).
2. **Pick today's version name.** Today's date in `YYYY-MM-DD` form. If a file with that exact name already exists in the folder (i.e., another accept happened today), append a same-day suffix: `B`, then `C`, etc. (E.g., `ABP 2026-06-05.md` already exists → new version is `ABP 2026-06-05 B.md`. If that also exists → `ABP 2026-06-05 C.md`.)
3. **Write the new version file** as `{slug} <new-date-with-suffix>.md` with Current's text verbatim.
4. **Detect the split** as described in the version-history table's Notes column. Split Current and the prior version into sections according to the latest split definition.
5. **Generate per-section diff HTMLs** named `{slug} <new-date-with-suffix> s1.html`, `s2.html`, etc. Each HTML uses the `[[md-track-changes]]` convention (`<del>`/`<ins>`/`.comment` markup) showing the diff between the prior version's section N and the new version's section N. **Sections with no changes still get an empty-diff HTML** — the file exists so the version-history table's row is complete; opening it confirms "no changes here, scanned."
6. **Update the anchor page's `## Version history` table.** Insert a new row at the top:
   ```
   | [[{slug} <new-date-with-suffix>]] | [[{slug} <new-date> s1.html\|s1]] [[… s2.html\|s2]] … [[… s{N}.html\|s{N}]] | (Notes column inherits from prior row unless split changed) |
   ```
7. **Leave `{slug} Current.md` unchanged.** It already equals the new accepted version (Current's text was just snapshotted).
8. **Glance the anchor page** so the user sees the new row + section HTML links.

### Split mutation — when the user edits the Notes column

The split is **mutable state** in the Notes column of the version-history table. The user can edit Notes any time to change the split structure (rename a section, merge two, split one, renumber, etc.).

**Agent detects on next interaction:**

1. On every file-mode interaction (edit Current, `/redline accept`, `/redline show`, etc.), the agent reads the Notes column of the **latest accepted version's row** + the Notes column of the row currently being computed against (if doing a diff).
2. If the Notes content differs from what the agent last applied (track via a small `.redline-state.json` file in the anchor folder, OR by computing a hash of the Notes content and storing it next to the version row → simpler: just re-read the Notes every time and recompute), regenerate the affected section HTMLs.
3. **Propagation rule:** when the Notes column changes for the *latest accepted version's row*, also update the row below it (the prior version) — wait, no. The split applies to a *pair*: latest-accepted vs Current. Both sides need the same split definition for the diff math to be meaningful. So the propagation is: latest-accepted's row Notes is the split for everything from-then-onward. Edit there propagates to Current's split too (Current doesn't have a row of its own; it inherits the latest accepted's split).
4. **Historical versions stay immutable.** Their Notes columns and section HTMLs reflect the split they used at their accept time. Only the **latest** baseline-vs-Current pair regenerates on edit.

### `/redline resplit` — agent re-proposes the split

User invokes when they want a fresh agent proposal (rather than hand-editing the Notes column). Procedure:

1. Read `{slug} Current.md`.
2. Re-run the split-choice heuristic from `/redline file` step 5.
3. Write the new split into the Notes column of the latest version's row in the version-history table.
4. Regenerate the section HTMLs for the latest accepted version (using the new split, against the prior version).
5. Glance the anchor page so the user sees the updated split.

### `/redline show [<slug>]` — re-enter a file-mode session

1. **Resolve the slug.** Explicit arg → use it. No arg → use the most-recently-modified `{slug} Current.md` across all anchors.
2. **Glance the anchor page** (which carries the version-history table) and `{slug} Current.md`.
3. **Enter redline-context** for this file-mode session.

## Conversational edit-mode (file mode)

Same three-bucket classification as section mode (edit directive / edit suggestion / off-topic). The only differences:

- **Edit target is `{slug} Current.md`** (the file in the anchor folder), not a `## Current` H2 in a workspace file.
- **Glance target on every edit is `{slug} Current.md` + the anchor page** (so the user sees what changed in Current + the version-history table).
- **No writeback** — `accept` is the only persistence verb; there's no round-trip to a source file.

## Anti-patterns (file mode)

In addition to the section-mode anti-patterns above:

- **Don't writeback.** File mode has no `writeback` — the document IS the canonical artifact. If the user says "writeback," gently correct: "File-mode sessions don't writeback; the file is already in its final location. Did you mean `accept`?"
- **Don't auto-accept on file edit.** Same rule as section mode — accept is the user's verb.
- **Don't regenerate historical versions' HTMLs.** Once a version's `s{N}.html` files are written, they're immutable. Only the latest-baseline-vs-Current pair regenerates on split mutation.
- **Don't lose the split.** The Notes column of the version-history table is the source of truth for the split. Never overwrite it without preserving content; never delete a row's Notes column accidentally.
- **Don't use `.anchor` to determine the active session.** The active session is determined by which `{slug} Current.md` is most-recently-touched. `.anchor` just marks the folder as an anchor; it has no session-state semantics.
- **Don't break the slug-prefix invariant.** Every file the skill creates is named `{slug} …`. If the slug is `ABP`, files are `ABP 2026-06-05.md`, `ABP Current.md`, `ABP 2026-06-05 s1.html`, etc. Never `Alien Biology Paper.md` or other variants.

## Notes (file mode)

- The session "active" state is implicit: it's whichever `{slug} Current.md` is most-recently-edited across all anchors. No global state file.
- Same-day version naming: first accept of the day → `{slug} YYYY-MM-DD.md` (no suffix); second → `{slug} YYYY-MM-DD B.md`; third → `{slug} YYYY-MM-DD C.md`; etc. Reverse-chronological in the version-history table.
- The `Current` file name is `{slug} Current.md` (capitalized `Current`).
- ✓ checkmarks the user may add to section links in the version-history table are **user-maintained, skill-ignored**. They're a personal tracking convenience.
- If the anchor doesn't have a `## Version history` H2 in its page yet, `/redline file` creates one on first invocation.
- For non-markdown file types (HTML, PDF, DOC, plaintext) — **out of scope for v1**. File mode is markdown-only initially.
