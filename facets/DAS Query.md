---
description: Query facet — the format of an anchor's `{slug} queries.md`, the file `/query` builds to ask the user questions. Rules about what a valid queries file looks like.
---

:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[DAS Track]] → [FCT Query](hook://p/DAS%20Query)
# FCT Query
The asking surface: one `{slug} queries.md` per anchor, in `{slug} Track/`, that `/query` builds and trims.

**Related:** [[SKL Query]] (the skill that builds it),  [[DAS Status]],  [[FCT Messages]]
**Examples:** [[SKA queries\|real instance (SKA anchor)]]

| Table of Contents |  |
|---|---|
| [[#What it is]] |  |
| [[#Parts]] |  |
| [[#Structure]] |  |
| [[#Verifications — agent runs, user judges]] |  |
| [[#No orphan items]] |  |
| [[#Questions]] |  |
| [[#Resolutions & Ready]] |  |
| [[#Cross-cutting]] |  |
| **[[#BRIEF]]** |  |

**TLDR** — One `{slug} queries.md` per anchor (cardinality: one), in `{slug} Track/`, owned by the `/query` skill. Fixed five-section order (`## Agent Resolutions` → `## Verifications` → `## Immediate Questions` → `## Questions` → `## Ready`); empty sections omitted. Verifications are agent-run / user-judged — never "user runs X". Questions are self-contained or wiki-linked. The file shrinks toward empty as answers are applied. Validated by `/audit doc` via `R-query`.

## What it is

`{slug} queries.md` is the single per-anchor surface where the user answers everything the agents need from them. The **`/query` skill** ([[SKL Query]]) *builds* it (the procedure — walking open questions, the determination routing, running verifications ahead of time, console echo); **this facet** governs what the resulting *file* must look like, so it can be audited (`/audit doc`, the F167 on-write hook). The skill cites these rules rather than restating them.

## Parts

- **Frontmatter + H1** — `description:` then `# {slug} Queries`.
- **Five sections, fixed order** (each omitted when empty): `## Agent Resolutions`, `## Verifications`, `## Immediate Questions`, `## Questions`, `## Ready`.
- The file is **agent-owned and trimmed on answer** — answered items are removed, so it shrinks toward empty.

# RULESET R-query
include::
where:: `file:{ANCHOR}/**/* queries.md`
description:: the `{slug} queries.md` format

What `/audit doc` checks on a queries file. The skill that produces it is [[SKL Query]]; these are the file-invariants it must satisfy. Format of this set: [[DAS Ruleset]].

## Structure

### RULE R-query-01 — Lives at `{slug} Track/{slug} queries.md` (checked)
check:: queries_location

One per anchor, slug-prefixed, in the tracking folder.

**Check pattern:** the file's basename is `{slug} queries.md` and its parent is `{slug} Track` (or a sub-folder rooted there).

### RULE R-query-02 — Opens with frontmatter `description:` then H1 `# {slug} Queries` (checked)
check:: frontmatter_has description

**Check pattern:** YAML frontmatter present with a non-empty `description:`; the first body line is `# {slug} Queries`.

### RULE R-query-03 — Five sections, fixed order, no others (checked)
check:: queries_sections_subsequence

Sections, when present, appear in this order and no foreign H2s interleave: `## Agent Resolutions` → `## Verifications` → `## Immediate Questions` → `## Questions` → `## Ready`. Empty sections are omitted.

**Check pattern:** the H2 sequence is a subsequence of `[Agent Resolutions, Verifications, Immediate Questions, Questions, Ready]`; no H2 outside that set.

## Verifications — agent runs, user judges

### RULE R-query-04 — Verifications begin with a bold `**V<n>` handle and carry an answer shape (checked)
check:: queries_verification_handle_and_shape

Each `## Verifications` bullet **begins** with a bold `**V<n>` handle (so it's answerable by reference — `V1: yes`) and asks the user to **judge** something the agent produced (an embedded image / output / rendered artifact), carrying an answer shape — a bold `**yes/no**`. Enforced mechanically by audit-q **C38** (handle) + **C40** (answer shape).

**Check pattern:** each Verifications bullet starts with `- **V<n>` and contains a bold yes/no prompt; ideally an embed (`![[…]]`) or quoted output is present.

```python
import re
V_HANDLE = re.compile(r"^\s*-\s+\*\*V\d+\b")
YESNO    = re.compile(r"\*\*[^*]*yes\s*/\s*no[^*]*\*\*", re.IGNORECASE)
OPTION   = re.compile(r"\*\*\([A-Za-z]\)\*\*")

def check_verification(bullet_opener: str, full_bullet: str) -> list[str]:
    """bullet_opener = the `- …` line; full_bullet = opener + indented
    continuations joined. Returns a list of violation codes."""
    out = []
    if not V_HANDLE.match(bullet_opener):
        out.append("C38: must begin with a bold **V<n> handle")
    if not (YESNO.search(full_bullet) or OPTION.search(full_bullet)):
        out.append("C40: needs a bold **yes/no** (or labeled options)")
    return out
```

### RULE R-query-05 — A verification never asks the user to run/execute anything (checked)
check:: regex_absent (?im)^[-*]\s+\*\*V\d+.*\b(run|execute|launch|invoke)\b

The user is never told to *do* a thing — the agent runs it (ahead of time + embed, or live-on-ready) and the user only looks. Imperatives directed at the user are forbidden.

**Check pattern:** no Verifications line contains a user-directed run/execute imperative. (The live-fallback form "tell me when you're ready; I'll run it" is the agent offering to run — allowed.)

### RULE R-query-06 — No "verify `F<n>`" / whole-document eyeball (stated)

Forbidden verification forms: "verify F113" with no concrete artifact; "does this doc look right?" pointed at a whole multi-page document. A verification names the *specific* thing being judged.

## No orphan items

### RULE R-query-07 — Every item is answerable; no orphan actionable lines (stated)

Every line under Verifications / Immediate Questions / Questions is either a question the user answers or a check the user judges. An actionable item that is neither — work to be done — does **not** belong here: it is landed immediately or becomes a `[Ready]` feature on the backlog (and may appear under `## Ready`). A line that asks nothing and offers no judgeable artifact is a violation.

## Questions

### RULE R-query-08 — Immediate Questions begin with `**Q<n>` and use the standard expanded question format (checked)
check:: queries_immediate_question_handle

Each `## Immediate Questions` item **begins** with a bold anchor-local `**Q<n>` handle (so the user answers by reference — `Q1: A`) and is otherwise the **same standard expanded format as a feature-doc `## Open Questions` item** ([[DAS ask-format]]): a one-line context lead naming the feature + what it's about, a `^{slug}-Q<n>` block-ID, each option a **bold `**(A)**` sub-bullet on its own line** (never inline — readability over density, user direction 2026-06-16), and a `- **Recommendation:**` line (which may be `None` — the rule forces the agent to *consider* whether it has a recommendation, not to manufacture one).

One format vault-wide: the option-own-line + recommendation-line + block-ID invariants are the **shared** ask-format checks (audit-q **C6/C8/C9/C19/C20**, the same ones feature-doc Qs get); the queries-specific additions are the **`Q<n>` handle** (C39) and that any feature named is a **wiki-link** (R-query-13/C37). The handle is always an anchor-local `Q<n>` — a feature's *native* `F<n> Q<m>` is referenced in the body, but the answer handle is the queries-local `Q<n>`. (Verifications, by contrast, are compact `**V<n>` yes/no — they have no options to expand; see R-query-04.)

**Check pattern (queries-specific, C39):** the *opener* line of each Immediate Questions item starts with `- **Q<n>`. The expanded-format checks are inherited from ask-format and run on the same Q-entries.

```python
import re
Q_HANDLE = re.compile(r"^\s*-\s+\*\*Q\d+\b")

def check_immediate_question_handle(opener_line: str) -> list[str]:
    """opener_line = the top-level `- …` line that opens the item (option
    sub-bullets and the `- **Recommendation:**` line belong to it, not new
    items). Only the opener is checked for the handle."""
    if not Q_HANDLE.match(opener_line):
        return ["C39: Immediate Questions item must begin with a bold **Q<n> handle"]
    return []
```

### RULE R-query-09 — Catch-all Questions link in `F<n> Q<m>` form (checked)
check:: queries_catchall_links

`## Questions` items are wiki-links to the feature-doc question (`F<n> Q<m>`) or the feature, clickable to the concrete background — not free-text restatements.

**Check pattern:** each Questions bullet contains a `[[…]]` wiki-link; the visible token is a work-item handle — `F<n>` / `T<n>` / `M-…` / `R-…` (optionally `… Q<m>`).

### RULE R-query-10 — A feature with more than 3 open questions is linked, not enumerated (stated)

When a feature has more than three open questions, `## Questions` carries a single link to the feature (answer in the doc), never the enumerated list.

## Resolutions & Ready

### RULE R-query-11 — Agent Resolutions are reversible-guess records, each linked (stated)

`## Agent Resolutions` items record a decision the agent made on its own — only for choices that are reversible AND soon-visible AND the agent has a sound basis for. Each names the decision + brief why, linked to the question's home, so the user can catch a wrong guess.

### RULE R-query-12 — Ready lists backlog `[Ready]` features and carries no questions (stated)

`## Ready` (optional) lists features that are `[Ready]` on the backlog, for visibility only. It contains no questions or verifications; the backlog is the source of truth.

## Cross-cutting

### RULE R-query-13 — A bullet that names an F-number links it (checked)
check:: queries_fnumber_is_link

Any `F<n>` token appearing in *any* queries bullet must be inside a `[[…]]` wiki-link — to its feature doc `[[F<n> — Title|F<n>]]` when one exists, else to the backlog row `[[{slug} Backlog#^F<n>|F<n>]]` (many items are bare backlog rows with no feature doc — e.g. an undesigned `[Ready]` sweep). A bare `F135` is forbidden: the user must always be one click from the item's home. Enforced by audit-q **C37**.

**Check pattern:** blank every `[[…]]` span, then search the remainder of the bullet for `\bF\d+\b`; any match is a bare (unlinked) F-number.

```python
import re
WIKILINK = re.compile(r"\[\[[^\]]*\]\]")
FNUM     = re.compile(r"\bF\d{1,4}\b")

def bare_fnumbers(full_bullet: str) -> list[str]:
    """F-numbers in the bullet that are NOT inside a wiki-link → violations."""
    return sorted(set(FNUM.findall(WIKILINK.sub("", full_bullet))))
```

### RULE R-query-15 — Every artifact a surfaced item names is a live wiki-link (checked)
check:: queries_named_artifact_is_link

**🚨 HARD REQUIREMENT.** The generalization of `R-query-13` (F-numbers) to **every** artifact. Any doc / file / template / report / folder / section that an answerable item (`## Verifications`, `## Immediate Questions`, `## Questions`) tells the user to *open / look at / skim / check* **MUST appear as a live `[[wiki-link]]`** (or clickable URL) inside that item. It is **illegal to name a thing the user should look at and not link it** — the user cannot click a bare name. Forbidden forms: a bare resolvable doc name (`FCT PRD`), a bare path (`traits/Drive`), a code-span filename (`` `_Disk {{LABEL}} Template.md` ``), or "see the X". Enforced by audit-q **C42**. Fix at the **source** (the backlog `- **Verify:**` line / the question body), then re-render — never edit the rendered `queries.md`.

**Check pattern:** in each Verifications / Immediate Questions / Questions item, blank `[[…]]` wiki-links + `[text](url)` md-links + backtick spans, then flag **(a)** any remaining slug-prefixed multi-word phrase (`FCT PRD`, `SKA Backlog`) that resolves to a vault basename, and **(b)** any code-span filename ending in a doc extension that C36 skips (templated / multi-word, e.g. `` `_Disk {{LABEL}} Template.md` ``).

```python
import re
WIKILINK  = re.compile(r"\[\[[^\]]*\]\]")
MDLINK    = re.compile(r"\[[^\]]*\]\([^)]*\)")
BACKTICK  = re.compile(r"`([^`\n]+)`")
SLUGDOC   = re.compile(r"\b[A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]+)+\b")
ARTIFACT  = re.compile(r"\.(md|py|svg|png|d2|sh|yaml|yml|json|txt|rs|ts|js)$", re.I)

def bare_artifacts(item: str, vault_index: dict) -> list[str]:
    """Named artifacts in an answerable item that are NOT wiki-links."""
    out = []
    for span in BACKTICK.findall(item):                 # (b) code-span filenames
        s = span.strip()
        if ARTIFACT.search(s) and ("{" in s or "}" in s or " " in s):
            out.append(f"`{s}`")
    plain = BACKTICK.sub("", MDLINK.sub("", WIKILINK.sub("", item)))
    for phrase in SLUGDOC.findall(plain):               # (a) bare resolvable doc name
        if phrase in vault_index:
            out.append(phrase)
    return list(dict.fromkeys(out))
```

### RULE R-query-14 — Never surface a commit/push question; steer the agent to its Git-aspect policy (when:: skill:post:audit-q)
when:: skill:post:audit-q

An agent must **never** ask the user "should I commit / push this branch?" — the anchor's Git aspect already answers it (**Commit** mode: commit at logical boundaries without asking; **PR** mode: commit freely on the branch + open/update the PR; **NoGit**: nothing to commit). This is an **executable when-rule** (F180): when the `audit-q` skill runs, `trigger(ctx)` scans the freshly-built `{slug} queries.md` for such a question and, instead of letting it reach the user, returns an **agent-directed steer** — telling the agent to follow its mode and decide for itself (and since it's *asking*, commit now). It never asks the user; it corrects the agent.

**Trigger:** if `ctx.queries_text` contains a "should I … commit/push?"-shaped question, return a mode-appropriate steer using `ctx.git_aspect` (`PR` / `Commit` / `NoGit`).

```python
import re
PUSHCOMMIT = re.compile(r"(?i)\b(push|commit)\b")
IMMEDIATE_Q = re.compile(r"^\s*-\s*\*\*Q\d+\b")

def trigger(ctx):
    # An Immediate Question (a user DECISION) that is about push/commit is the
    # bug — that decision belongs to the anchor's Git aspect, not the user.
    text = ctx.queries_text or ""
    hits = [ln for ln in text.splitlines()
            if IMMEDIATE_Q.match(ln) and PUSHCOMMIT.search(ln) and "?" in ln]
    if not hits:
        return []
    aspect = (ctx.git_aspect or "").lower()
    if aspect == "commit":
        steer = "commit at logical boundaries WITHOUT asking, and NEVER push — since you're asking, commit now (no push)."
    elif aspect == "push":
        steer = "commit at logical boundaries AND push, WITHOUT asking — since you're asking, commit and push now."
    elif aspect == "pr":
        steer = "commit freely on the branch and open/update the PR per policy — never ask."
    elif aspect == "nogit":
        steer = "this anchor is NoGit — there is nothing to commit/push; just drop the question."
    else:
        steer = "resolve it from the anchor's Git aspect yourself; never ask the user whether to commit/push."
    mode = ctx.git_aspect or "unknown"
    return [f"Do NOT ask the user about commit/push ({ctx.anchor}, {mode} mode): "
            f"{steer} Remove the question from queries.md."]
```

# BRIEF

*(Maintainer note — facet-specific cautions for whoever edits this spec. The normative spec is the body + `R-query` ruleset above; the procedure that builds the file lives in [[SKL Query]].)*

- **`R-query` is in the `R-doc` umbrella** — so `/audit doc {slug} queries.md` and the F167 on-write hook validate it. If the spec changes, fix it here; [[SKL Query]] cites these rules and follows.
