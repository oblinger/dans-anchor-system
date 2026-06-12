---
description: Default rules for describing a book — ships with the skill. User overrides in SRC rules/. Migrated from legacy /research book.
---
# profile-book — default rules

Default rules for `profile` on noun-type **book**. Ships with the skill; user overrides in `[[SRC rules/profile-book|SRC rules/]]`.

Subsumes the legacy `/research book` action — produces a book summary + dossier given a title and author.

## Default dimensions

| Dimension | Notes |
|---|---|
| Title (canonical) + subtitle | Exact, as on the cover |
| Author(s) | Primary author first; co-authors after |
| Edition / year | First-edition year + edition under review |
| Publisher | And imprint if relevant |
| Page count | Counts vary by edition; note which |
| Genre / category | Fiction, non-fiction, memoir, technical, etc. |
| Awards | Notable only — omit if none |
| Intended audience | Especially for technical / academic |
| Core thesis | One-sentence central argument |
| Major arguments | 3-5; each a discrete claim |
| Chapter overview | Numbered list, brief one-liner per chapter |
| Key takeaways | 4-6 bullet points |
| Author background | Credentials, other notable works |

## Default sources (authority order)

1. **Publisher's page** — canonical title, subtitle, page count, edition, blurb.
2. **Author's own site** — author framing, related work, errata.
3. **Wikipedia** — for notable books; cross-check facts.
4. **Goodreads** — reader reception, distribution shape of ratings.
5. **Review sites** — NYT / Guardian / domain-specific (e.g., LessWrong for rationality books, Hacker News for tech books).
6. **Amazon listing** — fallback for ISBN / edition disambiguation; reader reviews secondary.

## Default disambiguation

- **Multiple editions** — pin to the specific edition (first, revised, anniversary, paperback). Page count + cover art usually disambiguates.
- **Common titles** — "On Writing" exists in many forms (King, Strunk, Welty…). Pin to author + year.
- **Translations** — note original language + translator; reviews often refer to the original, dossier should specify.
- **Author with similar name** — Stephen King vs Stephen Hawking vs Stephen R. King the academic — confirm by topic + publication date.

## Default output shape (legacy BOOK Summary format)

```markdown
# {Book Title}

**Author:** {Author name(s)}
**Published:** {Year}
**Pages:** {Page count}
**Genre:** {Genre(s)}
**Awards:** {Notable awards — omit section if none}

## Summary

{2-3 paragraphs: what the book is about, central thesis, why it matters. Written for someone who hasn't read it.}

## Core Arguments

{3-5 bold-header paragraphs, each covering a major argument or theme. Format: **Claim.** Explanation.}

## Chapter Overview

{Numbered list of chapters with title + one-line description. For long books, group by part/section.}

## Key Takeaways

{Bulleted list of 4-6 takeaways — the most important ideas a reader should walk away with.}

## About the Author

{1 paragraph: credentials, other notable works.}

## Sources

{Full URLs to all referenced material.}
```

## Default behavior

- **Prefer primary sources** — publisher page, author's own site — over third-party summaries.
- **Include chapter titles** even when descriptions are brief; they help readers decide whether to read specific sections.
- **For academic/technical books**: note intended audience + prerequisite knowledge.
- **For older / classic books**: note historical context + lasting influence.
- **Keep summary accessible** to a general reader even for technical books.
- **Cross-reference facts** across multiple sources (publisher page, Wikipedia, Goodreads, review sites).

## Sub-type variants

- **Technical / textbook** — emphasize prerequisites, chapter dependencies, exercise structure, suitability as reference vs cover-to-cover.
- **Memoir / biography** — emphasize subject, time period covered, primary-source value, author's relationship to subject.
- **Fiction** — chapter overview may include light plot beats per part; avoid major spoilers unless the user asks for a "spoiler-OK" version.
- **Reference / handbook** — emphasize organization, search/lookup ergonomics, completeness of coverage vs depth.

## Default output location (legacy)

The legacy `/research book` action wrote to `~/ob/kmr/Topic/Misc/BOOK/BOOK Summary/{YYYY-MM-DD} {Title} by {Author}.md`. Under the new search-skill architecture, output lands in [[Profile]] (`~/ob/kmr/Topic/Search/Profile/`) per the [[profile/SKILL|/profile]] default — the BOOK Summary location is a legacy convention the user may still prefer for books specifically; if so, the user's `SRC rules/profile-book.md` overrides the output location.

## Gotchas

- Page counts vary by edition.
- Multiple editions / translations of the same book — pin to one.
- Author with common name — disambiguate by topic + publication date.
- For older books, "lasting influence" is more interesting than reception at release.
- Fiction summaries that spoil major plot beats are a courtesy violation — note when summarizing fiction.

## User rules

(Empty — user adds in `SRC rules/profile-book.md` to override these defaults.)
