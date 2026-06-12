# iOS Development

Reference for iOS-specific development concerns. Read when the current project targets iOS (or includes an iOS component).

# Rules



# Strategies

- **Read before write:** Always read existing code before modifying it. Understand the patterns, naming conventions, and architecture already in place before proposing changes.
- **Build after every change:** Run `swift build` or `xcodebuild` after each edit round. Catch compilation errors immediately, not after five files of changes.
- **Follow the codebase:** Match existing conventions exactly — file organization, naming style, error handling patterns, constraint idioms. New code should look like it was written by the same author as the existing code.
- **Module per feature:** Each feature gets its own directory with focused, single-responsibility files. New modules follow the structure of existing ones (e.g., if Companion/ has `CompanionTracker.swift` + `WindowGeometry.swift`, Glow/ follows the same pattern).
- **One source of truth:** A single observable state object owns all UI-visible state. Managers mutate it; views bind to it. Never duplicate state across multiple objects.
- **Combine for reactivity:** Use Combine publishers (`$property.combineLatest(...)`) to react to state changes. Subscribe in `init`, store in `cancellables`, always `receive(on: DispatchQueue.main)` before UI work.
- **Weak self always:** Use `[weak self]` in every closure that outlives the call site — timers, notification observers, Combine sinks, `DispatchQueue.async` blocks. No exceptions.
- **Generation counters:** For async operations that can be superseded (dictation start/stop, recognition sessions), capture a monotonic counter and bail if stale. Prevents cancelled operations from corrupting newer state.
- **Config-driven behavior:** User-facing settings belong in a config file (YAML), not hardcoded. Use Codable structs with `decodeIfPresent` + sensible defaults so missing fields never crash.
- **Constraint priorities:** Never use `.defaultHigh` (750) or `.required` (1000) on dynamic content dimensions. Dynamic rows, lists, and panels use priority 1 so they clip rather than force the window to grow. The window's `minSize` should be the true minimum — nothing internal should override it.
- **Diagnostic logging:** Each module gets its own `os.Logger` category (e.g., `Log.speech`, `Log.glow`). Log at boundaries: operation start, errors, and completion. Include relevant values with `privacy: .public` for debugging.
- **No fallback logic:** If a dependency or permission is missing, fail with a clear error message. Don't silently degrade to an alternative that masks the real problem.
- **No over-engineering:** Only implement what's directly needed for the current task. Don't add configurability, abstractions, or error handling for hypothetical scenarios. Three similar lines are better than a premature abstraction.
- **Small focused commits:** Commit at natural stopping points — one logical change per commit. Multiple small commits are better than one large one. Commit messages explain the "why."
- **Plan new features:** New features require explicit design and user approval before implementation. Bug fixes and changes that follow established patterns can proceed directly.
- **Recovery over restart:** When a subsystem gets stuck (recognition engine, observer, timer), implement escalating recovery — retry the session first, then recreate the underlying resource, then back off with increasing delays. Always track consecutive failures so recovery can escalate.
- **Permission declarations:** Declare all required permissions and entitlements upfront in Info.plist and .entitlements. Silent failures from missing permissions are the hardest bugs to diagnose — always check and log permission state at startup.
- **Permission redeploy flow:** When deploying a rebuilt binary that requires Accessibility (or other TCC) permissions, follow the Permission Redeploy Flow defined in the Notes section below. Claude builds first, then deletes the old app bundle as the handoff signal. The user handles permissions and launch — Claude never launches the app.


# NOTES

## Permission Redeploy Flow

When deploying a rebuilt macOS binary that requires Accessibility (or other TCC-managed) permissions, the code signature changes and macOS invalidates the old permission grant. This is the coordinated flow between Claude and the user.

**Claude does (in order):**
1. Kill the running app
2. Build the new binary (`swift build`) — do NOT delete the app bundle until the build succeeds
3. Delete the app bundle from /Applications — this is the user's visual signal that a new build is ready
4. Recreate the app bundle, copy the new binary in, and sign it
5. Open System Settings → Privacy & Security → Accessibility (first deploy only — keep the window open for the session)
6. Open /Applications in Finder (first deploy only — keep the window open for the session)
7. Stop. Do NOT message the user or launch the app. The app appearing in /Applications is the signal.

**User does (when they notice the app has reappeared in /Applications):**
1. In the Accessibility list: toggle off the old entry (if present)
2. Click the minus button to remove the old entry
3. Drag the app from the Finder /Applications window into the Accessibility list
4. Toggle the new entry on
5. Launch the app themselves (double-click in Finder)

**Key points:**
- The app must NOT be running when removing the Accessibility entry — that's why step 1 is kill
- Build BEFORE deleting the app bundle — if the build fails, the old app stays runnable
- Deleting and recreating the app bundle (not just overwriting the binary) forces macOS to treat it as a new app in the Accessibility list
- The Settings and Finder windows only need to be opened once per session — after that the user already has them available
- Claude never launches the app — the user launches it after setting permissions, avoiding the race condition where the app starts without Accessibility and keyboard/speech features silently fail
- If the user removes the app from Accessibility while it's still running, macOS may get confused and the app won't reappear in the list. The fix: force-kill the app, delete and recreate the bundle, then re-add

## Permissions and Entitlements

iOS requires explicit declarations for every sensitive capability. Missing one causes silent failures or App Store rejection.

**Info.plist usage descriptions** — every permission needs a user-facing string explaining why. Apple rejects apps with generic descriptions.

