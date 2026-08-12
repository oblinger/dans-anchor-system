#!/usr/bin/env python3
"""Surface appointments that arrive as mail but never reach a calendar.

Some senders mail a scheduled thing as rendered HTML with no `text/calendar`
part and no `.ics` attachment — so nothing exists for a calendar to add, and
Daybreak's Calendar step cannot see it. This scans the watchlisted senders and
pulls the date-time out of the body instead.

    python3 appointment-scan.py [--days 3] [--account EMAIL] [--asof DATE]

Senders come from `LUMEN Watchlist.md` — this script never carries its own
copy of the list. Prints one line per appointment found, soonest first, or
nothing at all when there is nothing scheduled.
"""

import argparse
import datetime as dt
import html
import re
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

GSA = Path.home() / "ob/kmr/SYS/Bespoke/Skill Agent/Doc/Google Suite Access/gsa"
WATCHLIST = (Path.home() / "ob/kmr/SYS/Staff/Lumen/LUMEN Design"
             / "LUMEN Watchlist.md")
API = "https://gmail.googleapis.com/gmail/v1/users/me"

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
MONTH_NUM = {m: i + 1 for i, m in enumerate(MONTHS)}

# Words that follow a clinician's name in these layouts and are not part of it.
NOT_A_NAME = {"Video", "Visit", "View", "Download", "My", "Health", "Online",
              "Appointment", "Telehealth", "Reminder", "Confirm", "Your"}


def die(msg):
    print(f"appointment-scan: {msg}", file=sys.stderr)
    sys.exit(1)


def watchlist_senders():
    """Email addresses named in the watchlist. No local fallback copy."""
    if not WATCHLIST.exists():
        die(f"watchlist not found at {WATCHLIST}")
    text = WATCHLIST.read_text()
    found = re.findall(r"`([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})`",
                       text)
    seen, out = set(), []
    for a in found:                       # keep watchlist order, drop dupes
        if a.lower() not in seen:
            seen.add(a.lower())
            out.append(a)
    if not out:
        die("no sender addresses in the watchlist — nothing to scan")
    return out


def strip_html(raw):
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"[ \t\xa0]+", " ", html.unescape(raw))


def body_text(gsa, msg_id, token):
    msg = gsa.api("GET", f"{API}/messages/{msg_id}?format=full", token=token)
    parts, stack = [], [msg.get("payload", {})]
    while stack:
        p = stack.pop()
        data = p.get("body", {}).get("data")
        if data and p.get("mimeType", "").startswith("text/"):
            import base64
            parts.append(base64.urlsafe_b64decode(data + "===")
                         .decode("utf-8", "replace"))
        stack.extend(p.get("parts", []))
    return strip_html(" ".join(parts))


def find_appointment(text):
    """Return (datetime, blurb) or None. Only a date WITH a time counts."""
    pat = (r"(" + "|".join(MONTHS) + r")\s+(\d{1,2}),?\s+(\d{4})"
           r"[\s,]*(?:at\s+)?(\d{1,2}):(\d{2})\s*([AaPp])\.?[Mm]\.?"
           r"\s*([A-Z]{2,4})?")
    m = re.search(pat, text)
    if not m:
        return None
    mon, day, year, hh, mm, ap, tz = m.groups()
    hh = int(hh) % 12 + (12 if ap.lower() == "p" else 0)
    when = dt.datetime(int(year), MONTH_NUM[mon], int(day), hh, int(mm))

    who = ""
    wm = re.search(r"[Ww]ith\s+((?:[A-Z][A-Za-z.'-]+\s*){1,3})", text)
    if wm:                                # trim layout words off the name
        parts = wm.group(1).split()
        while parts and parts[-1] in NOT_A_NAME:
            parts.pop()
        who = " ".join(parts)

    kind = "video visit" if re.search(r"video visit", text, re.I) else "visit"
    bits = [kind + (f" with {who}" if who else "")]
    if tz:
        bits.append(f"({tz})")
    return when, " ".join(bits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=3,
                    help="how far ahead to report (default 3)")
    ap.add_argument("--account", default=None)
    ap.add_argument("--asof", default=None,
                    help="YYYY-MM-DD to scan from; default today")
    a = ap.parse_args()

    if not GSA.exists():
        die(f"gsa not found at {GSA}")
    gsa = SourceFileLoader("gsa", str(GSA)).load_module()
    token = gsa.get_token(a.account)

    asof = (dt.datetime.strptime(a.asof, "%Y-%m-%d") if a.asof
            else dt.datetime.now().replace(hour=0, minute=0, second=0,
                                           microsecond=0))
    # look back a week for the notice, forward --days for the appointment
    since = (asof - dt.timedelta(days=7)).strftime("%Y/%m/%d")
    senders = watchlist_senders()
    q = "(" + " OR ".join(f"from:{s}" for s in senders) + f") after:{since}"

    data = gsa.api("GET", f"{API}/messages?q={q.replace(' ', '+')}"
                          "&maxResults=40", token=token)
    hits = []
    for m in data.get("messages", []):
        found = find_appointment(body_text(gsa, m["id"], token))
        if found and asof <= found[0] <= asof + dt.timedelta(days=a.days):
            hits.append(found)

    seen, out = set(), []
    for when, blurb in sorted(hits):
        key = (when, blurb)
        if key not in seen:
            seen.add(key)
            out.append((when, blurb))
    for when, blurb in out:
        day = "today" if when.date() == asof.date() else when.strftime("%a %-d %b")
        print(f"{day} {when.strftime('%-I:%M %p')} — {blurb}")
    if not out:
        print("(no unlisted appointments in the window)", file=sys.stderr)


if __name__ == "__main__":
    main()
