# Cards Format

Cards documents organize knowledge for review and spaced repetition using Obsidian's SR plugin. Three tiers: cheat sheets (overview), summary cards (grouped patterns), detail cards (single facts).

## Examples

## **`AREA NAME`**
```
CONCEPT1:  term — one-line definition
CONCEPT2:  term — one-line definition
RELATED:   term — one-line definition
```

---

## Summary Cards

### Area Name

Key concepts in this area
-?-
TERM1 does X. TERM2 does Y. They relate because Z.
.
**TERM1**: expanded detail about this concept including specifics.
.
**TERM2**: expanded detail about this concept including specifics.
<!--SR:-->

## Detail Cards

### Area Name

Specific technique name
-?-
Short meaningful answer — what you'd say in a conversation. Could be 1-3 sentences that capture the essential point.
.
> [!info]
> Expanded detail for wide/structured content that would word-wrap.
> Use callout blocks to keep structured content together and prevent wrapping.

<!--SR:-->

## Structure

- **Cheat sheets** at the top under H2 headers: `## **`NAME`**` with code blocks
- Separate cheat sheets with `---`
- **Summary cards** under `## Summary Cards` with `### Area` subheadings
- **Detail cards** under `## Detail Cards` with `### Area` subheadings

## Card Anatomy

```
Question or term
-?-
Short meaningful answer (1-3 sentences, what you'd actually say)
.
Expanded detail if needed
<!--SR:-->
```

### Answer format rules

- **First line after `-?-`**: a real, meaningful answer — not a throwaway pithy phrase. Should be something you could say in a conversation and sound knowledgeable. Avoid content-free summaries like "modeled after biosafety levels" when the card is asking what the levels ARE.
- **Don't use blank lines** inside the answer — blank lines end the card in Obsidian SR. Use a period on a line by itself (`.`) to create visual separation between sections.
- **Use `.` separator** to break a long answer into logical chunks (e.g., separating two contrasting concepts, or separating the short answer from expanded detail).
- **Use callout blocks** (`> [!info]`) for structured/wide content that would word-wrap in normal text (tables, multi-line formatted lists, code-like content).
- **Code blocks** (```` ``` ````) work for cheat sheets but tend to word-wrap on narrow displays. Prefer callout blocks for card answers that have structured/aligned content.
- **Don't use code blocks for card answers** unless the content is actual code. Use flowing prose or callout blocks instead.
- **Annotations** use `˹˺` (corner brackets) for inline notes.
- **Wiki-links** to glossary entries where applicable.
- Each card ends with `<!--SR:-->` for spaced repetition tracking.

### What makes a good card

- The short answer alone should be enough to pass a quiz
- Expanded detail is for reinforcement, not the primary answer
- Don't make the reader scroll to find the point — lead with it
- One concept per detail card; summary cards group related concepts
- If you're contrasting two things (A vs B), use `.` to separate them clearly
