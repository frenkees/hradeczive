// Jediné místo, které se ptá HERE (GitHub Actions, .github/workflows/doprava.yml, každých 20 min v době 4–23 h): návštěvníci mapy HERE nevolají,
// funkce /api/doprava jen přeposílá poslední snímek (live.json). Tím je měsíční počet dotazů pevně omezený a kvótu zdarma nelze překročit:
// počítadlo v agg.json (kvota) odmítne dotaz po dosažení limitu (DOPRAVA_MESICNI_LIMIT, výchozí 2000 z 2500 zdarma).
// Snímek se přičte do histogramu podle hodiny a typu dne (pracovní den 0–23, víkend 24–47); surové snímky se neukládají, jen poslední (live.json) a histogram.
// node skripty/doprava_sber.mjs <složka s daty> [URL]   ->  <složka>/live.json, agg.json (histogramy), typicka.json (medián jamFactoru ×10 podle hodiny)
// Bez HERE_API_KEY vezme snímek z URL (zpětná kompatibilita, testy).
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';

export const slot = (d = new Date()) => {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Prague', hour: 'numeric', hourCycle: 'h23', weekday: 'short' }).formatToParts(d).map((q) => [q.type, q.value]));
  return +p.hour + (p.weekday === 'Sat' || p.weekday === 'Sun' ? 24 : 0);
};

// měsíční počítadlo dotazů na HERE: true = dotaz je povolený (a započítá se)
export function kvota(agg, kdy = new Date(), limit = +(process.env.DOPRAVA_MESICNI_LIMIT || 2000)) {
  const m = kdy.toISOString().slice(0, 7);
  if (!agg.kvota || agg.kvota.m !== m) agg.kvota = { m, n: 0 };
  if (agg.kvota.n >= limit) return false;
  agg.kvota.n++; return true;
}

// přičte jeden snímek {t, s: {klíč: [jam×10, rychlost%]}} do agregace; vrací false, když je to týž snímek jako minule (cache funkce)
export function pridej(agg, snimek, kdy = new Date()) {
  if (!snimek || !snimek.s || !Object.keys(snimek.s).length) return false;
  if (snimek.t && agg.posledni === snimek.t) return false;
  const sl = slot(kdy);
  for (const [k, v] of Object.entries(snimek.s)) {
    const b = Math.max(0, Math.min(10, Math.round(v[0] / 10)));
    const u = (agg.s[k] ||= {});
    (u[sl] ||= new Array(11).fill(0))[b]++;
  }
  agg.n++; agg.posledni = snimek.t || kdy.toISOString(); agg.aktualizace = kdy.toISOString();
  return true;
}

// medián z histogramu (jamFactor ×10), hodina s méně než 2 snímky zůstane null
export function typicka(agg) {
  const s = {};
  for (const [k, u] of Object.entries(agg.s)) {
    const v = Array.from({ length: 48 }, (_, sl) => {
      const h = u[sl]; if (!h) return null;
      const n = h.reduce((a, b) => a + b, 0); if (n < 2) return null;
      let acc = 0; for (let i = 0; i < 11; i++) { acc += h[i]; if (acc >= n / 2) return i * 10; }
      return null;
    });
    if (v.some((x) => x !== null)) s[k] = v;
  }
  return { n: agg.n, aktualizace: agg.aktualizace, s };
}

// denní počítadlo dlaždic TomTom (zdarma 50 000 dlaždic denně; limit si držíme výrazně níž)
export function kvotaDen(agg, pocet, kdy = new Date(), limit = +(process.env.TOMTOM_DENNI_LIMIT || 20000)) {
  const d = kdy.toISOString().slice(0, 10);
  if (!agg.kvotaTT || agg.kvotaTT.d !== d) agg.kvotaTT = { d, n: 0 };
  if (agg.kvotaTT.n + pocet > limit) return false;
  agg.kvotaTT.n += pocet; return true;
}

// sloučí snímek jednoho zdroje do live.json: klíče TomTom začínají "t<číslo>/", klíče HERE číslem a čárkou; druhý zdroj zůstane z minula
export const jeTomTom = (k) => /^t\d+\//.test(k);
export function slucLive(stary, novy, zdroj) {
  const s = {};
  for (const [k, v] of Object.entries(stary?.s || {})) if (jeTomTom(k) !== (zdroj === 'tomtom')) s[k] = v;
  Object.assign(s, novy.s);
  return { t: novy.t, s, zdroje: { ...(stary?.zdroje || {}), [zdroj]: novy.t } };
}

if (process.argv[1] && process.argv[1].endsWith('doprava_sber.mjs')) {
  const dir = process.argv[2] || 'data', url = process.argv[3] || 'https://hradeczive.cz/api/doprava';
  mkdirSync(dir, { recursive: true });
  const f = join(dir, 'agg.json'), lf = join(dir, 'live.json');
  const agg = existsSync(f) ? JSON.parse(readFileSync(f, 'utf8')) : { n: 0, s: {} };
  let live = existsSync(lf) ? JSON.parse(readFileSync(lf, 'utf8')) : null;
  const H = process.env.HERE_API_KEY, TT = process.env.TOMTOM_API_KEY, kdy = new Date();
  // zdroje se střídají: TomTom při každém běhu (každých 10 min), HERE jen v první polovině každých 20 min (~1 700 dotazů měsíčně)
  const hereTed = !!H && (process.env.ZDROJ_HERE === '1' || kdy.getUTCMinutes() % 20 < 10);
  let hereSnimek = null;
  if (hereTed) {
    if (!kvota(agg)) console.log(`měsíční limit ${agg.kvota.n} dotazů na HERE dosažen, HERE se tento měsíc už nestahuje`);
    else {
      writeFileSync(f, JSON.stringify(agg));                          // dotaz se započítá i při selhání (HERE ho může účtovat)
      const { nactiProvoz } = await import('./vercel_api/doprava.js');
      try { hereSnimek = await nactiProvoz(H); live = slucLive(live, hereSnimek, 'here'); writeFileSync(lf, JSON.stringify(live)); }
      catch (e) { console.error('HERE selhalo:', e.message); }
    }
  }
  if (TT) {
    const { nactiTomTom, dlazdice } = await import('./doprava_tomtom.mjs');
    if (!kvotaDen(agg, dlazdice().length)) console.log('denní limit dlaždic TomTom dosažen');
    else {
      writeFileSync(f, JSON.stringify(agg));
      try { live = slucLive(live, await nactiTomTom(TT), 'tomtom'); writeFileSync(lf, JSON.stringify(live)); }
      catch (e) { console.error('TomTom selhal:', e.message); }
    }
  }
  if (!H && !TT) {                                                    // bez klíčů (testy): snímek z veřejné funkce
    const r = await fetch(url, { headers: { 'user-agent': 'hradeczive-doprava-sber' }, signal: AbortSignal.timeout(30000) });
    if (!r.ok) { console.error('api/doprava odpovědělo', r.status); process.exit(1); }
    hereSnimek = await r.json();
  }
  const novy = hereSnimek ? pridej(agg, hereSnimek) : false;          // do historie jen HERE (TomTom data se neukládají)
  writeFileSync(f, JSON.stringify(agg));
  if (novy) writeFileSync(join(dir, 'typicka.json'), JSON.stringify(typicka(agg)));
  console.log(novy ? `HERE snímek přidán, celkem ${agg.n}, dotazů na HERE tento měsíc ${agg.kvota?.n ?? '?'}` : 'do historie nic nepřibylo', '| TomTom dlaždic dnes', agg.kvotaTT?.n ?? 0, '| úseků v live', Object.keys(live?.s || {}).length);
}
