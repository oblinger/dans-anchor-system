---
name: google
description: >
  Google Workspace integration — Sheets, Slides, Drive search.
  Uses the gsa CLI tool with direct REST API calls and existing OAuth credentials.
  Use with an action argument: /google sheets, /google slides.
  Invoke bare (/google) for the quick-reference command summary.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Google — Workspace Integration

Read and write Google Sheets and Slides via the `gsa` CLI tool. No MCP server needed.


| ACTIONS            | File               | Description                                   |
| ------------------ | ------------------ | --------------------------------------------- |
| `/google sheets`   | [[google-sheets]]  | Read, write, append, search spreadsheets      |
| `/google slides`   | [[google-slides]]  | Read, update, search presentations            |


## Quick Reference

```bash
# Sheets
gsa sheets read  <id> [range]            # Read cells as JSON
gsa sheets write <id> <range> <json>     # Write cells
gsa sheets append <id> <range> <json>    # Append rows
gsa sheets info  <id>                    # Sheet metadata

# Slides
gsa slides read  <id>                    # Extract all text
gsa slides info  <id>                    # Presentation metadata
gsa slides add-slide <id> [layout]       # Add a blank slide
gsa slides update-text <id> <obj> <text> # Replace text in a shape

# Search
gsa search sheets [query]                # Find spreadsheets
gsa search slides [query]                # Find presentations
```

IDs accept full Google URLs or bare document IDs.


## Auth

- OAuth credentials: `~/.google_workspace_mcp/credentials/{user}@gmail.com.json`
- Token refreshed automatically on every call (~200ms)
- Google Cloud project: `oblio-claude-access`
- Script: `~/bin/gsa` (symlink to `Claude App/Google Suite Access/gsa`)


## Dispatch

On invocation:

1. Parse the argument to determine the action
2. Look up the file from the Actions table above
3. Read that file from this skill's directory and execute its workflow
4. If no argument or unrecognized argument, display the Quick Reference above
