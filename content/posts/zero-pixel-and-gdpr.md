---
title: Doorbell - Tracking Pageviews without Cookies while Complying with GDPR
date: 2026-07-17
excerpt: How am I tracking my pageviews without cookies while complying with GDPR? That's actually quite interesting story. Sit around and listen.
---


## Doorbell: Tracking Pageviews without Cookies while Complying with GDPR

![doorbell - GDPR compliant anonyomus analytics](/assets/doorbell.png)

### How am I tracking my pageviews without cookies while complying with GDPR? That's actually quite interesting.
I work my portfolio pretty extensively and put a lot of effort into since it's my selling and professional leverage. Out there, I ran into a necessity of tracing pageview analytics, but I have a few strict restrictions:
- I do not use any .js anywhere in the whole site.
- I do not introduce any third-party tooling.

At this point, I really wanted to know the "heatmap" of the site - what is being watched, by whom, and when.

### The GDPR "Hole"
I drafted a quite explicit data-shape and decided to run it against AI to reveal the holes:
**AI**: Your majesty, you lost sight of GDPR in your design. But I am most helpful and will provide you with a solution without introducing any .js.
**Me**: Nah bro, I would drop the 'heatmap' entirely rather than introduce a 'cookie popup' on a website which is as flat as one can be. Being a System Architect, I don't blur the lines - I respect the constraints.
**AI**: You hit the nail flat on the head. But you actually can achieve your initial vision without a popup, all while complying with GDPR. Keep the pageview logging anonymous.

### That actually spinned another set of gears in my head and resulted in `doorbell`.
Think about it this way: you are sitting in a mansion with a variety of entrance doors. When one of the doorbells chimes, you have absolutely no idea who is standing behind it, but you are well aware of the door itself.

To keep the pageview data anonymous and useful at the same time, I followed a few rules of thumb on what should NOT be stored: 
- IP Addresses.
- User-Agents.
- Detailed Geolocation.
- Session or Fingerprint Hashes.
- Any unique key composition that can identify one request among others.

For my "portfolio pages heatmap," I settled on a flat data-shape that satisfies all my needs:

```json
{
    "page_path": "string",
    "referrer_host": "string",
    "country_code": "string",
    "device_type": "string",
    "hit_date": "date"
}
```

### The Architecture: "Zero-Pixel" & Supabase
I quickly settled on the "Zero-Pixel" pattern. This is an industry standard: instead of composing a tracking payload on the client-side, you make the client download a 1x1 pixel image, and all the necessary data is tracked by the backend from the request properties.

For data storage, I host my pet projects with Supabase on their free tier. It is more than enough, and I am deeply happy with them.
But something still had to accept the request and pack the zero-pixel back.
My portfolio has no backend, and I didn't want to couple it with one.
AWS Lambda with a hard expense cap against DDoS? Okay-ish, but that means a $1 per month billing hassle and adds +1 platform to track.

That is when I found out that Supabase actually supports Edge Functions. This is their serverless solution, with only one catch: it only supports Deno under TypeScript.
Deno is a modern JavaScript runtime - think Node.js, but a bit different.
That flew fine by me, but as you will see, it eventually bit me a bit in my lower back.
The massive leverage of keeping it all in the same ecosystem is that instead of creating and tracking a dedicated service account, I can use Supabase's built-in system-reserved variables out of the box.
So I happilly "dropped all my eggs in a single basket" and it was absolutely the correct approach here.

### Solution Diagram:


```text
[ Browser ] 
        │
        │ (Zero-JS <img> request)
        ▼
┌────────────────────────────────────────────────────────┐
│               SUPABASE ECOSYSTEM                       │
│                                                        │
│   [ Edge Function ] ──> [ Local GeoIP DB ]             │
│          │             (Instant offline IP lookup)     │
│          │                                             │
│          │ (Uses built-in, secure service role token)  │
│          ▼                                             │
│   [ Database ] (Flat, anonymous schema log)            │
│                                                        │
└────────────────────────────────────────────────────────┘
```


### The GeoIP Hurdle
The biggest problem overall was resolving the country_code value.
My initial design utilized a third-party API (ip-api.com), which legally classifies as "sharing personal data" under GDPR.
To stay fully compliant, I had to resolve the country code from the raw IP directly in memory, right inside the serverless function.
The industry standard is typically done using a very lightweight, local binary database, like a .mmdb file, to resolve geo data offline.
This is where the TypeScript-only constraint of Supabase Edge Functions bit me.

If I wanted to introduce additional binary files directly into the Function folder, I would have to switch to the Supabase CLI. While that is not a massive hassle, it requires setting up a dedicated CI/CD pipeline and a dedicated repository - which is the definition of "engineering ahead of yourself" at this stage.
So, what did I actually do? I put the .mmdb database directly into Supabase Storage and fetched it into my Function on cold start.
Yes, fetching it is not completely optimal, but pragmatically, it is a great trade-off for what I wanted to achieve.
All the data bandwidth stays within a single ecosystem and does not count toward my public egress limits.
And besides, the entire analytics processing runs non-blockingly, so it never affects the load times for the client.

### Takeaways
- `doorbell` is a beautiful addition to my existing collection of "no-dependency" products, on par with `halepa` and `slim-jim`. I will introduce it as a stand-alone solution in very nearby future 
- GDPR compliance is an architectural layout. Especially if you are operating in the EU, familiarize yourself with it rather than ignoring it.  
- You do not have to show a cookie popup. If you design your data boundaries properly, you can completely avoid the popup zoo.
- Supabase is a highly capable platform for running lightweight, coupled microservices.
- Third-party tools are not "better by default." Building it yourself often yields a cleaner, more robust system.

Ain't that nice?