---
name: change
description: >
  Create an OpenSpec-style change — the C-numbered sibling of /feature.
  Mints a C-row onto the backlog and materializes a changes/C###-slug/
  folder (proposal, tasks, optional design, specs delta). Use when the user
  says "create a change", "new change", "open a change for X", or when working
  in an anchor that has adopted the changes/+specs/ layout (F230).
user_invocable: true
---

# Change — OpenSpec Change Lifecycle
requires:: vault, anchor-cli, skill:feature, skill:mint, skill:finalize, facet:backlog
subsystem:: [[DAS Drive Design]] — the Drive group's subsystem profile

Create and drive a **change** — the OpenSpec-conformant unit of work defined by [[DAS Changes]]. A change is `/feature`'s sibling: same backlog lifecycle, same agreement gate, but its artifacts live in an anchor-root `changes/C<NNN>-<slug>/` folder in OpenSpec's file shapes instead of a single F-doc. Created per F230 (incremental OpenSpec adoption); the `Features/` path remains the default for anchors that haven't adopted `changes/`.

## When to Use

- The user asks to "create a change" / "open a change" (vs. "new feature").
- Working in an anchor that has a `changes/` folder (it has adopted the OpenSpec layout) and the unit of work should follow it.
- **Not** for anchors without `changes/` unless the user explicitly adopts the layout — adoption is deliberate, never inferred (F230 Q1: no wholesale conversion; existing-project migration is [[Tink Backlog#^F238|F238]], per-project and user-reviewed).

## Runbook

### 1. Mint the C-row

From the anchor (walk up from `cwd` to `.anchor`):

```bash
~/.claude/skills/workflow/scripts/state define {slug} Backlog C+ <<'EOF'
- **C001 — {Title}** [Designing] — {one-line what/why}
EOF
```

The echoed id (`{slug}: added C<NNN> …`) names everything downstream. C-numbers are monotonic per-anchor, zero-padded (`C023`), never reused — a namespace parallel to F-numbers ([[DAS Changes]] § C-numbers). Always address the row by its padded id (`C001`, not `C1`).

### 2. Materialize the change folder

Create `changes/C<NNN>-<kebab-slug>/` at the **anchor root** (create `changes/` on first use — that IS the adoption moment; confirm with the user if this is the anchor's first change):

- `proposal.md` — why + what. H1 `# C<NNN> — {Title}`; sections `## Why`, `## What Changes`. Open questions live here (the first H2 below the H1 while pending, per the [[DAS ask-format]] lifecycle) and are managed by `state <path-to-proposal.md> Q+ define` — the path form, since OpenSpec filenames repeat across changes. Each Q-body carries a `- **Damage:**` line (first word ∈ `waste`/`priority`/`irreversible`/`locking`/`taste`/`other`; `waste`/`priority` auto-resolve on define — [[DAS ask-format]] § The Damage field).
- `tasks.md` — the implementation checklist, `- [ ]` per task, ordered for execution. This is what `/mint` walks.
- `design.md` — only when the change carries real design decisions (omit otherwise; transient notes, not durable design).
- `specs/<capability>/spec.md` — the delta: `## ADDED` / `## MODIFIED` / `## REMOVED` requirement sections, each ADDED/MODIFIED requirement with ≥1 `#### Scenario:` Given/When/Then block ([[DAS Specs]] § Delta semantics).

Then update the row body with a path-qualified link:

```bash
~/.claude/skills/workflow/scripts/state set {slug} Backlog C<NNN> \
  --body "→ [[{anchor-relative-path}/changes/C<NNN>-<slug>/proposal|C<NNN> proposal]] · {one-line}"
```

### 3. Reach agreement — same gate as /feature

Resolve open questions (via `/ask` batching or inline when the user is engaged), then present the **compact confirm form** from `/feature` § 4 Reach Agreement — status line, Q-resolution one-liners, the numbered plan (here: the `tasks.md` checklist), one `Also:` line, single "Say go" ask. On agreement: row → `[Ready]` via `state … set --status Ready`, with the `- **Next:**` sub-bullet naming the first task.

### 4. Execute and close — handoffs

- **`/mint`** executes a `[Ready]` C-row: it reads `tasks.md` as the execution plan and checks boxes as work lands (see `/mint` § C-entries).
- **`/finalize`** closes a verified C-row with the **archive-merge**: fold the `specs/` delta into the anchor's `specs/`, reconcile `design/` content into durable design docs, move the folder to `changes/archive/`, row → `[Done]` (see `/finalize` § C-entry close-out).

## What this skill does NOT do

- Doesn't convert existing feature docs to changes (F238, later, per-project, user-reviewed).
- Doesn't create `specs/` content directly — durable specs are only written by `/finalize`'s merge.
- Doesn't run on anchors without `changes/` adoption; it offers adoption, the user decides.
