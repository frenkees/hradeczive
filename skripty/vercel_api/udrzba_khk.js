// Zimní údržba silnic Královéhradeckého kraje pro mapu (doplněk udrzba_khk).
// Vercel funkce (Node, ESM). Zdroj: veřejná mapa „Obslouženost vozovek ZÚ“ Správy a údržby silnic KHK (https://uskhk.eu/suhhkap/), která bere data
// z veřejného rozhraní https://www.protank-dynamics.cz/SUSHK-AP (GeoJSON úseků podle stáří posledního ošetření nebo kontrolní jízdy, bez klíče).
// Zdroj se ptá nejvýš jednou za 5 minut bez ohledu na návštěvnost (společná cache CDN + paměť funkce). Posílají se jen úseky v okolí Hradce Králové,
// zjednodušené: { z: [pásmo 0..3 -> [[lon, lat, lon, lat, …], …]], t }. Pásma: 0 do 30 min, 1 30–60 min, 2 1–3 h, 3 3–12 h.
const ZDROJ = 'https://www.protank-dynamics.cz/SUSHK-AP/Modules/WRM/Roads/GetRoads?timeIndex=';
const BBOX = [50.12, 15.70, 50.30, 15.97];                  // jih, západ, sever, východ (Hradec Králové a okolí s rezervou)
const TTL = 270e3;                                          // paměť funkce; CDN drží 300 s
const hlavicky = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, s-maxage=300, stale-while-revalidate=600' };
let pamet = null;                                           // {kdy, telo}

const vBoxu = (lo, la) => la >= BBOX[0] && la <= BBOX[2] && lo >= BBOX[1] && lo <= BBOX[3];

// z jedné čáry nechá souvislé kusy uvnitř oblasti a vyřídí body těsně za sebou (~3 m)
export function upravCary(cary) {
  const out = [];
  for (const c of cary || []) {
    let cur = [];
    const flush = () => { if (cur.length >= 4) out.push(cur); cur = []; };
    let pl = null, pa = null;
    for (const [lo, la] of c) {
      if (!vBoxu(lo, la)) { flush(); pl = pa = null; continue; }
      if (pl !== null && Math.abs(lo - pl) < 0.00004 && Math.abs(la - pa) < 0.00003) continue;
      cur.push(Math.round(lo * 1e5) / 1e5, Math.round(la * 1e5) / 1e5); pl = lo; pa = la;
    }
    flush();
  }
  return out;
}

export async function nactiUdrzbu() {
  const z = await Promise.all([0, 1, 2, 3].map(async (i) => {
    const r = await fetch(ZDROJ + i, { headers: { 'user-agent': 'hradeczive-udrzba', accept: 'application/json' }, signal: AbortSignal.timeout(12000) });
    if (!r.ok) throw new Error('SUSHK ' + r.status);
    const d = JSON.parse((await r.text()).replace(/^﻿/, ''));
    return upravCary(d.coordinates);
  }));
  return { z, t: Date.now() };
}

export async function GET() {
  if (pamet && Date.now() - pamet.kdy < TTL) return new Response(pamet.telo, { headers: hlavicky });
  try {
    const telo = JSON.stringify(await nactiUdrzbu());
    pamet = { kdy: Date.now(), telo };
    return new Response(telo, { headers: hlavicky });
  } catch {
    if (pamet) return new Response(pamet.telo, { headers: hlavicky });       // starší odpověď je lepší než žádná
    return new Response('{"z":[[],[],[],[]]}', { status: 502, headers: { ...hlavicky, 'cache-control': 'no-store' } });
  }
}
