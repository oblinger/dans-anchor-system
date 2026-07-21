---
name: daybreak
description: >
  Morning routine — the day's opening sequence. Run each morning to set up
  what the day looks like. Use when the user says "daybreak", "/daybreak", or asks
  to start the day.
user_invocable: true
---

# Daybreak — the morning routine

The day's opening sequence. Lumen reads what arrived overnight, decides what matters, and puts a short list in front of the user. **The first thing on screen is a decision, not a report.**

Design: [[DAS Daybreak Design]]. User docs: [[DAS Daybreak]]. Owning feature: [[F002 — Morning ritual — calendar, mail, and addressed MUSE intake|Lumen F002]].

## Daybreak

Every row is one thing Lumen does in the morning, in order. Detail follows below.

| Activity | What Lumen does |
| --- | --- |
| **Messages** | Read what the user dictated into the watch since the watermark. Do the reversible ones; hold the rest for a yes/no. |
| **Questions** | Pull user-gated decisions out of `~/ob/kmr/Q.md` — every anchor's open questions in one file. |
| **Calendar** | Fetch today's events, so nothing time-bound gets missed. |
| **Mail** | Surface only messages matching `LUM Watchlist.md`. Skip entirely if it is empty. |
| **Hot** | Read [[Rocks]] — the live block only — for what the user has declared currently matters. |
| **Loose** | Scan [[Quick]] and Lumen's own `## Now` for anything captured since the last run. |
| **Today** | Choose 3–5 items *across* domains and put them on screen, decisions first. |
| **Stage** | Lift today's quick hits to the top of [[Quick]], above a blank line. Propose the set; add to it. |
| **Week** | Put the ≥30-min items into today's `### <Day>` in this week's [[Weekly]] file, as checkboxes. |
| **Runnable** | Name the Ready work that needs no user, offered as a single `'` (crank). |
| **Ahead** | Read `~/ob/kmr/LUM Ahead.md`; pull anything now due into the briefing's **Watching** section. |
| **Write** | Put the briefing at the top of `~/ob/kmr/LUM Day.md` — the user reads it there, not in chat. |
| **Close** | Write down anything deferred, then advance the watermark. In that order. |

Sources are read cheapest-and-most-decisive first, so an interrupted run still produced value. Watch messages lead because the user already decided those mattered; `Q.md` is second because one file federates every anchor. Everything else in [[LST]] is read on demand — do not sweep the list tree, that is weekly-review work.

## Watch messages

MUSE items live at `~/ob/kmr/Log/MUSE/MUSE <date> <letter> <title>.md`, indexed newest-first in `Log Muse.md`. Frontmatter carries `captured:`, `state:`, `word_count:`.

**Nothing ever flips `state: unreviewed`** — MUSE writes it once at ingest and no consumer clears it. Do NOT filter on that field; every item would surface every morning forever.

Use the watermark at `LUM Track/Daybreak Watermark.md` (a single ISO timestamp). Surface items whose `captured:` is newer than it. Skip items whose `state:` starts with `suppressed-` — MUSE already judged those noise.

```bash
WM=$(grep -o '[0-9-]\{10\} [0-9:]\{8\}' "$HOME/ob/kmr/SYS/Staff/Lumen/LUM Track/Daybreak Watermark.md" | head -1)
cd "$HOME/ob/kmr/Log/MUSE" && for f in MUSE*.md; do
  cap=$(grep -m1 '^captured:' "$f" | sed 's/^captured: //')
  st=$(grep -m1 '^state:' "$f" | sed 's/^state: //')
  case "$st" in suppressed-*) continue;; esac
  [[ "$cap" > "$WM" ]] && printf '%s\t%s\n' "$cap" "$f"
done | sort
```

**Advance the watermark only at the end of a completed run**, to the newest `captured:` actually surfaced. An interrupted run leaves it unchanged and loses nothing.

**A watermark is not a memory.** Anything the user wants kept must be written somewhere durable *before* the watermark advances — a backlog row, a [[Quick]] line, a list entry. Advancing past a deferred item without recording it loses it silently. When in doubt, write it down.

## Authority — what Lumen may do unprompted

Per [[F002 — Morning ritual — calendar, mail, and addressed MUSE intake|F002]]-Q2, decided:

- **In-vault and reversible → just do it.** Append to a list, file a note, create a backlog row. The vault is git-backed; mistakes are cheap.
- **Outward-facing or destructive → confirm first.** Mail, messages, purchases, calendar invites to others, deletions, pushes. Confirm regardless of what the voice said — a watch message is authenticated by physical possession, not identity.

Confirmation is **conversational, in the morning**: *"You asked me to email Sean about xbotgo — want me to send it?"* Not a block at capture time.

**Time-sensitive exception.** If waiting would defeat the purpose, say so and flag it urgent rather than silently deferring. The gate is "ask unless the cost of asking exceeds the cost of being wrong" — not "always ask."

## Calendar and mail

Both go through the `google_workspace_mcp` server registered per [[WIRE Claude Google MCP]] (44 tools, Calendar + Gmail included). If the server is not running, **say so and continue** — a missing calendar degrades the briefing, it does not abort the run. Never silently omit a channel; a briefing that quietly dropped the calendar is worse than one that admits the calendar was unreachable.

Mail is filtered through `LUM Design/LUM Watchlist.md` — a definition list of senders, subjects, and patterns worth surfacing. It starts empty and grows when the user says "flag this kind of thing." **Do not invent watchlist entries**; an unearned watchlist trains the user to ignore the channel.

## What goes on screen

One block, in this order, and nothing else:

