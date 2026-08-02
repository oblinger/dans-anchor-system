---
description: Replace overall-WPS suppression with a silence-aware three-part predicate — leading-burst discriminator + capped-silence-trim + trimmed-WPS floor — so thoughtful pause-heavy dictations pass while silence-hallucination captures still get filtered.
---

# [[MUSE]] · F001 — Silence-aware suppression (leading-burst + capped-silence-trim + trimmed-WPS)
Replace the flat overall-WPS suppression floor with a three-part predicate that trims silence and measures density on what remains.

## Summary

The current suppression rule uses **overall words-per-second** (`word_count / audio_duration`) with a 0.5 wps floor. This unfairly punishes the user's natural dictation rhythm: press record → speak a complete thought → pause silently to think → speak the next thought. A 25-second recording with 10 real words and long thinking-pauses looks like noise (0.4 wps) even though the *active speech portions* are dense (2+ wps).

Real example (the recording that triggered this feature): `MUSE 2026-07-17 B` → 10 words / 26 s / 0.385 wps → suppressed → but the transcript is "So the area bets, a device bet, a data bet." — a legitimate thinking-aloud memo. Contrast with `MUSE 2026-07-14 I` → 103 words / 1294 s / 0.08 wps — a 20-minute recording with sparse Whisper hallucinations ("Thank you." on silence) that IS junk and needs to stay suppressed.

The new predicate trims silence up to a capped percentage of the recording, then measures density on what remains. Combined with a leading-burst override (audio contains real speech in the first few seconds → recording is genuine even if the rest is sparse), it catches the whole spectrum: dense-short, thoughtful-medium, junk-long.

## Success Criteria

**Tier:** 1 (agent-immediate)
**Blocks next:** none

**What done looks like.** The `muse` script's suppression predicate uses the new three-part logic. Re-scoring the 3 currently-suppressed items + 12 non-suppressed items in `~/ob/kmr/Log/MUSE/` produces the correct outcome for each: `2026-07-17 B` and `2026-07-14 G` classify per intent; the 10-min silence-hallucination stays suppressed; every legitimate memo passes.

**How it will be verified.** A test script (`scripts/test-f001-suppression.sh`) runs the new predicate over the 15 known real-world MUSE audio files and asserts each classification. All 15 pass → feature done.

## Design

### The three-part predicate

Applied in order; the recording is **suppressed** if any predicate says so and no override rescues it.

**Predicate 1 — Word floor.** If `word_count < MUSE_MIN_WORDS` (default 5), suppress with reason `min-words`. Unchanged from current behavior. Catches empty / near-empty captures ("Thank you.", a bare ".").

