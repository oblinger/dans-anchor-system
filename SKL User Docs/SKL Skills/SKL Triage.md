# /Triage

Surface every item across the current anchor that requires user involvement — pending questions in feature docs and items in `[Verify]` state — into one batched inbox at `{NAME} Triage.md`. The user reads the inbox and answers with shorthand.

DMUX trigger: **`triage`** (prefix-trigger; speaking `triage` stashes `/triage`, parallel to `snip` / `commission` / `fortify` / `groom`). Punctuation: **`"`** (a single double-quote as the entire message), parallel to `crank`/`'` and `/land`/`.`. Slash invocation: `/triage`, `/triage roadmap`, `/triage milestone {N}`.


## What it does

Walks the anchor's backlog, finds every item in `[Questions]` or `[Verify]` state, and writes a destructively-rewritten `# [[{NAME}]] Triage` H1 banner + horizon-H2 body at `{NAME} Docs/{NAME} Plan/{NAME} Triage.md`. The whole file is agent-owned; the user reads and responds.

**Also regenerates the anchor's H2 in `~/ob/kmr/Q.md`** — the vault-level Agent Status dashboard. Both `/ask` and `/triage` produce a fresh local triage + a fresh Q.md anchor entry on every invocation (per F25).

Pairs with `/groom` (which *creates* `[Questions]` state by parking work) and `/roster` (state-of-the-work). `/triage` is roster-for-user-input: same per-bucket counts, but the body is filtered to items needing your attention.


## What you'll see

The Triage file opens at the end of every run. Top of the file is a banner:

```
# [[ACME]] Triage   -   Active: 1    Ready: 2    Now: 3    Next: 1    Later: 0    Verify: 1    Icebox: 4
```

Below the banner, items are grouped under their **horizon H2** (`## Now`, `## Next`, `## Later`) — exactly mirroring where they live in the backlog. Sections with no qualifying items are omitted.

Each row carries the existing `[Status]` bracket so you can scan: `[Questions]` items show `→ [[Feature Doc]]` + a count of pending Qs; `[Verify]` items show the verify-plan text the agent wrote when the item was set to Verify, plus up to three wiki-links at the end (feature, agent doc, user doc).


## How you respond

| You say | Agent does |
|---|---|
| `F5 Q4: yes` | Resolves Q4 in F5's feature doc with answer "yes". Moves the question to `### Resolved`. |
| `Q4: yes` (after announcing sticky context "I'm in F5 now") | Same as above. Sticky context survives turn-to-turn until you switch ("now F12"). |
| `verified F23` / `F23 verified` | Moves F23's backlog row from its horizon (with `[Verify]` bracket) to `## Done`; updates feature-doc Status to Done. |
| `F23 nope, X is broken` | Captures rejection; agent files a follow-up bullet on the backlog row and continues design. |


## Compound usage

**"triage and groom"** (or "groom and then triage") — runs `/groom` first to park new items in `[Questions]`, then `/triage` to surface the inbox. Pilot-level natural-language interpretation; both skills stay small.


## When to invoke

- After a long session where the agent has been parking questions; you want to see what's piled up.
- Whenever you switch context and want to know what's currently waiting on you.
- After a `/groom` run to immediately surface the freshly-parked items.
- Default check-in at the start of an engagement session.


## Idempotence

Strictly idempotent + destructive. The whole file (below YAML frontmatter) is agent-owned and rewritten on every run. There are no marker comments, no preserve-user-edits regions — anything the user wants to persist belongs in the relevant feature doc, not the Triage file.
