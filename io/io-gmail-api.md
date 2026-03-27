# Gmail — Read and Search Email

Read, search, and manage Gmail via the Google API using existing OAuth credentials.

## Setup

Already configured — credentials at `~/.google_workspace_mcp/credentials/{user}@gmail.com.json` include Gmail scopes (readonly, modify, send, compose, labels).

## Actions

### Search emails
```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import json

creds_path = os.path.expanduser("~/.google_workspace_mcp/credentials/{user}@gmail.com.json")
with open(creds_path) as f:
    cred_data = json.load(f)

creds = Credentials(
    token=cred_data["token"],
    refresh_token=cred_data["refresh_token"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=cred_data["client_id"],
    client_secret=cred_data["client_secret"],
    scopes=cred_data["scopes"]
)

service = build("gmail", "v1", credentials=creds)

# Search
results = service.users().messages().list(userId="me", q="from:someone@example.com subject:meeting", maxResults=10).execute()
messages = results.get("messages", [])
```

### Read a message
```python
msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
# Headers
headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
subject = headers.get("Subject", "")
from_addr = headers.get("From", "")
date = headers.get("Date", "")

# Body (plain text)
import base64
for part in msg["payload"].get("parts", [msg["payload"]]):
    if part["mimeType"] == "text/plain":
        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
```

### List labels
```python
labels = service.users().labels().list(userId="me").execute()
for label in labels["labels"]:
    print(f"{label['name']} ({label['id']})")
```

### Common search queries
```
from:name@example.com          # from specific sender
to:me                          # sent to me
subject:keyword                # subject contains
after:2026/03/01               # after date
before:2026/03/15              # before date
is:unread                      # unread only
has:attachment                 # has attachments
label:INBOX                    # in inbox
newer_than:7d                  # last 7 days
"exact phrase"                 # exact match
```

## Dependencies

```bash
pip install google-api-python-client google-auth
```

## Notes

- Token auto-refreshes using the refresh_token in the credentials file
- Gmail API rate limit: 250 quota units per user per second (generous for read operations)
- Messages are returned newest-first by default
- Use `format="metadata"` for headers-only (faster), `format="full"` for complete message
