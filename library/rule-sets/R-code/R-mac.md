---
description: macOS app development — code signing, TCC permissions, sandboxing, build conventions
trait: Code
applies-when: anchor builds a macOS application (`.app` bundle) — Swift, Objective-C, Catalyst, Electron-on-macOS, or any other framework producing a macOS app
set-id: MA
---

# R-mac — macOS app rules

Decisions that apply when an anchor builds a macOS app — a `.app` bundle deployed beyond throwaway debugging. Covers code signing, TCC (Transparency, Consent, Control) permissions, sandboxing, and the build conventions that interact with those systems.

The two load-bearing rules are **D-MA01** (stable code identity) and **D-MA02** (TCC will actually trust that identity) — every other decision in this set assumes both. Without them, the permission system fights you on every rebuild.


## App Permission Handling (Avoids need to re-granting permissions during development)


### D-MA01 — Never use ad-hoc code signing (checked)

**Decision:** Never sign a macOS app with ad-hoc code signing (`codesign -s -` or `codesign --sign -`). Always sign with a proper Apple Developer signing identity (`Developer ID Application: <Name> (<TEAM>)` or `Apple Development: <Name> (<TEAM>)`), issued from the Apple Developer Program.

**Why:** Ad-hoc signed apps have **no stable code identity** — every rebuild gets a fresh fingerprint, so macOS's permission system (TCC) treats every rebuild as a new app. Every Accessibility / Microphone / Camera / Screen Recording / Full Disk Access grant has to be re-approved by the user after every rebuild — typically by walking to System Settings, deleting the old entry, and re-adding the new one. This is not a "minor friction" cost; it makes any app that requests TCC permissions effectively unusable for daily development.

Properly signed apps keep a **stable code identity** across rebuilds. macOS remembers the permission grant by that identity; rebuilds inherit the existing grants. Permissions ask once, stay forever.

The cost of obtaining an Apple Developer Program membership ($99/year as of 2026) is far less than the cost of re-clicking permission dialogs across thousands of dev rebuilds.

**Check pattern:** Grep the anchor's build scripts and CI config for the ad-hoc signing form:

```bash
codesign -s -                      # ad-hoc, short flag form
codesign --sign -                  # ad-hoc, long flag form
codesign --force --sign -          # forced ad-hoc
CODE_SIGN_IDENTITY = "-"           # Xcode build setting form
CODE_SIGN_IDENTITY=-
```

Any match is a violation. Replace with `Developer ID Application: <Name> (<TEAM>)` or `Apple Development: <Name> (<TEAM>)` referenced from the developer's keychain.

**Exceptions (none currently allowed):** This decision is `(checked)` not `(tracked)` — there should be zero hits. If a legitimate exception ever arises (e.g., a one-off CI binary that explicitly will never request a TCC permission and has no persistent identity needs), promote the decision to `(tracked)` and document the exception in an EX-table.


### D-MA02 — Never enable `get-task-allow` in the default build (checked)

**Decision:** A macOS app's default build must NOT carry the `com.apple.security.get-task-allow` entitlement set to `<true/>`. The default-build entitlements file either omits the key entirely or sets it to `<false/>`. When debugger attach is genuinely needed (lldb attach, runtime view-hierarchy diagnostics, process introspection), create a **separate build target / recipe** — e.g., `just build-debug` alongside `just build` — that points at a different entitlements file with `get-task-allow=true`. The two targets coexist; you opt into the debuggable one only when you actually need it.

**Why:** TCC refuses to persist permission grants for debuggable binaries. A binary with `get-task-allow=true` could have arbitrary code injected after the grant is given, so the security model treats it as "this app's identity is meaningfully forgeable." Every rebuild of a `get-task-allow=true` binary re-prompts the user to grant Accessibility / Screen Recording / Input Monitoring / etc. — **even when D-MA01 is satisfied and the signing identity is otherwise stable**. The two decisions compose: D-MA01 establishes stable code identity, D-MA02 makes TCC actually willing to trust it.

