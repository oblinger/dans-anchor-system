---
description: "the hard cases — one example per thing the base ten don't cover, each naming the language gap it exposes"
---
# Warden Examples Extended

The [[Warden Examples|base ten]] cover every *shape* of a working rule. This file is the other half of the job: the **stress test**. As we rewrite the real rule corpus (~477 rules across the facets, disciplines, and the ruleset library) into Warden, most rules land cleanly in one of the ten shapes. The ones that *don't* land — the cases where writing the rule forces the language to the wall — get an entry here.

Rules on this file are **numbered from 100**, one per genuinely-new case. The title says what is unique about it. A `> [!warning] Gap:` callout names the language insufficiency it exposes — these are the open agenda for extending Warden, collected in one place so we can work them deliberately rather than patch them ad hoc. An example earns a number only when it shows something the existing entries don't.

> [!info] Provenance
> Entries E100–E102 came out of the first gold-standard rewrite — the 14-rule `R-markdown` ruleset ([[DSC markdown]]), chosen because it spans the full mechanical→judgment spectrum and is the direct test of the "native `if::` is a Vale superset" claim. Rule examples are shown as literal Warden source (fenced — the rule audit skips fenced example rulesets). They'll graduate to rendered SVG code-cards (matching [[Warden Examples]]) when the pass industrializes.

## E100 · A mechanical, lossless auto-fix — not a tell

Some rules shouldn't *ask* the agent to fix a thing; they should fix it and say nothing. Trailing whitespace is the cleanest case — stripping it never removes content, so a steer that says "please strip the trailing whitespace" is pure friction. What the rule wants to say:

```
### RULE R-markdown-14 — No trailing whitespace
description:: A line must not end in spaces or tabs.
when:: write:markdown
`file.sub(r'[ \t]+$', '')`        ＃ a floored, lossless line transform — repair in place, emit nothing
```

The same is true of escaping table pipes (R-markdown-01), inserting the blank line a table needs (R-markdown-02), and `--`→`—` (R-markdown-05). In the old model each carried a `fix::` naming a lossless repair. In Warden today they can only be written as **detect → tell**, because the `edit` action's vocabulary is `file.set_frontmatter` and `file.replace_section` — section-grained, structural. There is no verb for a mechanical text transform.

> [!warning] Gap: mechanical-edit verb. The `edit` action can set frontmatter and replace a whole section, but cannot express a floored line/regex transform (`file.sub`, `file.map_lines`) — so lossless auto-fixes degrade to steers. Need either a content-loss-floored text-edit verb, or a way to register a named lossless fixer the way the old `fix::` did. Until then R-markdown-01/02/05/14 detect-and-tell rather than repair.

## E101 · A check too complex to inline — the shared-checker library

A regex check inlines fine (`if:: re.search(...)`). But masking code spans, fences, HTML comments, and curated inline tags before scanning for a stray `<tag>` is fifty lines of parser — you would never inline it, and three other rules in the same set need the same fence-aware scan:

```
### RULE R-markdown-13 — No stray <tag>-like angle brackets
description:: A bare <identifier> glued to a tag-name char is parsed as HTML and eats text to the next >.
if:: `md.stray_angle_tag(file)`
A stray <identifier> is read as an unknown HTML element and silently eats the text up to the next >. ...
```

`md.stray_angle_tag`, `md.unescaped_table_pipe`, `md.fence_holds_renderable_markdown` — these are the ruleset's *own* helpers. Warden specifies the built-in surface precisely (`file` / `anchor` / `git` / `event` / `agent`, the verbs `tell` / `edit` / `deny` / `sh` / `ask_oracle`, ambient Python) — but says nothing about where a ruleset's own reusable Python comes from.

> [!warning] Gap: ruleset helper namespace. Real rulesets ship reusable checker (and fixer) functions; `if::`/body need to call them (`md.*` here). Warden has no notion of a ruleset-scoped helper module — how it's packaged alongside the ruleset, how it's imported into rule scope, and its trust class (presumably same-as-a-skill, since it's the author's code). Without this, every non-trivial check is either un-writable or copy-pasted.

## E102 · A heuristic finding — low-confidence, review-don't-assert

`if::` is a boolean and a prose tell is a *directive*: when the test is true, the agent is told, flatly, to act. But some checks are deliberately imprecise — a cheap regex pre-filter that over-flags, meant to surface a candidate for a human or LLM to judge, not to assert a violation:

```
### RULE R-markdown-04 — References to vault docs use wiki-links, not backticks
description:: A reference to a vault doc is a [[wiki-link]]; backticks are for code identifiers.
if:: `re.search(r'`[^`]+\.md`', file.text)`     ＃ deliberately imprecise — a heuristic pre-filter
A backtick-wrapped string *looks like* a reference to a vault document. If a reader could open it in Obsidian, make it a wiki-link ...
```

