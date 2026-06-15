---
description: "Q.md constraint validator with mechanical-fix mode; the three-tier fix flow."
---
just 
# [[SKA]] · F076 — `audit q` — Q.md constraint validator with mechanical-fix mode

## Summary

A focused Python script — `skills/audit/scripts/audit-q.py` — validates `~/ob/kmr/Q.md` against a minimum-viable constraint set with observed failure history. Invoked via `/audit q` (and `/audit q --fix` for mechanical repair). Internally contains a **`LinksManager` class** that re-reads a file on each call and returns a list of structured `LinkEntry` records describing every wiki-link with resolved filesystem pointers (target file path, target heading, target block ID). The class is reusable by other future audits that need fresh-read wiki-link inspection. Auto-wired into the F075 participating skills as a post-condition so Q.md validation runs after every state-touching skill action — agent-discipline violations become surfaced failures, not silent staleness.

## Design

### 1. Subaction shape — script-vs-skill split (per Q4 resolution)

`audit q` ships as **two layers**:

**Layer 1 — Python script** `skills/audit/scripts/audit-q.py`. Clean primitive:

```bash
python audit-q.py             # report-only — list failures, exit 1 if any
python audit-q.py --fix       # apply mechanical repairs (Q.md + backlog rows), then list remaining
python audit-q.py --dry       # report-only AND refuse to write anywhere
```

The script defaults to read-only. `--fix` is the explicit opt-in for write side-effects. Reusable and testable in isolation; can be imported by other tools (the `links_in_file` and `backlog_entries` functions in §§ 2, 2.5 are exposed for reuse).

**Layer 2 — `/audit q` skill** `skills/audit/audit-q.md`. Opinionated wrapper. Invokes the script **with `--fix`** by default — when a user (or another skill) types `/audit q`, the intent is "make Q.md correct," so the skill does the fix work without requiring the user to remember `--fix`. The chat output is what the script prints (findings + applied fixes); no additional output beyond the skill's invocation acknowledgment.

```bash
/audit q              # invokes `python audit-q.py --fix` — fixes by default
/audit q --dry        # invokes `python audit-q.py --dry` — report-only override
```

**Files:**
- `skills/audit/audit-q.md` — agent runbook (thin: invokes the script with --fix; documents the dry override).
- `skills/audit/scripts/audit-q.py` — the validator script. Contains `links_in_file()`, `backlog_entries()`, and the constraint logic.

### 2. `LinksManager` — wiki-link + markdown-link inspection (per Q3 resolution)

Per the user's refined directive: a Python function (or class with stateless `.links_in(path)`) that re-reads a file each call (no caching of contents), returns a **list of dict-shaped LinkEntry records**. Handles **both wiki-links AND markdown links**. Each entry includes **source position** (start/end), **target file path**, and **target position within the target file** (resolved heading line, resolved block-id line, or `0` for whole-file references). Lives as a section within `audit-q.py` so future audits and other validators can import it.

