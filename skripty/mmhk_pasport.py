# Data Magistrátu města Hradec Králové (geoportal.mmhk.cz) pro upřesnění mapy:
#   pasport komunikací (WFS pakom): plochy povrchů (vozovka/chodník/schodiště, materiál), parkoviště, řady parkovacích stání
#   vodorovné dopravní značení (WMS pakom, městská symbologie -> maska po 0,1 m v dlaždicích 200 m)
#   pasport zeleně (WFS pazel-sec): stromy a keře (druh, taxon), plochy zeleně (trávník, záhon, keře…), parky
#   veřejné osvětlení (WFS pvohk): stožáry lamp
#   DTMM (ArcGIS REST): opěrné zdi a zábradlí
# Výšky stromů z mračna bodů DMP 1G (build/dmp/*.laz, třída 5 = vysoká vegetace).
# Parkovací stání: z řad stání (značky 486 podélné, 487 kolmé/šikmé, 488 šikmé) a z masky značení se změří úhel a dělicí čáry.
# Výstup: izomapa/assets/mmhk.json + izomapa/assets/mmhk_znaceni/<tx>_<ty>.png (+ index.json), čte je assets/custom_prep.py.
#
# Spouštět z izomapa/:  PYTHONUTF8=1 .venv/Scripts/python ../skripty/mmhk_pasport.py [lat0 lon0 lat1 lon1]   (bez oblasti = celá mapa)
# Stažené části se ukládají do build/mmhk_cache/, opakované spuštění je přeskočí (--znovu = stáhnout znovu).
import sys, os, json, math, glob, time, io, hashlib, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
import numpy as np, laspy, shapely
from shapely.geometry import shape, Point, LineString
from pyproj import Transformer
from PIL import Image
sys.path.insert(0, '.')
import geo
Image.MAX_IMAGE_PIXELS = None

args = [a for a in sys.argv[1:] if not a.startswith('--')]
if len(args) >= 4:
    LAT0, LON0, LAT1, LON1 = (float(v) for v in args[:4])
else:
    lo0, lo1, la0, la1 = geo.bbox_lonlat(100.0); LAT0, LON0, LAT1, LON1 = la0, lo0, la1, lo1
ZNOVU = '--znovu' in sys.argv
TO_K = Transformer.from_crs(4326, 5514, always_xy=True)
TO_W = Transformer.from_crs(5514, 4326, always_xy=True)
xs, ys = TO_K.transform([LON0, LON1, LON0, LON1], [LAT0, LAT0, LAT1, LAT1])
X0, X1, Y0, Y1 = min(xs), max(xs), min(ys), max(ys)
G = 'https://geoportal.mmhk.cz/services/mapserver'
A = 'https://geoportal.mmhk.cz/arcgis/rest/services/thematic_urad/dtmm_komplet/MapServer/35/query'
UA = {'User-Agent': 'izomapa'}
CACHE = 'build/mmhk_cache'; os.makedirs(CACHE, exist_ok=True)
print(f'oblast {LAT0:.4f},{LON0:.4f} – {LAT1:.4f},{LON1:.4f} ({(X1 - X0) / 1000:.1f} × {(Y1 - Y0) / 1000:.1f} km)', flush=True)


def get(url, data=None, tries=8):
    for a in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=UA), timeout=180).read()
        except Exception as e:
            if a == tries - 1: raise
            print('  znovu', str(e)[:80], flush=True); time.sleep(3 * (a + 1))


def cached(key, fn):
    f = f'{CACHE}/{hashlib.md5(key.encode()).hexdigest()}.json'
    if os.path.exists(f) and not ZNOVU: return json.load(open(f, encoding='utf-8'))
    v = fn()
    if v is not None: json.dump(v, open(f, 'w', encoding='utf-8'))
    return v


LIM = 10000


