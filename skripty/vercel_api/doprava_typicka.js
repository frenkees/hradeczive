// Typická doprava podle hodiny: {n, s: {"lat,lon,délka": [48 hodnot jamFactor×10 nebo null]}}, spočítaná sběračem (skripty/doprava_sber.mjs,
// GitHub Actions) do větve doprava-data. Funkce jen přeposílá veřejný soubor s hodinovou cache; bez dat vrací prázdný objekt.
const ZDROJ = process.env.DOPRAVA_TYPICKA_URL || 'https://raw.githubusercontent.com/frenkees/hradeczive/doprava-data/typicka.json';
const h = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, s-maxage=3600, stale-while-revalidate=7200' };
export async function GET() {
  try {
    const r = await fetch(ZDROJ, { signal: AbortSignal.timeout(10000) });
    if (!r.ok) throw new Error(String(r.status));
    return new Response(await r.text(), { headers: h });
  } catch { return new Response('{"n":0,"s":{}}', { headers: { ...h, 'cache-control': 'public, s-maxage=300' } }); }
}
