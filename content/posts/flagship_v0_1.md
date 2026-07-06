---
title: Flagship v0.1 Release!
date: 2026-06-30
excerpt: I am happy to anounce the release of my very own YAOSFFS (Yet Another Open-Source Feature Flags Service) - Flagship!
---

![It ain't much, but it's honest work](/assets/it-aint-much.png)

Flagship ([repository here](https://github.com/NGUgeneral/headsntails-platform)) is YAOSFFS (Yet Another Open-Source Feature Flags Service). The twist - full gRPC communication loop by v1.0.<br>
It is not a unique solution, but will be a great case study for myself and hopefully an interesting digest into your feed.

## The Motivation:
As I recently shared with you - Feature Flags is not a universally adopted tool. My humble opinion, about heavy missing out without it in production, is nice to have. But it is not a reason to build it from scratch.<br>
The real reason? Bloat. Most enterprise flag services require massive architectural buy-in. I wanted a zero-friction, lightweight utility that I can quickly spin up the moment I join a new team that is missing the tool.
This brings us to

## The requirements:
Enclosed ecosystem which can be scaled all the way up to a SaaS solution if needed, but decoupled enough to be easily stripped down to core functionality and plugged into existing product As-Is without too much dancing around it.

## The solution:
High throughput core service, written in Golang, supported with JWT Authority and Rate Limiter sidecars, which can be whatever, but as part of Flagship - implemented with Python/FastAPI (leveraging Python's velocity for operational tooling, and Go's raw concurrency for execution).

## The Diagram:

```text
                  [ PUBLIC TRAFFIC ]
                          │
                          ▼
              [ Edge Ingress / Nginx:80 ]
               /          │          \
      /api/v1/flags/  /api/v1/auth/  /api/v1/limiter/
             /            │            \ (Restricted)
            ▼             ▼             ▼
     [Flagship Core] [JWT Authority] [Rate Limiter]
        (Go:8080)     (Python:3000)   (Python:8000)
         │    │                             │
         │    └─────────(Intranet)──────────┤
         ▼                                  ▼
   [PostgreSQL] ───────────────────────► [Redis]
 (Write-Through)                       (Sliding Window)
```

Very simple and straightforward.<br>
All but Flagship Core is optional.

## The v0.1:
The current release is a full ecosystem, ready to be spun up with a single docker-compose command.<br>
For this version:
- Full HTTP is acceptable for this release. But intranet between services is mandatory.
- State fully handled by Redis is acceptable for this release.
- JWT Authority can have a single high-entropy master cryptography key. It exists as a secret. On cloud, it lives in a single secret manager.
- Rate Limiter supports Token based rates.
- Rate Limiter bottleneck is known and is acceptable for this release.

## The Roadmap:

| Phase | Milestone | Core Focus | Architecture Impact | Status |
| :--- | :--- | :--- | :--- | :--- |
| **v0.1** | **Container Monolith Base** | Orchestrated REST Core | Edge Ingress routing, multi-language container isolation | **Released** |
| **v0.2** | **Source of Truth & Hydration** | Reliable State Handling | Write-Through pattern to PostgreSQL; ultra-fast reads from Redis | *In Progress* |
| **v0.3** | **Sidecar Latency Optimization** | gRPC Communication Layer | Migrate inter-service checks to gRPC to eliminate HTTP/1.1 HoL blocking | *Planned* |
| **v0.4** | **High-Perf Edge Layer** | Global gRPC Ingress | Transition public edge routing to utilize Protocol Buffers & HTTP/2 streaming | *Planned* |
| **v0.5** | **Advanced Targeting Engine**| Contextual Flag Evaluation | Abstract rule-matching evaluation engines beyond simple primitives | *Planned* |
| **v0.6** | **Distributed Event Bus** | Real-Time Cache Sync | Integrate RabbitMQ/Kafka to synchronize cache states across cross-region nodes | *Planned* |
| **v0.7** | **Cloud-Native Scale** | Infrastructure as Code | Multi-AZ AWS ECS Fargate deployment automated via Terraform | *Planned* |

I sure will have fun building it.<br>
If you will have fun watching me do it - that’s up to you.

Cheers!