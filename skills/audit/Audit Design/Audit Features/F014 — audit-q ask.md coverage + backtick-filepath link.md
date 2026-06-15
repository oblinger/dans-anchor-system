---
description: "ask.md joins Q.md as an audit surface; C36 rewrites backtick-filepaths to links."
---

# [[Audit]] · F014 — audit-q ask.md coverage + backtick-filepath link

## Summary

The audit-q discipline currently covers `Q.md` (backlog cross-refs, banner integrity, drift) and feature docs (Q-header / Recommendation / horizon rules). It does **not** cover `{NAME} ask.md` files — the bare-`/ask` rendered surface — even though those pages are the primary user-facing dashboard for "what does the agent need from me?" Drift between ask.md content and reality currently surfaces only when the user notices manually.

Independent failure mode: the agent routinely emits backtick-quoted file-paths in chat AND in markdown body text (e.g., `` `~/.claude/skills/role/role-pilot.md` ``) where a clickable wiki-link or markdown-link belongs. The user reasonably objects: *"the system gives me a file path... not a link. So I can't actually look at the file without going into my file system and typing it."* The fix is a mechanical 100%-replacement rule: any backtick-quoted token that parses as a file-path gets rewritten to `[[basename]]` (if the basename resolves in the vault index) or `[basename](path)` (markdown link) — every time, no exceptions.

Both fixes ship as a single audit-discipline extension: (1) ask.md joins Q.md as a first-class audit surface; (2) a new C36 check forbids backtick-filepaths on both surfaces; the `--fix` path mechanically replaces them.

## Success Criteria

**Tier:** 1 (agent-immediate) for the check + mechanical-fix surface; Tier 3 (user-passive) for the QFix residuals.
**Blocks next:** none

**What done looks like.**
1. `audit-q.py` exposes a new check **C36** (backtick-filepath should be link) that fires on Q.md AND every per-anchor `{NAME} ask.md` AND every anchor backlog (sources that Q.md is rendered from).
2. `audit-q.py --fix` mechanically replaces a detected backtick-filepath when the replacement is provably safe — see *Mechanical-fix rules* below.
3. Non-mechanical residuals route to the owning anchor's `B-QFix [Ready]` row per the audit governing principle; the user resolves them via `/triage` or `/groom` when they next touch each anchor.
4. C36 SKIPs audit-residual sub-bullet lines (`- **C<NN>** ...` and `- **D<NN>** ...`) so the QFix row's own descriptions don't get re-flagged as new findings (would create unbounded recursion).
5. Re-rendering `{NAME} ask.md` via `ask-render.py` after the fix produces output that still passes audit (round-trip stable).

**Mechanical-fix rules.** A backtick-quoted token gets replaced ONLY when:
- **Wiki-link path:** the basename is `.md` AND uniquely resolvable in the vault index → emit `[[stem]]`. Ambiguous basenames (`SKILL.md` ×46 in vault, `README.md`, etc.) are skipped — the resulting wiki-link resolves "somewhere" via path-proximity but the reader can't tell which target the author meant.
- **Absolute-path markdown link:** the path starts with `/` or `~/` AND the file exists on disk → emit `[name](path)`. Absolute paths resolve correctly through `_parse_markdown` and don't trigger C1/C22 link-existence errors downstream.
- Everything else (relative bare basenames, non-existent paths, directories, ambiguous `.md` stems) → stays as backticks; routes to QFix.

**How it will be verified.**
1. `python3 ~/.claude/skills/audit/scripts/audit-q.py --scope q --dry` shows 0 errors after the fix run (Tier 1, agent-runs-it). Residual warnings are expected and acceptable — they're QFix-routed for human review per the audit governing principle.
2. Eyeball: open `Q.md` in Obsidian, confirm previously-bare-backtick paths to vault docs (`SKILL.md`, `role-pilot.md`, etc.) now render as clickable wiki-links.

## Design

### Components

