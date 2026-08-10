---
description: "Two worked CLAUDE.md files — the plain-content tier and the agentic-project tier — as the DAS Claude facet's in-repo example"
---

| -[[FEX Claude]]- | → [[DAS]] → [[examples]] → [FEX Claude](hook://p/FEX%20Claude)  |
| --- | --- |
| Related | [[DAS Claude]],   |

# FEX Claude
Two complete `CLAUDE.md` files at the facet's two tiers: a plain-content anchor that only needs commands and architecture, and an agentic-project anchor that opens with a Pilot role declaration.

**Why this file is not a `CLAUDE.md`.** A real `CLAUDE.md` anywhere in this tree would be **loaded as live instructions** by any Claude Code session rooted at or below it — an example would start configuring the agent reading it. So the two instances below are quoted inside a teaching artifact instead, and their headings carry backslash escapes (`\## Mission`) so the quoted outline does not merge into this document's own. This is the same escaping convention [[DAS Claude]] uses in its inline reference block; preserve the backslashes when editing.

Both instances are **abridged from real files**, not invented — the plain-content tier from the `KM` anchor's `CLAUDE.md`, the agentic tier from `Hook Anchor`'s. What was cut is length, not shape.

## Tier 1 — plain content

The common case. No Pilot line, no role declaration: a mission, the commands that actually get run, and enough architecture that the agent does not have to rediscover the module layout on every session.

---

\## Commands

\### Main script usage
- `python3 hbr` — run the full catalog cycle (scan, dedup, checkpoint)
- `python3 hbr -s` — scan the media roots for new files
- `python3 hbr -d` — rebuild the content-hash dedup index
- `python3 hbr -k` — write a catalog checkpoint

\### Development commands
- `python3 -m py_compile hbr` — syntax check the main script
- `python3 -c "import hbr_lib"` — test module imports

\## Architecture

A home media catalog operating over the library at `~/media/harbor`. The single `hbr` script drives everything; the work is split across modules:

- **hbr_scan.py** — walk the media roots, stat and enqueue new files
- **hbr_hash.py** — content hashing and duplicate resolution
- **hbr_catalog.py** — catalog table generation and checkpointing
- **hbr_lib.py** — shared utilities, constants, file operations

\### Core workflow

`execute_all()` runs: scan roots → hash new files → resolve duplicates → write checkpoint.

---

## Tier 2 — agentic project

Adds one thing, and it must be the **first line of the file**: the Pilot role declaration, which is what makes the session adopt the role on startup and again after every compaction. Everything below it is ordinary `CLAUDE.md` content.

Note what this tier is really for. The body below is not documentation — it is a set of standing prohibitions written in the imperative, because the anchor is driven by agents and the expensive failures are the ones an agent commits confidently. That is the tier's actual signature, more than the Pilot line is.

---

You are the Pilot for the Harbor project. Role: `~/.claude/skills/role/role-pilot.md`

\## Split anchor structure

This project uses a Split Anchor layout:
- **Anchor root** (here): `~/notes/harbor/` — inside the vault
- **Planning / design / dev docs**: at the anchor root — `HBR Track/`, `HBR Design/`, `HBR Dev Docs/`
- **Code**: `~/code/harbor/`

Edit documentation here in the vault. Code changes go through the code path above.

\## ⚠️ Never copy binaries

**There must be only one copy of each binary on the system.**
- The only binaries live in `~/code/harbor/target/release/`
- `/Applications/Harbor.app` contains **symlinks**, not copies
- Never use `cp` on a Harbor binary — if a symlink is broken, recreate it

\## Commands

```bash
ha -p HBR                    # find anchor path
cargo test                   # run tests
cargo run -- --help          # CLI help
```

---

## What both tiers leave out

Neither instance restates project-wide agent policy — commit conventions, trigger words, shared tool usage. That lives in the global `~/.claude/CLAUDE.md` and is cited from an anchor's file where relevant, never copied into it. An anchor `CLAUDE.md` that re-declares global policy drifts from it silently, and the agent has no way to tell which copy is current.

Neither carries a dispatch table. `CLAUDE.md` is exempt from the F060 top-of-doc rule ([[DAS Claude]] § F060 — exempt) because the harness consumes it, not a reader navigating the anchor — the first lines are reserved for the Pilot declaration and the mission.

Neither opens with a `# CLAUDE.md` H1 either. The filename already says what the file is, and the first screen is worth more as content than as a restatement of the name.

# BRIEF

- **This file is an example, not a template.** Copying it wholesale produces a `CLAUDE.md` describing Harbor and KM. Copy the *shape* — mission, commands, architecture, prohibitions — and write the content from the anchor in front of you.
- **Keep the heading escapes.** The `\##` prefixes are load-bearing: without them the quoted headings join this document's outline and the two instances stop being distinguishable from the commentary around them.
- **Keep both instances abridged from real files.** If a tier needs a new section, take it from a live `CLAUDE.md` rather than inventing one — the facet's value is showing what these files actually look like, and an invented section is exactly the kind of thing that gets copied forward and never questioned.
- **Governed by [[DAS Claude]]** and its ruleset [[R-fct-claude]]; changes to the facet's required contents land there first, here second.
