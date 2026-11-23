// Soukromá data k hlášením z webu (fotky, e-maily autorů) jsou ve Vercel Blob (privátní store), NE v gitu.
// Použití (z izohradec/), potřebuje BLOB_READ_WRITE_TOKEN (vercel env pull) v prostředí:
//   node skripty/hlaseni_soukrome.mjs seznam                      přehled hlášení, ke kterým je fotka/kontakt
//   node skripty/hlaseni_soukrome.mjs foto <číslo>                stáhne fotky do izomapa/landmarks_ref/hlaseni_<číslo>/ (v .gitignore)
//   node skripty/hlaseni_soukrome.mjs oznam <číslo> "text"        pošle autorovi zprávu o stavu (RESEND_API_KEY, MAIL_FROM)
// Nic z toho se neukládá do repozitáře.
import { list, get } from '@vercel/blob';
import { mkdirSync, writeFileSync } from 'node:fs';
const [cmd, cislo, ...txt] = process.argv.slice(2);
if (!process.env.BLOB_READ_WRITE_TOKEN) { console.error('chybí BLOB_READ_WRITE_TOKEN'); process.exit(1); }
const vse = async (prefix) => { const out = []; let cursor; do { const r = await list({ prefix, cursor }); out.push(...r.blobs); cursor = r.cursor; } while (cursor); return out; };
const cti = async (p) => { const r = await get(p, { access: 'private' }); return Buffer.from(await new Response(r.stream).arrayBuffer()); };
if (cmd === 'seznam') {
  const m = new Map(); for (const b of await vse('hlaseni/')) { const [, c, f] = b.pathname.split('/'); const o = m.get(c) || { foto: 0, kontakt: false }; f.startsWith('foto-') ? o.foto++ : o.kontakt = true; m.set(c, o); }
  for (const [c, o] of [...m].sort((a, b) => a[0] - b[0])) console.log(`#${c}: fotek ${o.foto}, kontakt ${o.kontakt ? 'ano' : 'ne'}`);
} else if (cmd === 'foto' && cislo) {
  const dir = `izomapa/landmarks_ref/hlaseni_${cislo}`; mkdirSync(dir, { recursive: true });
  for (const b of (await vse(`hlaseni/${cislo}/`)).filter((x) => x.pathname.includes('/foto-'))) { const f = `${dir}/${b.pathname.split('/').pop()}`; writeFileSync(f, await cti(b.pathname)); console.log(f); }
} else if (cmd === 'oznam' && cislo && txt.length) {
  const { email } = JSON.parse((await cti(`hlaseni/${cislo}/kontakt.json`)).toString());
  const r = await fetch('https://api.resend.com/emails', { method: 'POST', headers: { authorization: `Bearer ${process.env.RESEND_API_KEY}`, 'content-type': 'application/json' },
    body: JSON.stringify({ from: process.env.MAIL_FROM, to: [email], subject: `Hlášení č. ${cislo} – Hradec živě`, text: `${txt.join(' ')}\n\nDěkujeme, že pomáháte mapě.\nHradec živě` }) });
  console.log(r.ok ? 'odesláno' : 'chyba ' + r.status);
} else console.error('seznam | foto <č> | oznam <č> "text"');
