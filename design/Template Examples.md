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

**Confirmed live 2026-08-05, and the exclusion list is longer than expected.** Authoring T5 tripped `R-progressive-05` (summary-freshness): its specimen `## Identity` / `## Hardware` were counted as two new *document* sections, so every case authored here will report the summary stale by construction. That rule is `where:: always` and advisory-only, so it cannot be excluded by a `where::` glob the way the doc-structure rules can — whatever mechanism carries the exclusion has to reach it too. Recorded here rather than filed, because it is a property of this document's format that M1 has to live with until [[TINK303 - Template DSL - one pattern language for facets, templates, and sections|F303]] M6 decides how Stencil-bearing files declare themselves to Warden.

**Status.** Language cut to three constructs 2026-08-04 on Dan's objections; seven cases identified. **T1–T3, T5 and T7 worked through; T4 and T6 carry their real instances and await examples and proposals.** Three findings so far, all of them the M1 gate doing its job rather than incidental: T5 added nothing to the language (it looked like it needed a filename anchor and turned out to be a T2 member); T5 was citing a gallery exemplar rather than a vault instance, which the Format Rules above forbid; and **T7, the acceptance test, passes** — a facet spec restates in one construct and three defaults, and the closed-world marker it was predicted to demand is refuted by the corpus instead.

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

**Example T5.a** — `SYS/SYS Catalog/Computer/_Computer {{NICKNAME}} Template.md`, abridged

<!-- begin example T5.a -->
---
kind: computer
---
# Computer {{NICKNAME}}

> **{{One-line role}}.** What this machine is for in the fleet (primary working machine / disk station / VM host / etc.).

## Identity

- **Hostname (mDNS):** `{{HOSTNAME}}.local`
- **Hostname (terminal):** `{{HOSTNAME}}`
- **My nickname / short reference:** {{NICKNAME}}{{, phonetic hint if non-obvious — delete otherwise}}

## Hardware

