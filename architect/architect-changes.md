---
name: architect-changes
description: >
  Re-derive the `## Changes since [[snapshot]]` section at the bottom of the
  live `Architecture.md` from a structural diff between live and the
  most-recent snapshot. **Never mutates the architecture body** — only the
  changes-since section. Recovery tool for when in-line tracking has drifted
  out of sync after long iteration on the live doc. Cheap, idempotent, safe
  to invoke anytime. Use when the user says: "architect changes",
  "regenerate changes since", "fix the changes-since section",
  "the changelog is stale".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Architect Changes — Re-derive `## Changes since` Section

One of the four `/architect` sub-skills (per [[F084 — Architect redesign]]). Small follow-on to `/architect update` — shares the **arch-doc parser** and **semantic-diff engine** with update.

`/architect changes` is a **recovery tool**. When the live `Architecture.md` has been iteratively edited (manually, by `/architect update` runs, by agent edits in conversation) and the inline `## Changes since` section has drifted out of sync with what's actually different from the most-recent snapshot, this skill re-derives that section from a structural diff. The architecture body itself is **never modified** — only the trailing changes-since section.

## When to use

- After a long iteration session on the live `Architecture.md` where the agent or user made edits without updating `## Changes since`.
- When the changes-since section feels stale, incomplete, or doesn't match what the user remembers changing.
- As a sanity check before sharing the architecture — "what actually changed since the last snapshot?"
- After multiple `/architect update` invocations where intermediate edits weren't tracked.

If there's no snapshot yet (first-ever invocation, only one architecture version exists), nothing to diff — report and stop.

## Workflow

1. **Detect anchor + architecture path.** Walk up from `cwd` to find `.anchor`. Resolve `{anchor}/Docs/User/Architecture/`. Live = `Architecture.md`; snapshots in `Versions/`.

2. **Locate the most-recent snapshot.** Walk `Versions/` for files matching `*Architecture*.md` (excluding `*greenfield*` — those are `/architect new` drafts, not snapshots). Sort by filename (date-prefixed) descending; pick the most recent.
   - **No snapshots found** → report `architect-changes: no snapshots in Versions/ — nothing to diff against (run /architect update at least once to take the first snapshot)` and stop.
   - **Multiple snapshots from today with sequence suffixes** (`Architecture.md`, `Architecture (b).md`, `Architecture (c).md`) → pick the most-recent (highest suffix; bare name is treated as the earliest).

3. **Parse both** via the shared **architecture-doc parser** (also used by `/architect update`). Extract structured representations of:
   - Subsystems (name, purpose, modules list)
   - Modules (name, owning subsystem, purpose)
   - Actions / operations (name, owning module, trigger + effect)
   - Data structures (name, owning subsystem, description)
   - Principles (text content)
   - Diagrams (Mermaid blocks separately from user-authored image references)

   See § Arch-doc parser shape for what the structured representation looks like.

4. **Diff semantically** via the **semantic-diff engine** (shared with `/architect update`). NOT raw textual diff — too noisy; small whitespace or wording changes shouldn't surface as architectural changes. Produce a list of architectural-element-level changes:

   - **Added** — element exists in live but not snapshot.
   - **Removed** — element exists in snapshot but not live.
   - **Renamed** — element with same role but different name (use fuzzy matching on description text + structural role).
   - **Moved** — module changed owning subsystem; subsystem element changed owning area.
   - **Updated** — element exists in both with same name but body changed substantively (paragraph rewrites, principle reworded, action trigger changed).

5. **Render the bullets** in a human-readable form, grouped by change kind when count exceeds ~5:

   ```markdown
   ## Changes since [[Versions/{YYYY-MM-DD} Architecture]]

   **Added**
   - Subsystem "Streaming" with modules `producer`, `consumer`, `bus`
   - Module `metrics-collector` in subsystem `observability`
   - Principle: "single source of truth applies to architectural facts, not just code"

   **Renamed**
   - Module `LayoutEngine` → `WindowManager` (within `ui` subsystem)

   **Removed**
   - Module `EventDispatcher` from subsystem `events` — superseded by `bus::Dispatcher`

   **Updated**
   - Principle "no fallback logic" — reworded for clarity
   - Action `compile-rules` (in `audit-markdown` module) — trigger expanded to include `/audit markdown --force-compile`
   ```

   When there are ≤5 total changes, drop the headers and just bullet-list.

6. **Locate the existing `## Changes since` section** at the bottom of `Architecture.md`. There are three cases:

   - **Section exists** — replace it (header + body) with the regenerated version.
   - **No section exists** (architecture was just promoted from greenfield, or section was deleted) — append the regenerated section at the end of `Architecture.md`.
   - **Section exists with a different snapshot link** (e.g., points to an older snapshot than the most-recent) — replace it; the new section links to the most-recent snapshot per step 2.

   The link target in the H2 always points to the most-recent snapshot per § Locate the most-recent snapshot.

