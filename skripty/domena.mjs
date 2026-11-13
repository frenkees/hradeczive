// Doména hradeczive.eu: nákup u WEDOS (WAPI) s nameservery Cloudflare a nastavení zóny/DNS v Cloudflare.
// Tajné údaje jen z proměnných prostředí, skript je nikdy nevypisuje:
//   WEDOS_LOGIN (e-mail účtu), WEDOS_WAPI_PASS (heslo WAPI, ne heslo účtu), CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID
//
// Použití (z izohradec/):
//   node skripty/domena.mjs wedos-ping
//   node skripty/domena.mjs wedos-check hradeczive.eu
//   node skripty/domena.mjs wedos-kontakt nasazeni/wedos_kontakt.json      -> vytvoří EU kontakt, vypíše jeho ID
//   node skripty/domena.mjs cf-zona hradeczive.eu                          -> založí zónu, vypíše nameservery
//   node skripty/domena.mjs wedos-koupit hradeczive.eu <kontakt> <ns1> <ns2> [--ostre]   (bez --ostre jen test)
//   node skripty/domena.mjs wedos-ns hradeczive.eu <ns1> <ns2>             -> změna NS u už koupené domény
//   node skripty/domena.mjs cf-dns hradeczive.eu                           -> apex + www na Vercel (bez proxy)
//   node skripty/domena.mjs cf-stav hradeczive.eu
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

const [cmd, ...a] = process.argv.slice(2);
const sha1 = (s) => createHash('sha1').update(s).digest('hex');
const need = (k) => { if (!process.env[k]) { console.error(`chybí proměnná prostředí ${k}`); process.exit(1); } return process.env[k]; };

// ---------- WEDOS WAPI ----------
const pragueHour = () => new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Prague', hour: '2-digit', hour12: false }).format(new Date()).padStart(2, '0').slice(-2);
async function wapi(command, data = {}, test = false) {
  const user = need('WEDOS_LOGIN'), pass = need('WEDOS_WAPI_PASS');
  const request = { user, auth: sha1(user + sha1(pass) + pragueHour()), command, clTRID: `izo-${Date.now()}`, data, ...(test ? { test: '1' } : {}) };
  const r = await fetch('https://api.wedos.com/wapi/json', { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ request: JSON.stringify({ request }) }) });
  const j = (await r.json()).response;
  console.log(`WAPI ${command}${test ? ' (test)' : ''}: ${j.code} ${j.result}`);
  return j;
}
const dns = (ns) => Object.fromEntries(ns.map((n, i) => [`server${i + 1}`, { name: n }]));

// ---------- Cloudflare API ----------
async function cf(path, method = 'GET', body) {
  const r = await fetch(`https://api.cloudflare.com/client/v4${path}`, { method,
    headers: { authorization: `Bearer ${need('CLOUDFLARE_API_TOKEN')}`, 'content-type': 'application/json' }, body: body && JSON.stringify(body) });
  const j = await r.json();
  if (!j.success) { console.error(`Cloudflare ${method} ${path}:`, JSON.stringify(j.errors)); }
  return j;
}
const zoneId = async (name) => ((await cf(`/zones?name=${name}`)).result || [])[0];

switch (cmd) {
  case 'wedos-ping': await wapi('ping'); break;
  case 'wedos-check': { const j = await wapi('domain-check', { name: a[0] }); console.log(JSON.stringify(j.data || {}, null, 1)); break; }
  case 'wedos-kontakt': {
    const c = JSON.parse(readFileSync(a[0], 'utf8'));
    const j = await wapi('contact-create', { tld: 'eu', contact: c });
    if (j.data?.cname) console.log(`ID kontaktu: ${j.data.cname}`);
    break;
  }
  case 'wedos-koupit': {
    const [name, owner, ...rest] = a, ns = rest.filter((x) => !x.startsWith('--')), ostre = a.includes('--ostre');
    if (!name || !owner || ns.length < 2) { console.error('použití: wedos-koupit <doména> <kontakt> <ns1> <ns2> [--ostre]'); process.exit(1); }
    const c = (await wapi('contact-info', { tld: 'eu', cname: owner })).data?.contact || {};
    const j = await wapi('domain-create', { name, period: 1, owner_c: owner, dns: dns(ns), rules: { fname: c.fname, lname: c.lname } }, !ostre);
    console.log(JSON.stringify(j.data || {}, null, 1));
    if (!ostre) console.log('Jen test, nic se nekoupilo. Na ostro přidej --ostre.');
    break;
  }
  case 'wedos-ns': await wapi('domain-update-ns', { name: a[0], dns: dns(a.slice(1)) }); break;
  case 'cf-zona': {
    let z = await zoneId(a[0]);
    if (!z) z = (await cf('/zones', 'POST', { name: a[0], account: { id: need('CLOUDFLARE_ACCOUNT_ID') }, type: 'full' })).result;
    if (z) console.log(`zóna ${z.name} (${z.id}), stav ${z.status}\nnameservery: ${z.name_servers.join(' ')}`);
    break;
  }
  case 'cf-dns': {
    const z = await zoneId(a[0]); if (!z) { console.error('zóna neexistuje'); process.exit(1); }
    const want = [{ type: 'A', name: a[0], content: '76.76.21.21' }, { type: 'CNAME', name: `www.${a[0]}`, content: 'cname.vercel-dns.com' }];
    const have = (await cf(`/zones/${z.id}/dns_records?per_page=100`)).result || [];
    for (const w of want) {
      const old = have.find((h) => h.name === w.name && ['A', 'AAAA', 'CNAME'].includes(h.type));
      const body = { ...w, ttl: 1, proxied: false };   // Vercel chce DNS bez proxy Cloudflare (vlastní certifikát a CDN)
      const r = old ? await cf(`/zones/${z.id}/dns_records/${old.id}`, 'PUT', body) : await cf(`/zones/${z.id}/dns_records`, 'POST', body);
      if (r.success) console.log(`${w.type} ${w.name} -> ${w.content}`);
    }
    break;
  }
  case 'cf-stav': {
    const z = await zoneId(a[0]); if (!z) { console.log('zóna neexistuje'); break; }
    console.log(`zóna ${z.name} (${z.id}): ${z.status}, NS ${z.name_servers.join(' ')}`);
    for (const r of (await cf(`/zones/${z.id}/dns_records?per_page=100`)).result || []) console.log(`  ${r.type} ${r.name} -> ${r.content}${r.proxied ? ' (proxy)' : ''}`);
    break;
  }
  default: console.log(readFileSync(new URL(import.meta.url), 'utf8').split('\n').filter((l) => l.startsWith('//')).join('\n'));
}
