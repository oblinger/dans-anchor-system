---
description: Meta-survey methodology — three composed surveys (sources, dimensions, items) plus cell-certainty notation for triangulated answers.
---
# Meta-Survey — Three-Stage Methodology

The **meta-survey** is the high-rigor form of `/survey`. It treats the comparison as three composed surveys run in sequence: first survey the **sources** that cover this domain, then survey the **dimensions** that matter for this kind of item, then survey the **items** themselves — with every cell carrying a **certainty annotation** that reflects how much corroboration the agent found.

Use when the stakes justify it: the user is about to commit (purchase, adopt, hire, publish), the domain is contested or rapidly changing, sources disagree, or "we got it wrong" has a real cost. For quick orientation, the standard [[survey/SKILL|/survey]] runbook stays as-is.

Invocation: `/survey meta <noun> — <topic>` (e.g., `/survey meta software — feature-flag libraries for Go services`). The single-stage runbook stays the default for `/survey <noun>`.

## Why three stages

A standard survey conflates three things into one pass: *whose claims are we trusting*, *what are we comparing on*, and *what are the values*. When the stakes are low this is fine — you trust the obvious source aggregators and the obvious dimensions and fill the table. When the stakes are real, conflating these three steps hides the assumptions doing the load-bearing work. Splitting them surfaces each judgment for inspection and produces an auditable comparison the user can later return to and trust.


## Stage 1 — Source survey (survey of sources)

Survey the **sources of information** for the target domain. Output is a ranked roster of sources the next two stages will draw from.

**Default dimensions for sources:**

| Dimension | Sub-axes |
|---|---|
| **Trustworthiness** | Business model (incentive alignment — affiliate? vendor? independent? academic? government?); community reputation (subreddit / HN / industry chatter); editorial record (corrections policy, retractions); track record on this domain specifically. |
| **Accuracy** | Effort signal (depth of articles, evidence of testing / first-hand experience); cross-checkability (do they cite primary sources? are their numbers reproducible?); past hits and misses (calls that turned out right vs wrong). |
| **Completeness** | Breadth of coverage in the domain; depth per entry; freshness (how stale is their data); gaps (what categories they skip). |
| **Independence (when sub-axis to Trustworthiness)** | Editorial-from-business separation; affiliate disclosure quality; whether the same org sells what it reviews. |

The agent enumerates candidate sources (Google + targeted searches: `"best X" site:reddit.com`, awesome-* lists, academic surveys, industry analysts, established review brands, vendor sites for first-hand spec data), then rates each across the three dimensions. Output: a table ranking sources, with a clear top tier the next stages will trust most.

**Anti-pattern at Stage 1**: defaulting to "the SEO-winning site for this category" without questioning incentive alignment. The point of Stage 1 is to make that questioning explicit.


## Stage 2 — Dimension survey (survey of dimensions)

Using the trusted sources from Stage 1, survey the **dimensions** that actually matter for this kind of item. Output is a ranked list of dimensions that becomes the column set for Stage 3.

