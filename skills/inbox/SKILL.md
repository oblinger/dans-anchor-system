---
name: inbox
description: >
  Drains the current anchor's [[DAS Inbox]] — reads every PENDING entry
  (raw input dropped in by another agent or the user via `state drop`),
  integrates each one into the right planning surface (Backlog, PRD,
  Roadmap, Discussion, or handled in place), and marks it processed with
  the sanctioned status tag (`DONE` or `MOVED → {destination}`) via
  `state inbox-tag`. Never hand-edits the Inbox markdown directly. Use
  when the user says "/inbox", "drain the inbox", "check the inbox",
  "process the inbox", or when the status banner shows `Inbox N` with
  N > 0. T131 leg 3 — the drain half of the agent-inbox pattern (leg 1:
  `state drop`; leg 2: the `Inbox N` banner signal).
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Inbox — Drain the Anchor's Drop Zone
requires:: vault, anchor-cli, skill:workflow, facet:inbox

The runbook for `/inbox` — reads the current anchor's pending Inbox entries, integrates each into the right planning surface, and writes the sanctioned status tag back through `state`.

`/inbox` is the third and final leg of the agent-inbox pattern ([[ATT045 - Agent inbox pattern]], [[TINK Backlog#^T395|T395]]): leg 1 (`state drop`) lets any agent hand another anchor a message without executing anything; leg 2 (`Inbox N` on the status banner) makes a pending drop visible; this skill is what actually reads and acts on it.

## Trigger

- Slash: **`/inbox`**
- Natural language: "drain the inbox", "process the inbox", "check the inbox", "what's in the inbox".
- Passive: the anchor's status banner shows `Inbox N` (N > 0) — per the vault-wide session-start convention in `~/ob/kmr/CLAUDE.md` § Check your anchor's Inbox at session start.

## What "pending" means — never re-derive it

An Inbox entry is a dated H2 (`## YYYY-MM-DD — Topic`); it is **pending** iff no sanctioned status tag (`` `DONE` `` or `` `MOVED → {destination}` ``) appears anywhere inside it. This is [[DAS Inbox]]'s definition (R-fct-inbox-02/-03), and it is also exactly what `count_pending_inbox` counts and the `Inbox N` banner reports. **Don't eyeball the file for this** — `state inbox-list <anchor>` already applies the identical regexes and prints only pending entries' markdown verbatim. A drain that disagreed with the banner about which entries qualify is the exact failure this project already hit once; the fix was making both sides import the same regexes instead of each spelling the rule out separately, and this skill inherits that fix by going through `inbox-list` rather than reading the raw file itself.

## Anchor resolution

Walk up from `cwd` to the nearest `.anchor` — same procedure `/crank` § Runbook 1 uses. If none is found, say so and stop; `/inbox` never guesses which anchor it is draining. Pass the resolved **directory** straight to `state` as the `<anchor>` argument (`state`'s own `ANCHOR RESOLUTION` mode 2 reads the slug off that directory's `.anchor` file) — this reuses `state`'s existing anchor-resolution helper rather than re-deriving the slug by hand.

`/inbox` drains **only the current anchor**. It never reaches into another anchor's Inbox uninvited, for the same reason `/crank` never scavenges another anchor's Ready queue — the user did not authorize that scope from this session.

## Runbook

### 1. List what's pending

```
~/.claude/skills/workflow/scripts/state inbox-list <anchor>
```

Prints every pending entry's full markdown (heading + attribution line + body) to stdout, oldest-drop-last (file order). If it prints nothing, the Inbox is clean — report that in one line and stop. Nothing else in this skill runs on an empty list.

### 2. For each pending entry, in the order printed

a. **Read it.** The heading names the date and topic; the body (usually a blockquote of the original message, plus an optional `*from: … · tag: …*` attribution line) is the actual content to act on.

b. **Decide the destination**, per [[DAS Inbox]] § Lifecycle — integrate into whichever planning surface the content actually belongs to:
   - A concrete piece of work → a Backlog row (`state define <anchor> Backlog T+ …` or `F+`/`C+` as appropriate).
   - A design thought, a discussion point → the anchor's Discussion doc or a feature doc's `## Open Questions` (`state define <anchor> <doc> Q+ …`).
   - A roadmap-level item → the Roadmap.
   - Something that requires no further action beyond having been read (an FYI, a status note, an already-actioned fact) → handled in place, no destination doc.

   Use the sanctioned writer for whatever surface receives it — `state define`/`set` for Backlog rows and doc Qs, the normal editing path for prose docs. `/inbox` never invents a new writing path for content it is relocating; it uses the same tools `/mint`, `/groom`, and hand-editing already use for that surface.

c. **If the right destination is genuinely ambiguous** — real uncertainty, not just inconvenience — leave the entry untagged and either ask inline (if the answer is needed to keep going) or route it through `/ask` like any other open question. An entry that stays pending because it is waiting on a real answer is not a failure of this skill; tagging it before the ambiguity resolves would be worse, because it would make the entry invisible to the banner while still actually unresolved.

d. **Write the tag** once the content has genuinely landed somewhere (or been fully handled in place):

```
~/.claude/skills/workflow/scripts/state inbox-tag <anchor> --date YYYY-MM-DD [--topic "substring"] --tag "DONE"
~/.claude/skills/workflow/scripts/state inbox-tag <anchor> --date YYYY-MM-DD [--topic "substring"] --tag "MOVED → {destination}"
```

   `--topic` is only needed to disambiguate two entries dropped the same day — `inbox-tag` refuses (naming the candidates) if the date alone doesn't pick one entry. `--date`/`--topic` must match what `inbox-list` printed for that entry; **never guess or retype the topic** — copy it from the heading `inbox-list` just showed.

   - Use **`DONE`** when the entry was processed in place — nothing to point to.
   - Use **`MOVED → {destination}`** when content moved somewhere with an address — name the actual place (`TINK Backlog#T131`, `[[HA Roadmap#M3]]`, a doc heading). **Never write a bare `MOVED`** — `inbox-tag` refuses it outright (R-fct-inbox: a reader who later finds `MOVED` with no destination learns nothing about where the content went), so there is nothing to remember here beyond naming the real place.
   - `inbox-tag` refuses an already-tagged entry and refuses any tag outside this two-value vocabulary — it is the enforcement point, not a courtesy, so a mistake here surfaces immediately rather than drifting into the file.

### 3. Close out

Re-run `state inbox-list <anchor>` (no output = fully drained) or just track counts while processing. Report one line: how many entries were tagged `DONE`, how many `MOVED → …` (naming each destination briefly), and how many are still pending and why (an open question, waiting on the user). A still-pending entry after a drain is not an error — it just means the entry keeps showing in `Inbox N` until the thing it's waiting on resolves.

## Anti-patterns

- **Hand-editing the Inbox markdown.** Every write to `{slug} Inbox.md` goes through `state drop` (sending) or `state inbox-tag` (marking processed) — never Edit/Write on the file directly. The vocabulary and the landed-check both live in `state`; a hand edit bypasses both.
- **Inventing a third tag.** `DONE` and `MOVED → {destination}` are the whole vocabulary (R-fct-inbox-03). `inbox-tag` refuses anything else, so there should never be a reason to try.
- **A bare `MOVED`.** Always name the destination. `inbox-tag` refuses a destination-less `MOVED` outright.
- **Re-deriving "pending" by reading the raw file.** Always go through `state inbox-list`, which applies the same regexes the `Inbox N` banner and `count_pending_inbox` do. A hand-eyeballed read risks disagreeing with the banner about which entries qualify — the exact bug this project already shipped once.
- **Tagging an entry before its content actually landed somewhere.** The tag is a claim that the content is handled; write it after the destination edit, not before.
- **Draining another anchor's Inbox uninvited.** `/inbox` is scoped to the current anchor, same as `/crank`.

## Cross-references

- **[[DAS Inbox]]** — the file-shape spec this skill conforms to (not restates).
- **[[R-fct-inbox]]** — the checked rules (`inbox_in_track_folder`, `inbox_entry_headings`, `inbox_status_tags`) any drained file must still satisfy.
- **`state drop` / `state inbox-list` / `state inbox-tag`** (`~/.claude/skills/workflow/scripts/state`) — the sending, reading, and writing verbs T131's three legs shipped.
- **`/crank`** — same anchor-scoping discipline (§ Anchor resolution above); does not itself invoke `/inbox` as part of its cascade.
- **`/ask`** — where a genuinely ambiguous entry's destination question gets parked, rather than guessed.
