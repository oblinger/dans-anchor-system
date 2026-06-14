---
description: "skim → click into the rule that applies"
---
# SKL Find
| -[[SKL Find]]- | → [[kmr]] → [[SYS]] → [[Bespoke]] → [[SKA]] → [[DAS]] → [[SKL Search]] → [SKL Find](hook://p/SKL%20Find)<br>: skim → click into the rule that applies |
| --- | --- |
| Find rules (any type) | [[SRC rules/find\|find.md]],   |
| Types | [[SRC rules/find-person\|find-person]],  [[SRC rules/find-corp\|find-corp]],  [[SRC rules/find-product\|find-product]],   |
| [[SKL Find Design\|Design]] |  |

**Find** locates one specific match for given criteria and returns identifier + canonical URL + 1-line context + confidence + sources. It disambiguates when candidates score close, rather than silently picking. For just identifying — not profiling (use [[SKL Profile]]) or comparing many (use [[SKL Survey]]).

Invoke: *"find me X"* / *"find the GitHub repo for X"* / *"find John Smith at Acme as VP Engineering."*

Outputs: [[Find]] (`~/ob/kmr/Topic/Search/Find/`).

Skill: [[find/SKILL|find/SKILL.md]] · Rules trait: [[skill-search-rules]] · Composition: [[SKL Search Overview]].
