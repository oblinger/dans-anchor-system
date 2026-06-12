# /io gsheet — Google Sheets

## Method 1: gsa CLI (preferred)

```bash
gsa sheets read  <id> [range]          # Read cells as JSON
gsa sheets write <id> <range> <json>   # Write cells
gsa sheets append <id> <range> <json>  # Append rows
gsa sheets info  <id>                  # Sheet metadata
gsa search sheets [query]              # Find spreadsheets
```

Auth: `~/.google_workspace_mcp/credentials/{user}@gmail.com.json`
IDs: full Google URL or bare document ID.

**Data format:** Read returns JSON array of arrays. Write/append takes JSON: `'[["A","B"],["C","D"]]'`

**Creating new sheets:** Use Python inline — see `io-gmail-api.md` for the token refresh pattern, then POST to `https://sheets.googleapis.com/v4/spreadsheets`.

## Method 2: python openpyxl (local .xlsx)

For local Excel files only. No auth needed.

```python
from openpyxl import load_workbook
wb = load_workbook('file.xlsx')
ws = wb.active
for row in ws.iter_rows(values_only=True):
    print(row)
```

## Method 3: browser (ctrl surf)

Fallback when API auth is expired.

```bash
ctrl surf "https://docs.google.com/spreadsheets/d/<id>/edit"
```
