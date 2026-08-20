---
description: "design trade-off threads on the Stencil grammar — what each construct has to carry, and what was rejected"
---

# STEN Language Discussions
Dated trade-off threads behind [[STEN Language]] — what the grammar has to be able to say, how each answer was reached, and what was rejected on the way.

Opened 2026-08-20 as a [[DAS Discussion]] method-2 sibling. Newest first.

## 2026-08-20 — A template's filename should stop encoding its instances' filename

**Problem.** A template today announces what it templates *in its own filename*: `_@{{PERSON_NAME}} Template.md`, `_Computer {{NICKNAME}} Template.md`, `_Disk {{LABEL}} Template.md`. The name is doing two jobs — identifying the template, and declaring the shape of the files it governs — and the second job is the one that goes wrong. Dan, 2026-08-20: *"I don't like having the structure of the path in the name of the template. It's very messy, and it's trying to jam a lot of information into a file name in a weird way. You get file names with curly braces in them."*

Three concrete costs, beyond the ugliness:

- **A filename cannot say very much.** It carries one pattern. It cannot say that a person entity is `@{{PERSON_NAME}}.md` when flat *and* `@{{PERSON_NAME}}/@{{PERSON_NAME}}.md` when promoted to folder form — which is exactly what [[DAS At Entity]] needs, and exactly the anchor+file vs anchor+folder distinction [[TINK336 - Facet association patterns, a path template per parent and method|F336]] measured as load-bearing.
- **Braces in a filename are hostile to the tools that touch filenames** — shell globs, `Edit`'s exact-match, link resolution — for a payload that is not a name.
- **It ties the template to a place.** `_@{{PERSON_NAME}} Template.md` governs its own folder and the tree beneath it ([[DAS Template]] § hierarchy climb). But `@` entities are no longer confined to [[AT]] — 655 pages across `AT/`, `SV/` and `Topic/` — so the one thing the filename form cannot express is the case that actually exists.

**Options considered.**

**(A) Leave it.** The form is ugly but self-documenting, costs nothing today, and every existing template already reads this way. Rejected as the default rather than on its merits: it is only free while a template governs one tree and has one instance shape, and [[DAS At Entity]] is a live counter-example to both halves.

**(B) A dedicated key on templates.** Give the template a plain name and one new field naming the instance pattern — `instance:: @{{PERSON_NAME}}.md`. Simple, and it reads well. Rejected because it is a **second grammar for a question that already has one**: F336 declares where instances live with `assoc-{parent}-{method}::` keys, measured against 533 instances, and a template that answers the same question in different words is the drift this repository keeps paying for.

**(C) The same `assoc-*::` keys, on templates as on facets.** Adopted as the proposal. A template is named plainly and declares its instances with the vocabulary F336 already established:

    _At Entity Template.md

      assoc-anchor-file::    {{ANCHOR}}/@{{PERSON_NAME}}.md
      assoc-anchor-folder::  {{ANCHOR}}/@{{PERSON_NAME}}/@{{PERSON_NAME}}.md

**Decision.** Proposed, not settled — asked as [[TINK336 - Facet association patterns, a path template per parent and method|F336]] Q3, because F336 owns the key grammar and this is a second consumer of it rather than a new feature. Three points worth keeping whichever way it is ruled:

1. **It answers the "where does an instance go" question once**, for facets and templates alike. Today a facet answers it in a `::` key and a template answers it in its filename, which is two answers to one question — and only one of them is checkable.
2. **The `{{PREFIX}}`/`{{SLUG}}` finding transfers directly.** F336 chose `{{PREFIX}}` because `{{SLUG}}` is unresolvable for the 176 instances whose anchor declares no slug. A template key written with `{slug}` would be unmatchable in the same way, which is worth knowing before any are drafted.
3. **Discovery has to be answered too, and it is the weak half.** If the name no longer encodes the pattern, finding the governing template means scanning for the `Template` **suffix** and reading each candidate's keys — Dan: *"when you do template instantiation, you're really looking for a file that has a suffix of the word template, and then you have to look at them to figure out which ones might apply."* That is a linear read where the old form was a glob. It is affordable because the corpus is small — `templates/` holds 15 — but it stops being affordable silently, and nothing currently counts them. Keeping the leading `_` is orthogonal and should stay: it sorts the template to the top of its folder and marks it as meta.

**Not urgent, and deliberately so.** Dan, in the same turn: *"for right now it may not even matter."* The reason to record it now is that [[DAS At Entity]] is being written this week and would otherwise mint one more `_@{{…}} Template.md` under a convention already known to be wrong.
