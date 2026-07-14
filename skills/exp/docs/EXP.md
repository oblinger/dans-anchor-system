---
description: "2026 Vast ML Testing — ML experiment suites (distillation, interpretability, LLM probing) run on vast.ai GPUs"
---
:>> [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [EXP](hook://p/EXP)
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
[[ASG]] - 
[[templates/backlog]] - 
[[completed-roadmap]] - 
[[DAS Anchor Design]] - 
[[DAS Anchor Toolkit]] - 
[[DAS Anchor Toolkit Design]] - 
[[DAS Architect]] - 
[[DAS Architect Design]] - 
[[DAS Ask]] - 
[[DAS Ask Design]] - 
[[DAS ask-inline]] - 
[[DAS Audit]] - 
[[DAS Audit Design]] - 
[[DAS Book]] - 
[[DAS Code Design]] - 
[[DAS Code Skill]] - 
[[DAS Code Skill Design]] - 
[[DAS Cook]] - 
[[DAS Cook Design]] - 
[[DAS Corp]] - 
[[DAS Crank]] - 
[[DAS Crank Design]] - 
[[DAS Crank PRD]] - 
[[DAS Create]] - 
[[DAS Create Design]] - 
[[DAS Ctrl]] - 
[[DAS Ctrl Design]] - 
[[DAS Design]] - 
[[DAS Design Design]] - 
[[DAS Doc Design]] - 
[[DAS Docs]] - 
[[DAS Drive Design]] - 
[[DAS Dupes]] - 
[[DAS Dupes Design]] - 
[[DAS Edit]] - 
[[DAS Exp]] - 
[[DAS Exp Design]] - 
[[DAS Feature]] - 
[[DAS Feature Design]] - 
[[DAS Feature PRD]] - 
[[DAS Finalize]] - 
[[DAS Finalize Design]] - 
[[DAS Finalize PRD]] - 
[[DAS Find]] - 
[[DAS Find Design]] - 
[[DAS Fix]] - 
[[DAS Fix Design]] - 
[[DAS Fortify]] - 
[[DAS Fortify Design]] - 
[[DAS Fortify PRD]] - 
[[DAS Groom]] - 
[[DAS Groom Design]] - 
[[DAS Groom PRD]] - 
[[DAS Hygiene Design]] - 
[[DAS Install]] - 
[[DAS Install Design]] - 
[[DAS IO]] - 
[[DAS Land]] - 
[[DAS Land Design]] - 
[[DAS Land PRD]] - 
[[DAS Maintain]] - 
[[DAS Maintain Design]] - 
[[DAS MD]] - 
[[DAS MD Design]] - 
[[DAS Meta Survey]] - 
[[DAS Migrate]] - 
[[DAS Migrate Design]] - 
[[DAS Mint]] - 
[[DAS Mint Design]] - 
[[DAS Mint PRD]] - 
[[DAS Move Design]] - 
[[anchor/DAS Move]] - 
[[DAS Parley]] - 
[[DAS Parley Design]] - 
[[DAS Person]] - 
[[DAS Pilot Flow]] - 
[[DAS Pilot Flow Design]] - 
[[DAS Plan]] - 
[[DAS PR Flow]] - 
[[DAS PR Flow Design]] - 
[[DAS Product]] - 
[[DAS Profile]] - 
[[DAS Profile Design]] - 
[[DAS Publish]] - 
[[DAS Publish Design]] - 
[[DAS Purchase]] - 
[[DAS Purchase Design]] - 
[[DAS Research]] - 
[[DAS Research Skill]] - 
[[DAS Rewire]] - 
[[DAS Rewire Design]] - 
[[DAS Rulesets]] - 
[[DAS Search Design]] - 
[[DAS Search Overview]] - 
[[search/DAS Skill]] - 
[[DAS Skills]] - 
[[DAS Slug Scan]] - 
[[DAS Slug Scan Design]] - 
[[DAS Snip]] - 
[[DAS Snip Design]] - 
[[DAS Software]] - 
[[DAS Streams]] - 
[[DAS Streams Design]] - 
[[DAS Survey]] - 
[[DAS Survey Design]] - 
[[DAS Templates]] - 
[[DAS Tidy]] - 
[[DAS Tidy Design]] - 
[[DAS Tracking Design]] - 
[[DAS Utility Design]] - 
[[DAS Viz]] - 
[[DAS Viz Design]] - 
[[anchor/DAS WP]] - 
[[DAS WP Design]] - 
[[DAS Yore]] - 
[[DAS Yore Design]] - 
[[templates/decisions]] - 
[[Diagram]] - 
[[disciplines]] - 
[[examples]] - 
[[docs/EXP]] - 
[[facets]] - 
[[fix/SKILL]] - 
[[library]] - 
[[messages]] - 
[[templates/prd]] - 
[[query]] - 
[[Query PRD]] - 
[[R-all-files]] - 
[[R-anchor]] - 
[[R-anchor-group]] - 
[[R-anchor-page]] - 
[[R-anchor-tree]] - 
[[R-api]] - 
[[R-arch]] - 
[[R-architecture]] - 
[[R-backlog]] - 
[[R-brief]] - 
[[R-bringhurst-typography]] - 
[[R-c4]] - 
[[R-cards]] - 
[[R-changes]] - 
[[R-cli]] - 
[[R-code]] - 
[[R-code-mirror]] - 
[[R-code-repository]] - 
[[R-code-surface]] - 
[[R-completed-roadmap]] - 
[[R-dated-entry-stream]] - 
[[R-decisions]] - 
[[R-design]] - 
[[R-design-dispatch]] - 
[[R-design-docs-group]] - 
[[R-design-gate]] - 
[[R-dev-dispatch]] - 
[[R-diagram]] - 
[[R-diagram-geometry]] - 
[[R-discussion]] - 
[[R-dispatch-group]] - 
[[R-dispatch-table]] - 
[[R-doc]] - 
[[R-doc-facet]] - 
[[R-doc-structure]] - 
[[R-documentation-site]] - 
[[R-dot-anchor]] - 
[[R-exception-discipline]] - 
[[R-facet]] - 
[[R-facet-spec]] - 
[[R-factory-pegboard]] - 
[[R-fct-claude]] - 
[[R-fct-features]] - 
[[R-fct-folder]] - 
[[R-fct-icebox]] - 
[[R-fct-inbox]] - 
[[R-fct-interface]] - 
[[R-fct-move]] - 
[[R-fct-outputs]] - 
[[R-fct-plan-dispatch]] - 
[[R-fct-system-design]] - 
[[R-fct-user-dispatch]] - 
[[R-file-association]] - 
[[R-files-architecture]] - 
[[R-git]] - 
[[R-interfaces-folder]] - 
[[R-ios]] - 
[[R-layering]] - 
[[R-log]] - 
[[R-mac]] - 
[[R-markdown]] - 
[[R-md]] - 
[[R-messages]] - 
[[R-module-doc]] - 
[[R-naming]] - 
[[R-ob]] - 
[[R-ob-cmd-proc]] - 
[[R-ob-observability]] - 
[[R-ob-remote-ops]] - 
[[R-ob-state-mgt]] - 
[[R-one-path]] - 
[[R-openspec]] - 
[[R-output-group]] - 
[[R-ownership]] - 
[[R-paper]] - 
[[R-pathguard]] - 
[[R-prd]] - 
[[R-process]] - 
[[R-progressive]] - 
[[R-project-page]] - 
[[R-query]] - 
[[R-roadmap]] - 
[[R-ruleset]] - 
[[R-simple]] - 
[[R-single-source-of-truth]] - 
[[R-skill]] - 
[[R-skill-anchor]] - 
[[R-skill-md]] - 
[[R-specs]] - 
[[R-stable-ids]] - 
[[R-state-region]] - 
[[R-status]] - 
[[R-stories]] - 
[[R-sugiyama]] - 
[[R-svg-hygiene]] - 
[[R-svg-jiggle]] - 
[[R-template]] - 
[[R-test]] - 
[[R-testing]] - 
[[R-topic]] - 
[[R-track-dispatch]] - 
[[R-track-group]] - 
[[R-trait]] - 
[[R-tufte-data-ink]] - 
[[R-ux]] - 
[[R-versions]] - 
[[R-wcag-contrast]] - 
[[R-wp]] - 
[[R-wrapper-cli]] - 
[[rulesets/README]] - 
[[Rulesets Brief]] - 
[[skill-docs]] - 
[[status]] - 
[[templates/log]] - 
[[templates/roadmap]] - 
[[templates/testing]] - 
[[traits]] - 
[[Warden]] - 
[[{slug} Log]] - 
[[{slug} Track]] - 
[[{{YYYY-MM-DD}} — {{short topic}}]] -
