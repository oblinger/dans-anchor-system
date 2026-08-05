---
description: "The case corpus the template DSL is derived from — named cases, verbatim real examples, then proposed notation. Every block is delimited and copy-pasteable."
---

# Template Examples
The working corpus for [[TINK303 - Template DSL - one pattern language for facets, templates, and sections|F303]] M1 — every template-shaped case that actually exists, and how the notation would express it.

## The format

**Cases are named, not numbered — the number is only a handle.** `T3 — Floating-Depth Section` is referred to as *the floating-depth-section case*; `T3` exists so a proposal can be called `T3.A` without repeating the name.

**Order inside a case: prose, then examples, then proposals.** The example is ground truth and fixed; the proposal is the thing under test. Leading with the proposal biases the reader into asking whether the case fits the notation instead of whether the notation fits the case.

**Every block is delimited, and everything inside a block is verbatim.** A block opens with a bold label and an HTML begin-marker and closes with an end-marker. **Nothing inside a block is commentary** — what is between the markers is exactly the bytes of the file or template, at its real heading depth, with no shifting and no annotation. If something needs saying about a block, it is said in the prose *above* the block. The markers are invisible when rendered and unambiguous in source, which is where you copy from.

Examples are lettered lowercase (`T3.a`), proposals uppercase (`T3.A`), so the two are distinguishable at a glance and in a cross-reference.

**Two consequences of verbatim-and-unfenced, both accepted deliberately.** Specimen headings are real headings, so they appear in this document's outline — that is the price of specimens that can be copied and of a notation where heading depth is semantic. And specimen wiki-links are live links, so this file must be excluded from link-resolution and doc-structure rules the way `_* Template` files already are. If outline noise ever becomes intolerable the escape is to graduate specimens to sibling files and leave the markers as links; the block boundaries are already file-shaped, so that migration is mechanical.

**Every case cites a real file.** A shape with no instance in the vault is not admitted — the language is defined from demonstrated need, so a plausible hypothetical must never justify a construct.

**Each case declares the direction it needs** — *match*, *generate*, or *both*. This is what will expose where the two directions genuinely diverge rather than merely look different.

**Status.** Format settled plus seven cases identified; T1–T3 worked through with examples and proposals, T4–T7 carrying their real instances and awaiting proposals. When Dan reads this and says the cases are covered, M1 is done and the DSL is written *from* it.

---

# T1 — Whole Document Template

The most common case: a facet whose instance is one document with a required section skeleton. `templates/backlog.md` governs every `{slug} Backlog.md` in the vault — forty-odd of them.

**Direction: both.** Generate — a new anchor's Backlog is instantiated from it. Match — `R-backlog` checks every existing Backlog against it.

**What the case demands.** A whole-document anchor; a variable in the title; a required sequence of H2 sections; and the interesting part — those sections must *exist* but their contents are governed by other rules entirely. The example below shows why that matters: its `## Now` holds one enormous row that no template should attempt to describe. So the notation needs to say **"this heading, and I say nothing about what is beneath it"**, which is the open-world marker in its match reading and the omit-marker in its generate reading.

**Example T1.a** — `SYS/Staff/Hermes/HERMES Track/HERMES Backlog.md`, complete and verbatim as of 2026-08-04.

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

**Proposal T1.A** — the anchor is the document root (no marker, per the default rule). `{slug}` binds from the anchor context. The `…` line is the open-world marker: ignored when matching, omitted when generating.

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

