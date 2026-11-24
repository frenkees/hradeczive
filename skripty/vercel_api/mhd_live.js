// Živá poloha a zpoždění vozidel MHD Hradec Králové pro mapu (doplněk mhd_live).
// Vercel funkce (Node, ESM). Zdroj: informační systém DPmHK (https://dpmhk.qrbus.me, veřejné JSON rozhraní webu dopravního podniku),
// záloha: zpracovaná mapa https://mapa.fcen.cz (stejná data). Odpověď má pro všechny návštěvníky společnou cache (~20 s),
// zdroj se tedy ptá nejvýš ~3× za minutu bez ohledu na návštěvnost.
// Z odpovědi se ukládá a posílá JEN: číslo vozidla, linka, poloha, směr, zpoždění, číslo trasy. Jména řidičů, počty cestujících
// a další provozní údaje, které zdroj vrací, se zahazují hned tady (nikdy neopustí funkci).
const DPMHK = 'https://dpmhk.qrbus.me/index/getAllRtdVehicles';
const FCEN = 'https://mapa.fcen.cz/api/vehicle_data';
const BBOX = [50.15, 15.74, 50.27, 15.93];                  // jih, západ, sever, východ (s rezervou kolem mapy)
const STARE_S = 180;                                        // záznam starší než 3 min se zahodí (vozidlo bez signálu)
const D_MIN = -300, D_MAX = 3600;                           // rozumné zpoždění v s
const TTL = 15e3;
const hlavicky = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, s-maxage=20, stale-while-revalidate=40' };
let pamet = null;                                           // {kdy, telo}: druhá pojistka vedle CDN cache

const vBoxu = (la, lo) => la >= BBOX[0] && la <= BBOX[2] && lo >= BBOX[1] && lo <= BBOX[3];
const cele = (x) => Math.round(Number(x));

export function zDpmhk(d, ted = Date.now()) {
  const out = [];
  for (const v of d.vehicles || []) {
    const ln = String(v.ln ?? '').trim();
    if (!ln || ln.toLowerCase() === 'x' || !v.li) continue;                // mimo linku / bez čísla vozidla
    const la = v.la / 1e5, lo = v.lo / 1e5, kdy = Date.parse(v.l);
    if (!Number.isFinite(la) || !Number.isFinite(lo) || !vBoxu(la, lo)) continue;
    if (!Number.isFinite(kdy) || ted - kdy > STARE_S * 1000) continue;
    const dl = cele(v.d);
    if (!Number.isFinite(dl) || dl < D_MIN || dl > D_MAX) continue;
    out.push({ id: String(v.li), ln, la: +la.toFixed(5), lo: +lo.toFixed(5), az: cele(v.az) || 0, d: dl, rn: String(v.rn ?? '') });
  }
  return out;
}

export function zFcen(d, ted = Date.now()) {
  const out = [];
  for (const v of d.vehicles || []) {
    const ln = String(v.line ?? '').trim();
    if (!ln || ln.toLowerCase() === 'x' || !v.vehicle_id) continue;
    const la = Number(v.latitude), lo = Number(v.longitude), kdy = Date.parse(v.vehicle_time);
    if (!Number.isFinite(la) || !Number.isFinite(lo) || !vBoxu(la, lo)) continue;
    if (Number.isFinite(kdy) && ted - kdy > STARE_S * 1000) continue;
    const dl = cele(v.delay);
    if (!Number.isFinite(dl) || dl < D_MIN || dl > D_MAX) continue;
    out.push({ id: String(v.vehicle_id), ln, la: +la.toFixed(5), lo: +lo.toFixed(5), az: cele(v.azimuth) || 0, d: dl, rn: String(v.route_number ?? '') });
  }
  return out;
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
