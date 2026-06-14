# RULESET R-doc
include:: [[R-markdown]], [[R-file-association]], [[R-ruleset]], [[R-brief]], [[R-discussion]], [[R-log]], [[R-messages]], [[R-query]]
description:: Everything checked when auditing a document — markdown + file conventions plus the doc-facet rulesets (Ruleset, Brief, Discussion, Log, Messages, Query).

The umbrella that **`/audit doc <path>`** resolves ([[F161 — Rule-driven audit engine — resolve, run, judge|F161]]). The convention sets (`R-markdown`, `R-file-association`) apply to every document (`always`); the doc-facet sets fire only on their `where::` targets — a `# RULESET` block → `R-ruleset`, a `# BRIEF` → `R-brief`, a Discussion heading → `R-discussion`, a `* Log.md` → `R-log`, a `* Messages.md` → `R-messages`. Add a doc facet's ruleset to the `include::` line to bring it into `/audit doc`.
