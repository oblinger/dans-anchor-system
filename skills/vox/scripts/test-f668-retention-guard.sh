#!/bin/bash
V="/Users/oblinger/ob/kmr/SYS/Bespoke/Skill Agent/dans-anchor-system/skills/vox/scripts/vox-process"
eval "$(awk '/^transcriber_ran\(\) \{/,/^\}/' "$V")"
fails=0
chk () { if [ "$2" = "$3" ]; then echo "PASS  $1"; else echo "FAIL  $1 (got $2 want $3)"; fails=$((fails+1)); fi; }
mk () { printf '%s' "$2" > "$1"; }

mk a.md '---
type: vox-transcript
audio: "x.mp4"
transcribed: 2026-08-18
model: ggml-large-v3-turbo
---

# x

## Transcript

'
transcriber_ran a.md && r=yes || r=no
chk "no-speech note WITH transcribed: stamp -> prunable" "$r" yes

mk b.md '---
type: vox-transcript
audio: "x.mp4"
---

# x
## Transcript
'
transcriber_ran b.md && r=yes || r=no
chk "note with NO stamp -> falls through to size guard" "$r" no

mk c.md '# x

transcribed: 2026-08-18

body prose mentioning transcribed: 2026-01-01
'
transcriber_ran c.md && r=yes || r=no
chk "stamp in the BODY, no frontmatter -> not honoured" "$r" no

mk d.md '---
type: vox-transcript
---

## Transcript
transcribed: 2026-08-18
'
transcriber_ran d.md && r=yes || r=no
chk "stamp AFTER the closing --- -> not honoured" "$r" no

mk e.md '---
transcribed: not-a-date
---
'
transcriber_ran e.md && r=yes || r=no
chk "malformed stamp value -> not honoured" "$r" no

transcriber_ran /nonexistent.md && r=yes || r=no
chk "missing file -> not honoured" "$r" no

echo; echo "$( [ $fails -eq 0 ] && echo OK || echo FAILED ) — $fails failure(s)"
exit $fails
