// calendar-today.swift — today's local-Calendar events for the Daybreak briefing.
//
// WHY THIS EXISTS (Lumen F004): the AppleScript route (`osascript` with a
// `whose start date ≥ …` filter) takes ~18s regardless of how many calendars
// you narrow to — the `whose` clause scans the whole event store. EventKit
// queries the store's indexed predicate directly and returns in well under a
// second, which a morning ritual can afford. Measured 2026-07-21:
//   osascript, all calendars ...... 18.03s
//   osascript, 3 named calendars .. 18.66s   (narrowing does NOT help)
//   EventKit (this) ............... ~1s incl. compile
//
// RUN:  swift calendar-today.swift            (today)
//       swift calendar-today.swift +1         (tomorrow; N days ahead)
//
// TCC: the calling process needs Calendar access. From a headless/SSH context
// the access request returns denied with no prompt — run grant-calendar.command
// once from the GUI to get the grant. On denial this prints CALENDAR_ACCESS_DENIED
// to stderr and exits 2, so the briefing can say "calendar unreachable" rather
// than silently dropping the channel.

import EventKit
import Foundation

let offset = CommandLine.arguments.dropFirst().first.flatMap { Int($0) } ?? 0

let store = EKEventStore()
let sem = DispatchSemaphore(value: 0)
var granted = false
store.requestFullAccessToEvents { ok, _ in granted = ok; sem.signal() }
sem.wait()
guard granted else {
    FileHandle.standardError.write("CALENDAR_ACCESS_DENIED\n".data(using: .utf8)!)
    exit(2)
}

let cal = Calendar.current
let base = cal.date(byAdding: .day, value: offset, to: Date())!
let start = cal.startOfDay(for: base)
let end = cal.date(byAdding: .day, value: 1, to: start)!
let pred = store.predicateForEvents(withStart: start, end: end, calendars: nil)
let evs = store.events(matching: pred).sorted { $0.startDate < $1.startDate }

let tf = DateFormatter(); tf.dateFormat = "HH:mm"
for e in evs {
    let title = e.title ?? "(untitled)"
    if e.isAllDay {
        print("all-day  \(title)")
    } else {
        print("\(tf.string(from: e.startDate))    \(title)")
    }
}
