---
description: the shared facet behind every kind of stone — one file per item, a control file that orders them (by hand or by machine), and propagation along the feed DAG
group: folder
---

| -[[DAS Stone]]- | → [[DAS]] → [[FCT]] → [DAS Stone](hook://p/DAS%20Stone)  |
| --- | --- |
| [[DAS Stone Design\|Design]]  | [[DAS Stone Keys\|Keys]],   |
| Examples | [[Lumen Pebble\|Pebbles — a second Kind]],  [[HBR Rocks\|Rocks]],   |
| Related | [[DAS Backlog]],  [[DAS Agenda]],   |
| Rules | [[R-stone]],   |
| ... | [[anchor-page]],  [[DAS All Files]],  [[DAS Anchor]],  [[DAS Anchor Page]],  [[DAS Anchor Tree]],  [[DAS API Design]],  [[DAS Architecture]],  [[DAS Aspects]],  [[DAS At Entity]],  [[DAS Brief]],  [[DAS Cards]],  [[DAS Changes]],  [[DAS Chores]],  [[DAS Claude]],  [[DAS CLI]],  [[DAS Code]],  [[DAS Code Repository]],  [[DAS Common Testing Types]],  [[DAS Completed Roadmap]],  [[facets/DAS Decisions]],  [[DAS Design Dispatch]],  [[DAS Design Docs]],  [[DAS Design Folder]],  [[DAS Dev Dispatch]],  [[DAS Discussion]],  [[DAS Dispatch]],  [[DAS Dispatch Table]],  [[DAS Dispatch Table Design]],  [[DAS Doc]],  [[DAS Doc Structure]],  [[DAS Documentation Site]],  [[DAS Dot Anchor]],  [[DAS Facet]],  [[DAS Facets]],  [[DAS Features]],  [[DAS Files Architecture]],  [[DAS Folder]],  [[DAS Icebox]],  [[DAS Inbox]],  [[DAS Interface]],  [[DAS Log]],  [[DAS Messages]],  [[DAS Module Doc]],  [[DAS Move]],  [[DAS Naming]],  [[DAS Notebook]],  [[DAS Output]],  [[DAS Outputs]],  [[DAS PRD]],  [[DAS Primitives]],  [[DAS Proj]],  [[DAS Project Page]],  [[DAS Query]],  [[DAS Roadmap]],  [[DAS Rocks]],  [[DAS Ruleset]],  [[DAS Skill]],  [[DAS Specs]],  [[DAS Status]],  [[DAS Stories]],  [[DAS System Design]],  [[DAS Template]],  [[DAS Template Files]],  [[DAS Template Folders]],  [[DAS Template Variables]],  [[DAS Testing]],  [[DAS Track]],  [[DAS User Dispatch]],  [[DAS UX Design]],  [[DAS Versions]],  [[DAS WP]],  [[project-page]],  [[Skill Anchor/skill-config]],  [[Skill Anchor/skill-script]],  [[Skill Anchor/skill-search-rules]],  [[Skill Anchor/skill-testing]],   |

# DAS Stone
Facet spec for a **stone group** — a `{slug} Track/{slug} {Kind}s/` folder holding one file per item, ordered by a control file that a human or a machine may arrange, and propagated to downstream anchors along the `feeds:` DAG.

**TLDR** — Pebbles and rocks are the same shape of thing at two sizes, so they are one facet parameterised by **kind**, not two facets that resemble each other.

**Cardinality:** any number of kinds; at most one group per kind per anchor.

**The example is a Pebbles group on purpose** (adjudicated 2026-08-18, [[Tink327 - Every facet has a worked example, and FEX {facet} is how you reach it|F327]]). This row previously cited `HBR Rocks` and `MED Rocks` — two instances of the *same* kind, and the first of them also [[DAS Rocks]]' own example. A facet whose entire claim is *"one shape parameterised by kind"* cannot demonstrate that with two examples of one kind: they show the shape and leave the parameter untested. [[Lumen Pebbles]] is the control file of a Pebbles group, so the pair now spans both kinds, and a reader can see which parts vary with kind and which do not.

## What a stone group is

A **stone** is one unit of work-worth-naming: a **pebble** is small and nagging, a **rock** is a multi-week chunk, a **book** is one agent's or one topic's register of what is actually live. Dan, 2026-08-28, on the seam that matters: *"the rocks are things that we're going to work on, but they're not active items that are actually generating traffic. Books are generating traffic."* A rock is committed-to; a book entry is **in flight**, and the balls it throws off are what [[Sparks Mandate|Sparks]] watches. All materialise identically — a folder under the anchor's Track facet, one markdown file per stone, and a **control file** carrying the ordering.

The kinds are open-ended and declared in configuration, and **no kind is named in code**. The table below is the complete list of what ships; this sentence deliberately does not restate it, because restating it is the thing that keeps going wrong. It read *"the two that ship"* while `sleeper` was already live, and *"the three that ship"* while `book` was being added in the row beside it — the second time caught 2026-08-28, minutes after the first was written up.

| | `pebble` | `sleeper` | `rock` | `book` |
|---|---|---|---|---|
| folder | `{slug} Pebbles/` | `{slug} Sleepers/` | `{slug} Rocks/` | `{slug} Book/` |
| control file | `{slug} Pebble` | `{slug} Sleeper` | `{slug} Rock` | `{slug} Book` |
| stone file | `{slug} P0001` | `{slug} S0001` | `{slug} R0001` | `YYYY-MM-DD {Title}` |
| stone display | `{slug}:` | `{slug}:` | `{slug}:` | `{slug}:` |
| header display | `-[[…\|{slug}]]-` | `-[[…\|{slug}]]-` | `-[[…\|{slug}]]-` | `-[[…\|{slug}]]-` |

**Retired to a shipped-defaults fallback — F628, 2026-08-30.** With a `stones:` section in `~/.config/anchor-system/global.yaml` this table is **not consulted**: the config section IS the type set (`pebbles`, `rocks`, `sleepers`, `book`), each name carrying convention-derived defaults — folder `{slug} <Name>/` under Track, control file = the **folder note inside** it, prefix = the name's first letter, 4-digit numbered members — and a list exists only where an anchor's own `.anchor` `stones:` registry declares it, addressed `Anchor.rocks` (bare `Anchor` = its `_` dotless list, default `pebbles`). Design and migration record: [[Tink628 - Named stone lists replace kinds|TINK F628]]. For an install without the config section this table remains the shipped default set, and `stone` parses it. It is located by `stone_kinds_doc` in `~/.config/anchor-system/global.yaml` — the table is content, its address is configuration (Dan, 2026-08-28). Until that day the declarations lived in `facets/DAS Stone Kinds.json`, the one non-markdown file among 77 markdown facets, and this table was a hand-kept second copy of it. It had already drifted: `sleeper` shipped into the JSON while this table still said *"they are the two that ship"*, and nobody noticed. The JSON did not prevent a second copy, it created one. Deleted; the parse lives in `skills/workflow/scripts/stone-kinds.py` and `audit-plan.py` borrows it rather than copying it.

**Folder names are singular or plural by what the word names**, per [[DAS Facets]] (Dan, 2026-08-18) — singular when it names the **container**, plural when it names the **elements**. `Pebbles`, `Sleepers` and `Rocks` name the elements; `Book` names the container, which is why its folder is singular and why folder and control file resolve to the same name. **A container-named kind therefore keeps its control file INSIDE the folder, as the folder note** *(F628 widened this on 2026-08-30: EVERY list now keeps its control file as the folder note — `Lumen Pebbles/Lumen Pebbles.md` — the names-coincide rule having become the default for element-named lists too, control files renamed plural to match)* — it is the only coherent place left, and the member check already exempts a `{folder}.md` inside the folder as the group's own anchor page. *(This line previously read "folder names default to plural", which misquoted the rule — the default was never plural, it was always "whatever the word names".)* The control-file name is **configuration, not convention** — it is invisible to the mechanism, because a header is identified by what it links to rather than by what it is called.

## A stone's line fits on one Obsidian line — the budget is `stone_line_max`

**Ruled by Dan, 2026-08-30:** *"in no cases do we want them to word wrap, because it just makes it unreadable."* The rendered line — `ALIAS: ` plus the `line::` with every `[[target|shown]]` collapsed to what Obsidian shows — must fit the reading view's column. The budget is the config key `stone_line_max` in `~/.config/anchor-system/global.yaml` (this vault: **84**, measured from the Minimal theme's 40rem column at 15px ≈ 85 characters). `stone new` **refuses** a longer `--line` — the detail belongs in `--body`, which is what teaches the habit — and `stone update` **warns** per stone still over budget without blocking reconciliation. The one-time sweep of 2026-08-30 shortened 126 lines by hand; each keeps its former text in the body under *Line before the 2026-08-30 length budget*.

