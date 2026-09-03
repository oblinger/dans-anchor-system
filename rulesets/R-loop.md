# RULESET R-loop
include::
import:: skills/workflow/scripts/loop_checks.py
where:: `file:{anchor}/**/* Pebbles/**, {anchor}/**/* Rocks/**, {anchor}/**/* Book/**, !**/DAS *.md`
description:: What makes a stone a loop, what a workflow may say, and what `loop` refuses — the key set, the closed `when`/probe/branch vocabularies, and the script-owned watch list.

Ruleset for the Loop facet — spec: [[DAS Loop]]. Every rule below is enforced by `skills/workflow/scripts/loop` at `start` and `advance` (refusal, nothing written) and reported by `loop check` / `loop due`; the guard is `test-f635-loop.py`, one fixture per refusal. Three carry a `check::` — `-01`, `-02`, `-06` are facts about a stone FILE, so `audit-plan` can judge them through `import:: skills/workflow/scripts/loop_checks.py`, which re-exports the script's own `check_stone` partitioned by rule (one resolver, never a second parser). The rest assert what the script refuses of a WORKFLOW or of the watch list — the shape [[R-stone]]-05 and [[R-exception-discipline]]-03 use — and read `(stated)` with the guard as their evidence.

### RULE R-loop-01 — A loop carries all four loop keys (checked)
check:: loop_keys_complete

A stone with `workflow::` also carries `step::`, `entered::` (a date) and `lapses::`. Half a loop — a workflow with no step, a step with no entry date — is refused at `start`/`advance` and reported by `check`. Guard: `test-f635-loop.py` § B.

### RULE R-loop-02 — `step::` names a step of a workflow that resolves (checked)
check:: loop_step_resolves

`workflow::` (or the `workflow::` on `channel::`'s page) resolves to exactly one file carrying a `## Workflow` section, and `step::` is a row of its table. An unresolvable link, an ambiguous one, a page with no section, or a step the table does not name is a refusal. Guard: § B, § G.

### RULE R-loop-03 — Every step has a `when` and a `probe`; `when` is in the vocabulary, hour floor (stated)
A row missing either cell is refused naming the step. `when` is one of: absolute date / date-hour, `daybreak`, `HH:00`, `+Nd`, `<key>±Nd`. Minutes other than `:00` are refused as finer than the hourly watch. Guard: § A (no probe), § B (`22:30`).

### RULE R-loop-04 — Probes are the four kinds, and `miss → dan` needs a falsifiable one (stated)
`mail:`, `key:`, `portal:` (with a `[[link]]`), `owner:` — nothing else. A step whose miss branch is `dan` carries at least one `key:` or `portal:` probe, because `mail:` alone can only return hit or unknown and an unknown may never reach Dan as a miss. A miss branch to a *step* on a `mail:`/`owner:`-only step is legal but unreachable; `loop lint` warns rather than refuses. `key:` miss is precise: the key absent, or present and empty. A `portal:` check is read-only — navigate and read, never submit. Guard: § B, § K.

### RULE R-loop-05 — Branch targets are a step name, `close`, `owner`, or `dan` (stated)
`hit` → a step or `close`; `miss` → a step, `owner` or `dan`. There is no cell for a channel, a rung or a command, and no target outside this set — that absence is the whole of the grammar's containment. Guard: § F (`--to dan`, `--to nowhere`).

### RULE R-loop-06 — Every `requires::` binding, and every key a `when` reads, is on the stone (checked)
check:: loop_bindings_present

A binding the workflow requires and the stone lacks, or a `when` that reads a key the stone does not carry, is refused at `start`/`advance` — `accepts:` one level down. Guard: § B.

### RULE R-loop-07 — The watch list is script-owned (stated)
Every line on [[TRAFFIC]]'s control file is a stone enrolled there by `loop start` (through `stone share`) and carrying `workflow::`. A hand-written line, a stone on the list without `enrolled:: TRAFFIC`, or an enrolled stone with no workflow is reported by `loop due` / `loop scan` as a WARN naming the line. Guard: § H. At the moment of writing, [[R-pathguard]]-06/-07 deny an agent's Edit/Write to that file outright (mend `loop-owns-the-watch-list`).

### RULE R-loop-08 — The workflow a stone runs on resolves inside the owner's anchor, or to the stone itself (checked)
check:: loop_workflow_contained

`workflow::` — direct, or supplied through `channel::` — must resolve to a page under the owning anchor's folder (`{owner anchor}/**`) or to the stone's own file. A workflow pulled from anywhere else writable in the vault is the injection path Dan named on [[DAS Loop]] § Security; refusing it at `start`/`advance` costs one path test and closes most of it today. Proposed by Atticus in the F635 review, 2026-09-02. The enclave ([[Atticus P0018]]) will later say *which* folders under the owner count — this rule is the placeholder that makes that narrowing a tightening rather than a new gate. Guard: § B.
