# RULESET R-ios
include::
description:: iOS / Apple-platform development guardrails (F237, user-directed 2026-07-13) — ad-hoc code signing is forbidden (DENY at `tool:pre:Bash` and `tool:pre:Edit`; sign with the user's Apple Developer account), and GUI-affecting test runs are steered to a bridge agent on a remote machine. Rides the anchor base; every rule self-gates on Xcode tooling evidence (the command or file itself), so non-Apple work never pays for it.

> [!info] Provenance
> Born from live pain: an app built with ad-hoc signing gets a fresh code-signing identity every rebuild, so macOS/iOS TCC permission grants (Accessibility, Screen Recording, Automation, …) silently reset — "just so buggy, just not worth it." The user has a real Apple Developer account; builds sign with it. Detection-based (not per-anchor declaration): the *project/tooling* is the evidence, so the rules fire correctly on any machine without machine-conditional ruleset inheritance.

### RULE R-ios-01 — ad-hoc code signing is forbidden in build commands (when:: tool:pre:Bash)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    import re
    # Self-gate: only Apple signing/build tooling — never prose or other builds.
    if not re.search(r"\b(xcodebuild|codesign|xcrun)\b", cmd):
        return []
    adhoc = (
        re.search(r"""CODE_SIGN_IDENTITY\s*=\s*["']?-["']?(\s|$)""", cmd)
        or re.search(r"\bcodesign\b[^\n;|&]*\s(?:-s|--sign)\s+(?:-|'-'|\"-\")(\s|$)", cmd)
        or re.search(r"CODE_SIGNING_(?:REQUIRED|ALLOWED)\s*=\s*NO\b", cmd)
    )
    if not adhoc:
        return []
    return ["DENY: ad-hoc code signing is forbidden (R-ios-01) — every rebuild mints a new "
            "signing identity, so TCC permission grants (Accessibility, Screen Recording, "
            "Automation) silently reset; known-buggy from experience. Sign with the user's "
            "Apple Developer account instead: set DEVELOPMENT_TEAM to the real team and use "
            "an Apple Development certificate (`xcodebuild ... DEVELOPMENT_TEAM=<team> "
            "CODE_SIGN_STYLE=Automatic`)."]
```

Catches `CODE_SIGN_IDENTITY=-` (the ad-hoc identity), `codesign -s -` / `--sign -`, and the disable-signing settings (`CODE_SIGNING_REQUIRED=NO` / `CODE_SIGNING_ALLOWED=NO`) — the same failure class: the product runs without a stable identity.

**Why:** ad-hoc-signed builds lose their TCC grants on every rebuild — the permission dialogs come back, launchd/Automation hooks break, and debugging the resulting flakiness costs far more than wiring the real certificate once.

### RULE R-ios-02 — ad-hoc signing settings can't enter project files (when:: tool:pre:Edit)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    target = getattr(ev, "target", None) if ev else None
    if not target:
        return []
    from pathlib import Path
    name = Path(target).name
    if not (name.endswith(".pbxproj") or name.endswith(".xcconfig")):
        return []
    inp = getattr(ev, "input", None) or {}
    new = inp.get("new_string") or ""
    import re
    adhoc = (
        re.search(r"""CODE_SIGN_IDENTITY\s*=\s*["']?-["']?\s*;?\s*$""", new, re.M)
        or re.search(r"CODE_SIGNING_(?:REQUIRED|ALLOWED)\s*=\s*NO\b", new)
    )
    if not adhoc:
        return []
    return ["DENY: this edit writes an ad-hoc signing setting into a project file "
            "(R-ios-02) — same failure as R-ios-01 at the config layer. Set "
            "DEVELOPMENT_TEAM to the user's Apple Developer team with "
            "CODE_SIGN_STYLE = Automatic instead."]
```

The config-layer sibling of rule 01 — guarding the command alone just teaches the failure mode to hide in `project.pbxproj` (the R-pathguard-03 lesson).

**Why:** a setting persisted in the project file re-applies the ad-hoc identity on every future build, including ones launched from Xcode where no warden hook runs.

### RULE R-ios-03 — GUI-affecting test runs favor a bridge agent on a remote machine (when:: tool:pre:Bash)

```python
def body(ctx):
    ev = getattr(ctx, "event", None)
    inp = getattr(ev, "input", None) or {}
    cmd = inp.get("command") or ""
    import re
    gui_test = (
        re.search(r"\bxcodebuild\b[^\n;|&]*\btest(?:-without-building)?\b", cmd)
        or re.search(r"\bxcrun\s+simctl\b[^\n;|&]*\b(boot|launch|ui)\b", cmd)
        or re.search(r"\bXCUITest\b", cmd)
    )
    if not gui_test:
        return []
    return ["GUI-affecting test run (R-ios-03): simulator boots and UI automation seize the "
            "local screen and focus. Favor dispatching this to a Claude bridge agent on a "
            "remote test machine via the /bridge skill; run locally only when the user "
            "expects the takeover."]
```

Advisory (steer, not DENY) — sometimes local is right (user watching, no remote available); the reminder makes remote-first the default posture.

**Why:** a locally-running simulator/UI test steals the user's machine mid-session; the bridge control plane exists exactly so long-running or screen-seizing work happens on hardware the user isn't sitting at.
