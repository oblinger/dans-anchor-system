# System Conversation

High-level interactive conversation to establish the technical foundation before writing the System Design doc. The agent prompts the user with targeted questions, captures decisions, and produces a summary that feeds into `/code system-design`.

## When to Use

After UX Design, before System Design. Run when the technical approach has not yet been decided, or when revisiting fundamental technical choices.

## Workflow

### 1. Review Context

Read the PRD and UX Design docs to understand what the system must do and how users interact with it.

### 2. Ask Foundation Questions

Present these topics one at a time or in small batches, adapting to what is already known:

**Language and Runtime**
- What language(s)? Any constraints on version or toolchain?
- What runtime environment? (native, browser, server, embedded)

**Event Model**
- What drives the system? (request-response, event loop, message queue, cron, user input)
- Is there real-time communication? (WebSocket, SSE, polling)

**Components and Boundaries**
- What are the major components? (frontend, backend, CLI, agent, database)
- Where do components run? (same process, separate processes, separate machines)
- What are the interfaces between components? (API, IPC, shared filesystem, message bus)

**State and Persistence**
- What state does the system maintain? (in-memory, files, database, external service)
- What is the source of truth for each piece of state?
- How does state survive restarts?

**Dependencies**
- What external services or APIs does it depend on?
- What libraries or frameworks are assumed?
- Are there dependencies that constrain the architecture?

**Deployment**
- Where does it run in production? (local machine, cloud, app store, package registry)
- How is it installed and updated?
- What are the operational requirements? (uptime, monitoring, logging)

### 3. Capture Decisions

Record each answer as a decision. For contested points, capture the alternatives considered and the reasoning for the choice in `{NAME} Discussion.md`.

### 4. Produce Summary

Write a summary document or section in `{NAME} Discussion.md` with all decisions. This becomes the input for `/code system-design`.

### 5. Identify Gaps

Flag any questions the user could not answer or deferred. Add them to `{NAME} Open Questions.md` so they are resolved before implementation.
