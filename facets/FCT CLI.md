---
description: CLI command reference — every command, flag, and exit code
---
# FCT CLI

Facet spec for `{NAME} CLI.md` — the exhaustive command/flag/exit-code reference page for an anchor that ships a CLI.

**Location:** `{NAME} Docs/{NAME} User/{NAME} CLI.md`


`{NAME} CLI.md` is the **complete command reference** for an application that ships a command-line interface. Every command the app exposes, every flag on each command, every exit code — one page, reference-style. Think "man page" as a markdown doc.

**Only create this file when the anchor actually has a CLI.** It is optional. Applications without a command-line interface (GUI-only, library-only, daemon-only) should not have one.

**Working example:** `~/.claude/skills/CAE/CAE Docs/CAE User/CAE CLI.md` — CLI reference.

**Relationship to other docs:**
- [[CAB User Guide]] / `{NAME} User Guide.md` — **tutorial**. Teaches the CLI by example, narrative-style. Mentions only the commands a new user needs.
- [[FCT CLI]] / `{NAME} CLI.md` — **reference**. Every command, every flag, exhaustive. Readers arrive here knowing what they want to look up.
- [[FCT UX Design]] — specifies the CLI shape during design. When an anchor's UX Design calls for a CLI, `/feature`-style work should produce this CLI doc as the user-facing output.

When both exist, User Guide links to CLI for "full reference" and CLI can link back to User Guide for "getting started."


# Reference Example
---

````markdown
---
description: CLI command reference for {app-name}
---

# {NAME} CLI

| -[[{NAME} CLI]]- | |
| --- | --- |
| --- | |

```
{app-name} --help                                                 # Show this help text
{app-name} --version                                              # Print version
{app-name} submit --deadline <time> [--retry N] -- <cmd>          # Enqueue a task at the deadline
{app-name} status [--json] [--filter <state>]                     # Show task states and queue depth
{app-name} cancel <task-id>                                       # Cancel a pending task
{app-name} drain [--timeout <sec>]                                # Wait for all pending tasks
```

