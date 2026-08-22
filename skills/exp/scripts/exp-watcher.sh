#!/bin/bash
# Remote watcher — runs on vast.ai in a tmux session.
# Polls for /workspace/_run.cmd, executes it, writes /workspace/_done.
#
# The user sees all output in their tmux session.
# Claude triggers execution by writing _run.cmd via SSH.
#
# Accepts EXP_REMOTE_NAME env var (passed by exp-init via tmux) to tag output.

WATCH_DIR="/workspace"
CMD_FILE="$WATCH_DIR/_run.cmd"
DONE_FILE="$WATCH_DIR/_done"
PYTHON="/venv/main/bin/python"
TAG="${EXP_REMOTE_NAME:+[$EXP_REMOTE_NAME] }"

# How commands get their own process group — decided once, announced once.
# `setsid` is part of util-linux: absent on macOS entirely and on minimal
# containers. Calling it unguarded means every command on such a host returns
# `setsid: command not found` and exit 127 — which the watcher then reports as
# the COMMAND's exit code, so the experiment takes the blame for the watcher.
# `set -m` (POSIX job control) makes a backgrounded job a process-group leader
# too, which is the only property `kill -- -$CMD_PID` below needs.
if command -v setsid >/dev/null 2>&1; then
    EXP_PGROUP_MODE="setsid"
else
    EXP_PGROUP_MODE="set -m"
fi

echo "========================================"
echo "  ${TAG}Watcher ready.  Waiting for commands."
echo "  ${TAG}process groups via: $EXP_PGROUP_MODE"
echo "========================================"
echo ""

while true; do
    if [ -f "$CMD_FILE" ]; then
        # _run.cmd format: line 1 = nonce, line 2 = command
        # If no nonce line (legacy), treat the whole file as the command.
        local_nonce=""
        CMD=""
        lines_read=0
        while IFS= read -r line; do
            if [ "$lines_read" -eq 0 ] && [[ "$line" == EXP-* ]]; then
                local_nonce="$line"
            elif [ "$lines_read" -eq 0 ]; then
                CMD="$line"  # legacy format: no nonce
            else
                CMD="$line"
            fi
            lines_read=$((lines_read + 1))
        done < "$CMD_FILE"
        rm -f "$CMD_FILE" "$DONE_FILE"

        START=$(date +%s)
        echo ""
        echo ">>> ${TAG}$CMD"
        echo ">>> ${TAG}started $(date '+%H:%M:%S')"
        echo ""

        # Execute from /workspace in its OWN PROCESS GROUP so killing the
        # command can never affect the watcher process. See EXP_PGROUP_MODE
        # above for why this is not an unguarded `setsid`.
        cd "$WATCH_DIR"
        if [ "$EXP_PGROUP_MODE" = "setsid" ]; then
            setsid bash -c "$CMD" &
        else
            set -m
            bash -c "$CMD" &
            set +m
        fi
        CMD_PID=$!
        echo "$CMD_PID" > "$WATCH_DIR/_pid"

        # Poll instead of blocking wait — lets us detect new _run.cmd (preemption)
        # and stuck/zombie processes. If a new _run.cmd appears while we're running,
        # kill the current command and let the main loop pick up the new one.
        EXIT_CODE=""
        while true; do
            if ! kill -0 $CMD_PID 2>/dev/null; then
                # Process finished — collect exit code
                wait $CMD_PID 2>/dev/null
                EXIT_CODE=$?
                break
            fi
            if [ -f "$CMD_FILE" ]; then
                # New command arrived — preempt the running one
                echo ""
                echo ">>> ${TAG}PREEMPTED by new command — killing pid $CMD_PID"
                kill -- -$CMD_PID 2>/dev/null
                sleep 0.5
                kill -9 -- -$CMD_PID 2>/dev/null
                wait $CMD_PID 2>/dev/null
                EXIT_CODE=143  # SIGTERM
                break
            fi
            sleep 0.5
        done
        rm -f "$WATCH_DIR/_pid"

        END=$(date +%s)
        ELAPSED=$(( END - START ))

        # Signal completion: write nonce + exit code so the caller can
        # distinguish its result from a stale _done left by a previous run.
        if [ -n "$local_nonce" ]; then
            echo "${local_nonce} ${EXIT_CODE}" > "$DONE_FILE"
        else
            echo "$EXIT_CODE" > "$DONE_FILE"
        fi

        echo ""
        if [ $EXIT_CODE -eq 0 ]; then
            echo ">>> ${TAG}Done (${ELAPSED}s)"
        else
            echo ">>> ${TAG}FAILED exit=$EXIT_CODE (${ELAPSED}s)"
        fi
        echo "% "

        # Signal any waiting SSH session
        tmux wait-for -S "cmd-done" 2>/dev/null
    fi
    sleep 0.5
done
