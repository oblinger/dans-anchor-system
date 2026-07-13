# host/

Host-machine artifacts that DAS ships alongside the portable skill/facet/template
content. Everything here is macOS-shaped (or would be linux-shaped on a Linux
port) and lives outside the `skills/` tree because it's not vanilla Python or
Markdown.

## `DAS Trust.app`

An unsigned .app bundle that acts as the **single Full-Disk-Access grant
target** for DAS operations invoked from unprivileged background contexts
(launchd, cron, login items, future scheduled jobs). See the header of
`DAS Trust.app/Contents/MacOS/DAS-Trust` for the full rationale.

**One FDA grant per machine, ever.** Any new background pipeline that needs
TCC-scoped access adds a verb to the `case` block inside `DAS-Trust` and
inherits access via the bundle-id `com.oblinger.das.trust`.

**Grant procedure (once per machine):**

1. System Settings → Privacy & Security → Full Disk Access → **+**
2. Navigate to `.../dans-anchor-system/host/` (`Cmd+Shift+G` in the picker)
3. Select `DAS Trust.app`
4. Toggle the row on

**When you edit `DAS-Trust`** — macOS TCC may consider the bundle
"changed" and require a re-toggle. If a launchd-invoked pipeline stops
finding files it should see, first check the FDA row is still on. Toggling
off/on (or remove + re-add) re-establishes the association.

**Interactive invocation doesn't need this.** Anything a human runs from a
terminal, Claude Code, Obsidian, or Keyboard Maestro inherits FDA from the
launching app — the target skill scripts can be invoked directly. Only
background/scheduled callers route through `DAS Trust.app`.