```python
@dataclass
class LinkEntry:
    # Source position
    source_file: Path           # the file containing the link
    source_line: int            # 1-indexed line number where the link starts
    source_col_start: int       # 1-indexed column where the link's opening character starts
    source_col_end: int         # 1-indexed column where the link's closing character ends
    raw: str                    # the verbatim link string (`[[X#Y]]` or `[X](path#Y)`)

    # Link form
    kind: str                   # 'wiki' or 'markdown'
    target_basename: str        # filename part (before '|' or '#' for wiki; before '#' in path for markdown)
    target_heading: str | None  # if '#Heading' suffix
    target_block_id: str | None # if '#^block-id' suffix (wiki-link form only — markdown doesn't have block refs)
    display_text: str | None    # alias text if present

    # Target resolution
    target_file_path: Path | None  # resolved via Obsidian path-proximity (wiki) or relative-path (markdown)
    target_line: int                # 1-indexed line in target file where the link lands; 0 = whole-file (no anchor)
    target_resolves: bool           # True if target_file_path is not None
    target_anchor_resolves: bool | None  # True/False for #Heading or #^block-id; None when no anchor

def links_in_file(file_path: Path, vault_index: dict[str, list[Path]]) -> list[LinkEntry]:
    """Re-read file_path fresh; parse every wiki-link AND markdown-link; resolve targets;
    return a list of LinkEntry records ordered by appearance in the source file."""
```

**Key properties:**
- **Two link forms supported:** wiki (`[[X]]`, `[[X#H]]`, `[[X#^id]]`, `[[X|alias]]`) AND markdown (`[text](path)`, `[text](path#heading)`). Same `LinkEntry` shape for both, distinguished by `kind`.
- **No caching of file contents.** Every call re-reads the file. (The vault-index `basename → paths` IS cached at the caller level — that's filesystem shape, not file content.)
- **Position pointers in BOTH directions.** Caller knows where the link lives in its source file (line + col range, for in-place rewrites) AND where it lands in the target file (line number, for verification or "open at line").
- **Reusable.** Future audits (`/architect` checking `Arch` rows, module-doc audits, anchor-page dispatch validation) all import `links_in_file`.

### 2.5. `BacklogReader` — derived backlog-entry list (per Q3 resolution)

Companion primitive: given a `{NAME} Backlog.md`, return a structured list of backlog entries. Used to **derive** the per-anchor Q.md banner (instead of validating it against an agent-written banner). Also reusable by `/roster`, future audits, and any skill that needs structured backlog data.

```python
@dataclass
class BacklogEntry:
    source_file: Path           # the {NAME} Backlog.md path
    source_line: int            # 1-indexed line where the entry begins
    identifier: str             # 'F063', 'B-md-durability', etc. — first bold-token in the bullet
    horizon: str                # 'Active' | 'Ready' | 'Now' | 'Next' | 'Later' | 'Done' | 'Icebox' | 'Legwork'
                                #   from the enclosing H2 (or 'Icebox' when sourced from {NAME} Icebox.md)
    status: str                 # bracket text: 'Ready', 'Questions', 'Designing', 'Blocked', 'Waiting',
                                #   'Watching', 'Verify', 'Active', 'Done', '' (empty bracket / unset)
    link: LinkEntry | None      # first link in the row body if present (typically the row's primary target)
    raw_body: str               # the first line of the entry verbatim (for description rendering)

def backlog_entries(backlog_file: Path, vault_index: dict[str, list[Path]]) -> list[BacklogEntry]:
    """Re-read backlog_file fresh; walk every list item under recognized H2s;
    return BacklogEntry records in source order."""
```

**Banner derivation:** the per-anchor Q.md banner is computed by:
- Walk the BacklogEntry list (plus `{NAME} Questions.md` for à la carte Qs, plus `{NAME} Icebox.md` for icebox count).
- Count by status bracket for Q/V/A/R; count by horizon for Now/Next/Later/Icebox.
- For `Questions`: sum the **count of `Q<n>` markers at each entry's link target** (using `links_in_file` on each target). Only used for the banner; not validated for exact match elsewhere.
- Compute the anchor TAG cascade.
- Emit the banner string.

This **replaces** the previous "validate banner ↔ body" check (per Q3 resolution). The banner is derived from authoritative sources every time `audit q` runs.

### 3. Constraint checks (per Q3 resolution)

The validator runs **two constraints** + **one derivation**. Each consumes the LinksManager + BacklogReader primitives from §§ 2 and 2.5.

#### C1. Link existence — every triage entry's link resolves

Walk every BacklogEntry across every anchor's backlog. For each entry's `link` field (the row's primary wiki/markdown link): verify `target_resolves` is True AND `target_anchor_resolves` is True (when an anchor is present). Failures:

- `Q.md:48 — entry F067 links to [[F067 — Drive mode: skip ...]] which does not resolve in vault`
- `Q.md:50 — entry F063 links to [[SKA Backlog#^F063]] which resolves to file but block-id `^F063` missing in target`
- `SKA Backlog.md:38 — entry F067 has no link in row body (every triage entry must link to something — the user-stated rule)`

This subsumes the "every triage entry must link to something that exists" rule the user named.

#### C2. Question presence — `[Questions]` brackets point at Q-marker-bearing targets

For each BacklogEntry with status `Questions` (or `N Questions`): follow the link, scan the target for **at least one** `^Q\d+\s+—` marker (in a feature doc's `## Open Questions` H2; in a backlog row's body sub-bullets; in a `{NAME} Questions.md` H2). **Existence only — not exact count.** Per user guidance: *"I'm not as worried that the number of questions is accurate."* Failures:

- `SKA Backlog.md:31 — B-md-durability has [Questions] but the row body contains no Q<n> markers`
- `Q.md:14 — F004 bracket says [Questions], target file has no Q<n> markers in any heading`

The user's reasoning for existence-only: mid-resolution states naturally have intermediate counts; locking the exact-count match produces false positives during ordinary Q-resolution flow. Existence catches the genuine "broken promise" failure mode (bracket asserts Qs, target has none) without churning on transitional states.

#### C4. Stale `[Done]` rows in horizon H2s — auto-move to `## Done`

If BacklogReader sees a row with bracket `[Done]` (or `[Done YYYY-MM-DD]`) under any horizon H2 (`## Active`, `## Ready`, `## Now`, `## Next`, `## Later`, `## Legwork`), the row is **stale** — finished work belongs in `## Done`. Mechanical fix: move the row to the top of `## Done` (preserving body verbatim), removing it from its previous horizon. Reported in the run summary; no QFix escalation since the move is unambiguous.

#### D1. Banner — DERIVED, not validated

The per-anchor section's H1 banner counts and TAG are **computed every run** from BacklogReader output (`{NAME} Backlog.md`) plus `{NAME} Questions.md` (à la carte Q count) plus `{NAME} Icebox.md` (icebox count). The derived banner overwrites the existing banner — there's no "compare and complain" step, because there's nothing to drift from when the banner is rewritten on every audit pass.

This replaces the previous validate-banner-against-body check entirely. Banner is a function of the backlog; the validator computes that function.

### 4. `--fix` scope — Q.md AND backlog-row repairs (per Q4 resolution)

`--fix` extends the bare (read-only) script run with mechanical repairs in **two surfaces**: Q.md AND the touched anchors' `{NAME} Backlog.md` files. Per Q4: *"when you do the fix, it's gonna fix the backlog row as well."*

| Failure | Mechanical fix? | Write surface | What `--fix` does |
|---|---|---|---|
| Per-anchor Q.md banner counts / TAG drift | **Yes** | Q.md | Derive from BacklogReader output; rewrite the H1 line on every run per D1. (Strictly, D1 runs even in bare mode — the banner is computed; `--fix` is what makes the rewrite land.) |
| Stale `[Done]` row in a horizon H2 (per C4) | **Yes** | `{NAME} Backlog.md` | Move the row to the top of `## Done`, preserving body. Removes from its previous horizon (`## Now` / `## Next` / `## Later` / `## Active` / `## Ready` / `## Legwork`). |
| Backlog row `[Ready]` with disqualifying hedging in body | **Yes** | `{NAME} Backlog.md` | Rebracket to `[Questions]` per the `[[SKA triage]]` rebracketing discipline; preserve row content otherwise. |
| Backlog row `[N Questions]` count mismatch with target's Q-marker count | **Yes** | `{NAME} Backlog.md` | Recount Q-markers at the link target; rewrite the bracket to match. |
| Backlog row carries `[Questions]` but link target has zero Q-markers | **No** | — | Either bracket or target is wrong; needs adjudication. Reported to stdout. |
| Stale wiki-link form (e.g., `[[NAME Triage]]` post-F075 retirement) | **No** | — | Needs human judgment about the replacement form. Reported to stdout. |
| Missing block-id at target (`[[SKA Backlog#^F063]]` but no `^F063` marker exists in target) | **No** | — | Adding `^block-id` to the target requires understanding the row layout; out of scope for mechanical fix. Reported to stdout. |

**Output after a `--fix` run** (printed to chat by the skill, stdout by the script):

```
audit q --fix
  applied:
    3 anchor banners derived + rewritten (SKA, A2X, HA)
    1 backlog rebracket: SKA Backlog F063 [Ready] → [Questions] (hedging in body)
  remaining (agent action required):
    Q.md:48 — entry links to [[NAME Triage]] which does not resolve in vault. Likely stale from before F075 — change to [[Q#NAME Triage|NAME Triage]] or remove.
    SKA Backlog.md:31 — B-md-durability has [Questions] bracket but the row body contains no Q<n> markers. Either hoist informal Qs to Q1/Q2/Q3 form, or rebracket to a state the row actually satisfies.
```

### 4.5. Non-mechanical findings — three-tier fix flow (per Q5 resolution)

After the Python script applies all its mechanical fixes, the **agent running `/audit q` reads any remaining findings and tries to fix them inline** using its own judgment. Only the **truly intractable** cases — rare in practice — get written to the `QFix` backlog entry for later attention.

#### The three tiers

| Tier | Who fixes | What kinds of findings | When |
|---|---|---|---|
| **(1) Mechanical** | `audit-q.py --fix` | Banner derivation (D1); backlog-row rebracketing where the body unambiguously signals the correct bracket; bracket-count rewrites that match a clean target | Always, during every `/audit q` invocation |
| **(2) Agent-judgment, INLINE** | The agent running `/audit q` | Stale wiki-link with a near-match candidate; bracket↔target Q-marker mismatch where the right fix is reasonably clear from context; missing block-id at target where the target row is identifiable; etc. | Same skill invocation. Agent reads the script's "remaining findings" output and fixes each one it can safely handle. |
| **(3) QFix backlog entry** | Later — user, or a `/audit q-fix` invocation | Cases where the agent genuinely can't tell what the right fix is (ambiguous link-rename intent; bracket-target mismatch where the row body has no clear signal; etc.) | Rare. The agent escalates only when it's confident inline-judgment would be unsafe. |

Per user direction: *"It should not just do the automatic stuff that Python can do. The agent that did the auditing should actually look at those and decide if it can just do them safely itself, in which case it should just do it. Then it doesn't have to add anything to the backlog... I think most of the cases, the agent running the audit can actually just fix all of the entries for all of the projects."*

#### `/audit q` runbook — sketch

1. **Invoke the Python script with `--fix`.** Script applies mechanical fixes (Tier 1), prints the list of remaining findings.
2. **For each remaining finding, the agent decides:**
   - **Safe to fix inline?** Apply the fix (edit the file in question). Don't escalate. Don't add to QFix.
   - **Genuinely unclear/unsafe?** Hold the finding for the QFix entry.
3. **If any findings were held**: write/regenerate the singleton `QFix` backlog entry with those findings as sub-bullets.
4. **If zero findings were held**: ensure no stale `QFix` entry exists from a prior run; remove if present.
5. **(Optional) Re-run the script** to confirm the audit comes out clean post-inline-fix. The agent's own fixes may have introduced new audit-relevant state — a second pass catches any.

When the QFix backlog entry IS written, `/audit q-fix` (next section) is the way to pick it up later.

#### The QFix backlog entry — shape and invariants

Stable identifier: **`QFix`** (not F-numbered — regenerated each audit pass; F-numbers would burn fast). Singleton — at most one per anchor at a time.

Position: **top of `## Ready`** in `{NAME} Backlog.md`. Bracket: `[Ready]`. The entry is ready-to-mint work — pulling it off the top is the user's path to "make the audit pass clean."

```markdown
## Ready
- **QFix — auditing errors to fix** [Ready] — work surfaced by `/audit q`. Errors below were found but couldn't be fixed mechanically. Run `/audit q-fix` to work through them; the skill loops back to `/audit q` after each pass until errors resolve. ^QFix
  - Q.md:48 — entry links to [[NAME Triage]] which does not resolve in vault. Likely stale from before F075. Suggested fix: `[[Q#NAME Triage|NAME Triage]]` or remove.
  - SKA Backlog.md:31 — B-md-durability has [Questions] bracket but row body contains no Q<n> markers. Either hoist informal Qs to Q1/Q2/Q3 form, or rebracket.
  - SKA Backlog.md:38 — F067 row has no link in body; every triage entry must link to something.
```

**Generation rules:**
- `/audit q` (the skill, fix-by-default) writes this entry **only when there are non-mechanical findings**. Zero non-mechanical findings → no QFix entry (and any pre-existing QFix entry from a previous run is removed).
- If a QFix entry already exists, regen rewrites its body in place; doesn't create a second.
- Findings list = errors only (what was found). Suggested fixes can be appended where unambiguous; the right fix often needs context the audit doesn't have.

#### The `/audit q-fix` skill — self-healing loop

New skill: `skills/audit/audit-q-fix.md`. Runbook:

1. **Read the QFix entry** from the cwd anchor's `{NAME} Backlog.md`. If absent → exit ("no QFix entry; nothing to do").
2. **For each sub-bullet (finding)**, apply a fix using agent judgment for the specific finding type:
   - Stale wiki-link → if a near-match candidate exists in the vault, rewrite the link.
   - Bracket↔target mismatch → read the row's body; either hoist informal Qs to numbered form, or rebracket the row to a state it actually satisfies.
   - Missing block-id → add `^block-id` to the target file at the appropriate row.
   - Findings genuinely needing user input (e.g., "is this row's intent X or Y?") → escalate to `/ask` (don't fix; tag the finding).
3. **Re-run `/audit q`** to regenerate the QFix entry from the fresh state.
4. **Check the result:**
   - QFix entry gone → done; loop exits cleanly.
   - QFix entry exists with **different** findings → loop back to step 1 (progress was made).
   - QFix entry exists with **same** findings as the previous iteration → exit with "stalled; user input needed" report listing what couldn't be auto-fixed.
5. **Termination cap: ≤3 iterations.** Even if the findings change each iteration, exit after 3 passes to prevent runaway loops.

#### Why a separate skill and not inline in `/audit q`

`/audit q` is the validator + mechanical fixer. `/audit q-fix` is the agent-judgment fixer. Separation lets the validator stay fast and side-effect-bounded (any agent-judgment is gated behind an explicit `/audit q-fix` invocation), while the fixer skill is allowed to take broader actions on findings. Users who only want to validate (or who don't trust the agent-judgment fixes) never invoke `/audit q-fix`.

### 5. Auto-wiring into participating skills (per Q6=a recommendation)

Add a brief `audit q` invocation to the end of each F075 participating skill's Q.md-update post-condition section. Spec text (template):

> After the Q.md regen completes, invoke `audit q` to verify. If any failures, surface them to the user instead of declaring "done." Mechanical repairs can be applied with `audit q --fix` — but this skill calls bare `audit q` to keep side-effects explicit at the user's invocation site.

Files to update (5):
- `skills/triage/SKILL.md` — § 6 (Regenerate Q.md) → append `audit q` call.
- `skills/groom/SKILL.md` — § 5 (Q.md post-condition).
- `skills/mint/SKILL.md` — § 7 (Q.md post-condition).
- `skills/finalize/SKILL.md` — § 7 (Q.md post-condition).
- `skills/feature/SKILL.md` — § 1c (refresh Q.md).
- `skills/audit/SKILL.md` — orchestrator (when `/audit` runs `audit q` directly).

### 6. Performance budget

Sub-second runtime. The script:
- Walks the vault once to build the basename index (~5-50ms depending on vault size).
- Reads Q.md once (~10ms).
- For each wiki-link in Q.md: opens the target file once to verify heading/block-id (~5ms each).
- Q.md has ~50-100 wiki-links typical → ~250-500ms total.

Bounded by IO. If sub-second budget is exceeded on the user's vault, profile and either parallelize the per-target reads or cache target-file metadata for the duration of the run.

### 7. Cross-references to update

- `skills/audit/SKILL.md` — add `/audit q` to the Actions table (parallel row to `/audit structure`, `/audit rules`, etc.).
- `skills/audit/audit-q.md` (new) — runbook for the subaction; pointer to `scripts/audit-q.py`.
- `skills/audit/scripts/audit-q.py` (new) — the validator + `LinksManager` class.
- F075 participating skills (5 SKILL.md files) — add `audit q` to their Q.md post-condition (per Q6=a, § 5 above).

### 8. Out of scope (v1)

- Validating per-anchor `{NAME} Questions.md` files. Different surface; if Qs there have similar staleness, file a separate F-row.
- Validating module-doc `Arch` rows (per F074). The `LinksManager` class would help, but the constraint checks are different; separate audit subaction.
- Auto-detecting the F075-style "renamed file" case (e.g., `[[F067 — Drive mode: skip ...]]` → suggest `[[F067 — Drive mode — skip ...]]` because the new file exists and the basename is close). Useful eventually, but the heuristics are tricky; defer until renames stop happening (or until we get burned again).
- Multi-run optimization (incremental check; only re-validate changed sections). Premature; sub-second runtime makes this irrelevant.

## Status

Agreed — all 6 Qs resolved 2026-05-20. Ready to mint.

## Resolved

- **Q1 — Lint→audit consolidation scope.** — **Resolution: (a)** — F076 commissions only `/audit q` as a new audit subaction. Lint deprecation is deferred to a separate feature [[F078 — Migrate /lint → /audit]] (filed 2026-05-20, parked in `## Later`). Resolved 2026-05-20. No Design change required.
- **Q2 — Subaction naming.** — **Resolution: (a) `/audit q`** — short, read-aloud-able, matches the canonical vocabulary the user already uses ("audit Q", "Q file"). No ambiguity with future `/audit X` subactions. Resolved 2026-05-20. No Design change required (already used throughout the design).
- **Q3 — v1 constraint set.** — **Resolution: two derived primitives + three constraints, with banner DERIVED not validated.** The validator builds two reusable Python primitives — `links_in_file(path)` (returns a list of dict-shaped LinkEntry records: source-position, target-file path, target-position) handling both wiki-links AND markdown links; `backlog_entries(path)` (returns a list of BacklogEntry records: source-line, horizon H2, status bracket, link, F/B identifier). Then applies three checks: **(C1) Link existence** — every triage entry must link to something that resolves. **(C2) Question presence** — `[Questions]` brackets target files/blocks that contain at least one `Q<n>` marker (existence-check only — exact count match is intentionally NOT verified; mid-resolution states have intermediate counts and the user is "not as worried that the number of questions is accurate"). **(C3) Banner is derived, not validated** — the per-anchor banner counts are computed from the BacklogReader output and rewritten to match (a `--fix` operation, but since the regen is mechanical and unambiguous, it can run by default within the bare `audit q` invocation when the rewrite is the only change). Resolved 2026-05-20. Incorporated into Design §§ 2 (LinksManager), 2.5 (BacklogReader, new), 3 (Constraint checks), 4 (`--fix` scope).
- **Q4 — Default behavior.** — **Resolution: script-vs-skill split.** The underlying Python script `audit-q.py` is **report-only by default; `--fix` flag triggers repairs** (clean primitive: testable, reusable, no side effects without an explicit flag). The `/audit q` SKILL invokes the script **with `--fix` automatically** (fix-by-default at the skill level). Users typing `/audit q` get the repair behavior because that's what they want from an audit-skill invocation. `--fix` scope expanded to include **backlog-row corrections** in addition to Q.md banner derivation — stale brackets (e.g., `[Ready]` on a row whose body has hedging), bracket counts not matching numbered Qs at target, and similar mechanical drift get rewritten in the backlog file too. The broader question — "should ALL /audit subactions fix by default?" — is **NOT** resolved by F076; it's a separate consideration to revisit per-subaction (some, like `/audit publish`, surface findings that genuinely need user judgment and should stay report-only). Resolved 2026-05-20. Incorporated into Design §§ 1 (subaction shape), 4 (`--fix` scope expanded).
- **Q5 — Non-mechanical findings destination.** — **Resolution: three-tier fix flow** — (1) mechanical (Python script handles); (2) **agent-judgment, INLINE during `/audit q`** (the agent running `/audit q` reads any non-mechanical findings the script reports and fixes them itself using its own expertise); (3) only the **truly intractable** cases — rare — go to a singleton **`QFix` backlog entry** at the top of `## Ready` for later attention. Per user clarification: *"the agent that did the auditing should actually look at those and decide if it can just do them safely itself, in which case it should just do it... I think most of the cases, the agent running the audit can actually just fix all of the entries for all of the projects."* The `/audit q-fix` skill still exists for the rare case (picking up a QFix backlog entry filed by an earlier run that's since had state changes), but is **rarely needed** — `/audit q` handles most cases inline. Sub-detail picks: **name `/audit q-fix`** (audit family, dash convention); **position top of `## Ready`**; **identifier stable `QFix`** (not F-numbered); **termination ≤3 iterations** when the loop is invoked. Resolved 2026-05-20. Incorporated into Design § 4.5 (three-tier fix flow with agent-inline-judgment step).
- **Q6 — Post-condition wiring into participating skills.** — **Resolution: (a) auto-wire.** Every state-touching skill that already calls the F075 Q.md-update post-condition (`/triage`, `/groom`, `/mint`, `/finalize`, `/feature`, `/audit`) ALSO invokes `/audit q` afterward as part of the same post-condition. Per Q4 the skill always passes `--fix`, so the auto-wired call runs the full three-tier fix flow (mechanical → agent-inline-judgment → QFix-backlog-as-last-resort). The validation IS the contract enforcement: if `/audit q` can't clean up everything inline, the QFix entry it writes surfaces the remaining issues. Per user: *"if you just say audit Q, it fixes it. The only time it's not fixed is if it's too difficult for the current agent. It has to put something on the backlog for somebody else. But it tries not to do that."* Resolved 2026-05-20. Incorporated into Design § 5 (auto-wiring).
