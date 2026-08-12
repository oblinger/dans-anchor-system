# RULESET R-progressive
include::
where:: `always`
description:: layout conventions of progressive disclosure — checked on every markdown doc
import:: skills/audit/scripts/audit-plan.py

The mechanical, whole-document layout checks of this discipline: the **section-spacing** conventions, the summary's freshness against the units it covers, and the artifact-leads rule. Applies to every markdown document (`always`); each rule decides internally whether and how it constrains a given doc. These are the deliberately *conditional, multi-check* rules — one rule that both determines what kind of doc it is looking at and makes several assertions accordingly — the case that stress-tests a declarative rule engine (per the [[Warden Roadmap]] item 8). Format of this set: [[DAS Ruleset]].

**Routing left this set in F308 M2, and `-01`, `-03` and `-04` are retired here rather than renumbered.** They governed which spine a document opens with — a question about *where the reader is*, not about *what they read next* — and they now live in [[R-spine]] as `R-spine-01`, `-02`, `-03` with their bodies and checkers unchanged. The numbers stay vacant per the never-recycle policy, so a citation of `R-progressive-03` in an old document resolves to nothing rather than to a different rule. This set now mentions routing nowhere.

### RULE R-progressive-02 — progressive-disclosure section spacing (checked)
check:: progressive_disclosure_layout
mend:: doc-spacing

The blank-line conventions that keep a doc's outline scannable: every `## H2` is preceded by a blank line, and the file carries no trailing blank lines. One rule, two assertions.

**Check pattern:** scanning outside fenced code blocks — (1) each `## H2` has a blank line immediately before it (no H2 glued to the prose above); (2) the last line is non-blank. Two conventions deliberately **excluded** as too noisy on ordinary docs: the anchor-page-only "no blank after the H1" glue rule (that is `R-anchor-page-07`'s job — an ordinary doc may have a blank after its H1) and the "no doubled blank line" rule (widely tolerated in practice).

**Why:** consistent section breaks let a navigator's eye find the structure at a glance — the second layer of progressive disclosure. An H2 glued to the prose above it hides where one section ends and the next begins.

### RULE R-progressive-05 — Re-consider the summary when the covered content moves (checked)
check:: summary_fresh

A summary covers a **set of units** — its own `##` sections for a file-scope doc, the folder's member files for a container or tree. When a quarter of those units have changed, or **any** unit has been added or removed, since the summary was last written, the doc is flagged for re-consideration. Blessing is **observed, never self-reported**: when the summary region's own hash changes the agent has evidently rewritten it, so the current unit set is re-blessed automatically — there is no completion handshake for an agent to forget or overstate. Advisory only; it never blocks a write.

**Check pattern:** against the blessing registry (`~/.warden/disclosure.json`), changed-units ÷ total ≥ 0.25, or ≥1 unit added or removed.

**Why:** counting changed units is what "big chunks moved" means mechanically. File-size delta fires on typo fixes; hashing only the heading set misses a section rewritten wholesale under an unchanged heading — which is exactly when a summary goes stale.

### RULE R-progressive-06 — The artifact leads the document (stated)

A document that exists to deliver **one element** — a tree, a generated table, a roster, a chart — puts that element directly under the H1's orientation line, above the dispatch table, and puts every word explaining it *below* the artifact under `## Overview`.

**Check pattern:** apply the selection test — *if you deleted everything but one element and the document still did its job, that element is the artifact.* Fails when a document has an artifact and any prose paragraph, dispatch table, TLDR, figure, or body H2 precedes it. Passes vacuously on documents with no artifact, which is most of them.

**Why this is stated and not checked.** The trigger is not mechanically decidable. No per-file checker can tell whether a large table is the document's whole reason for existing or one exhibit among many, and every honest proxy — largest block, `cssclasses: monospace`, fence length — fires on ordinary spec documents that legitimately carry a big example. Wiring a heuristic here would flag this repo's own rulesets and teach authors that the rule is noise. It becomes checkable the day an artifact is **declared** rather than inferred; until then the discipline states it and the author applies it.

**Why:** the reader's first disclosure layer is *what this is*, and when the document is one thing, showing that thing IS the disclosure. Explanation above it is a legend printed before the map — unreadable until the reader scrolls past it to find its referent. Repaired by hand on [[Agent Purview]] 2026-08-06, which is the worked instance; the spec was not silent but mis-shaped, since § Anti-patterns already forbade prose between the H1 and the first body H2 while § Figure placement sent content figures to the body, leaving the artifact nowhere legal to stand.

## Position in the catalog

Sits under [[R-doc]] (cross-cutting documentation conventions umbrella), beside [[R-markdown]] and [[R-spine]]. Applies to every markdown doc (`always`) — each rule decides internally whether/how it constrains a given doc.

## Mend

Remediation messages for these rules — what to actually do when one fires. Reached as `warden mend R-progressive-<nn>`; wired by the `mend::` line on each rule. State the fix, point at the facet, never restate it.

### MEND doc-spacing

Two mechanical edits, both safe to make blind.

Put a blank line before every `## H2` that is glued to the prose above it, and delete every blank line at the end of the file so the last line has content. Nothing else about spacing is checked — doubled blank lines mid-document are tolerated, and a blank line after the H1 is fine on an ordinary doc.

If a script wrote this file, fix the script rather than the file: a generator that emits trailing blanks will re-emit them on the next write, and the loop is silent because the hook fires on a file you did not hand-edit. That was the shape of T067, where thirteen copies of one join expression left a trailing newline on every `state` write.

For the model, read [[DAS progressive-disclosure]].

## See also

- [[DAS progressive-disclosure]] — discipline spec this ruleset enforces.
- [[R-spine]] — the routing half, extracted 2026-08-08.
- [[R-doc]] — cross-cutting documentation conventions umbrella.
- [[R-markdown]] — sibling always-applies ruleset (mechanical + authoring markdown rules).
