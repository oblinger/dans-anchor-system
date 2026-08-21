---
description: Warden inbox — raw input dropped for later processing.
---

| -[[Warden Inbox]]- |  |
| --- | --- |
| --- | |
| [[Design-Rules Catalog Proposal]]  | F218 deliverable — the mined design-rules catalog. UPGRADED 2026-07-05 (Q3 = A): all nine families live under library/Rulesets/ as R-arch / R-process children; this doc keeps the mining record, the parked-borderline list, and the executed housekeeping. |
| [[Warden Audit 2026-07-12]]  |  |
| [[Warden Backlog]]  | deferred work — roadmap milestones M0–M5 |
| [[Warden Dev Ruleset]]  | R-warden-dev — the first REAL Warden rule fired live (F220 dogfood): orients any agent working in the Warden anchor to its dev disciplines |
| [[Warden Exceptions]]  | numbered, graded accepted deviations from the rulesets the Warden anchor adopts (R-exception-discipline) — a violation neither fixed nor listed here is an open finding |
| [[Warden Features]]  | dated feature specs (F209–F217, F017) |
| [[Warden Messages]]  | agent inbox — background-process messages for this anchor; append-only. See [[DAS Messages]]. |
| [[Warden queries]]  | Warden queries — mechanically rendered from the backlog (Blockers / Ready+Next / Questions / Blocked / Verifications / Other), and copied verbatim into Q.md. Do not hand-edit; edit the backlog rows. |

# Warden Inbox
Drop zone for raw input; an entry with no status tag is pending, and draining writes `DONE` or `MOVED → {destination}` per [[DAS Inbox]].

## 2026-08-20 — A compiled ruleset cache wrote itself into the vault root

*from: atticus · tag: fact*

> Cleaning the kmr root (ATT T242) turned up `~/ob/kmr/umbrella/R-anchor-450377da353065e3.json` — a compiled `R-anchor` ruleset cache sitting in a directory named `umbrella` at the **vault root**, and **git-tracked**, so it has been committed.
>
> The file's first key is `{"umbrella": "R-anchor", "rulesets": [...]}`, and the directory it landed in is literally named `umbrella`. That shape says the output path was built from the JSON's own key rather than from a configured cache directory — which means the cache lands relative to whatever cwd the compile happened to run from. It ran from `~/ob/kmr/` at least once (mtime 2026-08-02 08:45).
>
> Two things worth knowing before deciding what to do:
>
> - **Nothing else in the vault has this shape.** A `find -maxdepth 4 -type d -name umbrella` across kmr returns exactly one hit, so this is not yet a spreading mess — it is one escape.
> - **I did not delete it**, deliberately. A regenerable cache deleted without fixing the writer just reappears at the next compile's cwd, and the next cwd might be somewhere less obvious than the vault root. The disposal is yours to sequence with the fix.
>
> For reference, `~/.config/anchor-system/` already has `rule/` and `warden/` directories, which look like where this was meant to go — `rule/` currently holds only `discovery-report.md`.
>
> No action needed from me; Atticus's root cleanup is closed either way (the four remaining root directories are ATT T244). Flagging it because a cache that writes to cwd is cheap to fix now and irritating to chase later.

## 2026-08-13 — Your hook engines now execute the DAS hook registry (TINK F…

*from: tink · tag: fact*

> Committed to your repo as `7eda348` (main, NOT pushed — your call): `warden_hook.run_registry` + its `hook.rs` mirror, called after dispatch in both engines. At each event, lines in `~/.config/anchor-system/hooks/registry` matching the event's moments run in file order; child stdout joins additionalContext; failures are logged to `~/.config/anchor-system/hooks/hook-run.log` (the DAS runner's shared log) and never suppress neighbours or the hook. Env overrides DAS_HOOK_REGISTRY / DAS_HOOK_LOG; the differential harness pins both engines identical (new case 12) and now pins DAS_HOOK_REGISTRY in `_env` so live entries cannot leak into differential runs. Suites at commit: rs unit 15/15, test_warden_hook.py green, differential 14/14. The live registry is empty of entries today, so live behavior is unchanged until something installs. Rationale + grammar: [[TINK328 - Hook registry - one intelligent installer for every hook moment|TINK F328]].

## 2026-08-11 — R-markdown-05 breaks wiki-links containing ' — '

*from: atticus · tag: note*

> **R-markdown-05 rewrites ` -- ` inside wiki-link targets and silently breaks the links** — The auto-fix converts a spaced double-hyphen to an em-dash **without excluding `[[…]]` interiors**, so any file holding a link whose *filename* contains ` -- ` has that link destroyed the moment anything writes to the file. Caught in the act 2026-08-08 on `SV/SV People/SV Individuals/@Sports Visio.md`: an unrelated one-line edit fired the fixer, which rewrote `[[@Achilles -- Tomas Sasovsky]]` → `[[@Achilles — Tomas Sasovsky]]` and `[[@Nazareno Cavazzon -- Nasa]]` → `[[@Nazareno Cavazzon — Nasa]]`. Both target files are really named with `--` on disk, so both links went dead. Confirmed by `git diff`, not inferred. **Refinement found while filing this note:** the rule *does* already exclude inline-code spans — the examples above survived inside backticks — so the exclusion machinery exists and simply does not cover `[[…]]` in prose. That should make the fix small. **This is the damaging shape, not a cosmetic one:** the fixer reports success (`✓ fixed R-markdown-05 — converted spaced (double-hyphen) to (em-dash)`), the edit that triggered it touched a different part of the file entirely, and a broken wiki-link renders as ordinary text in Obsidian rather than erroring — so nothing surfaces it. The agent that made the edit is the only witness, and only if it reads the diff. **Blast radius: 14 files** hold at least one ` -- ` inside a `[[…]]`, including `SV Individuals.md`, `Employees at Sports Visio.md`, `By Job Sports Visio.md`, `EOC.md`, `Legal.md`, `MGR.md`, `EduCorp.md` and `CMP System Design.md`; the targets span person pages, `.pptx`/`.pdf` attachments and heading anchors (`[[#Corp_AI -- Rise of a new world power -- The Corp AGI]]`). Every one is a live tripwire — the next ordinary write to any of them breaks its links.
>   - **Next:** Make the ` -- ` → ` — ` substitution skip link interiors before it runs anywhere else: exclude the span of every `[[…]]` (and, for the same reason, `[…](…)` targets and inline/fenced code) from the rule's match region. Then sweep the 14 files above for already-corrupted targets — `grep -rn "\[\[[^]]* — [^]]*\]\]"` cross-checked against real filenames finds them — and restore any that no longer resolve. The two in `@Sports Visio.md` were restored by hand 2026-08-08 via a non-Edit write path (a direct `python3` rewrite, chosen precisely because Edit would have re-fired the fixer and undone the repair); that workaround is the tell that the rule, not the file, is what needs fixing.
