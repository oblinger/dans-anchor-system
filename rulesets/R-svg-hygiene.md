# RULESET R-svg-hygiene
description:: File-format hygiene for hand-authored SVG diagrams.
include::
import:: skills/audit/scripts/audit-plan.py
where:: `{anchor}/**/*.svg`

> **Two checkers wired and the set's missing selector added, 2026-08-11 ([[Tink Backlog#^T349|T349]]).** `svg_no_orphan_defs` and `svg_validates_xml` sat registered and invoked by nothing while `-02` and `-03` read `(checked)` — the last two orphans of the walk with a rule of their own to serve. Measured over all **127** vault SVGs before wiring: `-02` finds **2** (`arrowhead`/`arrowthin` in an SV streaming diagram, `arr-leaf` in a Viz Bench render), `-03` finds **1** ([[ANC API]]`.svg`, which `xmllint` rejects at line 21). Small, true, and each names a specific dead or malformed thing.
>
> **The set declared no `where::`, and that — not the checkers — is what made wiring unsafe.** With no selector a set inherits `always`, so both rules would have run on every markdown file in the vault and answered `error`, *"not an SVG file"*, on each — a checker-malfunction verdict on ~7,800 documents whose only fault is not being a diagram. Four of the nine sets in the [[R-diagram]] family already carry an `.svg` selector and four carry none ([[R-sugiyama]], [[R-tufte-data-ink]], [[R-bringhurst-typography]] and the umbrella); this set now uses the majority form, `{anchor}/**/*.svg`, matching [[R-svg-jiggle]], [[R-diagram-geometry]] and [[R-c4]]. [[R-wcag-contrast]]'s `file:*.svg` is a fifth spelling of the same intent and is left as found.
>
> **The wiring is latent, and that is worth stating plainly.** [[R-diagram]] is an **inert umbrella** — `audit-plan.py` resolves [[R-doc]] and [[R-anchor]] and nothing else, so R-diagram's `include::` arms none of its seven children ([[Tink Backlog#^T208|T208]]). These two rules will not fire until that umbrella is armed. They are wired anyway because the alternative is leaving a checker orphan for a reason that has nothing to do with the checker: an orphan reads to the next author as *unimplemented*, and this one is implemented, measured and correct.
>
> **`svg_title_or_legend` is refused, and it belongs to [[R-c4]]-02, not here** — the refusal is recorded there with its measurement.

> [!info] Provenance
> Internal — no external citation. File-format hygiene baseline drawn from W3C SVG 1.1 / 2 specification (well-formed XML, `id` attribute conventions, `<defs>` referencing) and tooling lore (xmllint as the reference validator). The baseline a diagram has to meet before any higher-level rule applies — a malformed SVG isn't a diagram at all.

Stable IDs on every element, no orphan `<defs>` entries, SVG validates as XML.

Factored from [[R-diagram]] 2026-06-09.

### RULE R-svg-hygiene-01 — Stable IDs on every element (sampled)

Every interactive or stateful SVG element (rects, paths, text used as labels) has an `id` attribute. IDs are meaningful (e.g., `id="scheduler-box"`, not `id="rect42"`).

**Check pattern:** enumerate elements lacking `id`; flag. Future: heuristically detect machine-generated ID patterns and flag.

**Why:** stable IDs are required for any future tooling that wants to reference specific elements (interactive overlays, automated audit feedback, regression testing).

### RULE R-svg-hygiene-02 — No orphan `<defs>` entries (checked)
check:: svg_no_orphan_defs

Every `<marker>`, `<linearGradient>`, `<filter>`, etc. defined under `<defs>` is referenced by at least one rendered element (via `marker-end`, `fill="url(#…)"`, etc.).

**Check pattern:** enumerate all `id`s under `<defs>`; verify each is referenced by some attribute elsewhere in the document.

**Why:** dead `<defs>` accumulate during iteration; they bloat the file and create confusing "what's this for?" moments on later edits.

### RULE R-svg-hygiene-03 — SVG validates as XML (checked)
check:: svg_validates_xml

The SVG file parses as well-formed XML with no warnings under `xmllint --noout`.

**Check pattern:** `xmllint --noout {file}.svg` returns exit code 0 with no stderr output. Where `xmllint` is absent the checker falls back to the stdlib XML parser and says so in the verdict — the weaker test is named rather than silently substituted.

**This is the baseline every other diagram rule stands on, which is why `-02` defers to it.** An unparseable file has no `<defs>` to audit, so `-02` answers `pass` with a pointer here instead of reporting the same broken file in the *checker malfunctioned* voice.

**Why:** the absolute baseline. A malformed SVG isn't a diagram at all.
