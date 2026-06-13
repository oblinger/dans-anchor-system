# Discover — Walk the vault, find every rule, group by trait

Phase 1 of [[F082 — Common ruleset across projects]]. Sweeps every anchor under `vault_root`, parses every rule from per-anchor `rules/` folders and `*Rules.md` files, attributes each rule to the **nearest enclosing anchor** (avoiding double-counting in nested anchors), groups rules by **trait** (per F090's unified trait taxonomy), and clusters similar rules within each trait by Jaccard similarity.

Emits a normalized markdown report at `~/.config/ob-skills/rule/discovery-report.md` that the user (or `/rule curate`) reads to decide which rules belong in which canonical ruleset.

## When to Use

- Setting up the canonical rule library for the first time.
- Re-discovering when many anchors have changed or new rules have been authored across projects.
- Before a curation pass — the report is the input to `/rule curate`.
- One-off audit: "what rules do I have, scattered across the vault?"

## Runbook

### 1. Run the discovery script

```bash
python3 ~/.claude/skills/rule/scripts/rule-discover.py [--vault PATH] [--threshold FLOAT]
```

Defaults:
- `--vault` → reads `vault_root` from `ob-skills config`, falling back to `~/ob/kmr`.
- `--threshold` → `0.5` (Jaccard similarity for cluster membership).
- Report path → `~/.config/ob-skills/rule/discovery-report.md`.

The script walks the vault, identifies anchors (`.anchor` markers), prunes sub-anchor subtrees (each rule belongs to its **innermost** enclosing anchor), and writes the report.

### 2. Read the report

The report has four sections:

1. **Summary** — total anchors with rules, total rules parsed, multi-rule cluster count, unknown-trait count.
2. **By Trait** — per-trait clusters of similar rules. Clusters with N > 1 are the **candidates** for common rulesets (rules used by multiple anchors with overlapping vocabulary).
3. **Unknown-trait rules** — rules from anchors that don't declare a trait (no `traits: [...]` or `cab-type:` in `.anchor`). Until [[F090 — Retire CAB Types, unify under Traits, Facets-as-Traits-by-file-existence|F090]] ships and anchors declare traits, **expect most rules to land here.** This isn't a failure mode — it's the system reporting honest state.
4. **Anchors without rules** — informational; sampled.

### 3. Decide whether to proceed to curation

- If multi-rule clusters exist within traits, run `/rule curate` to walk them and assemble per-trait rulesets.
- If most rules are unknown-trait (pre-F090), the right next step is to declare traits on anchors first (a manual or scripted pass), then re-run `/rule discover`.

## Output format

```markdown
# Rule Discovery Report — YYYY-MM-DD HH:MM

_Vault: `<path>` · Similarity threshold: 0.50_

## Summary
- **Anchors with rules:** N
- **Anchors without rules:** M
- **Total rules parsed:** K
- **Multi-rule clusters (candidate common rules):** C
- **Unknown-trait rules (no `traits:` / `cab-type:` in `.anchor`):** U

## By Trait

### Code
#### Cluster 1 — <representative-rule-name>
- **<anchor-rel-path>** R07 — Sensors and Effectors Must Be Logic-Free
  > RULE: ...
- **<other-anchor>** R12 — Sensor methods are logic-free
  > RULE: ...

#### Singleton 2 — <rule-name>
- **<anchor>** R03 — ...

### Skill
...

## Unknown-trait rules
- **<anchor>** R<NN> — ...

## Anchors without rules (sampled)
- ...
```

## Discovery rules — what counts as a "rule"

Per [[F082]] Q1 resolution: structured rules only. Two locations per anchor:

1. **`<anchor>/rules/` folder** — any `*.md` inside. Each file contains `### R<NN> — <name>` H3 headings, each followed by a `RULE: <declaration>` line. (Multiple rules per file is standard.)
2. **`<anchor>/**/*Rules.md`** — single-file rule documents anywhere under the anchor (matches `HA Rules.md`, `SVAR Rules.md`, `CAB Rust Rules.md`, etc.). Same H3 + RULE: shape.

The script skips: `.history/`, `Yore/`, `.git/`, `node_modules/`, `__pycache__/`, `.claude/worktrees/`, `.trash/`, `Closet/`.

CLAUDE.md prose, inline conventions in SKILL.md, and unstructured rule-flavored text are NOT included in discovery (per F082 Q1 v1 scope).

## Trait detection

Per [[F082]] Q3 + [[F090 — Retire CAB Types, unify under Traits, Facets-as-Traits-by-file-existence|F090]]: traits are the categorization axis. Each anchor's traits are read from `.anchor`:

1. **Preferred (post-F090):** `traits: [Code, Skill]` (list).
2. **Legacy fallback (pre-F090):** `cab-type: code` → trait `Code` (capitalized).
3. **Neither:** the anchor's rules land in the "Unknown-trait rules" section.

Rules from a multi-trait anchor (Code + Skill) contribute to **both** trait groups.

## Clustering — Jaccard similarity on rule tokens

For each rule, the script computes a token set from `<name> <decl>` (lowercased words ≥ 3 chars, stopwords removed). Two rules cluster together when their Jaccard similarity (`|A ∩ B| / |A ∪ B|`) meets the threshold (default 0.5).

Greedy assignment: each rule joins the first existing cluster whose representative is similar enough, or starts a new cluster.

Tune via `--threshold`: lower → bigger, looser clusters; higher → tighter, more singletons.

## Output home

`~/.config/ob-skills/rule/discovery-report.md` — under the user-data namespace (per [[SKA System Design]] § Per-user parameters). The report is regenerated on every run (destructive).

The eventual **curated rulesets** (output of `/rule curate`) live in `~/.claude/skills/rule/sets/<trait>/<set-name>.md` — that's the **skill-asset** namespace (canonical content, version-controlled with the skills repo). Discovery output is data; rulesets are spec.

## What this skill does NOT do

- It doesn't curate, name, or commit rulesets. That's `/rule curate`.
- It doesn't propagate rules to projects. That's `/rule sync` (deferred to F082 v2).
- It doesn't suggest which sets a project should adopt. That's `/rule suggest` (also v2).
- It doesn't enforce or check rules. That's `/rule check`.

## Related

- [[F082 — Common ruleset across projects]] — the feature this implements (Phase 1).
- [[F090 — Retire CAB Types, unify under Traits, Facets-as-Traits-by-file-existence]] — provides the trait taxonomy this skill groups by.
- `/rule curate` — Phase 2 (consumes this skill's report).
- `/rule consider` — pre-existing; recommends rulesets for a project (different scope: matches existing rulesets to a project's shape, not building the rulesets).
