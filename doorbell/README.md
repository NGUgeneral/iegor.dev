Doorbell - is a serverless function, which is responsible to store anonymous, GDPR compliant, pageview data.
This folder stores the DB-seeding schemas and implementations for different cloud platforms.
user-country.mmdb is provided by https://github.com/sapics/ip-location-db

TODO: move it into a dedicated repo with it's own CI/CD.
- fetch .mmdb in a supabase cron job;
- add the .mmdb into Deno filesystem, right next to Edge Function resolver, so the db will be read directly instead of being fetched on every cold start from the storage; 