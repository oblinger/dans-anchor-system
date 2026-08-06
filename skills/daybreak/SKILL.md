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
| **Dates** | Read `MY Dates.md` for birthdays and anniversaries coming up. Card rows need six weeks, not two. |
| **Mail** | Surface only messages matching `LUMEN Watchlist.md`. Skip entirely if it is empty. |
| **Hot** | Read [[Rocks]] — the live block only — for what the user has declared currently matters. |
| **Loose** | Scan [[Quick]] and Lumen's own `## Now` for anything captured since the last run. |
| **Today** | Choose 3–5 items *across* domains and put them on screen, decisions first. |
| **Stage** | Lift today's quick hits to the top of [[Quick]], above a blank line. Propose the set; add to it. |
| **Week** | Put the ≥30-min items into today's `### <Day>` in this week's [[Weekly]] file, as checkboxes. |
| **Runnable** | Name the Ready work that needs no user, offered as a single `'` (crank). |
| **Ahead** | Read [[LUMEN Nudge]] (in Lumen's own folder); pull anything now due into the briefing's **Watching** section. |
| **Write** | Put the briefing at the top of `~/ob/kmr/SYS/Staff/Lumen/LUMEN Day.md` — the user reads it there, not in chat. |
| **Close** | Write down anything deferred, then advance the watermark. In that order. |

Sources are read cheapest-and-most-decisive first, so an interrupted run still produced value. Watch messages lead because the user already decided those mattered; `Q.md` is second because one file federates every anchor. Everything else in [[LST]] is read on demand — do not sweep the list tree, that is weekly-review work.

## Watch messages

MUSE items live at `~/ob/kmr/Log/MUSE/MUSE <date> <letter> <title>.md`, indexed newest-first in `Log Muse.md`. Frontmatter carries `captured:`, `state:`, `word_count:`.

**Nothing ever flips `state: unreviewed`** — MUSE writes it once at ingest and no consumer clears it. Do NOT filter on that field; every item would surface every morning forever.

Use the watermark at `LUMEN Track/Daybreak Watermark.md` (a single ISO timestamp). Surface items whose `captured:` is newer than it. Skip items whose `state:` starts with `suppressed-` — MUSE already judged those noise.

```bash
WM=$(grep -o '[0-9-]\{10\} [0-9:]\{8\}' "$HOME/ob/kmr/SYS/Staff/Lumen/LUMEN Track/Daybreak Watermark.md" | head -1)
[ -z "$WM" ] && { echo "daybreak: watermark missing or unparseable — refusing to surface (would dump the whole corpus)" >&2; exit 1; }
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

## Calendar

Today's events come from the **local macOS Calendar** via the shared `/io ical` capability ([[io-ical]], EventKit) — not from Google OAuth, and no longer a Daybreak-private script (SKA T047 moved it into `/io`). The local Calendar already carries the Google events (the `{user}@gmail` and `dan@sportsvisio.com` accounts sync into it), so it is a superset with no expiring permission to renew. Run it:

```bash
swift "$HOME/.claude/skills/io/scripts/calendar-today.swift"
```

It prints today's events one per line (`HH:MM    Title`, or `all-day  Title`), sorted. Per Lumen F004 this replaced the AppleScript route, which took ~18s regardless of calendar narrowing; EventKit returns in ~1s.

**If it exits 2 / prints `CALENDAR_ACCESS_DENIED`**, the calling context lacks Calendar permission — **say so in the briefing and continue** (never silently omit the channel; a briefing that admits the calendar was unreachable beats one that quietly dropped it). The one-time fix is a GUI grant: tell the user to double-click `$HOME/.claude/skills/io/scripts/grant-calendar.command` and click Allow. After that it runs granted every morning. Full capability docs: [[io-ical]]. Interim (until SKA T047 lands the responsible-process binding): the grant is currently bound to **Terminal.app**, so a headless session routes the shim through Terminal (`osascript -e 'tell app "Terminal" to do script "…calendar-today.swift > /tmp/cal.out; exit"'`) and reads the output file. Do **not** fall back to the AppleScript `whose` query — 2026-07-22 it silently returned empty on a 3-event day.

**Filter through [[LUMEN Background]] § Standing rhythm.** Standing meetings recorded there (e.g. the daily 14:00 CV ML standup) are suppressed from the briefing's calendar block — the user already knows their own rhythm; surface a standing meeting only when it moved, changed, or was cancelled. Everything else on the day gets listed.

## Dates

Read `~/ob/kmr/MY/MY Dates.md` — the register of recurring annual dates. It sits beside the calendar read because it is date-shaped, and because **the calendar does not carry these**: they are annual, they mostly have no event, and the register is the only place they exist.

**Read the key table at the top only.** Everything under § Other dates is an archive with no action attached, and § Unresolved has no usable month. Per-person context — what to send, what to avoid, open commitments — lives in `MY Dates Notes.md` beside it; open that only for a person actually surfacing.

**Two windows, because a card and a greeting are different jobs.**

| Window | Applies to | What the briefing says |
|---|---|---|
| **6 weeks** | rows with `Card` ✓ | "coming up" — start deciding what to say |
| 14 days | any row | "coming up" |
| 3 days | any row | "start acting" |
| day-of | any row | "today" |

**The six weeks is Dan's own convention, recovered from his 2022 system** (`Annual.html`: *"month prefix 6-weeks in advance of actual date"*). It was built for posted cards, which have to be bought, written and mailed. An e-card collapses most of that — but the six weeks was really about *deciding what to say*, and it stays the target for anyone who matters. The 14-day window is fine for awareness and demonstrably too late for action: Collette Roney's 1 August birthday was missed in 2026 precisely because nothing surfaced it.

**Surfacing a date is not the work.** A `Card` ✓ row inside the window belongs in the briefing's **Decisions** block with a concrete next action, not in a list of trivia. How a card actually gets sent is [[ADMIN Birthdays]]; the gift half is [[HERMES|Hermes]]'s when a row carries `Gift` ✓.

**Record what went out.** When a card is sent, tick the year into that row's Notes so next year's draft does not repeat itself, and log any promise the card made — *"let's talk in two weeks"* — as a dated [[LUMEN Nudge]] row. The promise is the perishable part.

## Mail

Mail goes through the `google_workspace_mcp` server registered per [[WIRE Claude Google MCP]] (Calendar + Gmail included; Daybreak uses only the Gmail half now that calendar is local). If the server is not running, **say so and continue** — a missing mail channel degrades the briefing, it does not abort the run.

Mail is filtered through `LUMEN Design/LUMEN Watchlist.md` — a definition list of senders, subjects, and patterns worth surfacing. It starts empty and grows when the user says "flag this kind of thing." **Do not invent watchlist entries**; an unearned watchlist trains the user to ignore the channel.

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

**Only the user's own work gets staged.** Anything Lumen wants *from* the user — run a grant, click a dialog, review something — never goes into [[Quick]], [[Todo]], or [[Weekly]]; those are the user's working lists, and agent asks clutter them (user, 2026-07-22: *"if you have things like that you want me to do, you just bring them up in the morning time"*). An agent ask lives as a `LUMEN Nudge.md` row (`next run`, or dated) and surfaces in the briefing's **Decisions** block until settled.

**[[Weekly]] day-list.** This week's file is `~/ob/kmr/LST/Weekly/YYYY-Www.md` (ISO week, zero-padded). Bigger items go under today's `### <Day>-<DD>` H3 as `- [ ]` so the user checks them off through the day. Week-level intentions — rocks, things aimed at the week as a whole — go in the **top block** between the H1 and the first `###`, not under a day.

**Lumen owns the week file — create it whenever it's missing** (user delegated 2026-07-27, see [[feedback_lumen_owns_week_calendar]]). Reproduce the `[[WEEKLY template]]` output by hand: `# W{NN}   {Mon YYYY-MM-DD}   [[{prev}|<<]] [[{next}|>>]]`, a one-line description, week-rock `- [ ]` bullets, then `### Mon-D` … `### Fri-D` (Mon–Fri, day-of-month no leading zero). Populate the rocks + carry-forwards, then review it with the user daily. (The old rule was "never hand-author, let the user stamp it" — superseded.)

**On Monday, plan the week first.** Before staging the day, walk last week's file for unfinished `- [ ]` items and propose the week's rocks into the top block. Per [[Weekly]] § BRIEF, a Friday item left unresolved is carry-forward — it gets checked, dropped, or migrated, never silently abandoned.

**On Monday, the planning is a session, not a delivery.** Per [[LUMEN Mandate]] the week is the layer Lumen owns outright, and the work is **decomposition**: read [[Rocks]] — which Dan settles with [[Vector]], and which Lumen never writes — and break the big undated things into parts that fit an actual day. Dan's own pronouns are load-bearing here: *"we'll figure out what things we're going to put on my list for the week and for the days."* Propose, do not hand down. Carrying a rock forward untouched week after week is the failure mode; breaking off the piece that fits Tuesday is the value. **Respect the focus cut** — a blank line inside the live Rocks block marks what is parked, and re-widening it every Monday is the same failure as ignoring it.

**On Friday, close the week — and ask whether the time actually went there.** The mirror of the Monday step, and the answer to [[LUMEN005 - Opportunistic time-slotting against a declared priority board|F005]]-Q3, which resolved that **Lumen asks rather than instruments**: the answer is a memory, not a measurement, and a weekly question that gets an honest answer beats an instrumented signal nobody built. So at Friday's close, alongside the carry-forward sweep, ask plainly whether the week's hours went against the rocks they were planned against. **Keep it an ask.** Let [[TEMPO]] replace it later once the shape is known, not before.

Two things this step must not become. It is **not** an accountability review — [[VEC Mandate]] gives that register to [[Vector]] deliberately, and Lumen mentions a slip once, lightly, then re-plans around it. And if the pattern of weeks contradicts what [[MY North Star]] declares, **the declaration may be the stale half**; that is a finding for Vector and Dan, not a verdict Lumen delivers.

## Where the briefing goes — [[LUMEN Day]] 

**Chat is not the delivery surface.** The user reacts to the first item, the rest scrolls away, and the briefing is gone. So every run writes the briefing to `~/ob/kmr/SYS/Staff/Lumen/LUMEN Day.md` **and** prints it in chat. The file is the record; chat is the conversation.

That file is **col-1 of the Daily View dashboard** (`CAPS-J D`), toggled in place of [[Work]]. On that same screen the user is simultaneously looking at:

| Dashboard slot | File | What Daybreak does with it |
| --- | --- | --- |
| col-1 top | [[LUMEN Day]] | write today's briefing here |
| col-1 bottom | [[Quick]] | lift the day's quick hits to the top, above a blank line |
| col-2 bottom | [[Todo]] | read-only — the user's own list |
| col-3/4 top | current [[Weekly]] | put ≥30-min items under today's `### <Day>` H3 |

So the briefing and the lists the user acts from are **all on screen at once**. Writing to `Quick` and `Weekly` is not bookkeeping for later — it is putting the work where their eyes already are.

Shape: today's block goes directly under the H1 as `## <Day> YYYY-MM-DD · W<nn>`, pushing the previous day down. Never rewrite a past day. Sections in fixed order — **Decisions / Today / Runnable / Gaps** — per the file's own `# BRIEF`. Keep lines short; it renders in one narrow column, so wide tables wrap and destroy the glance value.

## What Lumen is holding — [[LUMEN Nudge]] 

[[LUMEN Nudge]] (in Lumen's own folder) is the forward-looking commitment surface: a **table**, soonest-first, of things Lumen owes the user a nudge about. Read it every run; surface anything now due in the briefing's **Watching** section.

**Do not put these on the backlog.** The backlog holds work the agent does to *build things* — horizons, next-actions, features. LUMEN Nudge holds things about the *user's life* that the agent is carrying for them. Different kind of item, different reader, different shape. The user does not read the backlog, and making them would defeat the point.

**Writing a row is how Lumen remembers.** Any time the user defers something, or asks to be reminded, or an outward-facing action is held pending their go — add a row with its raising condition (a date, an event, or "waiting on you"). A promise made only in chat is a promise lost.

**Rows leave when they fire.** Raised and settled, or raised and declined → delete the row. Declined items do not return with escalating urgency.

**Keep it a table.** Three columns, one line per row. It exists to be glanced at; the moment it needs scrolling it has stopped working.

## Selection rule for Today

Provisional until `LUMEN Prioritization.md` exists (Lumen F001-Q4):

- **Never more than two items from one domain** — breadth is the point of a cross-cutting agent.
- **[[Rocks]] outranks backlog rows** — Rocks is the user's own declaration of what is hot.
- **Respect the focus cut.** A blank line inside the live [[Rocks]] block separates what the user is *actually working on now* (above) from rocks that are real but deliberately parked (below). When the cut is present it **overrides the breadth rules below** — draw Today from the rows above it and stop proposing items from beneath. Narrowing is the user telling you what to ignore; re-widening it every morning is the failure mode.
- **One item must be Health** — the only domain present in every framing the user has written ([[LUMEN Domains]]), and the one most reliably crowded out. *Currently constrained: exercise is off the table until ~2026-08-19 post-ablation, so pick recovery-compatible items — see the dated row in [[LUMEN Nudge]].*
- **Prefer what unblocks others** — a cleared blocker beats a finished leaf.
- **No anchor stays unheard — scan the starved list before filling Decisions.** Measured 2026-08-05 ([[LUMEN Backlog#^T021|LUMEN T021]]): [[ASH]], [[Boone]], [[Ember]] and [[Vector]] had **never once appeared** in any briefing across the whole run of [[LUMEN Day]] and its archive, while Ash alone carried **12 user-gated questions, more than any other anchor**. The anchors that did appear were exactly the ones the user had been talking about — a rich-get-richer loop in which an agent working quietly can never earn a mention, so its queue grows without bound and its questions expire unseen. Ash's did: one carried a window whose first date (2026-07-28) passed unnoticed, and another had already been answered by dictation and was still sitting in the queue. **The rule: before writing Decisions, read every `[U]` / `[U+A]` banner in `Q.md`, not only the anchors already in mind. If an anchor has user-gated questions and has not appeared in the last seven briefings, one of its questions takes a Decisions slot.** The three-item cap does not move; this only changes which three. **Pick its cheapest question rather than its most important one** — a queue that has never been touched is far more often unblocked by a single quick answer than by the right one. [[Vector]] is the cautionary case: its one open question is the sitting that would populate [[MY North Star]], and that file's emptiness is what keeps the effort-weighting check above dormant. The loop starved the thing that feeds it.

### Effort-weighting sanity check against [[MY North Star]] 

After the Today set is chosen and **before** it is written, read `~/ob/kmr/MY/MY North Star.md`. Each life-area H2 there carries a **Level of effort** — a declared target allocation, in hours/week or percent. Compare the *shape* of today's set against it and say something only when they visibly disagree.

**This is a sanity check, not an optimiser.** A single day is far too small a sample to match a weekly allocation, so never rebalance the day to hit a number, and never mention it when the day looks roughly reasonable. What earns a line in the briefing is a **persistent** divergence — an area declared as a major commitment that has drawn nothing for days, or one declared minor that keeps consuming the list. Surface that as a [[LUMEN Nudge]] row, not as a scolding paragraph in the briefing.

**Lumen reads this file; Lumen never writes it.** [[Vector]] authors it through debate turns with the user. If the observed pattern contradicts what is declared there, that is a finding *for Vector and the user* — the answer may well be that the declaration is stale, not that the days are wrong.

**While the file is an empty scaffold this step is a no-op** — say nothing at all rather than noting its absence every morning. It was created 2026-08-04 with placement and cross-references only; the life-area sections are on [[VEC Backlog]]. **It activates by itself the moment Vector fills in the first H2 carrying a Level of effort** — no further wiring needed here.

## Close

1. Record anything deferred-but-wanted in a durable place — a [[LUMEN Nudge]] row if Lumen is holding it, else a [[Quick]] line, a [[Weekly]] checkbox, or a backlog row.
2. Advance `Daybreak Watermark.md` to the newest `captured:` surfaced.
3. Confirm the briefing landed in [[LUMEN Day]] before finishing — a run that only spoke into chat did not deliver.
4. Do not commit unless asked — Daybreak is a read-and-decide ritual, not a work session.

Declined items do **not** return with escalating urgency. Three declines is a signal to raise it once, plainly, at the weekly review.
