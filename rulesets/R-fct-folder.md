# RULESET R-fct-folder
include::
where:: `file: **/.anchor`
description:: The rules every anchor folder must satisfy — a named directory containing a marker file whose name matches the folder exactly.

> **NOT ARMED 2026-08-11 ([[Tink Backlog#^T349|T349]]) — three of its four rules have nothing to add, and the fourth has 12 subjects.**
>
> **The selector cannot match.** `where:: file: **/.anchor` is the class-(a) form measured on [[R-code-repository]]: anchor-mode scope is built from `target.rglob("*.md")`, so a `file:` selector naming a non-`.md` path resolves to the empty set and the whole ruleset drops out of `plan["groupings"]` with nothing reported. This set is the third of the five carrying it. Unlike R-code-repository, repairing the selector to `anchor` would not make arming worthwhile — the rules are the problem here, not the aim.
>
> **`-01` is a verbatim duplicate of an already-armed rule.** It asserts that `{slug}/{slug}.md` exists; [[R-anchor-page]]-02 is armed, wired to `chk_entry_page_matches_slug`, and that checker's **first branch returns `fail` with *no entry page*** when the file is absent. Its `_entry_page` resolves `{slug}.md` then `{folder}.md` — the same two candidates in the same order this rule's check pattern names. Measured across the vault 2026-08-11: **96 of 1,395 anchors have no entry page**, and R-anchor-page-02 already reports every one of them. Arming `-01` would double-report 96 findings and add no coverage.
>
> **`-02` is the only rule with independent content, and it is small.** Redirect stubs are rare: of 1,395 anchors, **433 entry pages carry no H1 at all, but only 12 are `(See [[…]])` redirects**, and **9** of those carry more than the single permitted line (`_/_.md`, `SV/QQ`, three `SV/ww/` year-prefixed pages, `Topic/FIN/FIN Flows`, and two under `Topic/`). A real rule with a real corpus — and it has **no `check::` line** while reading `(checked)`, so arming it as written promotes it to a billed LLM judgment on all 1,395 anchors to ask 12 questions. Arming it correctly means giving it a checker and moving it to [[R-anchor-page]], where the `anchor` selector already works and its sibling rules about the entry page already live; it does not mean arming this set.
>
> **`-04` asserts the definition rather than a constraint.** *"Sub-folders inside the anchor are not themselves anchor roots unless they carry their own independent marker"* — but carrying its own marker is exactly what makes a folder an anchor ([[R-anchor-page]]-01: the declaration alone makes the anchor), and `sub_anchor_roots` already excludes such folders from the parent's scope. The rule is satisfied by construction for every folder in the vault, which is why it can be `(checked)` with no check pattern that could ever fail. `-03` is `(sampled)` and unaffected either way.
>
> **The orphan checker that looks like `-01`'s missing half is dead code.** `--verify-registry` lists `folder_marker_exists`, registered and invoked by nothing, and its docstring is this rule almost word for word. It resolves the marker as `{folder}/{folder}.md` — **by folder name, ignoring `slug:`** — where `_entry_page` tries `{slug}.md` first. Measured 2026-08-11: it fails **130** of 1,395 anchors, and **34** of those are anchors whose page is correctly slug-named (`SV/ww/Auto SV/` → `ASV.md`, `SV/ww/svar-docs/` → `SVAR.md`). The other 96 are exactly the set `entry_page_matches_slug` already reports. So it contributes **zero true findings and 34 false ones**, and the false class is the slug-named anchor — the form the rest of the engine is built around. It also `rglob`s the entire subtree per anchor while `sub_anchor_roots` has already dropped nested anchors from scope, so wiring it would re-report every nested anchor from its parent as well. Not a rule waiting to be written.
>
> **Disposition:** leave dormant. The live content is one rule with 9 findings, and its home is R-anchor-page.

### RULE R-fct-folder-01 — Marker file exists and name matches folder (checked)
Every anchor folder contains a markdown file whose basename equals the folder's own name (e.g. `My Project/My Project.md`).
**Check pattern:** `{slug}/{slug}.md` exists inside the anchor root.
**Why:** the marker file is how any tool or human identifies a directory as an anchor; without it the folder is just a folder.

### RULE R-fct-folder-02 — Redirect stub is one-line only (checked)
When the marker file is a slug-redirect stub (folder name ≠ anchor name), the body is a single line `(See [[slug]])` with no additional content.
**Check pattern:** if the marker does not begin with `# `, its entire non-blank content is a single `(See [[…]])` line.
**Why:** a stub that grows content blurs the redirect form with the anchor-page form; the two shapes must remain distinct.

### RULE R-fct-folder-03 — Parent-anchor naming conventions are honored (sampled)
The folder name follows any naming convention imposed by its parent anchor (e.g., a PP child carries a `YYYY ` year prefix).
**Check pattern:** spot-check child anchors against their parent's declared naming pattern.
**Why:** naming conventions cascade so that a parent anchor can enumerate or group its children predictably.

### RULE R-fct-folder-04 — Anchor folder is the single root (checked)
There is exactly one root folder per anchor; sub-folders inside the anchor are not themselves anchor roots unless they carry their own independent marker.
**Check pattern:** only one `.anchor` or marker file at the root level of the anchor (nested anchors must have their own independent marker).
**Why:** a single unambiguous root prevents two-root anomalies where tools disagree on which folder is the anchor.
