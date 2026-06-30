# /io excel — Microsoft Excel (local .xlsx, live-coordinated)

Read and edit a local **`.xlsx`** as if it were live-editable alongside a running Excel. Backed by the **`io-excel`** CLI (`~/.claude/skills/io/scripts/io-excel`, on PATH as `io-excel`).

## Why this exists

Excel holds the open workbook in memory, doesn't watch the file, and overwrites the file on save — so naïve disk edits get clobbered. `io-excel` wraps every operation in an AppleScript handshake so it *behaves like live editing*:

- **before a READ** → save that workbook in Excel (by name) so disk == the user's latest.
- **after a WRITE** → reload that workbook in Excel from disk, so Excel shows the change and can't clobber it on a later save.

Edits are **formatting-preserving**: load-modify-save through openpyxl, setting cell `.value` only — widths, heights, fills, fonts, conditional formatting, freeze panes, filters all survive.

## Method 1: io-excel CLI (preferred)

```bash
io-excel probe <file>                                   # sheets, dims, headers (cheap orient)
io-excel read  <file> [--sheet S] [--cols ...] [--where "COL op VAL"] [--format md|tsv|json]
io-excel set   <file> --cell G5 --value "..."           # direct cell
io-excel set   <file> --key-col A --key S4 --col Workaround --value "..."   # locate-by-key (preferred)
io-excel from-md <file> --md <doc.md> [--table N | --list] [--sheet NAME]   # build a grid from a markdown table
```

- **`--where`** ops: `contains`, `startswith`, `=`, `!=` — e.g. `--where "Segment contains sales"`.
- **`--cols`** accepts header names *or* column letters: `--cols "#,Segment,Workaround"` or `--cols "A,B,G"`.
- **`set` defaults to locate-by-key** (resilient to the user reordering rows); use `--cell` only when the address is stable.
- **`-v/--verbose`** prints the live-handshake result (`flushed` / `reloaded` / `not-open` / `skip`) to stderr.
- **`--no-live`** skips the Excel handshake (pure disk op).

## The coordination contract

The one rule that makes this safe: **the user's formatting must be saved before the agent writes.** The post-write reload discards any *unsaved* changes in Excel. Since the user's edits are mostly formatting and infrequent, "⌘S before handing it to me" is the whole protocol. The agent's edits then flow to the user automatically (write → reload), approximating markdown's live round-trip.

## Off-Mac — degrades gracefully

The live handshake is **macOS-only** (it's AppleScript). On Linux/Windows the platform gate (`IS_MAC`) makes every live op a no-op, so `io-excel` still works fully as a **plain disk reader/editor** — `probe`/`read`/`set`/`from-md` all run through openpyxl exactly the same, formatting preserved. The only difference: you save / reload your spreadsheet app (Excel, LibreOffice) by hand instead of the tool doing it. The skill is functional everywhere; it's just *automatic* on a Mac.

## Caveat — openpyxl-modeled content only

`io-excel` round-trips through openpyxl's object model, which does **not** represent **charts, embedded images, pivot tables, slicers, or macros/VBA** — those are dropped on save. Do not use `set`/`from-md` on a workbook containing them. Cells + standard formatting are safe.

## Method 2: ad-hoc openpyxl (escape hatch)

For operations the CLI doesn't cover (multi-cell transforms, pivot-style aggregation), write inline Python against openpyxl — but reuse the same discipline: `flush_live` before read, `reload_live` after write (the functions live in the `io-excel` script).
