---
description: "OAuth 2.0 Authorization-Code-with-PKCE login flow for a web checkout, traced across browser, app server, and identity provider."
---
# 03 — Sequence diagram

**Diagram kind:** Sequence diagram (UML interaction).
**Layout challenge:** preserving the strict top-to-bottom time axis while routing every ordered message between participant lifelines — including a self-message, a dashed return, and an async background call — without crossing or reordering arrows.
**Domain:** A shopper signs in to the "Marketplace" web store via an external identity provider (Auth0-style) using the OAuth 2.0 Authorization Code flow with PKCE, then is issued a session.

## Nodes
Each node is a **participant** with its own vertical lifeline. Messages are ordered events on those lifelines; the numeric prefix in each edge label fixes the time order (top to bottom).

- User — the human shopper at the keyboard [actor]
- Browser — the shopper's web browser [participant]
- AppServer — Marketplace web/app server (the OAuth client) [participant]
- AuthZ — Identity Provider authorization endpoint (`/authorize`) [participant]
- TokenSvc — Identity Provider token endpoint (`/token`) [participant]
- UserDB — Marketplace user/profile database [participant]
- SessionStore — Redis session store [participant]

## Edges
Every edge is one message; direction is `source → target`. Solid = a call/request initiated by the source; dashed = a return/response/redirect back to the caller. Labels are prefixed with their sequence number.

- User → Browser : "1. click 'Sign in'" [solid]
- Browser → AppServer : "2. GET /login" [solid]
- AppServer → AppServer : "3. generate code_verifier + code_challenge (PKCE)" [solid]
- AppServer → Browser : "4. 302 redirect to /authorize (challenge, state)" [dashed]
- Browser → AuthZ : "5. GET /authorize?challenge,state" [solid]
- AuthZ → Browser : "6. render login form" [dashed]
- User → Browser : "7. submit credentials" [solid]
- Browser → AuthZ : "8. POST credentials" [solid]
- AuthZ → Browser : "9. 302 redirect to /callback?code,state" [dashed]
- Browser → AppServer : "10. GET /callback?code,state" [solid]
- AppServer → TokenSvc : "11. POST /token (code, code_verifier)" [solid]
- TokenSvc → AppServer : "12. 200 {access_token, id_token}" [dashed]
- AppServer → UserDB : "13. upsert user from id_token claims" [solid]
- UserDB → AppServer : "14. user record" [dashed]
- AppServer → SessionStore : "15. SET session (user_id, tokens)" [solid]
- SessionStore → AppServer : "16. OK (session_id)" [dashed]
- AppServer → Browser : "17. 302 redirect to /account (Set-Cookie: session_id)" [dashed]
- Browser → User : "18. show account dashboard" [dashed]

## Groups / lanes / cardinality
- Lifelines: 7 participants, each owning one vertical lifeline; all messages live on those lifelines.
- Message 3 is a **self-message** (AppServer → AppServer) and must render as a loop on AppServer's own lifeline.
- Cardinality: exactly one message between any ordered pair as listed; no message is implied or merged.
- The two IdP endpoints (AuthZ, TokenSvc) are distinct participants — do not collapse them into a single "IdP" lifeline.
- Time order is total and explicit (1→18); the vertical position of each message must respect this order.

## Acceptance
- Fidelity: the render contains exactly these 7 nodes (participants) and 18 edges (messages); counts and labels match, including the self-message and every dashed return; none added, dropped, merged, or reordered.
- Legibility: text ≥ ~18px at page-width embed; aspect ~0.6–1.6; no overlaps; per [[R-diagram]].
