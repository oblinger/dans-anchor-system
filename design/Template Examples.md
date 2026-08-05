---
description: "The case corpus Stencil is derived from — a real example first, then proposed stencils, then the discussion. Every block is delimited, verbatim, and copy-pasteable."
---

# Template Examples
The working corpus for [[TINK303 - Template DSL - one pattern language for facets, templates, and sections|F303]] M1 — every template-shaped case that actually exists, and how **Stencil** would express it.

| Table of Contents                                        | what the case is for                                               |
| -------------------------------------------------------- | ------------------------------------------------------------------ |
| **[[#Stencil, entire]]**                                 | the whole language in one table — the size check                   |
| **[[#The format]]**                                      | how a case is laid out, and why the example comes first            |
| **[[#T1 — Whole Document Template]]**                    | a document with a required section skeleton                        |
| **[[#T2 — Folder Template With A Repeating Member]]**    | a directory with one-of-this and many-of-that                      |
| **[[#T3 — Floating-Depth Section]]**                     | a heading-anchored shape whose depth varies by file                |
| **[[#T4 — One Shape, Four Incompatible Spellings]]**     | reconciling records that must never be rewritten                   |
| **[[#T5 — Stencil Whose Anchor Is A Filename Pattern]]** | variables in the name; proves match and generate are one pattern   |
| **[[#T6 — Table With Fixed Head And Variable Rows]]**    | structure below the heading level — the case most likely to be cut |
| **[[#T7 — A Facet Spec's Own Shape]]**                   | the reflexive case, and the acceptance test                        |
| **[[#Cases still to be identified]]**                    | what has not been examined yet                                     |

## Stencil, entire

| construct | reads as |
| --- | --- |
| `{{NAME}}` | a variable — binds when matching, is filled when generating |
| `# ... LOG` | anchor: a heading matching `LOG` at **this depth or deeper** |
| `# == LOG` | anchor: a heading matching `LOG` at **exactly this depth** |

Three constructs. Everything else is a **default**, and the defaults are the reason the table is this short:

| default | means | so there is no marker for |
| --- | --- | --- |
| open world | a stencil says what is present, never what is absent | "and anything else" — it was `…` and is now silence |
| exactly one | an unmarked member appears once | `[1]` |
| many-by-variable | a pattern holding a **free** variable matches once per binding | `[0+]` |
| whole document | a stencil with no anchor marker governs the whole file | a "this is a file template" marker |

*(Provenance, since the table above deliberately omits it: `{{NAME}}` is inherited from the shipped template convention; the two anchor forms were demanded by T3, where `# LOG` sits at different depths in different files; the four defaults each replaced a construct that T1 or T2 proposed and that Dan cut on 2026-08-04.)*

### Not yet decided — how far a variable reaches

Dan, 2026-08-04: *"whether or not we need something special for a variable that is in line versus a variable that is multi-line… if it's a multi-line variable, it has to be on a line by itself."* The distinction is real — a matcher has to know whether `{{one-line description}}` binds part of one line or swallows the next forty — but **position alone does not draw it**, and T1.A is the counterexample: `{{one-line description}}` sits alone on its line and is a one-liner, while `{{dispatch table}}` sits alone on its line and is genuinely several.

| option | rule | cost |
| --- | --- | --- |
| **(A)** no construct | a variable reaches until the next **literal** the stencil names — `# ` and ` Backlog` bound `{{slug}}` to part of a line; a blank line bounds `{{one-line description}}` to what precedes it; nothing after a variable means it reaches to the end of its section | cannot *require* one-line-ness; two adjacent unbounded variables are ambiguous |
| **(B)** position declares it | alone on a line ⇒ multi-line; anything before or after ⇒ inline | disagrees with (A) almost nowhere, and where it does it gives the same answer; buys a declared property at the cost of a rule to remember |

**Lean (A)**, for the same reason cardinality became a default: extent is a *consequence* of what surrounds the variable, exactly as multiplicity is a consequence of whether it is free. It also keeps the escape hatch where Dan put it — if a stencil must insist a value is exactly one line, that is a **constraint on a bound variable** and belongs in the rules layer, not in the grammar.

**The one shape ambiguous under both** is two unbounded variables adjacent with no literal between them. No case in the corpus does this; when one appears, the answer is likely *"that stencil is malformed"* — a checkable defect, like two stencils claiming one anchor — rather than a new construct.

**A separate thing this question surfaced.** `{{dispatch table}}` is not really a variable awaiting a value; it is a placeholder for **a sub-shape governed by another stencil**. That is a different construct from `{{NAME}}` — a nested reference rather than a hole — and it is the question [[#T6 — Table With Fixed Head And Variable Rows|T6]] has to answer. Naming it here so it is not silently absorbed into the variable construct.

## The format

### Format Examples

| line | what it is |
| --- | --- |
| `# T3 — Floating-Depth Section` | a **case** — H1, named; `T3` is only a handle so proposals can be cited |
| `**Example T3.a** — ``AT/Corp/@Northwind/@Robin Calder.md`` | an **example label** — lowercase letter, path of the real file it came from |
| `<!-- begin example T3.a -->` | opens a **block**; everything to the matching end marker is byte-exact |
| `**Proposal T3.A** — ``AT/_LOG Template.md`` | a **proposal label** — uppercase letter, path the stencil file would have |
| `## T3 Overview` | the **discussion** — always last in the case, never between the artifacts |

### Format Rules

These govern *this document*, not Stencil. Stencil's own rules are the two tables above.

- **Ground truth first** — a case reads example → proposal(s) → discussion. The example is fixed and comes first; the proposal is the thing under test; nothing anyone wants to *say* sits between them.
- **Blocks are byte-exact** — between the markers is the file's own bytes: real heading depths, no shifting, no annotation, no dates.
- **Labels carry paths** — outside the block, so the block stays byte-exact. A path is literal, curly braces included: `templates/log/{{YYYY-MM-DD}} — {{short topic}}.md` is a real file whose real name on disk contains those braces.
- **Every case cites a real file** — a shape with no vault instance is not admitted, so a hypothetical can never justify a construct.
- **Each case names its direction** — *match*, *generate*, or *both* — in its Overview.

Two accepted costs of verbatim-and-unfenced: specimen headings are real headings and show up in this document's outline, and specimen wiki-links are live — so this file needs excluding from link-resolution and doc-structure rules the way `_* Template` files already are.

**Status.** Language cut to three constructs 2026-08-04 on Dan's objections; seven cases identified; T1–T3 worked through, T4–T7 carrying their real instances and awaiting proposals.

---

# T1 — Whole Document Template

**Example T1.a** — `SYS/Staff/Hermes/HERMES Track/HERMES Backlog.md`

<!-- begin example T1.a -->
# HERMES Backlog
<!-- state:backlog 6h -->
The work queue for [[HERMES|Hermes]], the purchasing agent — content curated is [[BUY]].

| -[[HERMES Backlog]]- | → [[kmr]] → [[SYS]] → [[Staff]] → [[HERMES]] → [[HERMES Track]] → [HERMES Backlog](hook://p/HERMES%20Backlog)  |
| --- | --- |
| ... | [[HERMES Messages]],   |

## Ready

## Notes

## Next

## Later

## Now

- **T001 — Build your Mandate** [Ready] — **From [[LUMEN|Lumen]].** Raw material for your own mandate. ^T001
  - **Next:** Read this against [[Tink]]'s view of agent specification, then write `HERMES Mandate.md` modelled on [[PROS Mandate]].
<!-- end example T1.a -->

**Proposal T1.A** — `templates/backlog.md`

<!-- begin proposal T1.A -->
# {{slug}} Backlog
{{one-line description}}

{{dispatch table}}

## Ready

## Notes

## Next

## Later

## Now
<!-- end proposal T1.A -->

## T1 Overview

The most common case: a facet whose instance is one document with a required section skeleton. `templates/backlog.md` governs every `{slug} Backlog.md` in the vault — forty-odd of them — so T1.A is not a new file, it is what that shipped template *becomes* under Stencil, which makes it the first concrete piece of M5.

**Direction: both.** Generate — a new anchor's Backlog is instantiated from it. Match — `R-backlog` checks every existing Backlog against it.

**What the case demands.** A whole-document anchor; a variable in the title; a required sequence of H2 sections whose *contents* other rules govern entirely. T1.a shows why the last part matters: its `## Now` holds a row no template should attempt to describe.

**The `…` marker is gone, and this proposal is the argument for cutting it.** An earlier draft put a `…` under every heading to mean "and I say nothing about what is beneath." Dan, 2026-08-04: *"It feels like you're gonna have to put dot dot dot everywhere… I just wonder if that isn't like the default of what a template is."* It is. A stencil states what is present and never claims completeness, so open-world is the default and the marker was noise on every line. What is now lost is the ability to say **"only these and nothing else"** — a genuinely stronger claim, no case has yet needed it, and it gets a marker when one does.

**Open in T1.A.** `{{dispatch table}}` stands in for a whole sub-shape — that is [[#T6 — Table With Fixed Head And Variable Rows|T6]], and whether it resolves to a nested stencil reference or stays an opaque variable is T6's question. Section *order* is also unstated: T1.a carries `Ready / Notes / Next / Later / Now` while `templates/backlog.md` lists a different order, so either order is not load-bearing or the corpus is already non-conforming — a real finding either way, surfaced only because the example is verbatim. Example taken 2026-08-04.

---

# T2 — Folder Template With A Repeating Member

**Example T2.a** — `templates/log/`

```
templates/log/
├── {slug} Log.md
└── {{YYYY-MM-DD}} — {{short topic}}.md
```

**Example T2.b** — `templates/log/{{YYYY-MM-DD}} — {{short topic}}.md`

<!-- begin example T2.b -->
# {{YYYY-MM-DD}} — {{short topic}}

## What happened

{{per-session plan + outcome, in narrative form}}

## Decisions

- {{decision made this session, with links to the docs it landed in}}
- ...

## Outstanding
<!-- end example T2.b -->

**Proposal T2.A** — `templates/log/` *(unchanged — the shipped folder is already a valid stencil)*

```
templates/log/
├── {slug} Log.md
└── {{YYYY-MM-DD}} — {{short topic}}.md
```

## T2 Overview

**Direction: both.** Generate — instantiate a Log folder for a new anchor. Match — check an existing one.

**What the case demands: how many of each member a conforming folder holds.** Instantiating `templates/log/` for TINK should produce exactly one `TINK Log.md` and any number of dated entry files, including none.

**The answer turned out to be "nothing" — and T2.A is the shipped folder, untouched.** Three earlier proposals put a count somewhere: a `_manifest.md` file, a `[0+]` prefix in the member's filename, and a `[0+]` line inside the member. Dan cut all three on two objections, 2026-08-04. First: *"I wonder about the need for cardinality exactly one. Isn't that the expected if you don't say anything?"* — yes, so `[1]` was never needed. Second, on the filename form: *"you would just use curly braces, and then in the constraints on the system, it would indicate an arbitrary constraint… I don't think we're going to have enough to be able to constrain strings using 0 or more."*

Following that through gives the **many-by-variable** default. `{slug} Log.md` holds a variable the anchor binds once, so it names exactly one file. `{{YYYY-MM-DD}} — {{short topic}}.md` holds variables nothing binds, so it matches once per binding — any number, including none. Multiplicity is a consequence of whether a variable is **free**, which is ordinary unification rather than a bolted-on quantifier.

**An earlier draft rejected a version of this as "too clever"; that was wrong and the record should say so.** The rejected form was a heuristic — *filenames that look pattern-ish are many*. This is not that: free-versus-bound is a real semantic property that a matcher computes rather than guesses.

**What is lost, stated plainly.** There is now no way to say *"exactly one file whose name varies"* or *"at least one entry."* Neither has an instance in the vault. If one appears, that is the case that earns a cardinality marker — and Dan's spelling for it is already chosen: a `+`, kept distinct inside brackets.

---

# T3 — Floating-Depth Section

**Example T3.a** — `AT/Corp/@Northwind/@Robin Calder.md`

<!-- begin example T3.a -->
# LOG
Reverse-chronological correspondence and notes with Robin Calder (Northwind champion), newest first.

## 2026-08-03 Mon  SENT — reply

To: robin@northwind.example
Subject: Thanks, Robin

Robin,

Thanks for the update, and for running a straight process throughout.

Best,
Dan
<!-- end example T3.a -->

**Proposal T3.A** — `AT/_LOG Template.md`

<!-- begin proposal T3.A -->
# ... LOG
{{one-line description}}

## {{YYYY-MM-DD}} {{DAY}}  {{DIRECTION}} — {{KIND}}
{{entry body}}
<!-- end proposal T3.A -->

**Proposal T3.B** — `AT/_LOG Template.md`

<!-- begin proposal T3.B -->
# == LOG
{{one-line description}}

## {{YYYY-MM-DD}} {{DAY}}  {{DIRECTION}} — {{KIND}}
{{entry body}}
<!-- end proposal T3.B -->

## T3 Overview

**Direction: match first.** These files exist and are not being regenerated; the value now is locating and checking the section. Generate matters later, for appending an entry in the right shape.

**What the case demands.** An **anchor** — a stencil attaching to a heading rather than to a document — with two depth modes, because `LOG` sits at H1 here and at other depths elsewhere.

**The marker follows the hashes, and that is Dan's correction.** An earlier draft wrote `…# LOG`, which is not a heading at all once rendered — just a line beginning with a dot. `# ... LOG` is a **real H1** whose text happens to start with `...`, so the stencil still renders as the thing it describes, which is the entire point of a specimen. Dan, 2026-08-04: *"if you do it the way you're showing it, it won't actually be a heading at all."*

**Why the marker cannot be defaulted away, even though every other default was.** The marker is not only a depth mode — its **presence is what makes the stencil a section anchor at all**. An unmarked `# LOG` first line would be indistinguishable from a whole-document stencil whose title happens to be LOG. So `...` and `==` both survive, and there is no third, unmarked form.

**Both proposals are the two modes side by side**, same path, same body — because the path being identical is the point: the anchor lives in the first line, not in the name. Depths after the first line are relative to the anchor, so `## {{YYYY-MM-DD}}…` means *one deeper than wherever LOG matched*. The path assumes [[TINK302 - Section templates and the scope ladder|F302]] Q4's lean; if Q4 lands the other way the file is `AT/_LOG Section Template.md` and nothing else changes.

**The entry heading needs no cardinality marker** — `{{YYYY-MM-DD}}` and friends are free, so many-by-variable already says "any number of entries." That is the same default doing the same work in T2, which is the evidence the two cases wanted one rule rather than two constructs.

**Open in T3.** The entry heading is `2026-08-03 Mon  SENT — reply` — date, weekday, direction, kind, separated by a double space and an em-dash. Whether Stencil should decompose that into four variables (as proposed) or treat the line as one opaque `{{HEADING}}` is the first place the language could over-reach: four variables is more expressive and four times more to get wrong, and only a rule ever needs the pieces.

---

# T4 — One Shape, Four Incompatible Spellings

## T4 Overview

**Real instances.** The email block inside [[AT]] log entries, in four mutually-incompatible forms across two files — bold field labels (`EMAILS:` then `**From:**` / `**Date:**` / `**To:**` / `**Subject:**`) in `@Alex Trenton.md`; a dashed header line and a dashed draft line in `@Robin Calder.md`; and a tilde fence with bare `From Alex` / `To Dan and Morgan` in `@Alex Trenton.md`. They share **no** common marker. Example T3.a above is a *fifth* spelling — bare `To:` / `Subject:` under a dated heading.

**Direction: match and reconcile only.** [[TINK302 - Section templates and the scope ladder|F302]] resolved that existing log entries are **never rewritten** — a log entry records a message actually sent, and normalizing one edits the record rather than the format. So Stencil must express the agreed shape and then answer *"is this old entry reconcilable with it?"*, which is weaker than *"does this match?"*.

**What the case demands.** Possibly nothing new, and that is worth testing: if Stencil expresses the target shape and the matcher reports **which parts bound and which did not**, reconcilability is a predicate over that result and stays out of the grammar. If it cannot be kept out, this is the case that proves the language needs a partial-match notion — a large addition, and one to resist.

*(Examples and proposals — to be written.)*

---

# T5 — Stencil Whose Anchor Is A Filename Pattern

## T5 Overview

**Real instance.** `_{{PURCHASE_DATE}} {{HOSTNAME}} Template.md` — a file template whose *name* carries the variables, so the pattern governs which files are members of the folder as well as what is inside them.

**Direction: generate first** (clone → rename → fill is its documented primary use), but match is what makes it a template rather than a snippet.

**What the case demands.** That an anchor can be a **filename** pattern, and that variables bound from the filename are in scope for the body. This is the case that proves the two directions are one pattern: the same `{{PURCHASE_DATE}}` is *read from* the name when matching and *written into* it when generating. It is also where the many-by-variable default gets its second test — those variables are free, so the pattern names a set of files, which is exactly right.

*(Examples and proposals — to be written.)*

---

# T6 — Table With Fixed Head And Variable Rows

## T6 Overview

**Real instances.** The dispatch table at the top of every anchor page — see [[DAS Dispatch Table]]; Example T1.a contains a live one. A fixed identity row, then a variable number of labelled rows drawn from a known vocabulary.

**Direction: both.**

**What the case demands.** Structure *below* the heading level — rows within a table — where the anchor construct does not reach. This is the case most likely to push Stencil further than it should go, and therefore the one to design last and cut first. `/audit dispatch` already generates these from a spec; if Stencil cannot express it cleanly, **that is an acceptable answer** and T1.A's opaque `{{dispatch table}}` stands.

*(Examples and proposals — to be written.)*

---

# T7 — A Facet Spec's Own Shape

## T7 Overview

**Real instance.** `facets/DAS Facet.md` states the shape every facet spec doc takes — H1, one-line summary, dispatch table, document-structure outline, the `# RULESET R-<facet>` block, the `# BRIEF` block. That prose *is* a stencil, written as a bullet list because there was no notation for it.

**Direction: both**, and it is the reflexive case — Stencil describing the documents that define Stencil's own vocabulary.

**What the case demands.** Nothing new, if T1–T3 land. Its value is as the **acceptance test** — if Stencil cannot restate `DAS Facet`'s document-structure list without loss, it is not yet expressive enough for the corpus it governs. It is also the first case likely to want the closed-world marker T1 cut, since a facet spec's section list reads as exhaustive.

*(Examples and proposals — to be written.)*

---

# Cases still to be identified

Collected in one pass and certainly incomplete. Candidates not yet examined: the `{slug} Track/` folder shape, study-card files, and the `.anchor` file itself — that last one out of scope until the markdown-first decision is revisited. The `## Open Questions` two-zone block is deliberately **not** a candidate: it is machine-maintained by `state`, and a stencil for it would be a second authority over bytes that already have one.
