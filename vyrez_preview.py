"""Výřezy z plného náhledu build/pilot_<v>.png kolem bodů (lat, lon) -> preview/"""
import json, sys
from PIL import Image
sys.path.insert(0, '.')
import geo
Image.MAX_IMAGE_PIXELS = None
MIS = {'velke_namesti': (50.20932, 15.83300), 'soutok': (50.20416, 15.82496), 'hucak_gymnazium': (50.20780, 15.82650),
       'ulrichovo': (50.21053, 15.82211), 'katedrala_bila_vez': (50.20888, 15.83067)}
for v in ('summer', 'lights'):
    im = Image.open(f'build/pilot_{v}.png'); m = json.load(open(f'build/pilot_{v}.json'))
    for k, (la, lo) in MIS.items():
        x, y = geo.to_local(lo, la); vx, vy, _ = geo.view(x, y, 0)
        px, py = (vx - m['x0']) / m['mpp'], (m['y1'] - vy) / m['mpp']
        W, H = 1600, 1000
        im.crop((int(px - W / 2), int(py - H / 2), int(px + W / 2), int(py + H / 2))).save(f'preview/{v}_{k}.png')
    print(v, 'ok')
