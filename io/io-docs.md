# google-docs — Google Docs

Read and write Google Docs using the `gsa` CLI tool.

## Commands

```bash
gsa docs read    <id>                    # Extract all text as plain text
gsa docs info    <id>                    # Document metadata (title, revision, char count)
gsa docs create  <title>                 # Create a new empty document
gsa docs append  <id> <text>             # Append text at end of document
gsa docs insert  <id> <index> <text>     # Insert text at character index
gsa docs replace <id> <old> <new>        # Find and replace text (case-sensitive)
gsa search docs  [query]                 # Find documents (newest first)
```

## IDs

The `<id>` argument accepts either:
- A full Google URL: `https://docs.google.com/document/d/1abc.../edit`
- A bare document ID: `1abc...`

## Data Format

- **Read output:** Plain text with tabs for table cells, newlines for rows
- **Info output:** JSON with documentId, title, revisionId, characterCount
- **Create output:** JSON with documentId, title, url
- **Append/insert output:** JSON with inserted char count and index
- **Replace output:** JSON with replacement count

## Examples

```bash
# List recent documents
gsa search docs

# Find documents by name
gsa search docs "Meeting Notes"

# Read all text from a document
gsa docs read 1abc...xyz

# Get document metadata
gsa docs info 1abc...xyz

# Create a new document
gsa docs create "Project Notes"

# Append a paragraph
gsa docs append 1abc...xyz "New paragraph at the end."

# Find and replace text
gsa docs replace 1abc...xyz "old phrase" "new phrase"

# Insert text at a specific position (character index)
gsa docs insert 1abc...xyz 42 "inserted text"
```

## Notes

- The `read` command extracts plain text only — formatting (bold, italic, etc.) is not preserved
- Tables are rendered as tab-separated values
- The `append` command inserts text just before the document's final newline
- The `replace` command is case-sensitive and replaces all occurrences
- Character indices for `insert` start at 1 (index 1 = beginning of document body)
