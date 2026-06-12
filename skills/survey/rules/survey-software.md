---
description: Default rules for surveying software in a category — ships with the skill. User overrides in SRC rules/.
---
# survey-software — default rules

Default rules for `survey` on noun-type **software**. Ships with the skill; user overrides in `[[SRC rules/survey-software|SRC rules/]]`.

Software surveys are **like product surveys, with one structural difference**: the "purchasable link verification" requirement from [[survey-product]] is **NOT mandatory** — many strong candidates are free OSS where the actionable artifact is `brew install X` or a GitHub URL, not a Buy button. Replace the purchasable-link gate with an **install-vector-resolution** gate (every row resolves to an install path: command, signup URL, or download).

Applies to: "best Postgres clients", "compare LLM observability tools", "open-source feature-flag libraries", "Pomodoro apps for Mac", "Kubernetes ingress controllers", "agent frameworks under MIT/Apache".

## Default dimensions per sub-type

**Open-source library / framework**: Name (link to repo), maker, license, language / runtime, stars, last release, key capability, top 3 alternatives, install command.

**Self-hostable OSS app**: Name (link), license, deployment story (Docker / managed / install script), maintainer (org / sole-maintainer + commercial backer), stars, last release, hosted-offering URL (if any).

**Open-core**: Name (link), OSS license, paid tier price, what's gated behind paid, free-vs-paid capability split.

**Pure SaaS**: Name (link), category, published price + real-if-known, free trial / freemium scope, target persona, key feature differentiator, top 3 alternatives, lock-in / data portability note.

**Consumer software / apps**: Name (link), platform, free tier?, subscription tier(s), rating (recency-weighted), key differentiator, last major update.

## Default sources per sub-type

- **OSS libraries / frameworks**: GitHub topic browsing → awesome-* lists → language-specific aggregators (Crates.io / PyPI trending) → category subreddits and HN search.
- **Self-hostable apps**: awesome-selfhosted → r/selfhosted → vendor sites.
- **Open-core / commercial OSS**: G2 / Capterra for the SaaS view; GitHub for the OSS view; both feed the same row.
- **Pure SaaS**: G2 / Capterra / TrustRadius / Gartner / Forrester / HN / category subreddits.
- **Consumer apps**: App Store / Play Store + category-specific blogs and subreddits.

## Default behavior

- **Resolve an install vector for every row** — the actionable artifact for each candidate. Acceptable forms:
  - `brew install X` / `npm install X` / `pip install X` / `cargo install X` (registry-resolved install)
  - GitHub URL with a clear "Installation" section in the README
  - SaaS signup URL (clearly priced page; not a "Contact Sales" wall, unless the category is enterprise-only)
  - App Store / Play Store URL for mobile / desktop apps
- **Surface license + pricing model in the table** — both are decisive for software choice; the free-vs-paid bucket alone changes whether a row even applies.
- **Weight maintenance signal over absolute stars** — last commit date + open-issue burn-down + release cadence beat star count for "is this alive."
- **Surface bus factor** for OSS — one-maintainer projects get a flag in the table or a note.
- **For open-core**, surface what's gated behind paid — the OSS surface is often less capable than the marketing implies.

## Default population

- **Software candidates**: 10 (top 10) by default. User can override.
- **Sources consulted**: 5-10 by default (GitHub topic + 1-2 awesome lists + 2-3 review aggregators + 1-2 community subreddits / HN searches).

## Workflow specifics

1. **Understand the need** — gather constraints (language / runtime, hosting model, license fit, budget, scale).
2. **Locate the category roster** — use awesome-* lists, GitHub topic, and 2-3 review aggregators to enumerate candidates.
3. **Identify dimensions** — from category-source consensus (e.g., what columns do awesome-feature-flags or G2's feature-flag category use?).
4. **Select top 10** based on roster + community signal.
5. **Phase 4.5 — install-vector resolution (REQUIRED)** — replaces [[survey-product]]'s purchasable-link gate; see below.
6. **Write the report** — RRR shape (per [[survey/rules/survey|survey.md]]) plus `## Key Dimensions`, `## License + Pricing Overview`, `## Maintenance Signal` sections.
7. **Surf everything** — open all candidate URLs in browser (`open "<url>"`).

## Phase 4.5 — Install-vector resolution (REQUIRED)

For every row in the comparison table, the URL in the first column MUST point to a page from which the user can immediately get the software running. A page that:

- Shows installation instructions OR a clear download link OR a Sign-Up / Start-Free button (for SaaS).
- Reflects the canonical / current version (not a deprecated install path for a renamed package).
- Is not "Contact Sales only" for sub-enterprise categories.

Acceptable link types, in order of preference:

1. **GitHub repo with a clear "Installation" / "Getting Started" README section** — best for OSS libraries / frameworks.
2. **Package-manager listing** (npm / PyPI / crates.io / Homebrew formula) — when the registry is the canonical install path.
3. **Vendor landing page with explicit pricing + signup** — for SaaS, the pricing page is usually better than the homepage.
4. **App Store / Play Store URL** — for mobile / desktop apps.
5. **Vendor info page (no install action)** — fallback ONLY when the project is in a state where installation isn't currently possible (pre-release, archived). Annotate `(info page — not installable at time of writing)`.

This gate is the software analogue of [[survey-product]]'s purchasable-link rule: the goal is to enable a *can-I-get-this-running-today* decision, not present a brochure.

## Hunt-before-find (workflow note)

Surveying a software category broadly (this skill) should precede pinning a specific project ([[find-software]]). Output: "based on the survey, the top candidate is X (link to find for canonical URL + install-vector details)."

## Meta-survey for novel categories

For a software category not surveyed before, **run meta-survey first** (per [[describe/SKILL|skill methodology]]). Look at how the most-cited reviewers in that ecosystem organize their comparisons — borrow their dimension set.

## Gotchas

- **Star count rot** — high-star, low-activity is dead. Weight recency.
- **License compatibility** — surface license per row; GPL ≠ MIT for downstream use.
- **Acquisitions and license changes** — note any recent acquisition / license-change events (BSL, SSPL, Elastic-license precedents).
- **Open-core gating** — confirm the OSS-vs-paid feature split per row.
- **Single-maintainer risk** — surface bus factor.
- **Renamed / forked** — note OSS / commercial forks when both have traction (Elasticsearch / OpenSearch; MySQL / MariaDB; Redis / Valkey).

## User rules

(Empty — user adds in `SRC rules/survey-software.md` to override these defaults.)
