// Since this is just a code-snippet, we disable type checking for
// this file to avoid any potential issues with type errors.
// @ts-nocheck

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"
import { Reader } from "npm:maxmind@4.3.15"
import { Buffer } from "node:buffer"

const PIXEL_BYTES = new Uint8Array([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
  0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
  0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89, 0x00, 0x00, 0x00,
  0x0a, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9c, 0x63, 0x00, 0x01, 0x00, 0x00,
  0x05, 0x00, 0x01, 0x0d, 0x0a, 0x2d, 0xb4, 0x00, 0x00, 0x00, 0x00, 0x49,
  0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82
]);

let readerPromise: Promise<Reader> | null = null;

serve(async (req) => {
  const pixelResponse = new Response(PIXEL_BYTES, {
    headers: {
      "Content-Type": "image/png",
      "Cache-Control": "no-store, max-age=0",
      "Access-Control-Allow-Origin": "*",
    },
  });

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabaseClient = createClient(supabaseUrl, supabaseServiceKey);

    const clientIp = req.headers.get("x-real-ip") || req.headers.get("cf-connecting-ip");
    let countryCode = "XX";

    if (clientIp && clientIp !== "127.0.0.1" && clientIp !== "::1") {
      try {
        if (!readerPromise) {
          readerPromise = (async () => {
            const { data, error } = await supabaseClient.storage
              .from("assets")
              .download("user-country.mmdb");

            if (error) throw error;

            const arrayBuffer = await data.arrayBuffer();
            const nodeBuffer = Buffer.from(new Uint8Array(arrayBuffer));
            return new Reader(nodeBuffer);
          })();
        }

        const readerInstance = await readerPromise;
        const geoData = readerInstance.get(clientIp);
        if (geoData && geoData.country_code) {
          countryCode = geoData.country_code;
        }
      } catch (geoErr) {
        console.error("[GeoIP] Resolution failed:", geoErr.message);
      }
    }

    const url = new URL(req.url);
    let pagePath = url.searchParams.get("path");
    const refererHeader = req.headers.get("referer") || "";

    if (!pagePath) {
      if (refererHeader) {
        try {
          pagePath = new URL(refererHeader).pathname;
        } catch {
          pagePath = "Malformed";
        }
      } else {
        pagePath = "Direct";
      }
    }

    const userAgent = req.headers.get("user-agent") || "";
    const deviceType = /Mobi|Android|iPhone/i.test(userAgent) ? "Mobile" : "Desktop";
    const isBot = /bot|crawler|spider|copt|mediapartners/i.test(userAgent);
    
    let referrerHost = "Bot";

    if (!isBot && pagePath !== "unknown") {
      referrerHost = "Direct";
      if (refererHeader) {
        try {
          const parsedHost = new URL(refererHeader).hostname;
          if (parsedHost === "iegor.dev" || parsedHost === "localhost" || parsedHost === "127.0.0.1") {
            referrerHost = "Direct";
          } else {
            referrerHost = parsedHost;
          }
        } catch {
          referrerHost = "Malformed";
        }
      }
    }

    supabaseClient
      .from("doorbell_pageviews")
      .insert([
        {
          page_path: pagePath,
          country_code: countryCode,
          device_type: deviceType,
          referrer_host: referrerHost,
          hit_date: new Date().toISOString().split("T")[0],
        }
      ])
      .then(({ error: dbError }) => {
        if (dbError) {
          console.error("Doorbell DB Write Error:", dbError.message);
        }
      })
      .catch((err) => {
        console.error("Doorbell DB Connection Error:", err.message);
      });

    return pixelResponse;

  } catch (err) {
    console.error("Doorbell Ingestion Error:", err.message);
    return pixelResponse;
  }
})