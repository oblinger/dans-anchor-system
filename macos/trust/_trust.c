/*
 * _trust — signed launcher for FDA-gated background pipelines on macOS.
 *
 * WHY THIS EXISTS
 * ---------------
 * macOS Sequoia only honors Full Disk Access grants on compiled Mach-O
 * binaries that are Developer-ID-signed + Apple-notarized. Shell scripts
 * (SIP-managed /bin/bash identity), adhoc-signed apps, and shell scripts
 * inside signed .app bundles all silently no-op TCC grants — verified
 * empirically 2026-07-13 during MUSE F018 work.
 *
 * `_trust` is the machine-local trust anchor. Granted FDA once (in
 * System Settings), it can dispatch to trusted target scripts which
 * inherit its TCC identity via execv. Adding a verb requires editing
 * this source, rebuilding, re-signing, re-notarizing. The audit surface
 * for "what background pipelines can this machine's FDA-having process
 * invoke?" IS this source file — no runtime config, no plugin registry.
 * That rebuild friction is a feature, not a bug.
 *
 * USAGE
 * -----
 *   _trust <verb> [args...]
 *
 * BUILD
 * -----
 *   ./build   (see README.md — cc + codesign + xcrun notarytool submit)
 *
 * DESIGN CONTEXT
 * --------------
 * F019 (SYS anchor): Background TCC — _trust launcher (personal) with
 * interactive fallback for others.
 */

#include <unistd.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "_trust: no verb given\n");
        fprintf(stderr, "usage: _trust <verb> [args...]\n");
        fprintf(stderr, "known verbs: muse-sweep\n");
        return 2;
    }

    if (strcmp(argv[1], "muse-sweep") == 0) {
        char *sweep_args[] = {
            "/Users/oblinger/.claude/skills/muse/scripts/muse",
            "ingest",
            "--sweep",
            NULL
        };
        execv(sweep_args[0], sweep_args);
        perror("_trust: execv muse-sweep");
        return 1;
    }

    fprintf(stderr, "_trust: unknown verb '%s'\n", argv[1]);
    fprintf(stderr, "known verbs: muse-sweep\n");
    return 2;
}
