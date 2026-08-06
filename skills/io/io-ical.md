# Calendar — Read Today's Events

Read the local macOS Calendar via Apple's **EventKit**, run through the `swift` interpreter. No OAuth tokens, no API keys — the local Calendar already carries every synced account (iCloud + the Google accounts that sync into it), so it is a superset with no expiring permission to renew.

**Access methods comparison:** See [[io-calendar-access]] for the trade-offs between local EventKit, the Google Calendar API, and the (rejected) AppleScript route.

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

## Permission (one-time)

EventKit needs the **calling process** to hold macOS Calendar (TCC) access. From a headless / SSH / background context the request returns denied with no prompt (a background context cannot show the dialog).

**If the script exits `2` / prints `CALENDAR_ACCESS_DENIED` to stderr**, the caller lacks Calendar permission — **report that and continue** (never silently drop the channel; a caller that admits the calendar was unreachable beats one that quietly omitted it). The one-time fix is a GUI grant: tell the user to double-click `$HOME/.claude/skills/io/scripts/grant-calendar.command` in Finder and click **Allow** (it launches in the Aqua GUI so the prompt can appear). Fallback: System Settings → Privacy & Security → Calendars → enable Terminal. After that it runs granted every time.

Why EventKit and not `osascript`: the AppleScript `whose start date ≥ …` filter scans the whole event store (~18s regardless of calendar narrowing); EventKit queries the indexed predicate directly and returns in ~1s. Measured under [[F004 — Calendar via local macOS Calendar, not Google OAuth|Lumen F004]].
