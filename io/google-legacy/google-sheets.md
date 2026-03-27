# google-sheets — Google Sheets

Read and write spreadsheet data using the `gsa` CLI tool.

## Commands

```bash
gsa sheets read  <id> [range]            # Read cells as JSON
gsa sheets write <id> <range> <json>     # Write cells
gsa sheets append <id> <range> <json>    # Append rows
gsa sheets info  <id>                    # Sheet metadata (title, tab names)
gsa search sheets [query]                # Find spreadsheets (newest first)
```

## IDs

The `<id>` argument accepts either:
- A full Google URL: `https://docs.google.com/spreadsheets/d/1abc.../edit`
- A bare document ID: `1abc...`

## Data Format

- **Read output:** JSON array of arrays (rows of cells)
- **Write/append input:** JSON array of arrays, e.g. `'[["A","B"],["C","D"]]'`
- **Search output:** Tab-separated lines: `date\tname\tid\tlink`
- **Write value input option:** `USER_ENTERED` — Google parses numbers, dates, formulas automatically

## Examples

```bash
# List recent spreadsheets
gsa search sheets

# Read cells A1:C5 from a sheet
gsa sheets read 1abc...xyz A1:C5

# Write a header row
gsa sheets write 1abc...xyz 'Sheet1!A1:C1' '[["Name","Price","URL"]]'

# Append rows to existing data
gsa sheets append 1abc...xyz 'Sheet1!A1:C1' '[["Widget","$10","https://example.com"]]'

# Get sheet tab names and sizes
gsa sheets info 1abc...xyz
```

## Creating New Spreadsheets

`gsa` does not have a create command. To create a new spreadsheet, use Python inline:

```bash
python3 -c "
import json, urllib.request, urllib.parse, os
creds_path = os.path.expanduser('~/.google_workspace_mcp/credentials/{user}@gmail.com.json')
with open(creds_path) as f: creds = json.load(f)
data = urllib.parse.urlencode({'client_id': creds['client_id'], 'client_secret': creds['client_secret'], 'refresh_token': creds['refresh_token'], 'grant_type': 'refresh_token'}).encode()
req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
token = json.loads(urllib.request.urlopen(req).read())['access_token']
body = {'properties': {'title': 'My New Sheet'}, 'sheets': [{'properties': {'title': 'Sheet1'}}]}
req = urllib.request.Request('https://sheets.googleapis.com/v4/spreadsheets', data=json.dumps(body).encode(), method='POST')
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Content-Type', 'application/json')
result = json.loads(urllib.request.urlopen(req).read())
print(result['spreadsheetId'])
print(result['spreadsheetUrl'])
"
```
