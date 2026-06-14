---
description: Query facet — the format of an anchor's `{NAME} queries.md`, the file `/query` builds to ask the user questions. Rules about what a valid queries file looks like.
---
# FCT Query
The asking surface: one `{NAME} queries.md` per anchor, in `{NAME} Track/`, that `/query` builds and trims.

| -[[FCT Query]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[FCT Track]] → [FCT Query](hook://p/FCT%20Query)<br>: the `{NAME} queries.md` format |
| --- | --- |
| Related | [[SKL Query]] (the skill that builds it),  [[FCT Status]],  [[FCT Messages]] |

**TLDR** — One `{NAME} queries.md` per anchor (cardinality: one), in `{NAME} Track/`, owned by the `/query` skill. Fixed five-section order (`## Agent Resolutions` → `## Verifications` → `## Immediate Questions` → `## Questions` → `## Ready`); empty sections omitted. Verifications are agent-run / user-judged — never "user runs X". Questions are self-contained or wiki-linked. The file shrinks toward empty as answers are applied. Validated by `/audit doc` via `R-query`.

## What it is

`{NAME} queries.md` is the single per-anchor surface where the user answers everything the agents need from them. The **`/query` skill** ([[SKL Query]]) *builds* it (the procedure — walking open questions, the determination routing, running verifications ahead of time, console echo); **this facet** governs what the resulting *file* must look like, so it can be audited (`/audit doc`, the F167 on-write hook). The skill cites these rules rather than restating them.

## Parts

- **Frontmatter + H1** — `description:` then `# {NAME} Queries`.
- **Five sections, fixed order** (each omitted when empty): `## Agent Resolutions`, `## Verifications`, `## Immediate Questions`, `## Questions`, `## Ready`.
- The file is **agent-owned and trimmed on answer** — answered items are removed, so it shrinks toward empty.

# RULESET R-query
include::
where:: file:{ANCHOR}/**/* queries.md
description:: the `{NAME} queries.md` format

What `/audit doc` checks on a queries file. The skill that produces it is [[SKL Query]]; these are the file-invariants it must satisfy. Format of this set: [[FCT Ruleset]].

## Structure

### RULE R-query-01 — Lives at `{NAME} Track/{NAME} queries.md` (checked)

One per anchor, slug-prefixed, in the tracking folder.

**Check pattern:** the file's basename is `{slug} queries.md` and its parent is `{slug} Track` (or a sub-folder rooted there).

### RULE R-query-02 — Opens with frontmatter `description:` then H1 `# {NAME} Queries` (checked)
check:: frontmatter_has description

**Check pattern:** YAML frontmatter present with a non-empty `description:`; the first body line is `# {NAME} Queries`.

### RULE R-query-03 — Five sections, fixed order, no others (checked)

Sections, when present, appear in this order and no foreign H2s interleave: `## Agent Resolutions` → `## Verifications` → `## Immediate Questions` → `## Questions` → `## Ready`. Empty sections are omitted.

**Check pattern:** the H2 sequence is a subsequence of `[Agent Resolutions, Verifications, Immediate Questions, Questions, Ready]`; no H2 outside that set.

## Verifications — agent runs, user judges

### RULE R-query-04 — Verifications are `V<n>` and end in a yes/no on an agent-produced artifact (checked)

Each `## Verifications` item is numbered `V1`, `V2`, … and asks the user to **judge** something the agent produced (an embedded image / output / rendered artifact), ending in a yes/no.

**Check pattern:** each Verifications bullet starts with `V<n>` and contains a yes/no prompt (e.g. `(yes / no)`); ideally an embed (`![[…]]`) or quoted output is present.

### RULE R-query-05 — A verification never asks the user to run/execute anything (checked)
check:: regex_absent (?im)^[-*]\s+\*\*V\d+.*\b(run|execute|launch|invoke)\b

The user is never told to *do* a thing — the agent runs it (ahead of time + embed, or live-on-ready) and the user only looks. Imperatives directed at the user are forbidden.

**Check pattern:** no Verifications line contains a user-directed run/execute imperative. (The live-fallback form "tell me when you're ready; I'll run it" is the agent offering to run — allowed.)

### RULE R-query-06 — No "verify F<n>" / whole-document eyeball (stated)

Forbidden verification forms: "verify F113" with no concrete artifact; "does this doc look right?" pointed at a whole multi-page document. A verification names the *specific* thing being judged.

## No orphan items

### RULE R-query-07 — Every item is answerable; no orphan actionable lines (stated)

Every line under Verifications / Immediate Questions / Questions is either a question the user answers or a check the user judges. An actionable item that is neither — work to be done — does **not** belong here: it is landed immediately or becomes a `[Ready]` feature on the backlog (and may appear under `## Ready`). A line that asks nothing and offers no judgeable artifact is a violation.

## Questions

### RULE R-query-08 — Immediate Questions are self-contained (stated)

Each `## Immediate Questions` item is readable without opening anything: one line of context (names the feature + what it's about) then a ≤2-line question, ideally yes/no.

### RULE R-query-09 — Catch-all Questions link in `F<n> Q<m>` form (checked)

`## Questions` items are wiki-links to the feature-doc question (`F<n> Q<m>`) or the feature, clickable to the concrete background — not free-text restatements.

**Check pattern:** each Questions bullet contains a `[[…]]` wiki-link; the visible token is `F<n>` or `F<n> Q<m>`.

### RULE R-query-10 — A feature with > 3 open questions is linked, not enumerated (stated)

When a feature has more than three open questions, `## Questions` carries a single link to the feature (answer in the doc), never the enumerated list.

## Resolutions & Ready

### RULE R-query-11 — Agent Resolutions are reversible-guess records, each linked (stated)

`## Agent Resolutions` items record a decision the agent made on its own — only for choices that are reversible AND soon-visible AND the agent has a sound basis for. Each names the decision + brief why, linked to the question's home, so the user can catch a wrong guess.

### RULE R-query-12 — Ready lists backlog `[Ready]` features and carries no questions (stated)

`## Ready` (optional) lists features that are `[Ready]` on the backlog, for visibility only. It contains no questions or verifications; the backlog is the source of truth.

# BRIEF

- **This file governs the `{NAME} queries.md` *file*** — sections + order + per-item validity. The *procedure* that builds it ( walking open questions, determination routing, run-verifications-ahead, console echo, trim-on-answer ) lives in the **[[SKL Query]]** skill, which cites `R-query` for the output shape. Two views of one system: facet = the artifact's rules; skill = how to produce it.
- **The load-bearing invariants:** verifications are agent-run / user-judged (never "user runs X" — R-query-04/05/06); no orphan items (R-query-07); questions are answerable + linked (R-query-08/09/10). These are what make a queries file trustworthy to answer.
- **Auditable:** `R-query` is in the `R-doc` umbrella, so `/audit doc {NAME} queries.md` and the on-write hook validate it. If the spec changes, fix it here — the skill follows.
