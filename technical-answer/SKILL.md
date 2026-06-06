---
name: technical-answer
description: Chat-response discipline for technical-interface questions — how the agent answers questions about APIs, function signatures, library behavior, config schemas, CLI flags, and wire formats in conversational replies (not file-output).
user_invocable: false
---

# Technical-Answer Discipline

`technical-answer` is *the chat-response discipline an agent applies when the user asks a question about how a technical interface or system actually works — APIs, signatures, library behavior, config schemas, CLI flags, wire formats — as opposed to asking for a written report (which routes to `[[describe]]` / `[[find]]` / `[[survey]]` / `[[deep-research]]`).* Implicit-trigger: the agent recognizes the question shape and consults this discipline without explicit user invocation.

(v1 stub per [[F118 — Technical-answer discipline — implicit-trigger chat-response rules for tech-interface Qs|F118]] Phase 1 — body content deferred to Phase 2 after user-driven walkthrough of F118 § Recommendations.)
