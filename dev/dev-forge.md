# Forge

Full rebuild, teardown, and restart cycle. The user should be testing new features within seconds of invoking forge.

## Principles
- **Terminate first** — Ensure the previous running instance is fully terminated before starting the new one. No port conflicts, no stale processes, no ambiguity about which version is running.
- **Skip build if unchanged** — Only rebuild if source code has actually been modified. If no source files changed, skip the build step entirely and just execute/restart the existing artifacts. The goal is fast iteration, not redundant builds.
- **Automatic verification** — When building, run fast checks (tests, lint, type-check) before deploying. Fail early, not after teardown.
- **Seamless handoff** — Tear down the old instance, start the new one, and restore operational state (permissions, services, connections) so the user can immediately test. No manual steps between forge and first interaction.
- **Logic lives in the justfile** — Each project defines a `just forge` recipe that automates the full cycle. The skill invokes the recipe; the recipe owns the details. If a step is missing, fix the recipe rather than doing manual steps alongside it.
- **Forge when it matters** — After making changes, decide whether to forge immediately or batch with more work. Forge now when the change is behavioral and the user needs to verify it works (e.g., fixing a startup bug, changing interaction flow). Batch when the change is small, mechanical, or part of a larger feature still being built (e.g., adding a helper function, renaming a variable). The goal is to avoid unnecessary rebuild cycles without letting untested behavioral changes pile up.

## macOS Apps with Permissions
Apps that require accessibility or other macOS permissions need careful choreography between the agent and user during forge. Ad-hoc code signing is unreliable — always use proper app signing.

### The .app bundle
The `.app` in `/Applications` should contain symlinks back to the repo's build artifacts, not copies. This gives it a stable identity for macOS permission grants while picking up new binaries on every rebuild.

### When permissions reset is needed
macOS tracks permissions by binary hash. The permission dance is only needed when the **compiled binary changes** — i.e., when Rust, Swift, or other compiled source files were modified. Frontend-only changes (TypeScript, CSS, HTML, assets) don't recompile the binary, so the hash stays the same and permissions survive.

**Before deleting the .app**, check whether any compiled source files changed in this forge cycle. If only frontend/asset files changed, skip the deletion — the app will pick up the new assets without losing permissions.

### Forge handoff protocol (when binary changed)
The agent and user each have a defined role in the permission dance. The app terminating on screen is the **only** signal — do NOT send chat messages warning the user about the dance or telling them what to do. The user already has both windows open and knows the drill.

**Agent does (in this order):**
1. Build everything while the previous app is still running
2. Run tests and verification
3. Only after the build succeeds: kill the running app and delete the `.app` from `/Applications`
4. Recreate the `.app` bundle (copy/symlink new binary, re-sign)
5. Say nothing. The user sees the app disappear and takes over.

The build must complete **before** killing the app — this eliminates the race condition. The moment the user sees the app vanish, the new `.app` is already in `/Applications` ready to be registered.

**User sees the app terminate and does:**
1. In the Accessibility list, toggle the old entry off and delete it
2. In Finder, double-click the `.app` to re-register it
3. In the Accessibility list, toggle the new entry on

### Forge without permission reset (frontend-only changes)
When no compiled source files changed, skip the app deletion entirely. Just rebuild and restart — the existing permissions remain valid.
