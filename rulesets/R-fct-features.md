# RULESET R-fct-features
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file: **/Features/F*.md, **/* Features/F*.md, F* — *.md, **/{slug} Features.md`
description:: The rules every Features-facet instance must satisfy — covering the folder layout, filename pattern, the two-zone feature-doc structure, and the index page shape. Embedded per F133. Tier legend: **checked** (mechanically verifiable), **sampled** (spot-checked), **stated** (author-honored principle).

**The `where::` needs three feature-doc terms, and the reason is worth reading before simplifying it back down** (T101, 2026-08-01). As shipped this selector was `**/Features/F*.md` — a path segment spelled exactly `Features` — and it matched **zero files in the whole vault**, because the documented location is `{slug} Features/`. Every rule here was inert, and silently: a selector that matches nothing produces no verdicts, so no surface ever said so. `**/* Features/F*.md` fixes that for the ordinary case. The third term, `F* — *.md`, covers a case the first two structurally cannot: **18 `* Features/` folders are themselves anchors** (`DKT Features`, `SKA Features`, `SVP Features`, `LUMEN Features`, …), and `where::` globs match *anchor-relative* paths, so inside one of those the path of a feature doc is a bare `F223 — Title.md` with no directory component left to match. Anchoring on the `F<n> — Title` filename is what reaches them; the looser `F*.md` was measured first and rejected, admitting 135 non-feature docs (`Fun.md`, `Friday.md`, `FAANG.md`). Measured after: **668 docs in scope, 23 findings.**

### RULE R-fct-features-01 — F-numbered filename pattern (checked)
Each individual feature doc filename matches `F<NNN> — <Title>.md` where `<NNN>` is a zero-padded three-digit decimal number unique within the anchor. Dated `YYYY-MM-DD <Title>.md` filenames are legacy — do not author new ones.
**Check pattern:** filename matches `^F\d{3} — .+\.md$`.
**Why:** the F-number is the stable cross-reference key; padded triple digits keep filename sort equal to numeric sort and distinguish per-anchor feature series from each other.

### RULE R-fct-features-02 — Open Questions is the first H2, below the H1 (checked)
While pending Qs exist, a feature doc's `## Open Questions` H2 (with its `### Resolved` H3 beneath) is the **first H2 in the file** — immediately below the `# [[{slug}]] · F{n} — {Feature Name}` H1 and its one-line orientation prose (per [[F241 — Questions block below H1 + state-stamped integrity hash|F241]], 2026-07-15; supersedes the earlier above-the-H1 placement). When zero Qs are pending the block is deleted entirely (Phase 2) — it is not kept as an empty placeholder.
**Check pattern:** if a `## Open Questions` H2 is present, it is the first `## ` heading in the file and follows the `# ` H1; resolved Qs live under a bottom `## Resolved` H2.
**Why:** blocking decisions must be visible the moment the reader passes the head, without forcing the file into an outline-breaking above-the-H1 shape; the state script's integrity stamp (R-state-region-03 / audit-q C48) keeps the block script-managed.

### RULE R-fct-features-03 — H1 carries anchor-slug breadcrumb (checked)
check:: h1_present
The feature-doc H1 reads `# [[{slug}]] · F{n} — {Feature Name}` — a wiki-link to the anchor page, a middle dot, and the feature title. The filename matches the title portion without brackets: `F{n} — {Feature Name}.md`.
**Check pattern:** H1 matches `^# \[\[.+\]\] · F\d+ — .+$`. The wired `h1_present` action is a **lower bound on this rule, not the whole of it** — it asserts the doc has a head H1 at all, which every violation of the breadcrumb form above also violates, and leaves the form itself to reading. The weaker action is deliberate: a regex for the full form would fail every pre-breadcrumb feature doc in the corpus at once, which is a migration and not an audit finding. (R-decisions-02 wires the same action against a stricter prose form for the same reason.)
**Why:** the `[[{slug}]]` breadcrumb lets the reader jump back to the anchor page and immediately see which anchor they're in — load-bearing when many anchors are active and feature docs look similar across them.

### RULE R-fct-features-04 — Index page lists features reverse-chronologically with status brackets (sampled)
The `{slug} Features.md` index page lists features newest-first. Each row is a wiki-link `[[F<NNN> — <Title>]]` followed by the lifecycle state in backtick-brackets (e.g. `` `[Done]` ``), an em-dash, and a one-line description. The lifecycle state in the index mirrors the `## Status` section of the feature doc.
**Check pattern:** index rows match `- \[\[F\d+ — .+\]\] \`\[.+\]\` — `.
**Why:** the index is the navigation surface; backtick-brackets make lifecycle state scannable at a glance without opening each feature doc.
