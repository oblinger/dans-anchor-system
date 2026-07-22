#!/bin/bash
# grant-calendar.command — one-time Calendar permission grant for Daybreak.
#
# Double-click this in Finder (or `open` it). Because it launches from the Aqua
# GUI, macOS can show the Calendar-access prompt that a headless session cannot.
# Click "Allow" once; after that `calendar-today.swift` runs granted and the
# morning briefing shows your day. You only ever need to do this once.
#
# See calendar-today.swift for why EventKit (not osascript) is the query path.

cd "$(dirname "$0")" || exit 1
echo "Requesting Calendar access — click Allow if a dialog appears…"
echo
swift calendar-today.swift
status=$?
echo
if [ "$status" -eq 2 ]; then
  echo "Access was DENIED. If no dialog appeared, grant it manually:"
  echo "  System Settings → Privacy & Security → Calendars → enable Terminal."
  echo "Then double-click this file again."
else
  echo "Calendar access is granted — the events above are today's. Daybreak is wired."
fi
echo
echo "Press Return to close."
read -r _
