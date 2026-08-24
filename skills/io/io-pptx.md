# /io pptx — Microsoft PowerPoint (local .pptx, live-coordinated)

Read and edit a local **`.pptx`** as if it were live-editable alongside a running PowerPoint. Backed by the **`io-pptx`** CLI (`~/.claude/skills/io/scripts/io-pptx`, on PATH as `io-pptx`). Sibling of [[io-excel]] — same handshake, same contract, retargeted from grid to slides.

## Why this exists

PowerPoint holds the open presentation in memory, doesn't watch the file, and overwrites it on save — so naïve disk edits get clobbered. `io-pptx` wraps every operation in an AppleScript handshake so it *behaves like live editing*:

- **before a READ** → save that presentation in PowerPoint (by name) so disk == the user's latest.
- **after a WRITE** → reload that presentation in PowerPoint from disk, so it shows the change and can't clobber it on a later save.

**Window stability (2026-08-24):** the reload puts the window back exactly where it was — same position, same size, same display, full-screen re-entered if it was full-screen — and PowerPoint is activated only if it was already the frontmost app. An agent edit must never rearrange the user's screen or steal focus mid-task. (The restore re-applies until it sticks, because PowerPoint re-cascades the window as the document finishes loading.)

Edits go through python-pptx, which round-trips the XML package **in place** — charts, images, media, themes, and transitions it doesn't model survive untouched (safer than openpyxl in this regard). Text replacement reuses the paragraph's first-run font, so shape-level styling, sizes, and theme survive.

## Method 1: io-pptx CLI (preferred)

```bash
io-pptx probe <file>                                  # slides, shapes, layouts (cheap orient)
io-pptx read  <file> [--slide N] [--format md|json]   # titles, bullets, tables, notes
io-pptx set   <file> --title-contains "Q3" --value "New title"          # locate-by-title (preferred)
io-pptx set   <file> --slide 2 --shape "Content Placeholder 2" --value $'Bullet\n\tsub-bullet'
io-pptx set-notes <file> --slide 1 --value "Speaker notes"
io-pptx add   <file> --title "Risks" --bullets $'Churn\n\tmitigation' [--layout NAME|N]
```

- **Slide addressing**: `--slide N` (1-based) or `--title-contains S` — the latter is resilient to the user reordering slides (the locate-by-key analog); it errors if ambiguous.
- **Shape addressing**: `--shape NAME` (names shown by `probe`); default is the title placeholder.
- **Multi-paragraph text**: `\n` splits paragraphs/bullets, leading tabs set indent level (use `$'...'` in bash).
- **`-v/--verbose`** prints the live-handshake result (`flushed` / `reloaded` / `not-open` / `skip`) to stderr.
- **`--no-live`** skips the PowerPoint handshake (pure disk op).

## The coordination contract

Same as [[io-excel]]: **the user's work must be saved before the agent writes.** The post-write reload discards any *unsaved* changes in PowerPoint — "⌘S before handing it to me" is the whole protocol. The agent's edits then flow to the user automatically (write → reload). The pre-read flush means the agent always sees the user's latest, saved or not.

## Off-Mac — degrades gracefully

The live handshake is **macOS-only** (AppleScript). Elsewhere the platform gate (`IS_MAC`) makes every live op a no-op and `io-pptx` still works fully as a plain disk reader/editor through python-pptx.

## Caveat — run-level formatting collapses on replaced text

`set` preserves the *paragraph's* formatting by copying the first run's font onto the new text — but mixed formatting **within** a replaced text frame (one bolded word mid-bullet) collapses to that single style. Everything not touched by the edit — other shapes, charts, pictures, theme, transitions — is untouched byte-for-byte. Building/editing charts is out of scope; do those in PowerPoint by hand.

## Method 2: ad-hoc python-pptx — FULL control (not an afterthought)

Slide work is open-ended — layout surgery, per-run formatting, images, colors, moving shapes — and the CLI deliberately does not try to be a language for all of it. **The agent has the entire python-pptx object model**, and the `flush`/`reload` verbs bracket any ad-hoc work with the same live handshake:

```bash
io-pptx flush deck.pptx        # before your reads: disk now == the user's live state
python3 your_arbitrary_pptx_edit.py
io-pptx reload deck.pptx       # after your writes: PowerPoint now shows your work
```

The CLI verbs are conveniences for the common ops; this bracket is the general contract. For the rare thing python-pptx can't express (running a slideshow, exporting, chart internals), drive the live app directly via AppleScript (`tell application "Microsoft PowerPoint"`) — no handshake needed since you're editing the live copy itself, but leave the presentation saved when done.
