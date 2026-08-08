# RULESET R-query
include::
import:: skills/audit/scripts/audit-plan.py
where:: `file:{anchor}/**/* queries.md`
description:: the `{slug} queries.md` format

What `/audit doc` checks on a queries file. The skill that produces it is [[DAS Ask]]; these are the file-invariants it must satisfy. Format of this set: [[DAS Ruleset]]. Spec: [[DAS Query]].

| Table of Contents |  |
|---|---|
| **[[#Structure]]** |  |
|    [[#RULE R-query-01 — Lives at `{slug} Track/{slug} queries.md` (checked)]] |  |
|    [[#RULE R-query-02 — Opens with frontmatter `description:` then the status-banner H1 (checked)]] |  |
|    [[#RULE R-query-03 — Six sections, fixed order, no others (checked)]] |  |
|    [[#RULE R-query-16 — Banner H1 has the exact status-banner form + spacing (checked)]] |  |
| **[[#Verifications — agent runs, user judges]]** |  |
|    [[#RULE R-query-04 — Verifications begin with a bold `**V<n>` handle and carry an answer shape (checked)]] |  |
|    [[#RULE R-query-05 — A verification never asks the user to run/execute anything (checked)]] |  |
|    [[#RULE R-query-06 — No "verify `F<n>`" / whole-document eyeball (stated)]] |  |
| **[[#No orphan items]]** |  |
|    [[#RULE R-query-07 — Every item is answerable; no orphan actionable lines (stated)]] |  |
| **[[#Questions]]** |  |
|    [[#RULE R-query-08 — Immediate Questions begin with `**Q<n>` and use the standard expanded question format (checked)]] |  |
|    [[#RULE R-query-09 — Catch-all Questions link in `F<n> Q<m>` form (checked)]] |  |
|    [[#RULE R-query-10 — A feature with more than 3 open questions is linked, not enumerated (stated)]] |  |
| **[[#Resolutions & Ready]]** |  |
|    [[#RULE R-query-11 — Agent Resolutions are reversible-guess records, each linked (stated)]] |  |
|    [[#RULE R-query-12 — Ready lists backlog `[Ready]` features and carries no questions (stated)]] |  |
| **[[#Cross-cutting]]** |  |
|    [[#RULE R-query-13 — A bullet that names an F-number links it (checked)]] |  |
|    [[#RULE R-query-15 — Every artifact a surfaced item names is a live wiki-link (checked)]] |  |
|    [[#RULE R-query-14 — Never surface a commit/push question; steer the agent to its Git-aspect policy (when:: skill:post:audit-q)]] |  |

## Structure

### RULE R-query-01 — Lives at `{slug} Track/{slug} queries.md` (checked)
check:: queries_location

One per anchor, slug-prefixed, in the tracking folder.

**Check pattern:** the file's basename is `{slug} queries.md` and its parent is `{slug} Track` (or a sub-folder rooted there).

### RULE R-query-02 — Opens with frontmatter `description:` then the status-banner H1 (checked)
check:: frontmatter_has description

**Check pattern:** YAML frontmatter present with a non-empty `description:`; the first body line is the status banner `# [<TAG>]  [[{slug}|{slug}]]  -  Runnable N …` (per § The banner), not a plain `# {slug} Queries` title.

### RULE R-query-03 — Seven sections, fixed order, no others (checked)
check:: queries_sections_subsequence

Sections, when present, appear in this order and no foreign H2s interleave: `## Blockers` → `## Ready` → `## Questions` → `## Blocked` → `## Verifications` → `## User` → `## Other`. Empty sections are omitted.

The order is F283's (2026-07-30), and each position is argued:

- `## Blockers` is **computed, never authored** — any row that some *other* row names in its `[Blocked <handle>]`, promoted out of whatever section would otherwise hold it, including `## Verifications`. Empty is the good state, which is why it leads: it reads in one glance. This is the render target for the reverse-blocker edge inversion.
- `## Ready` comes first among the working sections because it is short and orients the rest — it is what the agent can act on with no user involvement.
- `## Questions` is the one pile the user personally unsticks, so it stays its own section rather than merging into the ledger below it. The axis that earns a section break is *can the user act on it*, not *is it stopped*.
- `## Blocked` is the visibility ledger: `[Blocked <handle>]` and `[Waiting]` rows together. Scanned, not worked — but rendered, because a bracket recording "not moving" was previously the one bracket that hid the row entirely.
- `## Verifications` is last, deliberately below the fold: an unverified check is only a problem when something depends on it, and when something does, `## Blockers` has already promoted it to the top.
- `## User` (F259) holds the rows waiting on an action only Dan can take. It sits below `## Verifications` because both are user-facing but a verification is a judgement he can give in a sentence, where a `[User]` row asks him to go *do* something — and above `## Other`, which is not a state at all. This entry was missing until T141 (2026-08-05): `queries-render.py` had emitted the section since F259, so the rule was failing six live anchors for carrying a section the renderer is required to write.
- `## Other` is the F284 catch-all — every frontier row the named sections did not claim, with its bracket shown verbatim. It is what makes the render total: before it existed, an unrecognised bracket meant the row was dropped in silence (47 of 99 frontier rows vault-wide on 2026-07-29, the largest class being rows carrying no bracket at all). It sits last because it holds the work whose state is unclear, which must never displace the work whose state is clear.

`[Verify-by <date>]` rows render in no section at all: the bracket promises nothing happens until the date, and the stale-bracket sweep auto-Dones the row when the date arrives, so showing it only crowds the checks that still want a look.

**Check pattern:** the H2 sequence is a subsequence of `[Blockers, Ready, Questions, Blocked, Verifications, User, Other]`; no H2 outside that set.

**Why:** admitting `Other` is load-bearing, not permissive — a rule that forbade the catch-all would forbid the coverage guarantee itself.

### RULE R-query-16 — Banner H1 has the exact status-banner form + spacing (checked)
check:: queries_banner_form

The H1 is the status banner (§ The banner): `# [<TAG>]  [[{slug}|{slug}]]  -  Ready N    User N   |   Now N    Next N    Later N   |   Parked N    Waiting N    Icebox N`, with the locked spacing (two spaces after `[<TAG>]`; two around `-`; four between counts; `   |   ` between each of the three zones), optionally suffixed `    {N}` (the QFix residual count, shown only when N > 0). Zone 1 carries one further optional field, `    Inbox N` immediately after `User N`, likewise shown only when N > 0 — the count of pending (undrained) entries in the anchor's `{slug} Inbox.md`. The slug is wiki-linked (`[[{slug}|{slug}]]` inside queries.md, `[[{slug} queries|{slug}]]` in the Q.md copy) with a plain-text fallback when no target resolves. The renderer (`queries-render.py`) and the `Q.md` copy both depend on this exact form.

**This rule moves in the same pass as the format string it locks, never after it.** It has lagged once already — F260 renamed the headline pair while this rule kept the pre-F260 wording, so the check failed on 26 of 32 live queries files and fired against output that was correct. A lock that disagrees with the thing it locks is worse than no lock: it teaches every reader to ignore the warning. The three-zone form landed 2026-08-07 with [[TINK305 - Three answer shapes, one lifecycle|F305]], and every anchor was re-rendered in that same pass so no page ever sat in the failing interval.

`Inbox N` landed 2026-08-08 with [[TINK Backlog#^T131|T131]] leg 2, and needed no re-render at all: because the field is emitted only when N > 0 and nothing was pending anywhere in the vault, every live banner was already in the new form the moment the rule changed. An optional field is not two forms kept alive side by side — the renderer omits it in exactly the cases this rule permits it to be absent, so there is still one grammar with one producer.

**Check pattern:** the H1 matches the banner grammar with the prescribed spacing (linked or plain slug both accepted); single-spaced or pipe-missing forms fail.

**Why:** the same line is copied into `Q.md`, where the section-boundary scan keys off the `# [` prefix; relaxing the form silently breaks the dashboard render.

## Verifications — agent runs, user judges

### RULE R-query-04 — Verifications begin with a bold `**V<n>` handle and carry an answer shape (checked)

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
check:: regex_absent (?im)^[-*]\s+\*\*V\d+.*(?<![\w-])(run|execute|launch|invoke)(?![\w-])

The user is never told to *do* a thing — the agent runs it (ahead of time + embed, or live-on-ready) and the user only looks. Imperatives directed at the user are forbidden.

**Check pattern:** no Verifications line contains a user-directed run/execute imperative. (The live-fallback form "tell me when you're ready; I'll run it" is the agent offering to run — allowed.) Hyphen-adjacent compounds (`never-run`, `re-run`) are descriptive, not imperative — excluded via the lookarounds (false positive on MUX V24 "never-run anchor", 2026-07-13, the first self-fire day).

### RULE R-query-06 — No "verify `F<n>`" / whole-document eyeball (stated)

Forbidden verification forms: "verify F113" with no concrete artifact; "does this doc look right?" pointed at a whole multi-page document. A verification names the *specific* thing being judged.

## No orphan items

### RULE R-query-07 — Every item is answerable; no orphan actionable lines (stated)

Every line under Verifications / Immediate Questions / Questions is either a question the user answers or a check the user judges. An actionable item that is neither — work to be done — does **not** belong here: it is landed immediately or becomes a `[Ready]` feature on the backlog (and may appear under `## Ready`). A line that asks nothing and offers no judgeable artifact is a violation.

## Questions

### RULE R-query-08 — Immediate Questions begin with `**Q<n>` and use the standard expanded question format (checked)

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

**🚨 HARD REQUIREMENT.** The generalization of `R-query-13` (F-numbers) to **every** artifact. Any doc / file / template / report / folder / section that an answerable item (`## Verifications`, `## Immediate Questions`, `## Questions`) tells the user to *open / look at / skim / check* **MUST appear as a live `[[wiki-link]]`** (or clickable URL) inside that item. It is **illegal to name a thing the user should look at and not link it** — the user cannot click a bare name. Forbidden forms: a bare resolvable doc name (`DAS PRD`), a bare path (`traits/Drive`), a code-span filename (`` `_Disk {{LABEL}} Template.md` ``), or "see the X". Enforced by audit-q **C42**. Fix at the **source** (the backlog `- **Verify:**` line / the question body), then re-render — never edit the rendered `queries.md`.

**Check pattern:** in each Verifications / Immediate Questions / Questions item, blank `[[…]]` wiki-links + `[text](url)` md-links + backtick spans, then flag **(a)** any remaining slug-prefixed multi-word phrase (`DAS PRD`, `SKA Backlog`) that resolves to a vault basename, and **(b)** any code-span filename ending in a doc extension that C36 skips (templated / multi-word, e.g. `` `_Disk {{LABEL}} Template.md` ``).

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

**Trigger:** if `ctx.queries_text` contains a "should I … commit/push?"-shaped question, return a mode-appropriate steer using `ctx.git_aspect` (`pr` / `commit` / `nogit`).

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
