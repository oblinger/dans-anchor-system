---
description: the shared facet behind pebbles and rocks — one file per item, a hand-arranged control file that orders them, and propagation along the feed DAG
group: folder
---

| -[[DAS Stone]]- | → [[DAS]] → [[FCT]] → [DAS Stone](hook://p/DAS%20Stone)  |
| --- | --- |
| [[DAS Stone Design\|Design]]  | [[DAS Stone Keys\|Keys]],   |
| Examples | [[LUMEN Pebble\|Pebbles — a second Kind]],  [[HBR Rocks\|Rocks]],   |
| Related | [[DAS Backlog]],  [[DAS Agenda]],   |
| Rules | [[R-stone]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Chores]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[DAS Move]],  [[DAS Naming]],  [[DAS Notebook]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Ruleset]],  [[DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS Subs]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Stone
Facet spec for a **stone group** — a `{slug} Track/{slug} {Kind}s/` folder holding one file per item, ordered by a hand-arranged control file, and propagated to downstream anchors along the `feeds:` DAG.

**TLDR** — Pebbles and rocks are the same shape of thing at two sizes, so they are one facet parameterised by **kind**, not two facets that resemble each other.

**Cardinality:** any number of kinds; at most one group per kind per anchor.

**The example is a Pebbles group on purpose** (adjudicated 2026-08-18, [[TINK327 - Every facet has a worked example, and FEX {facet} is how you reach it|F327]]). This row previously cited `HBR Rocks` and `MED Rocks` — two instances of the *same* kind, and the first of them also [[DAS Rocks]]' own example. A facet whose entire claim is *"one shape parameterised by kind"* cannot demonstrate that with two examples of one kind: they show the shape and leave the parameter untested. [[LUMEN Pebble]] is the control file of a Pebbles group, so the pair now spans both kinds, and a reader can see which parts vary with kind and which do not.

## What a stone group is

A **stone** is one unit of work-worth-naming: a **pebble** is small and nagging, a **rock** is a multi-week chunk. Both materialise identically — a folder under the anchor's Track facet, one markdown file per stone, and a **control file** carrying the human's ordering.

The kinds are open-ended and declared in configuration. Nothing about `pebble` or `rock` is hard-coded; they are the two that ship.

| | `pebble` | `rock` |
|---|---|---|
| folder | `{slug} Pebbles/` | `{slug} Rocks/` |
| control file | `{slug} Pebble` | `{slug} Rock` |
| stone file | `{slug} P0001` | `{slug} R0001` |
| stone display | `{slug}:` | `{slug}:` |
| header display | `-[[…\|{slug}]]-` | `-[[…\|{slug}]]-` |

Folder names default to plural per [[DAS Facets]]; the control-file name is **configuration, not convention** — it is invisible to the mechanism, because a header is identified by what it links to rather than by what it is called.

## The one idea everything else follows from

**A control-file line is simultaneously a human's ordering decision and a machine's reference.** It opens with a link whose *target* is a numbered stone file and whose *display* is a short provenance label:

    [[VEC R0001|VEC:]] decide Aria

which reads `VEC: decide Aria`. Because the display carries the source anchor, that exact line can be pasted into any downstream anchor's control file and still reads correctly *and* still resolves to the original stone. **Propagation is therefore line-copying rather than rendering**, which is what lets a downstream control file stay hand-editable instead of becoming a generated block nobody may touch.

## Who edits what

This inverts the usual split, and the inversion is the point:

- **Agents** create, edit and delete **stone files**. They do not normally touch a control file.
- **The user** arranges **control files** — order, grouping, what is published.
- **`stone`** keeps the two consistent and propagates along the feed DAG.

## A backlog row deferred on a stone is linked from that stone's roadmap

**Interim convention, Dan 2026-08-13 — it exists because a backlog row cannot currently block on a stone.** `audit-q` **C55** resolves a `[Blocked <handle>]` against backlog rows only, so `[Blocked TINK-P0004]` is refused as a dangling handle even when the pebble is exactly what the row waits on.

Until that changes, when work is deferred because a stone has to happen first:

1. **Park the feature in `## Later`.** The bracket stops driving the frontier there, so pick the honest one rather than contorting to satisfy a checker.
2. **Add it to the stone's `## Roadmap`, in the same edit.** The stone body carries a table of the feature documents its work needs. That table is the *only* thing keeping a parked row reachable, so a row in Later with no entry there is lost rather than deferred — which is precisely the failure [[DAS Backlog]] § The four classes warns about for a blocker with no handle.

**⚠ Parking does NOT hide the row, and the earlier wording here said it did.** Step 1 read *"a Later row renders in no queue whatever its bracket, which is the invisibility being asked for"* until 2026-08-19. That is false, and it is false for exactly the brackets a deferred row usually carries. `audit_q.renders_in_body` — the single predicate the banner and the body both read — admits a `## Later` row whose bracket is **`Questions`, `Verify*`, or `Blocked …`**, and hides only `Ready`, `Designing`, `User` and `Waiting`. Each of those admissions was ruled deliberately: `Blocked` because 37 vault-wide `[Blocked …]` rows were vanishing from the very ledger F283 built to stop rows vanishing, and `Questions`/`User` because Dan's 2026-08-07 rule is *"Ready, User and Parked are all shown. The only one that's not shown is Waiting."*

**So the convention buys reachability, not invisibility.** Measured on TINK 2026-08-19: 62 rows parked into `## Later` across nine pebbles left `## Now` and `## Next` empty, and the queries render still enumerated 47 of them. Whether a Later row carried on a stone's roadmap should be suppressed from the render is an open question — [[TINK Backlog#^T246|T246]] — and it is the same question as the end state below, approached from the render side.

**The intended end state is that blocking on a stone is simply allowed.** It is not built yet because it mixes the two stores: a `stone update` pass would then have to affect the backlog, and that coupling needs designing before it ships rather than after.

## Headers, and how publishing works

A **header** is any line whose first link targets a control file. Pointing at *this* file's own control file makes it the **self-section**; pointing at another anchor's makes it that anchor's **import site**. An anchor publishes a stone by placing its line **below the self-section**.

Each downstream anchor chooses where imports land by writing a header for the source: a bare header takes block form, a header followed by a plain-text colon takes inline comma-separated form, and an absent header means the top of the file.

## Keys

A stone carries `key:: value` parameters, **at the top of the file, above the prose**. Full vocabulary and the reasoning: [[DAS Stone Keys]].

## Rules

**Four of the six are `checked` and armed, since 2026-08-11.** `R-stone-01`, `-02`, `-04` and `-06` carry `check::` refs into `audit-plan.py`. **The arming that counts is [[R-anchor]]'s `include::`, not [[R-facet]]'s** — `/audit anchor` resolves `R-anchor`, which names [[R-rocks]] and now [[R-stone]] directly; `R-facet` is one of the 60 rulesets outside that closure, so adding a set to it changes nothing that runs. Both were updated, and it is worth knowing which one did the work. The four checkers are **kind-generic**: not one of them names `pebble` or `rock`. Every per-kind fact — folder name, control-file name, stone prefix, digit count, and the two display aliases — is read from `DAS Stone Kinds.json`, the same file `stone` reads, so a third kind needs no code written. The one place a kind is still named twice is this ruleset's `where::` glob, which lists the folder shapes to select; adding a kind means adding its folder there.

**Two of the six stay `stated`, and that is the answer rather than a delay.** `R-stone-05` asserts what *the mint refuses*, which is behaviour of the `stone` script rather than content of any document; it wants a guard test, the shape [[R-exception-discipline]]-03 already uses. `R-stone-03` forbids *deriving* a prefix from a kind's name — a claim about how a value was chosen, which no file can evidence. Forcing a `check::` onto either would buy a coverage claim and no coverage.

**The live corpus is 8 groups across 2 kinds and all 8 pass, so the corpus is not the evidence.** Rocks: `AIS` 3, `HBR` 3, `MED` 1, `VEC` 1. Pebbles: `SV` 3, `SYS` 2, `NJ` 2, `MED` 1. A ruleset that passes 100% on its first run has demonstrated nothing about whether it *can* fail — that is the vacuous-zero shape this facet was written in the middle of. The evidence is a **deliberately malformed fixture** (`t164-fire-test.py`) carrying one defect per rule beside a well-formed twin: all four rules fire on the malformed group, none fires on the clean one. The live sweep is reported separately with its coverage counts — 8 groups, 56 judgements, 0 skipped-as-not-an-instance — because "no findings" is only meaningful next to "and here is how much it looked at".

**Those counts hold under a batch sweep and under no other access path, which the sentence above did not say.** Measured 2026-08-12 after [[ATT|Atticus]] reported zero `R-stone` verdicts on every pebble group he could reach. The two kinds are reached differently, and only one of the two is reached the way an agent actually audits its own anchor:

- **A rock group carries its own `.anchor`**, so it is a target in its own right. `--mode anchor` on the group's path fires all 24 stone judgements, and the T164 candidate-path fix in `_match_file_glob` is what lets `{anchor}/**/* Rocks/**` match from inside the folder the selector names.
- **A pebble group carries none** — `stone`'s `cmd_new` never mints one, and all 9 pebble groups in the vault confirm it. It is reachable only inside the scope of `{slug} Track/`, which *does* carry an `.anchor`. So `sub_anchor_roots` drops the whole Track folder from the owning anchor's scope, and **`--mode anchor SV` sees 11 files, zero of them a pebble.** `--mode anchor SV/SV Track` fires 18 stone judgements; `--batch SV --run` fires 12, because batch enumerates `SV Track` as an anchor in its own right. All three numbers were measured, not inferred.

So the pebble half is **armed and correct** — the facet's own reachability warning fired on the report rather than on the rules. What the measurement actually exposes is one level up and not specific to stones: **`/audit anchor <X>` is not an audit of X's tree.** It excludes every `{slug} Track/`, `{slug} Design/` and every other facet folder that carries an `.anchor`, alongside genuinely separate nested projects — 147 of them under `SV` — and nothing distinguishes the two, because a facet sub-anchor declares no trait that says it is one. An agent auditing its own anchor gets a green over the anchor page and its loose notes while its Backlog, Agenda, queries, Messages and stones were never opened. Filed as [[TINK Backlog#^T232|T232]].

**Three things had to be true before one rule ran, and each failed silently on its own.** The `check::` had to resolve to a registered checker; the ruleset had to exist as `rulesets/R-stone.md` rather than embedded in this file; and it had to be reachable from `R-anchor`. Fixing only the first two still produced a sweep with zero stone verdicts and no error anywhere — the recipe listed the rules, the tier read `(checked)`, and nothing ran. **Do not read an include, a tier, or a green sweep as evidence that a rule fired.** The only evidence is a named rule appearing in `--run` output against a named file, which is why the coverage counts below are reported next to the finding count.

**The `where::` blocker is gone, measured 2026-08-11.** This paragraph used to say a folder-shaped facet's `where::` *"currently selects nothing"*. It selects correctly now: a sweep over `Topic/MED` visits `MED Rocks` **as its own anchor** and emits verdicts. The earlier zero came from scoping on the *owning* anchor, which by design cannot see a facet sub-anchor ([[DAS Facet]] § folder facets).

**The evidence for that conclusion was itself wrong, and is corrected here** (T207, same day). This paragraph originally cited *"a `--batch` sweep … emits 13 `R-rocks` verdicts"*. Those thirteen were **recipe lines** — entries in the agent-judgment manifest — not executed checks, because `audit-plan`'s `--batch` branch returned before it ever reached `--run` and silently discarded the flag. The conclusion happened to be right and the number did not measure it; nothing in the output distinguished the two. `--batch --run` now executes (`test-t207-batch-run-executes.py` holds it), and the same sweep reports **1813 verdicts across 15 anchors**. Left standing as a caution: a count that agrees with what you expected is the one you are least likely to interrogate. Note the asymmetry the four kinds expose: a **rock** group carries its own `.anchor` and is reached as a sub-anchor, while a **pebble** group carries none and is reached inside its owning anchor's scope. The checkers resolve the owning slug the same way from either.

## The ruleset is a standalone companion, not embedded here
The rules live at **[[R-stone]]** (`rulesets/R-stone.md`), linked from the masthead's `Rules` row — the repo default since 2026-07-13 per [[R-facet-spec]] § companion ruleset, which superseded the F133 embedded form.

**This block used to be embedded in this file, and that is why arming it did nothing.** The plan builder resolves a ruleset slug to `rulesets/R-<slug>.md`; there was no such file, so `include:: [[R-stone]]` in [[R-facet]] resolved to nothing and no stone rule ever entered a plan. Measured 2026-08-11: `--batch Topic/MED` produced R-rocks verdicts on `MED Rocks` and not one R-stone verdict, before and after the arming. **The failure was silent in both directions** — the umbrella showed the include, this file showed six rules, four of them reading `(checked)`, and the sweep reported no findings. Every surface agreed the facet was covered; nothing was. That is the same shape as the `(retired)` tier fold that disabled `R-rocks-03`, arriving by a different route, and it is the third time this project has hit it. Moving the block out is the fix; the general lesson is that **a ruleset is not armed until a rule from it is seen in a plan**, and an include is not evidence of that.

# BRIEF

**This spec is the *shared* half only.** Anything true of every kind belongs here; anything true of one kind belongs to that kind's own facet — [[DAS Rocks]] and ~~[[DAS Pebble]]~~ — which declare their own `key::` vocabulary on top of this one. If you find yourself writing the word "pebble" into a rule here, it belongs there instead.

**[[R-stone]] is armed — added to [[R-facet]]'s `include::` 2026-08-11, four rules `checked`.** The condition this paragraph used to set has been met: the selector reaches folder-shaped instances, and the rules were verified by seeing them **fire**. Read the verification claim carefully before trusting it — the live corpus passes 8-for-8, which on its own is the failure this facet was written in the middle of (a ruleset reading `(checked)`, an audit reporting nothing, and no rule ever evaluated). What licenses the claim is the malformed fixture beside the clean twin, plus the coverage counts printed next to the zero. **Any future rule added here owes the same two things**: a fixture in which it fires, and a count of what it actually judged.

**Two rules here will never be `checked`, and the ruleset is stronger for saying so.** `R-stone-03` and `R-stone-05` are not weakly-evidenced — they are un-evidenced by any file, and marking them `checked` would trade a real limit for a false coverage number. When they get enforcement it will be a guard test against `stone`, not a `check::` here.

**The control-file name is configuration and must stay that way.** It is invisible to the mechanism because headers resolve by link target. Any rule that hard-codes `{slug} Rock` is a bug, not a tightening.
