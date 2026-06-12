---
description: Default rules for finding a software project (canonical URL, install vector, license-and-pricing) — ships with the skill. User overrides in SRC rules/.
---
# find-software — default rules

Default rules for `find` on noun-type **software** — pinning a specific software project, its canonical home page, and how to install it. Ships with the skill; user overrides in `[[SRC rules/find-software|SRC rules/]]`.

Software is **like product, with the purchase action optional** — most software has either a free install path (OSS / freemium) or a paid one (SaaS / commercial license). The find resolves *which path applies*, not just *where to buy*.

## Default sources for identification

**Open-source / dev tools**: GitHub canonical repo (stars + last commit + license) → package-manager registry (npm, PyPI, crates.io, Homebrew, apt) → official site if separate from repo → awesome-* curated lists for category placement.

**SaaS / web apps**: vendor's `.com` (often the canonical) → G2 / Capterra for plan reality → product-hunt for launch-era context → company LinkedIn for org-size signal.

**Desktop / mobile apps**: Mac App Store / Microsoft Store / Setapp / vendor site → official download page → category-specific review sites (MacStories, Android Authority, etc.).

**CLI tools**: `brew search` / `apt search` / GitHub topic — the install command IS the canonical reference for these.

## Default behavior

- **Pin the exact project + version** — for software, naming collisions are common (multiple "foo" projects on npm vs PyPI vs GitHub). Disambiguate by registry namespace + URL.
- **Resolve the install vector** — the actionable artifact is *how the user gets it running*: `brew install X` / `npm install X` / a download link / a SaaS signup URL. Include this verbatim in the lookup.
- **Note the license and pricing model** — open-source license (MIT / Apache / GPL / proprietary), or pricing tier (free / freemium / paid / subscription). The user's next decision depends on this.
- **`find-product`'s purchase-button rule does NOT apply universally to software** — many candidates are free. Falling back to "manufacturer info page" is fine when there is no purchase action because there is no purchase.

## Default disambiguation

- **Namespace collisions** — `react` on npm is one thing; `React` on iOS App Store is another. Always include the namespace in the identifier.
- **Forks vs canonical** — for forks-with-traction (Bun ≠ Node, Bun fork-of-Node), pin which lineage the user wants.
- **Open-source vs commercial fork** — e.g., Elasticsearch vs OpenSearch, MySQL vs MariaDB, Redis vs Valkey. Surface both when relevant.
- **Discontinued / abandoned** — `last commit > 2 years` for a non-stable-stable project is a fork-flag; note it.

## Default output (the saved lookup)

- Canonical project name + namespace (`github.com/<org>/<repo>` or `npm:<pkg>` or `<vendor>.com/<product>`)
- Maker (org / corp / sole maintainer)
- License + pricing model (Free OSS / Freemium / Paid / SaaS subscription)
- Install / signup vector (the actual command or URL that gets the user running)
- Canonical URL (`<vendor>.com` for SaaS; GitHub repo for OSS; App Store URL for apps)
- Star count + last release/commit date (for OSS) — staleness signal
- Pricing tier landing page URL (when paid)
- Major alternatives (Wikipedia "alternatives to X" or category subreddit)

## When to escalate to a different verb

If the user asks "what's the best X for Y" — that's not `find`, it's `survey` (multi-software comparison) or `profile` (one-software deep profile).

## Hand-off

This skill resolves the canonical identifier and install vector. For full evaluation (architecture, license fit, ecosystem signal), continue with [[profile/SKILL|/profile]]. For category comparison, use [[survey/SKILL|survey]].

## User rules

(Empty — user adds in `SRC rules/find-software.md` to override these defaults.)
