---
description: skills dispatch table
---

| -[[SKL]]- | → [SKL](hook://p/SKL)<br>:  |
| --- | --- |
| Related | [[CAB]], [[SKL Skills\|Skills]],  |
|  |  |
| **[[cab/SKILL\|CAB]]** | [[cab/cab-create\|create]], [[cab/cab-tidy\|tidy]], [[cab/cab-move\|move]], [[cab/cab-migrate\|migrate]], [[cab/cab-lint\|lint]], [[cab/cab-yore\|yore]], [[cab/cab-pr-flow\|pr-flow]], [[cab/cab-pilot-flow\|pilot-flow]], [[cab/cab-slug-scan\|slug-scan]], [[cab/cab-maintain\|maintain]], [[cab/cab-scan\|scan]], [[cab/cab-config\|config]], [[cab/cab-install\|install]] |
| **[[ctrl/SKILL\|Ctrl]]** | box, outbox, surf, search, navigate |
| **[[code/SKILL\|Dev]]** | [[feature/SKILL\|feature]], [[code/code-plan\|plan]], [[code/code-execute\|execute]], [[code/code-test\|test]], [[code/code-replan\|replan]], [[code/code-setup\|setup]], [[code/code-forge\|forge]], [[code/code-bugfix\|bugfix]], [[code/code-spike\|spike]], [[code/code-delegate\|delegate]], [[code/code-rewire\|rewire]] |
| **[[edit/SKILL\|Edit]]** | [[edit/edit-excalidraw\|excalidraw]] |
| **[[io/SKILL\|IO]]** | [[io/io-sheets\|sheets]], [[io/io-slides\|slides]], [[io/io-docs\|docs]], [[io/io-email\|email]], [[io/io-sync\|sync]] |
| **[[md/SKILL\|MD]]** | [[md/md-file-tree\|file-tree]], [[md/md-toc\|toc]], [[md/md-dispatch-table\|dispatch-table]], [[md/md-cards\|cards]], [[md/md-track-changes\|track-changes]] |
| **[[product/SKILL\|Product]]** | [[product/product-hunt\|hunt]], [[product/product-find\|find]], [[product/product-buy\|buy]], [[product/product-reorder\|reorder]] |
| **[[research/SKILL\|Research]]** | [[research/research\|dig/survey]] |
| **[[role/SKILL\|Role]]** | [[role/role-pilot\|pilot]], [[role/role-pm\|pm]], [[role/role-worker\|worker]], [[role/role-setup\|setup]] |
| **[[rule/SKILL\|Rule]]** | [[rule/rule-create\|create]], [[rule/rule-check\|check]], [[rule/rule-triage\|triage]], [[rule/rule-fix\|fix]], [[rule/rule-sync\|sync]], [[rule/rule-consider\|consider]] |
| **[[audit/SKILL\|Audit]]** | [[audit/audit-structure\|structure]], [[audit/audit-rules\|rules]], [[audit/audit-docs\|docs]], [[audit/audit-publish\|publish]] |
| ... |  |


| LIFECYCLE    | Actions                                                                                                               |
| ------------ | --------------------------------------------------------------------------------------------------------------------- |
|              | Create → Plan → ↻( [[SKL Feature\|Feature]] ([[SKL Ready\|Ready]]) → [[SKL Mint\|Mint]]  ([[SKL Finalize\|Finalize]]) |
| **Setup**    | Distill, [[cab/cab-install\|Install]], [[cab/cab-slug-scan\|Rid-scan]], [[cab/cab-scan\|Scan]]  \|  [[SKL Migrate\|Migrate]], [[code/code-rewire\|Rewire]], [[cab/cab-tidy\|Tidy]], [[CAB Move\|Move]] |
| **Create**   | [[cab/cab-create\|Anchor]], [[feature/SKILL\|Feature]], [[cab/cab-wp\|Wp]]                                        |
| **Audit**    | [[audit/audit-structure\|Structure]], [[audit/audit-docs\|Docs]], [[audit/audit-rules\|Rules]], [[audit/audit-code\|Code]], [[audit/audit-publish\|Pre-publish]], [[cab/cab-lint\|Lint]] |
| **Rule**     | [[rule/rule-create\|Create]], [[rule/rule-check\|Check]], [[rule/rule-triage\|Triage]], [[rule/rule-fix\|Fix]], [[rule/rule-sync\|Sync]], [[rule/rule-consider\|Consider]] |
| **Maintain** | [[cab/cab-maintain\|Maintain]]                                                                                        |
| **Publish**  | [[cab/cab-publish\|Publish]]                                                                                          |
| **Status**   | Add, Update, Archive, Show, Activate                                                                                  |
| **Archive**  | [[cab/cab-yore\|Yore]]                                                                                                |
| **Role**     | [[role/role-pilot\|Pilot]], [[role/role-pm\|Pm]], [[role/role-worker\|Worker]], [[role/role-setup\|Setup]]              |

| DOCUMENT      | Actions                                              |
| ------------- | ---------------------------------------------------- |
| **IO**        | [[io/io-gsheet\|Gsheet]], [[io/io-gslide\|Gslide]], [[io/io-gdoc\|Gdoc]], [[io/io-gdrive\|Gdrive]], [[io/io-email\|Email]], [[io/io-notion\|Notion]], [[io/io-gauth\|Gauth]] |
| **Edit**      | [[edit/edit-excalidraw\|Excalidraw]]                 |
| **Markdown**  | [[md/md-file-tree\|File-tree]], [[md/md-toc\|Toc]], [[md/md-dispatch-table\|Dispatch-table]], [[md/md-cards\|Cards]], [[md/md-track-changes\|Track-changes]] |
| **Research**  | [[research/research\|Dig]], [[research/research\|Survey]] |

| CODE             | Actions                                                                                                                 |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------- |
|                  | Anchor → Plan →  ↻( [[SKL Feature\|Feature]] ([[SKL Ready\|Ready]]) → [[SKL Mint\|Mint]]  ([[SKL Finalize\|Finalize]])) |
| **Create**       | [[feature/SKILL\|Feature]], Spec                                                                                    |
| **Plan**         | [[code/code-plan\|Plan]], [[code/code-prd\|Prd]], [[code/code-ux\|Ux]], [[code/code-system\|System]], [[code/code-research\|Research]], (plus Architect) |
| →→ **Architect** | [[code/code-architect\|Architect]], [[code/code-system-design\|System-design]], [[code/code-modules\|Modules]], [[code/code-roadmap\|Roadmap]] |
| **Ready**        | [[SKL Ready\|Ready]], [[code/code-replan\|Replan]], [[code/code-open-questions\|Open-questions]]                         |
| **Mint**         | [[code/code-mint\|Mint]], [[code/code-code\|Code]], [[code/code-bugfix\|Bugfix]], [[code/code-spike\|Spike]], [[code/code-forge\|Forge]], (plus Test) |
| →→ **Test**      | [[code/code-test\|Test]], [[code/code-verify\|Verify]], [[code/code-review\|Review]]                                    |
| **Publish**      | [[code/code-release\|Release]], [[cab/cab-publish\|Publish]], [[code/code-ship\|Ship]]                                  |
| **Delegate**     | [[code/code-delegate\|Delegate]], [[code/code-workers\|Workers]], [[code/code-pr-flow\|Pr-flow]], [[code/code-merge\|Merge]] |

