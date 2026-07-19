---
title: doorbell - release v1.0
date: 2026-07-19
excerpt: What was initially designed as a quick feature to my personal portfolio grew up into quite a robust standalone solution for tracking anonymous pageview data while introducing zero JS to the client-side application for a whopping $0 per month.
---

## I am happy to announce the release of `doorbell` v1.0.

![doorbell release illustration](/assets/doorbell-release/release-illustration.png)

What was initially designed as a quick feature to my personal portfolio grew up into quite a robust standalone solution for tracking anonymous pageview data while introducing zero JS to the client-side application for a whopping $0 per month. As the development came into an active stage, the decision was made to utilize the Supabase platform to its fullest.

The starting point was me realizing that I need to track a heatmap of pageviews for my personal portfolio. But I had quite some limitations with existing constraints:
*   Portfolio does not have any client-side JS running and none shall be introduced.
*   Being located in the EU - I have to comply with GDPR and, tied with the previous bullet, should gather anonymous data exclusively.
*   Keep the solution cost-free while utilizing as much as possible from the Supabase platform.

## The Illusion of Simplicity

Easy-peasy. I just introduce a very basic implementation of the "zero-pixel" pattern (one simply decalares an `<img>` tag with source pointing to API which returns 1x1 transparent image while processing the request data) and handle client requests in some serverless function.

![20 minutes adventure](/assets/doorbell-release/20-minute-adventure.jpg)
*Me prompting AI Chatbot about initial `doorbell` design*

Initially, I had absolutely no preference regarding where the function will be stored. But since my pet project DB is located at Supabase - it made perfect sense to spin it up there. 

I will go a little further and give a brief description of the platform.
Supabase is a BaaS (Backend-as-a-Service) whose core implementations are:
*   **PostgreSQL DB** (powered by PostREST and GraphQL out of the box!).
*   **Blob Storage**.
*   **Edge Functions** (Deno + TypeScript).
*   **Built-in Authentication**.

The only "trick" was that Edge Functions are supported by the Deno runtime with TypeScript syntax. For me, it was a bit of a learning curve. Deno is a JavaScript runtime which, among other things, allows resolving dependencies by direct URL. But what I found incredibly awesome is how well-plumbed everything is if you navigate inside of the platform.

## The Scramble

I think it is a perfect time to introduce the final product diagram to you and explain the trade-offs which led to such a design (which is most definitely ***not*** a "happy 20 minutes adventure")

```text
+-------------------------------------------------------------------+
|                              USER                                 |
|-------------------------------------------------------------------|
|                                                                   |
|   [ Client Browser ] (Visitor on your portfolio)                  |
|               |                                                   |
|               | 1. GET request for 1x1 image                      |
|               |    (Headers: x-real-ip, user-agent, referer)      |
|               |                                                   |
+---------------|---------------------------------------------------+
                v
+===================================================================+
|                        SUPABASE PLATFORM                          |
|===================================================================|
|                                                                   |
|  +-------------------------------------------------------------+  |
|  |             Supabase Edge Function ('doorbell')             |  |
|  |-------------------------------------------------------------|  |
|  |  2. Parse path & device type, check for bots.               |  |
|  |  3. Connect directly via 'postgres' driver pooler URL.      |  |
|  |                                                             |  |
|  |  4. Execute GeoIP Query (sql`SELECT...`)                    |  |
|  |        |                                                    |  |
|  |        | (Fast read via GiST index)                         |  |
|  |        v                                                    |  |
|  |  [ Database Read ] ===> Resolves "NL", "US", or "XX"        |  |
|  |        |                                                    |  |
|  |        +===========#= Split Execution Paths ===========+    |  |
|  |                    |                                   |    |  |
|  | (Sync Core Thread) |                (Async Background) |    |  |
|  |                    v                                   |    |  |
|  |          +-------------------+                         v    |  |
|  |          | 5. Return 1x1 PNG |         +-----------------+  |  |
|  |          |    immediately to |         | 6. EdgeRuntime. |  |  |
|  |          |    Client Browser |         |    waitUntil()  |  |  |
|  |          +-------------------+         +--------|--------+  |  |
|  |                                                 |           |  |
|  |                                                 v           |  |
|  |                                        +-----------------+  |  |
|  |                                        | 7. INSERT log   |  |  |
|  |                                        |    row payload  |  |  |
|  |                                        +--------|--------+  |  |
|  +-------------------|-----------------------------|-----------+  |
|                      |                             |              |
|                      |          (Background write) |              |
|                      v                             v              |
|  +-------------------------------------------------------------+  |
|  |                Supabase PostgreSQL Database                 |  |
|  |-------------------------------------------------------------|  |
|  |  [Table: geoip_country_blocks]   [Table: doorbell_pageviews]|  |
|  |  - network (cidr)                - page_path                |  |
|  |  - country_code (bpchar)         - country_code             |  |
|  |                                  - device_type              |  |
|  |                                  - referrer_host            |  |
|  |                                  - hit_date                 |  |
|  +-------------------------------------------------------------+  |
|                      ^                                            |
+======================|============================================+
                       |
                       | 8. TRUNCATE table
                       | 9. Bulk INSERT chunked SQL files
                       |
+-------------------------------------------------------------------+
|               GitHub Actions CI/CD (Deploy + Weekly Cron)         |
|-------------------------------------------------------------------|
|  - cURL: sapics/ip-location-db (IPv4+IPv6 CIDR format)            |
|  - split/awk: Slice 394k rows into 50k-line chunks                |
|  - supabase CLI: Push raw SQL statements to bypass 413 limits     |
+-------------------------------------------------------------------+
```

