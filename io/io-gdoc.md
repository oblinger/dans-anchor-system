# /io gdoc — Google Docs

## Method 1: gsa CLI (preferred)

```bash
gsa docs read    <id>                    # Extract all text (plain text)
gsa docs info    <id>                    # Metadata (title, revision, char count)
gsa docs create  <title>                 # Create new empty document
gsa docs append  <id> <text>             # Append text at end
gsa docs insert  <id> <index> <text>     # Insert at character index
gsa docs replace <id> <old> <new>        # Find and replace (case-sensitive)
gsa search docs  [query]                 # Find documents
```

Auth: `~/.google_workspace_mcp/credentials/{user}@gmail.com.json`

**Notes:** Read returns plain text only — no formatting. Tables render as tab-separated. Replace is case-sensitive, replaces all occurrences.

## Method 2: python-docx (local .docx)

For local Word files or creating formatted documents to upload.

```python
from docx import Document
doc = Document('file.docx')
for para in doc.paragraphs:
    print(para.text)
```

## Method 3: browser (ctrl surf)

```bash
ctrl surf "https://docs.google.com/document/d/<id>/edit"
```