Splitting into two build recipes gives you both: the default (`just build`) ships TCC-stable and skips the prompt-every-rebuild cycle; the opt-in (`just build-debug`) supports lldb attach for the rare sessions that need it. Daily dev runs against the stable build; you flip to debug only when actively introspecting the running process.

**Check pattern:** Inspect each entitlements file referenced by the default build target for `get-task-allow=true`:

```bash
# In each *.entitlements file the default build references:
grep -A1 'get-task-allow' YourApp.entitlements
# A "<true/>" on the line below is a violation.
```

Also check installed app bundles built by the default recipe:

```bash
codesign -d --entitlements - /Applications/YourApp.app 2>&1 | grep -A1 get-task-allow
```

Any default-build path that ends with `get-task-allow=true` is a violation. The fix is one of:
1. Flip the value to `<false/>` (or remove the key entirely)
2. If lldb attach is genuinely needed: split into separate `build` (TCC-stable) and `build-debug` (debuggable) recipes, each pointing at a different entitlements file
3. Two different bundle IDs (e.g., `com.example.app` and `com.example.app.debug`) if you need both granted side-by-side rather than swapping

**Exceptions:** `(checked)` — there should be zero hits in default-build paths. An explicit `build-debug` / `build-with-lldb` recipe pointing at a `<true/>` entitlements file is allowed and expected; that separation is the discipline this decision encodes, not a violation. Hits flagged by the check pattern are only violations if they appear in the default build's entitlements file.


### D-MA03 — Self-signed dev cert: long-lived, generated once, never regenerated (checked)

**Decision:** When the signing identity is a **self-signed** certificate (the path for projects without paid Apple Developer Program membership, or for additional dev-only identities), that cert must:
1. Be generated with a validity period of **≥100 years** (e.g., `openssl req ... -days 36500`).
2. Be persisted in the user's login keychain and treated as a one-shot install.
3. Be generated by an **idempotent** setup script — re-running the script reuses the existing cert, never regenerates one.

**Why:** TCC keys the designated requirement on the cert's **leaf hash** for self-signed identities (`certificate leaf = H"ab2e..."`). Any regenerated cert — even with the same Common Name — has a new leaf hash → new DR → all TCC grants invalidated and re-prompted. Two repeated failure modes this decision prevents:

1. **Cert expiration** — finite validity means a "permissions decay" effect on a calendar schedule. A 100-year cert removes the calendar dimension entirely.
2. **Accidental regeneration** — running the setup script on a fresh checkout, a new machine, or as part of an over-eager "reset dev env" recipe creates a new cert despite the old one being valid. An idempotent script removes this dimension.

**Check pattern:**

Validity:

```bash
security find-certificate -c "YourApp Dev" -p | openssl x509 -noout -enddate
# Date must be ≥10 years in the future. Refuse anything sooner.
```

Idempotency of setup script:

```bash
grep -nE 'security find-certificate|security delete-certificate|openssl req' scripts/setup-codesign-cert.sh
# The script must short-circuit if the named cert already exists. Unconditional generation is a violation.
```

**Exceptions:** `(checked)` — none. A long-lived self-signed cert costs nothing; cert churn costs repeated re-prompts that this decision exists to prevent.


### D-MA04 — Strip the quarantine xattr on every install / deploy (checked)

**Decision:** Every recipe that copies a `.app` bundle into a run location (local install, redeploy, rsync-to-remote, scp, CI deploy) must end with:

```bash
xattr -dr com.apple.quarantine /path/to/YourApp.app
```

No exceptions, including for bundles you built yourself a moment ago.

**Why:** macOS attaches `com.apple.quarantine` to files arriving via download, AirDrop, certain rsync flag combinations, and other "from the internet" code paths. Its presence makes Gatekeeper re-validate the bundle on next launch, which can silently disturb TCC state — typically by forcing first-launch flow as if the app were new. Failure modes by workflow:

