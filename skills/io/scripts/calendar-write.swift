// calendar-write.swift — create, inspect and delete local-Calendar events.
//
// WHY THIS EXISTS: calendar-today.swift reads. Nothing wrote, so every event an
// agent produced had to be hand-copied by the user — which is where trip
// itineraries and their departure reminders actually got lost. Same framework
// as the reader (EventKit) rather than AppleScript, for the same measured
// reason: `osascript` with a `whose` clause scans the whole store (~18s);
// EventKit hits the indexed predicate (~1s). Authorized by Dan 2026-08-20.
//
// TCC: uses requestFullAccessToEvents — the same grant the reader already
// holds, which on macOS 14+ covers writing too. No second prompt expected. On
// denial: prints CALENDAR_ACCESS_DENIED to stderr, exits 2 (never silent).
//
// RUN:
//   swift calendar-write.swift list
//   swift calendar-write.swift create [--dry-run]  < event.json
//   swift calendar-write.swift show   <eventIdentifier>
//   swift calendar-write.swift delete <eventIdentifier>
//
// create reads JSON on STDIN, deliberately — event notes are multi-line and
// shell argument quoting mangles them (a trailing newline is silently eaten by
// command substitution, which has already corrupted one document this week).
//
//   { "title": "Christmas — Kentucky",
//     "calendar": "Home",                 // optional, default calendar if absent
//     "allDay": true,
//     "start": "2026-12-22",              // "yyyy-MM-dd" or "yyyy-MM-dd HH:mm"
//     "end":   "2026-12-29",              // all-day: INCLUSIVE last day
//     "notes": "line one\nline two",
//     "url":   "https://…",               // optional
//     "alarmsMinutesBefore": [10] }       // optional
//
// Exit codes: 0 ok · 2 access denied · 3 bad input · 4 write failed.

import EventKit
import Foundation

func die(_ msg: String, _ code: Int32) -> Never {
    FileHandle.standardError.write((msg + "\n").data(using: .utf8)!)
    exit(code)
}

func emit(_ obj: Any) {
    let d = try! JSONSerialization.data(withJSONObject: obj, options: [.prettyPrinted, .sortedKeys])
    print(String(data: d, encoding: .utf8)!)
}

// ---- access -------------------------------------------------------------
let store = EKEventStore()
do {
    let sem = DispatchSemaphore(value: 0)
    var granted = false
    store.requestFullAccessToEvents { ok, _ in granted = ok; sem.signal() }
    sem.wait()
    guard granted else { die("CALENDAR_ACCESS_DENIED", 2) }
}

var args = Array(CommandLine.arguments.dropFirst())
guard let cmd = args.first else {
    die("usage: calendar-write.swift list | create [--dry-run] | show <id> | delete <id>", 3)
}
args.removeFirst()
let dryRun = args.contains("--dry-run")
args.removeAll { $0 == "--dry-run" }

// ---- date parsing -------------------------------------------------------
// Two accepted shapes. Time-bearing wins when a colon is present, so a caller
// cannot accidentally get a midnight event by writing a time the parser drops.
func parseDate(_ s: String) -> Date? {
    let f = DateFormatter()
    f.locale = Locale(identifier: "en_US_POSIX")
    f.timeZone = TimeZone.current
    for fmt in ["yyyy-MM-dd HH:mm", "yyyy-MM-dd'T'HH:mm", "yyyy-MM-dd"] {
        f.dateFormat = fmt
        if let d = f.date(from: s) { return d }
    }
    return nil
}

let stamp: DateFormatter = {
    let f = DateFormatter()
    f.locale = Locale(identifier: "en_US_POSIX")
    f.timeZone = TimeZone.current
    f.dateFormat = "yyyy-MM-dd HH:mm"
    return f
}()

func describe(_ e: EKEvent) -> [String: Any] {
    var out: [String: Any] = [
        "eventIdentifier": e.eventIdentifier ?? "",
        "title": e.title ?? "",
        "calendar": e.calendar?.title ?? "",
        "allDay": e.isAllDay,
        "start": stamp.string(from: e.startDate),
        "end": stamp.string(from: e.endDate),
    ]
    if let n = e.notes, !n.isEmpty { out["notes"] = n }
    if let u = e.url { out["url"] = u.absoluteString }
    if let alarms = e.alarms, !alarms.isEmpty {
        out["alarmsMinutesBefore"] = alarms.map { Int(-$0.relativeOffset / 60) }
    }
    return out
}

