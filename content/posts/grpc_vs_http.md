---
title: gRPC vs HTTP high-load showdown
date: 2026-07-10
excerpt: While introducing v0.3 of `headsntails` I ran comprehensive benchmark of gRPC vs HTTP intranet communication. The results prooved to be pretty insightful and I am happy to share them. 
---

##The gRPC Myth: What Actually Happens to HTTP at 100 Concurrent Threads?

![HTTP vs gRPC](/assets/http-vs-grpc/http_vs_grpc.png)

I used to buy into the generic developer hype: *"gRPC is 10x faster than HTTP, it just has some configuration overhead."* 

While technically true on paper, running a comprehensive stress test on my own system revealed a much more pragmatic reality. 

When building my Architecture-Boilerplate [`headsntails`](https://github.com/NGUgeneral/headsntails-core) (Golang based infrastructure which in its current state serves as plug-and-play Feature Flag Service and is able to scale up to SaaS out of the box), our public endpoint validates every incoming request against a cart [`rate-limiter`](https://github.com/NGUgeneral/rate-limiter) service.

Originally, this intranet communication ran over standard HTTP. Recognizing this as a potential bottleneck, I set out to replace (and benchmark) it with gRPC in v0.3. 

Rather than blindly ripping and replacing, I implemented a simple configuration flag (`RATE_LIMITER_USE_GRPC=true|false`) and spun up a [Fortio](https://github.com/fortio/fortio#fortio) load-testing container to stress-test both protocols under the exact same conditions.

Here is what happened when I pushed max QPS across 1 to 100 parallel threads - and why the results changed my perspective on gRPC.

###The Benchmark Setup 
To run a clean stress test, I needed a tool that could generate predictable, high-concurrency traffic without introducing its own client-side performance bottlenecks.

I chose Fortio, an open-source load-testing engine originally built for Istio that natively supports both HTTP and gRPC protocols at high QPS. Rather than running Fortio from my local terminal, I deployed it as a standalone container directly inside the Docker Compose network. This gave Fortio direct intranet access to both gRPC and HTTP interfaces on the `headsntails-core` public endpoint (`/api/v1/flag/get`).

The endpoint itself evaluates an incoming request by performing an internal rate-limit check against the `rate-limiter` service. Using the `RATE_LIMITER_USE_GRPC` flag, I swapped the internal transport layer between HTTP and gRPC without touching the underlying business logic.

I then hit the public endpoint with maximum QPS across four distinct concurrency levels for 20 seconds each:
* **1 Parallel Thread**: Establishing the baseline for low-concurrency, single-connection throughput.
* **5 Parallel Threads**: Simulating light, realistic concurrent service requests.
* **50 Parallel Threads**: Pushing the transport layer into moderate contention.
* **100 Parallel Threads**: Saturating the system to force a resource wall and isolate the bottleneck.

The detailed logs from running the benchmarks are available here: [Github Gist](https://gist.github.com/NGUgeneral/ea6997b8ec9cee786e35f629f9fbb79c).

###The Illusion at Low Concurrency
![QPS comparison](/assets/http-vs-grpc/http_vs_grpc_diagram_qps.png)
At 1 to 5 threads, the hype held up completely. gRPC absolutely destroyed HTTP. It felt like a rabbit racing a turtle... 

###The Concurrency Wall: When Communication Becomes Computation
When I cranked the system up to 50 and 100 concurrent threads, I honestly expected HTTP to absolutely spin its wheels in mud. But to my surprise HTTP didn't crumble into pieces and the performance gap flattened drastically. Its throughput curve began matching gRPC's trajectory.

Why?
Because at peak concurrency, the network protocol stopped being the primary bottleneck. **The system hit a physical resource wall where the communication bottleneck transformed into a CPU/computation bottleneck**. Both protocols were left standing in line waiting for the exact same CPU clock cycles.
![Avg. Lat (ms)](/assets/http-vs-grpc/http_vs_grpc_diagram_avg_lat.png)
At this threshold, the "gRPC performance domination" isn't linear. The remaining delta wasn't gRPC's magic transport layer - it was purely the serialization tax of parsing JSON string arrays versus binary Protobuf payloads.

###Pragmatic Engineering Takeaways
* **HTTP is a reliable workhorse**: Don't let microservice dogmatists convince you HTTP crumbles under load. It remains remarkably resilient.
* **Ultra-Low Latency**: gRPC got true multiplexing out of the box and communicates extremely fast without the need of a “cold-start” (more precisely: the cold-start is blazing fast compared to HTTP).
* **gRPC shines in high-frequency serialization**: If your bottleneck is raw CPU cycles spent parsing heavy JSON payloads, gRPC is worth every line of configuration.
* **Avoid premature gRPC complexity**: If your system isn't running into serialization CPU bounds, adding Protobuf compilation pipelines and gRPC setup overhead is pure over-engineering.

Stay pragmatic and be sure what you’re implementing.