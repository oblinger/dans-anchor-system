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
- **`<label>`** — LETTERS+DIGITS, the item's primary key within the doc: `F157` / `T8` / `Q9` on the Backlog, `Q7` / `V3` on any other doc. The mint form LETTERS+`+` (`F+`, `T+`, `Q+`, `V+`) assigns the next unused number — valid only with `define`; the assigned label is printed in the output. **`Q<n>` is polymorphic on the `<doc>` argument** (F275): on `Backlog` it is a *standalone feature-less question row* (the row body IS the question); on any other doc it is a *doc-scoped Open Question*. The two number-spaces are independent.
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

### Standalone question rows — `state Backlog Q<n> define` (F275 M2/M3)

A `Q<n>` row is a **feature-less question** — sibling to `F`/`T`, minted with `state Backlog Q+ define`. It exists because a genuine question may have no host feature (a config value, a spoken-vocabulary word, a cross-cutting call); the row **body is the question itself**, so `define` runs the same gates as a doc-scoped Q — ask-format (≥2 labeled options + `- **Recommendation:**`), the F270 `- **Damage:**` field (a `waste`/`priority` row auto-resolves to the lean and lands `[Done]`, never surfacing) — **plus** a hard-required F275 `- **On answer:**` clause (the concrete consequence of each answer; a define missing it is refused). The row brackets `[Questions]`, is self-backing (its number lives in the header, so it needs no linked Q-bearing doc and is exempt from the `[Questions]`-promise write-guard and audit-q C24), renders under `## Questions` in `{slug} queries.md`, and resolves with `state Backlog Q<n> resolve`.

## DOC QUERIES — `state <doc> <Q<n>|V<n>> <verb>`

Questions (`Q`) live in `## Open Questions`, the first H2 below the doc's H1; verifications (`V`) live under the doc's `## Verifications` H2 (per F235 the doc is the verify home).

**The block has two zones and two states (F291).** While it lives it holds every question the round raised — unresolved first, then a `### Resolved` zone — and `resolve` moves a question between them rather than removing it. So the open count is a prefix length rather than a scan, and a question arriving mid-round is not a structural event at all. The block only ever leaves the doc once: the `resolve` that empties the unresolved zone also deletes the block and writes every entry to the top of the bottom `## Resolved`. That replaces the old Phase 1/2/3 lifecycle, in which the block was deleted when its last Q resolved and **recreated** when a new one arrived — each recreation an opportunity to write the format wrong. The agent performs no part of the migration.

```
Q define    create-or-replace Q<n> in place (subsumes add + rewrite). Q+ mints ONE ABOVE
            the doc's high-water Q-number — monotonic forever, never recycled, because a
            migrated entry keeps its ^F<n>-Q<n> block-ID and a reused number would put that
            anchor in the file twice (Obsidian resolves the duplicate by proximity, and no
            audit check would catch it). Same policy F-numbers already follow.
            Body via stdin / --body / --from-file; accepts either the bare
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

Q resolve   move the Q to the block's `### Resolved` zone as a `### Q<n> — Title` H3,
            keeping its ^F<n>-Q<n> block-ID. When that empties the unresolved zone, the
            same call migrates: the block is deleted and every entry is written to the TOP
            of the bottom ## Resolved, above what is already there — so the section reads
            newest-batch-first, interleaving migrated rounds with F068 auto-decisions.
            --choice OPT  required. An option label ('(B)') — validated against the Q's own
                          listed options, so a resolve issued against a stale reading of
                          them is refused — or the literal `none` when the resolution
                          landed outside every listed option, optionally with what happened
                          instead: --choice 'none — handed to DMP F005'. Required rather
                          than optional on purpose: an omitted flag cannot be told apart
                          from a forgotten one, so optionality would trade a real signal
                          for an ambiguity (the T079 failure mode).
            <BODY>        optional rationale — WHY this option won. What got BUILT as a
                          result belongs on the backlog row's Next/Done; a note that
                          absorbs implementation detail fills the archive with text that
                          is stale within a week.

            The entry reads question → resolution → options → lean. Resolution and lean are
            separate lines because they answer different questions: `**Lean:**` carries what
            the agent recommended, `**Resolved:**` what actually happened, and the delta
            between them is the calibration signal the old conflated `**Choice:**` line
            destroyed. Rejected options ride along, one line each, so the record stands
            alone instead of sending a reader to git.

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

**Enforcement is two-sided.** `state`-side integrity runs audit-q on every mutation; hand-edit-side, warden's `R-pathguard` denies backlog/queries hand-edits and hand-edits to a feature doc's `## Open Questions`, while `R-state-region` (anchor-base, vault-wide) reminds on hand-edits to any item-bearing doc's `## Open Questions` / `## Resolved` / `## Status` regions (advisory, per F236 Q3).

**The guard covers the open block, not the archive (F291).** A feature doc's `## Resolved` carries only the advisory, on the rule *deny where desync is possible, detect where it is not*. `state` owns the open block because it maintains things that can silently drift — the integrity stamp, the Q-numbering, the rendered queue, the counts that reach `Q.md`. None of that survives archiving: a resolved entry is not rendered, not counted, and gates nothing. Half the section is unaddressable by construction anyway — F068 auto-decisions go straight in as un-numbered H3s that no `Q<n>` verb can reach — so a blanket deny forbade the mechanism that populates it, and produced the T066 deadlock where a lint demanded a fix inside a region every write path refused.

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
