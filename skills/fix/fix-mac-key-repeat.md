# Fix: Fast Key Repeat Rate

macOS defaults to slow key repeat with press-and-hold for accents. This fix sets the fastest repeat rate and disables press-and-hold.

## Runbook

### 1. Disable press-and-hold (enables key repeat)

```bash
defaults write -g ApplePressAndHoldEnabled -bool false
```

### 2. Set fastest key repeat

```bash
defaults write NSGlobalDomain KeyRepeat -int 0
```

### 3. Report

---

**>>> RESTART AFFECTED APPS (or log out and back in) FOR CHANGES TO TAKE EFFECT <<<**

**>>> RESTART AFFECTED APPS (or log out and back in) FOR CHANGES TO TAKE EFFECT <<<**

**>>> RESTART AFFECTED APPS (or log out and back in) FOR CHANGES TO TAKE EFFECT <<<**

---

Already-running apps won't pick up the change until restarted.