- **Pure local dev** rarely sees this (build → `/Applications/` stays quarantine-free).
- **Remote-test workflows** (rsync from dev Mac to a test Mac) reattach the xattr on every push → re-prompt every push.
- **Mixed workflows** are the worst: the app behaves fine for weeks of local builds, then mysteriously re-prompts after the first remote sync, with no obvious cause.

A one-line strip at install time makes the install location quarantine-free regardless of how the bundle arrived.

**Check pattern:**

Installed bundle:

```bash
xattr -lr /Applications/YourApp.app | grep com.apple.quarantine
# Must produce no output.
```

Install/deploy recipes:

```bash
grep -nE 'xattr.*quarantine' justfile scripts/
# Every recipe that copies the bundle to a run location must call `xattr -dr com.apple.quarantine` on the destination.
```

**Exceptions:** `(checked)` — none. One line; no downside for self-controlled binaries; asymmetric cost of forgetting it.


### D-MA05 — All codesign invocations produce an identical designated requirement per bundle ID (checked)

**Decision:** Every `codesign` invocation in the project's build, install, deploy, refresh, and helper-signing recipes — including every fallback branch — must produce a **byte-for-byte identical designated requirement (DR)** for a given bundle ID. The string output of `codesign -d -r-` must be the same regardless of which recipe produced the installed bundle.

In practice, every codesign call for a given bundle ID uses:
- the same **signing identity** (never a silent fallback to `--sign -`)
- the same **`--identifier`** value
- the same **`--options`** flags (especially `runtime`)
- the same **entitlements file** (or no entitlements file — but consistent)

The D-MA02 `build` / `build-debug` split is **not** an exception — it intentionally produces two distinct bundles, each DR-deterministic within itself.

**Why:** TCC stores the grant against whatever DR it observed at grant time. If any later build presents a different DR, TCC sees a new app and re-prompts. This is the most insidious cause of "permissions sometimes work and sometimes don't" — the build is non-deterministic at the DR level, you don't notice until an unlucky branch fires, and the symptom is indistinguishable from a flaky OS. Common offenders:

- **Adhoc-fallback branches** ("if the stable cert isn't found, fall back to `codesign -s -`"). The first time the fallback fires, the DR becomes `Signature=adhoc` and every stable-cert grant is orphaned. D-MA01 forbids the fallback existing at all; D-MA05 catches the case where someone "kept the fallback for robustness."
- **Refresh / redeploy / forge** paths that re-sign with slightly different arguments than the original build path.
- **Helper-app or framework signing** that uses different flags than the parent app's signing call.
- **Hardened-runtime drift** — one recipe adds `--options runtime`, another doesn't.

**Check pattern:**

The authoritative check — run after every recipe that touches the install; all outputs must match exactly:

```bash
just build       && codesign -d -r- /Applications/YourApp.app 2>&1 > /tmp/dr-build.txt
just redeploy    && codesign -d -r- /Applications/YourApp.app 2>&1 > /tmp/dr-redeploy.txt
just refresh     && codesign -d -r- /Applications/YourApp.app 2>&1 > /tmp/dr-refresh.txt
diff /tmp/dr-build.txt /tmp/dr-redeploy.txt        # must be empty
diff /tmp/dr-redeploy.txt /tmp/dr-refresh.txt      # must be empty
```

Also grep for hidden adhoc-fallback branches that D-MA01's static check might miss inside conditional logic:

```bash
grep -nE 'codesign.*(--sign|^-s)\s+-($|\s)' justfile scripts/
# Any match — even inside an `if` branch that "shouldn't fire" — is a violation.
```

**Exceptions:** `(checked)` — none. Any intentional DR variation should be modeled as a separate bundle ID (the D-MA02 split is the template), never as same-bundle variants.
