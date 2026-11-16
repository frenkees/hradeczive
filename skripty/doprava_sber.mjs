// Sběr typické dopravy: stáhne aktuální stav z veřejné funkce /api/doprava (HERE klíč zůstává jen ve Vercelu, dotaz jde přes její cache,
// takže sběr nezvyšuje počet dotazů na HERE) a přičte ho do histogramu podle hodiny a typu dne (pracovní den 0–23, víkend 24–47).
// node skripty/doprava_sber.mjs <složka s daty> [URL]   ->  <složka>/agg.json (histogramy) a <složka>/typicka.json (medián jamFactoru ×10 podle hodiny)
// Pouští ho GitHub Actions (.github/workflows/doprava.yml) každých 30 min; bez zapnutého počítače.
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';

export const slot = (d = new Date()) => {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Prague', hour: 'numeric', hourCycle: 'h23', weekday: 'short' }).formatToParts(d).map((q) => [q.type, q.value]));
  return +p.hour + (p.weekday === 'Sat' || p.weekday === 'Sun' ? 24 : 0);
};

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

if (process.argv[1] && process.argv[1].endsWith('doprava_sber.mjs')) {
  const dir = process.argv[2] || 'data', url = process.argv[3] || 'https://hradeczive.cz/api/doprava';
  mkdirSync(dir, { recursive: true });
  const f = join(dir, 'agg.json');
  const agg = existsSync(f) ? JSON.parse(readFileSync(f, 'utf8')) : { n: 0, s: {} };
  const r = await fetch(url, { headers: { 'user-agent': 'hradeczive-doprava-sber' }, signal: AbortSignal.timeout(30000) });
  if (!r.ok) { console.error('api/doprava odpovědělo', r.status); process.exit(1); }
  const novy = pridej(agg, await r.json());
  if (novy) {
    writeFileSync(f, JSON.stringify(agg));
    writeFileSync(join(dir, 'typicka.json'), JSON.stringify(typicka(agg)));
  }
  console.log(novy ? `snímek přidán, celkem ${agg.n}, úseků ${Object.keys(agg.s).length}` : 'beze změny (stejný snímek jako minule)');
}
