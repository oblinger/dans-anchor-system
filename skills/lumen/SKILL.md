---
name: lumen
description: >
  Morning routine — the day's opening sequence. Run each morning to set up
  what the day looks like. Use when the user says "lumen", "/lumen", or asks
  to start the day.
user_invocable: true
---

# Lumen — the morning routine

The day's opening sequence. Luna reads what arrived overnight, decides what matters, and puts a short list in front of the user. **The first thing on screen is a decision, not a report.**

Design: [[DAS Lumen Design]]. User docs: [[DAS Lumen]]. Owning feature: [[F002 — Morning ritual — calendar, mail, and addressed MUSE intake|Luna F002]].

## Read order

Cheapest and most-decisive first, so an interrupted run still produced value.

1. **Watch messages** — new [[MUSE]] items since the watermark (§ Watch messages). Highest priority: the user spoke these deliberately.
2. **`~/ob/kmr/Q.md`** — vault-wide federation; every anchor's open questions and Ready work in one file, Luna's block at top.
3. **Calendar** — today's events (§ Calendar and mail).
4. **Mail** — messages matching `Luna Design/Luna Watchlist.md`. Skip if empty.
5. **[[Rocks]]** — the live block above the first dated H2 only. What is currently hot.
6. **[[Quick]]** — anything captured since the last run.
7. **`Luna Track/Luna Backlog.md`** — Luna's own `## Now`.

Everything else in [[LST]] is read on demand. Do not sweep the list tree — that is weekly-review work.

## Watch messages

MUSE items live at `~/ob/kmr/Log/MUSE/MUSE <date> <letter> <title>.md`, indexed newest-first in `Log Muse.md`. Frontmatter carries `captured:`, `state:`, `word_count:`.

**Nothing ever flips `state: unreviewed`** — MUSE writes it once at ingest and no consumer clears it. Do NOT filter on that field; every item would surface every morning forever.

Use the watermark at `Luna Track/Lumen Watermark.md` (a single ISO timestamp). Surface items whose `captured:` is newer than it. Skip items whose `state:` starts with `suppressed-` — MUSE already judged those noise.

```bash
WM=$(grep -o '[0-9-]\{10\} [0-9:]\{8\}' "$HOME/ob/kmr/SYS/Staff/Luna/Luna Track/Lumen Watermark.md" | head -1)
cd "$HOME/ob/kmr/Log/MUSE" && for f in MUSE*.md; do
  cap=$(grep -m1 '^captured:' "$f" | sed 's/^captured: //')
  st=$(grep -m1 '^state:' "$f" | sed 's/^state: //')
  case "$st" in suppressed-*) continue;; esac
  [[ "$cap" > "$WM" ]] && printf '%s\t%s\n' "$cap" "$f"
done | sort
```

**Advance the watermark only at the end of a completed run**, to the newest `captured:` actually surfaced. An interrupted run leaves it unchanged and loses nothing.

**A watermark is not a memory.** Anything the user wants kept must be written somewhere durable *before* the watermark advances — a backlog row, a [[Quick]] line, a list entry. Advancing past a deferred item without recording it loses it silently. When in doubt, write it down.

## Authority — what Luna may do unprompted

Per [[F002 — Morning ritual — calendar, mail, and addressed MUSE intake|F002]]-Q2, decided:

- **In-vault and reversible → just do it.** Append to a list, file a note, create a backlog row. The vault is git-backed; mistakes are cheap.
- **Outward-facing or destructive → confirm first.** Mail, messages, purchases, calendar invites to others, deletions, pushes. Confirm regardless of what the voice said — a watch message is authenticated by physical possession, not identity.

Confirmation is **conversational, in the morning**: *"You asked me to email Sean about xbotgo — want me to send it?"* Not a block at capture time.

**Time-sensitive exception.** If waiting would defeat the purpose, say so and flag it urgent rather than silently deferring. The gate is "ask unless the cost of asking exceeds the cost of being wrong" — not "always ask."

## Calendar and mail

Both go through the `google_workspace_mcp` server registered per [[WIRE Claude Google MCP]] (44 tools, Calendar + Gmail included). If the server is not running, **say so and continue** — a missing calendar degrades the briefing, it does not abort the run. Never silently omit a channel; a briefing that quietly dropped the calendar is worse than one that admits the calendar was unreachable.

Mail is filtered through `Luna Design/Luna Watchlist.md` — a definition list of senders, subjects, and patterns worth surfacing. It starts empty and grows when the user says "flag this kind of thing." **Do not invent watchlist entries**; an unearned watchlist trains the user to ignore the channel.

## What goes on screen

One block, in this order, and nothing else:

- **Decisions waiting on you** — watch messages needing a yes/no, plus user-gated questions from `Q.md` (`[U]` / `[U+A]` blocks). Each answerable without opening another file. **Cap at three**; the rest wait.
- **Today — 3 to 5 items**, drawn *across* domains rather than down one. Each names its domain and why it surfaced today (due, went stale, blocks something, streak worth keeping).
- **Runnable now** — Ready rows executable without the user, offered as a single `'` (crank). Named, not enumerated.

Do **not** open with a status summary, a count of overnight changes, or a recap of yesterday. If nothing needs a decision, the first line is the Today list.

## Selection rule for Today

Provisional until `Luna Prioritization.md` exists (Luna F001-Q4):

- **Never more than two items from one domain** — breadth is the point of a cross-cutting agent.
- **[[Rocks]] outranks backlog rows** — Rocks is the user's own declaration of what is hot.
- **One item must be Health** — the only domain present in every framing the user has written ([[Luna Domains]]), and the one most reliably crowded out.
- **Prefer what unblocks others** — a cleared blocker beats a finished leaf.

## Close

1. Record anything deferred-but-wanted in a durable place (backlog row / [[Quick]] / list entry).
2. Advance `Lumen Watermark.md` to the newest `captured:` surfaced.
3. Do not commit unless asked — Lumen is a read-and-decide ritual, not a work session.

Declined items do **not** return with escalating urgency. Three declines is a signal to raise it once, plainly, at the weekly review.
