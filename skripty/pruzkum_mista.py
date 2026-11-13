"""Podklady pro modelování stavby: ortofoto ČÚZK kolem bodu a seznam budov z dat (výška z laseru, rozměry, natočení).

python ../skripty/pruzkum_mista.py <klíč> <lat> <lon> [poloměr_m=90]   (spouštět z izomapa/)
-> preview/orto_<klíč>.jpg (sever nahoře, 0,25 m/px) a výpis budov do vzdálenosti poloměru
"""
import json, math, subprocess, sys
import numpy as np, pyarrow.parquet as pq, shapely
sys.path.insert(0, '.')
import geo

key, la, lo = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); R = float(sys.argv[4]) if len(sys.argv) > 4 else 90.0
dla, dlo = R / 110574, R / geo.KX
px = int(2 * R / 0.25)
subprocess.run(['curl', '-s', '-m', '90', '-o', f'preview/orto_{key}.jpg',
                'https://ags.cuzk.gov.cz/arcgis1/services/ORTOFOTO/MapServer/WMSServer?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=0&STYLES='
                f'&CRS=EPSG:4326&BBOX={la - dla},{lo - dlo},{la + dla},{lo + dlo}&WIDTH={px}&HEIGHT={px}&FORMAT=image/jpeg'], check=True)
dmp = json.load(open('assets/dmp_vysky.json'))
pt = shapely.Point(lo, la); cx, cy = geo.to_local(lo, la)
rows = []
for r in pq.read_table('data_all/building.parquet', columns=['id', 'names', 'class', 'height', 'roof_shape', 'geometry']).to_pylist():
    g = shapely.from_wkb(r['geometry'])
    if g.distance(pt) * geo.KX > R or g.geom_type != 'Polygon': continue
    x, y = geo.to_local(*zip(*g.exterior.coords)); P = shapely.Polygon(list(zip(x, y)))
    if P.area < 60: continue
    o = P.minimum_rotated_rectangle; cs = list(o.exterior.coords)
    e = [math.dist(cs[i], cs[i + 1]) for i in range(2)]; k = int(e[1] > e[0])
    ang = math.degrees(math.atan2(cs[k + 1][1] - cs[k][1], cs[k + 1][0] - cs[k][0])) % 180
    c = g.centroid
    rows.append((P.area, r['id'][:8], (r.get('names') or {}).get('primary'), r['class'], r['height'], r.get('roof_shape'), dmp.get(r['id']),
                 [round(max(e)), round(min(e))], round(ang), f'{c.y:.6f},{c.x:.6f}', (round(P.centroid.x - float(cx)), round(P.centroid.y - float(cy)))))
for q in sorted(rows, reverse=True)[:14]:
    print(f'{q[0]:7.0f} m² {q[1]} {str(q[2])[:28]:28s} {q[3]} h={q[4]} {q[5]} laser={q[6]} {q[7]} m osa {q[8]}° {q[9]} vůči bodu {q[10]}')
