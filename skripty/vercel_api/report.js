// Hlášení chyb z mapy: formulář v kartě místa -> POST /api/report -> nové issue v GitHubu (návštěvník se nemusí nikde registrovat).
// Vercel funkce (Node, ESM). Tajné: GITHUB_TOKEN (fine-grained PAT, jen repozitář s právem Issues: read & write), volitelně GITHUB_REPO (výchozí frenkees/hradeczive).
// Volitelně fotka a e-mail: ukládají se SOUKROMĚ do Vercel Blob (BLOB_READ_WRITE_TOKEN, privátní store), do veřejného issue jde jen informace, že fotka/kontakt existuje.
// E-mail slouží jen k poděkování a oznámení stavu (RESEND_API_KEY + MAIL_FROM, bez nich se jen uloží). Ukládá se jen text hlášení, název a poloha místa a odkaz na pohled; IP adresa se nikam neposílá ani neukládá.
import { createHmac } from 'node:crypto';
import { put } from '@vercel/blob';
const json = (d, s = 200) => new Response(JSON.stringify(d), { status: s, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
const zasahy = new Map();                                  // hrubý limit na instanci funkce: hash zařízení -> časy hlášení (hlavní ochrana je honeypot a délka)
const clean = (s, n) => String(s ?? '').replace(/[\u0000-\u0008\u000b-\u001f]/g, '').trim().slice(0, n);
const bezPingu = (s) => s.replace(/@/g, '@​').replace(/#(\d)/g, '#​$1');   // žádná zmínka uživatele ani odkaz na jiné issue

const GH = (token) => ({ authorization: `Bearer ${token}`, accept: 'application/vnd.github+json', 'x-github-api-version': '2022-11-28', 'content-type': 'application/json', 'user-agent': 'hradeczive-report' });
const podpis = (cislo) => createHmac('sha256', process.env.GITHUB_TOKEN || '').update('hlaseni:' + cislo).digest('hex').slice(0, 32);   // k doplnění fotky/e-mailu smí jen ten, kdo hlášení právě podal
const EMAIL = /^[^\s@<>"]{1,64}@[^\s@<>"]{1,200}\.[^\s@<>"]{2,}$/;
const blobOk = () => !!process.env.BLOB_READ_WRITE_TOKEN;

// fotka přijde jako data URL (klient ji zmenší na ~1600 px), ověří se typ podle hlavičky souboru
function fotoZ(dataUrl) {
  const m = /^data:(image\/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=]+)$/.exec(String(dataUrl || ''));
  if (!m) return null;
  const buf = Buffer.from(m[2], 'base64');
  if (buf.length < 200 || buf.length > 3.5e6) return null;
  const jpg = buf[0] === 0xff && buf[1] === 0xd8, png = buf.subarray(1, 4).toString() === 'PNG', webp = buf.subarray(0, 4).toString() === 'RIFF' && buf.subarray(8, 12).toString() === 'WEBP';
  if (!(jpg || png || webp)) return null;
  return { buf, type: jpg ? 'image/jpeg' : png ? 'image/png' : 'image/webp', ext: jpg ? 'jpg' : png ? 'png' : 'webp' };
}
// soukromé úložiště: hlaseni/<číslo>/foto-<čas>.ext a hlaseni/<číslo>/kontakt.json (nikdy ne veřejně v gitu)
async function ulozSoukrome(cislo, d) {
  const out = { foto: false, email: false };
  if (!blobOk()) return out;
  const f = fotoZ(d.foto);
  if (f) { await put(`hlaseni/${cislo}/foto-${Date.now()}.${f.ext}`, f.buf, { access: 'private', contentType: f.type, addRandomSuffix: true }); out.foto = true; }
  const em = clean(d.email, 254).toLowerCase();
  if (EMAIL.test(em)) {
    await put(`hlaseni/${cislo}/kontakt.json`, JSON.stringify({ email: em, souhlas: new Date().toISOString() }), { access: 'private', contentType: 'application/json', allowOverwrite: true, addRandomSuffix: false });
    out.email = em;
  }
  return out;
}
async function posliMail(komu, cislo) {
  const key = process.env.RESEND_API_KEY, from = process.env.MAIL_FROM;
  if (!key || !from) return;
  try {
    await fetch('https://api.resend.com/emails', { method: 'POST', headers: { authorization: `Bearer ${key}`, 'content-type': 'application/json' },
      body: JSON.stringify({ from, to: [komu], subject: `Děkujeme za hlášení č. ${cislo} – Hradec živě`,
        text: `Dobrý den,\n\nděkujeme, že jste nám na mapě Hradec živě nahlásili nepřesnost (hlášení č. ${cislo}). Až ho vyřešíme, napíšeme vám.\n\nTento e-mail používáme jen k poděkování a ke zprávě o stavu vašeho hlášení, jinam ho neposíláme. Pokud si nepřejete další zprávy, stačí odpovědět.\n\nHradec živě` }) });
  } catch {}
}
const komentar = (token, repo, cislo, text) => fetch(`https://api.github.com/repos/${repo}/issues/${cislo}/comments`, { method: 'POST', headers: GH(token), body: JSON.stringify({ body: text }) }).catch(() => {});

export async function POST(request) {
  let d; try { d = await request.json(); } catch { return json({ ok: false, msg: 'Hlášení se nepovedlo přečíst.' }, 400); }
  if (d.hp) return json({ ok: true });                     // vyplněná past pro boty: tváříme se, že vše prošlo
  const token = process.env.GITHUB_TOKEN;
  if (!token) return json({ ok: false, msg: 'Hlášení zatím není zprovozněné. Zkuste to prosím později.' }, 503);
  const repo = process.env.GITHUB_REPO || 'frenkees/hradeczive';
  const ip = (request.headers.get('x-forwarded-for') || '').split(',')[0].trim() || 'x', now = Date.now();
  const arr = (zasahy.get(ip) || []).filter((t) => now - t < 3600e3);
  if (arr.length >= 8) return json({ ok: false, msg: 'Z tohoto zařízení přišlo za poslední hodinu už několik hlášení. Zkuste to prosím později.' }, 429);

  // doplnění fotky / e-mailu k už odeslanému hlášení (po potvrzení odeslání)
  if (d.doplnit) {
    const cislo = Math.floor(Number(d.doplnit));
    if (!(cislo > 0) || d.podpis !== podpis(cislo)) return json({ ok: false, msg: 'Doplnění se nepovedlo ověřit.' }, 403);
    if (!blobOk()) return json({ ok: false, msg: 'Přijímání fotek zatím není zprovozněné.' }, 503);
    arr.push(now); zasahy.set(ip, arr);
    let u; try { u = await ulozSoukrome(cislo, d); } catch { return json({ ok: false, msg: 'Uložení se nepovedlo. Zkuste to prosím za chvíli.' }, 502); }
    if (!u.foto && !u.email) return json({ ok: false, msg: 'Fotka nebo e-mail nejsou v pořádku (fotka JPG/PNG/WebP do ~3 MB).' }, 400);
    if (u.foto) await komentar(token, repo, cislo, '📷 Autor hlášení přiložil fotku (uložena soukromě, mimo GitHub).');
    if (u.email) { await komentar(token, repo, cislo, '✉️ Autor hlášení chce dostat poděkování a stav vyřešení (e-mail je uložen soukromě).'); await posliMail(u.email, cislo); }
    return json({ ok: true, foto: u.foto, email: !!u.email });
  }

  const note = clean(d.note, 600), title = clean(d.title, 120) || 'místo na mapě';
  if (note.length < 3) return json({ ok: false, msg: 'Napište prosím, co tu nesedí (aspoň pár slov).' }, 400);
  arr.push(now); zasahy.set(ip, arr); if (zasahy.size > 500) zasahy.clear();
  const lat = Number(d.lat), lon = Number(d.lon), okPoloha = Number.isFinite(lat) && Number.isFinite(lon);
  let odkaz = ''; try { const u = new URL(String(d.url || '')); if (/(^|\.)hradeczive\.(cz|eu)$|\.vercel\.app$/.test(u.hostname)) odkaz = u.href.slice(0, 400); } catch {}
  const maFoto = !!fotoZ(d.foto) && blobOk(), maMail = EMAIL.test(clean(d.email, 254).toLowerCase()) && blobOk();
  const body = ['**Hlášení z mapy**', '', ...bezPingu(note).split('\n').map((r) => '> ' + r), '', '---',
    `Místo: ${bezPingu(title)}`, okPoloha ? `Souřadnice: ${lat.toFixed(5)}, ${lon.toFixed(5)}` : '', odkaz ? `Odkaz na pohled: ${odkaz}` : '',
    maFoto ? 'Fotka: přiložena (uložena soukromě)' : '', maMail ? 'Kontakt: autor chce poděkování a stav vyřešení (e-mail uložen soukromě)' : '', 'Odesláno formulářem na webu.'].filter((r) => r !== '').join('\n');
  const vytvor = (labels) => fetch(`https://api.github.com/repos/${repo}/issues`, { method: 'POST', headers: GH(token), body: JSON.stringify({ title: 'Mapa: ' + bezPingu(title), body, ...(labels ? { labels } : {}) }) });
  let r = await vytvor(['z-mapy']);
  if (!r.ok && r.status === 422) r = await vytvor(null);   // štítek ještě neexistuje: zkus bez něj
  if (!r.ok) return json({ ok: false, msg: 'Hlášení se nepovedlo odeslat. Zkuste to prosím za chvíli.' }, 502);
  const cislo = (await r.json().catch(() => ({}))).number;
  if (cislo && (maFoto || maMail)) { try { const u = await ulozSoukrome(cislo, d); if (u.email) await posliMail(u.email, cislo); } catch {} }
  return json({ ok: true, cislo, podpis: cislo ? podpis(cislo) : '', soukrome: blobOk(), foto: maFoto, email: maMail });
}