def wfs_box(svc, typ, x0, y0, x1, y1):
    q = urllib.parse.urlencode({'service': 'WFS', 'request': 'GetFeature', 'version': '1.1.0', 'outputformat': 'json',
                                'typeName': typ, 'maxFeatures': LIM, 'bbox': f'{x0},{y0},{x1},{y1},EPSG:5514'})
    def _f():
        for a in range(3):
            try: return json.loads(get(f'{G}/{svc}/gservice?{q}'))['features']
            except ValueError: time.sleep(5 * (a + 1))          # prázdná odpověď (přetížený server): znovu
        return None
    try:
        fs = cached(f'{svc}|{typ}|{x0:.0f}|{y0:.0f}|{x1:.0f}|{y1:.0f}', _f)
    except TypeError:
        fs = None
    if fs is None:                                                       # ani na potřetí: menší dlaždice
        if x1 - x0 < 100: raise SystemExit(f'{typ}: služba neodpovídá ani pro {x0:.0f},{y0:.0f}')
        fs = [None] * LIM
    if len(fs) >= LIM or (len(fs) >= 1000 and len(fs) % 1000 == 0):     # limit služby (některé vrací max. 1000): rozdělit
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        return sum((wfs_box(svc, typ, *b) for b in ((x0, y0, mx, my), (mx, y0, x1, my), (x0, my, mx, y1), (mx, my, x1, y1))), [])
    return fs


def wfs(svc, typ, step=1500.0):
    boxes = [(x, y, min(x + step, X1), min(y + step, Y1)) for x in np.arange(X0, X1, step) for y in np.arange(Y0, Y1, step)]
    out = {}
    with ThreadPoolExecutor(4) as ex:
        for fs in ex.map(lambda b: wfs_box(svc, typ, *b), boxes):
            for f in fs: out[f['properties'].get('ogc_fid', f.get('id'))] = f
    print(f'{typ}: {len(out)}', flush=True)
    return list(out.values())


def wgs(coords):                                   # [[x, y], …] S-JTSK -> [[lat, lon], …]
    a = np.asarray(coords, float)[:, :2]; lo, la = TO_W.transform(a[:, 0], a[:, 1])
    return [[round(float(b), 7), round(float(c), 7)] for b, c in zip(la, lo)]


def polys(g):
    if g is None: return []
    if g['type'] == 'Polygon': return [g['coordinates']]
    if g['type'] == 'MultiPolygon': return g['coordinates']
    return []


def rings(g):
    return [{'o': wgs(p[0]), 'h': [wgs(h) for h in p[1:] if len(h) >= 4]} for p in polys(g) if len(p[0]) >= 4]


def lines_of(g):
    if g is None: return []
    if g['type'] == 'LineString': return [g['coordinates']]
    if g['type'] == 'MultiLineString': return g['coordinates']
    return []


# ---------- povrchy komunikací ----------
POV, KOM = [], []
for f in wfs('common/pakom', 'pk-pov'):
    p = f['properties']
    for r in rings(f['geometry']):
        POV.append({**r, 'typ': p.get('typ') or '', 'mat': p.get('material') or '', 'tr': p.get('komunikace_trida') or ''})
    if (p.get('typ') or '') == 'komunikace':
        try: KOM.append(shape(f['geometry']).buffer(0))
        except Exception: pass
PARK = [r for f in wfs('common/pakom', 'pk-park-p') for r in rings(f['geometry'])]
ROWS = [(f['properties'].get('druh_vodorovne_znacky_tid'), l) for f in wfs('common/pakom', 'pk-dzv-l')
        if f['properties'].get('druh_vodorovne_znacky_tid') in (486, 487, 488) for l in lines_of(f['geometry']) if len(l) >= 2]
print('řad parkovacích stání', len(ROWS), flush=True)

# ---------- zeleň ----------
BIOP = []
for f in wfs('common/pazel-sec', 'ibiops'):
    for r in rings(f['geometry']): BIOP.append({**r, 'druh': f['properties'].get('druh_nazev') or ''})
PZ = []
for f in wfs('common/pazel-sec', 'pzplo'):
    for r in rings(f['geometry']): PZ.append({**r, 'nazev': f['properties'].get('nazev') or '', 'druh': f['properties'].get('druh_nazev') or ''})
kor = {}
for f in wfs('common/pazel-sec', 'den-kor'):
    g = f['geometry']
    if g and g['type'] in ('Point', 'MultiPoint') and g['coordinates']:
        c = g['coordinates'] if g['type'] == 'Point' else g['coordinates'][0]; kor[(round(c[0], 1), round(c[1], 1))] = f['properties'].get('velikost')
