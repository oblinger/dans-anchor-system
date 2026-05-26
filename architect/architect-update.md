---
name: architect-update
description: >
  Integrate new architecture ideas into the live `Architecture.md`. Snapshot
  the current live doc to `Versions/{YYYY-MM-DD} Architecture.md`, mutate the
  live doc in place, and append a `## Changes since [[snapshot]]` section
  surfacing the delta. The live doc is canonical the whole time — no separate
  staging area. If no recent `/architect new` draft exists, auto-runs it to
  produce one before integrating. First-time invocation (no live arch yet)
  promotes the greenfield draft to live without snapshotting.
  Use when the user says: "architect", "architect update", "update the
  architecture", "integrate this", "fold the new design into the architecture".
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Architect Update — Integrate New Ideas Live

One of the four `/architect` sub-skills (per [[F084 — Architect redesign]]). **Bare `/architect` routes here** — `/architect update` is the most common action.

`/architect update` is the verb that does an **architecture work session**: take the current live architecture, snapshot it for posterity, then integrate new ideas (from a `/architect new` greenfield draft + any user prompt argument) into the live doc in-place. The user reviews the integrated result on the live doc itself — no separate "proposed" staging area. The `## Changes since` section at the bottom of the live doc surfaces the delta from the snapshot.

## When to use

- Folding a greenfield draft (output of `/architect new`) into the live architecture.
- Incorporating one or more new features into the architecture without doing a full greenfield rewrite.
- Reshaping a subsystem in response to learning ("the streaming subsystem should split into producer/consumer halves").
- Anytime the architecture would benefit from a deliberate integration step rather than ad-hoc inline edits.

If the architecture's `## Changes since` section has drifted out of sync after lots of inline edits, use `/architect changes` to re-derive it without touching the body. If the live arch is out of date relative to code, use `/architect drift` to diagnose.

## Workflow

1. **Detect anchor + architecture path.** Walk up from `cwd` to find `.anchor`. Resolve the architecture folder: `{anchor}/Docs/User/Architecture/`. The live doc is `Architecture.md` within that folder; snapshots live in `Versions/`.

2. **Branch on whether the live arch exists:**

   - **Live `Architecture.md` exists** → standard flow (steps 3–8 below).
   - **No live `Architecture.md`** → first-time invocation flow (§ First-time invocation). Skip ahead.

3. **Snapshot the current live arch.** Copy `Architecture.md` to `Versions/{YYYY-MM-DD} Architecture.md`.
   - Date is today.
   - If the file already exists (same-day re-invocation), append a sequence suffix: `Architecture (b).md`, `Architecture (c).md`, etc. — first invocation today gets the bare name, second gets `(b)`, third gets `(c)`.
   - Mechanical copy — do NOT regenerate or reformat the snapshot. It must be byte-identical to live at the moment of snapshot.

4. **Locate or generate the new-architecture draft.** Walk `Versions/` for files matching `*Architecture (greenfield)*.md`. Define "recent" as **newer than the just-taken snapshot** (i.e., the user ran `/architect new` since the last `/architect update`; presumably they saw it and want it integrated now).

   - **Recent draft found** → use the most-recent matching file as the integration input.
   - **No recent draft** → auto-run `/architect new` to produce one. This generates a fresh greenfield draft in `Versions/` (per the `architect-new.md` workflow); use it as the integration input.

5. **Integrate.** Compose the new live `Architecture.md` by:
   - Taking the **snapshotted-old architecture** as the base (the existing live arch had user buy-in; preserve it).
   - Applying **changes informed by the new draft** (subsystems added/renamed, modules moved, principles updated).
   - Applying **changes informed by any user prompt argument** to `/architect update` (e.g., `/architect update "add a metrics subsystem"` — incorporate that intent).

   **Conservative-changes default:** don't propose changes that aren't motivated by the new input. The existing architecture's structure is presumed-good unless the new draft or the user's prompt argues otherwise. **User can override** with explicit flags in the prompt argument:
   - *"be aggressive"* — accept more from the greenfield draft, including changes to subsystems the draft restructured.
   - *"redo the X subsystem"* — fully replace subsystem X with the greenfield draft's version.
   - *"throw away the state model"* — drop a specific architectural element regardless of the conservative default.

