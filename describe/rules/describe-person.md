---
description: Default rules for describing a person — ships with the skill. User overrides in SRC rules/.
---
# describe-person — default rules

Default rules for `describe` on noun-type **person**. Ships with the skill; the user can override in `[[SRC rules/describe-person|SRC rules/]]` for their own preferences.

## Default dimensions

When describing a person, the standard dimension set:

| Dimension | Notes |
|---|---|
| Canonical name + aliases | Married/maiden, professional pseudonyms, handles |
| Current role + org | Title, company, location |
| Prior roles (history) | Reverse-chronological |
| Expertise areas | What this person is known for / cited for |
| Affiliations | Boards, advisory, communities, alma maters |
| Public presence | Personal site, blog, GitHub, scholar, socials, podcasts, talks |
| Recent activity | Publications, talks, posts, news (last ~12 months) |
| Contact surface | Public-facing only (email patterns, contact forms) |

## Default sources (authority order)

1. The person's own site / blog — primary source for their framing.
2. LinkedIn — work history; trust structure, verify dates against other sources.
3. GitHub / arXiv / Google Scholar / professional registries — domain authority.
4. Wikipedia — only when subject is notable enough.
5. News mentions — recent context, role changes, events.
6. Crunchbase / PitchBook — founders / executives at funded companies.

## Default output shape

- **Header card** — name, current role, current org, location, primary contact surface.
- **Background** — education, prior roles (reverse-chron), affiliations.
- **Work / output** — what they've produced, citations / talks / publications.
- **Public footprint** — site, blog, socials, podcasts, recent mentions.
- **Recent activity** — last ~12 months.
- **Sources** — full URLs.

### Legacy AT file format (when output lands under `~/ob/kmr/AT/`)

The legacy `/research person` action wrote person dossiers to the user's AT (address tree) folder:

- If a company folder exists at `AT/Corp/@{Company}/` → write to `AT/Corp/@{Company}/@{Name}.md`.
- Otherwise → write at AT top level: `AT/@{Name}.md`.

When the user's `SRC rules/describe-person.md` (or `SRC rules/person.md`) selects the AT location instead of the default [[Profile]] output, follow this shape.

**Line 1 — the `#pp` header:**

```
#pp   [{Job Title}]({LinkedIn URL}) [[@{Company}]]
```

- **Job title is the linked text** — the clickable text is the person's role/title (e.g., "Senior Software Engineer"), NOT the company name. Link URL points to LinkedIn.
- **Company wiki-link** — `[[@{Company Name}]]` follows the title link. Always include even when the company page doesn't exist yet — the wiki-link resolves later.
- If no LinkedIn is found, use the job title as plain text (no link).

Existing examples in the codebase:
```
  [[FAANG]]    [Senior Software Engineer](https://www.linkedin.com/in/abhishekkapatkar/)  [[@Netflix 1]]
=[[AT]]     [Managing General Partner](https://www.linkedin.com/in/andrewyng/)  [[@AI Fund]]
 [[VC ORG]]  [Co-Founder](https://www.linkedin.com/in/aliaalaoui/) [[@Njord Venture Group]]
```

**Body shape:**

```
- {email if known}

## Web Presence

- **LinkedIn** — {full URL}
- **GitHub** — {full URL}
- **Twitter/X** — {full URL}
- **Personal site** — {full URL}
- **Other** — {Google Scholar, publications, talks, project pages}

(Omit any category where nothing was found.)

## Background

{2-3 sentences: education, career arc, notable work}

## Notes

{Bullet points: how they connect to the user, context from the request, open questions}


# LOG
```

**Company-page sync** — when a company page exists at `AT/Corp/@{Company}.md` or `AT/Corp/@{Company}/@{Company}.md`, add the person's wiki-link (`[[@{Name}]]`) to its team/employee listing as part of writing the person file.

## Privacy / OSINT (load-bearing)

- **Public figures** — research as you would any public entity; standard sources fine.
- **Private individuals** — conservative; only what the person themselves published or legitimate news. Don't compile addresses, phones, family, or doxxing-shape aggregations.
- **Never** use breach data, scraped private data, social-engineered access, dark web.
- When a request crosses the line, surface the concern before complying.

## Default disambiguation tiebreakers

When multiple candidates: current org + role → location → time period → topical area → user-provided known fact.

## Sub-type variants

Public figure (all sources fair game) · researcher/academic (citation graph, h-index, lab) · founder/operator (current venture, prior exits) · private individual (conservative, self-published only).

## Entity-specific investigation tips

- **LinkedIn** — primary source for job title, employer, career history. Note: LinkedIn blocks direct WebFetch requests (returns 999). Use `ctrl surf "{linkedin_url}"` to open the profile in Chrome for the user to view, or use `ctrl cexec` to extract page content via Chrome CDP.
- **GitHub** — look for repos, contributions, org memberships.
- **Twitter/X** — bio, pinned tweets, employer mentions.
- **Google Scholar** — for researchers; publications + citation count.
- **Personal sites** — often linked from LinkedIn or Twitter bios.
- **Conference talks** — search YouTube, conference proceedings.
- **Email domain** — strong signal for employer when LinkedIn is ambiguous.

## Gotchas

- LinkedIn dates soft (rounded to year, "present" stale). Cross-check.
- LinkedIn returns 999 on direct WebFetch — use `ctrl surf` or `ctrl cexec`.
- Name-collision rate high in tech (~5+ John Smiths per company). Don't trust top result.
- Recent role changes lag on LinkedIn; check Twitter/news for joining announcements.
- Historical figures: prioritize academic sources over Wikipedia.

## User rules

(Empty — user adds in `SRC rules/describe-person.md` to override these defaults.)
