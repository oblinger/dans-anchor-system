# RULESET R-backlog
include::
where:: `file:{anchor}/**/* Backlog.md, !**/DAS *.md`
exclusion-note:: `!**/DAS *.md` exempts the facet-spec catalog (a `DAS <Name>.md` is the SPEC for the facet, not an instance; specs are governed by [[R-facet-spec]]) — added 2026-07-13, T014 follow-on.
description:: what /audit doc checks on a backlog file

What `/audit doc` checks on a backlog file. The skills that maintain it are `/groom` (frontier planning) and the `state` tool (mutations); these are the file-invariants the groomed state must satisfy. Format of this set: [[DAS Ruleset]].

## The groomed states — each carries a body contract that a rule checks

Grooming drives every frontier row into exactly one **groomed state**, and each state is only honest if its body carries the contract below. These are the same canonical states as [[SKA workflow]] § The canonical state graph; the table names, per state, *what the body must contain* and *which `R-backlog` / `R-query` rule mechanically checks it*. A row whose bracket claims a state its body doesn't satisfy is malformed — that is the failure the rules exist to catch.

| # | Groomed state | Bracket(s) | Body contract — what must be present | Checked by |
|---|---|---|---|---|
| 1 | **Executable** | `[Ready]` / `[Active]` | a `- **Next:**` sub-bullet stating the next step the agent takes with zero user involvement | R-backlog-02 |
| 2 | **Questions** | `[Questions]` | at least one numbered `Q<n>` reachable from the row — inline `- **Q<n>` sub-bullets, or a `→ [[Feature Doc]]` link to a `## Open Questions` block; each Q satisfies the five-part question bar (identifier + specific question + labeled `**(A)**` options + Recommendation + a live wiki-link to every named artifact) | R-backlog-05 + R-query-08 / R-query-13 / R-query-15 |
| 3 | **Blocked / Waiting** | `[Blocked]` / `[Waiting …]` / `[Watching …]` | names the *specific* obstacle or awaited/observed event (`[Blocked F<NNN>]` is exempt — the chained link is the description) | R-backlog-06 |
| 4 | **Verify** | `[Verify]` / `[Verify-by …]` | a `- **Verify:**` sub-bullet stating the concrete yes/no the user answers from where they sit | R-backlog-04 |
| 5 | **Watching** | `[Watching …]` | a `- **Verify:**` non-recurrence question (R-backlog-04) **and**, for timed forms, an absolute `YYYY-MM-DD` soak-expiry date in the body | R-backlog-04 + R-backlog-07 |

Timed `[Waiting Nd/Nh]` forms share the state-3 obstacle contract *and* the state-5 absolute-date contract (R-backlog-07). Transient `[Designing]` (still being planned) and terminal `[Done]` are not groomed exit states — a frontier row must not rest in `[Designing]` after a groom. The cross-cutting rule behind states 2–5 is **references get links**: any artifact a row's body tells the user to look at is a live `[[wiki-link]]` (enforced on the queries surface by R-query-15).

### RULE R-backlog-01 — The frontier is Now + Next + the next roadmap milestone (stated)

The **groom frontier** — the tasks that could be next for execution — is the rows under `## Active` / `## Ready` / `## Now` / `## Next`, plus the next unmet milestone of `{slug} Roadmap.md` when the anchor has one. `## Later` and the icebox are not frontier. The rules below hold over the frontier: after a groom, every frontier row is either executable (`[Ready]`/`[Active]` with a declared plan) or honestly parked (`[Questions]`/`[Blocked]`/`[Waiting]`/`[Watching]`/`[Verify]` with the obstacle named).

### RULE R-backlog-02 — Frontier `[Ready]`/`[Active]` rows declare a `Next:` step (checked)
check:: backlog_frontier_planned
mend:: backlog-next-step