## A control file may be machine-maintained — a script or an agent may reorder, add and delete stones

**Ruled by Dan, 2026-08-28.** In his words: *"there can be a script which reorders and adds and deletes stones. And I think the agent can also do that. So all of the above is allowed."*

This facet previously described the control file as *hand-arranged* in three places, including its own `description::`. That wording was never a constraint anyone chose — it described the only two kinds that existed, both of which a human ranks. Read as a rule it would have refused a whole class of legitimate group: one whose ordering is **derivable**, such as a chronological register sorted by the date it presses.

**Three things are now explicitly legal**, and the distinction between them does not matter to the mechanism:

- a human arranging the control file by hand, as [[Lumen Pebbles]] and the rock groups do;
- an **agent** rewriting it as part of its own work;
- a **script** regenerating it wholesale on a schedule.

**Nothing about the file format changes**, and that is the point. A generated control file is the same file — the same header line, the same `[[{slug} P0001|{slug}:]]` stone lines, the same `feeds:` propagation. Identity still comes from the link target (`R-stone-04`), never from who typed it. So a group may switch between hand and machine arrangement, in either direction, with no migration.

**What this does NOT license.** A generated control file still may not invent an ordering the source does not carry: if the sort key is a date, the file is sorted by date and nothing else, so a reader can reconstruct it. And the merged `{node} Stones.md` at a feed node was already generated before this ruling — the precedent was half-established; this completes it rather than opening a door.

