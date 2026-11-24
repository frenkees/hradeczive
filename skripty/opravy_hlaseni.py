"""Opravy podle hlášení z mapy (GitHub issues frenkees/hradeczive) -> izomapa/assets/upresneni.json, klíč "b" (ruční opravy budov).

Spouštět z izomapa/:  PYTHONUTF8=1 .venv/Scripts/python ../skripty/opravy_hlaseni.py [--vypis lat lon poloměr]
Budova se najde podle bodu z hlášení (nejbližší do 15 m, jinak vyjmenované výběry). Klíče opravy čte prep.py:
  name, cls_cz (zobrazený druh), cls (třída pro pravidla), fl (podlaží), h (výška), r (střecha), wc/rc (barvy), sachta (výtahová šachta), skryt (zaniklá budova; zapíše se do "skryt_budovy").
Názvy a popisy podle návštěvníků jsou NEOVĚŘENÉ (viz poznámky v issues).
"""
import glob, json, math, sys
import pandas as pd
import pyarrow.parquet as pq
import shapely
import shapely.ops
from shapely.geometry import Point

sys.stdout.reconfigure(encoding='utf-8')
KY = 110574.0


def nacti():
    fr = []
    for f in glob.glob('data*/building.parquet'):
        t = pq.read_table(f).to_pandas(); t['geom'] = shapely.from_wkb(t.geometry.values)
        fr.append(t[['id', 'class', 'height', 'num_floors', 'geom']])
    return pd.concat(fr).drop_duplicates('id').reset_index(drop=True)


B = nacti()
RU = json.load(open('assets/ruian_budovy.json')); DMP = json.load(open('assets/dmp_vysky.json'))


def kx(lat): return math.cos(math.radians(lat)) * 111320.0


def nejblizsi(lat, lon, r=15.0, n=1):
    p = Point(lon, lat); k = kx(lat); out = []
    for i, g in zip(B.id, B.geom):
        if g.centroid.distance(p) > 0.001: continue
        d = g.distance(p) * min(k, KY)
        if d <= r: out.append((d, i))
    return [i for _, i in sorted(out)[:n]]


def vyber(lat, lon, rad, podm):
    k = kx(lat); out = []
    for r in B.itertuples():
        c = r.geom.centroid; dx, dy = (c.x - lon) * k, (c.y - lat) * KY
        if math.hypot(dx, dy) > rad: continue
        a = r.geom.area * k * KY
        if podm(r, a, dx, dy): out.append(r.id)
    return out


if '--vypis' in sys.argv:
    i = sys.argv.index('--vypis'); la, lo, rad = float(sys.argv[i + 1]), float(sys.argv[i + 2]), float(sys.argv[i + 3])
    for bid in vyber(la, lo, rad, lambda r, a, dx, dy: a > 40):
        r = B[B.id == bid].iloc[0]
        print(bid[:8], round(r.geom.area * kx(la) * KY), r['class'], r.height, r.num_floors, RU.get(bid), DMP.get(bid))
    sys.exit()

UP = json.load(open('assets/upresneni.json', encoding='utf-8')); UB = UP.setdefault('b', {})


def nastav(issue, ids, **kv):
    if kv.pop('skryt', False):                       # upstream klíč "skryt_budovy" (seznam id) místo naší "skryt" v "b"
        SK = UP.setdefault('skryt_budovy', [])
        for bid in ids:
            if bid not in SK: SK.append(bid)
            if not kv: UB.pop(bid, None)
        if not kv: return
    for bid in ids:
        UB[bid] = {**UB.get(bid, {}), **kv, 'hl': issue}


