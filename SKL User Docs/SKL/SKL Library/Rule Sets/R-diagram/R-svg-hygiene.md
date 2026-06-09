# RULESET R-svg-hygiene
description:: File-format hygiene for hand-authored SVG diagrams.
include::

Stable IDs on every element, no orphan `<defs>` entries, SVG validates as XML. The baseline a diagram has to meet before any higher-level rule applies — a malformed SVG isn't a diagram at all.

Factored from [[R-diagram]] 2026-06-09.

### R-svg-hygiene-01 — Stable IDs on every element (sampled)

Every interactive or stateful SVG element (rects, paths, text used as labels) has an `id` attribute. IDs are meaningful (e.g., `id="scheduler-box"`, not `id="rect42"`).

**Check pattern:** enumerate elements lacking `id`; flag. Future: heuristically detect machine-generated ID patterns and flag.

**Why:** stable IDs are required for any future tooling that wants to reference specific elements (interactive overlays, automated audit feedback, regression testing).

### R-svg-hygiene-02 — No orphan `<defs>` entries (checked)

Every `<marker>`, `<linearGradient>`, `<filter>`, etc. defined under `<defs>` is referenced by at least one rendered element (via `marker-end`, `fill="url(#…)"`, etc.).

**Check pattern:** enumerate all `id`s under `<defs>`; verify each is referenced by some attribute elsewhere in the document.

**Why:** dead `<defs>` accumulate during iteration; they bloat the file and create confusing "what's this for?" moments on later edits.

### R-svg-hygiene-03 — SVG validates as XML (checked)

The SVG file parses as well-formed XML with no warnings under `xmllint --noout`.

**Check pattern:** `xmllint --noout {file}.svg` returns exit code 0 with no stderr output.

**Why:** the absolute baseline. A malformed SVG isn't a diagram at all.