**The graph-sizing rule is a different rule and is untouched.** [[Stones]] says *"create a stone group only when you are willing to sit down and rank that anchor's work against itself."* That governs **how many hand-kept surfaces the graph should have**, not what a stone is. Reading it as an object-model constraint is what briefly disqualified [[Traffic]] from being a stone node on 2026-08-28; [[Sonar|Sonar]] published that argument and withdrew it the same day. A group whose order is derived costs a human nothing to keep, so the sizing rule does not bear on it at all.

## The one idea everything else follows from

**A control-file line is simultaneously a human's ordering decision and a machine's reference.** It opens with a link whose *target* is a numbered stone file and whose *display* is a short provenance label:

    [[Vector R0001|VEC:]] decide Aria

which reads `VEC: decide Aria`. Because the display carries the source anchor, that exact line can be pasted into any downstream anchor's control file and still reads correctly *and* still resolves to the original stone. **Propagation is therefore line-copying rather than rendering**, which is what lets a downstream control file stay hand-editable instead of becoming a generated block nobody may touch.

## Who edits what

This inverts the usual split, and the inversion is the point:

- **Agents** create, edit and delete **stone files**. They do not normally touch a control file.
- **The user** arranges **control files** — order, grouping, what is published.
- **`stone`** keeps the two consistent and propagates along the feed DAG.

**When an agent does need to change the order, the verb is `stone move <Anchor[.list]> <ID>`, never an edit** (T602, 2026-08-28). `new` always mints at the top and `update` reconciles rather than reorders, so a stone that belonged *behind* existing work had no route but hand-editing a machine-maintained file — the one thing this tool exists to prevent. Hit live on `AUP Pebble.md`, where `P0003` minted above `P0001`. `move <ANCHOR> <ID> --after|--before <ID> | --to-top | --to-bottom` rewrites the line order in place and travels only within the stone's own **run** of lines: a move that would carry it across a header is refused, because that changes which source the stone is filed under rather than its rank. Guard: case U in `test-f313-stone.py`, which also pins that the next `update` leaves a hand-chosen order alone.

## A backlog row deferred on a stone is linked from that stone's roadmap

**Interim convention, Dan 2026-08-13 — it exists because a backlog row cannot currently block on a stone.** `audit-q` **C55** resolves a `[Blocked <handle>]` against backlog rows only, so `[Blocked TINK-P0004]` is refused as a dangling handle even when the pebble is exactly what the row waits on.

Until that changes, when work is deferred because a stone has to happen first:

1. **Park the feature in `## Later`.** The bracket stops driving the frontier there, so pick the honest one rather than contorting to satisfy a checker.
2. **Add it to the stone's `## Roadmap`, in the same edit.** The stone body carries a table of the feature documents its work needs. That table is the *only* thing keeping a parked row reachable, so a row in Later with no entry there is lost rather than deferred — which is precisely the failure [[DAS Backlog]] § The four classes warns about for a blocker with no handle.