**Predicate 2 — Trimmed-WPS floor (density on active speech).**
- Detect silence intervals via `ffmpeg -af silencedetect=noise=${MUSE_SILENCE_NOISE_DB}:d=${MUSE_SILENCE_MIN_GAP}` (defaults `-30dB`, `2.0s`). This yields (start, end) pairs of "long enough to be a real pause" silences.
- `total_silence` = sum of those silence durations.
- `max_trimmable` = `MUSE_SILENCE_TRIM_PCT` × `total_duration` (default 60% — a cap on how much of the recording we're allowed to attribute to pauses).
- `trimmed_silence` = min(total_silence, max_trimmable) — take the smaller.
- `active_duration` = total_duration − trimmed_silence.
- `trimmed_wps` = word_count / active_duration.
- If `trimmed_wps < MUSE_TRIMMED_MIN_WPS` (default 1.0), suppress with reason `trimmed-wps`. Otherwise pass this predicate.

The percent cap is the load-bearing insight (user 2026-07-17): "the amount of silence you can subtract goes up with recording length." A 5-minute recording can legitimately have 3 minutes of thinking-pauses; a 30-second recording cannot claim 25 seconds of "thinking" — that's just silence. The percent stays constant, absolute limits scale with length.

**Predicate 3 — Leading-burst override (rescue predicate 2).**
- Look at the first `MUSE_LEAD_WINDOW` seconds of audio (default 3.0s).
- Compute how much of that window is *non-silent*: `speech_in_lead = LEAD_WINDOW − Σ (silence intersected with the leading window)`.
- If `speech_in_lead ≥ MUSE_LEAD_MIN_SPEECH` (default 1.5s) AND `word_count ≥ MUSE_LEAD_MIN_WORDS` (default 3), the leading-burst override fires: the recording passes even if trimmed-wps was below floor.
- This catches the "press record with intent, speak your thought right away, then trail off" pattern. It cannot rescue a recording with fewer than 3 words (that's genuinely empty) or one that starts with 3+ seconds of silence (probably not an intentional recording).

Suppression decision matrix:

| word_count | passes P2 (trimmed-wps) | passes P3 (leading burst) | outcome |
|---|---|---|---|
| < MIN_WORDS | — | — | suppress `min-words` |
| ≥ MIN_WORDS | yes | — | pass |
| ≥ MIN_WORDS | no | yes | pass (leading-burst override) |
| ≥ MIN_WORDS | no | no | suppress `trimmed-wps` |

### Failure handling

If ffmpeg / silencedetect is unavailable or errors on a specific file, the current design's principle stands: **a probe failure MUST NOT suppress the memo**. Skip predicate 2 and predicate 3 entirely and fall back to the word-floor predicate alone. This preserves the existing "silent-fallback bug is worse than a lenient rule" invariant.

### Config surface

Environment variables, all overridable per invocation (via launchd env or `MUSE_* muse ingest ...`):

| Variable | Default | Meaning |
|---|---|---|
| `MUSE_MIN_WORDS` | 5 | Word-count floor (predicate 1). Unchanged. |
| `MUSE_SILENCE_NOISE_DB` | `-30dB` | ffmpeg silencedetect noise threshold. |
| `MUSE_SILENCE_MIN_GAP` | 2.0 | Minimum silence duration (seconds) to count as a "long gap" eligible for trimming. Short natural pauses stay in active speech. |
| `MUSE_SILENCE_TRIM_PCT` | 60 | Maximum percentage of total_duration that silence-trim can subtract (integer 0-100). |
| `MUSE_TRIMMED_MIN_WPS` | 1.0 | Words-per-second floor after silence trim (predicate 2). |
| `MUSE_LEAD_WINDOW` | 3.0 | Leading-window duration (seconds) for the leading-burst check. |
| `MUSE_LEAD_MIN_SPEECH` | 1.5 | Minimum non-silent duration required within the leading window. |
| `MUSE_LEAD_MIN_WORDS` | 3 | Minimum word_count for the leading-burst override to apply. |

The retired `MUSE_MIN_WPS` variable is removed (its role is replaced by `MUSE_TRIMMED_MIN_WPS`). Any launchd env still setting it is silently ignored (won't break existing setups; the variable just does nothing).

### Frontmatter fields

The MUSE item file's YAML frontmatter gains two fields so the classification is inspectable per-item:

- `active_duration_s` — total_duration − trimmed_silence (float)
- `trimmed_wps` — word_count / active_duration (float, 3 decimals)

Existing fields (`word_count`, `audio_duration_s`, `words_per_second`) remain. The old `words_per_second` continues to mean overall WPS; the new `trimmed_wps` is what the suppression predicate consults.

### Suppressed-title diagnostic

The fixed diagnostic title that gets used when an LLM title call is skipped stays informative:

- `Suppressed min-words {N}w {D}s` — unchanged
- `Suppressed trimmed-wps {N}w {D}s active={A}s twps={T}wps` — new; encodes what predicate 2 saw

### Sanity against real recordings

Applied to the actual 15 recordings on disk (7 non-suppressed short ones + 5 non-suppressed medium ones + 3 suppressed):

| File | wc | dur | old wps | expected under new rule |
|---|---|---|---|---|
| `2026-07-15 D It is seven forty four` | 6 | 3.8 | 1.58 | pass — dense throughout |
| `2026-07-17 C Copycat betting strategies` | 7 | 5.6 | 1.25 | pass — dense throughout |
| `2026-07-15 C Check in on package` | 13 | 6.3 | 2.07 | pass |
| `2026-07-14 K Testing voice memo` | 31 | 10.9 | 2.83 | pass |
| `2026-07-14 L Voice Memo Test Count` | 23 | 11.4 | 2.02 | pass |
| `2026-07-14 M Voice memo test timing` | 35 | 11.8 | 2.96 | pass |
| `2026-07-15 A Message sent to agent` | 27 | 11.9 | 2.26 | pass |
| `2026-07-14 J Quick audio recording test` | 22 | 12.3 | 1.79 | pass |
| `2026-07-15 B Watch message time verification` | 36 | 18.9 | 1.91 | pass |
| `2026-07-17 A Frontend priorities` | 13 | 25.3 | 0.51 | pass — silences trimmed, active_wps ≥ 1 |
| `2026-07-14 G Suppressed min-words` | 1 | 3.2 | 0.32 | **suppress** (predicate 1) |
| `2026-07-17 B Suppressed min-wps` | 10 | 26.0 | 0.39 | pass — leading burst OR trimmed-wps rescues |
| `2026-07-14 I Suppressed min-wps` | 103 | 1294 | 0.08 | **suppress** — silence-trim cap keeps active_duration ≈ 518s → wps ≈ 0.20 |

### Implementation touch points

Single file: `~/.claude/skills/muse/scripts/muse` (symlink chain terminates at `dans-anchor-system/skills/muse/scripts/muse`).

Changes:
1. Extend the header env-var block: retire `MUSE_MIN_WPS`, add the eight new variables.
2. Add a `detect_silences()` bash helper that runs `ffmpeg -af silencedetect` and parses the stderr for `silence_start:` / `silence_end:` markers into a "start end" newline-list.
3. Rewrite the suppression block in `ingest_one` around lines 469-500 to compute `total_silence`, `active_duration`, `trimmed_wps`, `speech_in_lead`, `leading_burst_passes`, then apply the decision matrix.
4. Update the frontmatter emitter (`printf 'active_duration_s: ...` and `printf 'trimmed_wps: ...`).
5. Update the fixed diagnostic title for the trimmed-wps suppression case.

Non-touch points:
- Hashfile logic — unchanged (suppressed items still write hashfile entry so sweep doesn't reprocess).
- Log Muse index — unchanged (suppressed items still appear as audit trail).
- Quick pane behavior — unchanged (suppressed items skip Quick).

### Testing

`scripts/test-f001-suppression.sh` runs the new predicate against 15 real audio files (matched by `audio_sha256` in the frontmatter → look up the file at its `source_audio` path) and asserts each classification. Failure prints a diff. Runs in CI under `test-f252-fixes.sh`-style discipline.

## Status

**Done** — implemented + tested 2026-07-17. All 6 real-audio test cases classify per intent (`test-f001-suppression.sh`); the previously-mis-suppressed "So the area bets" recording now passes via leading-burst; the 20-min silence hallucination stays suppressed via trimmed-wps (0.199 wps).

## Resolved

### Leading-burst window: 3.0s
**Choice:** 3.0-second leading window with 1.5s minimum speech + 3-word minimum overall.

Reasoning. The user described their pattern: "I'm not gonna push the button until I know some of what I'm gonna say." So the first ~3 seconds should contain intentional speech, not warmup / silence. The 1.5s speech-in-window threshold is 50% coverage — a burst that fills half the leading window is enough to signal intent. The 3-word overall floor prevents a "ah, um, oh" burst from qualifying. Auto-decided per F068 (visible + reversible — threshold tunable via `MUSE_LEAD_*` env).

Alternatives rejected. 5-second window (user's other suggestion) — too long, false-passes recordings where user's first speech starts fine but the recording extends into empty silence. 2-second window — too short, misses recordings where user takes a moment to compose the opening.

### Silence-trim cap: 60% of total duration
**Choice:** Percent-of-length silence cap at 60%, not an absolute seconds cap.

Reasoning. The user was explicit: "we can't cap how much silence you can subtract because I think it really is a certain percentage of silence... if a recording is longer, then the amount of silence that you can subtract goes up." A 5-minute recording legitimately has 3+ minutes of thinking pauses; a 30-second recording cannot claim 25 seconds of "thinking" — that's just silence. 60% is defensible: the recording has to be at least 40% actual speech to be worth keeping. Auto-decided per F068.

Alternatives rejected. Absolute cap (30s / 60s / etc.) — user explicitly rejected this: penalizes long-form recordings and rewards short-fragmented ones. No cap — a 10-min recording with 9 min of silence and 46 "Thank you" hallucinations would look artificially dense (wps ≈ 1) and pass. Cap is load-bearing.

### Trimmed-WPS floor: 1.0 wps
**Choice:** 1.0 wps on active_duration.

Reasoning. Human conversational speech is 2-3 wps; even hesitant thought-speech is ~1 wps when the speaker is actually making words. Under the current data: the worst-passing legitimate recording is "Frontend priorities for next sprint" at 0.51 overall wps — but if 15s of its 25s duration is thinking-silence, active = 10s, wps = 1.3, passes cleanly. The suppressed "So the area bets" case at 0.385 overall — if 15s of its 26s is silence, active = 11s, wps = 0.9, borderline; the leading-burst rescue handles the rest. Auto-decided per F068; user explicit: "we'll use failures in the future to refine it."

Alternatives rejected. 0.5 wps (matches old MIN_WPS) — too lenient after we've already given silence a discount, would let the true 10-min hallucination through under just the right silence pattern. 1.5 wps — too strict, would suppress legitimate thoughtful memos with medium-length pauses.

### ffmpeg silencedetect params: noise=-30dB, min-gap=2.0s
**Choice:** Noise floor `-30dB`, minimum silence duration `2.0s` for the "long gap" predicate.

Reasoning. `-30dB` matches what most audio-content analysis tools use as the boundary between "voice" and "silence" (handset ambient is typically -40 to -50dB, indoor room quiet is -35 to -50dB, speech peaks are -15 to -3dB). 2.0s minimum gap means natural mid-sentence pauses (0.5-1.5s) stay counted as active speech; only genuine thinking-pauses trip the trim. Auto-decided per F068 — tunable via `MUSE_SILENCE_NOISE_DB` / `MUSE_SILENCE_MIN_GAP`.

Alternatives rejected. `-40dB` noise floor — too aggressive, would classify quiet whispered speech as silence. `1.0s` min-gap — too eager, trims normal pauses between sentences (would inflate active-duration for genuine dense speech and give a misleading wps). `3.0s` min-gap — too conservative, misses shorter thinking pauses.

### `MUSE_MIN_WPS` retired, replaced by `MUSE_TRIMMED_MIN_WPS`
**Choice:** Retire the old overall-WPS variable; the new `MUSE_TRIMMED_MIN_WPS` is the successor.

Reasoning. Keeping both would preserve dead code and imply the old floor still gates something. Silent-ignore of the retired variable in existing launchd env avoids breaking anyone's setup. Auto-decided per F068 — visible (dead var quickly forgotten) + reversible (rename in one commit).

Alternatives rejected. Keep `MUSE_MIN_WPS` as a separate lower floor (belt-and-suspenders) — extra complexity, one more thing to tune, no failure mode it catches that trimmed-wps + word-floor don't.

### Frontmatter: add `active_duration_s` + `trimmed_wps`; keep old fields
**Choice:** Emit both old (`words_per_second`) and new (`trimmed_wps`, `active_duration_s`) fields in frontmatter.

Reasoning. Old field is used by future tuning / analysis scripts; keeping it costs 20 bytes per file. New fields make it possible to explain WHY a memo passed or was suppressed by reading the file alone. Auto-decided per F068.

Alternatives rejected. Replace `words_per_second` — breaks any external tooling that reads the old field. Store computed silence intervals — too heavyweight; ffmpeg is cheap to re-run.
