# architect-overview — Portable bare-project architecture overview

The portable, bare-project sub-action of `/architect` (per [[F184 — Skill portability — architect bare-project mode + environment gating|F184]]). Produces an **`Architecture Overview.md` + an embedded hand-drawn SVG** for *any* codebase — including one with **no CAB scaffolding** (no `.anchor`, no `{NAME} Dev/` module docs, no `{NAME} Docs/…` layout) and **no kmr vault**. This is the entry point a colleague uses after cloning `ob-skills` onto a fresh machine.

It is deliberately lighter than the full `/architect` runbook: it reads the repo *itself* as ground truth (there are no module docs to roll up), writes one self-contained folder, and touches nothing vault-coupled.

## When to use

- The user runs `/architect overview <subject>`.
- The working tree is a plain codebase with no CAB anchor, and the user wants a top-level architecture document with a diagram.
- A colleague with only the cloned skills wants "an architecture overview of this repo, with the SVG drawn by the viz skill."

For a CAB-structured anchor (module docs present), use plain `/architect` / `/architect update` instead — it does the richer rollup with bidirectional module-doc linking.

## Subject is required — never no-op

`/architect overview` **must be told what to architect.** The `<subject>` argument names the target: a path, a repository, a directory, or a named scope within the codebase.

- **Subject given** (`/architect overview ./src`, `/architect overview the payments service`, `/architect overview .`) → proceed.
- **No subject given** (`/architect overview` with nothing after it) → **ask, in one line: "What do you want me to architect? (a path, a repo, or a named part of the system)"** and stop. Do **not** guess a target, scan the whole machine, or silently do nothing. A bare architect with no subject has nothing to architect.

Resolve the subject to a concrete root directory (or set of paths) before scanning. If the subject is a description rather than a path ("the auth layer"), map it to the relevant directories first, confirming the mapping in one line if it's ambiguous.

## Runbook

### 1. Resolve subject + project name

- Confirm the subject resolves to one or more real paths under the cwd (or an absolute path the user gave).
- **Project name** — derive from the subject: the resolved directory's basename, or the named scope. Fall back to the cwd basename only when the subject *is* the current directory. This name titles the overview and the figure's H2.

### 2. Scan the codebase (repo is the ground truth)

There are no module docs here, so read the repo's own signals directly. Source-dip is the **norm**, not the exception:

- **Structure** — the top-level package/directory layout under the subject root.
- **Docs** — `README*`, `docs/`, `DESIGN*`, `ARCHITECTURE*`, `CONTRIBUTING*` if present (cheap, high-signal).
- **Entry points** — `main`/`__main__`/`index`/`cmd/`/`bin/`, build manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`).
- **Dependency edges** — coarse import/require graph between top-level components (who calls whom), enough to place arrows in the figure. Don't read every file; sample representative ones per component.
- **External boundaries** — databases, queues, third-party services, network surfaces the code talks to.

Keep this proportionate: the goal is an architecture-level decomposition (a handful of subsystems/components), not a per-file inventory.

### 3. Synthesize the decomposition

From the scan, produce:

- A **short prose overview** — what the system does and how it's split, in a few sentences.
- A **component table** — one row per major component (subsystem/package/service): the component name (link to its directory when useful) and a one-line role.
- The **key boundaries** — process/network/persistence lines, external dependencies.

Group modules into components by responsibility cluster and dependency proximity, the same judgment the full skill applies — just sourced from code instead of module docs.

### 4. Draw the figure — hand-written SVG via `/viz svg`

Author a hand-drawn architecture **SVG via [[viz-svg]]** (NOT Mermaid — per F184 the point is to exercise the viz skill's SVG drafting). Use `/viz diagram` instead when the user wants the [[R-diagram]] rule-checked variant (it's portable — rulesets ship in the repo).

- The figure shows the components from §3 and the major relationships + external boundaries.
- **No title text inside the figure** — the H2 above the embed names it (same rule as the full skill).
- Write the SVG to `Architecture/architecture.svg`; render a `.png` companion when `rsvg-convert` is available (`rsvg-convert -w 1800 Architecture/architecture.svg -o Architecture/architecture.png`); skip the PNG with a note if it isn't installed.

### 5. Write the overview doc

Create a self-contained `Architecture/` folder at the subject root:

```
Architecture/
├── Architecture Overview.md
├── architecture.svg
└── architecture.png        (when rsvg-convert is available)
```

`Architecture Overview.md` shape (top-of-doc → body):

- YAML frontmatter `description:` + an H1 naming the project.
- `## <Project> Architecture` H2, then the figure embed `![[architecture.svg]]` (or a relative `![](architecture.svg)` when the consuming tool isn't Obsidian).
- A prose overview paragraph.
- The **component table** (component → one-line role).
- Optional short H2s — Boundaries, Data Flow, External Dependencies — only when they add signal.

No `## Changes since` section on first authoring. No dispatch table, no bidirectional `Arch` rows — there are no module docs to link to. This is the bridge artifact; if the project later adopts CAB, plain `/architect` takes over.

### 6. Skip every vault-coupled step

This path runs anywhere, so it **omits** the CAB-only and vault-only steps of the full runbook:

- No staleness precondition (no `module_docs_audited:` field to read).
- No reading module docs / no dispatch-table `Arch`-row reconciliation.
- **No Q.md post-condition** and **no `/audit architecture` post-condition** (§8 / §8a) — both are skip-if-absent per F184 and never fire off-vault.
- If a design decision genuinely needs the user and `/query` isn't installed, ask inline in chat.

### 7. Glance + report

- Glance the figure per [[viz-diagram]] § Glance the PNG preview (`open Architecture/architecture.png`, or the SVG when no PNG). On non-macOS, name the output paths instead.
- Report: the path to `Architecture/Architecture Overview.md`, the figure path, and a one-line summary of the components found.

## What this trades away (vs full `/architect`)

- Bidirectional module-doc ↔ architecture linking (no module docs exist).
- Subsystem-as-folder management and the multi-subsystem dispatch indirection.
- Vault dashboard / audit integration.

What it gains: it runs on any codebase, on any machine, with only `viz` + `architect` cloned — producing a real diagrammed overview a reader can use immediately.

## See also

- [[viz-svg]] — the hand-written SVG action this calls for the figure.
- [[viz-diagram]] — the rule-checked SVG variant (portable; rulesets ship in-repo).
- [[architect-new]] — the CAB greenfield draft (assumes vault/anchor); `overview` is its portable, scaffolding-free sibling.
- [[F184 — Skill portability — architect bare-project mode + environment gating|F184]] — design doc.
