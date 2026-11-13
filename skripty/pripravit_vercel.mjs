// Připraví nasazeni/vercel/ = izomapa/site/ bez dlaždic; tiles.json ukazuje na dlaždice v R2.
// Použití (z izohradec/):  node skripty/pripravit_vercel.mjs https://pub-xxxx.r2.dev
// Pak:  cd nasazeni/vercel && vercel deploy --prod --yes
import { cpSync, rmSync, readFileSync, writeFileSync, existsSync, readdirSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

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

// hlavičky: tiles.json a index se ověřují vždy, data s ?v= se smí cachovat
writeFileSync(join(OUT, 'vercel.json'), JSON.stringify({
  cleanUrls: false,
  headers: [
    { source: '/(tiles.json|index.html|)', headers: [{ key: 'Cache-Control', value: 'public, max-age=0, must-revalidate' }] },
    { source: '/(overlay|preview|stromy)/(.*)', headers: [{ key: 'Cache-Control', value: 'public, max-age=3600' }] },
  ],
}, null, 2));
console.log(`nasazeni/vercel připraveno, přepsáno ${n} adres dlaždic na ${R2}`);
if (!existsSync(join(OUT, 'index.html'))) { console.error('chybí index.html'); process.exit(1); }