**Parking a row does hide it — but for two months it did not, and the wording here was briefly rewritten to match the bug.** Step 1's original claim (*"a Later row renders in no queue whatever its bracket"*) is the design and is now true again. Between 2026-06-04 and 2026-08-19 `audit_q.renders_in_body` admitted `Questions`, `Verify*` and `Blocked …` from `## Later`, so parking bought reachability without invisibility; measured on TINK, 62 rows parked across nine pebbles left `## Now` and `## Next` empty while the queries render still enumerated 47 of them. Dan caught it from the symptom — *"if they didn't disappear, it feels like something's wrong with that script"* — and the predicate was restored. Full provenance: [[DAS Query]] § *A `## Later` row renders nowhere*; the row that found it, [[Tink Backlog#^T548|T548]].

**Nothing a stone parks is lost.** Every parked row is counted in the banner's `Later N`, and a `[Blocked …]` or `[Verify]` row is counted again in `Parked N` — zone 3 is unscoped by horizon precisely so that omission from the body is not disappearance. The stone's `## Roadmap` is what makes the row *reachable* rather than merely counted, which is why step 2 is not optional.

**The intended end state is that blocking on a stone is simply allowed.** It is not built yet because it mixes the two stores: a `stone update` pass would then have to affect the backlog, and that coupling needs designing before it ships rather than after.

## Headers, and how publishing works

A **header** is any line whose first link targets a control file. Pointing at *this* file's own control file makes it the **self-section**; pointing at another anchor's makes it that anchor's **import site**. An anchor publishes a stone by placing its line **below the self-section**.

Each downstream anchor chooses where imports land by writing a header for the source: a bare header takes block form, a header followed by a plain-text colon takes inline comma-separated form, and an absent header means the top of the file.

**The control file is an arbitrary document; the engine only inserts.** Its one requirement is that it links every stone. A line that is missing is inserted — directly under a `## New` header if the file has one (any level; that is how you steer new lines away from the top), else at the top of the content past frontmatter and a leading H1 — and nothing else in the file is touched: no packing, no blank-line stripping, no H1 removal. Whether the member is numbered or dated has no bearing on placement. The file can be a bare list or a full page with prose and a dispatch table; the user moves the lines wherever they belong. (Dan, 2026-08-29 — [[Tink618 - Teach the stone engine to read date-named members|TINK T618]].)

## Placement — one stone on someone else's list, by a deliberate act

