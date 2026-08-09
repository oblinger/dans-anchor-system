#!/usr/bin/env bash
# test-t176-agent-identity.sh — bridge must never DERIVE an agent identity.
#
# T171 gave every agent its own tmux window; T176 found the window name was
# derived from `$(basename "$PWD")-${CLAUDE_CODE_SESSION_ID:0:8}`, and that the
# Claude Code harness hands every subagent of a fan-out the SAME session id,
# pid, and messaging socket. So the derivation produced ONE window for four
# agents — the exact collision T171 exists to prevent.
#
# These tests pin the resolution order and, above all, the refusal. They are
# offline: `resolve_agent` and `sanitize_slug` are lifted out of `bridge` and
# evaluated here, so no host, no ssh, and no tmux server is involved.
#
# Run: bash test-t176-agent-identity.sh

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
BRIDGE="$HERE/bridge"
PASSED=0; FAILED=0

check() { # check <label> <got> <want>
  if [ "$2" = "$3" ]; then PASSED=$((PASSED+1)); printf '  ok    %s\n' "$1"
  else FAILED=$((FAILED+1)); printf '  FAIL  %s\n          got:  %s\n          want: %s\n' "$1" "$2" "$3"; fi
}

# Lift the two definitions out of `bridge` without running it — the script
# dispatches on $VERB at top level, so sourcing it would execute a verb.
lifted=$(awk '/^sanitize_slug\(\)/,/^}/' "$BRIDGE"; awk '/^resolve_agent\(\)/,/^}/' "$BRIDGE")
[ -n "$lifted" ] || { echo "FAIL  could not lift resolve_agent/sanitize_slug from $BRIDGE"; exit 1; }

# Resolve in a clean subshell: $1 = --agent value, $2 = $BRIDGE_AGENT value.
# Prints the resolved WINDOW, or "REFUSED" plus the refusal text on stderr.
resolve() {
  ( set +u
    AGENT_FLAG="${1:-}"
    export BRIDGE_AGENT="${2:-}"
    [ -z "${2:-}" ] && unset BRIDGE_AGENT
    fail() { printf 'REFUSED %s\n' "$*"; exit 7; }
    eval "$lifted"
    resolve_agent && printf '%s\n' "$WINDOW"
  ) 2>&1
}

echo "Resolution order — an explicit slug wins, then the environment"

out=$(CLAUDE_CODE_SESSION_ID=ba8ab4e2-b6fa-43b4 resolve "scout" "")
check "--agent wins" "$out" "agent-scout"

out=$(CLAUDE_CODE_SESSION_ID=ba8ab4e2-b6fa-43b4 resolve "" "reaper")
check "\$BRIDGE_AGENT is used when no --agent" "$out" "agent-reaper"

out=$(resolve "sc out/2" "")
check "a slug is sanitized to a tmux-safe window name" "$out" "agent-sc-out-2"

echo
echo "The refusal — nothing is derived, and a session id must not rescue it"

# The load-bearing case. Before T176 this returned a window derived from
# CLAUDE_CODE_SESSION_ID, which every sibling subagent shares.
out=$(CLAUDE_CODE_SESSION_ID=ba8ab4e2-b6fa-43b4-9b1c-b6c01ca5646c \
      CLAUDE_PID=25716 \
      CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/25716.sock \
      CLAUDE_CODE_CHILD_SESSION=1 \
      resolve "" "")
case "$out" in REFUSED*) v=refused ;; *) v="resolved to '$out'" ;; esac
check "a full Claude Code environment does NOT yield an identity" "$v" "refused"

case "$out" in *"--agent"*) v=yes ;; *) v=no ;; esac
check "the refusal names --agent as the fix" "$v" "yes"

case "$out" in *T176*) v=yes ;; *) v=no ;; esac
check "the refusal cites the measurement (T176) rather than just saying no" "$v" "yes"

out=$(resolve "" "")
case "$out" in REFUSED*) v=refused ;; *) v="resolved to '$out'" ;; esac
check "a bare environment refuses too" "$v" "refused"

# A slug of only separators sanitizes to empty — that must refuse, not produce
# the window literally named `agent-`, which every such caller would share.
out=$(resolve "///" "")
case "$out" in REFUSED*) v=refused ;; *) v="resolved to '$out'" ;; esac
check "a slug that sanitizes to empty refuses instead of becoming 'agent-'" "$v" "refused"

echo
echo "The source itself carries no derivation"

# The invariant is about EXPANSION, not about the word. The header block quotes
# the removed derivation to explain why it is gone, and the refusal message
# names the variable in prose so the agent reading it understands the reason —
# both are wanted. What must never come back is a `$`/`${` expansion outside a
# comment, which is the only form that can put a session id into a window name.
if grep -v '^[[:space:]]*#' "$BRIDGE" | grep -qE '\$\{?CLAUDE_CODE_SESSION_ID'; then d=present; else d=absent; fi
check "no live code in bridge EXPANDS \$CLAUDE_CODE_SESSION_ID" "$d" "absent"

if grep -c 'CLAUDE_CODE_SESSION_ID:0:8' "$BRIDGE" >/dev/null && \
   grep -q 'CLAUDE_CODE_SESSION_ID:0:8' "$BRIDGE"; then d=documented; else d=undocumented; fi
check "...and the removed derivation is still quoted in the comments, so it stays explained" "$d" "documented"

echo
printf '%d passed, %d failed\n' "$PASSED" "$FAILED"
[ "$FAILED" = 0 ] || exit 1
