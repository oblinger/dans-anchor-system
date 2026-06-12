---
description: Default rules for describing a software project — ships with the skill. User overrides in SRC rules/.
---
# describe-software — default rules

Default rules for `describe` on noun-type **software**. Ships with the skill; user overrides in `[[SRC rules/describe-software|SRC rules/]]`.

Software profiles are **like product profiles, with two structural differences**: (1) the **purchase / pricing card** is conditional — many candidates are free or freemium, so the profile must handle both paid and unpaid; (2) the **ecosystem-and-source signal** is unusually rich (GitHub activity, package downloads, community size, integration list) and replaces some of the review-aggregator structure used for physical products.

## Default dimensions

| Dimension | Notes |
|---|---|
| Canonical name + namespace | `github.com/<org>/<repo>` or `<pkg>` on its registry |
| Maker | Org / corp / sole maintainer; commercial backer (if any) |
| Category + sub-category | Software taxonomy slot |
| License | OSI-approved license / source-available / proprietary EULA |
| Pricing model | Free / Freemium / Paid one-time / Subscription / Open-core (free + paid) |
| Pricing tiers (if paid) | Plan structure, cost per tier, what gates a tier upgrade |
| Language / runtime | Implementation language; runtime requirements |
| Install vector | The actual command / signup URL that gets the user running |
| Key capabilities | The 3-5 capabilities that differentiate within the category |
| Target use / persona | Who it's for; what problem it solves |
| Competitors / alternatives | 3-5 most-considered alternatives |
| Reviews / community signal | Star count + last commit (OSS); G2/Capterra (SaaS); recent reviews (apps); category-subreddit chatter |
| Integrations | Official integrations + plugin ecosystem (when material) |
| Maintenance signal | Last release date; release cadence; open issue count; bus factor |
| Security posture | CVE history; SOC2 / FedRAMP / etc. (B2B SaaS); transparency reports |
| Lock-in / portability | Data export format; API stability; exit cost |

## Default sources (by sub-type)

**Open-source / dev tools**: GitHub repo (README + recent issues + last 5 releases) → package-manager download stats → official site → category subreddits / HN search → awesome-* lists.

**B2B SaaS / paid software**: vendor site (skeptically) → G2 / Capterra / TrustRadius → status page + uptime history → company blog (cadence + scope) → HN / r/SaaS for adoption signal.

**Consumer software / apps**: App Store / Play Store recent reviews → app site + changelog → r/<platform>apps or category subreddit → MacRumors / Android Police-style review sites.

## Default output shape

- **Identity card** — name, namespace, maker, category, license, pricing model.
- **Capabilities that matter** — the 3-5 differentiating capabilities.
- **Pricing card** — free tier (if any) + paid tiers (if any). **Conditional** — for fully free OSS, this section reads "Free / OSS" and lists license details only.
- **Install / signup** — the actual command or URL.
- **Reviews / community signal** — star count, download stats, ratings, distribution shape; recent commit / release activity for OSS.
- **Integrations + ecosystem** — plugins, official integrations, third-party tooling.
- **Maintenance + risk** — release cadence, bus factor, security posture, EOL signals.
- **Alternatives** — 3-5 competitors with one-line differentiators (including any commercial/OSS fork if applicable).
- **Verdict** (Deep only, only when asked).
- **Sources** — full URLs.

## Adopt-decision factors (when used for recommendations)

Hard constraints first (license compatibility with the user's project, runtime / platform fit, regulatory) → community-and-maintenance signal (active development, response time on issues, stable API) → ecosystem (integration with what the user already uses) → cost (TCO including engineering time, not just license fee) → lock-in (data portability, API stability, exit cost).

For paid software, run the standard buy-decision factors from [[describe-product]] § Buy-decision factors as a second pass.

## Sub-type variants

- **OSS library / framework** — GitHub-first signals; pricing card is empty; integration-and-ecosystem dominates.
- **OSS app (self-hostable)** — like OSS library but adds deployment story (Docker image / install scripts / hosted offering).
- **Open-core (Sentry / Mattermost / GitLab CE/EE shape)** — pricing card describes the gate between free and paid; the OSS side and the commercial side both get covered.
- **Pure SaaS** — like describe-product B2B SaaS; community signal is review-aggregator-driven, not GitHub.
- **Consumer app** — App Store / Play Store recent reviews dominate; pricing model is freemium / paid up-front / subscription.

## Gotchas

- **GitHub stars rot** — a 10k-star repo with last commit 2 years ago is dead; weight recency over absolute count.
- **License compatibility** — "open source" includes GPL (copyleft, viral) and MIT (permissive) — these have very different downstream implications.
- **Open-core gating** — confirm which capabilities are OSS vs paid; the OSS surface is often less capable than the docs let on.
- **SaaS "free tier" hooks** — free-tier limits often drive a forced upgrade at scale; surface the trigger thresholds.
- **Bus factor** — single-maintainer projects are risky; surface this for adopt-decisions.
- **Acquisitions** — corporate parent changes can change license overnight (HashiCorp BSL, Redis SSPL). Surface recent acquisition activity.
- **Naming churn** — software renames more often than physical products (npm scope changes, GitHub org transfers); anchor to the canonical URL.

## User rules

(Empty — user adds in `SRC rules/describe-software.md` to override these defaults.)
