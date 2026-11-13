// Snímek prohlížeče mapy: node ../skripty/screenshot.mjs <url> <výstup.png> [čekání ms]
import { chromium } from 'playwright';
const [url, out, wait = '9000'] = process.argv.slice(2);
const b = await chromium.launch({ args: ['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
const errs = [];
p.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
p.on('console', (m) => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
await p.goto(url); await p.waitForTimeout(+wait);
await p.screenshot({ path: out });
console.log(errs.length ? errs.join('\n') : 'bez chyb');
await b.close();
