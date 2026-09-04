#!/bin/bash
# webfetch-authwall-hook.sh — F181 PostToolUse:WebFetch auth-wall advice hook.
#
# Reads the PostToolUse JSON payload on stdin. When the WebFetch result carries a
# known auth-wall / bot-wall signature, classifies WHICH wall fired and emits the
# matching one-line fix as additionalContext for the agent's next turn. A normal
# successful fetch matches no signature and emits nothing.
#
# Signature → advice routing (the classifier picks ONE branch):
#   • LinkedIn / session-gated  → Safari or the user's real Chrome; cpage CANNOT help
#     (its sandbox Chrome has no login session and hits the same wall).
#   • Generic bot wall (403/999/Cloudflare, no login) → ctrl cpage.
#
# Registered in ~/.claude/settings.json under PostToolUse matcher "WebFetch".
# Presence of that entry IS activation (F181 Q2) — no other flag exists.

payload=$(cat)

# Fast prefilter — no python spin-up unless a wall-ish token is present at all.
# A thin result is the OTHER half of the problem (Dan, 2026-09-03: an agent that
# "succeeded" and got a JS shell keeps going instead of upgrading), so a small
# payload also gets the python pass even with no wall token in it.
if [ "${#payload}" -ge 4000 ]; then
  printf '%s' "$payload" | grep -qiE 'authwall|/uas/login|sessionRedirect|cloudflare|just a moment|attention required|forbidden|[^0-9](403|999)[^0-9]|enable javascript|requires javascript|noscript|econnrefused|etimedout|failed to fetch' || exit 0
fi

WF_PAYLOAD="$payload" python3 - << 'PY'
import json, os, re, sys

try:
    data = json.loads(os.environ["WF_PAYLOAD"])
except Exception:
    sys.exit(0)
if data.get("tool_name") != "WebFetch":
    sys.exit(0)

url = (data.get("tool_input") or {}).get("url", "")
resp = data.get("tool_response", "")
text = resp if isinstance(resp, str) else json.dumps(resp)
hay = url + "\n" + text

# Branch 1 — session-gated wall (LinkedIn et al.): the fetch got bounced to a login.
session_wall = re.search(
    r"authwall|linkedin\.com/uas/login|sessionRedirect", hay, re.I)

# Branch 2 — generic bot wall: an HTTP-error signature, not a page that merely
# mentions the number. Require error context around 403/999.
bot_wall = re.search(
    r"cloudflare|just a moment|attention required"
    r"|403 forbidden"
    r"|(?:status(?:\s*code)?|error|http|code)\s*[:=]?\s*(?:403|999)\b",
    hay, re.I)

if session_wall:
    ctx = (
        f"WebFetch auth-wall advice (F181 hook): {url} bounced to a LOGIN wall "
        "(session-gated site, e.g. LinkedIn). Your session lives in Safari / your "
        "real Chrome, not a sandbox — use `open -a Safari \"<url>\"` then osascript "
        "DOM extraction (or `ctrl jpage` / `ctrl jgetlist`). Do NOT fall back to "
        "`ctrl cpage` here: its sandbox Chrome has no login session and hits the "
        "same wall."
    )
elif bot_wall:
    ctx = (
        f"WebFetch auth-wall advice (F181 hook): {url} hit a BOT wall "
        "(403/999/Cloudflare — no login needed). Fall back to "
        "`ctrl cpage \"<url>\" --output /tmp/page.json --yaml`, then Read the file "
        "back. cpage drives a real Chrome via DevTools Protocol and passes bot "
        "checks that WebFetch cannot."
    )
else:
    # Branch 3 — the fetch "worked" and returned nothing usable: a JS shell, a
    # consent stub, an empty body, or a transport error. This is the half the
    # wall branches missed, and the one that reads as success (Dan, 2026-09-03:
    # "at least half the time when an agent is using WebFetch, it should just
    # upgrade"). Deliberately NOT fired on every fetch: advice that arrives on
    # good fetches too is advice agents learn to skip.
    body = text.strip()
    js_shell = re.search(r"enable javascript|requires javascript|<noscript|"
                         r"please turn on javascript|loading\.\.\.", hay, re.I)
    transport = re.search(r"econnrefused|etimedout|enotfound|failed to fetch|"
                          r"request timed out|network error", hay, re.I)
    gone = re.search(r"\b(404|410)\b", hay)
    if gone and not transport:
        sys.exit(0)                       # genuinely absent page — no tool upgrades that
    if not (js_shell or transport or len(body) < 600):
        sys.exit(0)
    why = ("returned a JavaScript shell rather than the page" if js_shell
           else "could not be reached at all" if transport
           else "returned almost no text (%d chars) — a rendered page it is not" % len(body))
    ctx = (
        f"WebFetch upgrade advice (F181 hook): {url} {why}. WebFetch reads the raw "
        "HTML and runs no JavaScript, so a modern page often comes back empty and "
        "LOOKS like a success. Re-fetch it with a real browser: "
        "`ctrl cpage \"<url>\" --output /tmp/page.json --yaml`, then Read the file "
        "back. If the page needs the user's login, use Safari instead "
        "(`ctrl jpage`) — cpage's Chrome has no session. More than a couple of "
        "pages, or a whole crawl, runs on Dexter through the bridge, not on this "
        "laptop. Claim the browser first: `ctrl own <minutes> --reason \"...\"`."
    )

print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": ctx,
}}))
PY
exit 0