# ---------- názvy a druh budovy podle hlášení (neověřeno) ----------
BODOVE = [
    (7, 50.21149, 15.84052, dict(name='Klášter sester Notre Dame', cls_cz='klášter')),
    (9, 50.20893, 15.84430, dict(name='Loděnice VK Slavia HK', cls_cz='loděnice')),
    (10, 50.19982, 15.82741, dict(name='Kavárna (pavilon 56)', cls_cz='kavárna v nemocnici')),
    (11, 50.21816, 15.82068, dict(name='Sídlo ODS', cls_cz='kancelář politické strany')),
    (15, 50.19959, 15.85989, dict(name='Restaurace Hrázka, Grilbar Splávek', cls_cz='restaurace')),
    (16, 50.20997, 15.83290, dict(name='Hospoda Na hradě', cls_cz='hospoda')),
    (17, 50.20995, 15.83278, dict(name='Hospoda Na hradě', cls_cz='hospoda')),
    (18, 50.20985, 15.83150, dict(name='Batalion U Draků, Vinotéka In Vino', cls_cz='hospoda a vinotéka')),
    (19, 50.19626, 15.85576, dict(name='Kuželna Malšovice', cls_cz='kuželna')),
    (20, 50.20638, 15.85864, dict(name='TJ Sokol Malšovice', cls_cz='sokolovna')),
    (34, 50.20655, 15.83352, dict(name='Biskupské gymnázium (odborné učebny)', cls_cz='škola')),
    (38, 50.17561, 15.83767, dict(name='Stáje s jízdárnou', cls_cz='stáje')),
    (39, 50.18396, 15.83796, dict(name='Školy pro sluchově postižené a žáky s vadami řeči (VOŠ, SŠ, ZŠ, MŠ, SPC)', cls_cz='škola')),
    (41, 50.20951, 15.83500, dict(name='Galerie Na Parkány (obchod Limen, Kadeřnický pokojík)', cls_cz='dům s obchody')),
    # výška, třída, střecha
    (21, 50.18304, 15.82928, dict(cls='apartments', cls_cz='bytový dům', r='flat')),
    (22, 50.18434, 15.82705, dict(cls='apartments', cls_cz='bytový dům', r='flat', h=23.0, fl=8)),
    (26, 50.19581, 15.84061, dict(fl=13, h=37.5)),                                            # Kejzlarova 1677–1679, 13 pater (i #27; #35 uvádí 12)
    (36, 50.21167, 15.82901, dict(r='hipped', wc=[176, 98, 74], rc=[78, 128, 112])),          # Muzeum východních Čech: cihlová fasáda, patinovaná měděná střecha
    (40, 50.23249, 15.89246, dict(r='flat', rc=[96, 140, 70], cls_cz='rodinný dům se zelenou střechou')),
    (23, 50.21536, 15.82560, dict(skryt=True)), (24, 50.21519, 15.82520, dict(skryt=True)),   # zbořené domy, na místě se staví nový komplex
]
for issue, la, lo, kv in BODOVE:
    ids = nejblizsi(la, lo)
    if not ids: print('NENALEZENO', issue); continue
    nastav(issue, ids, **kv)
# #9: malé domky v areálu loděnice jsou sklady vodáckého náčiní
nastav(9, [i for i in nejblizsi(50.20893, 15.84430, 35, 8) if i not in nejblizsi(50.20893, 15.84430)
           and B[B.id == i].iloc[0].geom.area * kx(50.2) * KY < 60], name='Sklad vodáckého náčiní (VK Slavia HK)', cls_cz='sklad lodí')
# #12: Na Rozhraní 1511–1514 mají chybějící výtahové šachty
nastav(12, vyber(50.19939, 15.84272, 85, lambda r, a, dx, dy: r._2 in ('residential', 'apartments') and a > 300 and RU.get(r.id, [None, 0])[1] in (6, 7, 8)), sachta=True)
# #8 Orlická kotlina: nejvýš 4 patra, ve Švendově ulici 3 (RÚIAN v části domů uvádí 5)
orl = vyber(50.21239, 15.84445, 210, lambda r, a, dx, dy: r._2 in ('residential', 'apartments') and 140 < a < 700 and RU.get(r.id, [None, 0])[1] in (5, 6))
nastav(8, orl, fl=4)
sv = [i for i in vyber(50.21239, 15.84445, 210, lambda r, a, dx, dy: dy < -75 and r._2 in ('residential', 'apartments') and 140 < a < 700)]
nastav(8, sv, fl=3, h=11.0)
# #43/#44 Meruňková (panorama Mapy.com 2025): řadové dvoupodlažní domky s plochou střechou, fasáda pískově žlutá, přízemní garáže světle šedé; dům 817 a sousední novostavba stejně
nastav(43, vyber(50.22193, 15.80204, 90, lambda r, a, dx, dy: r._2 == 'house' and 50 < a < 95 and (r.height != r.height or r.height <= 4.2)), r='flat', wc=[236, 212, 150], rc=[92, 94, 100])
nastav(43, vyber(50.22193, 15.80204, 90, lambda r, a, dx, dy: r._2 == 'house' and 80 < a < 95 and r.height != r.height), fl=2)
nastav(43, vyber(50.22193, 15.80204, 40, lambda r, a, dx, dy: a > 200 and r._2 == 'residential'), r='flat', wc=[236, 212, 150], rc=[92, 94, 100], fl=2)

# #54/#55 Kyjevská 333 (duplicitní hlášení se stejnou fotkou): panelák po zateplení, broskvově oranžová fasáda s tmavšími pilíři, 4 podlaží, ploché střechy; stejné sousední domy
_kyj = vyber(50.22987, 15.84052, 75, lambda r, a, dx, dy: r._2 in ('residential', 'apartments') and 200 < a < 270)
nastav(54, _kyj, fl=4, r='flat', wc=[232, 190, 150], rc=[110, 110, 114])
for _i in _kyj: UB[_i]['hl'] = 55 if _i != _kyj[0] else 54
# (vstupní dveře a balkony generátor zatím neumí)

