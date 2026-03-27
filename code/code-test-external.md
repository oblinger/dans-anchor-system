# External Dependency Testing — Reference

Loaded by `/code test` when dealing with OS APIs, network, hardware, or other external interfaces.


## Why This Matters

Code that interfaces with the OS or external services is where **95% of painful bugs** come from. Not the logic bugs (fixed in seconds) but the integration bugs (days to diagnose).

Examples from real projects:
- Apple's dictation API behaving differently across OS versions
- Accessibility permissions silently failing
- tmux sessions that may or may not exist
- Speech recognition with timing-dependent behavior
- Window focus changes during test execution


## Strategy: Isolate and Pound

### Step 1: Isolate

Extract the external interface into a thin wrapper. The wrapper does ONLY the external call — no business logic. Test the wrapper in isolation.

```
Production code → Wrapper → External API
                     ↑
              Test this boundary
```

### Step 2: Pound

Run many variations against the isolated interface:
- What happens when it's slow? (Add artificial delays)
- When it returns unexpected data? (Fuzz the inputs)
- When permissions are denied? (Test with restricted privileges)
- When it's called concurrently? (Multiple threads hitting it)
- When the resource doesn't exist? (Missing file, dead process, no network)

### Step 3: Tag Appropriately

| Scenario | Category | Tag |
|----------|----------|-----|
| Fast, deterministic external call | pr | |
| Slow or timing-dependent | demand | probe |
| Grabs mouse, pops windows, plays audio | witness | |
| Network-dependent | demand | probe |
| May show permission dialog | witness | probe |


## Stochastic Behavior

Some external interfaces are inherently non-deterministic:
- Speech recognition accuracy varies
- Window positioning depends on display configuration
- File system timing varies under load
- Network latency varies

For these, tests should:
- Assert within **tolerances**, not exact values
- Run **multiple iterations** and check statistical properties
- Have a **retry budget** before failing (tag as `probe`)
- Log the actual values on failure for debugging


## Recording / Replay

For expensive or flaky external calls, consider recording real responses once and replaying in tests:
- Capture actual API responses to a file
- Test against the recording instead of the live API
- Re-record periodically to catch API changes
- Category: `snap` (replay is fast and deterministic)

This avoids both flakiness and the need for the external system to be available during testing.