**`feeds:` is aggregation; placement is enrollment, and they are different relationships.** Aggregation says *this list is the sum of those lists* — structural, total, implicit, right for a [[HUD]]-style overview, where a miss costs a less complete view. Enrollment says *this one stone is also on that list* — one deliberate act, with a receipt, right for a watch that must not be missed, where a miss means **a deadline passes**. The test: *does a missing item merely look incomplete, or does something in the world go unwatched?*

    stone push Sonar P0007 --to Sparks
    SONAR P0007 -> SPARKS Pebble   (due:: 2026-09-02 15:00, done:: the materials are in the recruiter's inbox, importance:: high)

    stone recall Sonar P0007 --from Sparks
    SONAR P0007 <- SPARKS Pebble   line removed

**Why an act and not a filter.** The first proposal was a predicate on the feed — `feeds: SONAR where due` — so a pebble carrying `due::` routed to Sparks by itself. Dan rejected it (2026-08-29, [[Tink626 - Stone placement an explicit push verb, so enrolling a watch cannot|TINK T626]]): *"now Sonar can think that she alerted Sparks, but she didn't, because she didn't get it right. It didn't parse right. It didn't go through."* Silent success is the worst failure available here — nobody is positioned to notice until the deadline. An omission (forgetting to push) is visible to the agent committing it; a parse failure is visible to no one. Failures you can see beat failures you cannot.

**Four parts, all mechanical.** *The receipt* — `push` prints what happened, not that it happened. *Validation at the act* — a receiving anchor declares `accepts: due, done, importance` in its `.anchor`, and a push of a stone missing any of those keys is refused there, naming the key, to the agent that can still fix it; that is [[ASTR Comms]] § The handoff contract made mechanical — *what outcome counts as done*, *when it decays*, *how important it is*. What to do if it does not land is deliberately **not** a key: Dan ruled the same day (§ Picking a rung, take two) that the rung is Sparks's to choose, not the owner's, so the engine asks the owner only for what the owner knows. *The sweep* — `update` warns on stderr about any live stone carrying `due::` that is enrolled with nobody, so the forgotten push is caught by the pass rather than by the one agent least likely to look. *The exit* — `recall` un-enrolls and removes the line; archiving the stone withdraws it too.

**How it is kept.** The stone records `enrolled:: SPARKS` ([[DAS Stone Keys]]), and `update` treats an enrolled stone as desired on that list regardless of `feeds:` — where a merely-propagated line would be swept, an enrolled one stays, and a `line::` edit reaches it like any projection. Enrollment is not publication: the line lands above the target's self-header and travels no further, and a `feeds:` consumer of the owner does not receive it. `recall` on a target that also draws the stone by `feeds:` withdraws the enrollment and leaves the line, and says so.

**`push` is Dan's word for the act**; `recall` is the exit because `drop` already means *deposit* everywhere else in this system (`state drop` puts a note in an inbox), and a verb that means both directions is exactly the ambiguity the feature exists to remove.

## Keys

A stone carries `key:: value` parameters, **at the top of the file, above the prose**. Full vocabulary and the reasoning: [[DAS Stone Keys]].

## Rules

**Four of the six are `checked` and armed, since 2026-08-11.** `R-stone-01`, `-02`, `-04` and `-06` carry `check::` refs into `audit-plan.py`. **The arming that counts is [[R-anchor]]'s `include::`, not [[R-facet]]'s** — `/audit anchor` resolves `R-anchor`, which names [[R-rocks]] and now [[R-stone]] directly; `R-facet` is one of the 60 rulesets outside that closure, so adding a set to it changes nothing that runs. Both were updated, and it is worth knowing which one did the work. The four checkers are **kind-generic**: not one of them names `pebble` or `rock`. Every per-kind fact — folder name, control-file name, stone prefix, digit count, and the two display aliases — is read from the kind table in this doc, the same table `stone` reads, so a third kind needs no code written. The one place a kind is still named twice is this ruleset's `where::` glob, which lists the folder shapes to select; adding a kind means adding its folder there.

**Two of the six stay `stated`, and that is the answer rather than a delay.** `R-stone-05` asserts what *the mint refuses*, which is behaviour of the `stone` script rather than content of any document; it wants a guard test, the shape [[R-exception-discipline]]-03 already uses. `R-stone-03` forbids *deriving* a prefix from a kind's name — a claim about how a value was chosen, which no file can evidence. Forcing a `check::` onto either would buy a coverage claim and no coverage.

**The live corpus is 8 groups across 2 kinds and all 8 pass, so the corpus is not the evidence.** Rocks: `AIS` 3, `HBR` 3, `MED` 1, `VEC` 1. Pebbles: `SV` 3, `SYS` 2, `NJ` 2, `MED` 1. A ruleset that passes 100% on its first run has demonstrated nothing about whether it *can* fail — that is the vacuous-zero shape this facet was written in the middle of. The evidence is a **deliberately malformed fixture** (`t164-fire-test.py`) carrying one defect per rule beside a well-formed twin: all four rules fire on the malformed group, none fires on the clean one. The live sweep is reported separately with its coverage counts — 8 groups, 56 judgements, 0 skipped-as-not-an-instance — because "no findings" is only meaningful next to "and here is how much it looked at".

**Those counts hold under a batch sweep and under no other access path, which the sentence above did not say.** Measured 2026-08-12 after [[Atticus|Atticus]] reported zero `R-stone` verdicts on every pebble group he could reach. The two kinds are reached differently, and only one of the two is reached the way an agent actually audits its own anchor:

- **A rock group carries its own `.anchor`**, so it is a target in its own right. `--mode anchor` on the group's path fires all 24 stone judgements, and the T164 candidate-path fix in `_match_file_glob` is what lets `{anchor}/**/* Rocks/**` match from inside the folder the selector names.
- **A pebble group carries none** — `stone`'s `cmd_new` never mints one, and all 9 pebble groups in the vault confirm it. It is reachable only inside the scope of `{slug} Track/`, which *does* carry an `.anchor`. So `sub_anchor_roots` drops the whole Track folder from the owning anchor's scope, and **`--mode anchor SV` sees 11 files, zero of them a pebble.** `--mode anchor SV/SV Track` fires 18 stone judgements; `--batch SV --run` fires 12, because batch enumerates `SV Track` as an anchor in its own right. All three numbers were measured, not inferred.

So the pebble half is **armed and correct** — the facet's own reachability warning fired on the report rather than on the rules. What the measurement actually exposes is one level up and not specific to stones: **`/audit anchor <X>` is not an audit of X's tree.** It excludes every `{slug} Track/`, `{slug} Design/` and every other facet folder that carries an `.anchor`, alongside genuinely separate nested projects — 147 of them under `SV` — and nothing distinguishes the two, because a facet sub-anchor declares no trait that says it is one. An agent auditing its own anchor gets a green over the anchor page and its loose notes while its Backlog, Agenda, queries, Messages and stones were never opened. Filed as [[Tink Backlog#^T337|T337]].

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
