---
description: "CLI reference for the `state` script — canonical state editor for everything below the anchor level, on one address scheme: `state <doc> <label> <verb>` for backlog rows, doc questions, and doc verifications. F129 (shipped 2026-06-07), unified by F236 (2026-07-13)."
---

# state — canonical state editor (CLI reference)
Man-page-style reference for the `state` CLI — the one write path for backlog rows, doc Open Questions, and doc Verifications.

> **STATUS:** Canonical. Shipped 2026-06-07 via F129; unified on the one-address-scheme v2 grammar 2026-07-13 via F236. Legacy `backlog-edit.py` ships alongside at the helper level — `state` delegates to it via importlib; new code always invokes `state`.

## NAME

`state` — canonical state editor for backlog rows, doc Open Questions, and doc Verifications

## SYNOPSIS

```
state [-a ANCHOR] <doc> <label> <verb> [flags] [< body]

state [-a ANCHOR] status  <set|show> ...       # {slug} Status.md facet cells (F130)
state [-a ANCHOR] roadmap <status|migrate> ... # {slug} Roadmap.md milestone state (F145)
```

- **`<doc>`** — the addressed document: the literal **`Backlog`** (the anchor's backlog file), a **wiki-name** (case-insensitive `.md` basename match — anchor tree first, then vault root; zero matches errors, multiple matches errors listing every candidate), or a **path**. Any markdown doc qualifies — feature docs, PRDs, standalone design docs.
- **`<label>`** — LETTERS+DIGITS, the item's primary key within the doc: `F157` / `T8` on the Backlog, `Q7` / `V3` on any other doc. The mint form LETTERS+`+` (`F+`, `T+`, `Q+`, `V+`) assigns the next unused number — valid only with `define`; the assigned label is printed in the output.
- **`<verb>`** — `define` | `set` | `resolve` | `remove` (per-target semantics below).

## ANCHOR RESOLUTION

`-a ANCHOR` (long form: `--anchor`) is OPTIONAL on every invocation. Resolved in this order:

1. `-a PATH` — path to an anchor folder (the directory containing `.anchor`).
2. `-a SLUG` — slug name; script looks up via `ha --dump`. Errors if non-unique across the vault.
3. Flag absent — script walks cwd UP looking for `.anchor`; uses that folder.

Errors if all three modes fail (flag absent AND no `.anchor` ancestor of cwd).

## BACKLOG ROWS — `state Backlog <F<n>|T<n>> <verb>`

```
define    create-or-replace the WHOLE row. Body (stdin / --body / --from-file) is the
          complete row markdown:
              - **<label> — Title** [Status] — body
          optionally followed by indented sub-bullets (carried through verbatim).
          F+ / T+ mints the next number (independent namespaces, zero-padded triple-digit);
          write the placeholder in the body header (`- **F+ — Title** [Status]`) and the
          minted label is substituted. An explicit F<NNN> label replaces that row in place.
          --horizon H   optional. Now|Next|Later|Active|Ready|Verify|Done.
                        New rows default to Now; existing rows stay put.
          Status guards enforce as always: [Ready]/[Active] need a Next declared,
          [Verify]/[Watching] need a Verify question (in the body sub-bullets).
          Entering the Verify/Verify-by/Watching family additionally needs
          --why-user (F240 ownership gate; see `set` below).

set       partial update; omitted flags preserve current values. At least one of:
          --status S    new bracket text (guards enforce; pair with --next / --verify
                        when the target status requires one).
          --horizon H   moves the row between H2 sections.
          --title  T    new title.
          --body   B    new body (flag only — set never reads stdin).
          --next   X    `- **Next:**` no-user action sub-bullet.
          --verify Q    `- **Verify:**` yes/no question sub-bullet.
          --user   A    F259 — `- **User:**` action a [User] row is gated on
                        (what the USER must do: log in, click a permission
                        dialog, enter a credential, tap 2FA). A [User] bracket
                        REQUIRES this sub-bullet + --why-user-action; it MAY
                        also carry a queued --next (the agent's post-user step).
          --why-user-action J
                        F259 ownership gate (the F240 sibling) — one sentence
                        naming the credential or human-only faculty the [User]
                        action requires. Required when a row ENTERS [User];
                        appended to `- **User:**` as `· *why-user-action: …*`.
                        Refused if the agent could do the action itself (then
                        it is [Ready] with a --next, not [User]).
          --why-user W  F240 ownership gate — one sentence naming the human
                        faculty the check invokes (taste / preference /
                        ratification / passive-use). Required when a row
                        ENTERS Verify/Verify-by/Watching or its --verify text
                        is rewritten; appended to the Verify sub-bullet as
                        `· *why-user: …*`. A mechanically-phrased question
                        ("did X mint/run/render", "does the file exist") is
                        refused outright — agent-grade; run it now or park
                        [Waiting] with an agent-check plan. Same-family
                        re-touches (horizon moves) are grandfathered.

resolve   move the row to ## Done [Done], appending `— resolved <date>: <note>` to the
          body. Note via stdin / --body / --from-file (optional).

remove    delete the row entirely. Rare — normally `resolve`, or `set --status Done`.
```

`F` rows are features (have a feature doc; the row links it `→ [[F<n> — Title]]`); `T` rows are tasks (the row IS the spec). `B-QFix` is a grandfathered machinery singleton owned by `audit-q.py --fix`, not a v2-addressable label.

## DOC QUERIES — `state <doc> <Q<n>|V<n>> <verb>`

Questions (`Q`) live in `## Open Questions` ABOVE the doc's H1 while pending (Phase 1/2/3 lifecycle per [[DAS ask-format]]); verifications (`V`) live under the doc's `## Verifications` H2 (per F235 the doc is the verify home).

```
Q define    create-or-replace Q<n> in place (subsumes add + rewrite). Q+ mints the lowest
            unused Q-number. Body via stdin / --body / --from-file; accepts either the bare
            body or the complete `- **Q<n> — ...` bullet. Write-time gate: ask-format
            requires >=2 own-line labeled option bullets (`- **(A)** ...`) AND a
            `- **Recommendation:**` line at indent 0 (value may be None).
            --why-ask J   F257 ownership gate (the F240 sibling) — one sentence justifying
                          why a Lean/Strong Q surfaces despite the agent having a
                          recommendation (high-stakes irreversibility: an external action,
                          an interface-sticky name/schema, an architecture lock-in, a
                          taste-only call). REQUIRED to mint a Lean/Strong Q; appended as
                          `· *why-ask: …*`. A `Recommendation: None` mints freely. An
                          agent-territory shape (ordering / batching / rollback / cosmetic
                          rename) is refused regardless of --why-ask. An already-annotated
                          Q is grandfathered on re-touch. audit-q C50 is the mirror.

Q resolve   move the Q to the bottom ## Resolved as a `### Q<n> — Title` H3.
            --choice OPT  required. the chosen option label, e.g. '(A)' — written into
                          `**Choice:** OPT` in the H3.
            <BODY>        optional resolution body; the blockquoted original Q context is
                          appended automatically. When the last pending Q resolves, the doc
                          enters Phase 2 (the above-H1 block is deleted).

Q remove    soft-delete (audit trail in ### Removed H3). --reason TEXT optional.
            Q-numbers stay consumed forever; never reused.

V define    create-or-replace V<n> under ## Verifications (H2 auto-created). V+ mints.
V resolve   record the user's answer on the V-item.
V remove    soft-delete with audit trail.
```

## BODY SOURCE

Pick ONE. Priority order if multiple given:

```
--body TEXT      inline (short one-liners; shell-quoted).
--from-file P    read from file (long bodies).
<stdin>          default when neither given. Heredoc-friendly. (`set` is the exception —
                 it never reads stdin; its --body is the row body value.)
```

## POST-CONDITIONS

Every mutation runs the full sync in one call — this is the atomic-propagation contract (F236 § Design):

```
1. target doc / backlog row updated.
2. audit-q.py --scope backlog --anchor <slug> --fix — refreshes ~/ob/kmr/Q.md
   (banner counts, status drift). Doc targets also run a lenient
   audit-q --scope q --dry (errors warn to stderr; never unwind the edit).
3. one [INFO] entry appended to {slug} Messages.md + the global agent-messages sentinel.
```

**Bracket normalization is part of step 2 — an unbacked `[Designing]`/`[Questions]` is promoted to `[Ready]`.** The `--fix` pass re-derives status against ground truth: a `[Designing]` row (C23) or a `[Questions]`/`[N Questions]` row (C24) whose backing shows **zero** pending Qs is rewritten to `[Ready]` (Designing-alone is a turn-ownership deadlock — user direction 2026-05-26; a Questions bracket over no open questions is stale). Backing is counted from the row's arrow link `→ [[doc]]` (its `## Open Questions` block) when present, else the row's own inline `- **Q<n> —` sub-bullets (T012). **Consequence for operators:** `state` prints the bracket you *asked for*, but if it isn't backed the on-disk bracket becomes `[Ready]`. To genuinely park a row in `[Designing]`/`[Questions]`, give it real pending Qs — inline `- **Q<n> —` sub-bullets in the same `define`, or an arrow link to a doc whose `## Open Questions` is live. This is working-as-designed, not drift; it is exactly the groom discipline that a frontier row may not rest in `[Designing]`.

## EXAMPLES

```
# row: mint a new Designing feature, default horizon Now — parse "added F<NNN>" from stdout
echo '- **F+ — Sparse-checkout docs migration** [Designing]' | state Backlog F+ define

# row: cross-anchor mint (explicit slug)
echo '- **F+ — Dmux ghost-panel bug** [Designing]' | state -a MUX Backlog F+ define

# row: promote to Ready (guards demand the Next)
state Backlog F099 set --status Ready --next "implement per Design § 2"

# row: move horizon AND change body
state Backlog F099 set --horizon Later --body "→ [[F099 — sparse-checkout]] — deferred to v2"

# row: finish with a resolution note
state Backlog F099 resolve --body "Shipped 2026-07-13 — commit abc123"

# q: mint on any doc (feature doc, PRD, design doc) — ask-format enforced at write time
state "MUX PRD" Q+ define < q-body.md

# q: replace an existing Q's body (define IS the rewrite)
state "F091 — Trigger mechanism" Q5 define < new-body.md

# q: resolve by number
echo 'team picked A' | state "F091 — Trigger mechanism" Q5 resolve --choice '(A)'

# q: remove with audit trail
state "F091 — Trigger mechanism" Q5 remove --reason 'obsoleted by F128'

# v: define an addressable verification on the doc (F235)
echo 'Does the render link the doc first? — check SKA queries.md' | state "Bridge Design" V+ define
```

## DESIGN NOTES

The design decisions behind the grammar (F236, user-designed 2026-07-13):

- **One address scheme** — a document's stateful sub-items are all the same kind of thing, addressed the same way; `state <doc> <label> <verb>` collapses the old per-family surface (`task`/`q`/`--verify`) to one grammar, the label letter (F/T/Q/V) distinguishing kind.
- **`define` is create-or-replace** — one idempotent verb, no add-vs-rewrite mode split; the audit trail is git + `remove`'s soft-delete, not write-mode ceremony.
- **`set` exists for rows only** — the bracket-only transition is the common case; `set`'s preserve-on-omit flags keep `--status X --next "..."` convenient. Q/V partial edits are full-body `define`s.
- **Any doc can carry items** — a design doc with open questions is a first-class target; asking a question IS assigning it to a document.
- **anchor optional (cwd-walkup)** — agents know their anchor via cwd; path lookup handles non-unique slugs; explicit slug still accepted.
- **Doesn't create the feature-doc file** — `state Backlog F+ define` mints the ROW; `/feature` owns the doc. Orphan rows surface as audit-q findings by design; bundling would duplicate `/feature`'s shape conventions into the script.

**Enforcement is two-sided.** `state`-side integrity runs audit-q on every mutation; hand-edit-side, warden's `R-pathguard` denies backlog/queries hand-edits and `R-state-region` (anchor-base, vault-wide) reminds on hand-edits to any item-bearing doc's `## Open Questions` / `## Resolved` / `## Status` regions (advisory, per F236 Q3).

## IMPLEMENTATION STATUS

- **Canonical (F236, 2026-07-13):** the v2 grammar above — `<doc> <label> <verb>` with `+`-mint and `set` — plus the surviving `status` (F130) and `roadmap` (F145) domains. The F129 `task`/`q` verb families were retired in the same release (tombstones point at the v2 forms); all skill runbooks (`/feature`, `/ask`, `/groom`, `/crank`, `/mint`, `/finalize`, `/rewire`, `/audit`, workflow) were swept in the same pass.
- **Helper layer:** `~/.claude/skills/workflow/scripts/backlog-edit.py` holds the shared row/Q helpers; `state` delegates via importlib — single source of truth at the helper level; both share the same state.json file used by `/audit integrity`.

## RELATED

- [[F236 — state v2 — one address scheme — state doc label verb for rows, questions, and verifications|F236]] — the one-address-scheme design + milestones.
- [[DAS ask-format]] — Q-format spec the script enforces.
- [[F235 — Verification lives in the feature doc — Success Criteria as the verify home, render links the doc|F235]] — the doc-first verification chain V-items complete.
- [[F127 — Always-render ask report — ask invariant render + audit + glance before dialogue|F127]] — the render-audit-glance invariant the doc-target post-conditions implement.
- [[F128 — Status script as source-of-truth for Q-management — extend backlog-edit.py|F128]] / F129 — the predecessors (2026-06-07).
- [[DAS workflow]] — user-voice discipline page.
