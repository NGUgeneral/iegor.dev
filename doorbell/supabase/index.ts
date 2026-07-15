// @ts-ignore
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const PIXEL_BYTES = new Uint8Array([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
  0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
  0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89, 0x00, 0x00, 0x00,
  0x0a, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9c, 0x63, 0x00, 0x01, 0x00, 0x00,
  0x05, 0x00, 0x01, 0x0d, 0x0a, 0x2d, 0xb4, 0x00, 0x00, 0x00, 0x00, 0x49,
  0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82
]);

// @ts-ignore
Deno.serve(async (req) => {
  const url = new URL(req.url);
  const path = url.searchParams.get("path") || "unknown";
  const userAgent = req.headers.get("user-agent") || "";
  const refererHeader = req.headers.get("referer") || "";

  const isBot = /bot|crawler|spider|copt|mediapartners/i.test(userAgent);

  if (!isBot && path !== "unknown") {
    let referrerHost = "Direct";
    if (refererHeader) {
      try {
        referrerHost = new URL(refererHeader).hostname;
      } catch {
        referrerHost = "Malformed";
      }
    }

    // 1. EXTRACT CLIENT IP Safely
    const clientIp = req.headers.get("cf-connecting-ip") || 
                     req.headers.get("x-forwarded-for")?.split(",")[0].trim() || 
                     "";

    // 2. GEOLOCATE COUNTRY VIA FREE API (Async / Non-blocking)
    let country = "Unknown";
    if (clientIp && clientIp !== "127.0.0.1") {
      try {
        const geoResponse = await fetch(`http://ip-api.com/json/${clientIp}?fields=countryCode`);
        if (geoResponse.ok) {
          const geoData = await geoResponse.json();
          country = geoData.countryCode || "Unknown";
        }
      } catch {
        country = "Error";
      }
    }

    let deviceCategory = "Desktop";
    if (/Mobi|Android|iPhone|iPad/i.test(userAgent)) {
      deviceCategory = "Mobile";
    }

    const today = new Date().toISOString().split('T')[0];

    const supabase = createClient(
      // @ts-ignore
      Deno.env.get('SUPABASE_URL') ?? '',
      // @ts-ignore
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    // 3. PERSIST THE ANONYMIZED ROW
    supabase.from('doorbell_pageviews').insert([{
      page_path: path,
      referrer_host: referrerHost,
      country_code: country,
      device_type: deviceCategory,
      hit_date: today
    }]).then();
  }

  return new Response(PIXEL_BYTES, {
    headers: {
      "Content-Type": "image/png",
      "Cache-Control": "no-cache, no-store, must-revalidate",
    },
  });
});