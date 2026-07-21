---
description: "**Remote compute** — ephemeral GPU instances via SSH + rsync + watcher (not yet under the SKA prefix)."
---
:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [SKL](hook://SKL) → [EXP](hook://p/EXP)
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
- `exp` — CLI for remote experimentation ([exp.sh](exp.sh); dispatcher script lives at `scripts/exp` inside this skill and is wired onto `$PATH` by the user)
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
[[anchor-install]] - 
[[Architect]] - 
[[Atlas Design]] - 
[[atlas/Atlas]] - 
[[Audit]] - 
[[backlog/Backlog]] - 
[[brief-template]] - 
[[cab-migrate]] - 
[Cleanup](hook://Cleanup) - 
[[code-anchor]] - 
[[code-arch-audit]] - 
[[code-ask-questions]] - 
[[code-bugfix]] - 
[[code-changelog]] - 
[[code-code]] - 
[[code-delegate]] - 
[[code-execute]] - 
[[code-forge]] - 
[[code-ios]] - 
[[code-mac-gui]] - 
[[code-merge]] - 
[[code-mint]] - 
[[code-modules]] - 
[[code-package]] - 
[[code-plan-audit]] - 
[[code-pr-flow]] - 
[[code-publish]] - 
[[code-release]] - 
[[code-replan]] - 
[[code-research]] - 
[[code/code-review]] - 
[[code-rewire]] - 
[[code-rewire.compiled]] - 
[[code-setup]] - 
[[code-ship]] - 
[[code-spec]] - 
[[code-spike]] - 
[[code-system-design]] - 
[[code-test]] - 
[[code-test-external]] - 
[[code-test-plan]] - 
[[code-test-quality]] - 
[[code-test-scaffolds]] - 
[[code-testing]] - 
[[code-verify]] - 
[[code-version]] - 
[[code-workers]] - 
[[code-worktrees]] - 
[Crank](hook://Crank) - 
[Create](hook://Create) - 
[[DAS Skills]] - 
[design](hook://design) - 
[[excalidraw-examples]] - 
[[docs/EXP]] - 
[[EXP Backlog]] - 
[[EXP Messages]] - 
[Feature](hook://Feature) - 
[Finalize](hook://Finalize) - 
[[find/Find]] - 
[[find-corp]] - 
[[find-person]] - 
[[find-product]] - 
[[find-software]] - 
[[fix-claude-permissions]] - 
[[fix-claude-session]] - 
[[fix-google-reauth]] - 
[[fix-mac-finder-dotfiles]] - 
[[fix-mac-key-repeat]] - 
[[fix-mac-mail-delete-to-archive]] - 
[[fix-mac-sudo-nopassword]] - 
[[fix-mac-unsigned-apps]] - 
[[fix-obsidian-python-comments]] - 
[Fortify](hook://Fortify) - 
[[google-sheets]] - 
[[google-slides]] - 
[Groom](hook://Groom) - 
[[io/SKILL]] - 
[[io-email]] - 
[[io-email-access]] - 
[[io-excel]] - 
[[io-gdoc]] - 
[[io-gdrive]] - 
[[io-gsheet]] - 
[[io-gslide]] - 
[[io-notion]] - 
[Land](hook://Land) - 
[[md-cards]] - 
[[md-dispatch-table]] - 
[[md-file-tree]] - 
[[md-toc]] - 
[[md-track-changes]] - 
[[meta-survey]] - 
[Mint](hook://Mint) - 
[[MUSE]] - 
[[profile/Profile]] - 
[[profile-book]] - 
[[profile-corp]] - 
[[profile-person]] - 
[[profile-product]] - 
[[profile-software]] - 
[[rewire]] - 
[Rule](hook://Rule) - 
[[rules/find]] - 
[[rules/profile]] - 
[[rules/survey]] - 
[[SKILL-retired]] - 
[[status-doc-template]] - 
[[survey/Survey]] - 
[[survey-corp]] - 
[[survey-person]] - 
[[survey-product]] - 
[[survey-skill]] - 
[[survey-software]] - 
[[template.docx]] - 
[[viz-d2]] - 
[[viz-diagram]] - 
[[viz-docx]] - 
[[viz-dot]] - 
[[viz-excalidraw]] - 
[[viz-matplot]] - 
[[viz-mermaid]] - 
[[viz-pdf]] - 
[[viz-pptx]] - 
[[viz-svg]] - 
[Workflow](hook://Workflow) -