BIOB = []
for f in wfs('common/pazel-sec', 'ibiobs'):
    g = f['geometry']
    if not g or g['type'] not in ('Point', 'MultiPoint') or not g['coordinates']: continue
    p = f['properties']; x, y = (g['coordinates'] if g['type'] == 'Point' else g['coordinates'][0])[:2]
    BIOB.append({'x': x, 'y': y, 'druh': p.get('druh_nazev') or '', 'taxon': p.get('taxon') or '', 'kor': kor.get((round(x, 1), round(y, 1)))})

# výška stromů z DMP 1G: nejvyšší bod vysoké vegetace do 3 m od kmene minus terén (medián třídy 2 do 12 m), po listech
from scipy.spatial import cKDTree
TX = np.array([[t['x'], t['y']] for t in BIOB]) if BIOB else np.zeros((0, 2))
TH = np.full(len(BIOB), np.nan)
for fn in sorted(glob.glob('build/dmp/*.laz')):
    with laspy.open(fn) as l: h = l.header; mn, mx = h.mins, h.maxs
    sel = np.where((TX[:, 0] >= mn[0]) & (TX[:, 0] < mx[0]) & (TX[:, 1] >= mn[1]) & (TX[:, 1] < mx[1]))[0] if len(TX) else []
    if not len(sel): continue
    l = laspy.read(fn); P = np.column_stack([np.array(l.x), np.array(l.y), np.array(l.z)]); C = np.array(l.classification)
    V, Gr = P[C == 5], P[C == 2]
    if not len(V) or not len(Gr): continue
    tv, tg = cKDTree(V[:, :2]), cKDTree(Gr[:, :2])
    for i, iv, ig in zip(sel, tv.query_ball_point(TX[sel], 3.0), tg.query_ball_point(TX[sel], 12.0)):
        if iv and ig:
            hh = float(V[iv, 2].max() - np.median(Gr[ig, 2]))
            if 2 <= hh <= 40: TH[i] = round(hh, 1)
for t, hh in zip(BIOB, TH): t['h'] = None if np.isnan(hh) else float(hh)
print('stromů/keřů', len(BIOB), 's výškou z DMP', int((~np.isnan(TH)).sum()), flush=True)
if BIOB:
    ll = wgs(TX)
    for t, (la, lo) in zip(BIOB, ll): del t['x'], t['y']; t['lat'], t['lon'] = la, lo

LAMP = []
for f in wfs('local/pvohk', 'gpktechovostozar'):
    g = f['geometry']
    if g and g['type'] in ('Point', 'MultiPoint') and g['coordinates']:
        lat, lon = wgs([(g['coordinates'] if g['type'] == 'Point' else g['coordinates'][0])[:2]])[0]
        LAMP.append({'lat': lat, 'lon': lon, 'typ': f['properties'].get('typ_objektu') or ''})

# ---------- DTMM: opěrné zdi a zábradlí ----------
def dtmm(where):
    ids = cached(f'dtmm|ids|{where}', lambda: json.loads(get(A, urllib.parse.urlencode({'where': where, 'returnIdsOnly': 'true', 'f': 'json'}).encode()))['objectIds'])
    out = []
    for i in range(0, len(ids), 400):
        ch = ids[i:i + 400]
        fs = cached(f'dtmm|{where}|{ch[0]}|{len(ch)}', lambda: json.loads(get(A, urllib.parse.urlencode({
            'objectIds': ','.join(map(str, ch)), 'outFields': 'popis', 'returnGeometry': 'true', 'outSR': 5514, 'f': 'json'}).encode()))['features'])
        for f in fs:
            for path in (f.get('geometry') or {}).get('paths', []):
                a = np.asarray(path)
                if len(a) >= 2 and a[:, 0].max() > X0 and a[:, 0].min() < X1 and a[:, 1].max() > Y0 and a[:, 1].min() < Y1:
                    out.append((f['attributes']['popis'], a[:, :2]))
    print(where, len(out), flush=True)
    return out
ZDI = [{'k': 'v' if 'vzorovan' in p else 'h', 'q': wgs(a)} for p, a in dtmm("popis LIKE 'Op%'")]
ZABR = [wgs(a) for p, a in dtmm("popis LIKE 'Z_bradl_'")]

