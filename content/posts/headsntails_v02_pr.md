---
title: headsntails v0.2 Release!
date: 2026-07-06
excerpt: Just like if out of nowhere - headsntails (formerly known as Flagship) released with v0.2
---

![It ain't much, but it's honest work](/assets/aint_much_memphis_v0.2.png)

Recap:
`headsntails` ([repository here](https://github.com/NGUgeneral/headsntails-platform)) is my pet project - a fully decoupled infrastructure built to serve the Feature Flags pattern. It's designed to start as a simple, zero-friction plug-in, with the architectural legs to scale all the way up to a standalone SaaS solution.

Milestones reached to unlock the v0.2 achievement:

- **The Rename**: The entire ecosystem was officially migrated from "Flagship" to headsntails.
- **Full Test Coverage**: Added dedicated unit test suites for each separate service, backed by full E2E testing for the entire distributed system.
- **State & Hydration**: Implemented a single source of truth, local caching, and automatic Redis hydration on startup.
- **Code Health**: Handled minor optimizations and foundational refactoring across the codebase.

It was tedious groundwork - the "*you really better do it now*" one, which pays dividends later.

By clearing this out, we are now standing right in front of the main architectural twist: full gRPC communication.
For the upcoming v0.3 release, the target is "simply" eliminating the obvious bottleneck: HTTP communication between the Go Core and the Python Rate-Limiter.

Stay tuned!