---
description: macOS app development — code signing, TCC permissions, sandboxing, build conventions
trait: Code
applies-when: anchor builds a macOS application (`.app` bundle) — Swift, Objective-C, Catalyst, Electron-on-macOS, or any other framework producing a macOS app
set-id: MA
---

# Code/mac-app — macOS app coding decisions

Decisions that apply when an anchor builds a macOS app — a `.app` bundle deployed beyond throwaway debugging. Covers code signing, TCC (Transparency, Consent, Control) permissions, sandboxing, and the build conventions that interact with those systems.

The single load-bearing rule is **D-MA01** — every other decision in this set assumes proper signing. Without it, the permission system fights you on every rebuild.


## Signing


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
