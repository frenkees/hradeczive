// Statický rozpis zápasů FC Hradec Králové (záloha, když neběží /api/zapasy, např. lokální náhled).
// node skripty/zapasy.mjs [výstup.json]   (výchozí izomapa/site/zapasy.json)
import { writeFileSync } from 'node:fs';
import { nactiZapasy } from './vercel_api/zapasy.js';

const out = process.argv[2] || new URL('../izomapa/site/zapasy.json', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const d = await nactiZapasy();
d.staticky = true;
writeFileSync(out, JSON.stringify(d));
const doma = d.zapasy.filter((z) => z.doma && z.t && Date.parse(z.t) > Date.now());
console.log(out, 'zápasů', d.zapasy.length, 'domácích budoucích', doma.length, doma[0] ? `další: ${doma[0].datum} ${doma[0].cas} ${doma[0].hoste}` : '');
