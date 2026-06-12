# Fix: Show/Hide Dot Files in Finder

Toggle visibility of hidden files (dotfiles) in Finder.

## Runbook

### To show dot files

```bash
defaults write com.apple.finder AppleShowAllFiles TRUE
killall Finder
```

### To hide dot files again

```bash
defaults write com.apple.finder AppleShowAllFiles FALSE
killall Finder
```

Finder restarts automatically after `killall`. The change takes effect immediately.