- **Decisions waiting on you** — watch messages needing a yes/no, plus user-gated questions from `Q.md` (`[U]` / `[U+A]` blocks). Each answerable without opening another file. **Cap at three**; the rest wait.
- **Today — 3 to 5 items**, drawn *across* domains rather than down one. Each names its domain and why it surfaced today (due, went stale, blocks something, streak worth keeping).
- **Runnable now** — Ready rows executable without the user, offered as a single `'` (crank). Named, not enumerated.

Do **not** open with a status summary, a count of overnight changes, or a recap of yesterday. If nothing needs a decision, the first line is the Today list.

## Staging the day — [[Quick]] and [[Weekly]]

Today's plan gets written into the two lists the user actually works against, **sorted by size**:

| Size | Goes to | Shape |
| --- | --- | --- |
| A couple of minutes | [[Quick]] | plain bullet, lifted to the **top** of the file |
| 30 minutes or more | [[Weekly]] → today's `### <Day>` H3 | `- [ ]` checkbox |

**[[Quick]] staging.** Move the items the user is likely to knock off today to the top of `Quick.md`, then **one blank line**, then everything else untouched. The blank line is the whole convention — it is what makes the day's picks visible at a glance in the HUD. Propose the set rather than deciding it silently, and feel free to *add* items that belong there.

**[[Weekly]] day-list.** This week's file is `~/ob/kmr/LST/Weekly/YYYY-Www.md` (ISO week, zero-padded). Bigger items go under today's `### <Day>-<DD>` H3 as `- [ ]` so the user checks them off through the day. Week-level intentions — rocks, things aimed at the week as a whole — go in the **top block** between the H1 and the first `###`, not under a day.

**Never hand-author a new week file.** It comes from `[[WEEKLY template]]`, which computes Monday's date and wires the prev/next arrows. If this week's file is missing, say so and let the user stamp it.

**On Monday, plan the week first.** Before staging the day, walk last week's file for unfinished `- [ ]` items and propose the week's rocks into the top block. Per [[Weekly]] § BRIEF, a Friday item left unresolved is carry-forward — it gets checked, dropped, or migrated, never silently abandoned.

## Where the briefing goes — [[LUM Day]]

**Chat is not the delivery surface.** The user reacts to the first item, the rest scrolls away, and the briefing is gone. So every run writes the briefing to `~/ob/kmr/LUM Day.md` **and** prints it in chat. The file is the record; chat is the conversation.

That file is **col-1 of the Daily View dashboard** (`CAPS-J D`), toggled in place of [[Work]]. On that same screen the user is simultaneously looking at:

| Dashboard slot | File | What Daybreak does with it |
| --- | --- | --- |
| col-1 top | [[LUM Day]] | write today's briefing here |
| col-1 bottom | [[Quick]] | lift the day's quick hits to the top, above a blank line |
| col-2 bottom | [[Todo]] | read-only — the user's own list |
| col-3/4 top | current [[Weekly]] | put ≥30-min items under today's `### <Day>` H3 |

So the briefing and the lists the user acts from are **all on screen at once**. Writing to `Quick` and `Weekly` is not bookkeeping for later — it is putting the work where their eyes already are.

Shape: today's block goes directly under the H1 as `## <Day> YYYY-MM-DD · W<nn>`, pushing the previous day down. Never rewrite a past day. Sections in fixed order — **Decisions / Today / Runnable / Gaps** — per the file's own `# BRIEF`. Keep lines short; it renders in one narrow column, so wide tables wrap and destroy the glance value.

## What Lumen is holding — [[LUM Ahead]]

`~/ob/kmr/LUM Ahead.md` is the forward-looking commitment surface: a **table**, soonest-first, of things Lumen owes the user a nudge about. Read it every run; surface anything now due in the briefing's **Watching** section.

**Do not put these on the backlog.** The backlog holds work the agent does to *build things* — horizons, next-actions, features. LUM Ahead holds things about the *user's life* that the agent is carrying for them. Different kind of item, different reader, different shape. The user does not read the backlog, and making them would defeat the point.

**Writing a row is how Lumen remembers.** Any time the user defers something, or asks to be reminded, or an outward-facing action is held pending their go — add a row with its raising condition (a date, an event, or "waiting on you"). A promise made only in chat is a promise lost.

**Rows leave when they fire.** Raised and settled, or raised and declined → delete the row. Declined items do not return with escalating urgency.

**Keep it a table.** Three columns, one line per row. It exists to be glanced at; the moment it needs scrolling it has stopped working.

## Selection rule for Today

Provisional until `LUM Prioritization.md` exists (Lumen F001-Q4):

- **Never more than two items from one domain** — breadth is the point of a cross-cutting agent.
- **[[Rocks]] outranks backlog rows** — Rocks is the user's own declaration of what is hot.
- **One item must be Health** — the only domain present in every framing the user has written ([[LUM Domains]]), and the one most reliably crowded out.
- **Prefer what unblocks others** — a cleared blocker beats a finished leaf.

## Close

1. Record anything deferred-but-wanted in a durable place — a [[LUM Ahead]] row if Lumen is holding it, else a [[Quick]] line, a [[Weekly]] checkbox, or a backlog row.
2. Advance `Daybreak Watermark.md` to the newest `captured:` surfaced.
3. Confirm the briefing landed in [[LUM Day]] before finishing — a run that only spoke into chat did not deliver.
4. Do not commit unless asked — Daybreak is a read-and-decide ritual, not a work session.

Declined items do **not** return with escalating urgency. Three declines is a signal to raise it once, plainly, at the weekly review.
