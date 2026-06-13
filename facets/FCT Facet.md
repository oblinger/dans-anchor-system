---
description: "the Facet primitive — what a facet is and how to write its spec"
---
# FCT Facet
A narrow, usually file-based aspect of an anchor — and the spec for how to write one.

| -[[FCT Facet]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[OBSK]] → [FCT Facet](hook://p/FCT%20Facet)<br>: the Facet primitive — what a facet is and how to write its spec |
| --- | --- |
| Related | [[FCT Skill]],  [[FCT Rules]],  [[FCT Facets]] (the index),  [[CAB Aspects]], |
| Examples | [[FEX Manifest\|single-file, one]],  [[FEX Pin\|single-file, many]],  [[FEX Bundle\|folder, many]],   |

A **facet** is a narrow, usually file-based aspect of an anchor — one specific structural feature (a `Backlog` file, an `Architecture` doc, a website subfolder), defined by its own spec doc and detected (by default) through file-existence. This page is the spec for *the facet kind itself*: what a facet is and the shape every facet spec doc takes. It is the singular **definition**; [[FCT Facets]] (plural) is the **index** of all concrete facets.

A facet **defines a kind**. The concrete `<NAME> Backlog.md` inside a real project is an *instance* of the Backlog facet, not a facet itself — keep the two apart.

Facets are one of the two kinds of [[CAB Aspects|Aspect]] — the narrow, file-based kind; the broad declared-paradigm kind is the [[CAB Traits|Trait]] (full distinction: [[CAB Aspects]] § Trait vs Facet). The shared model lives in [[CAB Aspects]]; this page is the facet-authoring view of it.

# Facet Document Structure

A facet spec is one file (`facets/FCT <Name>.md`), authoritative for that facet. Like any anchor page it opens with an **H1 + one-line summary + dispatch table**, then the sections every Aspect spec carries (per [[CAB Aspects]] § Spec-doc structure):

- **`## What it is`** — the narrow aspect this facet names, in a sentence.
- **`## How it's detected`** — how the system decides the facet is present (default file-existence; override here), and its **cardinality** (`one` per anchor, or `many`).
- **`## Format`** — filename pattern, frontmatter, required body sections, naming rules.
- **`## Constraints`** — legal-usage rules: mutual exclusion, co-requirement, format invariants — often formalized as a paired rule set (e.g. [[R-fex-manifest]]).
- **`## Expected Usage`** — recommended patterns: common combinations, typical scale, skill pairings.
- **`## Skills and audits that attach`** — which skills write/read it, which audits check it.
- **`## Triggers`** *(optional)* — behavioral triggers the facet declares (per [[CAB Aspects]] § Triggers).

For a worked facet, open an example in the dispatch table above — there is no embedded copy here, because a facet is itself a full anchor page and embedding one inside this spec just blurs example-vs-spec.

# BRIEF

- **This is the spec for the *facet* primitive** — what a facet is and the shape of a facet spec doc. Sibling to [[FCT Skill]] (skill primitive) and [[FCT Rules]] (rule-set primitive); indexed from [[FCT Primitives]].
- **Singular, not the index.** [[FCT Facets]] (plural) is the *catalog* of concrete facets; this page (singular) *defines the kind*. The Primitives-row "Facet" link points here.
- **Don't embed a worked example.** A facet example is itself a full anchor page (dispatch table, sections, often a paired rule set); embedding one inside this spec confuses example-vs-spec. Describe the shape with the `Facet Document Structure` bullet list; link real examples in the dispatch `Examples` row.
- **`Examples` lists *facets* (definitions), never instances.** A project's `Architecture.md` is an *instance* of the Architecture facet — it belongs on that facet's own page, not here. Label each `Examples` entry by what kind of facet example it is (small / complete; single-file / folder / many-cardinality).
- **The umbrella model lives in [[CAB Aspects]]** — don't duplicate the Aspect/Trait/Facet vocabulary or the composability matrix here; link to it.