# ---------- vodorovné značení: WMS po 0,1 m/px v dlaždicích 200 m, jen kde jsou vozovky ----------
RES, T = 0.1, 2000; TM = RES * T
ZD = 'assets/mmhk_znaceni'; os.makedirs(ZD, exist_ok=True)
POVU = shapely.STRtree([shape({'type': 'Polygon', 'coordinates': [np.array(TO_K.transform(*np.array(r['o'])[:, ::-1].T)).T.tolist()]}).buffer(0)
                        for r in POV] or [Point(1e9, 1e9)])
tiles = [(i, j) for i in range(int(math.floor(X0 / TM)), int(math.ceil(X1 / TM))) for j in range(int(math.floor(Y0 / TM)), int(math.ceil(Y1 / TM)))
         if len(POVU.query(shapely.box(i * TM, j * TM, (i + 1) * TM, (j + 1) * TM)))]
print('dlaždic značení', len(tiles), flush=True)


def tile(ij):
    i, j = ij; f = f'{ZD}/{i}_{j}.png'
    if os.path.exists(f) and not ZNOVU: return ij, True
    if os.path.exists(f[:-4] + '.empty') and not ZNOVU: return ij, False
    q = urllib.parse.urlencode({'service': 'WMS', 'version': '1.1.1', 'request': 'GetMap', 'layers': 'pk-dzv-p,pk-dzv-l', 'styles': '',
                                'srs': 'EPSG:5514', 'bbox': f'{i * TM},{j * TM},{(i + 1) * TM},{(j + 1) * TM}', 'width': T, 'height': T,
                                'format': 'image/png', 'transparent': 'true'})
    if '--bez-site' in sys.argv: return ij, None
    try:
        time.sleep(0.4)                                   # šetrně: server po stovkách rychlých dotazů odmítá spojení
        a = np.asarray(Image.open(io.BytesIO(get(f'{G}/common/pakom/gservice?{q}', tries=3))).convert('RGBA')).astype(np.int16)
    except Exception as e:
        return ij, None                                   # chybí, doplní se dalším spuštěním
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    m = ((al > 128) & (r > 200) & (g > 200) & (b > 200)) | ((al > 128) & (r > 190) & (g > 160) & (b < 120))
    if not m.any(): open(f[:-4] + '.empty', 'w').close(); return ij, False
    Image.fromarray(m).save(f, optimize=True); return ij, True


done = 0; nonempty = []; missing = 0
with ThreadPoolExecutor(1) as ex:
    for ij, ok in ex.map(tile, tiles):
        done += 1; missing += ok is None
        if ok or os.path.exists(f'{ZD}/{ij[0]}_{ij[1]}.png'): nonempty.append(list(ij))
        if done % 100 == 0: print(f'značení {done}/{len(tiles)}', flush=True)
nonempty = [ij for ij in nonempty if os.path.exists(f'{ZD}/{ij[0]}_{ij[1]}.png')]
json.dump({'res': RES, 'tile': T, 'tiles': nonempty}, open(f'{ZD}/index.json', 'w'))
if missing: print('CHYBÍ dlaždic značení', missing, '(spusť skript znovu, stažené se přeskočí)', flush=True)
_TC = {}


def M(x, y):                                       # maska značení v bodech S-JTSK
    x, y = np.asarray(x, float), np.asarray(y, float); out = np.zeros(x.shape, bool)
    ti, tj = np.floor(x / TM).astype(int), np.floor(y / TM).astype(int)
    for i, j in set(zip(ti.ravel().tolist(), tj.ravel().tolist())):
        k = (i, j)
        if k not in _TC:
            f = f'{ZD}/{i}_{j}.png'; _TC[k] = np.asarray(Image.open(f)) > 0 if os.path.exists(f) else None
        a = _TC[k]
        if a is None: continue
        s = (ti == i) & (tj == j)
        c = np.clip(((x[s] - i * TM) / RES).astype(int), 0, T - 1); r = np.clip(((j + 1) * TM - y[s]) / RES, 0, T - 1).astype(int)
        out[s] = a[r, c]
    return out


# ---------- parkovací stání z řad stání + masky značení ----------
KT = shapely.STRtree(KOM) if KOM else None


def on_road(x, y):
    if KT is None: return False
    p = Point(x, y); return any(KOM[i].contains(p) for i in KT.query(p))