| Permission | Info.plist Key | Example Description |
|---|---|---|
| Camera | NSCameraUsageDescription | "Take photos for your profile" |
| Microphone | NSMicrophoneUsageDescription | "Record voice notes" |
| Location (in use) | NSLocationWhenInUseUsageDescription | "Show nearby results" |
| Location (always) | NSLocationAlwaysAndWhenInUseUsageDescription | "Track your run in the background" |
| Photos | NSPhotoLibraryUsageDescription | "Choose images to upload" |
| Contacts | NSContactsUsageDescription | "Find friends on the platform" |
| Bluetooth | NSBluetoothAlwaysUsageDescription | "Connect to your fitness tracker" |
| Face ID | NSFaceIDUsageDescription | "Unlock with Face ID" |
| Local Network | NSLocalNetworkUsageDescription | "Discover devices on your network" |
| Tracking | NSUserTrackingUsageDescription | "Personalize ads across apps" |

**Entitlements** — declared in `.entitlements` file, signed into the binary. Common ones:
- `com.apple.security.app-sandbox` — required for Mac Catalyst and App Store
- `com.apple.developer.associated-domains` — universal links
- `aps-environment` — push notifications (development vs production)
- `com.apple.developer.healthkit` — HealthKit access
- `keychain-access-groups` — shared keychain between apps

**Privacy Manifest** (`PrivacyInfo.xcprivacy`) — required since Spring 2024. Declares:
- APIs used that Apple considers "required reason APIs" (UserDefaults, file timestamp, disk space, etc.)
- Data collected and its purposes
- Tracking domains

## Code Signing

**Development** — automatic signing with a personal team works for simulators and personal devices. For team distribution, use a Development certificate + provisioning profile.

**Distribution** — requires:
1. Distribution certificate (App Store or Ad Hoc)
2. Provisioning profile matching bundle ID + certificate + device list (Ad Hoc) or no device list (App Store)
3. Correct entitlements in the profile

**Common failures:**
- "No signing certificate" — certificate expired or not in keychain
- "Provisioning profile doesn't match" — bundle ID mismatch, or entitlement not enabled in Apple Developer portal
- "Device not registered" — for Ad Hoc, the test device UDID must be in the profile

## Project Structure

**Xcode project** — `.xcodeproj` for simple projects, `.xcworkspace` when using CocoaPods or multiple projects.

**Swift Package Manager** — preferred for dependencies. `Package.swift` at the root or as a local package within the Xcode project.

**Key directories:**
- `Sources/` or `AppName/` — Swift source files
- `Resources/` or `Assets.xcassets` — images, colors, data files
- `Tests/` — unit and UI tests
- `Preview Content/` — SwiftUI preview assets (excluded from release builds)

## Testing

**Unit tests** — `XCTest` framework. Run via `xcodebuild test` or Xcode.

```bash
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 16,OS=latest' \
  -resultBundlePath TestResults
```

**UI tests** — `XCUITest`. Slower, requires simulator. Use sparingly for critical flows.

**Simulator gotchas:**
- No push notifications (use a physical device)
- No camera/microphone (mock these in tests)
- Performance doesn't match device — always profile on hardware
- Keychain behaves differently than on device

## App Store Submission

**Pre-submission checklist:**
- All permission strings are specific and accurate
- Privacy manifest is complete
- No private API usage (Apple scans for this)
- App icons for all required sizes
- Launch screen configured (not a static image for new apps)
- Minimum deployment target matches your intent
- Version and build number incremented
- TestFlight beta tested on real devices

**Common rejection reasons:**
- Vague permission descriptions
- Crashes on launch (test on oldest supported device/OS)
- Incomplete functionality (placeholder screens)
- Links to external payment (for digital goods)
- Missing privacy policy URL

## SwiftUI vs UIKit

**SwiftUI** — preferred for new development. Declarative, preview-friendly, less boilerplate. Limitations: some advanced customizations still require UIKit bridging via `UIViewRepresentable`.

**UIKit** — required for complex custom views, some system integrations, and backward compatibility below iOS 15. Use when SwiftUI doesn't expose the API you need.

**Mixing** — common and supported. SwiftUI views can host UIKit views and vice versa. Don't fight it — use whichever is better for each screen.

## Background Execution

iOS aggressively suspends apps. Background work requires explicit configuration:

- **Background Tasks** (`BGTaskScheduler`) — for periodic work (data sync, cleanup). System decides when to run.
- **Background URL sessions** — for large downloads/uploads that continue after suspension.
- **Location updates** — continuous background location requires `location` background mode and strong justification.
- **Audio/VoIP** — `audio` or `voip` background modes.
- **Push notifications** — silent pushes can wake the app briefly.

**Don't rely on `beginBackgroundTask`** for long work — you get ~30 seconds, then the system kills the task.

## Common Pitfalls

**Main thread** — all UI updates must happen on the main thread. Use `@MainActor` or `DispatchQueue.main.async`. SwiftUI's `@Published` properties in `ObservableObject` must be set on main thread.

**Retain cycles** — use `[weak self]` in closures that capture `self` and outlive the object. Especially common with timers, notification observers, and network callbacks.

**Large assets** — don't bundle large files in the app binary. Use On Demand Resources or download at runtime. App Store has a 200MB cellular download limit.

**Keychain vs UserDefaults** — never store tokens, passwords, or secrets in UserDefaults. Use Keychain Services. UserDefaults is not encrypted.

**Deep links** — test both Universal Links (https://yourdomain.com/path) and Custom URL Schemes (myapp://path). They have different setup requirements and failure modes.
