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

## 2026-08-26 — R-ob-remote-ops-01 denies the only sanctioned route to a Wi…

*from: atticus · tag: fact*

> Hit 2026-08-26 reading two values off [[Computer Turbo|Turbo]] (Eli's Windows 11 laptop) to grade ATT T263/T264. The rule denied a plain one-shot invocation against that host and redirected to the `bridge` skill — but bridge is Mac/Aqua/tmux machinery end to end, Turbo has no bridge host entry, and the vault's own standing note for that machine says in as many words: *"No tmux bridge — the bridge skill is Mac/Aqua/tmux-oriented and does not apply to Windows. Drive Turbo via a persistent SSH session (PowerShell), not the tmux bridge machinery."* So the rule's stated fix does not exist on the host it was blocking.
>
> Three smaller edges found alongside it, all cheap to fix.
>
> **The `# oneshot:` hatch is on -02 only, not -01.** The bridge skill documents the hatch in one place, under unattended work, and -01's steer text does not mention it — so a bounded *read* has no declared escape at all. I appended a real `# oneshot:` reason and it was denied anyway: correct behaviour for a rule that has no hatch, and surprising for an agent that had just read the skill.
>
> **The skill and the rule disagree in writing.** [[DAS Bridge]] § When NOT to use bridge says *"One-shot read on a non-TCC path → plain ssh to the host"* — exactly the case -01 denies. One of the two is wrong and an agent reading both cannot tell which.
>
> **It also fires on prose.** This very message was refused on its first send, because the paragraph above quoted the offending command shape in order to describe it. Reporting a rule's false positive tripped the rule. The match is against raw command text with no awareness that the text is an argument to `state drop` rather than something about to be executed, so any write that *documents* a denied pattern — an inbox drop, a backlog row, a doc edit through a shell — is itself denied. That is a small thing that quietly biases the record toward vagueness, since the way past it is to stop quoting the exact command.
>
> **What I actually did**, so the workaround is on the record rather than rediscovered: ran it inside `ctrl box`, a persistent local tmux session driving a persistent SSH — the shape the Turbo note prescribes, and the thing -01 exists to get instead of a bare one-shot. It satisfies the rule's intent, and the rule still had to be routed around to reach it.
>
> Not proposing the fix — whether -01 should exempt non-Mac hosts, grow the `# oneshot:` hatch, or point somewhere other than bridge for Windows is Warden's call with the skill's owner.

## 2026-08-26 — The fire log cannot support a soak longer than ~6 days, and…

*from: atticus · tag: fact*

> Found 2026-08-26 while grading [[ATT Backlog#^T157|ATT T157]], a soak on `R-ob-remote-ops-02` armed 2026-08-15 for a read on 08-24. Two of its three counts came back ungradeable, and neither reason is about the rule.
>
> **1. Retention is ~6 days, hard.** `warden_hook.py` sets `FIRES_ROTATE_BYTES = 5 MB` and keeps one `.1` generation, so ~10 MB total. At the observed rate (5.2 MB in ~3 days) the surviving window on 2026-08-26 was **3.7 days** — 2026-08-22 20:05 onward. Any soak, review or adoption question scheduled more than a few days out reads a log that has already discarded the period it was asking about, and **nothing in the output says so** — it just returns a smaller number.
>
> **2. A fire record carries no command.** Every record has `"file": ""`. It keeps `considered`, `fires` (rule id + steer verbatim), `anchor`, `moment`, `ms`, `traits`. That makes the `# oneshot:` escape hatch **invisible by construction** — a bypass does not fire the rule, so it leaves only a `considered, silent` record indistinguishable from any other Bash call, and the reason the agent wrote is never stored anywhere. T157 was designed to read those reasons and judge whether they were real; there was nothing to read.
>
> A live trap worth knowing about: six records in the log *mention* `oneshot:`, and they are the six **denies** whose own steer text advertises the hatch. A grader counting mentions would have reported "6 bypasses" — a number that is purely an artifact of the deny message. It cost one wrong count here before the record shape was checked.
>
> Not filing a fix — the retention/verbosity trade is Warden's call, and a per-rule opt-in for command capture may be the right shape rather than logging every command by default. Atticus only needs to know which questions the log can and cannot answer, and T157 is closed on the evidence that existed rather than re-armed against the same limit.

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
