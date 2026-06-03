---
name: vox
description: >
  File voice-memo audio into the VOX folder with a whisper-transcribed `.md`
  sibling. Two surfaces. (1) Manual mode — `/vox` (no args) scans `~/Desktop`
  and `~/Downloads` for audio files and processes each; `/vox <path>` processes
  one named file or every audio file in a named directory. Each filed source is
  removed from its original location (the canonical copy lives in the VOX folder
  with 40-day retention). (2) Email mode — an Apple Mail rule catches messages
  whose subject contains "VOX" and routes the attachment through the same
  `vox-process` script. Both modes share SHA-256 content dedup, audio-metadata
  date extraction, and the same retention sweep. Use when the user says "/vox",
  "vox these files", "process these voice memos", "transcribe these audio
  files", or hands you a path to one or more audio files to file.
tools: Read, Edit, Write, Bash
user_invocable: true
---

# vox — File voice memos with transcripts

`vox-process` files an audio file into `~/ob/kmr/Log/VOX/` as `<date> <title>.<ext>` paired with a `<date> <title>.md` whisper.cpp transcript. The skill is the user-facing wrapper: it finds the audio (or accepts a path), calls the script, and reports what happened.

## File layout

```
~/ob/kmr/Log/VOX/
  YYYY-MM-DD <title>.m4a       # audio (kept for 40 days, then pruned if transcribed)
  YYYY-MM-DD <title>.md        # transcript (kept forever)
  .vox.log                     # operational log
  .vox.hashes                  # SHA-256 dedup index
```

## Underlying script — `~/.claude/skills/vox/scripts/vox-process`

```
vox-process --input <audio-path>          (manual: file + delete source)
vox-process <audio-path> "<subject>" [vtt-path]
                                          (email-rule: routes by subject)
```

Both call the shared `handle_vox` pipeline, which:

1. Computes the audio's SHA-256 and checks `.vox.hashes`. If the hash is already filed → **log a SKIP, return.** No transcription, no copy. The hash stays in the index even after the 40-day audio prune deletes the `.m4a`, so a re-send years later still dedups.
2. Runs whisper.cpp against the audio for a local transcript.
3. Asks the Claude API (tool-less, sandboxed) for a 3–6 word title from the transcript.
4. **Derives the filename date from the audio metadata** (`creation_time` for m4a/mp4, `date`/TDRC for mp3) — this is the actual recording time. Only if metadata is absent does it fall back to a `YYYY-MM-DD` in the email subject.
5. Picks a collision-free basename via `unique_base`, copies the audio + writes the transcript markdown, appends the hash to `.vox.hashes`.
6. (`--input` mode only) Deletes the source file.
7. Runs the retention sweep — `.m4a` files older than 40 days are deleted **only if** their paired `.md` holds a non-trivial transcript; transcripts are always kept.

## Actions

### `/vox` (no args) — scan Desktop + Downloads

1. List audio files in `~/Desktop` and `~/Downloads` matching `*.mp3`, `*.m4a`, `*.wav`, `*.caf`, `*.aac`, `*.aiff`, `*.aif`, `*.mp4`, `*.m4b` (case-insensitive). If both folders have zero matches, say so and stop.
2. For each match, invoke:
   ```bash
   ~/.claude/skills/vox/scripts/vox-process --input "<path>"
   ```
   Capture the script's stdout (one line per call: either `vox-process: VOX -> wrote …` for new files or `vox-process: VOX -> skipped (duplicate of …)` for dedup'd ones).
3. Print a chat summary:
   ```
   /vox — processed N file(s) from Desktop/Downloads:
     ✓ <name1>.m4a → 2026-06-03 <derived-title>.m4a
     ✓ <name2>.m4a → 2026-06-03 <derived-title>.m4a
     ⊘ <name3>.m4a — duplicate of 2026-05-28 <existing>.m4a (source still removed)
   ```

### `/vox <path>` — file a specific path

1. If `<path>` is a file: invoke `vox-process --input "<path>"`. Print the result line.
2. If `<path>` is a directory: list audio files in that directory (non-recursive) and process each. Same summary format as bare `/vox`.
3. If `<path>` doesn't exist: error out — don't fall back to scanning Desktop, since the user named a specific path.