It all really boiled down to finding a way to resolve the Country Code from a raw IP in memory. How did I come up with this problem? 

Simple: The very first implementation was making an async request to a 3rd party GeoIP API. But routing a visitor's raw IP to an external cloud processor is not GDPR compliant. Quick research of the problem pointed out that it is a standard problem, and it is resolved by querying a lightweight data-specific DB which usually has an `.mmdb` extension. Since it is a single-task type DB - the lookup in there is incredibly fast and efficient, while the DB itself weighs 4 to 7MB. So I put `user-country.mmdb` into a bucket and fetched it with each cold start. That was fine for the MVP.

But for my specific case - every start is pretty much a cold start, so we were talking gigabytes in bandwidth per month for such a simple operation.

**Pivot: *Ok, for v1.0 I will just bundle the .mmdb into the Edge Function and call it directly* **

Time was to pay up for the assumption.  
`413 - bundle size exceeds limit`

Oh, I was not expecting that. I was sure that the bundle size limit was 20MB - but I assume the bundling engine computes absolute compilation weights, meaning my binary files breached the max edge function allocation.

> **AI:** "Oh well, it was worth a shot. Let us revert the changes and just fetch 7MB on every request. We most likely will stay within monthly limits..."
> 
> **Me:** "Wait wait wait. That does not sound like a 'No' No. We have a whole PostgreSQL database for our pleasure. Let's just extract the whole .mmdb into a dedicated table and query it!"

And that was actually a great idea which I still am proud of. By storing the subnets using Postgres's native network (`cidr`) data type paired with a GiST index, we can execute lightning-fast IP lookups via containment operators (`network >> client_ip::inet`) without any file-system overhead.

But, remember I told you "Supabase is super comfortable to use as long as you stay INSIDE"? Yep, you guessed it right: as soon as I wrote a DB update stage into my CI/CD - I slammed into every gateway payload restriction imaginable, resolving which took a good 80% of development time. The Supabase Management API queries endpoint enforces strict limits on raw HTTP payload size per request, yielding timeouts or 413 responses when uploading massive SQL scripts.

But eventually, I found a working solution that operates well within Supabase limits. In short: I use a database connection string with a Postgres client instead of the Supabase CLI, and use Unix `split` and text-parsing `awk` to chunk the raw CSV rows into smaller, manageable transaction packages of 50K rows to stream them directly into the database.

## The Cron

GeoIP subnets shift constantly and data is being updated on a daily basis. I had to follow and make it automatic, and once per week will be fine by me. First of all - I decided not to introduce additional tooling for a Cron. Luckily - even with the existing ones, I had a choice to make:

1.  **Postgres-based cron job (`pg_cron`):** A big benefit of this approach is that everything is happening right inside of the same DB where the data itself will be stored. We are talking absolutely no hassle with authentication. But I had to waive this approach since keeping data-fetching logic hidden in a database extension will become a "magic-trigger" right away, hurting long-term visibility.
2.  **GitHub Actions based cron job:** This is what I actually implemented. Yes, in the process I had an immersive headache and said some things to the chatbot that I regret, but the trigger is very well on the surface and is maintainable.

## The Engine

Funny. This is the heart of the solution, but I have absolutely nothing interesting happening out there. Let me translate: Edge Function behavior was incredibly predictable and very well documented. Such functionality as aggregating request header-data, filtering out bots using regex, and putting the payload into the DB was as trivial as it sounds. This is an incredible strength of the platform.

And just look at this list of predefined system variables available in the runtime out of the box.

![available supabae secrets](/assets/doorbell-release/supabase-secrets.png)
*All these are available in your runtime out of the box*

I didn't have to create a single additional secret or authentication resource.

## The Test

I can't be objective here. Test coverage is not my strength, but I sure recognize the necessity of them. Thankfully, Deno features an incredibly clean, native unit testing engine.

The challenges which I faced at this stage were rather "testing serverless functions" in general - mocking the database connection cleanly without blatantly hacking the code was a challenge. Because the `npm:postgres` driver creates a unique callable function proxy for tagged template literals (like `sql`SELECT...`), standard object stubs cannot intercept queries directly. 

The workaround required extracting the internal execution prototype framework from a synchronous dummy expression (`Object.getPrototypeOf(sql`SELECT 1`)`) and using TypeScript's `Parameters<...>` utility to stub the underlying `.then` promise resolution method. This lets us intercept the async thread completely in-memory, inject static mock data arrays (returning `{ country_code: "NL " }`), and preserve type safety without writing a single `any` keyword. But I am pretty happy with the result, and future development is safely covered by a fail-fast gateway step in the pipeline.

## Conclusion

As soon as CI/CD with a test stage gave me "the green," I wanted to cry. This whole development process was quite a nice challenge which - despite the physical and mental drain - was incredibly enjoyable and gave me experience which I will carry with me through my career.

Talking about the product, `doorbell`, itself? Yes, it is an incredibly useful solution. Look at what I get with it:

![portfolio heatmap](/assets/doorbell-release/supabase-db.png)
*Heatmap of portfolio visitors*

Being cloud-native and packed as "plug-and-play" in your project - is just a great style. It is incredibly lightweight, follows a "zero-dependency" approach, and will be a great addition to my similar solutions: `halepa` and `slim-jim`. Absolutely no client-side configuration! Just declare `<img>` in the footer. A $0 price tag of use is a cherry on top.

Now, if you excuse me, I need to have some sleep.
