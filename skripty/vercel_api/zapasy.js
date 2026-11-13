// Zápasy FC Hradec Králové (A-tým) pro mapu: rozpis z fchk.cz, při zápase průběžné skóre z onlajny.com.
// Vercel funkce /api/zapasy (Node, ESM). Stejný parser používá skripty/zapasy.mjs pro statický záložní zapasy.json.
// Odpověď: { stav: ISO, zdroj, zapasy: [{ t (UTC ISO nebo null), datum 'YYYY-MM-DD', cas 'HH:MM'|null, soutez, kolo,
//   domaci, hoste, doma (hraje se v Malšovické aréně), skore: [d, h]|null, online }], live: {..}|null }

const UA = { 'user-agent': 'Mozilla/5.0 (compatible; izomapa-hradec/1.0)' };
const ROZPIS = 'https://www.fchk.cz/matches/MUZ';
const strip = (s) => s.replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/\s+/g, ' ').trim();

// místní čas v Praze -> UTC (letní/zimní čas podle Intl)
export function prahaUtc(y, m, d, hh, mm) {
  const guess = Date.UTC(y, m - 1, d, hh, mm);
  const f = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Prague', hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
  const p = Object.fromEntries(f.formatToParts(new Date(guess)).map((x) => [x.type, x.value]));
  const local = Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute);
  return new Date(guess - (local - guess));
}

export function parseRozpis(html) {
  const out = [];
  for (const blk of html.split('<li class="match-card').slice(1)) {
    const b = blk.slice(0, blk.indexOf('</li>'));
    const soutez = /chance-logo/.test(b) ? 'Chance Liga' : strip((b.match(/label-[a-z-]+">([^<]*)</) || [])[1] || '');
    const det = [...b.matchAll(/<p class="fs-small">([^<]*)<\/p>/g)].map((m) => strip(m[1]));
    const dm = (det[1] || '').match(/(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})/);
    if (!dm) continue;
    const misto = strip((b.match(/<\/div>\s*<p>([^<]*)<\/p>\s*<\/div>\s*<div class="match-card_teams"/) || [])[1] || '');
    const cols = [...b.matchAll(/<div class="flex-col gap-1">([\s\S]*?)<\/div>/g)].map((m) => [...m[1].matchAll(/<p[^>]*>([\s\S]*?)<\/p>/g)].map((q) => strip(q[1])));
    const names = cols.find((c) => c.length === 2 && c.every((x) => /[A-Za-zÁ-ž]/.test(x))) || [];
    const nums = cols.find((c) => c.length === 2 && c.every((x) => /^\d+$/.test(x)));
    const cas = (b.match(/match-card_time[^>]*>\s*(\d{1,2}:\d{2})/) || [])[1] || null;
    const [y, m, d] = [+dm[3], +dm[2], +dm[1]];
    const t = cas ? prahaUtc(y, m, d, +cas.split(':')[0], +cas.split(':')[1]).toISOString() : null;
    out.push({
      t, datum: `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`, cas, soutez, kolo: det[0] || '', misto,
      domaci: names[0] || '', hoste: names[1] || '', doma: /Hradec Králové/.test(misto) && /Hradec/.test(names[0] || ''),
      skore: nums ? nums.map(Number) : null,
      online: (b.match(/href="(https:\/\/www\.onlajny\.com\/match\/index\/id\/\d+)"/) || [])[1] || null,
    });
  }
  return out;
}

// průběžný stav z onlajny.com: skóre z titulku stránky, fáze ze třídy posledního záznamu (m-status-1/2 poločas, p přestávka, k konec)
export function parseOnline(html) {
  const tt = (html.match(/<title>([^<]*)<\/title>/) || [])[1] || '';
  const sc = tt.match(/\b(\d+):(\d+)\b/);
  const st = (html.match(/m-status-([0-9a-z]+)/) || [])[1] || null;
  const faze = { 1: '1. poločas', 2: '2. poločas', p: 'přestávka', k: 'konec', n: 'před zápasem' }[st] || null;
  return { skore: sc ? [+sc[1], +sc[2]] : null, faze, konec: st === 'k' };
}

export async function nactiZapasy(now = Date.now()) {
  const r = await fetch(ROZPIS, { headers: UA });
  if (!r.ok) throw new Error('fchk.cz ' + r.status);
  const zapasy = parseRozpis(await r.text());
  // zápas, který právě běží (od 15 min před výkopem do 2,5 h po něm): průběžné skóre
  let live = null;
  const z = zapasy.find((q) => q.t && now >= Date.parse(q.t) - 15 * 60e3 && now <= Date.parse(q.t) + 150 * 60e3);
  if (z) {
    live = { ...z, skore: null, faze: Date.now() < Date.parse(z.t) ? 'před zápasem' : null };
    if (z.online) try {
      const o = await fetch(z.online, { headers: UA });
      if (o.ok) Object.assign(live, Object.fromEntries(Object.entries(parseOnline(await o.text())).filter(([, v]) => v !== null)));
    } catch { /* bez průběžného stavu */ }
  }
  return { stav: new Date(now).toISOString(), zdroj: ROZPIS, zapasy, live };
}

export async function GET() {
  try {
    const d = await nactiZapasy();
    const maxAge = d.live && !d.live.konec ? 30 : 600;               // během zápasu čerstvé skóre, jinak cache 10 min
    return new Response(JSON.stringify(d), { headers: { 'content-type': 'application/json; charset=utf-8',
      'cache-control': `public, max-age=${maxAge}, s-maxage=${maxAge}, stale-while-revalidate=60` } });
  } catch (e) {
    return new Response(JSON.stringify({ chyba: String(e.message || e) }), { status: 502, headers: { 'content-type': 'application/json' } });
  }
}