**Open in T1.A.** The dispatch table is a placeholder standing in for a whole sub-shape — that is [[#T6 — Table With Fixed Head And Variable Rows|T6]], and whether it resolves as a nested template reference or stays an opaque variable is the question T6 has to answer. Section *order* is also unstated here: the example carries `Ready / Notes / Next / Later / Now` while `templates/backlog.md` lists a different order, so either order is not load-bearing or the corpus is already non-conforming — a real finding either way, and one this case surfaced only because the example is verbatim.

---

# T2 — Folder Template With A Repeating Member

**Direction: both.** Generate — instantiate a Log folder for a new anchor. Match — check an existing one.

**What the case demands.** This is the **cardinality** case, and the cleanest in the vault: one member is exactly-one and the other is zero-or-more, in the same template, distinguished today only by the fact that one filename is a literal-with-a-variable and the other is a pure pattern. Dan, 2026-08-04: *"I want to have multiple, 0 or more of these or one or more of these, those kinds of things in there."* The notation must say which is which rather than leaving it inferred from whether a name looks pattern-ish.

**Example T2.a** — the shipped folder template `templates/log/`, as a file tree.

```
templates/log/
├── {slug} Log.md
└── {{YYYY-MM-DD}} — {{short topic}}.md
```

**Example T2.b** — `templates/log/{{YYYY-MM-DD}} — {{short topic}}.md`, complete and verbatim.

<!-- begin example T2.b -->
# {{YYYY-MM-DD}} — {{short topic}}

## What happened

{{per-session plan + outcome, in narrative form}}

## Decisions

- {{decision made this session, with links to the docs it landed in}}
- ...

## Outstanding
<!-- end example T2.b -->

**Proposal T2.A** — the anchor is the directory; members are named by filename pattern and quantified. `1` and `0+` are the cardinality markers; a `0+` member generates zero instances and matches any number.

<!-- begin proposal T2.A -->
[1]  {{slug}} Log.md
[0+] {{YYYY-MM-DD}} — {{short topic}}.md
<!-- end proposal T2.A -->

**Open in T2.A.** The member bodies are governed by their own templates (T2.b is one), so a folder template is a **manifest** of anchors rather than a container of specimens — which is the same disjoint-composition rule sections use, applied to a directory. Whether the cardinality marker belongs in a manifest line or on the member template itself is the open question; putting it on the member would mean a template declares its own multiplicity, which reads oddly for a file that is also a single specimen.

---

# T3 — Floating-Depth Section

**Direction: match first.** These files exist and are not being regenerated; the immediate value is locating and checking the section. Generate matters later, for appending a new entry in the right shape.

**What the case demands.** The **anchor** construct — a template attaching to a heading rather than to a document — with Dan's two depth modes (*this deep or deeper* versus *exactly this deep*), heading text as a literal, and relative depths inside the specimen. The depth genuinely floats: LOG sits at H1 in the example below and at other depths elsewhere.

**Example T3.a** — the `# LOG` section of `AT/Corp/@Northwind/@Robin Calder.md`, verbatim, first entry only (a complete instance of the anchored shape).

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

**Proposal T3.A** — `…` before the hashes marks the anchor and reads *this deep or deeper*. Everything after the first line is relative to it, so the H2 entry is "one deeper than the anchor" rather than literally H2.

<!-- begin proposal T3.A -->
…# LOG
{{one-line description}}

[0+] ## {{YYYY-MM-DD}} {{DAY}}  {{DIRECTION}} — {{KIND}}
…
<!-- end proposal T3.A -->

**Proposal T3.B** — same anchor, exact depth. `=` reads *exactly this deep*; the rest is unchanged. Offered as the contrast case so the two markers can be compared side by side rather than described.

<!-- begin proposal T3.B -->
=# LOG
{{one-line description}}

[0+] ## {{YYYY-MM-DD}} {{DAY}}  {{DIRECTION}} — {{KIND}}
…
<!-- end proposal T3.B -->

**Open in T3.** The entry heading in T3.a is `2026-08-03 Mon  SENT — reply` — a date, a weekday, a direction, and a kind, in one line with a double space and an em-dash as separators. Whether the notation should decompose that into four variables (as proposed) or treat the whole line as one opaque `{{HEADING}}` is the first place the language could over-reach: four variables is more expressive and four times more to get wrong, and only a rule ever needs the pieces. Cardinality `[0+]` is the T2 marker reused, which is the first evidence these two cases want one construct rather than two.

---

# T4 — One Shape, Four Incompatible Spellings

**Real instances.** The email block inside [[AT]] log entries, in four mutually-incompatible forms across two files — bold field labels (`EMAILS:` then `**From:**` / `**Date:**` / `**To:**` / `**Subject:**`) in `@Alex Trenton.md`; a dashed header line and a dashed draft line in `@Robin Calder.md`; and a tilde fence with bare `From Alex` / `To Dan and Morgan` in `@Alex Trenton.md`. They share **no** common marker. Note that Example T3.a is a *fifth* spelling — bare `To:` / `Subject:` under a dated heading.

**Direction: match and reconcile only.** [[TINK302 - Section templates and the scope ladder|F302]] resolved that existing log entries are **never rewritten** — a log entry is a record of a message actually sent, and normalizing one edits the record rather than the format. So the notation must express the agreed shape and then answer *"is this old entry reconcilable with it?"*, which is weaker than *"does this match?"*.

**What the case demands.** Possibly nothing new, and that is the interesting thing to test: if the DSL expresses the target shape and the matcher reports **which parts bound and which did not**, reconcilability is a predicate over that result and stays out of the grammar entirely. If it cannot be kept out, this is the case that proves the language needs a partial-match notion — a large addition, and one to resist.

*(Examples and proposals — to be written.)*

# T5 — Template Whose Anchor Is A Filename Pattern

**Real instance.** `_{{PURCHASE_DATE}} {{HOSTNAME}} Template.md` — a file template whose *name* carries the variables, so the pattern governs which files are members of the folder as well as what is inside them.

**Direction: generate first** (clone → rename → fill is its documented primary use), but match is what makes it a template rather than a snippet.

**What the case demands.** That an anchor can be a **filename** pattern, and that variables bound from the filename are in scope for the body. This is the case that proves the two directions are one pattern: the same `{{PURCHASE_DATE}}` is *read from* the name when matching and *written into* it when generating.

*(Examples and proposals — to be written.)*

# T6 — Table With Fixed Head And Variable Rows

**Real instances.** The dispatch table at the top of every anchor page — see [[DAS Dispatch Table]], and Example T1.a above contains a live one. A fixed identity row, then a variable number of labelled rows drawn from a known vocabulary.

**Direction: both.**

**What the case demands.** Structure *below* the heading level — rows within a table — and cardinality applied to something that is neither a heading nor a file. This is the case most likely to push the language further than it should go, and therefore the one to design last and cut first. `/audit dispatch` already generates these from a spec; if the DSL cannot express it cleanly, **that is an acceptable answer** and T1.A's opaque `{{dispatch table}}` placeholder stands.

*(Examples and proposals — to be written.)*

# T7 — A Facet Spec's Own Shape

**Real instance.** `facets/DAS Facet.md` states the shape every facet spec doc takes — H1, one-line summary, dispatch table, document-structure outline, the `# RULESET R-<facet>` block, the `# BRIEF` block. That prose *is* a template, written as a bullet list because there was no notation for it.

**Direction: both**, and it is the reflexive case — the DSL describing the documents that define the DSL's own vocabulary.

**What the case demands.** Nothing new, if T1–T3 land: required sections, an optional one, open-world content beneath each. Its value is as the **acceptance test** — if the notation cannot restate `DAS Facet`'s document-structure list without loss, it is not yet expressive enough for the corpus it is meant to govern.

*(Examples and proposals — to be written.)*

# Cases still to be identified

Collected in one pass and certainly incomplete. Candidates not yet examined: the `{slug} Track/` folder shape, study-card files, and the `.anchor` file itself — that last one out of scope until the markdown-first decision is revisited. The `## Open Questions` two-zone block is deliberately **not** a candidate: it is machine-maintained by `state`, and a template for it would be a second authority over bytes that already have one.
