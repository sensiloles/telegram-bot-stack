## Summary
BotBase currently focuses on very simple bots (registration, admin commands). To build medium-complexity assistants with this framework, we need richer conversation orchestration, persistent state helpers, proactive jobs, and stronger extension points across BotBase, AdminManager, UserManager, and storage modules.

## Market snapshot
- Customer-service & FAQ bots need branching forms, escalation hooks, and message templates.
- Commerce & booking bots need cart/order state, scheduled reminders, and payment-proof workflows.
- Education/coaching bots need sequenced lessons, drip campaigns, and progress tracking.
- Community/loyalty bots need segmentation, broadcast safety rails, and analytics on engagement.

## Problem
Developers currently have to reimplement conversation state, background tasks, middleware, and observability on top of BotBase. This creates duplicated effort and slows adoption for teams targeting the segments above.

## Goals
1. Extend BotBase with a scene/step engine (state store, validation, timeouts, resume).
2. Provide middleware/dependency hooks so features can inject logic before/after handlers.
3. Expand storage contracts (StorageBackend, UserManager, AdminManager) to keep arbitrary per-user/per-chat metadata needed by flows.
4. Add a lightweight job scheduler/reminder API (async tasks + persistence hooks).
5. Ship first-party utilities: templated replies, keyboard builders, localization + pluralization helpers.
6. Expose observability (structured logging, metrics counters/hooks) and a test harness for flow simulations.
7. Update docs/examples to showcase a “medium complexity” bot (e.g., booking or onboarding flow).

## Acceptance criteria
- BotBase supports declarative registration of scenes/steps with persistence + validation.
- Middleware pipeline allows stacking of auth, logging, throttling without editing core handlers.
- Storage interfaces support namespaced arbitrary data with migration notes.
- Scheduler API can enqueue delayed jobs and survives bot restarts.
- Utilities for templated messaging/localization are reusable across bots.
- Example bot + docs walk through building a multi-step flow using the new APIs.
- Ruff + pytest suites cover the new modules (≥ existing 80% coverage target).

## Out of scope
- Payment integrations or channel adapters beyond Telegram.
- Web dashboards (only CLI/docs for now).