- **Model:** {{Model Name + year, e.g. "MacBook Pro 16" 2019" or "Mac mini M2 Pro 2023"}}
- **RAM:** {{GB}}

✂ ──── template notes ──── ✂

- **`{{NICKNAME}}`** — what you call the machine in conversation (e.g. `haorui`). Fills the **filename** (`Computer {{NICKNAME}}.md`), the **H1**, and the nickname line.
- **`{{HOSTNAME}}`** — the machine's actual hostname (e.g. `haorui`). Fills both **Identity** hostname lines and the **SSH** command. Often equals the nickname; they diverge when the nickname is a phrase (e.g. "Daniel MacBook Pro").

NOTES:
- **Filename:** strip the leading `_` and trailing ` Template` → `Computer {{NICKNAME}}.md`, matching the existing instances.
<!-- end example T5.a -->

**Example T5.b** — the two live members of that folder, which is what makes the filename pattern load-bearing rather than decorative:

- `SYS/SYS Catalog/Computer/Computer haorui.md` — binds `NICKNAME = haorui`
- `SYS/SYS Catalog/Computer/Computer Daniel MacBook Pro.md` — binds `NICKNAME = Daniel MacBook Pro`

The second is the one that earns its place. Its nickname is a **phrase containing spaces**, so a filename pattern has to bind a greedy variable between two literals rather than a single token — and it is the instance where `NICKNAME` and `HOSTNAME` genuinely diverge, which is exactly the divergence the template's own notes call out.

**Proposal T5.A** — the folder, in T2's form

```
SYS/SYS Catalog/Computer/
└── Computer {{NICKNAME}}.md
```

**Proposal T5.B** — `SYS/SYS Catalog/Computer/Computer {{NICKNAME}}.md`, the member

<!-- begin proposal T5.B -->
# Computer {{NICKNAME}}
{{role — one line}}

## Identity

- **Hostname (mDNS):** `{{HOSTNAME}}.local`
- **Hostname (terminal):** `{{HOSTNAME}}`
- **My nickname / short reference:** {{NICKNAME}}

## Hardware
<!-- end proposal T5.B -->

## T5 Overview

**Real instance corrected 2026-08-05.** This case previously cited `_{{PURCHASE_DATE}} {{HOSTNAME}} Template.md`, which lives in `examples/FEX Templates/` — a **constructed exemplar in the example gallery, not a vault instance**. That breaks this document's own rule (*"Never a hypothetical; a case with no instance in the vault is not yet a case"*), and it is worth recording rather than quietly swapping, because the exemplar is the weaker specimen in the way that matters: its `{{HOSTNAME}}` appears in the filename *and* the H1, so it cannot show a variable that is bound from the name but used only in the body. The real corpus has **27** filename-pattern templates; `Computer` was chosen because it is the one whose own notes already state the filename rule in prose.

**Direction: generate first** (clone → rename → fill is its documented primary use), but match is what makes it a template rather than a snippet.

**What the case demands.**

1. **Nothing at the filename level — and that is the finding.** The first draft of T5.A invented a `file::` anchor, a fourth construct beside the two heading anchors. It is not needed: [[#T2 — Folder Template With A Repeating Member|T2]] already expresses member filenames as *the member's name in the folder tree*, so `Computer {{NICKNAME}}.md` is a T2 member, not a new kind of thing. **The language does not grow here.** Recorded rather than silently corrected, because M1's whole job is deciding whether Stencil is small, and a case that looked like it demanded a construct and then did not is evidence for the same conclusion as a case that never did.
2. **Variables bound from the name are in scope for the body — this is what T5 actually demands.** `{{NICKNAME}}` binds from the filename in T5.a and is then *used* in the H1 and the nickname line. This is the case that proves the two directions are one pattern: the same variable is **read from** the name when matching and **written into** it when generating. It is also a **scope** claim T2 never had to make — T2's `{{YYYY-MM-DD}}` binds in the filename and is used again in the member's H1, but nothing there distinguishes "the same variable" from "two variables that happen to share a name." T5.a settles it: its template documents `{{NICKNAME}}` as filling the filename *and* the H1 *and* the nickname line, so a binding is per-member and shared across the member's artifacts.
3. **A variable that appears only in the body.** `{{HOSTNAME}}` is free — the pattern says nothing about it at the name level. So a filename pattern does not have to bind every variable, and T5.b shows why: the two live members disagree about whether hostname and nickname are the same string.
4. **Greedy binding between literals.** `Computer Daniel MacBook Pro.md` binds `NICKNAME` to a phrase with spaces. A tokenizing match would bind `Daniel` and fail; a filename pattern must bind maximally between its literal parts.

**What it does NOT demand, and this is the useful negative.** The `_` prefix and the ` Template` suffix are **not** part of the notation. T5.a's own notes describe the transform in prose — *"strip the leading `_` and trailing ` Template`"* — but that is a fact about where the template FILE is parked so it does not itself look like a member, not a fact about the pattern. Under T5.A the pattern is stated directly and positively as `Computer {{NICKNAME}}.md`, and the parking convention stays where it belongs, in [[DAS Template Files]]. **Resist folding it in:** a notation that derives the member name by string-surgery on the template's own name cannot express a template parked anywhere else, and there are already 27 of these to be wrong about.

**Second test of the many-by-variable default.** `NICKNAME` is free, so `Computer {{NICKNAME}}.md` names a *set* of files — every member of the folder — rather than one. That is the right reading, and it is the same default T1 established for repeated headings, arriving here at a different scope. Examples taken 2026-08-05.

---

# T6 — Table With Fixed Head And Variable Rows

## T6 Overview

**Real instances.** The dispatch table at the top of every anchor page — see [[DAS Dispatch Table]]; Example T1.a contains a live one. A fixed identity row, then a variable number of labelled rows drawn from a known vocabulary.

**Direction: both.**

**What the case demands.** Structure *below* the heading level — rows within a table — where the anchor construct does not reach. This is the case most likely to push Stencil further than it should go, and therefore the one to design last and cut first. `/audit dispatch` already generates these from a spec; if Stencil cannot express it cleanly, **that is an acceptable answer** and T1.A's opaque `{{dispatch table}}` stands.

*(Examples and proposals — to be written.)*

---

# T7 — A Facet Spec's Own Shape

**Example T7.a** — `facets/DAS Facet.md`, its `# Facet Document Structure` section verbatim

<!-- begin example T7.a -->
- **H1** — `# DAS <Name>`: the slug-name and the full name.
- **One-line summary** — a single sentence on the line directly under the H1 (no blank line between).
- **Dispatch table** — the breadcrumb row, then `Related` (lateral links only) and `Examples`.
- **Document structure** — this dense outline, placed first so a reader sees the doc's shape before any prose.
- **Overview** — a short paragraph: what the facet is and what it's for. *(Optional.)*
- **The Aspect contract** — content the body usefully conveys, mostly via the ruleset (section shapes vary; **not** fixed H2s; all optional).
- **`# RULESET R-<facet>`** — **REQUIRED.** The embedded ruleset.
- **`# BRIEF`** — **REQUIRED.** Agent-facing documentation.
<!-- end example T7.a -->

**Example T7.b** — the shape those bullets describe, as it actually appears in `facets/DAS Facet.md` itself

<!-- begin example T7.b -->
# DAS Facet
A facet is a named, recurring document/folder kind — this page is the spec for the spec docs that define them.

| -[[DAS Facet]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[facets\|FCT]] → [DAS Facet](hook://p/DAS%20Facet)  |
| --- | --- |
| Related | [[DAS Facets]],   |

# Facet Document Structure

# Facet Overview

# RULESET R-facet-spec

# BRIEF
<!-- end example T7.b -->

**Proposal T7.A** — `facets/{{FACET_NAME}}.md`

<!-- begin proposal T7.A -->
# DAS {{FACET_NAME}}
{{one-line summary}}

{{dispatch table}}

# {{FACET_NAME}} Document Structure

# RULESET R-{{facet-slug}}

# BRIEF
<!-- end proposal T7.A -->

## T7 Overview

**Real instance.** `facets/DAS Facet.md` states the shape every facet spec doc takes, as a bullet list, because there was no notation for it. That prose *is* a stencil. T7.a is the prose; T7.b is the shape it describes, present in the same file — which is what makes this the reflexive case rather than merely a self-referential joke.

**Direction: both**, and it is Stencil describing the documents that define Stencil's own vocabulary.

**What the case demands: nothing new — and T1–T3 already carry it.** T7.A uses one construct (`{{NAME}}`) and three defaults (open world, exactly one, whole document). No anchor marker: a facet spec is a whole file, which is T1's case at a different scope. **This is the acceptance test passing.** Had T7.A needed a construct T1–T3 did not supply, Stencil would not yet be expressive enough for the corpus that defines it.

**But it does NOT restate T7.a without loss, and the loss is the interesting part.** Three things the bullet list says that T7.A cannot:

1. **Which members are REQUIRED.** T7.a marks `# RULESET` and `# BRIEF` **REQUIRED** and `Overview` *(Optional.)*. Under the open-world default a stencil states what is present and never claims completeness, so T7.A asserts *these appear* and cannot assert *these must*. **That is correct and should stay correct** — required-ness is a constraint on a conforming document, which is the rules layer's job, and `R-facet-spec` already carries it. The bullet list is doing two jobs at once; Stencil should only take the shape half.
2. **The no-blank-line rule** between H1 and summary. A byte-level adjacency constraint, not a shape. Also rules-layer, and `R-progressive-03` already owns it.
3. **The dispatch table's internal shape.** `{{dispatch table}}` is opaque here for the same reason it is opaque in T1.A — that is [[#T6 — Table With Fixed Head And Variable Rows|T6]]'s question, and T7 inherits whatever T6 answers rather than re-asking.

**The closed-world marker, predicted here and NOT demanded after all.** The overview written before this pass expected T7 to be *"the first case likely to want the closed-world marker T1 cut, since a facet spec's section list reads as exhaustive."* Reading T7.a against the corpus refutes it: `DAS Facet.md` itself carries `# Examples of a facet — project instances vs standalone FEX artifacts`, an H1 the list never mentions. The list is **not** exhaustive even of the file that states it, so the open-world default is not merely tolerable here — it is the accurate reading, and the prediction was wrong. Recorded because a construct nearly earned its way in on an intuition the corpus then contradicted. Examples taken 2026-08-05.

---

# Cases still to be identified

Collected in one pass and certainly incomplete. Candidates not yet examined: the `{slug} Track/` folder shape, study-card files, and the `.anchor` file itself — that last one out of scope until the markdown-first decision is revisited. The `## Open Questions` two-zone block is deliberately **not** a candidate: it is machine-maintained by `state`, and a stencil for it would be a second authority over bytes that already have one.