// ---- commands -----------------------------------------------------------
switch cmd {

case "list":
    // Only writable calendars are listed — an unwritable one in the list is a
    // trap, since selecting it fails at save time with a useless error.
    let cals = store.calendars(for: .event)
        .filter { $0.allowsContentModifications }
        .sorted { $0.title < $1.title }
    let def = store.defaultCalendarForNewEvents?.calendarIdentifier
    emit(cals.map { c -> [String: Any] in
        ["title": c.title,
         "identifier": c.calendarIdentifier,
         "source": c.source?.title ?? "",
         "isDefault": c.calendarIdentifier == def]
    })

case "show":
    guard let id = args.first else { die("show needs an eventIdentifier", 3) }
    guard let e = store.event(withIdentifier: id) else { die("no event with identifier \(id)", 3) }
    emit(describe(e))

case "delete":
    guard let id = args.first else { die("delete needs an eventIdentifier", 3) }
    guard let e = store.event(withIdentifier: id) else { die("no event with identifier \(id)", 3) }
    let snapshot = describe(e)
    if dryRun { emit(["wouldDelete": snapshot]); break }
    do {
        try store.remove(e, span: .thisEvent, commit: true)
        emit(["deleted": snapshot])
    } catch { die("delete failed: \(error.localizedDescription)", 4) }

case "create":
    let input = FileHandle.standardInput.readDataToEndOfFile()
    guard !input.isEmpty,
          let spec = (try? JSONSerialization.jsonObject(with: input)) as? [String: Any]
    else { die("create expects a JSON object on stdin", 3) }

    guard let title = spec["title"] as? String, !title.isEmpty else { die("title is required", 3) }
    guard let startStr = spec["start"] as? String, let rawStart = parseDate(startStr)
    else { die("start is required, as yyyy-MM-dd or yyyy-MM-dd HH:mm", 3) }

    let allDay = (spec["allDay"] as? Bool) ?? false
    let rawEnd: Date
    if let endStr = spec["end"] as? String {
        guard let d = parseDate(endStr) else { die("end is unparseable: \(endStr)", 3) }
        rawEnd = d
    } else {
        // A timed event with no end is an hour; an all-day one is that day.
        rawEnd = allDay ? rawStart : rawStart.addingTimeInterval(3600)
    }
    guard rawEnd >= rawStart else { die("end is before start", 3) }

    let e = EKEvent(eventStore: store)
    e.title = title
    e.isAllDay = allDay
    if allDay {
        // EventKit treats an all-day span as INCLUSIVE of the end day, which
        // matches how a person names a trip ("22nd through the 29th"). Both
        // ends are floored so a stray time cannot shorten the span.
        let c = Calendar.current
        e.startDate = c.startOfDay(for: rawStart)
        e.endDate = c.startOfDay(for: rawEnd)
    } else {
        e.startDate = rawStart
        e.endDate = rawEnd
    }
    if let n = spec["notes"] as? String { e.notes = n }
    if let u = spec["url"] as? String, let url = URL(string: u) { e.url = url }

    if let name = spec["calendar"] as? String {
        guard let c = store.calendars(for: .event).first(where: {
            $0.title == name && $0.allowsContentModifications
        }) else { die("no writable calendar named '\(name)' — run `list` to see the options", 3) }
        e.calendar = c
    } else {
        guard let c = store.defaultCalendarForNewEvents else { die("no default calendar available", 3) }
        e.calendar = c
    }

    if let mins = spec["alarmsMinutesBefore"] as? [Int] {
        e.alarms = mins.map { EKAlarm(relativeOffset: TimeInterval(-$0 * 60)) }
    }

    if dryRun { emit(["wouldCreate": describe(e)]); break }
    do {
        try store.save(e, span: .thisEvent, commit: true)
        emit(["created": describe(e)])
    } catch { die("save failed: \(error.localizedDescription)", 4) }

default:
    die("unknown command '\(cmd)' — expected list | create | show | delete", 3)
}