7. **Write the updated `Architecture.md`** — body unchanged, only the trailing `## Changes since` section replaced.

8. **Glance the live `Architecture.md`** so the user can review the regenerated delta:
   ```bash
   open "{anchor}/Docs/User/Architecture/Architecture.md"
   ```

9. **Print a one-line summary.** Format:
    ```
    architect-changes: regenerated → {N} changes vs [[Versions/{YYYY-MM-DD} Architecture]] ({A} added, {R} renamed, {D} removed, {U} updated)
    ```

## Arch-doc parser shape

The parser is **shared with `/architect update`** — same parser, same output structure. Spec for the structured representation:

```
ArchDoc {
  principles: [Principle]
  diagrams: {
    mermaid: [MermaidBlock]    # agent-managed
    images: [ImageRef]          # user-managed; never touched
  }
  subsystems: [Subsystem]
  data_structures: [DataStructure]
  actions: [Action]
}

Subsystem {
  name: str
  purpose: str             # one-paragraph description
  modules: [Module]
}

Module {
  name: str
  owning_subsystem: str    # back-reference for diff
  purpose: str             # one-line
}

Action {
  name: str
  owning_module: str
  trigger: str
  effect: str
}

DataStructure {
  name: str
  owning_subsystem: str
  description: str
}

Principle {
  text: str
}
```

Parser implementation deferred to first compilation step (Python script or in-agent parsing — v1 spec-level allows either; see § What's deferred).

## Semantic-diff engine

For each element kind (subsystem / module / action / data / principle / diagram), the diff engine:

1. **Match by name first.** Same name in both → candidate for "Updated".
2. **For unmatched elements, attempt fuzzy match on description text + structural role.** A subsystem named `LayoutEngine` in snapshot and `WindowManager` in live, both with the same modules-list and same purpose-paragraph → likely a "Renamed", not an Added + Removed pair.
3. **Categorize matched pairs:**
   - Same name + same body → no change.
   - Same name + body changed substantively → Updated. Substantive = paragraph rewrites, principle reworded, action trigger changed. Whitespace, capitalization, or single-word edits = no change.
   - Same name + different owning subsystem (module case) → Moved.
4. **Unmatched in live** → Added.
5. **Unmatched in snapshot** → Removed.

**Substantive-vs-trivial threshold.** Default heuristic: if word-overlap ratio between the two versions is >85%, treat as no change. Tune as the skill is used.

## What `/architect changes` does NOT do

- **Does not modify the architecture body.** Only the trailing `## Changes since` section. The body is read-only input.
- **Does not snapshot.** That's `/architect update`'s job. Snapshots are taken on update; changes is a recovery tool that operates on existing snapshots.
- **Does not validate against code.** That's `/architect drift`.
- **Does not propose architectural changes.** It reports what's already different, not what should change.
- **Does not delete snapshots.** All snapshots in `Versions/` are preserved as historical record.

## Idempotence

Running `/architect changes` twice in a row produces identical output — the second run finds the same diff and writes the same section. Safe to invoke anytime; cheap (no LLM call for the structural extraction; semantic-diff can be either rule-based or LLM-assisted).

## What's deferred (v1)

This is the **spec-level v1**. The arch-doc parser and semantic-diff engine are described above as functional behavior; the **compiled implementation** (Python script or formal in-agent procedure) is a follow-on:

- **Compiled arch-doc parser** — for v1, the agent reads both arch files and extracts the structured representation by reading. A future compiled parser (Python, regex + light parsing) would speed this up and make it deterministic.
- **Compiled semantic-diff engine** — similar story. v1 agent does the matching by reading. v2 compiled engine pre-computes matches for the agent to render.
- **Configurable substantive-vs-trivial threshold** — v1 uses the 85% word-overlap default. v2 may expose this via F080 config.

These follow-ons share machinery with `/architect update`'s integration step; build them together rather than separately.

## Relationship to other `/architect` sub-skills

- **`/architect update`** — primary partner. Update writes `## Changes since` inline as it integrates; changes re-derives it when that inline tracking has drifted. Same parser, same diff engine.
- **`/architect new`** — unrelated. Greenfield drafts have no snapshot to diff against; they're standalone.
- **`/architect drift`** — orthogonal. Drift compares arch to code; changes compares arch to a prior snapshot of itself.

## Sources

- [[F084 — Architect redesign]] — parent spec defining the four-sub-skill split.
- [[F068 — Assume-and-announce discipline (Drive mode)|F068]] — assume-and-announce discipline (informs substantive-vs-trivial threshold).
