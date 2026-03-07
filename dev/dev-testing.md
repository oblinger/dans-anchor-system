# Testing

## Principles
- **Default test command must be safe.** No side effects, no system state changes. Ever.
- **Gate dangerous tests behind a feature flag.** Only run with explicit user confirmation.
- **Mock at the boundary, not everywhere.** Use trait-based backends so core logic is fully testable without mocks leaking into every function.




## Live Tests

Tests that affect real system state — switching tmux clients, creating sessions, writing to filesystem, hitting network endpoints.

### Convention

```rust
#[test]
#[cfg(feature = "live")]
fn test_that_switches_tmux_client() { ... }
```

```toml
[features]
live = []  # Tests that affect real system state
```

### Rules

- Never run without user confirmation — the user must explicitly say "do live testing"
- Document what each live test modifies (comment above the test)
- Prefer mocks for unit tests — only use live when verifying real integration

### Running

```
cargo test --features live
```
