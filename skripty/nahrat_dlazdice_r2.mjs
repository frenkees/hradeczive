// Nahraje izomapa/site/tiles/ do Cloudflare R2 přes `wrangler r2 object put` (přihlášení řeší wrangler sám,
// bez S3 klíčů a rclone). Navazuje: co už je nahrané, přeskočí podle nasazeni/r2_manifest_<bucket>.json.
// Porovnává se OBSAH (sha256), ne čas změny: dzi.py přepíše všechny dlaždice čtverce, ale po opravě jedné dominanty
// se změní jen pár dlaždic, ostatní mají stejné bajty a nahrávat se nemusí. Starý záznam "velikost:čas" se při
// prvním běhu převede na hash, pokud soubor od posledního nahrání nikdo nezměnil.
//
// Použití (z izohradec/):  node skripty/nahrat_dlazdice_r2.mjs <bucket> [--paralelne 16] [--dry-run]
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, existsSync, mkdirSync, statSync, readdirSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

const ROOT = new URL('..', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const IZOMAPA = join(ROOT, 'izomapa');
const SITE = join(IZOMAPA, 'site');
const WRANGLER = join(IZOMAPA, 'node_modules', 'wrangler', 'bin', 'wrangler.js');
const args = process.argv.slice(2);
const BUCKET = args.find((a, i) => !a.startsWith('--') && args[i - 1] !== '--paralelne' && args[i - 1] !== '--prefix');
const PAR = +(args[args.indexOf('--paralelne') + 1] || 0) || 16;
const DRY = args.includes('--dry-run');
const PREFIX = (args[args.indexOf('--prefix') + 1] && args.includes('--prefix')) ? args[args.indexOf('--prefix') + 1].replace(/^\/+|\/+$/g, '') + '/' : '';   // např. --prefix test: dlaždice pod test/tiles/…, produkce zůstává nedotčená
if (!BUCKET) { console.error('chybí název bucketu'); process.exit(1); }

const walk = (d) => readdirSync(d, { withFileTypes: true }).flatMap((e) => e.isDirectory() ? walk(join(d, e.name)) : [join(d, e.name)]);
const files = walk(join(SITE, 'tiles'));
mkdirSync(join(ROOT, 'nasazeni'), { recursive: true });
const MAN = join(ROOT, 'nasazeni', `r2_manifest_${BUCKET}${PREFIX ? '_' + PREFIX.replace(/\W+/g, '') : ''}.json`);
const man = existsSync(MAN) ? JSON.parse(readFileSync(MAN, 'utf8')) : {};
const sha = (f) => createHash('sha256').update(readFileSync(f)).digest('hex').slice(0, 32);
const todo = files.map((f) => { const s = statSync(f); return { f, key: PREFIX + relative(SITE, f).split(sep).join('/'), old: `${s.size}:${Math.floor(s.mtimeMs)}`, size: s.size }; })
  .filter((x) => {
    const m = man[x.key];
    if (m === x.old) { man[x.key] = x.hash = sha(x.f); return false; }          // starý záznam, soubor beze změny -> jen převést na hash
    x.hash = sha(x.f);
    return m !== x.hash;
  });
const total = todo.reduce((a, x) => a + x.size, 0);
console.log(`souborů ${files.length}, k nahrání ${todo.length} (${(total / 1e6).toFixed(0)} MB) do ${BUCKET}, paralelně ${PAR}`);
writeFileSync(MAN, JSON.stringify(man));   // uloží i převod starých záznamů na hash
if (DRY || !todo.length) process.exit(0);

const TYPES = { webp: 'image/webp', png: 'image/png', jpg: 'image/jpeg', json: 'application/json', dzi: 'application/xml', xml: 'application/xml' };
const run = (x) => new Promise((res) => {
  const p = spawn(process.execPath, [WRANGLER, 'r2', 'object', 'put', `${BUCKET}/${x.key}`, '--file', x.f, '--remote',
    '--content-type', TYPES[x.key.split('.').pop()] || 'application/octet-stream',
    '--cache-control', 'public, max-age=31536000, immutable'], { cwd: IZOMAPA, stdio: ['ignore', 'ignore', 'pipe'] });
  let err = ''; p.stderr.on('data', (d) => { err += d; });
  p.on('close', (code) => res(code === 0 ? '' : err.trim().split('\n').slice(-3).join(' ') || `exit ${code}`));
});

let done = 0, bytes = 0, i = 0, lastSave = Date.now();
const failed = [], t0 = Date.now();
await Promise.all(Array.from({ length: PAR }, async () => {
  while (i < todo.length) {
    const x = todo[i++];
    let e = 'x';
    for (let a = 0; a < 4 && e; a++) { e = await run(x); if (e) await new Promise((r) => setTimeout(r, 2000 * 2 ** a)); }
    if (e) failed.push(`${x.key}: ${e}`); else man[x.key] = x.hash;
    done++; bytes += x.size;
    if (Date.now() - lastSave > 15000) {
      lastSave = Date.now(); writeFileSync(MAN, JSON.stringify(man));
      const s = (Date.now() - t0) / 1000;
      console.log(`${done}/${todo.length}  ${(bytes / 1e6).toFixed(0)}/${(total / 1e6).toFixed(0)} MB  ${(bytes / 1e6 / s).toFixed(1)} MB/s  chyb ${failed.length}`);
    }
  }
}));
writeFileSync(MAN, JSON.stringify(man));
console.log(`hotovo za ${((Date.now() - t0) / 60000).toFixed(1)} min, chyb ${failed.length}`);
if (failed.length) { console.log(failed.slice(0, 20).join('\n')); process.exit(1); }
