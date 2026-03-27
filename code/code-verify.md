# Verify

Run the test suite and produce a completion proof. No milestone is done without this report.

## When to Use

After code and tests are written for a milestone. Run to prove the implementation works.

## Workflow

### 1. Run the Test Suite

Execute the project's test runner:
```bash
just test              # snap tests
just test pr           # snap + pr tests
```

Run the appropriate category for the milestone scope.

### 2. Produce Completion Proof

MUST produce this report by RUNNING the test suite — not by belief:

```
## Test Report
Tests written this session: N
Tests passing: N
Tests failing: N (list each with file:line)
Kitchen sink scaffold: extended / unchanged
Gaps remaining: N (listed below)
```

No "done" without this report.

### 3. Red-Green Verification (Levels 6+)

For adversarial test levels, additionally mutate production code to confirm tests catch breakage. Undo after verifying the test fails as expected.

### 4. Handle Failures

If tests fail:
- Diagnose the root cause (do not apply blind fixes)
- Fix the code or the test as appropriate
- Re-run and produce a new completion proof
- If 3 fix attempts fail, escalate: "Is this code testable? Should we refactor?"

### 5. Update Roadmap

Mark the milestone as verified in the roadmap. If gaps remain, note them for the next iteration.