**Default meta-dimensions on each candidate dimension** (these are the columns of Stage 2's table — dimensions about dimensions):

| Meta-dimension | What it measures |
|---|---|
| **Source coverage** | How many of Stage 1's trusted sources treat this as a column? |
| **Source prominence** | Where does it land in their criteria — top-3, mid-pack, footnote? |
| **Discriminative power** | Does this dimension actually separate the candidates, or is it a rubber-stamp ("does the product exist? yes")? |
| **User-fit** | How well does this dimension match what the user said they care about (their stated constraints + budget + use case)? |
| **Measurability** | Can the agent get a defensible value into each cell, or is this dimension fuzzy/aspirational? |

The agent reads the trusted sources, harvests their dimensions, deduplicates synonyms, scores each candidate dimension across the meta-dimensions, then **ranks**. Top N (5-7 for Standard, 10+ for Deep) become the Stage 3 columns.

**Anti-pattern at Stage 2**: picking dimensions the agent thinks should matter without checking what the trusted sources actually emphasized. The whole point of Stage 1's source ranking is that those sources' editorial judgment about *what to measure* is part of what we're trusting.


## Stage 3 — Item survey (survey of items, with certainty annotation)

Run the actual comparison: rows are the items, columns are the dimensions from Stage 2, sourced from the trusted set from Stage 1. The structural difference from a standard `/survey`: **every cell carries a certainty annotation** that reflects how much corroboration the agent found across the Stage 1 sources.

Process per cell:
1. Look up the value in each Stage 1 source that covers this item × dimension.
2. If multiple sources covered it: do they agree? Within tolerance?
3. Compose a single cell value + certainty annotation per the scheme below.
4. Record the source list per cell (footnote or inline).

The certainty annotation is the user's mental model of "how much should I trust this cell." A row of `***exceptional*** ★★★` cells is one the user can act on; a row dominated by `???vague???` cells is one to be skeptical about — and the format makes it visible at a glance without reading footnotes.


## Cell-certainty notation

Markdown-friendly. The agent applies the annotation to **the cell value** (not the surrounding cell). Both the format and the meaning are stable across all meta-survey reports.

| Level | Notation | Meaning |
|---|---|---|
| Definitive | `***value*** ★★★` | Multiple primary-source confirmations OR primary source plus authoritative corroboration. The user can act on this. |
| Very high | `***value*** ★★` | Multiple top-tier (Stage 1) sources agree exactly. |
| High | `***value*** ★` | One top-tier source states it, no other source contradicts. |
| Confident | `**value**` | Single trustworthy source; not contradicted but not corroborated either. |
| Baseline | `value` | Stated by a Stage 1 source with adequate sourcing — the implicit standard. |
| Slight doubt | `?value?` | Thin sourcing OR sources disagree on a minor axis. |
| Significant doubt | `??value??` | Conflicting sources; reasonable people would land on different values. |
| Speculative | `???value???` | Rumor, single low-tier source, or no live sourcing — included only because the dimension demands a value. |

**Composing the markers:** Stars trail the value (with a space). Question marks wrap the value tightly. Multi-word values still get one set of markers around the whole — `?value with words?`, not `?value? ?with? ?words?`.

**Combined claims** (numeric range + qualitative tag): annotate each independently if their certainty differs — `**$50-$100** but ?freemium tier disappears at 100 users?`. The user can see the price is confident but the freemium-tier claim is shakier.

**Empty cell**: `—` (em-dash). Distinct from low certainty — em-dash means *the agent looked and found no source claim*, not *the claim is weak*. Don't conflate.

**Footnote per cell**: every cell — at any certainty level — gets a source attribution. The certainty annotation does NOT replace the source citation. In the Sources section at the end, list URLs grouped by cell or by source-cluster.


## Output shape

The standard RRR report shape (per [[survey/rules/survey|survey.md]]) with three appendices for the three stages:

1. **Stage 3 results table** at the top — this is the user's main deliverable, cells annotated per the scheme above.
2. **Interpretive notes** — what's notable, where the table is sparse, where uncertainty clusters.
3. **Stage 1 appendix — Source roster** — the trusted-sources ranking that drove Stages 2-3. One row per source, columns: trustworthiness / accuracy / completeness, plus a one-line note.
4. **Stage 2 appendix — Dimensions considered** — the full dimension candidate list with the meta-dimension scoring; mark which made it into Stage 3 columns and which were dropped (with why).
5. **Sources** — every URL touched, grouped by source-cluster.

These appendices are the auditable record. A future-user (or future-you) can re-open the report and see *which sources were trusted and why*, *which dimensions made the cut and why*, before drawing fresh conclusions from the table.


## Population + depth

| Tier | Sources at Stage 1 | Dimensions at Stage 2 | Items at Stage 3 |
|---|---|---|---|
| Quick meta | 5-7 sources, light scoring | top 5 | top 5-7 |
| Standard meta (default) | 7-12 sources, full scoring | top 5-7 | top 10 |
| Deep meta | 15+ sources, multi-pass scoring | top 10+ | full population within bound |


## When meta-survey is overkill

Don't reach for the meta-survey when:

- The user wants quick orientation, not a commit-this-decision report.
- The standard sources are obvious and well-aligned (no real Stage 1 work to do).
- The dimensions are well-known and stable in the domain (no real Stage 2 work to do).
- The items have clear authoritative data (no certainty annotation needed beyond baseline).

For these, use the standard [[survey/SKILL|/survey]] runbook. Meta-survey's cost (multi-stage execution, source-roster appendix, cell-by-cell certainty annotation) is justified by stake, not by completeness.


## Anti-patterns specific to meta-survey

- **Skipping Stage 1 in a hurry** and trusting whichever sources the search engine returned first. The whole point is auditing the *trust assumption*; defaulting to it negates the methodology.
- **Letting Stage 2 dimensions be the agent's intuition** rather than harvesting what the Stage 1 sources actually emphasized.
- **Uniform certainty across all cells**. If every cell ends up `**bold**`, the agent didn't actually triangulate — they just bolded everything. Real triangulation produces a mix.
- **Annotating the *cell* instead of the *value***. The format wraps the value, not the table cell. `| ***value*** ★ |` is right; `| value |★ ` is wrong.
- **Dropping the source attribution because the cell got annotated**. The annotation summarizes the trust verdict; the citations are still required.


## Composition with noun-rules

Meta-survey runs on top of the noun-rules. When `/survey meta software` runs:

- Stage 2 starts from [[survey/rules/survey-software|survey-software.md]]'s default dimensions (license / pricing model / install vector / etc.) as the *candidate set*, then rescores and reorders based on what Stage 1's trusted sources emphasize for this specific topic.
- Stage 1 inherits source patterns from the noun-rules' "Default sources" section as candidate sources, then rates and prunes.
- Stage 3's cell shape (link in column 1, license/pricing visible up front) follows the noun-rules' default output table shape.

This means meta-survey *enriches* the noun-rules' defaults; it doesn't replace them. The noun-rules tell the agent where to look and what columns to start from; meta-survey adds the rigor of explicit source-judgment, explicit dimension-judgment, and explicit per-cell trust-judgment on top.
