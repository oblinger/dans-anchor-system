---
name: roster
description: >
  Show roster — concise summary of in-progress, ready, and backlog items
  for the current anchor, with totals at the bottom (including icebox count).
  Use when the user says "show roster", "roster", "what's on the backlog",
  or asks for a state-of-the-work view.
tools: Read, Bash, Glob, Grep
user_invocable: true
---

# Roster — Backlog & In-Flight Summary

Render a concise view of what's currently in flight, what's ready to start, and what's deferred — drawn from the current anchor's Backlog file (and Icebox, if present).

DMUX trigger: **`show roster`** (two words). Skill name is just `roster`.

## When to Use

When the user types `roster` or `show roster`, or asks for a quick view of what's in progress, ready, or on the backlog.

## Output

Print these sections in order, **omitting any section with zero items**. Each entry shows its **B-number** so the user can refer to it unambiguously ("do B5", "tell me about B12"):

```
## Active
- **B<n> — <Item Name>** — <one-line gloss>

## Ready
- **B<n> — <Item Name>** — <one-line gloss>

## Backlog
- **B<n> — <Item Name>** — <one-line gloss>

---
{N} in progress · {N} ready · {N} backlog · {N} icebox
```

The **footer line always prints**, even when buckets are zero — the user sees the full picture every time.

The **Icebox is counted but never listed**.

The B-number is parsed from the source bullet. Source format per [[CAB Backlog]]: `- **B<n> — Item Name** — description`. If a backlog item lacks a B-number, render it as `- **Q?** — <Item Name>** — gloss` and flag the missing number — but don't fix it inline; that's a job for the skill that edits the backlog.

## Sources

Find the current anchor by walking up from `cwd` until you hit `.anchor`. Read `{NAME} Docs/{NAME} Plan/{NAME} Backlog.md` (and `{NAME} Icebox.md` if it exists).

| Source | Roster bucket |
|--|--|
| `## Active` H2 in Backlog | In Progress |
| `## Ready` H2 in Backlog | Ready |
| Any other H2 in Backlog except `## Verify`, `## Done` | Backlog |
| `## Verify`, `## Done` | (not shown) |
| Items in any H2 of Icebox file | Icebox count only |

Missing sections / files → zero items.

## Item Format

Each source entry is a Q-numbered named-list bullet:

```
- **B<n> — Item Name** — short description
```

Render the B-number and name together in bold, separated by an em-dash, exactly as in the source. Gloss the description to the first sentence or ~70 chars (whichever is shorter), suffix `…` if clipped. Preserve the source order within each bucket.

## Counts

Count bullets under the relevant H2 sections by reading the file directly. No code helper needed.

- **In Progress** — bullets under `## Active`
- **Ready** — bullets under `## Ready`
- **Backlog** — bullets under any other H2 in the Backlog file, excluding `## Verify` and `## Done`
- **Icebox** — bullets across all H2 sections in `{NAME} Icebox.md`, or `0` if the file doesn't exist

## Failure Modes

- **No anchor found** — say "No anchor found from `<cwd>` upward." and stop.
- **No Backlog file** — say "No `{NAME} Backlog.md` at `<expected path>`." and stop.
- **Empty file** — print just the footer line, all zeros.

## Notes

- Render directly in chat; don't write to a file.
- The "In Progress" and "Ready" sections are defined in [[CAB Backlog]] — that's the source of truth for what they mean and how items flow between them.
