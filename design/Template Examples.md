---
description: "The case corpus Stencil is derived from — a real example first, then proposed stencils, then the discussion. Every block is delimited, verbatim, and copy-pasteable."
---

# Template Examples
The working corpus for [[TINK303 - Template DSL - one pattern language for facets, templates, and sections|F303]] M1 — every template-shaped case that actually exists, and how **Stencil** would express it.

| Table of Contents | what the case is for |
|---|---|
| **[[#The format]]** | how a case is laid out, and why the example comes first |
| **[[#Constructs proposed so far]]** | the whole proposed language in one table — the size check |
| **[[#T1 — Whole Document Template]]** | a document with a required section skeleton; introduces open-world `…` |
| **[[#T2 — Folder Template With A Repeating Member]]** | a directory with one-of-this and many-of-that; introduces cardinality |
| **[[#T3 — Floating-Depth Section]]** | a heading-anchored shape whose depth varies by file |
| **[[#T4 — One Shape, Four Incompatible Spellings]]** | reconciling records that must never be rewritten |
| **[[#T5 — Stencil Whose Anchor Is A Filename Pattern]]** | variables in the name; proves match and generate are one pattern |
| **[[#T6 — Table With Fixed Head And Variable Rows]]** | structure below the heading level — the case most likely to be cut |
| **[[#T7 — A Facet Spec's Own Shape]]** | the reflexive case, and the acceptance test |
| **[[#Cases still to be identified]]** | what has not been examined yet |

## The format

Each case is an H1 and reads top to bottom as **example → proposal(s) → discussion**. The example is ground truth and comes first; the proposal is the thing under test; everything anyone wants to *say* about either lives in the `## {case} Overview` H2 at the bottom of the case, so the artifacts stay clean and the argument stays out of them.

**Every block is delimited and byte-exact.** A block opens with a bold label and an HTML begin-marker, closes with an end-marker, and contains **nothing but the file's own bytes** — real heading depths, no shifting, no annotation, no dates. The markers are invisible when rendered and unambiguous in source, which is where you copy from.

**Every label names a path.** An example's label gives the path of the real file it was taken from; a proposal's label gives the path of the stencil file it would *be*. The path sits on the label line rather than inside the block, so the block stays byte-exact.

**A path is literal, curly braces included.** `templates/log/{{YYYY-MM-DD}} — {{short topic}}.md` is a real file whose real name on disk contains those braces. These are not sketches of a stencil; they are the stencil.

Examples are lettered lowercase (`T3.a`), proposals uppercase (`T3.A`).

**Every case cites a real file.** A shape with no instance in the vault is not admitted — Stencil is defined from demonstrated need, so a plausible hypothetical must never justify a construct.

**Each case declares the direction it needs** — *match*, *generate*, or *both* — in its Overview. This is what will expose where the two directions genuinely diverge rather than merely look different.

**Two consequences of verbatim-and-unfenced, both accepted deliberately.** Specimen headings are real headings, so they appear in this document's outline — the price of specimens that can be copied, in a notation where heading depth is semantic. And specimen wiki-links are live, so this file must be excluded from link-resolution and doc-structure rules the way `_* Template` files already are. If the outline noise ever becomes intolerable, the escape is graduating specimens to sibling files and leaving the markers as links; the block boundaries are already file-shaped, so that migration is mechanical.

**Status.** Format settled 2026-08-04 to Dan's shape; seven cases identified; T1–T3 worked through, T4–T7 carrying their real instances and awaiting proposals. When Dan reads this and says the cases are covered, M1 is done and Stencil is written *from* it.

## Constructs proposed so far

Stencil does not exist yet, so every proposal below invents notation as it goes. This table is the running total — **the whole language, as currently proposed, in one glance** — and it exists so the "does it stay small?" question is answerable without reading every case. Nothing enters this table without a case that demanded it, and the case is named.

| construct | reads as | first demanded by |
|---|---|---|
| `{{NAME}}` | a variable: binds when matching, is filled when generating | inherited — the shipped template convention |
| `…` on its own line | open-world: *ignore* when matching, *omit* when generating | T1 — sections that must exist but whose contents other rules govern |
| `[1]` · `[0+]` · `[1+]` | cardinality: exactly one · zero or more · one or more | T2 — a folder holding one dispatch page and any number of entries |
| `…#` prefixing a heading | anchor at *this depth or deeper* | T3 — `# LOG` sits at different depths in different files |
| `=#` prefixing a heading | anchor at *exactly this depth* | T3 — the contrast case for the above |

Five constructs across three cases. Two observations already: `[0+]` was introduced for a folder's members and reused unchanged for a section's repeated headings, which is evidence the two want **one** construct rather than two; and every construct so far is a *quantifier or a wildcard*, none is a predicate — which is the line [[TINK303 - Template DSL - one pattern language for facets, templates, and sections|F303]] draws between Stencil and the rules that constrain what it binds.

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
…

## Notes
…

## Next
…

## Later
…

## Now
…
<!-- end proposal T1.A -->

## T1 Overview

The most common case: a facet whose instance is one document with a required section skeleton. `templates/backlog.md` governs every `{slug} Backlog.md` in the vault — forty-odd of them — so T1.A is not a new file, it is what that shipped template *becomes* under Stencil, which makes it the first concrete piece of M5.

**Direction: both.** Generate — a new anchor's Backlog is instantiated from it. Match — `R-backlog` checks every existing Backlog against it.

**What the case demands.** A whole-document anchor; a variable in the title; a required sequence of H2 sections; and the interesting part — those sections must *exist* while their contents are governed by other rules entirely. T1.a shows why: its `## Now` holds a row no template should attempt to describe. So the notation needs to say **"this heading, and I say nothing about what is beneath it"** — the `…` line, read as *ignore* when matching and *omit* when generating.

**Open in T1.A.** `{{dispatch table}}` is a placeholder standing in for a whole sub-shape — that is [[#T6 — Table With Fixed Head And Variable Rows|T6]], and whether it resolves as a nested stencil reference or stays an opaque variable is T6's question. Section *order* is also unstated: T1.a carries `Ready / Notes / Next / Later / Now` while `templates/backlog.md` lists a different order, so either order is not load-bearing or the corpus is already non-conforming — a real finding either way, and one this case surfaced only because the example is verbatim. Example taken 2026-08-04.

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

**Proposal T2.A** — `templates/log/_manifest.md`

<!-- begin proposal T2.A -->
[1]  {{slug}} Log.md
[0+] {{YYYY-MM-DD}} — {{short topic}}.md
<!-- end proposal T2.A -->

**Proposal T2.B** — `templates/log/[0+] {{YYYY-MM-DD}} — {{short topic}}.md`

<!-- begin proposal T2.B -->
# {{YYYY-MM-DD}} — {{short topic}}

## What happened

{{per-session plan + outcome, in narrative form}}

## Decisions

- {{decision made this session, with links to the docs it landed in}}
- ...

## Outstanding
<!-- end proposal T2.B -->

**Proposal T2.C** — `templates/log/{{YYYY-MM-DD}} — {{short topic}}.md`

<!-- begin proposal T2.C -->
[0+]
# {{YYYY-MM-DD}} — {{short topic}}

## What happened

{{per-session plan + outcome, in narrative form}}

## Decisions

- {{decision made this session, with links to the docs it landed in}}
- ...

## Outstanding
<!-- end proposal T2.C -->

## T2 Overview

**Direction: both.** Generate — instantiate a Log folder for a new anchor. Match — check an existing one.

**What the case demands, in one sentence:** a folder template must be able to say **how many of each member** a conforming folder holds, and today it cannot.

Instantiating `templates/log/` for TINK should produce `TINK Log/` containing exactly one `TINK Log.md` and any number of dated entry files — including none. The directory listing states neither count. A reader infers them from the fact that one filename carries a date-shaped placeholder and the other does not, and **that inference is what must not be relied on**: `{slug} Log.md` also contains a variable and is nevertheless exactly-one, so "looks pattern-ish" is not the distinction. Dan, 2026-08-04: *"I want to have multiple, 0 or more of these or one or more of these, those kinds of things in there."*

**Why not derive it instead of marking it?** A tempting rule: a member whose filename varies *per member* (`{{YYYY-MM-DD}}`) is many, while one whose variables are all fixed by the anchor (`{slug}`) is exactly one. That is a genuine semantic distinction rather than a heuristic, and it would need no marker at all — but it breaks on any case wanting exactly one file whose name varies, and it makes cardinality a consequence of variable scoping rather than something an author can state. Rejected as too clever, and recorded here so it is not re-proposed.

**Three proposals, differing only in where the count lives.**

- **T2.A — a manifest file.** `_manifest.md` lists each member with its count. Members stay ordinary files and the folder's shape is readable in one place. The cost is a **third representation** of the same folder — the real listing, the manifest, and the member files — and the listing and manifest can drift apart.
- **T2.B — in the member's filename.** The directory listing *is* the manifest, so nothing can disagree with it; this is the same instinct that made granularity the artifact's own shape. The cost is genuinely ugly filenames plus a strip-the-prefix step at instantiation, a rule that exists nowhere else in the naming convention. Shown as a full member file rather than a manifest line, because under T2.B there is no manifest — which is the point of it.
- **T2.C — on the member's own first line.** The member is itself a stencil, so it can declare its multiplicity in its own body, above its anchor line. No extra file, no drift, clean filenames, no strip step. The cost is that the folder's shape is no longer visible from `ls` — you must open each member to learn the counts, which is exactly what T2.B was buying.

**Open in T2.** A folder template's members are governed by their own stencils, so a folder stencil is a **manifest of anchors** rather than a container of specimens — the disjoint-composition rule sections use, applied to a directory. That holds under all three; only the count's *home* is at issue.

---

# T3 — Floating-Depth Section

**Example T3.a** — `AT/Corp/@Omnifold/@Burke Schrauth.md`

<!-- begin example T3.a -->
# LOG
Reverse-chronological correspondence and notes with Burke Schrauth (Omnifold champion), newest first.

## 2026-08-03 Mon  SENT — reply

To: burke@omnifold.ai
Subject: Thanks, Burke

Burke,

Thanks for the update, and for running a straight process throughout.

Best,
Dan
<!-- end example T3.a -->

**Proposal T3.A** — `AT/_LOG Template.md`

<!-- begin proposal T3.A -->
…# LOG
{{one-line description}}

[0+] ## {{YYYY-MM-DD}} {{DAY}}  {{DIRECTION}} — {{KIND}}
…
<!-- end proposal T3.A -->

**Proposal T3.B** — `AT/_LOG Template.md`

<!-- begin proposal T3.B -->
=# LOG
{{one-line description}}

[0+] ## {{YYYY-MM-DD}} {{DAY}}  {{DIRECTION}} — {{KIND}}
…
<!-- end proposal T3.B -->

## T3 Overview

**Direction: match first.** These files exist and are not being regenerated; the immediate value is locating and checking the section. Generate matters later, for appending a new entry in the right shape.

**What the case demands.** The **anchor** construct — a stencil attaching to a heading rather than to a document — with two depth modes, heading text as a literal, and relative depths inside the specimen. The depth genuinely floats: LOG sits at H1 in T3.a and at other depths elsewhere.

**The two proposals are the two depth markers, side by side.** `…#` reads *this deep or deeper*; `=#` reads *exactly this deep*. Both are shown against the same case so the markers can be compared rather than described. Everything after the first line is relative to the anchor, so `## {{YYYY-MM-DD}}…` means *one deeper than the anchor*, not literally H2.

**The path is the same for both**, which is the point: the anchor lives in the stencil's first line, not in its name. The name reverts to plain `_{Name} Template.md` under [[TINK302 - Section templates and the scope ladder|F302]] Q4's lean; if Q4 lands the other way the file would be `AT/_LOG Section Template.md` and nothing else about T3 changes.

**Open in T3.** The entry heading in T3.a is `2026-08-03 Mon  SENT — reply` — a date, a weekday, a direction, and a kind, separated by a double space and an em-dash. Whether Stencil should decompose that into four variables (as proposed) or treat the line as one opaque `{{HEADING}}` is the first place the language could over-reach: four variables is more expressive and four times more to get wrong, and only a rule ever needs the pieces. Note also that `[0+]` here is the T2 marker reused — the first evidence that these two cases want one construct rather than two.

---

# T4 — One Shape, Four Incompatible Spellings

## T4 Overview

**Real instances.** The email block inside [[AT]] log entries, in four mutually-incompatible forms across two files — bold field labels (`EMAILS:` then `**From:**` / `**Date:**` / `**To:**` / `**Subject:**`) in `@Jake Wachman.md`; a dashed header line and a dashed draft line in `@Burke Schrauth.md`; and a tilde fence with bare `From Jake` / `To Dan and Chris` in `@Jake Wachman.md`. They share **no** common marker. Example T3.a above is a *fifth* spelling — bare `To:` / `Subject:` under a dated heading.

**Direction: match and reconcile only.** [[TINK302 - Section templates and the scope ladder|F302]] resolved that existing log entries are **never rewritten** — a log entry records a message actually sent, and normalizing one edits the record rather than the format. So Stencil must express the agreed shape and then answer *"is this old entry reconcilable with it?"*, which is weaker than *"does this match?"*.

**What the case demands.** Possibly nothing new, and that is what makes it worth testing: if Stencil expresses the target shape and the matcher reports **which parts bound and which did not**, reconcilability is a predicate over that result and stays out of the grammar. If it cannot be kept out, this is the case that proves the language needs a partial-match notion — a large addition, and one to resist.

*(Examples and proposals — to be written.)*

---

# T5 — Stencil Whose Anchor Is A Filename Pattern

## T5 Overview

**Real instance.** `_{{PURCHASE_DATE}} {{HOSTNAME}} Template.md` — a file template whose *name* carries the variables, so the pattern governs which files are members of the folder as well as what is inside them.

**Direction: generate first** (clone → rename → fill is its documented primary use), but match is what makes it a template rather than a snippet.

**What the case demands.** That an anchor can be a **filename** pattern, and that variables bound from the filename are in scope for the body. This is the case that proves the two directions are one pattern: the same `{{PURCHASE_DATE}}` is *read from* the name when matching and *written into* it when generating. It is also the case that makes the format's literal-path rule matter most — the stencil's own filename is the pattern.

*(Examples and proposals — to be written.)*

---

# T6 — Table With Fixed Head And Variable Rows

## T6 Overview

**Real instances.** The dispatch table at the top of every anchor page — see [[DAS Dispatch Table]]; Example T1.a contains a live one. A fixed identity row, then a variable number of labelled rows drawn from a known vocabulary.

**Direction: both.**

**What the case demands.** Structure *below* the heading level — rows within a table — and cardinality applied to something that is neither a heading nor a file. This is the case most likely to push Stencil further than it should go, and therefore the one to design last and cut first. `/audit dispatch` already generates these from a spec; if Stencil cannot express it cleanly, **that is an acceptable answer** and T1.A's opaque `{{dispatch table}}` stands.

*(Examples and proposals — to be written.)*

---

# T7 — A Facet Spec's Own Shape

## T7 Overview

**Real instance.** `facets/DAS Facet.md` states the shape every facet spec doc takes — H1, one-line summary, dispatch table, document-structure outline, the `# RULESET R-<facet>` block, the `# BRIEF` block. That prose *is* a stencil, written as a bullet list because there was no notation for it.

**Direction: both**, and it is the reflexive case — Stencil describing the documents that define Stencil's own vocabulary.

**What the case demands.** Nothing new, if T1–T3 land: required sections, an optional one, open-world content beneath each. Its value is as the **acceptance test** — if Stencil cannot restate `DAS Facet`'s document-structure list without loss, it is not yet expressive enough for the corpus it governs.

*(Examples and proposals — to be written.)*

---

# Cases still to be identified

Collected in one pass and certainly incomplete. Candidates not yet examined: the `{slug} Track/` folder shape, study-card files, and the `.anchor` file itself — that last one out of scope until the markdown-first decision is revisited. The `## Open Questions` two-zone block is deliberately **not** a candidate: it is machine-maintained by `state`, and a stencil for it would be a second authority over bytes that already have one.
