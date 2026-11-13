"""Kontrolní obrázky tras MHD: pro každou linku trasa z mhd.json obarvená podle kvality úseků, relace z OSM a čára města.

python ../skripty/mhd_trasy_kontrola.py [linka ...]     (z izomapa/, po mhd.py) -> preview/mhd_trasy/<linka>.png + index.html
Barvy: zelená jistý úsek (OSM i město), modrozelená jen OSM, žlutá jen město, fialová rozpor OSM × město, červená nejistý.
Podklad: světle modrá široká = relace linky v OSM, oranžová čárkovaná = mapa linek magistrátu, šedé = silnice.
"""
import json, math, os, re, sys
from collections import defaultdict
import pyarrow.parquet as pq, shapely, shapely.ops
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '.')
from geo import to_local

D = json.load(open('site/mhd.json', encoding='utf-8'))
REF = json.load(open('assets/mhd_trasy_ref.json', encoding='utf-8'))
os.makedirs('preview/mhd_trasy', exist_ok=True)
ll = lambda q: [tuple(float(v) for v in to_local(b, a)) for a, b in q]
base = lambda n: (re.match(r'\d+', n) or [n])[0]
KC = {'j': (40, 160, 70), 'o': (30, 150, 160), 'm': (225, 180, 20), 'r': (190, 40, 190), 'n': (220, 30, 30)}
roads = []
for r in pq.read_table('data_all/segment.parquet', columns=['subtype', 'class', 'geometry']).to_pylist():
    if r['subtype'] == 'road' and r['class'] in ('motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'unclassified', 'living_street', 'service'):
        g = shapely.from_wkb(r['geometry'])
        for l in getattr(g, 'geoms', [g]): roads.append(ll([(la, lo) for lo, la in l.coords]))
by_line = defaultdict(set)
for t in D['trips']: by_line[D['routes'][t[0]][0]].add(t[1])
want = sys.argv[1:] or sorted(by_line, key=lambda x: (len(base(x)), base(x), x))
try: FONT = ImageFont.truetype('arial.ttf', 22)
except Exception: FONT = ImageFont.load_default()
rows = []
for ln in want:
    shs = sorted(by_line.get(ln, []))
    if not shs: continue
    pts = [p for s in shs for p in D['shapes'][s]]
    x0, x1 = min(p[0] for p in pts) - 150, max(p[0] for p in pts) + 150
    y0, y1 = min(p[1] for p in pts) - 150, max(p[1] for p in pts) + 150
    S = 1500 / max(x1 - x0, y1 - y0)
    W, H = int((x1 - x0) * S), int((y1 - y0) * S)
    im = Image.new('RGB', (W, H), (250, 250, 247)); dr = ImageDraw.Draw(im)
    P = lambda q: [((x - x0) * S, (y1 - y) * S) for x, y in q]
    box = shapely.box(x0, y0, x1, y1)
    for q in roads:
        if len(q) > 1 and box.intersects(shapely.LineString(q)): dr.line(P(q), fill=(210, 210, 205), width=1)
    for r in REF['osm']:
        if r['ref'] in (ln, base(ln)):
            for w in r['ways']: dr.line(P(ll(w)), fill=(160, 205, 245), width=11, joint='curve')
    for k, ws in REF['mesto'].items():
        if k in (ln, base(ln)):
            for w in ws:
                q = P(ll(w))
                for a, b in zip(q, q[1:]):
                    L = math.dist(a, b); n = max(1, int(L / 12))
                    for i in range(0, n, 2): dr.line([(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n), (a[0] + (b[0] - a[0]) * (i + 1) / n, a[1] + (b[1] - a[1]) * (i + 1) / n)], fill=(245, 140, 30), width=5)
    cnt = defaultdict(float)
    for s in shs:
        sh = shapely.LineString(D['shapes'][s])
        dr.line(P(sh.coords), fill=KC['j'], width=3)
        cnt['j'] += sh.length
        for a, b, k in D.get('kvalita', {}).get(str(s), []):
            seg = shapely.ops.substring(sh, a, b)
            if seg.length > 0: dr.line(P(seg.coords), fill=KC[k], width=4); cnt[k] += seg.length; cnt['j'] -= seg.length
    dr.text((10, 8), f'Linka {ln}: zelená jistý, modrozelená jen OSM, žlutá jen město, fialová rozpor, červená nejistý', fill=(0, 0, 0), font=FONT)
    im.save(f'preview/mhd_trasy/{ln}.png')
    tot = sum(cnt.values()) or 1
    rows.append((ln, {k: round(v) for k, v in cnt.items() if v > 1}, round(100 * cnt['j'] / tot)))
    print(ln, rows[-1][1])
html = ['<!doctype html><meta charset="utf-8"><title>Trasy MHD – kontrola</title><style>body{font:14px system-ui;margin:16px}img{max-width:100%;border:1px solid #ccc}</style>',
        '<h1>Trasy MHD – kontrola</h1><p>Zelená jistý úsek (OSM i mapa města), modrozelená jen OSM, žlutá jen mapa města, fialová rozpor, červená nejistý.</p>']
for ln, c, pj in rows: html.append(f'<h2>Linka {ln} – jisté {pj} %</h2><p>{c}</p><img src="{ln}.png" loading="lazy">')
open('preview/mhd_trasy/index.html', 'w', encoding='utf-8').write('\n'.join(html))
