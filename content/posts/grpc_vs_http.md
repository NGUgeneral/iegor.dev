---
title: gRPC vs HTTP high-load showdown
date: 2026-07-10
excerpt: While introducing v0.3 of `headsntails` I ran comprehensive benchmark of gRPC vs HTTP intranet communication. The results prooved to be pretty insightful and I am happy to share them. 
---

![HTTP vs gRPC](/assets/http-vs-grpc/http_vs_grpc.png)

I never thought about gRPC too much, just "yeah, it's times faster compared to HTTP, just have some configuration overhead". That's true, but running a comprehensive benchmark on my own system gave a bit more nuanced ground to the initial statement and, quite frankly, was interesting.

**Problem**: Public endpoint in [`headsntails-core`](https://github.com/NGUgeneral/headsntails-core) service validates each request against cart service [`rate-limiter`](https://github.com/NGUgeneral/rate-limiter).
The initial implementation allowed usage of HTTP connection as long as we are talking intranet. But it was a very obvious and very critical bottleneck of the whole system, marking it as an early major milestone in the product roadmap. v0.3 was dedicated to replace existing HTTP communication with gRPC.

**Solution**: I didn't replace connection, but complement it at this stage, so the protocol can be switched from the system configuration (RATE_LIMITER_USE_GRPC boolean flag in .env). For the high-load and benchmark I have introduced [Fortio](https://github.com/fortio/fortio#fortio) service to the existing system, so I can stress-test the service from both an external and internal endpoint.

**Twist**: I never thought about it too much, just accepted it as "gRPC is times faster, just have configuration overhead". But this time I wanted to "touch the meat" and look what exactly I am winning with gRPC.

**Methodology**: I have interacted with a public endpoint (`/api/v1/flag/get`) sending max Queries per Second with 1, 5, 50 and 100 parallel threads for 20 seconds. Did that with gRPC and HTTP configurations separately.

**Results**: you can familiarize yourself with the resulting data [here](https://gist.github.com/NGUgeneral/ea6997b8ec9cee786e35f629f9fbb79c).

**Takeaway**: yes it is fair to say that "gRPC is times faster" compared to HTTP, very much in a low concurrency environment. But:

1. gRPC IS times faster compared to HTTP, especially in low concurrent environment, where HTTP operates a single digit number of connections.
This diagram represents it perfectly.
![QPS comparison](/assets/http-vs-grpc/http_vs_grpc_diagram_qps.png)

2. Under heavy concurrency gRPC faces the wall of the system capabilities itself.
This is very well illustrated in the Average Latency Time diagram.
![Avg. Lat (ms)](/assets/http-vs-grpc/http_vs_grpc_diagram_avg_lat.png)

3. **gRPC "performance domination" compared to HTTP is not linear**. 

4. HTTP does not crumble in pieces under high-load peaks. On contrary - it gets very close to gRPC productivity. But the reason for this, despite all the open connections, is that the communication bottleneck has been transformed into computation bottleneck. This can be clearly seen on both diagrams, for both protocols. The difference is purely serialization based.

5. HTTP still IS a very robust communication protocol.

**So should you use gRPC in every case possible? Sure not. HTTP is a very robust protocol which works incredibly well, even under the high level of pressure. But it will be a bottleneck of your system and if you have a high frequency communication channel - gRPC is most likely more applicable.**