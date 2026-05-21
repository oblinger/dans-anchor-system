:>> [[ _ ]] > [[kmr]] > [[SYS]] > [[Bespoke]] > [EXP](hook://p/EXP)


# EXP System

## Documentation

### Process
- [[EXP Orchestrator Flow]] — main session: dispatch, monitor, review, integrate (uses ROADMAP)
- [[EXP Master Flow]] — research cycle process (frame → execute → polish)
- [[EXP Experiment Flow]] — single experiment lifecycle (design → delegate → run → review → integrate)

### Worker
- [[EXP Worker Instructions]] — worker operating manual (setup → run → pull → write up → signal done)

### Deliverables
- [[EXP Write Up Template]] — deliverable template (summary up top, detailed evidence below)
- [[EXP Experiment Template]] — standard format for individual experiment specs

## Core Tools, Config & Workers
- `exp` — CLI for remote experimentation ([exp.sh](exp.sh), dispatcher: `~/bin/exp`)
- [EXP Config Folder](hook://EXP%20Config%20Folder) — `~/.config/exp/` (remote configs, worker symlink)
- Worker instructions symlink: `~/.config/exp/exp-worker.md` → [[EXP Worker Instructions]]

## Quick Reference

```bash
exp init <ip:port> -r <name>       # save remote, verify, set up watcher
exp exe "cmd" [timeout] -r <name>  # push → run → wait → pull
exp push <folder> -r <name>        # rsync to remote
exp pull <folder> -r <name>        # rsync from remote
exp check [lines] -r <name>        # tail remote tmux
exp status [-r <name>]             # quick status check
exp health [-r <name>] [--fix] [--alert <pane>]  # health report
exp stop -r <name>                 # kill running command
exp close -r <name>                # tear down watcher
exp list                           # show all remotes
exp worker <name> --host "port root@ip"  # create/update worker (idempotent)
exp teardown -r <name>                   # full teardown (stop + remove + kill tmux)
exp zap <folder> [instruction] -r <name> # dispatch experiment folder to worker
exp build                          # ZIP experiments for deliverable bundle
```


## .
. __ .
