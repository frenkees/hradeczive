// Připraví nasazeni/vercel/ = izomapa/site/ bez dlaždic; tiles.json ukazuje na dlaždice v R2.
// Použití (z izohradec/):  node skripty/pripravit_vercel.mjs https://pub-xxxx.r2.dev
// Pak:  cd nasazeni/vercel && vercel deploy --prod --yes
import { cpSync, rmSync, readFileSync, writeFileSync, existsSync, readdirSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = new URL('..', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const SITE = join(ROOT, 'izomapa', 'site');
const OUT = join(ROOT, 'nasazeni', 'vercel');
const R2 = (process.argv[2] || '').replace(/\/+$/, '');
if (!/^https:\/\//.test(R2)) { console.error('zadej veřejnou adresu R2, např. https://pub-xxxx.r2.dev'); process.exit(1); }

// zachovat propojení s projektem Vercelu (.vercel/), zbytek přepsat
mkdirSync(OUT, { recursive: true });
for (const e of readdirSync(OUT)) if (e !== '.vercel') rmSync(join(OUT, e), { recursive: true, force: true });
for (const e of readdirSync(SITE)) if (e !== 'tiles') cpSync(join(SITE, e), join(OUT, e), { recursive: true });

// tiles.json: relativní "tiles/..." -> absolutní adresa v R2 (dlaždice mají v R2 stejnou cestu)
const t = JSON.parse(readFileSync(join(SITE, 'tiles.json'), 'utf8'));
let n = 0;
const fix = (o) => {
  if (!o || typeof o !== 'object') return;
  if (typeof o.Url === 'string' && o.Url.startsWith('tiles/')) { o.Url = `${R2}/${o.Url}`; n++; }
  for (const v of Object.values(o)) fix(v);
};
fix(t);
writeFileSync(join(OUT, 'tiles.json'), JSON.stringify(t));

// serverové funkce Vercelu (skripty/vercel_api/*.js -> api/): zápasy FC Hradec Králové pro Malšovickou arénu
const API = join(ROOT, 'skripty', 'vercel_api');
if (existsSync(API)) {
  mkdirSync(join(OUT, 'api'), { recursive: true });
  for (const e of readdirSync(API)) if (e.endsWith('.js')) cpSync(join(API, e), join(OUT, 'api', e));
  writeFileSync(join(OUT, 'package.json'), JSON.stringify({ private: true, type: 'module', dependencies: { '@vercel/blob': '^2.0.0' } }, null, 2));
}
// statická záloha rozpisu zápasů (když funkce neodpoví)
try {
  const { nactiZapasy } = await import('./vercel_api/zapasy.js');
  const d = await nactiZapasy(); d.staticky = true;
  writeFileSync(join(OUT, 'zapasy.json'), JSON.stringify(d));
} catch (e) { console.warn('zapasy.json se nepodařilo stáhnout:', e.message); }

// hlavičky: tiles.json a index se ověřují vždy, data s ?v= se smí cachovat
writeFileSync(join(OUT, 'vercel.json'), JSON.stringify({
  cleanUrls: false,
  // hlavní adresa je hradeczive.cz; .eu a www vedou sem (trvalé přesměrování, cesta se zachová)
  redirects: ['www.hradeczive.cz', 'hradeczive.eu', 'www.hradeczive.eu'].map((h) => ({ source: '/(.*)', has: [{ type: 'host', value: h }], destination: 'https://hradeczive.cz/$1', permanent: true })),
  headers: [
    { source: '/(tiles.json|index.html|)', headers: [{ key: 'Cache-Control', value: 'public, max-age=0, must-revalidate' }] },
    { source: '/(overlay|preview|stromy)/(.*)', headers: [{ key: 'Cache-Control', value: 'public, max-age=3600' }] },
    { source: '/zapasy.json', headers: [{ key: 'Cache-Control', value: 'public, max-age=600' }] },
  ],
}, null, 2));
console.log(`nasazeni/vercel připraveno, přepsáno ${n} adres dlaždic na ${R2}`);
if (!existsSync(join(OUT, 'index.html'))) { console.error('chybí index.html'); process.exit(1); }
// Vercel Web Analytics (bez cookies, anonymní: návštěvy, země, odkud přišli, zařízení; zapíná se v projektu na Vercelu v záložce Analytics)
{
  const f = join(OUT, 'index.html'); let h = readFileSync(f, 'utf8');
  if (!h.includes('/_vercel/insights/script.js')) {
    h = h.replace('</head>', '<script>window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };</script>\n<script defer src="/_vercel/insights/script.js"></script>\n</head>');
    writeFileSync(f, h); console.log('přidán skript Vercel Web Analytics');
  }
}
// Umami (bez cookies): Website ID z env UMAMI_WEBSITE_ID nebo ze souboru skripty/umami_id.txt (ID není tajné, je vidět v HTML)
// Self-host: nastavit i UMAMI_SRC (např. https://umami.example.cz/script.js); výchozí je Umami Cloud
{
  const idFile = join(dirname(fileURLToPath(import.meta.url)), 'umami_id.txt');
  const id = (process.env.UMAMI_WEBSITE_ID || (existsSync(idFile) ? readFileSync(idFile, 'utf8') : '')).trim();
  const src = process.env.UMAMI_SRC || 'https://cloud.umami.is/script.js';
  const f = join(OUT, 'index.html'); let h = readFileSync(f, 'utf8');
  if (id && !h.includes('data-website-id')) {
    h = h.replace('</head>', `<script defer src="${src}" data-website-id="${id}"></script>\n</head>`);
    writeFileSync(f, h); console.log('přidán skript Umami');
  } else if (!id) console.log('Umami přeskočeno (chybí UMAMI_WEBSITE_ID / skripty/umami_id.txt)');
}
