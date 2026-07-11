---
description: "skim → click into the rule that applies"
---
# SKL Find
| -[[DAS Find]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [DAS Find](hook://p/DAS%20Find)<br>: skim → click into the rule that applies|
| --- | --- |
| Related | [[skills/find/SKILL.md\|SKILL]],   |
| Find rules (any type) | [[SRC rules/find\|find.md]],   |
| Types | [[SRC rules/find-person\|find-person]],  [[SRC rules/find-corp\|find-corp]],  [[SRC rules/find-product\|find-product]],   |
| [[DAS Find Design\|Design]] |  |

**Find** locates one specific match for given criteria and returns identifier + canonical URL + 1-line context + confidence + sources. It disambiguates when candidates score close, rather than silently picking. For just identifying — not profiling (use [[DAS Profile]]) or comparing many (use [[DAS Survey]]).

Invoke: *"find me X"* / *"find the GitHub repo for X"* / *"find John Smith at Acme as VP Engineering."*

Outputs: [[Find]] (`~/ob/kmr/Topic/Search/Find/`).

Skill: [[find/SKILL|find/SKILL.md]] · Rules trait: [[skill-search-rules]] · Composition: [[DAS Search Overview]].
