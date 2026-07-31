#!/usr/bin/env python3
"""Re-authorize Google OAuth for gsa CLI. Opens browser for consent."""
import json, os, glob, http.server, urllib.request, urllib.parse, webbrowser, threading

# Resolved, not hardcoded: the filename IS the account address, so a literal
# here bakes one person's identity into a repo that ships publicly (SKA F030).
# Exactly one credentials file is expected — zero or several is a real
# ambiguity about which account to re-authorize, so it fails loudly rather than
# guessing.
CREDS_DIR = os.path.expanduser("~/.google_workspace_mcp/credentials")
_creds = sorted(glob.glob(os.path.join(CREDS_DIR, "*.json")))
if len(_creds) != 1:
    raise SystemExit(
        f"expected exactly one credentials file in {CREDS_DIR}, found {len(_creds)}"
        + (": " + ", ".join(os.path.basename(p) for p in _creds) if _creds else ""))
CREDS_PATH = _creds[0]

with open(CREDS_PATH) as f:
    creds = json.load(f)

CLIENT_ID = creds["client_id"]
CLIENT_SECRET = creds["client_secret"]
SCOPES = " ".join(creds.get("scopes", [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]))
REDIRECT_URI = "http://localhost:8789"

auth_code = None

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Authorization successful! You can close this tab.</h2>")
    def log_message(self, *args):
        pass

# Build auth URL
auth_url = (
    f"https://accounts.google.com/o/oauth2/v2/auth?"
    f"client_id={CLIENT_ID}&"
    f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
    f"response_type=code&"
    f"scope={urllib.parse.quote(SCOPES)}&"
    f"access_type=offline&"
    f"prompt=consent"
)

print(f"\nOpening browser for authorization...")
print(f"If browser doesn't open, visit:\n{auth_url}\n")
webbrowser.open(auth_url)

# Start local server to catch the redirect
server = http.server.HTTPServer(("localhost", 8789), Handler)
server.handle_request()

if not auth_code:
    print("ERROR: No authorization code received")
    exit(1)

print("Got authorization code, exchanging for tokens...")

# Exchange code for tokens
data = urllib.parse.urlencode({
    "code": auth_code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code",
}).encode()

req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
req.add_header("Content-Type", "application/x-www-form-urlencoded")
resp = urllib.request.urlopen(req)
tokens = json.loads(resp.read())

# Update credentials file
creds["token"] = tokens["access_token"]
if "refresh_token" in tokens:
    creds["refresh_token"] = tokens["refresh_token"]
creds["expiry"] = ""  # will be refreshed on next use

with open(CREDS_PATH, "w") as f:
    json.dump(creds, f, indent=2)

print(f"\n✅ Authorization successful!")
print(f"Token saved to {CREDS_PATH}")
print(f"Refresh token: {'updated' if 'refresh_token' in tokens else 'unchanged'}")
