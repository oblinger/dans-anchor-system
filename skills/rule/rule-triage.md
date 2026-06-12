# Triage — Adversarial Re-evaluation of Exceptions

Re-evaluate existing exceptions with skepticism. The previous assessment was probably too generous — find what it missed, challenge every grade, and demand better alternatives.

**MANDATORY: When done, call `stat add` with "Review" status and results, then add an H2 entry with grade changes and findings to the Now file. The user watches the Now file — if you don't post, they won't know what happened.**

## When to Use

When you suspect the original check was sloppy, grades are too lenient, alternatives are lazy ("None" when one exists), or violations were missed entirely. This is the quality gate on the quality gate.

## Adversarial Stance

Retriage operates with deliberate distrust:

1. **Challenge every grade** — Is this really an A? Prove it. Show why no alternative exists. "None" is suspicious until confirmed.
2. **Challenge every "None" Alternative** — Search harder. Look at how other projects solve this. Consider restructuring, not just local fixes. The original agent may have given up too easily.
3. **Challenge coverage** — Re-scan the code looking for violations the original check missed. Attention fatigue makes later files get less scrutiny.
4. **Challenge Gain/Loss ordering** — Does the ordering actually match the analysis? Or did the agent just mirror the existing grade without thinking?

The attitude: **"The previous assessment was probably too generous. Find what it missed."**

## Exception Description Format

Each exception's Description cell has five parts separated by `<br>`:

1. **Summary** (no label) — What the exception is. Short phrase.
2. **Purpose:** — What it's trying to accomplish.
3. **Keep:** — Why this exception should stay as-is.
4. **Alternative:** — Concrete spec for what you'd do instead. "None" only if genuinely no alternative exists.
5. **Gain/Loss** or **Loss/Gain** — Two labeled parts on one line. Order encodes net assessment.

### Grade scale

Full scale from best to worst: A, B+, B, B-, C+, C, C-, D+, D, D-, F

### Gain/Loss ordering rule

- **Gain:** first → net positive, switching is worth it (D/F grades)
- **Loss:** first → net negative, keeping is better (A/B grades)
- C grades can go either way
- The grade must be derivable from the ordering — if they disagree, fix one or the other

### What to omit

Do not include gains or losses that are obvious and universal:
- "Takes time to implement" — always true
- Use **—** for empty gain or loss when nothing meaningful beyond the obvious

## Workflow

### 1. Load the Rules File

Read the project's rules file using `cab-config get rules`.

### 2. Re-scan the Code

Don't just read the exception table — go back to the source code. For each exception:
- Read the actual code at the Location
- Verify the description is accurate
- Look for context the original check may have missed

### 3. Re-evaluate Each Exception

**a. Read the code.** Don't trust the description.

**b. Challenge the five parts:**
- Is the Purpose still accurate?
- Is the Keep argument actually compelling, or is it hand-waving?
- Is the Alternative truly the best option? Or is there a better approach the original agent didn't consider?
- Does the Gain/Loss ordering match reality?

**c. Re-assign the grade** if warranted. Document why it changed.

**d. Consistency check:** Grade must match Gain/Loss ordering.

### 4. Find Missing Violations

Re-scan source files that were checked before, looking for:
- Violations the original check missed (attention fatigue, unfamiliar patterns)
- New violations introduced since the last check
- Patterns that look fine individually but violate rules when seen in aggregate

### 5. Catch Stale Exceptions

Flag exceptions where:
- The code was refactored and the exception no longer applies
- The EX tag exists but the pattern it excuses is gone
- The architecture changed enough to invalidate the justification

### 6. Post to Now

Post results summarizing:
- Grade changes (upgraded or downgraded) with reasoning
- New violations found that the original check missed
- Stale exceptions to remove
- Exceptions with improved Alternatives

```bash
stat add --status "Review" --ref "[[DMUX Rules]]" "Retriage: 4 grade changes, 2 missed violations, 1 stale"
```