### Other invocation phrases

When the user says "vox these files" / "process these voice memos" / "transcribe these audio files" without an explicit path, treat as `/vox` (scan Desktop + Downloads).

When the user mentions specific filenames in conversation ("vox the 02-04 recording on my desktop"), invoke `/vox ~/Desktop/<specific-file>` if disambiguation is clear; otherwise list candidates and ask.

## Email mode (user-configurable)

The repo also ships `~/.claude/skills/vox/scripts/vox-process.applescript`, an Apple Mail rule action that:

- Watches incoming mail for a subject containing "VOX".
- Saves audio attachments to `~/Library/Caches/ob_process_email/`.
- Backgrounds `vox-process <staged-audio> "<subject>"` — the positional invocation, which leaves the source alone (Apple Mail's cache cleans itself up).

Setup (the user's personal configuration — others' mail clients will differ):

```bash
# Compile the AppleScript into Mail's actions folder
osacompile -o "$HOME/Library/Application Scripts/com.apple.mail/ob_process_email.scpt" \
           "$HOME/.claude/skills/vox/scripts/vox-process.applescript"
```

Then in Mail ▸ Settings ▸ Rules, add a rule with **Condition: Subject contains "VOX"** and **Action: Run AppleScript ▸ ob_process_email**. The account must download attachments locally (Mail ▸ Settings ▸ Accounts ▸ <account> ▸ Account Information → Download Attachments: All).

Other mail clients can wire the same shell call through their own filter/rule mechanism — the script's positional invocation accepts an audio path + subject; only the Mail rule and AppleScript are macOS-specific.

## Backward compatibility

A symlink at `~/ob/bin/ob_process_email → ~/.claude/skills/vox/scripts/vox-process` keeps the previous wiring working (the AppleScript previously referenced `~/bin/ob_process_email`; that path still resolves via `~/bin` → `~/ob/bin` → the symlink → the new location). After recompiling the AppleScript with the updated `procBin` path, the symlink is no longer load-bearing but kept as a finder for users who go looking under `~/bin/`.

## Configurable knobs (env vars)

| Var | Default | Meaning |
|---|---|---|
| `VOX_DIR` | `~/ob/kmr/Log/VOX` | Where files land |
| `VOX_LOG` | `$VOX_DIR/.vox.log` | Operational log |
| `VOX_HASHES` | `$VOX_DIR/.vox.hashes` | Dedup index |
| `VOX_RETENTION_DAYS` | `40` | Days before an `.m4a` is eligible for pruning |
| `VOX_MIN_TRANSCRIPT_CHARS` | `100` | Smallest "non-trivial" transcript that allows pruning the paired audio |
| `VOX_TINY_MP3_BYTES` | `51200` | `.m4a` smaller than this is treated as failed/empty — deleted unconditionally when old |
| `VOX_TITLE_MODEL` | `claude-haiku-4-5-20251001` | Anthropic model for title derivation |
| `ANTHROPIC_KEY_FILE` | `~/.config/anthropic/api_key` | Where the title-API key is read from |
| `WHISPER_BIN` | `/opt/homebrew/bin/whisper-cli` | whisper.cpp CLI path |
| `WHISPER_MODEL` | `~/whisper-models/ggml-large-v3-turbo.bin` | whisper model file |
| `FFMPEG_BIN` | `/opt/homebrew/bin/ffmpeg` | ffmpeg path (used for audio resample + metadata extraction) |

## Notes

- **The audio file path is the canonical anchor for dedup.** Same content → same SHA-256 → dedup hits. Different sources (re-encoded, edited) → different hashes → both filed.
- **Filename dates come from audio metadata first.** Most modern voice-memo apps write `creation_time` to the m4a container; the script reads it via ffprobe. Subject-line `YYYY-MM-DD` is the fallback if metadata is absent.
- **Transcripts are always preserved.** The 40-day prune deletes audio only when a non-trivial transcript exists alongside.
- **Dedup is content-based, not metadata-based.** Re-encoding the same recording to different bitrates will produce different SHA-256s and file twice. If that becomes a problem, an upgrade to transcript-based dedup is possible.
