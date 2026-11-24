// Letadla nad městem pro mapu (volba "letadla" v mesto.json): ADS-B z adsb.lol (ODbL, bez klíče).
// Vercel funkce (Node, ESM) nahrazuje Cloudflare funkci functions/api/flights.js, kterou Vercel nespouští.
// Prohlížeč se na adsb.lol přímo nedostane (CORS), proto se ptá sem: dotaz lamin, lamax, lomin, lomax (rámeček mapy);
// odpověď {ac: [...]} má pro všechny návštěvníky společnou cache (15 s). Posílají se jen údaje, které mapa kreslí.
const R_NM = 35;                                            // poloměr dotazu v námořních mílích (~65 km kolem středu mapy)
const POLE = ['hex', 'flight', 'r', 't', 'desc', 'category', 'lat', 'lon', 'alt_baro', 'alt_geom', 'gs', 'track', 'mag_heading', 'baro_rate', 'squawk', 'dbFlags'];
const hlavicky = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, s-maxage=15, stale-while-revalidate=30' };
const pamet = new Map();                                    // klíč zdroje -> {kdy, telo}: druhá pojistka vedle CDN cache

export function zjednoduseni(d) {
  const ac = [];
  for (const a of d.ac || []) {
    if (typeof a.lat !== 'number' || typeof a.lon !== 'number') continue;
    const o = {};
    for (const k of POLE) if (a[k] != null) o[k] = typeof a[k] === 'string' ? a[k].trim() : a[k];
    ac.push(o);
  }
  return { ac, t: d.now || Date.now() };
}

export async function GET(request) {
  const q = new URL(request.url).searchParams, n = (k) => Number.parseFloat(q.get(k));
  const [la0, la1, lo0, lo1] = ['lamin', 'lamax', 'lomin', 'lomax'].map(n);
  if (![la0, la1, lo0, lo1].every(Number.isFinite)) return new Response('{"ac":[]}', { status: 400, headers: { 'content-type': 'application/json' } });
  const lat = ((la0 + la1) / 2).toFixed(2), lon = ((lo0 + lo1) / 2).toFixed(2), src = `https://api.adsb.lol/v2/point/${lat}/${lon}/${R_NM}`;
  const p = pamet.get(src);
  if (p && Date.now() - p.kdy < 12e3) return new Response(p.telo, { headers: hlavicky });
  try {
    const r = await fetch(src, { headers: { 'user-agent': 'hradeczive-letadla' }, signal: AbortSignal.timeout(8000) });
    if (!r.ok) throw new Error('adsb.lol ' + r.status);
    const telo = JSON.stringify(zjednoduseni(await r.json()));
    pamet.set(src, { kdy: Date.now(), telo });
    return new Response(telo, { headers: hlavicky });
  } catch (e) {
    if (p) return new Response(p.telo, { headers: hlavicky });   // starší odpověď je lepší než žádná
    return new Response('{"ac":[]}', { status: 502, headers: { ...hlavicky, 'cache-control': 'no-store' } });
  }
}
