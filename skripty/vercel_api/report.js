// Hlášení chyb z mapy: formulář v kartě místa -> POST /api/report -> nové issue v GitHubu (návštěvník se nemusí nikde registrovat).
// Vercel funkce (Node, ESM). Tajné: GITHUB_TOKEN (fine-grained PAT, jen repozitář s právem Issues: read & write), volitelně GITHUB_REPO (výchozí frenkees/hradeczive).
// Ukládá se jen text hlášení, název a poloha místa a odkaz na pohled; IP adresa se nikam neposílá ani neukládá.
const json = (d, s = 200) => new Response(JSON.stringify(d), { status: s, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
const zasahy = new Map();                                  // hrubý limit na instanci funkce: hash zařízení -> časy hlášení (hlavní ochrana je honeypot a délka)
const clean = (s, n) => String(s ?? '').replace(/[\u0000-\u0008\u000b-\u001f]/g, '').trim().slice(0, n);
const bezPingu = (s) => s.replace(/@/g, '@​').replace(/#(\d)/g, '#​$1');   // žádná zmínka uživatele ani odkaz na jiné issue

export async function POST(request) {
  let d; try { d = await request.json(); } catch { return json({ ok: false, msg: 'Hlášení se nepovedlo přečíst.' }, 400); }
  if (d.hp) return json({ ok: true });                     // vyplněná past pro boty: tváříme se, že vše prošlo
  const note = clean(d.note, 600), title = clean(d.title, 120) || 'místo na mapě';
  if (note.length < 3) return json({ ok: false, msg: 'Napište prosím, co tu nesedí (aspoň pár slov).' }, 400);
  const token = process.env.GITHUB_TOKEN;
  if (!token) return json({ ok: false, msg: 'Hlášení zatím není zprovozněné. Zkuste to prosím později.' }, 503);
  const ip = (request.headers.get('x-forwarded-for') || '').split(',')[0].trim() || 'x', now = Date.now();
  const arr = (zasahy.get(ip) || []).filter((t) => now - t < 3600e3);
  if (arr.length >= 5) return json({ ok: false, msg: 'Z tohoto zařízení přišlo za poslední hodinu už několik hlášení. Zkuste to prosím později.' }, 429);
  arr.push(now); zasahy.set(ip, arr); if (zasahy.size > 500) zasahy.clear();
  const lat = Number(d.lat), lon = Number(d.lon), okPoloha = Number.isFinite(lat) && Number.isFinite(lon);
  let odkaz = ''; try { const u = new URL(String(d.url || '')); if (/(^|\.)hradeczive\.(cz|eu)$|\.vercel\.app$/.test(u.hostname)) odkaz = u.href.slice(0, 400); } catch {}
  const body = ['**Hlášení z mapy**', '', ...bezPingu(note).split('\n').map((r) => '> ' + r), '', '---',
    `Místo: ${bezPingu(title)}`, okPoloha ? `Souřadnice: ${lat.toFixed(5)}, ${lon.toFixed(5)}` : '', odkaz ? `Odkaz na pohled: ${odkaz}` : '', 'Odesláno formulářem na webu.'].filter((r) => r !== '').join('\n');
  const repo = process.env.GITHUB_REPO || 'frenkees/hradeczive';
  const r = await fetch(`https://api.github.com/repos/${repo}/issues`, { method: 'POST',
    headers: { authorization: `Bearer ${token}`, accept: 'application/vnd.github+json', 'x-github-api-version': '2022-11-28', 'content-type': 'application/json', 'user-agent': 'hradeczive-report' },
    body: JSON.stringify({ title: 'Mapa: ' + bezPingu(title), body, labels: ['z-mapy'] }) });
  if (!r.ok && r.status === 422) {                          // štítek ještě neexistuje: zkus bez něj
    const r2 = await fetch(`https://api.github.com/repos/${repo}/issues`, { method: 'POST',
      headers: { authorization: `Bearer ${token}`, accept: 'application/vnd.github+json', 'content-type': 'application/json', 'user-agent': 'hradeczive-report' },
      body: JSON.stringify({ title: 'Mapa: ' + bezPingu(title), body }) });
    return r2.ok ? json({ ok: true }) : json({ ok: false, msg: 'Hlášení se nepovedlo odeslat. Zkuste to prosím za chvíli.' }, 502);
  }
  return r.ok ? json({ ok: true }) : json({ ok: false, msg: 'Hlášení se nepovedlo odeslat. Zkuste to prosím za chvíli.' }, 502);
}
