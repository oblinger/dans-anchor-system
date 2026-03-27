# Person — Individual Dossier

Research a specific person given their name and identifying details (employer, email, role, etc.). Produce a dossier in the AT folder system using the standard person-file format.

## Workflow

1. **Identify the person** — confirm name, employer, role, and any other identifying details provided by the user
2. **Determine the file location** — the user may provide a file path directly. Otherwise:
   - If a company folder exists at `AT/Corp/@{Company}/`, create the file there: `AT/Corp/@{Company}/@{Name}.md`
   - Otherwise, create the file at the AT top level: `AT/@{Name}.md`
3. **Search broadly** — use web search to find their LinkedIn, GitHub, Twitter/X, personal website, project pages, publications, talks, and any other public presence
4. **Cross-reference** — verify identity across sources using employer, location, and role to avoid confusing people with the same name
5. **Write the person file** — using the format below
6. **Update the company page** — if a company page exists (e.g., `AT/Corp/@{Company}.md` or `AT/Corp/@{Company}/@{Company}.md`), add the person's name as a wiki-link on that page (e.g., `[[@{Name}]]`) in the team/employee listing
7. **Glance the result** — run `open "{file_path}"` so the user can see the completed dossier in Obsidian
8. **No RSH Log entry** — person dossiers live in AT, not RSH Log

## Person File Format

The file follows the AT person-file convention. The first line is the header:

```
#pp   [{Job Title}]({LinkedIn URL}) [[@{Company}]]
```

**Examples from the codebase:**
```
  [[FAANG]]    [Senior Software Engineer](https://www.linkedin.com/in/abhishekkapatkar/)  [[@Netflix 1]]
=[[AT]]     [Managing General Partner](https://www.linkedin.com/in/andrewyng/)  [[@AI Fund]]
 [[VC ORG]]  [Co-Founder](https://www.linkedin.com/in/aliaalaoui/) [[@Njord Venture Group]]
```

- **Job title is the linked text** — the clickable text is the person's role/title (e.g., "Senior Software Engineer"), NOT the company name. The link URL points to their LinkedIn profile.
- **Company wiki-link** — `[[@Company Name]]` follows the title link. Always include this even if the company page doesn't exist yet — the wiki-link will resolve once the page is created.
- If no LinkedIn is found, use the job title as plain text (no link)

After the header:

```
- {email if known}

## Web Presence

- **LinkedIn** — {full URL}
- **GitHub** — {full URL}
- **Twitter/X** — {full URL}
- **Personal site** — {full URL}
- **Other** — {any other relevant pages: project pages, Google Scholar, publications, talks}

(Omit any category where nothing was found.)

## Background

{2-3 sentences: education, career arc, notable work}

## Notes

{Bullet points of anything notable: how they connect to the user, context from the request, open questions}


# LOG

```

## Handling Ambiguity

- There are many people with common names. Use all identifying details (employer, email domain, location, field) to pin down the right person.
- If the person cannot be confidently identified, state what was found and what remains unconfirmed. Do not guess.
- If multiple candidates exist, list them and ask the user to confirm before writing the file.

## Entity-Specific Investigation Tips

- **LinkedIn** — primary source for job title, employer, career history. Note: LinkedIn blocks direct WebFetch requests (returns 999). Use `ctrl surf "{linkedin_url}"` to open the profile in Chrome for the user to view, or use `ctrl cexec` to extract page content via Chrome CDP.
- **GitHub** — look for repos, contributions, org memberships
- **Twitter/X** — look for bio, pinned tweets, employer mentions
- **Google Scholar** — for researchers, find publications and citation count
- **Personal sites** — often linked from LinkedIn or Twitter bios
- **Conference talks** — search YouTube, conference proceedings
- **Email domain** — strong signal for employer when LinkedIn is ambiguous
