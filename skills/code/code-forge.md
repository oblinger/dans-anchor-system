# Forge

Full rebuild, teardown, and restart cycle. The user should be testing new features within seconds of invoking forge.

## Workflow

**Every forge follows this sequence:**

1. **Check dependencies** — Scan for updated dependencies (Cargo.lock, package-lock.json, Podfile.lock, etc.). If any dependency has changed since last build, rebuild those dependencies first.
2. **Rebuild** — Recompile all changed source code and dependencies. Do this while the old app is still running — the user keeps working until the new build is ready.
3. **Terminate** — Kill the running instance. Only after the build succeeds. This minimizes downtime.
4. **Restart** — Launch the new build and restore operational state (permissions, services, connections).

**The user should be testing within seconds of invoking forge.** No manual steps between forge and first interaction.

## Principles
- **Always terminate, always rebuild** — Forge means "tear it all down and rebuild from scratch." Don't skip steps. Don't assume nothing changed. The user invoked forge because they want certainty.
- **Check all dependencies** — Before compiling, check if any dependency lockfiles have changed. Rebuild dependency trees as needed. This includes: Cargo dependencies, npm packages, Swift packages, Python requirements, submodules, and any local workspace crates or packages.
- **Seamless handoff** — Tear down the old instance, start the new one, and restore operational state so the user can immediately test. No manual steps.
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