```
~/.claude/skills/audit/scripts/audit-q.py
  ↳ new check_c36_backtick_filepath(...)
  ↳ new apply_c36_fix(...)
  ↳ extended Q.md-scope to include every {NAME} ask.md surface
```

### C36 — backtick-quoted file-paths must be links

**Trigger.** A bullet line on `Q.md` or `{NAME} ask.md` contains a backtick-quoted token that looks like a file-path:

- Absolute: `` `/Users/...` `` or `` `/etc/...` ``
- Home-relative: `` `~/path/...` ``
- Relative: `` `./path/...` `` or `` `../path/...` ``
- Bare filename with a recognized extension: `` `audit-q.py` ``, `` `SKILL.md` ``, `` `migrate-f113.py` `` (extensions: `.md`, `.py`, `.sh`, `.yaml`, `.yml`, `.toml`, `.json`, `.txt`, `.html`, `.css`, `.rs`, `.ts`, `.tsx`, `.js`, `.jsx`)

**Exclusions** (do NOT flag):
- Backtick-quoted *commands* containing arguments / flags (`` `git add -u` ``, `` `audit-q.py --scope q` ``) — recognized by presence of whitespace or `--` after the path-like prefix.
- Backtick-quoted *patterns* that contain glob/regex metacharacters (`*`, `?`, `[`).
- Backtick-quoted *code fragments* — heuristic: presence of `()`, `=`, `{`, etc.
- File-paths *already inside* a markdown-link target `[text](path)` or wiki-link `[[name]]`.
- File-paths inside fenced code blocks (``` `…` ```).

**Severity.** Warning (mechanically fixable via `--fix`).

**Fix.** Replace `` `<path>` `` with:
- `[[<basename>]]` — when the basename (stem without extension for `.md`, or full filename for others) resolves uniquely in the vault index (`build_vault_index` already exists in audit-q.py).
- `[<basename>](<path>)` — when the basename doesn't resolve cleanly OR the file is non-`.md` (Obsidian wiki-links don't follow `.py` reliably).
- Skip with a `# unresolved` warning if neither path resolves and the basename isn't in the vault — surfaces as a manual-review residual on QFix.

### ask.md joins the Q.md scope

The Q.md scope in `audit-q.py` currently walks `Q.md` only. Extension: also walk every `{NAME} ask.md` reachable from `find_anchor_backlogs(...)`. The existing C1/C2 link-integrity checks apply unchanged (just iterate over the additional file list); the new C36 check applies to both surfaces.

**Edge case** — ask.md files are *generated by `ask-render.py`*. The `--fix` pass on ask.md mutates a derived artifact; the next `ask-render.py` run would regenerate it and could re-introduce backticks if the renderer itself emits them. Mitigation: `ask-render.py` reads the existing ask.md and preserves the `## Agent Resolutions` body verbatim — so once the body is clean of backtick-filepaths, regen preserves the cleanup. The Questions section is built fresh from feature-doc Q-bullets and never contains paths inline (only feature-doc wiki-links), so it's naturally clean.

### Auto-decisions (announced, not asked)

