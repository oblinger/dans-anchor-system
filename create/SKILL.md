---
name: create
description: >
  Create a new thing — anchor, feature, work product, spec, rule.
  Use when the user says: "create a new", "set up", "start a new", "new project",
  "new feature", "new wp", "new rule".
  Requires an argument: /create anchor, /create feature, /create wp, /create spec, /create rule.
tools: Read, Write, Edit, Bash, Glob, Grep
user_invocable: true
---

# Create

Create a new thing. Requires an argument specifying what to create.

| Usage | Delegates to | Description |
|-------|-------------|-------------|
| `/create anchor` | `/cab create` | New anchor — folder structure, config, dispatch tables |
| `/create feature` | `/code feature` | New feature design doc in Features folder |
| `/create wp` | `/cab wp` | New dated work product folder |
| `/create spec` | `/code spec` | New implementation spec for a milestone |
| `/create rule` | `/rule create` | New project rule |