STANI = []
for druh, cs in ROWS:
    l = LineString(np.asarray(cs)[:, :2])
    if l.length < 4: continue
    mid = l.interpolate(0.5, normalized=True); a_ = l.interpolate(max(0, l.length / 2 - 1)); b_ = l.interpolate(min(l.length, l.length / 2 + 1))
    tx, ty = b_.x - a_.x, b_.y - a_.y; tl = math.hypot(tx, ty) or 1; tx, ty = tx / tl, ty / tl
    side = 0
    for d in (2.5, 1.5, 3.5):
        L_, R_ = on_road(mid.x - ty * d, mid.y + tx * d), on_road(mid.x + ty * d, mid.y - tx * d)
        if L_ != R_: side = 1 if L_ else -1; break
    S_ = np.arange(0.3, l.length - 0.3, 0.2)
    if not len(S_): continue
    pts = np.array([[p.x, p.y] for p in shapely.line_interpolate_point(l, S_)])
    dd = np.gradient(pts, axis=0); dd /= np.linalg.norm(dd, axis=1, keepdims=True) + 1e-9
    U = np.linspace(0.8, 4.2, 12)
    best = None
    for sg in ([side] if side else [1, -1]):
        nrm = np.stack([-dd[:, 1], dd[:, 0]], 1) * sg
        for ang in range(30, 151, 5):
            ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            dv = dd * ca + nrm * sa
            px = pts[:, None, 0] + dv[:, None, 0] * U[None, :]; py = pts[:, None, 1] + dv[:, None, 1] * U[None, :]
            cov = M(px, py).mean(1)
            sc = float((cov > 0.7).mean())
            if best is None or sc > best[0]: best = (sc, sg, ang, cov, dv, nrm)
    occ = lambda x, y: int(hashlib.md5(f'{x:.1f}{y:.1f}'.encode()).hexdigest()[:4], 16) / 65535
    if druh == 486 or best is None or best[0] < 0.02:
        if druh != 486 or not side: continue          # podélná stání: auta podél řady, 1,1 m do vozovky, po 5,8 m
        for s in np.arange(3.0, l.length - 2.5, 5.8):
            p = l.interpolate(s); q = l.interpolate(min(l.length, s + 1)); vx, vy = q.x - p.x, q.y - p.y; vl = math.hypot(vx, vy) or 1
            cx, cy = p.x - vy / vl * 1.1 * side, p.y + vx / vl * 1.1 * side
            if occ(cx, cy) < 0.75: STANI.append([cx, cy, cx + vx / vl, cy + vy / vl])
        continue
    sc, sg, ang, cov, dv, nrm = best
    hit = cov > 0.6; seps = []; i = 0
    while i < len(hit):
        if hit[i]:
            j = i
            while j + 1 < len(hit) and hit[j + 1]: j += 1
            seps.append((i + j) // 2); i = j + 1
        else: i += 1
    for a, b in zip(seps, seps[1:]):
        gap = (b - a) * 0.2
        if not 1.8 <= gap <= 4.8: continue
        k = (a + b) // 2; d = dv[k]
        cx, cy = pts[k, 0] + d[0] * 2.5, pts[k, 1] + d[1] * 2.5
        if occ(cx, cy) < 0.75: STANI.append([cx, cy, cx + d[0], cy + d[1]])
print('parkovacích stání s autem', len(STANI), flush=True)
STANI_W = [a + b for a, b in zip(wgs([[s[0], s[1]] for s in STANI]), wgs([[s[2], s[3]] for s in STANI]))] if STANI else []

json.dump({'zdroj': 'geoportal.mmhk.cz (Statutární město Hradec Králové): pasport komunikací, pasport zeleně, veřejné osvětlení, DTMM',
           'stazeno': time.strftime('%Y-%m-%d'), 'oblast': [LAT0, LON0, LAT1, LON1],
           'povrchy': POV, 'parkoviste': PARK, 'zelen': BIOP, 'parky': PZ, 'stromy': BIOB, 'lampy': LAMP,
           'stani': STANI_W, 'zdi': ZDI, 'zabradli': ZABR},
          open('assets/mmhk.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('hotovo: assets/mmhk.json', {k: len(v) for k, v in (('povrchy', POV), ('zelen', BIOP), ('stromy', BIOB), ('lampy', LAMP),
                                                          ('stani', STANI_W), ('zdi', ZDI), ('zabradli', ZABR))}, flush=True)
