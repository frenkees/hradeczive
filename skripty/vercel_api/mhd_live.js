// Živá poloha a zpoždění vozidel MHD Hradec Králové pro mapu (doplněk mhd_live).
// Vercel funkce (Node, ESM). Zdroj: informační systém DPmHK (https://dpmhk.qrbus.me, veřejné JSON rozhraní webu dopravního podniku),
// záloha: zpracovaná mapa https://mapa.fcen.cz (stejná data). Odpověď má pro všechny návštěvníky společnou cache (~20 s),
// zdroj se tedy ptá nejvýš ~3× za minutu bez ohledu na návštěvnost.
// Z odpovědi se ukládá a posílá JEN: číslo vozidla, linka, poloha, směr, rychlost, stáří záznamu, zpoždění, číslo trasy. Jména řidičů, počty cestujících
// a další provozní údaje, které zdroj vrací, se zahazují hned tady (nikdy neopustí funkci).
const DPMHK = 'https://dpmhk.qrbus.me/index/getAllRtdVehicles';
const FCEN = 'https://mapa.fcen.cz/api/vehicle_data';
const BBOX = [50.15, 15.74, 50.27, 15.93];                  // jih, západ, sever, východ (s rezervou kolem mapy)
const STARE_S = 180;                                        // záznam starší než 3 min se zahodí (vozidlo bez signálu)
const D_MIN = -300, D_MAX = 3600;                           // rozumné zpoždění v s
const TTL = 15e3;
const DUCH_S = 15;                                          // záznam téhož vozu starší o víc než 15 s než jeho nejčerstvější sourozenec je zamrzlý „duch“
const hlavicky = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, s-maxage=20, stale-while-revalidate=40' };
let pamet = null;                                           // {kdy, telo}: druhá pojistka vedle CDN cache

const vBoxu = (la, lo) => la >= BBOX[0] && la <= BBOX[2] && lo >= BBOX[1] && lo <= BBOX[3];
const cele = (x) => Math.round(Number(x));
const praha = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Prague', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
function offsetPraha(ted) {                                 // posun pražského času proti UTC v ms (zdroj posílá místní čas s příponou „Z“)
  const p = Object.fromEntries(praha.formatToParts(new Date(ted)).map((q) => [q.type, q.value]));
  return Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour % 24, +p.minute, +p.second) - Math.floor(ted / 1000) * 1000;
}
// Zdroj vrací pro část vozů (~8 %) dva záznamy se stejným číslem vozidla: čerstvý a starší „duch“ (jiná poloha až stovky metrů, někdy jiná linka).
// Necháme jen nejčerstvější, jinak by se vůz na mapě přeskakoval mezi nimi.
function nejcerstvejsi(out) {
  const m = new Map();
  for (const v of out) { const o = m.get(v.id); if (!o || v.ag < o.ag) m.set(v.id, v); }
  return [...m.values()];
}

export function zDpmhk(d, ted = Date.now()) {
  const out = [], skup = new Map();
  for (const v of d.vehicles || []) {                       // záznamy podle čísla vozu; filtry (linka, oblast, stáří) až potom, jinak by zůstal starší „duch“
    if (!v.li) continue;
    const k = String(v.li); if (!skup.has(k)) skup.set(k, []); skup.get(k).push({ ...v, _t: Date.parse(v.l) });
  }
  const nej = [];
  for (const g of skup.values()) {
    const max = Math.max(...g.map((v) => v._t || 0)), zive = g.filter((v) => max - (v._t || 0) <= DUCH_S * 1000);   // starší záznam se zamrzlým časem je „duch“ předchozího spoje
    for (const v of zive) nej.push(zive.length > 1 ? { ...v, li: `${v.li}~${v.tn ?? v.rn ?? ''}` } : v);      // dva současně živé záznamy téhož čísla jsou dvě vozidla: samostatná id
  }
  for (const v of nej) {
    const ln = String(v.ln ?? '').trim();
    if (!ln || ln.toLowerCase() === 'x') continue;                // mimo linku / bez čísla vozidla
    const la = v.la / 1e5, lo = v.lo / 1e5, kdy = Date.parse(v.l) - offsetPraha(ted);
    if (!Number.isFinite(la) || !Number.isFinite(lo) || !vBoxu(la, lo)) continue;
    if (!Number.isFinite(kdy) || ted - kdy > STARE_S * 1000) continue;
    const ag = Math.max(0, Math.round((ted - kdy) / 1000));
    const dl = cele(v.d);
    if (!Number.isFinite(dl) || dl < D_MIN || dl > D_MAX) continue;
    out.push({ id: String(v.li), ln, la: +la.toFixed(5), lo: +lo.toFixed(5), az: cele(v.az) || 0, sp: Math.max(0, cele(v.s) || 0), ag, d: dl, rn: String(v.rn ?? '') });
  }
  return nejcerstvejsi(out);
}

export function zFcen(d, ted = Date.now()) {
  const out = [];
  for (const v of d.vehicles || []) {
    const ln = String(v.line ?? '').trim();
    if (!ln || ln.toLowerCase() === 'x' || !v.vehicle_id) continue;
    const la = Number(v.latitude), lo = Number(v.longitude), kdy = Date.parse(v.vehicle_time) - offsetPraha(ted);   // i zde je to pražský čas s příponou „Z“
    if (!Number.isFinite(la) || !Number.isFinite(lo) || !vBoxu(la, lo)) continue;
    if (Number.isFinite(kdy) && ted - kdy > STARE_S * 1000) continue;
    const ag = Number.isFinite(kdy) ? Math.max(0, Math.round((ted - kdy) / 1000)) : 0;
    const dl = cele(v.delay);
    if (!Number.isFinite(dl) || dl < D_MIN || dl > D_MAX) continue;
    out.push({ id: String(v.vehicle_id), ln, la: +la.toFixed(5), lo: +lo.toFixed(5), az: cele(v.azimuth) || 0, sp: Math.max(0, cele(v.speed) || 0), ag, d: dl, rn: String(v.route_number ?? '') });
  }
  return nejcerstvejsi(out);
}

export async function nactiVozidla(fetchFn = fetch) {
  const hlav = { 'user-agent': 'hradeczive-mhd (mapa hradeczive.cz)', accept: 'application/json' };
  try {
    const r = await fetchFn(DPMHK, { headers: hlav, signal: AbortSignal.timeout(8000) });
    if (!r.ok) throw new Error('DPmHK ' + r.status);
    const v = zDpmhk(await r.json());
    if (v.length) return { t: new Date().toISOString(), z: 'dpmhk', v };
  } catch (e) { /* zkusit zálohu */ }
  const r = await fetchFn(FCEN, { headers: hlav, signal: AbortSignal.timeout(8000) });
  if (!r.ok) throw new Error('fcen ' + r.status);
  return { t: new Date().toISOString(), z: 'fcen', v: zFcen(await r.json()) };
}

export async function GET() {
  if (!pamet || Date.now() - pamet.kdy > TTL) {
    try { pamet = { kdy: Date.now(), telo: JSON.stringify(await nactiVozidla()) }; }
    catch (e) {
      if (!pamet) return new Response('{"v":[]}', { status: 502, headers: { ...hlavicky, 'cache-control': 'no-store' } });   // starší odpověď je lepší než žádná
    }
  }
  return new Response(pamet.telo, { headers: hlavicky });
}
