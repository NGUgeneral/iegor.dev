---
title: headsntails - distributed and decoupled infrastructure
date: 2026-07-06
excerpt: A distributed and decoupled infrastructure which implements Feature Flags functionality with a all around gRPC connection twist.
---

![It ain't much, but it's honest work](/assets/it-aint-much.png)

🔗 [`headsntails`](https://github.com/NGUgeneral/headsntails-platform)

# Description 

Deacoupled distributed infrastructure system which implements Feature Flags functionality.
Can be Plugged in as a feature or deployed as a standalone ecosystem and scaled up all the way to be a SaaS.

---

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

---

## The Roadmap:

| Phase | Milestone | Core Focus | Architecture Impact | Status |
| :--- | :--- | :--- | :--- | :--- |
| **v0.1** | **Container Monolith Base** | Orchestrated REST Core | Edge Ingress routing, multi-language container isolation | **Released** |
| **v0.11** | **Renaming** | Swap "Flagship" to `headsntails` | The project is positioned rather as architectural boilerplate. Naming should be distanced from Feature Flags | **Released** |
| **v0.15** | **Test Coverage** | Full Test coverage + E2E | Support stable product evolution be ensuring compability with existing functionality | **Released** |
| **v0.2** | **Source of Truth & Hydration** | Reliable State Handling | Write-Through pattern to PostgreSQL; ultra-fast reads from Redis | **Released** |
| **v0.3** | **Sidecar Latency Optimization** | gRPC Communication Layer | Migrate inter-service checks to gRPC to eliminate HTTP/1.1 HoL blocking | **Released** |
| **v0.4** | **High-Perf Edge Layer** | Global gRPC Ingress | Transition public edge routing to utilize Protocol Buffers & HTTP/2 streaming | *In Progress* |
| **v0.5** | **Advanced Targeting Engine**| Contextual Flag Evaluation | Abstract rule-matching evaluation engines beyond simple primitives | *Planned* |
| **v0.6** | **Distributed Event Bus** | Real-Time Cache Sync | Integrate RabbitMQ/Kafka to synchronize cache states across cross-region nodes | *Planned* |
| **v0.7** | **Cloud-Native Scale** | Infrastructure as Code | Multi-AZ AWS ECS Fargate deployment automated via Terraform | *Planned* |
