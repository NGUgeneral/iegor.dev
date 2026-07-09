---
title: headsntails v0.3 Release!
date: 2026-07-09
excerpt: Going strong, `headsntails` releases v0.3. Overal system resilience improved and the main communication bottleneck eliminated.
---

![It ain't much, but it's honest work](/assets/aint_much_memphis_v03.png)

Recap:
`headsntails` ([repository here](https://github.com/NGUgeneral/headsntails-platform)) is my pet project - a fully decoupled infrastructure built to serve the Feature Flags pattern as a standalone distributed system or plainly as plug-and-play internal Go service
 But with each release it shapes up more and more as a resilient system infrastructure blueprint.

Milestones reached to unlock the v0.3:

- **gRPC Introduced**: the initial design had one major bottleneck: rate-limiter communication via HTTP. This version replaces it with gRPC at once. The change is drastic.
- **The Documentation**: All public-facing services have exposed their endpoints in one place. Openapi documentation is now available `/docs`. Internal endpoints, even if visible, are whitelisted on Nginx to local IPs. For now - it is enough.
- **The High-Load**: High-Load benchmark service, [Fortio](https://fortio.org/) introduced into the system. It proved to be a great asset outside of simple benchmark but stress testing the system. Implementing it directly allows to test internal endpoints as well.
- **The Configuration**: All the hardcoded configuration values were moved out into .env values.
- **Quality of Life changes**: stress testing the system revealed some holes which were fixed.

Implementing unit test suites for each service and E2E tests into the CI/CD pipelines definitely was a must investment which made implementing current "complex" features way more efficient and predictable.

By introducing gRPC into the system we now can proceed to the next milestone in v0.4: implementing consumer side gRPC connection. For Flags consumption - both connections will be available side by side, HTTP and gRPC (where the first will be a system bottleneck if implemented as a distributed system, but may be acceptable as a sidecar service).

Stay tuned!