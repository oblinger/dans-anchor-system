# /io notion — Notion

**Status: Not yet set up.** Requires creating a Notion integration.

## Method 1: Notion API (preferred — TBD)

Setup required:
1. Go to https://www.notion.so/my-integrations
2. Create integration ("Claude Access")
3. Copy the API key
4. Share pages/databases with the integration
5. Store key at `~/.config/notion/api_key`

```python
# pip install notion-client
from notion_client import Client
notion = Client(auth="secret_...")
results = notion.search(query="meeting notes")
page = notion.pages.retrieve(page_id="...")
```

## Method 2: Notion export (manual)

Export pages as Markdown from Notion UI: three-dot menu → Export → Markdown & CSV.

## Method 3: browser (ctrl surf)

```bash
ctrl surf "https://www.notion.so/<page-id>"
```

Note: Notion in browser can be slow to load. May show gray screen for 10-15 seconds.