6. **Per-rename behavior** (per F068 amendment + F084 § Per-rename ask-vs-auto-decide rule):
   - **Module renames within a subsystem** are visible + low-recoverability → **auto-decide and announce inline** in the `## Changes since` section. Don't ask.
   - **Subsystem-level renames** are interface-sticky (subsystem names appear in module-doc dispatch tables, cross-references, the dev folder layout) → **ASK**.
   - **Interface-touching renames** (action names that appear in CLI / public API / external integration points) → **ASK**.

7. **Add `## Changes since` section** at the bottom of the new live `Architecture.md`:

   ```markdown
   ## Changes since [[Versions/{YYYY-MM-DD} Architecture]]

   - Added new subsystem "Streaming" with modules `producer`, `consumer`, `bus`
   - Renamed module `LayoutEngine` → `WindowManager` (within `ui` subsystem) — matches existing usage
   - Dropped proposed `EventDispatcher` — existing `bus::Dispatcher` covers
   - Updated `## Principles` — added "single source of truth applies to architectural facts, not just code"
   - ...
   ```

   The link points to the just-taken snapshot. The list shows the delta the update introduced. Group bullets by change kind (Added / Renamed / Dropped / Updated) if there are >5 entries.

8. **Handle diagrams per F084 § Diagram tooling.** The `## Diagram` (or `## Diagrams`) section may contain:
   - **Mermaid blocks** — agent-managed. Regenerate to reflect the new architecture.
   - **User-authored image references** (Excalidraw, image links) — **preserved byte-identical**. Never touch.
   - **When structural changes happened AND a user-authored image exists**, append a small note:
     ```markdown
     ⚠️ The image diagram(s) above may be stale relative to the updated architecture — see the Mermaid block below for the current shape.
     ```
     Don't force a redraw — just flag that one may be wanted.

9. **Glance the live `Architecture.md`** so the user can review the updated architecture and the changes summary:
   ```bash
   open "{anchor}/Docs/User/Architecture/Architecture.md"
   ```

10. **Print a one-line summary.** Format:
    ```
    architect-update: integrated → Architecture.md ({N} additions, {M} renames, {K} drops); snapshot at Versions/{YYYY-MM-DD} Architecture.md
    ```

11. **Discuss live** (interactive follow-up, if the user engages). The user iterates by saying things like:
    - *"drop the Streaming change — too speculative"* → remove from the integration; update `## Changes since` to reflect.
    - *"rename WindowManager back to LayoutEngine"* → revert the rename in the body; update `## Changes since`.
    - *"what about adding a metrics subsystem?"* → integrate the new ask; update `## Changes since`.

    The agent edits `Architecture.md` directly (no separate staging area). No formal "accept" gate — when the user is satisfied, they just stop iterating. The architecture is live the whole time.

## First-time invocation

If no `Architecture.md` exists in `{anchor}/Docs/User/Architecture/` yet:

