// Doprava pro mapu: aktuální rychlost a míra zácpy na ulicích města z HERE Traffic API v7 (/flow).
// Vercel funkce (Node, ESM). Tajné: HERE_API_KEY (v Vercelu jako proměnná prostředí, nikdy v repu ani v prohlížeči).
// Odpověď {t, s: {"lat,lon,délka": [jamFactor×10, rychlost v % volné rychlosti]}} má pro všechny návštěvníky společnou cache (10 min),
// aby se HERE ptal nejvýš ~6× za hodinu bez ohledu na návštěvnost (kvóta Traffic: ~5 000 dotazů za měsíc zdarma).
const BBOX = '15.785,50.175,15.885,50.245';                // west,south,east,north: celé město
const TTL = 600e3;
let pamet = null;                                           // {kdy, telo} na instanci funkce: druhá pojistka vedle CDN cache
const hlavicky = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, s-maxage=600, stale-while-revalidate=300' };

export async function nactiProvoz(klic, fetchFn = fetch) {
  const r = await fetchFn(`https://data.traffic.hereapi.com/v7/flow?in=bbox:${BBOX}&locationReferencing=shape&apiKey=${encodeURIComponent(klic)}`,
    { headers: { 'user-agent': 'hradeczive-doprava' }, signal: AbortSignal.timeout(20000) });
  if (!r.ok) throw new Error('HERE ' + r.status);
  const d = await r.json(), s = {};
  for (const x of d.results || []) {
    const f = x.currentFlow, p = x.location?.shape?.links?.[0]?.points?.[0];
    if (!f || !p || typeof f.jamFactor !== 'number') continue;
    const ff = f.freeFlow || 0;
    s[`${p.lat.toFixed(5)},${p.lng.toFixed(5)},${Math.round(x.location.length || 0)}`] =
      [Math.round(f.jamFactor * 10), ff ? Math.round(100 * Math.min(1, (f.speed || 0) / ff)) : 100];
  }
  return { t: d.sourceUpdated || new Date().toISOString(), s };
}

// Návštěvníci HERE nevolají: poslední snímek stahuje jen GitHub Actions (skripty/doprava_sber.mjs, pevný rozvrh = pevná měsíční kvóta)
// do větve doprava-data (live.json); funkce ho jen přeposílá. nactiProvoz zůstává tady, protože ho sběrač importuje.
const ZDROJ = process.env.DOPRAVA_LIVE_URL || 'https://raw.githubusercontent.com/frenkees/hradeczive/doprava-data/live.json';
export async function GET() {
  if (!pamet || Date.now() - pamet.kdy > 120e3) {
    try {
      const r = await fetch(ZDROJ, { signal: AbortSignal.timeout(10000) });
      if (!r.ok) throw new Error(String(r.status));
      pamet = { kdy: Date.now(), telo: await r.text() };
    } catch (e) {
      if (!pamet) return new Response('{"s":{}}', { status: 502, headers: { ...hlavicky, 'cache-control': 'no-store' } });   // starší odpověď je lepší než žádná
    }
  }
  return new Response(pamet.telo, { headers: hlavicky });
}
