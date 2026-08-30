# RULESET R-backlog
include::
import:: skills/audit/scripts/audit-plan.py
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
| 3 | **User-action** | `[User]` | a `- **User:**` sub-bullet naming the genuinely user-only action the row waits on — a login only the user holds, a GUI permission dialog, a 2FA tap — with a live wiki-link to anything it says to open | R-backlog-08 |
| 4 | **Blocked / Waiting** | `[Blocked]` / `[Waiting …]` / `[Watching …]` | names the *specific* obstacle or awaited/observed event (`[Blocked F<NNN>]` is exempt — the chained link is the description) | R-backlog-06 |
| 5 | **Verify** | `[Verify]` / `[Verify-by …]` | a `- **Verify:**` sub-bullet stating the concrete yes/no the user answers from where they sit | R-backlog-04 |
| 6 | **Watching** | `[Watching …]` | **either** a `- **Verify:**` non-recurrence question **or** a `- **Probe:**` naming the agent-owned deferred check and its trigger (R-backlog-04) — **and**, for timed forms, an absolute `YYYY-MM-DD` soak-expiry date in the body | R-backlog-04 + R-backlog-07 |

Timed `[Waiting Nd/Nh]` forms share the state-4 obstacle contract *and* the state-6 absolute-date contract (R-backlog-07). Transient `[Designing]` (still being planned) and terminal `[Done]` are not groomed exit states — a frontier row must not rest in `[Designing]` after a groom. The cross-cutting rule behind states 2–6 is **references get links**: any artifact a row's body tells the user to look at is a live `[[wiki-link]]` (enforced on the queries surface by R-query-15).

