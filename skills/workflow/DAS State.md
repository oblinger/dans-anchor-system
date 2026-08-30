---
description: "CLI reference for the `state` script — canonical state editor for everything below the anchor level. Verb-first: `state <verb> <anchor> <doc> [<label>]` for backlog rows, doc questions, and doc verifications. F129 (shipped 2026-06-07), unified by F236 (2026-07-13), verb-first since F293 (2026-08-01)."
---

# state — canonical state editor (CLI reference)
Man-page-style reference for the `state` CLI — the one write path for backlog rows, doc Open Questions, and doc Verifications.

> **STATUS:** Canonical. Shipped 2026-06-07 via F129; unified on one address scheme 2026-07-13 via F236; moved to the verb-first v3 grammar 2026-08-01 via F293, which REMOVED the address-first v2 form rather than deprecating it. `backlog-edit.py` ships alongside at the helper level — `state` delegates to it via importlib; new code always invokes `state`.

| Table of Contents |  |
|---|---|
| **[[#NAME]]** |  |
| **[[#SYNOPSIS]]** |  |
| **[[#ANCHOR RESOLUTION]]** |  |
| **[[#BACKLOG ROWS — `state <verb> <anchor> Backlog <F<n>|T<n>>`]]** |  |
|    [[#Standalone question rows — `state define <anchor> Backlog Q<n>` (F275 M2/M3)]] |  |
| **[[#DOC QUERIES — `state <verb> <anchor> <doc> <Q<n>|V<n>>`]]** |  |
| **[[#READING AN ITEM — `state show <anchor> <doc> <label>`]]** |  |
| **[[#INBOX — `state drop | inbox-list | inbox-tag`]]** |  |
| **[[#BODY SOURCE]]** |  |
| **[[#POST-CONDITIONS]]** |  |
| **[[#EXAMPLES]]** |  |
| **[[#DESIGN NOTES]]** |  |
| **[[#IMPLEMENTATION STATUS]]** |  |
| **[[#RELATED]]** |  |

## NAME

`state` — canonical state editor for backlog rows, doc Open Questions, and doc Verifications

## SYNOPSIS

```
state <verb> <anchor> <doc> <label> [verb-flags] [< body]   # item verbs
state show <anchor> <doc> <label>                           # read verb (T064)
state revalidate <anchor> <doc>                             # doc verb (F241)

state status  <anchor> <set|show> ...       # {slug} Status.md facet cells (F130)
state roadmap <anchor> <status|migrate> ... # {slug} Roadmap.md milestone state (F145)
state triage  <anchor>                      # crank exit handshake (F239)
state crank   <anchor> <start|stop|status>  # crank-session sentinel (F239)
state groom-list   <anchor> [--count]       # grooming worklist (F244)
state summary-line <anchor> --recommend R   # the canonical closing line (F248)
```

- **`<verb>`** — comes FIRST, and each verb owns its own flag schema, so `state <verb> --help` prints what that verb takes and nothing else. There are **item verbs** (`define` | `set` | `resolve` | `remove` | `show`) that address something inside a doc, **one doc verb** (`revalidate`) that acts on the doc itself, and the **domain verbs** listed above. A flag a verb does not declare is rejected by name — `set --from-file` and `resolve --horizon` are parse errors, not runtime complaints.
- **`<anchor>`** — MANDATORY on every verb; see ANCHOR RESOLUTION.
- **`<doc>`** — the addressed document: the literal **`Backlog`** (the anchor's backlog file), a **wiki-name** (case-insensitive `.md` basename match — anchor tree first, then vault root; zero matches errors, multiple matches errors listing every candidate), or a **path**. Any markdown doc qualifies — feature docs, PRDs, standalone design docs.
- **`<label>`** — LETTERS+DIGITS, the item's primary key within the doc: `F157` / `T8` / `Q9` on the Backlog, `Q7` / `V3` on any other doc. The mint form LETTERS+`+` (`F+`, `T+`, `Q+`, `V+`) assigns the next unused number — valid only with `define`; the assigned label is printed in the output. **`Q<n>` is polymorphic on the `<doc>` argument** (F275): on `Backlog` it is a *standalone feature-less question row* (the row body IS the question); on any other doc it is a *doc-scoped Open Question*. The two number-spaces are independent.
- **`<verb>`** — `define` | `set` | `resolve` | `remove` (per-target semantics below).

## ANCHOR RESOLUTION

`<anchor>` is a **mandatory positional on every verb**, resolved two ways:

1. **SLUG** — the normal form; looked up by the vault scan. For the backlog verbs, errors if no `{slug} Backlog.md` is found.
2. **PATH** — a directory containing `.anchor`; the slug is read from that file's `slug:` line. For anchors not yet reachable by name.

**The Inbox verbs need no backlog** ([[Tink Backlog#^T562|T562]], 2026-08-20). `drop` / `inbox-list` / `inbox-tag` write and read `{slug} Inbox.md`, which has nothing to do with a backlog — but slug resolution ran through `find_backlog` for every verb, so an anchor that tracks without a backlog could not be addressed by name at all. Measured: **1,466 vault anchors answer to a unique slug and 1,430 of them hold no backlog**, so `state drop <SLUG>` reached about 36 of them. For these three verbs the slug now resolves to the anchor that answers to it — the one whose `.anchor` **declares** that slug, or, when `.anchor` declares none, the one whose **folder is named** it ([[DAS Dot Anchor]]'s basename fallback; four of the five anchors that surfaced this declared no slug). Declarations are matched first, so a declaration beats a naming coincidence.

**Exactly one, never the first of several.** An ambiguous slug still errors. A drop is fire-and-forget — no reply, no ack, and the sender never comes back to check — so delivering to the wrong anchor because two answered is a message nobody ever finds. The backlog verbs are unchanged in every respect, including their error text, which was written against real incidents and diagnoses more than a resolution would.

**Nothing is inferred (F293).** v2 accepted the anchor as an optional `-a` flag and, when it was omitted, walked cwd upward to the nearest `.anchor`. That made the same command write to a different anchor depending on where the caller was standing, with nothing in the output naming which one it picked — *"a bug waiting to happen"* (Dan, 2026-08-01). `state` is a called tool, not a typed one, so the address is spelled out. Removing the inference is also what let the whole address become positional: an optional argument cannot sit in the middle of other positionals, which is the only reason the anchor was ever a flag.

## BACKLOG ROWS — `state <verb> <anchor> Backlog <F<n>|T<n>>`

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

`F` rows are features (have a feature doc; the row links it `→ [[F<n> — Title]]`); `T` rows are tasks (the row IS the spec). `B-QFix` is a grandfathered machinery singleton owned by `audit-q.py --fix`, not a `state`-addressable label.

### Standalone question rows — `state define <anchor> Backlog Q<n>` (F275 M2/M3)

A `Q<n>` row is a **feature-less question** — sibling to `F`/`T`, minted with `state define <anchor> Backlog Q+`. It exists because a genuine question may have no host feature (a config value, a spoken-vocabulary word, a cross-cutting call); the row **body is the question itself**, so `define` runs the same gates as a doc-scoped Q — ask-format (≥2 labeled options + `- **Recommendation:**`), the F270 `- **Damage:**` field (a `waste`/`priority` row auto-resolves to the lean and lands `[Done]`, never surfacing) — **plus** a hard-required F275 `- **On answer:**` clause (the concrete consequence of each answer; a define missing it is refused). The row brackets `[Questions]`, is self-backing (its number lives in the header, so it needs no linked Q-bearing doc and is exempt from the `[Questions]`-promise write-guard and audit-q C24), renders under `## Questions` in `{slug} queries.md`, and resolves with `state resolve <anchor> Backlog Q<n>`.

## DOC QUERIES — `state <verb> <anchor> <doc> <Q<n>|V<n>>`

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

            If the bottom ## Resolved ALREADY holds a `### Q<n>` for a question in
            the migrating batch — an agent wrote the entry itself, which F291 made
            legal — the two are MERGED, not both written. The agent's text wins:
            it was written while the decision was fresh and is normally better
            reasoned than a generated stub, so only a missing `**Resolved:**` line
            is grafted on, at the end, where it reorders nothing. `state` says so
            on stderr (`Q8 already had a Resolved entry; kept yours`). Writing both
            would put `^F<n>-Q<n>` in the file twice — a duplicate block-ID, the
            F281 collision class at document scale, which no audit check looks for
            (T085).

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

## READING AN ITEM — `state show <anchor> <doc> <label>`

```
show      print the item's full markdown — the row line or Q/V header PLUS its
          sub-bullet span — and do nothing else. Reads F/T/C/Q rows on the
          Backlog (Icebox included) and Q/V items on any other doc, in ANY
          zone: unresolved, `### Resolved`, `### Removed`, or archived under
          the bottom `## Resolved`. Not knowing which zone an item is in is
          the reason to be asking.
          stdout is the markdown verbatim, so it pipes straight back into
          `define`; the file + line locator goes to stderr.
          Runs NONE of the post-conditions below — no audit-q, no Q.md
          refresh, no Messages entry. Reading is not an event.
```

Until T064 (2026-08-01) `state` had no read verb: `define` / `set` / `resolve` /
`remove` are every one of them writes, so you could create and mutate a row but
never ask what one said. That hole is what made a malformed row unrecoverable —
`state` refuses to edit a row its parser cannot read, `R-pathguard` refuses the
hand edit, and the only way through was `remove` then `define`, with nothing to
look at first.

**`show`, not `get`.** `get` reads as the symmetric opposite of `set`, and the
symmetry does not hold: `set` is rows-only by design while `show` reads Q/V on
any doc, and `set` writes a *field* (`--status Done`) whose true inverse returns
one value, whereas `show` dumps the whole item. Git draws the same line for the
same reason — `git show` displays an object, `git config --get` retrieves a
value. `get` is deliberately left unspent for the operation that genuinely is
`set`'s inverse: scriptable field access, `state get <addr> --status` printing
to stdout, which anything branching on a row's state would want today.

**`remove` echoes what it deleted**, to stderr, before printing its status line
— kept as a backstop rather than an alternative. `show` serves the caller who
looks first; the echo serves the one who does not. A row `remove` is a HARD
delete of the row *and* every sub-bullet under it, with none of the `### Removed`
audit trail a Q gets. This is also why a `remove --dry-run` was dropped rather
than built: a dry run only helps someone who already suspected they needed one.

## INBOX — `state drop | inbox-list | inbox-tag`

Three verbs cover the [[DAS Inbox]] drop-zone's whole lifecycle (T131). `<anchor>` here is the TARGET anchor whose Inbox is being written to or read — resolved the same two ways as everywhere else (SLUG or a path holding `.anchor`); nothing is inferred from cwd.

```
drop        state drop <anchor> "<message>" [--source S] [--tag T] [--topic H]
            Appends ONE pending entry to `{prefix} Track/{prefix} Inbox.md`
            (`{prefix}` comes off the anchor's own Backlog FILENAME, not the
            `.anchor` slug — those differ whenever the display name isn't
            already all-caps), creating the file from the standard template
            on first drop. The entry carries NO status tag — that absence is
            the whole pending signal the `Inbox N` banner counts. --source
            names the sender (attribution line only); --tag here is a
            message TYPE (fact/handoff/note/nudge), NOT a status — DONE /
            MOVED → are written by inbox-tag, never by drop. --topic sets
            the dated H2's topic; derived from the message's opening
            sentence when omitted. Nothing is executed by dropping.

inbox-list  state inbox-list <anchor> [--all]
            Prints every PENDING entry's markdown verbatim (heading +
            attribution + body). "Pending" is decided by the exact regexes
            `count_pending_inbox` (audit-q.py) counts against — imported,
            not restated, so this can never disagree with the `Inbox N`
            banner about which entries qualify. --all also lists processed
            entries (debugging only).

inbox-tag   state inbox-tag <anchor> --date D [--topic T] --tag TAG
            The drain's sanctioned writer, paired with `drop` at the other
            end of an entry's lifecycle. Locates the one entry dated `D`
            (disambiguated by --topic, a case-insensitive substring, when
            more than one entry shares that date) and appends the
            normalized tag to its existing H2 line — the topic text already
            on disk is never re-typed. --tag must be exactly `DONE` or
            `MOVED → {destination}` (R-fct-inbox-03's whole vocabulary); a
            bare `MOVED` with no destination is refused, and so is a
            re-tag of an already-processed entry.
```

The `/inbox` skill is the procedure that walks the pending list, integrates each entry into the right planning surface, and calls `inbox-tag`; it never hand-edits the Inbox markdown.

## BODY SOURCE

Pick ONE. Priority order if multiple given:

```
--body TEXT      inline (short one-liners; shell-quoted).
--from-file P    read from file (long bodies). Declared by `define` and `resolve`.
<stdin>          default when neither given. Heredoc-friendly.

`set` is the exception: it names each field with its own flag and reads no body stream at
all, so it declares `--body` (the row body value) and not `--from-file`. Under v2 that was
a runtime refusal inside the handler, because all thirteen flags were declared globally and
every verb inherited every one of them; per-verb schemas make it a parse error instead.
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

```bash
# row: mint a new Designing feature, default horizon Now — parse "added F<NNN>" from stdout
echo '- **F+ — Sparse-checkout docs migration** [Designing]' | state define SKA Backlog F+

# row: another anchor — the same call shape, because the anchor is always spelled out
echo '- **F+ — Dmux ghost-panel bug** [Designing]' | state define MUX Backlog F+

# row: promote to Ready (guards demand the Next)
state set SKA Backlog F099 --status Ready --next "implement per Design § 2"

# row: move horizon AND change body
state set SKA Backlog F099 --horizon Later --doc "F099 — sparse-checkout"

# row: finish with a resolution note
state resolve SKA Backlog F099 --body "Shipped 2026-07-13 — commit abc123"

# q: mint on any doc (feature doc, PRD, design doc) — ask-format enforced at write time
state define MUX "MUX PRD" Q+ < q-body.md

# q: replace an existing Q's body (define IS the rewrite)
state define SKA "F091 — Trigger mechanism" Q5 < new-body.md

# q: resolve by number
echo 'team picked A' | state resolve SKA "F091 — Trigger mechanism" Q5 --choice '(A)'

# q: the outcome was none of the listed options
state resolve SKA "F091 — Trigger mechanism" Q5 --choice 'none — handed to DMP F005'

# q: remove with audit trail
state remove SKA "F091 — Trigger mechanism" Q5 --reason 'obsoleted by F128'

# v: define an addressable verification on the doc (F235)
echo 'Does the render link the doc first?' | state define SKA "Bridge Design" V+

# doc: validate-then-stamp an Open Questions block after a hand-edit (F241)
state revalidate SKA "F091 — Trigger mechanism"
```

## DESIGN NOTES

The design decisions behind the grammar (F236, user-designed 2026-07-13; F293, 2026-08-01):

- **One address scheme** — a document's stateful sub-items are all the same kind of thing, addressed the same way; `<anchor> <doc> <label>` collapses the old per-family surface (`task`/`q`/`--verify`) to one grammar, the label letter (F/T/Q/V) distinguishing kind.
- **Verb-first (F293)** — the verb is read before anything else, which is what makes per-verb flag schemas possible at all: v2 had to consume the address before it knew the verb, so every flag was declared globally and all thirteen printed on every usage line. It also deletes a class of ambiguity rather than managing it — `revalidate` takes no label, and under an address-first grammar that shape could only be told from `<doc> <label> <verb>` by inspecting the last token, a heuristic that hijacked dispatch whenever the word appeared in a `--reason` or a title (F250 #12).
- **`define` is create-or-replace** — one idempotent verb, no add-vs-rewrite mode split; the audit trail is git + `remove`'s soft-delete, not write-mode ceremony.
- **`set` exists for rows only** — the bracket-only transition is the common case; `set`'s preserve-on-omit flags keep `--status X --next "..."` convenient. Q/V partial edits are full-body `define`s.
- **Any doc can carry items** — a design doc with open questions is a first-class target; asking a question IS assigning it to a document.
- **anchor mandatory (F293)** — spelled out on every call, never inferred. See ANCHOR RESOLUTION for why cwd-walkup went.
- **Doesn't create the feature-doc file** — `state define <anchor> Backlog F+` mints the ROW; `/feature` owns the doc. Orphan rows surface as audit-q findings by design; bundling would duplicate `/feature`'s shape conventions into the script.

**Enforcement is two-sided.** `state`-side integrity runs audit-q on every mutation; hand-edit-side, warden's `R-pathguard` denies backlog/queries hand-edits and hand-edits to a feature doc's `## Open Questions`, while `R-state-region` (anchor-base, vault-wide) reminds on hand-edits to any item-bearing doc's `## Open Questions` / `## Resolved` / `## Status` regions (advisory, per F236 Q3).

**The guard covers the open block, not the archive (F291).** A feature doc's `## Resolved` carries only the advisory, on the rule *deny where desync is possible, detect where it is not*. `state` owns the open block because it maintains things that can silently drift — the integrity stamp, the Q-numbering, the rendered queue, the counts that reach `Q.md`. None of that survives archiving: a resolved entry is not rendered, not counted, and gates nothing. Half the section is unaddressable by construction anyway — F068 auto-decisions go straight in as un-numbered H3s that no `Q<n>` verb can reach — so a blanket deny forbade the mechanism that populates it, and produced the T066 deadlock where a lint demanded a fix inside a region every write path refused.

## IMPLEMENTATION STATUS

- **Canonical (F293, 2026-08-01):** the verb-first grammar above — `<verb> <anchor> <doc> [<label>]` with `+`-mint, `set`, and per-verb flag schemas — plus the `status` (F130), `roadmap` (F145), `triage`/`crank` (F239), `groom-list` (F244) and `summary-line` (F248) domains, each now carrying the same mandatory anchor. The address-first v2 form was REMOVED in the same commit that added v3, not deprecated beside it: a half-done migration leaves both grammars live, which is the outcome Q003 rated worst. A v2-shaped call gets a tombstone naming the v3 form. Earlier: F236 (2026-07-13) unified the address scheme and retired the F129 `task`/`q` verb families.
- **Helper layer:** `~/.claude/skills/workflow/scripts/backlog-edit.py` holds the shared row/Q helpers; `state` delegates via importlib — single source of truth at the helper level; both share the same state.json file used by `/audit integrity`.

## RELATED

- [[F236 — state v2 — one address scheme — state doc label verb for rows, questions, and verifications|F236]] — the one-address-scheme design + milestones.
- [[DAS ask-format]] — Q-format spec the script enforces.
- [[F235 — Verification lives in the feature doc — Success Criteria as the verify home, render links the doc|F235]] — the doc-first verification chain V-items complete.
- [[F127 — Always-render ask report — ask invariant render + audit + glance before dialogue|F127]] — the render-audit-glance invariant the doc-target post-conditions implement.
- [[F128 — Status script as source-of-truth for Q-management — extend backlog-edit.py|F128]] / F129 — the predecessors (2026-06-07).
- [[F293 — state CLI v3 — verb-first grammar|F293]] — the verb-first grammar, mandatory anchor, and per-verb schemas.
- [[DAS workflow]] — user-voice discipline page.