The old model marked exactly this with the `(sampled)` tier — "imprecise; sample / flag for review; don't hard-assert." R-markdown-03/04/08/09 were all sampled. The prose can hedge ("looks like"), but the rule still *fires definitively* whenever the regex hits, with no way to say "this one is a guess."

> [!warning] Gap: finding confidence / sampling. Warden has one firing mode — `if::` true ⇒ the tell lands as a directive. There is no dimension for a low-confidence / heuristic finding: no way to mark it review-not-assert, to rate-limit or sample it, or to render it as a soft suggestion rather than a steer. Candidates: a `confidence::` field, a `sample::` rate, or a soft-`tell` variant. (Adjacent to, but distinct from, the re-evaluation economy gate of [[F215 — Re-evaluation economy — the significant-edit gate|F215]], which throttles *expensive* rules; this throttles *uncertain* ones.)

## E103 · A structured-document rule — the dispatch masthead

The dispatch facets (~50 rules across [[FCT Dispatch Table]] and [[FCT Anchor Page]]) all operate on one artifact: the masthead table. `R-dispatch-table-01` wants its rows in a fixed order:

```
### RULE R-dispatch-table-01 — Masthead rows appear in a fixed order
description:: After the breadcrumb, masthead rows occur in order — Related, type, Design, Track, User Docs, Dev Docs — each only if present.
where:: `{ANCHOR}/**/*.md`
if:: `dispatch.masthead_order_violated(file)`
The masthead rows are out of order — reorder them to Related, type, Design, Track, User Docs, Dev Docs.
```

With only `.text` / `.lines` / `.links`, this is unwritable — there's no structured access to tables, and ~50 rules want exactly that one artifact. That drove the resolution: **`file` becomes the root `Section`**, a document a **recursive section tree** with lazy **`.tables`** (`Table.rows`, a 2-D list — robust for a masthead with no real header) — and the structure is **read/write**, so a fix is a floored assignment (`table.rows[0][1] = …`). Dispatch semantics stay in `dispatch.*` helpers reading `.rows`; nothing dispatch-specific enters the language. ([[Warden Semantics]] § `file`.)

> [!success] Gaps G4 + G1 — resolved by one change. **G4** (structured-document access): added the Section tree + lazy `.tables`, ~130 LOC read. **G1** (mechanical-edit verb): the same structure is read/**write** (~40–60 marginal LOC, mostly table re-serialization), so most fixes are floored assignments — no special edit verb. Residual G1: a pure whole-text transform uses the run-class `file.text = …` escape hatch.

## E104 · A cross-file rule — reaching past the trigger

Some checks are about the *tree*, not the file: "exactly one `{NAME} Backlog.md` under the anchor," or "this doc doesn't restate a rule that lives in its facet." They must read other files:

```
### RULE R-backlog-07 — One backlog per anchor
description:: Exactly one {NAME} Backlog.md exists under the anchor root.
where:: anchor
if:: `len(anchor.files("**/{NAME} Backlog.md")) != 1`
This anchor has zero or several backlogs — there must be exactly one {NAME} Backlog.md.
```

The reach is `anchor.files(glob)` (each match loaded as a root `Section`, lazy) and `anchor.doc(path)`. The catch: a rule that reads beyond its trigger is no longer a pure function of `(file, event)` — a sibling change can stale its verdict. Rather than a live cross-file dependency graph, **cross-file rules are audit-passive** — they run at `/audit`, which re-scans the anchor whole.

> [!success] Gap G5 — resolved (scoped). Added `anchor.files(glob)` / `anchor.doc(path)` (cosmetic, ~20 LOC). The structural part — live incremental invalidation of cross-file rules — is consciously deferred to [[Warden Roadmap]] M8; cross-file rules are audit-passive until then.

## The running gap list

| # | Gap | One-line | Status |
|---|---|---|---|
| G1 | mechanical-edit verb | lossless auto-fixes had no edit verb (E100) | **largely resolved** — writable structure (E103); residual = run-class `file.text =` |
| G2 | ruleset helper namespace | a ruleset's own reusable `md.*` / `dispatch.*` helpers (E101) | **resolved** — sidecar `.py` via `helpers:: ./X.py as ns`; namespaced, unit-testable, skill-class trust |
| G3 | finding confidence / sampling | one firing mode; no review-don't-assert / sampled / soft-tell dimension (E102) | open |
| G4 | structured-document access | no structured tables / section tree on `file` (E103) | **resolved** — `file` = root Section + lazy `.tables`, read/write |
| G5 | cross-file reach | rules need to read past the trigger file (E104) | **resolved (scoped)** — `anchor.files()` / `.doc()`; live invalidation deferred to M8 (audit-passive) |

## See also

- [[Warden Examples]] — the base ten (every working shape; start there).
- [[Warden Semantics]] — how the engine runs a rule; the object surface and the actions.
- [[DSC markdown]] — the `R-markdown` ruleset these three came out of (the first gold-standard rewrite).