Every `[Ready]` or `[Active]` row under a frontier H2 carries a `- **Next:**` sub-bullet declaring the next concrete step the agent will take with zero user involvement. A `[Ready]` row that cannot state a no-user next step is not really Ready — the bracket is lying (this is the render's `⚠ none declared` forcing-function, promoted to a rule).

**Check pattern:** for each top-level row under `## Active` / `## Ready` / `## Now` / `## Next` whose bracket is `[Ready]` or `[Active]`, the row's indented sub-bullets include one starting `- **Next:**`.

### RULE R-backlog-03 — Frontier rows are bracket-resolved (checked)
check:: backlog_frontier_bracketed
mend:: backlog-groom-the-row

A top-level row under `## Now` / `## Next` with no status bracket (or the bare placeholder `[ ]`) is **ungroomed frontier** — the task might be next, but nobody has planned it, questioned it, or named its blocker. Groom owes it a pass. (`## Later` rows may sit unbracketed; they are not frontier.)

**Check pattern:** every top-level `- **…**` row under `## Now` / `## Next` carries a `[...]` bracket other than `[ ]`.

### RULE R-backlog-04 — `[Verify*]` / `[Watching*]` rows carry a concrete question (checked)
check:: backlog_verify_concrete
mend:: backlog-verify-question

Every `[Verify]` / `[Verify-by …]` / `[Watching …]` row carries a `- **Verify:**` sub-bullet stating the concrete yes/no the user can answer from where they sit (do X, observe Y — did Y happen?). The mechanical queries render quotes it verbatim; a Verify row without one renders as an unanswerable ⚠.

**Check pattern:** for each row whose bracket starts `Verify` or `Watching`, the row's indented sub-bullets include one starting `- **Verify:**`.

### RULE R-backlog-05 — `[Questions]` rows keep the bracket promise — a numbered `Q<n>` is reachable (checked)
check:: backlog_questions_have_numbered_q
mend:: backlog-question-promise

`[Questions]` is a **structural promise**: following the row lands the user on a numbered `Q<n>` they can answer in chat (`<id> Q<n>: <answer>`). The state-2 body contract is satisfied one of two ways — inline `- **Q<n>` sub-bullets at the top of the row body (B-rows / task-rows with no doc, per § B-row inline Qs), **or** a `→ [[Feature Doc]]` link delegating the Qs to that doc's `## Open Questions` (per § The `→ [[X]]` link convention). A `[Questions]` row with neither is malformed — the user clicks and lands on prose with nothing to answer (the [[feedback_close_round_trip_loopholes]] failure). Fix by hoisting the informal questions to numbered form or adding the `→ [[Doc]]` link — or rebracket to a state the row actually satisfies.

**Check pattern:** for each row whose bracket is `Questions` (or `N Questions`), either an indented sub-bullet starts `- **Q<n>` or the row/sub-bullets contain a `→ [[…]]` link.

### RULE R-backlog-06 — `[Blocked]` / `[Waiting …]` / `[Watching …]` rows name their obstacle (checked)
check:: backlog_blocker_named
mend:: backlog-name-the-obstacle

The state-3 body contract, and the antidote to the lazy-Blocked / lazy-Waiting / lazy-Watching failure mode ([[SKA workflow]] § The lazy-Blocked … failure mode): a bracket claiming one of these states is a claim about *why the row is not actionable right now*, and the body must make that claim auditable in one read — the specific blocker (Blocked), the awaited event we *want* (Waiting), or the shipped change + what non-recurrence proves (Watching). A bare bracket with no explanatory body (or sub-bullet) is a thought-terminating label, not a groomed state. **`[Blocked F<NNN>]` is exempt** — the chained F-number link *is* the description.

**Check pattern:** for each row whose bracket head is `Blocked` / `Waiting` / `Watching` and is not the chained `Blocked F<NNN>` form, the row carries descriptive body text after the bracket (or at least one sub-bullet). An empty or near-empty body with no sub-bullet fails.

### RULE R-backlog-07 — Timed `[Waiting Nd/Nh]` / `[Watching Nd/Nh]` rows carry an absolute expiry date (checked)
check:: backlog_timed_has_expiry_date
mend:: backlog-absolute-expiry

The relative duration in a timed bracket (`1d`, `4h`, `7d`) **ages** — "1d" is meaningless without knowing when it was written. So the state-5 (and timed state-3) contract requires the body to give the absolute calendar date the wait/soak expires, in `YYYY-MM-DD` form. The terse `Nd`/`Nh` stays in the bracket for glanceability; the date lives in the body, and `/groom` reads it to decide when to prompt for rebracketing.

**Check pattern:** for each row whose bracket matches `(Waiting|Watching) \d+[dh]`, the row line or a sub-bullet contains a `\d{4}-\d{2}-\d{2}` date.

## Mend

Remediation messages for these rules — what to actually do when one fires. Reached as `warden mend R-backlog-<nn>`; wired by the `mend::` line on each rule. Every fix below goes through `state`, never a hand-edit: the backlog carries an integrity stamp and a hand-edit is detected on the next write.

### MEND backlog-next-step

Give the row a next step through `state`, or drop the bracket that promised one.

```sh
state set <anchor> Backlog <id> --next "<the concrete step, no user involved>"
```

The step must be something the agent can start now with zero user involvement. If you cannot write one, the bracket is the thing that is wrong — the row is not Ready. Rebracket it to the state it actually satisfies: `[Questions]` if a decision is missing, `[Blocked <handle>]` if something else must land first, `[User]` if the next move is genuinely the user's, `[ ]` under `## Later` if it is simply not scheduled.

Watch for the lazy-delegation shape: "ask the user whether X" is not a next step, it is a question. File it as one.

For the model, read [[DAS Backlog]] § Definition of Ready.

### MEND backlog-groom-the-row

Decide what this row's state actually is and set it through `state`.

A row under `## Now` or `## Next` with no bracket (or the bare `[ ]`) is on the frontier with nobody having planned it. Four honest outcomes, in rough order of how often they are right:

- It is executable → `--status Ready --next "<step>"`.
- A decision is missing → file the question and `--status Questions`.
- Something must land first → `--status Blocked` naming the handle, or `--status Waiting` naming the event.
- It is not really imminent → `--horizon Later`, where an unbracketed row is legitimate.

Demoting to `## Later` is a real answer, but apply the boredom test first: are you moving it because there is a reason it should wait, or because you are tired of looking at it?

For the model, read [[DAS Backlog]] § The groom frontier.

### MEND backlog-verify-question

Add the concrete yes/no the user can answer from where they sit.

```sh
state set <anchor> Backlog <id> --verify "<do X, observe Y — did Y happen?>"
```

The render quotes this verbatim, so it has to stand alone: name the observation, not the feature. "Have you sent a Voice Memo since 2026-05-28 and seen the transcript land in `~/ob/kmr/Log/VOX/`?" is answerable; "verify F093" is not.

Before writing it, apply the positioning test: would the user's answer actually be better than yours? If the check lives in a file, a log, or a probe, run it now and set the row `[Done]` — a verification that surfaces to the user is one that needs a human faculty (taste, ratification, passive-use observation).

For the model, read [[DAS verification]].

### MEND backlog-question-promise

Make the bracket's promise true, or change the bracket.

`[Questions]` promises that following the row lands the user on a numbered `Q<n>` they can answer in chat. Two ways to keep it:

- The row owns its questions — add inline `- **Q<n> — …**` sub-bullets at the top of the row body. Right for task-rows with no feature doc. Answer one with `state resolve <anchor> Backlog <row>.Q<n> --choice "(B)"`, which archives it in the row's own `- **Resolved**` zone and recounts the bracket (T086).
- A feature doc owns them — add a `→ [[F<n> — Title]]` link and put the questions in that doc's `## Open Questions` via `state define <anchor> "<doc>" Q+`.

If the row has neither and no question is actually pending, the bracket is stale — rebracket it. Landing a user on prose with nothing to answer is the round-trip loophole this rule exists to close.

Only the **pending prefix** counts toward the promise. An answered question stays in the row below the `- **Resolved**` zone head, keeping its `**Q<n> —` header, so a row whose every question has landed cannot go on honouring `[Questions]` on the strength of its own history.

For the model, read [[DAS Backlog]] § B-row inline Qs and [[DAS ask-format]].

### MEND backlog-name-the-obstacle

Say in the body what is actually in the way.

- `[Blocked]` — name the specific obstacle, and prefer the chained `[Blocked F<NNN>]` form when the blocker is another row, since the link *is* the description and is exempt from this rule.
- `[Waiting]` — name the event you want to occur. Waiting has no actor whose action would unblock it; if one exists, the row is Blocked, not Waiting.
- `[Watching]` — name the change you shipped and what non-recurrence would prove.

A bare bracket with no body is a thought-terminating label. Before writing one, ask whether you could unblock it yourself — most rows that reach for `[Blocked]` are rows nobody tried.

For the model, read [[SKA workflow]] § Blocked, Waiting, and Watching semantics.

### MEND backlog-absolute-expiry

Put the calendar date in the body, in `YYYY-MM-DD` form.

The `Nd`/`Nh` in the bracket stays — it is what makes the row glanceable — but it ages the moment it is written, and nothing records when that was. `/groom` reads the absolute date to decide when to prompt for rebracketing, so without it the row waits forever.

Write the date the wait or soak expires, not the date you wrote the row.

For the model, read [[DAS Backlog]] § Status brackets.