For a tutorial introduction, see [[{NAME} User Guide]]. Per-command detail below: [[#submit]], [[#status]], [[#cancel]], [[#drain]].


## submit

Enqueue a task for execution at or after a deadline.

**Usage:**
```
{app-name} submit --deadline <ISO-8601> [--retry <N>] [--priority <0-9>] -- <command> [args...]
```

**Flags:**

| Flag           | Type        | Default | Description                                    |
|----------------|-------------|---------|------------------------------------------------|
| `--deadline`   | ISO-8601    | —       | Earliest time the task should run. Required.  |
| `--retry`      | int         | 3       | Max retries before the task is marked failed. |
| `--priority`   | 0–9         | 5       | Higher = runs sooner among same-deadline set. |

**Exit codes:**

| Code | Meaning                                      |
|------|----------------------------------------------|
| 0    | Task enqueued; task ID printed on stdout.   |
| 1    | Usage error (missing required flag, etc.).  |
| 2    | Scheduler unreachable or shutdown.          |

**Example:**
```bash
{app-name} submit --deadline 2026-04-21T15:00:00 --retry 5 -- ./build.sh
# → t-4f2
```


## status

Print current scheduler state and task list.

... (same shape for each command)


## Exit Codes (global)

| Code | Meaning                                                   |
|------|-----------------------------------------------------------|
| 0    | Success.                                                  |
| 1    | Usage error — bad flags, missing args, invalid values.    |
| 2    | Runtime error — scheduler down, DB locked, permission.    |
| 64   | Configuration error — invalid config file.                |
```

---



# Format Specification

## Location

`{NAME} CLI.md` lives in `{NAME} Docs/{NAME} User/{NAME} CLI.md`. It is a user-facing document — users reach for it when they need to look up syntax.

## Required Sections

| Section | Purpose |
|---------|---------|
| **Help block** (FIRST, directly under H1) | Fenced code block with every command on one line + trailing `# comment`. See below — this rule is non-negotiable. |
| **Per-command H2** | One section per command with Usage / Flags / Exit codes / Example |
| **Exit codes (global)** | Table of app-level exit codes (in addition to per-command) |

## The Help Block — READ THIS

**Non-negotiable: under the `# {NAME} CLI` H1 (with the standard dispatch-table placeholder per F060), the very next content is the fenced help code block.** No intro paragraph, no Synopsis section, no description between the dispatch table and the help fence.

Inside the fence: every command the CLI exposes, one per line, with a `#` comment at the end of the line describing its purpose. The block looks exactly like the `--help` output of a well-written UNIX tool. It is the reader's single-page reference.

**Template:**

````
# {NAME} CLI

| -[[{NAME} CLI]]- | |
| --- | --- |
| --- | |

```
{app-name} --help                                  # Show this help text
{app-name} --version                               # Print version
{app-name} <cmd-1> <sig>                           # <purpose>
{app-name} <cmd-2> <sig>                           # <purpose>
...
```

<optional one-line pointer to User Guide and per-command anchors>

## <cmd-1>
...
````

**Rules for the block:**

- **Fenced code block (```...```), NOT 4-space indent.** The fence must be the first non-frontmatter content under the H1.
- **Complete.** Every command the binary exposes appears here. Include `--help` and `--version` as their own lines.
- **One line per command.** Multi-line invocations are disallowed in the block; split rare corner cases to the per-command H2 section below.
- **Trailing `# comment` on every line.** The comment is the one-line purpose. Align the comments to a consistent column across rows (same alignment discipline as [[FCT Files]]).
- **Flags in summary form.** `[--json]`, `[--filter <state>]` — just enough to know what the command takes. Full flag reference lives in the per-command H2 sections below.
- **No wiki-links inside the block.** Code blocks don't render them; navigation links go in the line immediately after the block.
- **Matches `{app-name} --help` output as closely as reasonable.** If the binary supports `--help`, the block is a rendered version of that output.

**Nothing else is allowed before the block.** No preamble paragraph, no "For a tutorial introduction, see ...", no Synopsis section — all of that goes *after* the block.

## Optional Sections

| Section | When to include |
|---------|-----------------|
| **Environment variables** | If the CLI respects any (e.g., `TSK_CONFIG`, `NO_COLOR`) |
| **Config file** | If the CLI reads a config file — document the format |
| **Output modes** | If the CLI has `--json` / `--quiet` / `--verbose` patterns |
| **Signal handling** | If long-running commands respond to SIGINT / SIGTERM differently |

## Per-Command Structure

Each H2 section for a command has the same shape so readers can skim without re-learning the layout:

1. One-line description
2. **Usage** — code block with the canonical invocation pattern
3. **Flags** — 4-column table: `Flag | Type | Default | Description`
4. **Exit codes** — 2-column table (if any are command-specific; otherwise fall back to global)
5. **Example** — at least one realistic copy-pasteable bash example with expected output

Keep examples short. For long walkthroughs, link to [[{NAME} User Guide]].

## Linking

The CLI doc must be linked from:

1. **`{NAME} User.md` dispatch page** — as a row: `| [[{NAME} CLI\|CLI]] | command reference |`
2. **`{NAME}.md` anchor page** — as an inline highlight on the User row: `| User | [[{NAME} User Guide\|User Guide]], [[{NAME} CLI\|CLI]] |`

`/audit docs` should flag missing CLI doc on anchors whose UX Design spec calls for one.

## When to Create

Create `{NAME} CLI.md` when:

- The anchor ships an executable binary (Rust `[[bin]]`, Python entry point, shell script, etc.), AND
- That binary has more than one command OR more than a few flags worth documenting, AND
- External users (not just the maintainer) need to look up syntax

Applications with only a one-shot entry point (e.g., `tool --input FILE --output FILE`) can document the usage inside `{NAME} User Guide.md` without a separate CLI doc.

## Lifecycle

- **Create** when the CLI surface becomes non-trivial — typically right after the first user-facing release
- **Update** with every new command, flag, or exit code — the CLI doc is generated or hand-written, but either way it must reflect what the binary actually does
- `/audit docs` can cross-check the CLI doc against `--help` output if the CLI supports a machine-readable help mode

# BRIEF

- **This file is the facet spec for `{NAME} CLI.md`** — it defines the structure (mandatory help block first, per-command H2s, exit-code tables) every anchor's CLI reference must conform to. Edits here change the contract for all CLI docs across the vault.
- **NOT a CLI doc itself.** Do not document a real binary's commands here; concrete examples live in linked working examples (e.g. `CAE CLI.md`). Keep instance content out of the spec.
- **Inclusion test for new rules:** a rule belongs here only if it applies to *every* `{NAME} CLI.md` regardless of anchor. Anchor-specific quirks belong in that anchor's CLI doc or its `{NAME} Rules.md`, not here.
- **Load-bearing constraint — the help-block-first rule is non-negotiable.** The fenced help block sits directly under the H1 + dispatch table with no preamble. Do not weaken this rule or add intro-paragraph exceptions; the §The Help Block section is the canonical source.
- **Cross-cite rather than inline.** Tutorial/narrative content belongs in [[CAB User Guide]]; CLI-shape design belongs in [[FCT UX Design]]; markdown rendering rules belong in [[R-markdown]]. If a rule starts to drift toward one of those, move or link rather than duplicate.
- **When updating the template:** keep the Reference Example block, the Format Specification, and the dispatch-table placeholder (`| -[[{NAME} CLI]]- | |`) in sync — readers copy from the Reference Example, validators read the Format Specification.
- **Linking discipline (§Linking) is load-bearing for `/audit docs`.** Do not change the required link locations (`{NAME} User.md` row + `{NAME}.md` User cell) without updating the audit script in lockstep.
