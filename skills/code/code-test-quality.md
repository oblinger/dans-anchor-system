# Test Quality — Reference

Loaded by `/code test review` or when writing tests and self-checking.


## Anti-Patterns

### 1. Testing Mock Behavior Instead of Real Behavior

**Bad:** Test verifies `mock.send_text` was called with "hello"
**Good:** Test verifies the target tmux pane actually contains "hello"

If the test only proves the mock was called, it doesn't prove the system works. A mock can be called correctly and the system can still fail. Test outcomes, not intermediate calls.

**Gate check:** "If I replaced the mock with the real implementation, would this test still be meaningful?"

### 2. Test-Only Methods in Production Code

**Bad:** Adding `_get_internal_state_for_testing()` to a production class
**Good:** Refactoring so the state is observable through the public API

Test hooks in production code are tech debt that compounds. If you can't test it through the public interface, the design needs to change — propose refactoring to the user.

**Gate check:** "Would this method exist if there were no tests?"

### 3. Assertions That Always Pass

**Bad:** `assert result is not None` — passes even when result is completely wrong
**Good:** `assert result.command_name == "grep"` — fails if the wrong command was matched

Weak assertions give false confidence. Every assertion should be **mutation-resistant**: if you changed the implementation to return a different value, the test should fail.

**Gate check:** "If I changed the function to return a hardcoded wrong value, would this test catch it?"

### 4. Incomplete Mocks Hiding Assumptions

**Bad:** Mock that always returns success — hides the assumption that the real system always succeeds
**Good:** Mock that returns realistic responses including errors, timeouts, partial results

**Gate check:** "Does my mock represent how the real system actually behaves, including failure modes?"

### 5. Integration Tests as Afterthought

Building unit tests for everything and then bolting on a few integration tests at the end. The integration tests should come FIRST (kitchen sink), unit tests only for isolated complex logic.


## Mutation-Resistant Assertions

A test is mutation-resistant if changing the production code's logic would cause the test to fail. Rules:

- Assert **specific values**, not types or existence
- Assert **multiple properties** of the result, not just one
- Assert **relationships** between inputs and outputs
- For collections: assert contents AND order (if order matters)
- For state changes: assert both the new state AND that the old state is gone


## Test Quality Checklist

Run this after writing a batch of tests:

- [ ] Every test has at least one assertion checking a specific value
- [ ] No test-only methods were added to production code
- [ ] Mocks (if any) include failure scenarios, not just success
- [ ] Integration tests use the kitchen sink, not toy data
- [ ] Each test comment explains WHAT it verifies and WHY it matters
- [ ] Tests are tagged with the correct category (snap/pr/demand/witness)
- [ ] Test module doc is updated to reflect what was built