**State 3 was missing from this table until 2026-08-20, and its absence is the reason it is worth a sentence.** [[SKA groom]] has listed six groomed states since F259 shipped `[User]`; this table listed five, so the one bracket whose entire meaning is *a person must act* was the only groomed state with no stated body contract and no rule — while `audit-q` C51 checked it all along. A contract enforced by a sweep and absent from the ruleset is the [[Tink Backlog#^T552|T552]] parity failure in its purest form: one uncheckable copy that has drifted, and nothing to notice.

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

Every `[Verify]` / `[Verify-by …]` row carries a `- **Verify:**` sub-bullet stating the concrete yes/no the user can answer from where they sit (do X, observe Y — did Y happen?). The mechanical queries render quotes it verbatim; a Verify row without one renders as an unanswerable ⚠. **This half is not relaxed by anything below**: `[Verify*]` is the user-owned family, and letting it satisfy the rule with an agent-side field would be a way to park a user check where the user never sees it.

A `[Watching …]` row carries **either** that `- **Verify:**` question **or** a `- **Probe:**` — the F305 agent-owned deferred check, naming its trigger and what to run when it fires. The two are different owners of the same shape, and a Watching row may legitimately be either; T237 relaxed the three code sites (the `define` refusal, F240's ownership gate, audit-q C41) and this is the statement they implement.

**Check pattern:** for each row whose bracket starts `Verify`, the row's indented sub-bullets include one starting `- **Verify:**`; for each row whose bracket starts `Watching`, they include one starting `- **Verify:**` or one starting `- **Probe:**`.

### RULE R-backlog-05 — `[Questions]` rows keep the bracket promise — a numbered `Q<n>` is reachable (checked)
check:: backlog_questions_have_numbered_q
mend:: backlog-question-promise

`[Questions]` is a **structural promise**: following the row lands the user on a numbered `Q<n>` they can answer in chat (`<id> Q<n>: <answer>`). The state-2 body contract is satisfied one of two ways — inline `- **Q<n>` sub-bullets at the top of the row body (B-rows / task-rows with no doc, per § B-row inline Qs), **or** a `→ [[Feature Doc]]` link delegating the Qs to that doc's `## Open Questions` (per § The `→ [[X]]` link convention). A `[Questions]` row with neither is malformed — the user clicks and lands on prose with nothing to answer. Fix by hoisting the informal questions to numbered form or adding the `→ [[Doc]]` link — or rebracket to a state the row actually satisfies.

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

### RULE R-backlog-08 — `[User]` rows name the user-only action (checked)
check:: backlog_user_action_named
mend:: backlog-name-the-user-action

The state-3 body contract. `[User]` is the bracket that says *the agent has stopped and a person must act*, so the body must name **which** act: the login only the user holds, the GUI permission dialog, the 2FA tap, the physical thing only they can do. A bare `[User]` bracket is addressed to someone and does not tell them what for — strictly worse than the lazy-`[Blocked]` of R-backlog-06, which at least does not claim to be asking anyone.

**The rule has two clauses, and mirroring only the audit would have left half the contract unstated.** `audit-q` C51 asks whether an action is *named*. The F259 mint gate asks more: it refuses a `[User]` entry without `--why-user-action`, which persists on the row as a `· *why-user-action: …*` trailer. So the rule checks both — the action, and the credential or human-only faculty it needs. Naming the action says *what to do*; the justification says *why it cannot be the agent doing it*, and that second claim is the one that decides whether the row belongs in a person's queue at all. A row can name a perfectly concrete action that the agent was simply too incurious to attempt, and only the second clause catches it.

**Three enforcement points, none redundant.** The gate stops the bracket being *created* without either; this rule catches rows that never went through the gate — everything predating it, and everything hand-edited since; C51 sweeps the vault for the first clause. What this rule adds beyond both is that the contract is now *stated where the rules live* rather than existing only as behaviour inside two scripts.

**Deliberately no doc-side escape.** R-backlog-02 exempts a derived row whose arrow-linked doc carries a `next::` field, and the symmetry invites a matching `user::` exemption here. There is no such field: F332 moved exactly one thing into the doc, and `backlog-edit` reads back only `next::` — `- **User:**`, `- **Verify:**` and `- **Probe:**` all stay on the row. An exemption keyed on a field nothing writes would exempt every row in the vault — a guard that passes without ever protecting anything, and reads as coverage while providing none.

**Measured at arming, 2026-08-20: 41 backlogs, 29 live `[User]` rows across six anchors (TINK 10, ATT 7, SONAR 5, TAP 4, MUX 2, SVP 1) — 29 of 29 named their action, and 29 of 29 carried the `why-user-action` trailer. Zero findings on both clauses.** The counts are here because a zero is a claim about the instrument as much as about the corpus, and this rule was armed on an already-clean one: the F259 gate has held since it shipped, and both clauses were measured separately rather than inferred from a single pass. If a later run reports zero after the row population changes, this is the figure to check it against before believing the clean.

**Check pattern:** for each row whose bracket is `User` (or `N User`), the row's indented sub-bullets include one starting `- **User:**`, and that sub-bullet's text contains a `· *why-user-action:` annotation.

### RULE R-backlog-09 — A surfaced `- **Verify:**` is user-grade and names the faculty (checked)
check:: backlog_verify_is_user_grade
mend:: backlog-earn-the-surfacing

R-backlog-04 requires a `[Verify*]` / `[Watching*]` row to *carry* a question. This rule asks whether that question had any business reaching a person. It is the standing form of F240's who-is-better-positioned test — *would the user's answer actually be better than the agent's?* — and it mirrors both of the refusals the `state` mint gate already makes:

- **The question must not read as a machine event.** "Did the hook fire", "does the file exist", a bare command to run — those are agent-grade. If the answer lives in a file, a log, or a probe, the agent runs the check *now*: the row goes `[Done]` with the evidence, or `[Waiting]` naming the wake event and the agent-check plan. It never reaches the user's queue. **This half is refused regardless of the justification**, exactly as the gate refuses it — a `why-user` sentence pinned to a machine question does not make the question the user's, it just makes the misfiling articulate.
- **It must carry the `· *why-user: …*` annotation** naming the human faculty in play — taste, preference, ratification, passive-use observation. A row without one asserts the user is better positioned and never says why, and that claim is the whole basis on which their attention is being spent. It is also the half nothing else was checking: `audit-q` C47 sweeps the phrasing, so before this rule the missing-faculty refusal existed only inside `state` and vanished the moment a row was written any other way.

**The phrasing test is borrowed, never re-implemented.** The checker calls `backlog-edit.is_mechanical_verify` — the same function the mint gate and C47 call — through the module-borrow `R-backlog-02` already uses for `next::`. A second copy of a heuristic is a second thing to drift, and it would drift silently in the worst direction: a checker that had quietly stopped agreeing with the writer would nag rows `state` itself accepts, which is the read-the-warning-and-ignore-it training the audit discipline exists to prevent.

A `[Watching]` row carrying only a `- **Probe:**` is untouched. R-backlog-04 lets that row be agent-owned, and this rule governs what reaches the user — a row that surfaces nothing to them has nothing to justify.

**Measured at arming, 2026-08-20: 56 `- **Verify:**` questions across 41 backlogs — 48 clean, 0 machine-phrased, 8 with no `why-user`.** The zero is the load-bearing number: the F240 gate has held on phrasing everywhere it ran. The eight are all genuine user questions written before the annotation was required (ASH 5, FX5 / FX6 / FX7 1 each — *"any freeze recurrence since the fix? yes/no"* is typical), and they are named here rather than smoothed over, because each surfaces in its own anchor's audit where its owner can annotate or retire it. None is in [[Tink]]; the rule was not armed against a corpus its author had pre-cleaned.

**Check pattern:** for each row whose bracket starts `Verify` or `Watching` and whose sub-bullets include one starting `- **Verify:**`, the text after that marker fails `backlog-edit.is_mechanical_verify` **and** contains a `· *why-user:` annotation. Rows with no `- **Verify:**` sub-bullet are out of scope here — R-backlog-04 governs their presence.

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

### MEND backlog-name-the-user-action

Say what the person is supposed to do.

```sh
state set <anchor> Backlog <id> --user "<the action only the user can take>" --why-user-action "<the credential or faculty it needs>"
```

The render quotes the action verbatim and the row surfaces in the Questions bucket, so it has to stand alone the way a Verify question does: *"Mint a fresh API key at https://console.anthropic.com/settings/keys and write it into `~/.config/anthropic/api_key`, then say 'key is in'"* is actionable; *"needs Dan"* is not. Link every artifact it tells the user to open.

Before writing it, apply the positioning test in the other direction from R-backlog-04's: not *would their answer be better than mine*, but **is this genuinely theirs to do at all?** `[User]` is for what the agent cannot do — a credential it does not hold, a dialog it cannot click, a physical act. Work the agent simply has not started is `[Ready]` with a `- **Next:**`, and mislabelling it `[User]` parks the agent's own task in the user's queue, where it waits on someone who is waiting on you.

For the model, read [[DAS Backlog]] § The groomed states.

### MEND backlog-earn-the-surfacing

Two different fixes, and which one you need depends on which half fired.

**"reads as a machine event"** — the check is yours. Run it now.

```sh
state set <anchor> Backlog <id> --status Done          # it passed; put the evidence in the body
state set <anchor> Backlog <id> --status Waiting --next "<the agent-check to run when <event> lands>"
```

Nothing you can add to the question will make it the user's. The gate refuses this shape whatever justification accompanies it, on purpose: the tell that a check belongs to the agent is that its answer lives in a file, a log, or a probe, and none of those become human-readable by being asked about politely.

**"names no human faculty"** — say what you need from them.

```sh
state set <anchor> Backlog <id> --verify "<do X, observe Y — did Y happen?>" --why-user "<the faculty>"
```

The faculty is one of four: **taste** (does this read right), **preference** (which do you want), **ratification** (do you accept this call), **passive-use observation** (in normal use, did it break). If you cannot name one, that is the answer — you are in the first case, not this one.

For the model, read [[DAS verification]] and [[Tink Backlog#^F240|F240]].