- **Check code = C36.** Next unused integer after C35 (F124's drift check). Stable forever per audit-q numbering policy.
- **Severity = warning + mechanically fixable.** Matches C10 (Recommendation outdent), C24 (Questions count mismatch), C25 (Designing justification). Per `[[audit-q]]` § Governing principle: every C-code drives toward 100% fix; warning + fix path is the standard shape.
- **Replacement form preference.** Wiki-link `[[basename]]` for `.md` files (Obsidian-native), markdown-link `[basename](path)` for everything else (works in any markdown renderer). User can iterate on this preference; both forms are cheap to swap.
- **Extension whitelist** — `.md`, `.py`, `.sh`, `.yaml`, `.yml`, `.toml`, `.json`, `.txt`, `.html`, `.css`, `.rs`, `.ts`, `.tsx`, `.js`, `.jsx`. Covers the user's known file types; missing extensions can be added when a real false-negative surfaces.
- **Scope = Q.md + every `{NAME} ask.md`** for v1. Vault-wide application (every markdown file) is a future enhancement — starting with the two named surfaces matches the user's stated trigger (*"audit on cue and run that same audit on ask"*) and keeps the v1 blast radius bounded.

### Implementation plan

1. **`check_c36_backtick_filepath(file_path: Path, vault_index) -> list[Finding]`** — read file, scan line-by-line, detect backtick-quoted file-path tokens (regex), filter against exclusions, emit a `Finding` per hit with the suggested replacement in the message.
2. **`apply_c36_fix(file_path, findings) -> int`** — for each finding on this file (descending line order so column offsets don't shift), perform the in-place replacement. Returns the count of fixes applied. Idempotent: re-running on a clean file is a no-op.
3. **Extend the Q.md-scope branch** in `main()` to iterate over `[Q_MD] + [backlog_file.parent / f"{name} ask.md" for name, backlog_file in anchor_backlogs.items() if (backlog_file.parent / f"{name} ask.md").exists()]`.
4. **C36 in the C-code registry** — add to the dispatch + the help text + the QFix residual routing if a fix can't be auto-applied.

### Test strategy

- Add a Python smoke test in `~/ob/kmr/Topic/Misc/Test/F126/` (per durable feedback: smoke tests live in the vault, not /tmp): a fixture file with known backtick-filepath patterns + expected post-fix output. Run `audit-q.py --fix` against the fixture, diff against expected.
- Run `audit-q.py --scope q --dry` on the live vault, capture finding count, run `--fix`, capture 0 findings, run again (idempotency).

## Roadmap

Single-phase v1 — all auto-decisions ship together; no Phase 2 deferred work.

## Status

**Verify** — v1 shipped 2026-06-07. C36 check + apply_c36_fix wired into audit-q.py § scope=q path. Scope extended to Q.md + every per-anchor `{NAME} ask.md` + every anchor backlog (backlog rows are the source content that triage-section.py copies into Q.md, so source-fix is durable). Two false-start iterations were rolled back via git (broken markdown links + wiki-links to ambiguous basenames); final discipline: ONLY emit `[[basename]]` when basename is `.md` AND unique in the vault index — everything else routes to QFix for human judgment. Vault-wide sweep applied (skills@dd52173, kmr@afbda4ad5): 0 errors, 311 warnings on QFix. Tier 3 user-passive verify — the 311 QFix residuals chip down as the user touches each anchor's `/triage` or `/groom` over time.

## Resolved

### Audit code assignment (agent-decided)
**Choice:** C36 — next unused integer after F124's C35. Stable forever per audit-q numbering policy. Visible (audit-q output names the code) + low recoverability (renumbering is mechanical if a collision is later discovered).

### Replacement form for .md vs non-.md (agent-decided)
**Choice:** `.md` → `[[basename]]` wiki-link (Obsidian-native, no path text needed); non-`.md` → `[basename](path)` markdown link (renders in any viewer, preserves the path). Visible + low recoverability — both forms are cheap to swap if user prefers different policy.

### Scope = Q.md + per-anchor ask.md for v1 (agent-decided)
**Choice:** Apply the audit to Q.md AND every `{NAME} ask.md` reachable from `find_anchor_backlogs(...)`. Vault-wide application (every markdown file) is out of scope for v1 — matches the user's stated trigger ("audit on cue and run that same audit on ask") and keeps the blast radius bounded. Future enhancement file-able when needed.

### Extension whitelist (agent-decided)
**Choice:** `.md`, `.py`, `.sh`, `.yaml`, `.yml`, `.toml`, `.json`, `.txt`, `.html`, `.css`, `.rs`, `.ts`, `.tsx`, `.js`, `.jsx`. Covers known file types in the user's workflow; user can extend when a real false-negative surfaces. Visible + low recoverability.
