"""Místní dashboard projektu (jen čtení + otevírání): render, git, nasazení, doména, hlášení z mapy. Běží na 127.0.0.1:8765, bez závislostí.
Spuštění: python skripty/dashboard/server.py   (ikona v liště: python skripty/dashboard/tray.py)"""
import json, os, re, subprocess, threading, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IZO = ROOT / 'izomapa'
LOG = IZO / 'build' / 'postav_render.log'
PORT = 8765
CHUNKS = 16
CACHE, LOCK = {}, threading.Lock()


def sh(cmd, cwd=None, timeout=25):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout, shell=isinstance(cmd, str))
        return (r.stdout or '').strip()
    except Exception:
        return ''


def cached(key, ttl, fn):
    with LOCK:
        t, v = CACHE.get(key, (0, None))
    if time.time() - t < ttl and v is not None: return v
    try: v = fn()
    except Exception as e: v = {'chyba': str(e)}
    with LOCK: CACHE[key] = (time.time(), v)
    return v


def render():
    if not LOG.exists(): return {'stav': 'nic', 'hotovo': [], 'celkem': CHUNKS}
    txt = LOG.read_text(encoding='utf-8', errors='replace')
    done = [{'ctverec': m[0], 's': int(m[1]), 'prep': int(m[2]), 'render': int(m[3]), 'dzi': int(m[4])}
            for m in re.findall(r'hotovo (-?\d+,-?\d+) za (\d+) s \(prep (\d+) s, render (\d+) s, dzi (\d+) s\)', txt)]
    age = time.time() - LOG.stat().st_mtime
    par = int((re.findall(r'souběžně (\d+)', txt) or ['4'])[-1])
    chyba = bool(re.search(r'Traceback|Error:|FAILED|Killed', txt))
    konec = 'Hotovo.' in txt
    stav = 'hotovo' if konec else 'chyba' if chyba and age > 120 else 'bezi' if age < 900 else 'stoji'
    eta = None
    if done and stav == 'bezi' and len(done) < CHUNKS:
        eta = round((CHUNKS - len(done)) * (sum(d['s'] for d in done) / len(done)) / par)
    return {'stav': stav, 'hotovo': done, 'celkem': CHUNKS, 'eta_s': eta, 'paralelne': par, 'ticho_s': round(age),
            'posledni': txt.strip().splitlines()[-1][:160] if txt.strip() else ''}


def git():
    out = {}
    for n, p in (('izomapa', IZO), ('koren', ROOT)):
        out[n] = {'commity': sh(['git', 'log', '--format=%h|%ar|%s', '-5'], p).splitlines(),
                  'zmeny': len([l for l in sh(['git', 'status', '--short'], p).splitlines() if l.strip()]),
                  'vetev': sh(['git', 'branch', '--show-current'], p)}
    return out


def nasazeni():
    txt = sh('vercel ls', ROOT / 'nasazeni' / 'vercel', 40)
    return {'radky': [l.strip() for l in txt.splitlines() if 'vercel.app' in l][:4]}


def domena():
    out = {}
    for h in ('hradeczive.cz', 'hradeczive.eu', 'hradeczive.vercel.app'):
        try:
            rq = urllib.request.Request(f'https://{h}/', method='HEAD', headers={'user-agent': 'dashboard'})
            out[h] = urllib.request.urlopen(rq, timeout=8).status
        except urllib.error.HTTPError as e: out[h] = e.code
        except Exception: out[h] = 0
    return out


def hlaseni():
    j = sh(['gh', 'issue', 'list', '--repo', 'frenkees/hradeczive', '--label', 'z-mapy', '--state', 'open', '--json', 'number,title,createdAt,url', '--limit', '20'], ROOT, 30)
    try: return {'otevrena': json.loads(j or '[]')}
    except Exception: return {'otevrena': [], 'chyba': 'gh nedostupné'}


def fronta():
    f = ROOT / 'STAV_PROJEKTU.md'
    if not f.exists(): return {'polozky': []}
    txt = f.read_text(encoding='utf-8', errors='replace')
    m = re.search(r'## Čeká na překreslení.*?\n(.*?)(?=\n## )', txt, re.S)
    pol = [re.sub(r'\*\*', '', l.strip('- ').strip())[:140] for l in (m.group(1).splitlines() if m else []) if l.startswith('- ')]
    return {'polozky': pol}


def stav():
    return {'cas': time.strftime('%H:%M:%S'), 'render': render(), 'git': cached('git', 20, git), 'nasazeni': cached('nas', 90, nasazeni),
            'domena': cached('dom', 60, domena), 'hlaseni': cached('hl', 120, hlaseni), 'fronta': cached('fr', 60, fronta)}


OPEN = {'mapa-lokalne': 'http://localhost:8123/', 'mapa': 'https://hradeczive.cz/', 'slozka': str(IZO), 'stav': str(ROOT / 'STAV_PROJEKTU.md'), 'log': str(LOG)}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def send(self, code, body, ctype):
        b = body if isinstance(body, bytes) else body.encode('utf-8')
        self.send_response(code); self.send_header('content-type', ctype); self.send_header('cache-control', 'no-store')
        self.send_header('content-length', str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if self.path == '/api/stav': return self.send(200, json.dumps(stav(), ensure_ascii=False), 'application/json; charset=utf-8')
        if self.path.startswith('/otevri/'):
            k = self.path.split('/', 2)[2]
            if k in OPEN:
                t = OPEN[k]
                os.startfile(t) if os.name == 'nt' else subprocess.Popen(['xdg-open', t])
                return self.send(200, '{"ok":true}', 'application/json')
            return self.send(404, '{"ok":false}', 'application/json')
        if self.path in ('/', '/index.html'): return self.send(200, (Path(__file__).parent / 'index.html').read_text(encoding='utf-8'), 'text/html; charset=utf-8')
        self.send(404, 'nenalezeno', 'text/plain')


if __name__ == '__main__':
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), H)
    print(f'Dashboard: http://127.0.0.1:{PORT}/'); srv.serve_forever()
