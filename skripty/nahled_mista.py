"""Rychlý náhled jednoho místa čtverce (0,0): vyrenderuje jen dlaždice kolem bodu a vyřízne výřez.

python ../skripty/nahled_mista.py <lat> <lon> <výstup.png> [season=summer] [w=900] [h=1100] [vyska=35] [c=i,j]
Spouštět z izomapa/ po prep.py daného čtverce (c=0,0 výchozí). Bod je pata stavby; výřez se posune nahoru o polovinu výšky stavby.
"""
import json, math, os, subprocess, sys
from PIL import Image
sys.path.insert(0, '.')
import geo

la, lo, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
kw = dict(a.split('=') for a in sys.argv[4:])
season = kw.get('season', 'summer'); W = int(kw.get('w', 900)); H = int(kw.get('h', 1100)); vys = float(kw.get('vyska', 35))
mode = 'lights' if season == 'lights' else 'day'
c = tuple(int(v) for v in kw.get('c', '0,0').split(',')); D = geo.chunk_dir(c)
info = json.load(open(f'{D}/tiles_summer/info.json'))
x, y = geo.to_local(lo, la); vx, vy, _ = geo.view(float(x), float(y), vys / 2)
px, py = (vx - info['x0']) / info['mpp'], (info['y1'] - vy) / info['mpp']
T = info['tile']; x0, y0, x1, y1 = px - W / 2, py - H / 2, px + W / 2, py + H / 2
tiles = [f'{i}_{j}' for i in range(int(x0 // T), int(x1 // T) + 1) for j in range(int(y0 // T), int(y1 // T) + 1)]
od = f'{D}/nahled_mista'
G = ['gx0=-1646.34559672906', 'gy1=988.7958500237901']
subprocess.run(['node', 'render.mjs', 'mpp=0.2', f'dir={D}', f'out={od}', f'season={"autumn" if mode == "lights" else season}', f'mode={mode}', 'alpha=1', *G,
                'tiles=' + ';'.join(tiles)], check=True, stdout=subprocess.DEVNULL)
img = Image.new('RGBA', (W, H), (27, 35, 51, 255))
for t in tiles:
    i, j = map(int, t.split('_'))
    im = Image.open(f'{od}/{t}.png').convert('RGBA')
    img.paste(im, (int(i * T - x0), int(j * T - y0)), im)
img.save(out)
print(out, tiles)
