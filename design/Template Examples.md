---
description: "The case corpus the template DSL is derived from — real vault instances first, proposed notation second, one H1 per case."
---

# Template Examples
The working corpus for [[TINK303 - Template DSL - one pattern language for facets, templates, and sections|F303]] M1 — every template-shaped case that actually exists, and how the notation would express it.

## How to read and extend this document

**Cases first, proposals second.** Within each case the real instances come before any proposed notation. The case is ground truth; the proposal is the thing under test. Leading with the proposal biases the reader into asking whether the case fits the notation instead of whether the notation fits the case.

**Every case cites a real file.** A shape with no instance in the vault is not admitted — the language is defined from demonstrated need, so a plausible hypothetical is exactly what must not justify a construct.

**Each case declares which direction it needs** — *match*, *generate*, or *both*. This is what will expose where the two directions genuinely diverge rather than merely look different.

**Heading-shift convention.** Specimens are shown **one heading level deeper than they appear in the real file**, because this document uses one H1 per case and markdown specimens are shown live rather than fenced (fencing makes wiki-links and headings inert). So a whole-file template whose real first line is `# {slug} Backlog` appears here as `## {slug} Backlog`. Relative depths inside a specimen are preserved; only the absolute level is shifted.

**Status.** Frame plus the seven cases identified so far, two worked through. The remaining five carry their real instances and await proposals. When Dan reads this and says the cases are covered, M1 is done and the DSL is written *from* it.

# Case 1 — a whole-document facet instance

**Real instances.** `templates/backlog.md` in this repo governs every `{slug} Backlog.md` in the vault — [[SCOUT Backlog]], [[TINK Backlog]], [[LUMEN Backlog]], and ~40 others. Its specimen opens with an H1 title pattern, carries a dispatch table, then a fixed sequence of H2 sections.

**Direction: both.** Generate — a new anchor's Backlog is instantiated from it. Match — every existing Backlog is checked against it by `R-backlog`.

**What the case demands.** A whole-document anchor; a variable in the title (`{slug}`); a fixed sequence of required H2 sections; and — the interesting part — those sections are *required to exist* but their contents are governed by other rules entirely. So the specimen needs to say "this heading, and I say nothing about what is under it."

*(Proposal — to be written. The open-world marker is the construct at issue.)*

# Case 2 — a folder template with a repeating member

**Real instance.** `templates/log/` in this repo — a directory containing exactly two entries: `{slug} Log.md` (the dispatch page, exactly one) and `{{YYYY-MM-DD}} — {{short topic}}.md` (an entry, zero or more).

**Direction: both.** Generate — instantiate a Log folder for a new anchor. Match — check an existing Log folder's shape.

**What the case demands.** This is the **cardinality** case, and it is the cleanest one in the vault: one member is exactly-one and the other is zero-or-more, in the same template, distinguished only by the fact that one filename is a literal-with-a-variable and the other is a pure pattern. The notation has to say which is which rather than leaving it to be inferred from whether the name looks pattern-ish.

Dan, 2026-08-04: *"I want to have multiple, 0 or more of these or one or more of these, those kinds of things in there."* This is that requirement's first real instance.

*(Proposal — to be written. Cardinality markers, and how a `1+` reads in the generate direction, where it must emit exactly one.)*

# Case 3 — a section inside a document, matched at floating depth

**Real instances.** The `# LOG` section inside `@{{PERSON}}.md` files under [[AT]] — a heading whose text is the literal `LOG`, carrying dated entries beneath it. The depth varies between files, which is why [[TINK302 - Section templates and the scope ladder|F302]] settled on floating depth.

**Direction: match first.** These files exist and are not being regenerated; the immediate value is locating and checking the section. Generate matters later, for appending a new entry in the right shape.

**What the case demands.** The **anchor** construct — a template that attaches to a heading rather than to a document — with Dan's two depth modes (*this deep or deeper* versus *exactly this deep*), the heading text as a literal, and relative depths inside the specimen.

**Proposal A.** The template's first line is the anchor, carrying a depth marker. The rest of the specimen is what must appear beneath, at depths relative to the anchor:

