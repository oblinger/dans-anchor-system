# RULESET R-feed
include::
where:: `file:**/.anchor`
description:: Rules for the feed DAG — the `feeds:` key in `.anchor`, its consumer-only declaration, the acyclicity and resolvability invariants, and the no-silent-empty reporting duty of any pass that walks it.

Ruleset for the feed discipline ([[DAS feed]]). It governs the **graph**, not what travels it: the shape of a stone group, its numbering, its control file and its keys are [[R-stone]]'s, and the rules here name no kind.

It is the **first ruleset for a corpus-level graph**. [[DAS anchor-dag]] — the containment graph this one is the sibling of — carries no ruleset of its own, so there is no established form to copy; the `stated`-with-a-named-guard-test shape below is chosen because the alternative is a rule that cannot be evidenced by any file, and this repo has already shipped several of those.

**Every rule here is `stated`, and that is the honest tier rather than a delay.** All four are properties of a **pass over the whole corpus**, not of any one document — no `where::`-selected file can evidence "the graph is acyclic", because acyclicity is not a fact about a file. They are enforced where they are enforceable, at run time in `stone`, and each rule below names the guard test that holds it. This is the [[R-exception-discipline]]-03 shape, and it is deliberately **not** the shape [[DAS Stone]]'s BRIEF warns against: arming these as `checked` would buy a coverage claim and no coverage.

**Not adopted by any umbrella**, and it must not be: the rules below select no file, so there is nothing for an umbrella to bind them to.

> **Reviewed and left dormant 2026-08-11 ([[TINK Backlog#^T349|T349]]) — the disposition above is right, and the `where::` line above it is right by accident.**
>
> This set's `where:: file:**/.anchor` is the class-(a) unmatchable form measured on [[R-code-repository]] (anchor-mode scope is `target.rglob("*.md")`, so a `file:` selector naming a non-`.md` path resolves to the empty set). Everywhere else that form is a defect. **Here the empty set is the correct answer** — the header two paragraphs up says plainly that these rules select no file — so the ruleset behaves exactly as intended, for a reason that has nothing to do with what it wrote.
>
> **It cannot be repaired, because the selector grammar has no way to say "selects no file."** Deleting the line is strictly worse, not neutral: `_selector_of` falls back `rule → ruleset → "always"`, and `always` is *every file in scope*, so a set whose whole thesis is that no file can evidence its rules would suddenly select all of them. The two available spellings fail in opposite directions and neither says the true thing. R-feed is the first corpus-level ruleset in the repo, so it is the first to need that spelling; [[DAS anchor-dag]], the sibling graph, avoided the problem by carrying no ruleset at all.
>
> Left exactly as written. Anyone adding a selector kind for corpus-level rules should start here, and should not "fix" this line in the meantime — the accident is currently load-bearing.

Note for whoever later decides otherwise — **[[R-facet]] is not the umbrella that arms anything.** Measured 2026-08-11 (`--verify-registry`): 94 rulesets carry rules and only 34 are reachable from the `R-doc`/`R-anchor` closure that `/audit anchor` actually resolves; `R-facet` is among the other 60. A corpus sweep over `Topic/MED` bears this out — `R-rocks` and `R-stone` emit verdicts because [[R-anchor]] names them directly, not because `R-facet` includes them. Several facet BRIEFs still instruct agents to "add it to `R-facet`'s `include::`", which arms nothing while looking exactly like adoption.

### RULE R-feed-01 — `feeds:` is declared by the consumer, and only by the consumer (stated)

An anchor's `.anchor` names the anchors it draws **from**. No key declares the other direction; consumers are computed by inverting the graph.

**Check pattern:** stated; any second key purporting to declare out-edges (`feeds-to:`, `exports:`, `consumers:`) is the defect this rule exists to prevent.

**Why:** two declared directions are two things that drift apart, and the drift is silent — a source that thinks it publishes to an anchor no longer drawing from it produces no error anywhere. Declaring one direction makes the disagreement unrepresentable. The cost is real and accepted: *"where does my work go?"* is not answerable by reading your own `.anchor` and needs an inverted index, which is a tooling job. The benefit is that a leaf anchor needs no configuration at all — joining the graph edits the consumer, which is the file where the decision was actually made.

### RULE R-feed-02 — The graph is acyclic, and a cycle is reported as a path (stated)

`feeds:` must be a DAG. A pass that finds a cycle reports it as an arrow path — `A → B → C → A` — and aborts **before writing anything**, rather than returning a boolean or a count.

**Check pattern:** stated; guard test `skills/workflow/scripts/test-f313-stone.py` case I — a deliberately introduced cycle is reported as the expected arrow path, the pass exits non-zero, and every watched file is byte-identical afterward.

**Why:** a cycle does not merely loop a renderer; it makes **ownership** circular, and single-owner write-back is what the whole propagation model rests on. The path form is the load-bearing half: a cycle reported as `True` is a cycle nobody can locate, and therefore a cycle nobody fixes.

### RULE R-feed-03 — Every name in a `feeds:` list resolves to an anchor (stated)

A pass refuses, naming the offending string, when a declared source matches no anchor under the scanned root.

**Check pattern:** stated; guard test `test-f313-stone.py` case N — an anchor declaring `feeds: SRC, TYPPO` refuses the pass, quotes `TYPPO` in the message, and writes nothing.

**Why:** this is the least visible of the three invariants and the reason the other two are not enough. An unresolvable source supplies zero items and is **indistinguishable from a source that happens to be empty**, so without an explicit check a typo'd feed edge is invisible forever — the anchor simply never receives anything and nothing ever says why. See [[project_a_threshold_detector_proves_a_vacuous_zero]].

### RULE R-feed-04 — A pass reports its counts, including when they are zero (stated)

Any pass that walks the feed DAG prints what it did and how much it looked at — files written, items moved, anchors visited — and prints it on a run with nothing to do just as on a busy one.

**Check pattern:** stated; guard test `test-f313-stone.py` case O — a pass over a single anchor with no work exits 0 and still prints `0 control file(s) written … across 1 anchor(s)`.

**Why:** the vault's most repeated defect shape. A pass that prints nothing when it does nothing is indistinguishable from a pass that never ran, so the one moment the report is most needed — *"did it look?"* — is the one moment a silent pass cannot answer. "No findings" is only meaningful beside "and here is how much it examined".

## Position in the catalog

Sits under the discipline rulesets beside [[R-stream]], as the enforcement half of a discipline rather than of a facet. Its subject is the second corpus-level graph over the anchor set — same nodes as [[DAS anchor-dag]]'s containment graph, different edges, its own invariants. Distinct from [[R-stone]], which governs the facet whose items travel these edges: R-feed never names a kind, and R-stone never names an edge.

## Adoption

Cited by [[DAS feed]] and by [[DAS Stone]], whose `stone` pass is the one live implementation of the invariants above. Not pulled by [[R-facet]] — see the header.

## See also

- [[DAS feed]] — the discipline this ruleset enforces.
- [[DAS anchor-dag]] — the containment graph; the sibling this one was opened beside.
- [[DAS Stone]] / [[R-stone]] — the facet that travels these edges.
- [[DAS Dot Anchor]] — the field-set index where `feeds:` is registered.
- [[DAS Rulesets]] — top-level catalog.
