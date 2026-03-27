# Research

Investigate the landscape before committing to an approach. Understand what exists, how others have solved similar problems, and what tools or libraries are available.

## When to Use

After the PRD defines WHAT to build, but before UX/System decisions commit HOW to build it. Also invoked anytime during development when a decision needs external input.

## Workflow

### 1. Identify Research Questions

Read the PRD and extract questions that need external input:
- What tools/libraries exist for this?
- How have others solved this problem?
- What are the common architectures for this kind of system?
- Are there standards or protocols we should follow?
- What are the risks or gotchas others have encountered?

### 2. Quick Scan

For each question, do a quick search. Many questions can be answered in a few minutes:
- Web search for overviews, comparisons, blog posts
- Check GitHub for similar projects
- Look at documentation for candidate tools

Capture findings in `{NAME} Research.md` in the Plan folder. Use a simple format:

```markdown
# {NAME} Research

## {Question 1}
{What we found. Links. Key takeaways.}

## {Question 2}
{What we found.}
```

### 3. Formal Surveys (if needed)

If a question is important enough to warrant deep investigation, run `/research survey`. The survey report goes to RRR and gets linked from the Research doc:

```markdown
## Tool Landscape
See [[2026-03-20 Widget Framework Survey]] for the full survey.
Summary: We evaluated 12 frameworks. Recommending X because...
```

### 4. Feed Into Design

Research findings should flow into:
- **PRD** — new constraints, scope adjustments based on what's available
- **System Design** — tool choices, architecture decisions informed by research
- **Discussion** — trade-off reasoning captured for posterity

## What Goes in the Research Doc vs RRR

| Content | Where |
|---------|-------|
| Quick lookups, notes, links | `{NAME} Research.md` (project) |
| Formal survey with results table | RRR folder, linked from Research doc |
| Decision rationale | Discussion doc |

The Research doc is the project's working notes. RRR is the permanent archive for formal surveys that might be useful to other projects.

## Output

`{NAME} Research.md` in the Plan folder with sections for each question investigated. May contain links to RRR survey reports.