1. **Skip the snapshot step** — nothing to snapshot.
2. **Locate or auto-run `/architect new`** — same logic as standard step 4. Most likely auto-runs since this is first-time.
3. **Promote the greenfield draft directly to live.** Copy the contents of the greenfield draft into `Architecture.md` (at the anchor's architecture folder root, not under `Versions/`).
4. **No `## Changes since` section** — there's no previous version to diff against. (The next `/architect update` will add one.)
5. **Glance the new live `Architecture.md`.**
6. **Print:** `architect-update: first-time invocation — promoted greenfield draft to Architecture.md ({N} subsystems, {M} modules).`

The greenfield draft remains in `Versions/` as the historical record of the first architecture.

## Same-day multiple updates

Each `/architect update` invocation snapshots the current state, regardless of how many times you've already run it today.

- 1st run today → snapshot at `Versions/{YYYY-MM-DD} Architecture.md`
- 2nd run today → snapshot at `Versions/{YYYY-MM-DD} Architecture (b).md`
- 3rd run today → snapshot at `Versions/{YYYY-MM-DD} Architecture (c).md`
- ...

The `## Changes since` link in the live doc **always points to the most-recent snapshot** (i.e., the one taken at the start of the current update). Previous snapshots remain in `Versions/` for historical reference; the user can compare any two snapshots manually if they want a multi-step delta.

## Failure mode: agent forgets to update `## Changes since` during iteration

When the user iterates ("drop change X", "rename Y back") in step 11, the agent must update **both** the body **and** the `## Changes since` section. If the changes-since section drifts out of sync with what's actually different from the snapshot:

- The user invokes **`/architect changes`** — re-derives the changes-since section from a structural diff between live and the most-recent snapshot. Recovery without re-doing the update.

This is the explicit recovery path for in-line tracking drift. The discipline during update is "update both at once"; `/architect changes` is the safety net when discipline lapses.

## Conservative-changes default — what it means in practice

The greenfield draft proposes a fresh architecture. The live arch reflects the user's accumulated decisions. **Default = preserve live, integrate from greenfield only what's clearly motivated.**

Decision rubric for each element in the greenfield draft:

| Element | Live also has it? | Same shape? | Default action |
|---|---|---|---|
| Subsystem | yes | yes | keep live's version |
| Subsystem | yes | renamed | ASK (subsystem renames are interface-sticky) |
| Subsystem | yes | restructured | keep live's structure unless user prompt argues otherwise |
| Subsystem | no | new | INTEGRATE (the greenfield identified a gap) |
| Module | yes | yes | keep live's version |
| Module | yes | renamed within subsystem | auto-rename + announce |
| Module | yes | moved between subsystems | ASK (structural move) |
| Module | no | new | INTEGRATE if its subsystem exists in live; otherwise this was probably an aspirational addition tied to a new subsystem (see subsystem row above) |
| Principle | yes | same | keep |
| Principle | yes | reworded | keep live wording unless reword is substantive |
| Principle | no | new | INTEGRATE (greenfield observed a new commitment) |
| Action / data | yes | same | keep |
| Action / data | no | new | INTEGRATE if motivated; otherwise note in `## Changes since` as "proposed but not adopted" |

When in doubt, prefer asking via `/ask` to silently dropping or silently adding. The user spent effort on the existing architecture; surprise drops are costly.

## What `/architect update` does NOT do

- **Does not generate the greenfield draft itself.** That's `/architect new`'s job. Update auto-runs new only when no recent draft exists.
- **Does not validate against code.** That's `/architect drift`.
- **Does not regenerate `## Changes since` from a structural diff.** That's `/architect changes`. Update writes changes-since inline based on what it actually integrated.
- **Does not touch user-authored image diagrams.** Mermaid is agent-managed; images are user-managed.
- **Does not modify module docs.** Architecture is rollup-of-rollup; module docs live at `{anchor}/Dev/<module>/<module>.md` and are owned by other skills.

## Relationship to other `/architect` sub-skills

- **`/architect new`** — produces the input draft that `/architect update` integrates. Update auto-runs new when no recent draft exists.
- **`/architect drift`** — diagnostic. Drift findings are typical inputs to update; after running drift, the user often invokes update to bring arch in line with code.
- **`/architect changes`** — recovery. Re-derives the changes-since section from a structural diff when the inline tracking has drifted during long iteration sessions.

## Sources

- [[F084 — Architect redesign]] — parent spec defining the four-sub-skill split.
- [[F074 — Architect skill — Architecture as anchor folder with subsystems]] — the original `/architect` design that F084 supersedes; closest analog to update minus the snapshot/changes-since mechanics.
- [[F068 — Assume-and-announce discipline (Drive mode)|F068]] § amendment — per-rename auto-decide-vs-ask discipline.