# ---------- #6 zahrádkářská kolonie u Labe (50.2248, 15.84494): zahrádky, kůlny a ovocné stromy ----------
import random
lat6, lon6 = 50.22477, 15.84482; k6 = kx(lat6)
# kolonie je dlouhý pás mezi kanálem a silnicí (ortofoto ČÚZK, 4 px/m, střed = bod hlášení); dvě části
CELL_A = [(335, 905), (375, 780), (430, 690), (465, 590), (520, 500), (585, 400), (660, 300), (715, 225), (745, 250), (690, 340), (630, 440), (575, 540), (520, 640), (450, 760), (385, 890)]
CELL_B = [(700, 150), (790, 110), (880, 160), (900, 250), (850, 290), (760, 270), (715, 215)]
pxll = lambda C: [(lat6 + (480 - y) / 4 / KY, lon6 + (x - 480) / 4 / k6) for x, y in C]
poly6, poly6b = pxll(CELL_A), pxll(CELL_B)
UP['plochy'] = [q for q in UP.get('plochy', []) if 'hl' not in q] + [{'k': 'garden', 'q': [list(c) for c in pl], 'hl': 6} for pl in (poly6, poly6b)]
UP['custom_bld'] = [q for q in UP.get('custom_bld', []) if not str(q.get('id', '')).startswith('hl6-')]
rnd = random.Random(6); pg6 = shapely.geometry.MultiPolygon([shapely.geometry.Polygon([(lo, la) for la, lo in pl]).buffer(0) for pl in (poly6, poly6b)]); minx, miny, maxx, maxy = pg6.bounds
BARVY = [(214, 200, 170), (180, 120, 80), (150, 160, 140), (200, 180, 120), (170, 170, 175)]
STR = [(120, 74, 56), (80, 90, 100), (150, 90, 60), (96, 110, 90)]
sheds, stromy6 = [], []
for _ in range(8000):
    if len(sheds) >= 45: break
    lo_, la_ = rnd.uniform(minx, maxx), rnd.uniform(miny, maxy)
    if not pg6.buffer(-0.00003).contains(Point(lo_, la_)): continue
    if any(abs(lo_ - s[0]) * k6 < 7 and abs(la_ - s[1]) * KY < 7 for s in sheds): continue
    w, d = rnd.uniform(2.6, 3.8), rnd.uniform(2.4, 3.4); a_ = math.radians(35 + rnd.uniform(-4, 4)); sheds.append((lo_, la_, w, d, a_))
for n, (lo_, la_, w, d, a_) in enumerate(sheds):
    cs = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
    pts = [[round(la_ + (math.sin(a_) * x + math.cos(a_) * y) / KY, 7), round(lo_ + (math.cos(a_) * x - math.sin(a_) * y) / k6, 7)] for x, y in cs]
    UP['custom_bld'].append({'id': f'hl6-{n}', 'poly': pts, 'h': round(2.3 + rnd.random() * 0.5, 1), 'cls': 'allotment_house', 'r': 'gabled', 'wc': list(BARVY[n % 5]), 'rc': list(STR[n % 4])})
for _ in range(3000):
    if len(stromy6) >= 40: break
    lo_, la_ = rnd.uniform(minx, maxx), rnd.uniform(miny, maxy)
    if pg6.buffer(-0.00003).contains(Point(lo_, la_)): stromy6.append([round(la_, 7), round(lo_, 7), round(3.0 + rnd.random() * 2.5, 1), 0])

# #5 Bezručova 555 (stromy před domem) zahozeno: nejsou podklady (foto), dřívější odhad stromů se odstraňuje z oblasti.json
OB = json.load(open('assets/oblasti.json', encoding='utf-8'))
OB = {k: v for k, v in OB.items() if k not in ('hl5_bezrucova', 'hl6_kolonie', 'hl6_kolonie_b')}
_pgA = shapely.geometry.Polygon([(lo, la) for la, lo in poly6]).buffer(0)
OB['hl6_kolonie'] = {'poly': [list(c) for c in poly6], 'trees': [t for t in stromy6 if _pgA.contains(Point(t[1], t[0]))], 'b': {}, 'b_auto': {}}
OB['hl6_kolonie_b'] = {'poly': [list(c) for c in poly6b], 'trees': [t for t in stromy6 if not _pgA.contains(Point(t[1], t[0]))], 'b': {}, 'b_auto': {}}
json.dump(OB, open('assets/oblasti.json', 'w', encoding='utf-8'), ensure_ascii=False)
# ---------- #13 jez (Malšovický jez na Orlici, OSM way 36887106) a #25 kašna před Muzeem východních Čech (OSM way 1243817661; geometrie stažená z OSM 2026-11-18) ----------
from shapely.geometry import LineString, Polygon as _Poly
JEZ = [(50.2115621, 15.8606645), (50.2114819, 15.860714), (50.2113628, 15.8607871), (50.2114076, 15.8610086), (50.2113972, 15.8610926), (50.2113782, 15.861138), (50.2113552, 15.8611932),
       (50.2112814, 15.8613603), (50.2111505, 15.8615527), (50.2110901, 15.8616388), (50.2110143, 15.8617242), (50.2108884, 15.8618038), (50.210544, 15.861867), (50.2104612, 15.8618813)]
