---
description: >
  Drive a native macOS app via click/type/screenshot to reproduce bugs,
  verify behavior, and debug the UI. Use when user says: "mac gui",
  "debug the app", "eyeball it", "run it and see what happens",
  "test the UI", "click through", or references visual/UI issues
  (modal, button, screen, layout, window) in a Mac app.
---

# Mac GUI — Drive Native Mac Apps for Debugging

**This is a tool, not a workflow.** It gives an agent the ability to see and
control a running Mac app. Other skills (bugfix, spike, forge, test) may call
on this when they need to reproduce or verify through the actual UI.

## When to use

- Visual / layout bugs ("modal is clipping", "button is off-screen")
- Reproducing a bug that only manifests through interaction
- Verifying a fix end-to-end by driving the real app
- Exploring app behavior no automated test covers
- Any case where you need to see what the user sees

## How to do it

### 1. Enable Computer Use (once per machine)

```
/computer-use on
```

First run, macOS prompts for:
- **Accessibility** — allows clicks, keystrokes, scrolls
- **Screen Recording** — allows screenshots / screen reads

If already enabled, skip.

### 2. Core loop

1. **Launch** the app under test (`open -a "AppName"` or via Finder)
2. **Screenshot** to confirm starting state
3. **Act** — click, type, scroll to reproduce or exercise behavior
4. **Screenshot** after each meaningful interaction
5. **Read** the accessibility tree if pixel-level diagnosis is insufficient
6. **Report** findings back to whoever invoked this skill

### 3. Safety rules

- **View-only zones:** browsers with sessions, banking apps, trading platforms, password managers — never drive these
- **Destructive actions:** confirm with the user before delete/submit/send/pay
- **Pause if confused:** if the UI state doesn't match expectations, screenshot
  and ask — do not keep clicking blindly
- **Screenshots:** save to `/tmp/mac-gui-<timestamp>/`; don't leave them lying
  around after the session

## Fallback tools

Built-in Computer Use is enough for ~95% of debugging. Reach for these only
when you hit a specific limitation:

| Tool | Adds | Use when |
|------|------|----------|
| **[Peekaboo](https://github.com/steipete/Peekaboo)** | Visual Q&A via local model | Need "what's wrong with this screen" semantic analysis |
| **[macos-ui-automation MCP](https://playbooks.com/mcp/mb-dev-macos-ui-automation)** | Accessibility tree + JSONPath selectors | Need scripts that don't break on layout shifts |
| **[Desktop Pilot MCP](https://glama.ai/mcp/servers/VersoXBT/desktop-pilot-mcp)** | AX API + AppleScript + CGEvent, no vision | Fastest, most precise; heavy scripting |
| **[automation-mcp](https://github.com/ashwwwin/automation-mcp)** | Full mouse/keyboard/window primitives | Custom automation kit |

Install a fallback only when the built-in can't do the job.

## What this skill does NOT do

- **Deciding which app to test** — that's the parent skill's call
- **Writing the fix** — that's `/code bugfix` or similar
- **Long-running test suites** — use a test framework, not Computer Use
- **Web / browser automation** — use the Chrome MCP skill instead

## Integration

When called from other skills:

- `/code bugfix` — reproduce bug in the real app before patching
- `/code spike` — drive the UI to probe a hypothesis
- `/code forge` — verify golden-path flow after rebuild+restart
- `/code test` — run scripted UI scenarios

Return findings in a form the caller can act on:
1. Reproduced? yes/no
2. Observed behavior (with screenshot paths)
3. Expected behavior (what should have happened)
4. Any hypotheses formed during exploration
