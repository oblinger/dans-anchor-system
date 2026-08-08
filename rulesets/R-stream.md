# RULESET R-stream

include:: [[R-file-association]] 
import:: skills/audit/scripts/audit-plan.py
where:: `sentinel: ^## \d{4}-\d{2}-\d{2} —`
description:: Rules ADDED by the dated specialization on top of [[R-file-association]] — newest-first ordering + prepend immutability, the parallel-entry-skeleton invariant, and ISO-date entry-file naming.

Ruleset for the stream specialization ([[DAS stream]]). The **general** association rules (three methods, cardinality→placement, naming, migration, one-form, linkage, folder shape, method declaration) live in [[R-file-association]] and are inherited via the `include::` above (promoted there per F154); only the **dated extras** are stated here. Sits under [[R-doc]] in the catalog.

### RULE R-stream-01 — Reverse chronological, newest-first, prepend-immutable (checked)
check:: dated_entries_reverse_chronological

Entries are ordered newest-first by date; new entries **prepend**, never append; recorded entries are not edited after their decision/outcome lands (the stream is a ledger).

**Check pattern:** parse entry headings (date in `## YYYY-MM-DD — Title` for methods 1/2, or filename `YYYY-MM-DD — Title.md` for method 3); assert dates are non-increasing in document / folder-listing order.

**Why:** a reader's first encounter is "what's the latest thinking / latest event?" — newest-first puts the answer first; prepend-immutability preserves the audit trail.

### RULE R-stream-02 — Parallel entry skeleton declared by the citing facet (sampled)

Every entry within one facet's stream follows the same H3 sub-structure. The skeleton is declared by the citing facet (Discussion → Problem / Options Considered / Decision; Log → its own shape). The discipline mandates uniformity; the facet defines the shape.

**Check pattern:** sample entries within one facet's stream; assert the same H3 set appears in the same order; flag entries missing a required H3.

**Why:** uniform skeletons make the stream scannable. Reading a third entry should not be a fresh navigation problem.

### RULE R-stream-03 — Dated entry-file naming (method 3) (checked)
check:: dated_entry_file_naming

When method 3 is used for a dated stream, each per-entry file opens with an ISO date prefix, then a separator, then the title. **The date prefix is the invariant; the separator is not.** Two separator forms are admitted:

- `YYYY-MM-DD — <Title>.md` — em-dash, **recommended** for new streams.
- `YYYY-MM-DD <Title>.md` — plain space, **accepted**; this is what the corpus actually uses.

**The H1 clause belongs to the citing facet, not to this rule.** Under the em-dash form the H1 matches the title *without* the date. Where a citing facet specifies its own top-of-doc header — [[R-fct-outputs]]-04 and [[R-wp]]-02 both require a `# {date} {name}` H1 — **the facet's rule governs and this rule does not contradict it.** This is the dated specialization of file-association's general sibling-folder shape ([[R-file-association]]-07).

**Check pattern:** for each method-3 dated stream, assert every entry file matches `^\d{4}-\d{2}-\d{2}( —)? .+\.md$`. The H1 sub-check applies only to the em-dash form.

**Why:** the ISO prefix is what buys correct chronological sort in any file listing — that is the whole functional payload, and both separators deliver it. The em-dash was specified as the sole form on 2026-07-17 and **the corpus never adopted it**: measured 2026-08-08 across every method-3 dated stream in the vault (Log, Outputs, WP), **126 entry files use the space form and 0 use the em-dash form.** Narrowing to the em-dash would have required 126 renames — breaking every wiki-link and dispatch row pointing at them — to change a separator that no check ever enforced, while putting this rule in direct contradiction with `R-fct-outputs-02`, `R-wp-02` and `R-log-03`, all three of which already mandate the space form in their own text. A parent rule that 100% of instances and three child rules violate is the rule that is wrong.

## Position in the catalog

Sits under [[R-doc]] (documentation conventions umbrella). Sub-discipline of [[DAS file-association]] (the broader umbrella covering structural patterns for attaching content to a parent). Cited by every facet whose content is a dated entry stream: [[DAS Discussion]] today; [[DAS Log]] pending refactor.

## Adoption

This ruleset is cited explicitly by each facet that uses it (in their `R-<facet>` block, via a delegation note). Not pulled by the [[R-facet]] umbrella — it is a discipline ruleset, not a per-facet ruleset.

## See also

- [[DAS stream]] — sub-discipline spec this ruleset enforces.
- [[DAS file-association]] — parent umbrella discipline.
- [[R-doc]] — documentation-conventions catalog row this set sits under.
- [[DAS Discussion]] — citing facet (doc-scoped, methods 1 + 2).
- [[DAS Log]] — citing facet at the anchor scope (forthcoming refactor).
- [[DAS Rulesets]] — top-level catalog.
