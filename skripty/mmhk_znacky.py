"""Svislé dopravní značky z pasportu komunikací Magistrátu HK (WFS common/pakom, vrstva pk-dzs-z) -> klíč "znacky" v izomapa/assets/mmhk.json.

Spouštět z izomapa/:  python ../skripty/mmhk_znacky.py [--znovu]
Záznam: [lat, lon, kód značky (např. A15, B20a, IP12, E13), natočení°]. Stahuje se po dlaždicích 1,5 km, vlákna 3 (geoportál je citlivý na rychlé dotazy),
dlaždice se ukládají do build/mmhk_cache/ (znovu se nestahují). Kreslí je hook assets/custom_prep.py (fáze props) a model v render.html.
"""
import hashlib, json, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from pyproj import Transformer

G = 'https://geoportal.mmhk.cz/services/mapserver'
UA = {'User-Agent': 'izomapa'}
ZNOVU = '--znovu' in sys.argv
CACHE = 'build/mmhk_cache'; os.makedirs(CACHE, exist_ok=True)
M = json.load(open('assets/mmhk.json', encoding='utf-8'))
LAT0, LON0, LAT1, LON1 = M['oblast']
TO_S = Transformer.from_crs(4326, 5514, always_xy=True); TO_W = Transformer.from_crs(5514, 4326, always_xy=True)
xs, ys = TO_S.transform([LON0, LON1, LON0, LON1], [LAT0, LAT0, LAT1, LAT1])
X0, X1, Y0, Y1 = min(xs), max(xs), min(ys), max(ys)
LIM = 1000


def get(url):
    for a in range(8):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180).read()
        except Exception as e:
            if a == 7: raise
            print('  znovu', str(e)[:80], flush=True); time.sleep(3 * (a + 1))


def box(x0, y0, x1, y1):
    key = f'dzs-z|{x0:.0f}|{y0:.0f}|{x1:.0f}|{y1:.0f}'; f = f'{CACHE}/{hashlib.md5(key.encode()).hexdigest()}.json'
    if os.path.exists(f) and not ZNOVU: fs = json.load(open(f, encoding='utf-8'))
    else:
        q = urllib.parse.urlencode({'service': 'WFS', 'request': 'GetFeature', 'version': '1.1.0', 'outputformat': 'json', 'typeName': 'pk-dzs-z',
                                    'maxFeatures': 10000, 'bbox': f'{x0},{y0},{x1},{y1},EPSG:5514'})
        fs = None
        for a in range(3):
            try: fs = json.loads(get(f'{G}/common/pakom/gservice?{q}'))['features']; break
            except ValueError: time.sleep(5 * (a + 1))
        if fs is None: raise SystemExit(f'pk-dzs-z: služba neodpovídá pro {x0:.0f},{y0:.0f}')
        json.dump(fs, open(f, 'w', encoding='utf-8'))
    if len(fs) >= LIM and (x1 - x0) > 100 and len(fs) % 1000 == 0:        # možný limit služby: rozdělit
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        return sum((box(*b) for b in ((x0, y0, mx, my), (mx, y0, x1, my), (x0, my, mx, y1), (mx, my, x1, y1))), [])
    return fs


step = 1500.0
boxes = [(x, y, min(x + step, X1), min(y + step, Y1)) for x in np.arange(X0, X1, step) for y in np.arange(Y0, Y1, step)]
out = {}
with ThreadPoolExecutor(3) as ex:
    for fs in ex.map(lambda b: box(*b), boxes):
        for f in fs: out[f['properties'].get('ogc_fid', f.get('id'))] = f
pts, meta = [], []
for f in out.values():
    g, p = f.get('geometry'), f['properties']
    if not g or g['type'] != 'Point': continue
    sym = (p.get('sym') or '').rsplit('/', 1)[-1].rsplit('.', 1)[0]
    if not sym or p.get('platnost_znacky_tid') not in (1, None): continue
    pts.append(g['coordinates'][:2]); meta.append((sym, p.get('rotace') or 0))
ll = TO_W.transform(*np.asarray(pts, float).T) if pts else ([], [])
Z = [[round(la, 6), round(lo, 6), s, int(r) % 360] for lo, la, (s, r) in zip(ll[0], ll[1], meta)]
M['znacky'] = Z
json.dump(M, open('assets/mmhk.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
import collections
print('značek', len(Z), 'druhy', collections.Counter(re.sub(r'\d.*', '', s) if False else ''.join(c for c in s if c.isalpha())[:2] for _, _, s, _ in Z).most_common(14))