## …# LOG

### {{YYYY-MM-DD}} — {{TOPIC}}

{{entry body}}

*(Shown per the heading-shift convention; the anchor's real depth in `@{{PERSON}}.md` is H1 and the entries are H2.)* The `…` prefix reads *this deep or deeper*, so the same template matches a file where LOG sits at H2. Cardinality on the entry — zero or more — is the Case 2 construct reused, which is the first evidence that these two cases want the same marker.

# Case 4 — one shape, four incompatible spellings

**Real instances.** The email block inside [[AT]] log entries, in four mutually-incompatible forms across two files — bold field labels (`EMAILS:` then `**From:**` / `**Date:**` / `**To:**` / `**Subject:**`) in `@Jake Wachman.md`; a dashed header line (`--- Burke → Dan, Mon 2026-07-20 9:07 AM · "Re: …" ---`) and a dashed draft line (`--- DRAFT: Dan → Burke ---`) in `@Burke Schrauth.md`; and a tilde fence with bare `From Jake` / `To Dan and Chris` in `@Jake Wachman.md`. They share **no** common marker.

**Direction: match and reconcile only.** [[TINK302 - Section templates and the scope ladder|F302]] resolved that existing log entries are **never rewritten** — a log entry is a record of a message actually sent, and normalizing one edits the record rather than the format. So the notation must be able to express the agreed shape and then be used to ask *"is this old entry reconcilable with it?"*, which is a weaker question than *"does this match?"*.

**What the case demands.** Possibly nothing new — reconcilability may be a *rule* over a partial match rather than a construct in the grammar. That is the interesting finding to test: if the DSL can express the target shape and the matcher reports *which parts bound and which did not*, reconcilability is a predicate over that result and stays out of the language.

# Case 5 — a template whose anchor is a filename pattern

**Real instance.** `_{{PURCHASE_DATE}} {{HOSTNAME}} Template.md` — a file template whose *name* carries the variables, so the pattern governs which files are members of the folder as well as what is inside them.

**Direction: generate first** (clone → rename → fill is its documented primary use), but match is what makes it a template rather than a snippet — it states what the folder's records look like.

**What the case demands.** That the anchor can be a **filename** pattern, not only a heading or a document root, and that variables bound from the filename are in scope for the body. This is the case that proves the two directions are the same pattern: the *same* `{{PURCHASE_DATE}}` is read from the name when matching and written into the name when generating.

*(Proposal — to be written.)*

# Case 6 — a table with a fixed head and variable rows

**Real instances.** The dispatch table at the top of every anchor page — see [[DAS Dispatch Table]] and any anchor page for a live one. A fixed identity row, then a variable number of labelled rows drawn from a known vocabulary.

**Direction: both.**

**What the case demands.** Structure below the heading level — rows within a table — and cardinality applied to something that is not a heading or a file. This is the case most likely to push the language further than it should go, and therefore the one to design last and cut first if it does not fit cleanly. A dispatch table is already generated by `/audit dispatch` from a spec; if the DSL cannot express it, that is an acceptable answer.

# Case 7 — a facet spec's own shape

**Real instances.** `facets/DAS Facet.md` states the shape every facet spec doc takes — H1, one-line summary, dispatch table, document-structure outline, the `# RULESET R-<facet>` block, the `# BRIEF` block. That prose *is* a template, written as a bullet list because there was no notation for it.

**Direction: both**, and it is the reflexive case: the DSL describing the documents that define the DSL's own vocabulary.

**What the case demands.** Nothing new, if the earlier cases land — required sections, an optional one, and open-world content beneath each. Its value is as the **acceptance test**: if the notation cannot restate `DAS Facet`'s document-structure list without loss, it is not yet expressive enough for the corpus it is meant to govern.

# Cases still to be identified

The seven above were collected in one pass and are certainly incomplete. Candidates not yet examined: the `{slug} Track/` folder shape, the `## Open Questions` two-zone block (which is machine-maintained and may not want a template at all), study-card files, and the `.anchor` file itself — though that last one is out of scope until the markdown-first decision is revisited.