KASNA = [(50.2116293, 15.8286432), (50.2116361, 15.8287274), (50.2115838, 15.8287378), (50.211577, 15.8286536)]
def _poly_m(pts, k, buf):
    lat0, lon0 = pts[0]
    xy = [((lo - lon0) * k, (la - lat0) * KY) for la, lo in pts]
    g = LineString(xy).buffer(buf, cap_style='flat') if buf and len(xy) > 2 and xy[0] != xy[-1] and buf < 0 else None
    return lat0, lon0, xy
def _ll(g, lat0, lon0, k): return [[round(lat0 + y / KY, 7), round(lon0 + x / k, 7)] for x, y in list(g.exterior.coords)[:-1]]
kj = kx(50.2110); la0, lo0, xy = _poly_m(JEZ, kj, 0)
jez = LineString(xy).buffer(2.2, cap_style='flat', join_style='round').simplify(0.3)
UP['custom_bld'] = [q for q in UP.get('custom_bld', []) if not str(q.get('id', '')).startswith(('hl13-', 'hl25-'))]
UP['custom_bld'].append({'id': 'hl13-0', 'poly': _ll(jez, la0, lo0, kj), 'h': 1.3, 'cls': 'service', 'r': 'flat', 'wc': [178, 178, 172], 'rc': [168, 168, 162], 'name': 'Malšovický jez'})
kk = kx(50.2116); la1, lo1, xy2 = _poly_m(KASNA, kk, 0)
kas = _Poly(xy2).buffer(0.9)
UP['plochy'] = [q for q in UP['plochy'] if q.get('hl') != 25] + [{'k': 'pool', 'q': _ll(kas, la1, lo1, kk), 'hl': 25}]
cx_, cy_ = _Poly(xy2).centroid.x, _Poly(xy2).centroid.y
sloup = _Poly([(cx_ - 0.55, cy_ - 0.55), (cx_ + 0.55, cy_ - 0.55), (cx_ + 0.55, cy_ + 0.55), (cx_ - 0.55, cy_ + 0.55)])
UP['custom_bld'].append({'id': 'hl25-0', 'poly': _ll(sloup, la1, lo1, kk), 'h': 2.6, 'cls': 'service', 'r': 'flat', 'wc': [206, 202, 188], 'rc': [196, 192, 180], 'name': 'Kašna před Muzeem východních Čech'})
# ---------- #45–#48 Brněnská (ortofoto ČÚZK 2026-11-19), #50 kanceláře, #53 Aupark ----------
def _pid(pref): return [i_ for i_ in B.id if i_.startswith(pref)]
nastav(45, _pid('b38f3d6b') + _pid('9cc9cee2'), name='Hotel AWAM (nová přístavba)', cls_cz='hotel')            # plochá bílá střecha v ortofotu u 50.19219, 15.84938
nastav(46, _pid('5b2e54ce'), fl=2, wc=[226, 208, 172])                                                          # sklad Brněnská 207: dvě patra, světlá fasáda (podle hlášení)
nastav(47, _pid('78534937'), fl=4, h=14.0, r='hipped', wc=[232, 214, 178], rc=[214, 172, 130])                  # čtvercový dům s valbovou střechou (ortofoto: světlá střecha)
nastav(48, _pid('fd98a918'), r='hipped', fl=3, rc=[62, 66, 76], name='Brněnská 300')                            # čtvercový dům, valbová střecha z tmavé břidlice (ortofoto)
nastav(50, _pid('f0603d32'), skryt=True)                                                                         # drobný objekt uvnitř zástavby, překrývá se s budovami (zdánlivé „dvě budovy v sobě“)
nastav(53, _pid('b55ae712'), h=22.0, fl=7, cls_cz='parkovací dům')                                              # 7 podlaží; laser měřil jen vrchní parkovací palubu (3,6 m)

json.dump(UP, open('assets/upresneni.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('upraveno budov:', sum(1 for v in UB.values() if 'hl' in v), '| Orlická kotlina', len(orl), '+ Švendova', len(sv))
