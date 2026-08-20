# ical — macOS Calendar (read and write)

Read **and write** the local macOS Calendar via Apple's **EventKit**, run through the `swift` interpreter. No OAuth tokens, no API keys — the local Calendar already carries every synced account (iCloud + the Google accounts that sync into it), so it is a superset with no expiring permission to renew. (`ical` = the local Apple/EventKit surface; a future server-side Google Calendar API surface would be `/io gcal`.)

**Access methods comparison:** See [[io-ical-access]] for the trade-offs between local EventKit, the Google Calendar API, and the (rejected) AppleScript route.

## Today's events

```bash
swift "$HOME/.claude/skills/io/scripts/calendar-today.swift"
```

Prints today's events one per line, sorted by start time — `HH:MM    Title` for timed events, `all-day  Title` for all-day events.

## A different day (N days ahead)

```bash
swift "$HOME/.claude/skills/io/scripts/calendar-today.swift" +1   # tomorrow
swift "$HOME/.claude/skills/io/scripts/calendar-today.swift" +7   # a week out
```

The optional integer argument is a day offset (default `0` = today). Only whole days ahead are supported today.

## Writing events

```bash
W="$HOME/.claude/skills/io/scripts/calendar-write.swift"
swift "$W" list                          # writable calendars, which one is default
swift "$W" create /tmp/event.json        # add --dry-run to see it without saving
swift "$W" show   <eventIdentifier>
swift "$W" delete <eventIdentifier>      # --dry-run works here too
```

**`create` takes a JSON file path, never a shell string, and that is load-bearing.** Event notes are multi-line, and shell quoting mangles them — command substitution silently eats a trailing newline, which corrupted a document the same week this was written. A file is also what makes `--dry-run` worth having: the same bytes that were previewed are the bytes that get saved.

    {
      "title": "Christmas — Kentucky",
      "calendar": "Family",
      "allDay": true,
      "start": "2026-12-22",
      "end":   "2026-12-29",
      "notes": "line one\nline two",
      "url":   "https://…",
      "alarmsMinutesBefore": [10]
    }

| Field | Notes |
|---|---|
| `title` | required |
| `start` | required — `yyyy-MM-dd` or `yyyy-MM-dd HH:mm`, local time |
| `end` | optional — defaults to +1h (timed) or the same day (all-day) |
| `allDay` | **the end day is INCLUSIVE** — `22`→`29` covers the 29th, matching how a person names a trip |
| `calendar` | optional, defaults to the system default-for-new-events; must be writable |
| `alarmsMinutesBefore` | a list, so several alerts are one field |

**Every command answers in JSON, and `create` returns the `eventIdentifier`.** Keep it: that string is the only handle for `show` and `delete`, and a created event with a lost identifier can only be removed by hand. Exit codes: `0` ok · `2` access denied · `3` bad input · `4` write failed.

**`list` shows only writable calendars.** An unwritable one in that list would be a trap, since choosing it fails at save time with an unhelpful error.

**Two things this deliberately does NOT do:** edit an existing event's fields, and touch recurring series beyond `.thisEvent`. Both are easy to get subtly wrong and hard to notice afterwards; delete-and-recreate is the supported edit, and it is cheap now that both halves exist.

## Permission (one-time)

EventKit needs the **calling process** to hold macOS Calendar (TCC) access. **One grant covers both reading and writing** — both scripts call `requestFullAccessToEvents`, which on macOS 14+ is the full-access API, and writing raised no second prompt (verified 2026-08-20). From a headless / SSH / background context the request returns denied with no prompt (a background context cannot show the dialog).

**If the script exits `2` / prints `CALENDAR_ACCESS_DENIED` to stderr**, the caller lacks Calendar permission — **report that and continue** (never silently drop the channel; a caller that admits the calendar was unreachable beats one that quietly omitted it). The one-time fix is a GUI grant: tell the user to double-click `$HOME/.claude/skills/io/scripts/grant-calendar.command` in Finder and click **Allow** (it launches in the Aqua GUI so the prompt can appear). Fallback: System Settings → Privacy & Security → Calendars → enable Terminal. After that it runs granted every time.

Why EventKit and not `osascript`: the AppleScript `whose start date ≥ …` filter scans the whole event store (~18s regardless of calendar narrowing); EventKit queries the indexed predicate directly and returns in ~1s. Measured under [[F004 — Calendar via local macOS Calendar, not Google OAuth|Lumen F004]].
