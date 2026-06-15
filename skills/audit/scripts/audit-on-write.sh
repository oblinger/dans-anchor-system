#!/bin/bash
# audit-on-write.sh — F177 PostToolUse Write/Edit document-audit hook.
#
# Reads the PostToolUse JSON payload on stdin. For a `.md` write whose path sits
# under an opted-in root, it runs the doc audit (audit-plan --mode doc --on-write):
#   • mechanical findings WITH a fixer → repaired in place, silently;
#   • mechanical findings WITHOUT a fixer → surfaced to the agent as a message.
# Every other write is a fast no-op (pure-bash prefilter, no python spin-up).
#
# Opt-in is deliberate: a global write-hook that ran the full engine on every
# write would be slow and noisy. The roots file names the paths that want it.
# (The millisecond always-on fast-path is F166's /distill work, not this slice.)

payload=$(cat)

# Fast prefilter — extract file_path without spinning python.
fp=$(printf '%s' "$payload" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
[ -z "$fp" ] && exit 0
case "$fp" in *.md) ;; *) exit 0 ;; esac

# Never touch VCS / dependency dirs.
case "$fp" in */.git/*|*/node_modules/*) exit 0 ;; esac

# Scope. A `__VAULT__` sentinel line in the roots file = vault-wide (every .md under
# ~/ob/kmr); otherwise the file lists explicit roots and the hook acts only beneath
# one. Tests pass AUDIT_ON_WRITE_ROOTS to a scratch roots file for isolation.
ROOTS_FILE="${AUDIT_ON_WRITE_ROOTS:-$HOME/.config/ob-skills/audit-on-write-roots}"
[ -f "$ROOTS_FILE" ] || exit 0
if grep -qx '__VAULT__' "$ROOTS_FILE" 2>/dev/null; then
    case "$fp" in "$HOME/ob/kmr/"*) ;; *) exit 0 ;; esac
else
    match=0
    while IFS= read -r root; do
        [ -z "$root" ] && continue
        root="${root/#\~/$HOME}"
        case "$fp" in "$root"*) match=1; break ;; esac
    done < "$ROOTS_FILE"
    [ "$match" = 1 ] || exit 0
fi

AP="$HOME/.claude/skills/audit/scripts/audit-plan.py"
[ -f "$AP" ] || exit 0
out=$(python3 "$AP" "$fp" --mode doc --on-write --no-cache --json 2>/dev/null)
[ -z "$out" ] && exit 0

# Translate the engine's {fixed,messages} into a PostToolUse response — fixes are
# already applied on disk; messages become agent-visible additionalContext.
# (Pass the audit output via env, not stdin: stdin is consumed by the heredoc program.)
AOW_FP="$fp" AOW_OUT="$out" python3 - << 'PY'
import os, sys, json
fp = os.environ["AOW_FP"]
try:
    rep = json.loads(os.environ["AOW_OUT"])
except Exception:
    sys.exit(0)
fixed, msgs = rep.get("fixed", []), rep.get("messages", [])
if not fixed and not msgs:
    sys.exit(0)
lines = [f"auto-fixed {f['rule']} ({f['detail']})" for f in fixed]
for m in msgs:
    line = f"{m['rule']}: {m['detail']}"
    if m.get("why"):
        line += f"  [why: {m['why']}]"
    lines.append(line)
ctx = f"Document audit-on-write (F177) on {fp}:\n- " + "\n- ".join(lines)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                          "additionalContext": ctx}}))
PY
exit 0
