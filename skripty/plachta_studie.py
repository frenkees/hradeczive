"""Urbanistická studie „Na Plachtě“ (maketa, sídliště pro 19 000 obyvatel, konec 70.–80. let) -> hypotetická zástavba v mapě.

Podklady v kořeni repa: studie4.jpg = fotografie makety s ručně nakreslenými obrysy (ČERVENĚ domy, MODŘE silnice; pixely makety, levých 960 × 771)
a studie_colored.png = barevná verze téže makety (1400 × 1123, 1,458× větší): z ní se berou tvary domů (šedé střechy), rybníky a druhy ploch.
Obrysy se zakotví do mapy podle západního rybníka u silnice (podobnostní transformace) a zapíšou do izomapa/assets/plachta_studie.json. Dodělané detaily (domysleno): parkoviště u domů, parkovací domy kolem silnic,
pískoviště a dětské hřiště uprostřed každého bloku, uliční stromořadí, atletický ovál.

Spouštět z izomapa/:  PYTHONUTF8=1 .venv/Scripts/python ../skripty/plachta_studie.py [--nahled vystup.png]
"""
import json, math, os, subprocess, sys, time
import numpy as np
import scipy.ndimage as ndi
import shapely
import shapely.affinity
from PIL import Image, ImageDraw
from shapely.affinity import rotate
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

KOTVA = ((177.0, 451.7), (50.18750, 15.85276))    # střed západního rybníka u silnice (z barevné makety): pixel makety -> WGS84
# měřítko a natočení: z hloubky panelových domů (~14 m), šířky území mezi silnicí a okrajem lesa a směru silnice u rybníka
MERITKO, NATOCENI = 1.25, 9.0                      # m na pixel makety (velikost bloků ~420 obyvatel, šířka území mezi silnicí a lesem, ~19 tis. obyvatel); ° proti směru hodin
LAT0 = 50.187
KX, KY = math.cos(math.radians(LAT0)) * 111320.0, 110574.0
OVAL = (357, 433, 24, 33)                          # atletický ovál uprostřed makety: střed (px), poloosy (px)
SX, SY, DX, DY = 1.48, 1.4567, 6.0, -54.0          # barevná maketa = maketa * (SX, SY) + (DX, DY); barevný snímek je oříznutý o ~37 px výš (nalezeno korelací s červenými obrysy)
K = 1.4583
BAREVNA = '../studie_colored.png'
PODKLAD = '../studie4.jpg'


def m(lat, lon): return ((lon - 15.85) * KX, (lat - LAT0) * KY)


def transformace():
    (pa, ga) = KOTVA
    s, th = MERITKO, math.radians(NATOCENI)
    b1 = np.array(m(*ga)); a1 = np.array([pa[0], -pa[1]], float)
    R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    return lambda px: tuple(s * R @ (np.array([px[0], -px[1]], float) - a1) + b1)


def maska_na_polygon(mask):
    ys, xs = np.nonzero(mask)
    boxes = shapely.box(xs - 0.5, ys - 0.5, xs + 0.5, ys + 0.5)
    return unary_union(boxes)


def c2m(x, y):
    """pixel barevné makety -> pixel makety"""
    return ((x - DX) / SX, (y - DY) / SY)


def tvar_z_barevne(mask, kolem=0.0):
    """maska v pixelech barevné makety -> polygon v pixelech makety (zjednodušený)"""
    pg = maska_na_polygon(mask)
    pg = pg.buffer(kolem, join_style='mitre') if kolem else pg
    pg = shapely.affinity.affine_transform(pg.simplify(1.6), [1 / SX, 0, 0, 1 / SY, -DX / SX, -DY / SY])
    return pg


def nacti():
    """domy (šedé střechy z barevné makety v okolí červených obrysů), silnice (modré obrysy) a voda (barevná maketa); vše v pixelech makety"""
    col = np.asarray(Image.open(BAREVNA).convert('RGB')).astype(int)
    H, W = col.shape[:2]
    r, g, b = col[..., 0], col[..., 1], col[..., 2]; mx = col.max(2); sat = mx - col.min(2)
    a4 = np.asarray(Image.open(PODKLAD).convert('RGB')).astype(int)[:, :960]
    red = ndi.binary_closing((a4[..., 0] > 170) & (a4[..., 1] < 90) & (a4[..., 2] < 90), np.ones((3, 3)))
    blue = ndi.binary_closing((a4[..., 2] > 150) & (a4[..., 0] < 100) & (a4[..., 1] < 100), np.ones((3, 3)))
    yy, xx = np.mgrid[0:H, 0:W]; my = ((yy - DY) / SY).astype(int); mxx = ((xx - DX) / SX).astype(int)
    ok = (my >= 0) & (my < red.shape[0]) & (mxx >= 0) & (mxx < red.shape[1])
    red_c = np.zeros((H, W), bool); red_c[ok] = red[my[ok], mxx[ok]]
    gray = (sat < 26) & (mx > 55)
    cand = gray & ndi.binary_dilation(red_c, iterations=12)
    cand = ndi.binary_closing(ndi.binary_opening(cand, np.ones((7, 7))), np.ones((5, 5)))
    lab, n = ndi.label(cand)
    domy = []
    for k in range(1, n + 1):
        mk = lab == k
        if mk.sum() < 220: continue
        pg = tvar_z_barevne(mk)
        if pg.geom_type == 'MultiPolygon': pg = max(pg.geoms, key=lambda q: q.area)
        if pg.is_empty or pg.area < 15: continue
        domy.append((pg, None))
    yy2, xx2 = np.mgrid[0:blue.shape[0], 0:blue.shape[1]]                  # přes ovál a tenisové kurty žádná silnice nevede
    blue[((xx2 - OVAL[0]) / (OVAL[2] * 1.6)) ** 2 + ((yy2 - OVAL[1]) / (OVAL[3] * 1.5)) ** 2 < 1] = False
    kx0, ky0 = c2m(575, 622); kx1, ky1 = c2m(640, 646)
    blue[int(ky0) - 6:int(ky1) + 6, int(kx0) - 6:int(kx1) + 6] = False
    silnice = maska_na_polygon(blue).buffer(0.4).simplify(1.0)
    water = (g > r + 12) & (b > r + 10) & (mx < 130) & (abs(g - b) < 28)
    water = ndi.binary_opening(ndi.binary_closing(water, np.ones((9, 9))), np.ones((5, 5)))
    lw, nw = ndi.label(water)
    voda = [tvar_z_barevne(lw == k) for k in range(1, nw + 1) if (lw == k).sum() > 5000]
    return domy, silnice, voda, blue


def v_metrech(pg, f):
    if pg.geom_type == 'MultiPolygon': return unary_union([v_metrech(q, f) for q in pg.geoms])
    return Polygon([f(p) for p in pg.exterior.coords], [[f(p) for p in h.coords] for h in pg.interiors])


def main():
    f = transformace()
    domy_px, silnice_px, voda_px, blue = nacti()
    s = MERITKO
    st = []                                           # {'g': polygon v m, 'p': podlaží, 'cls': třída}
    for pg, zona_ in domy_px:
        c = pg.centroid; w, h = pg.bounds[2] - pg.bounds[0], pg.bounds[3] - pg.bounds[1]; area = pg.area * s * s
        if zona_ == 'jih': p, cls = 3, 'parking'                # jižní blok: parkovací domy a haly mezi parkovacími pruhy
        elif zona_ == 'vybaveni': p, cls = 3, 'commercial'
        elif c.y < 205 and 175 < c.x < 560: p, cls = 4, 'office'      # bílé pole nahoře: administrativa, obchody
        elif area < 600: p, cls = 3, 'commercial'               # drobné objekty (vybavenost, 2–3 podlaží)
        elif max(w, h) / max(1.0, min(w, h)) > 4 and area < 2400: p, cls = 5, 'apartments'   # dlouhý nižší dům
        else: p, cls = 8, 'apartments'                          # panelové bloky A22 a A14 mají podle řezu 8 a 7 podlaží
        st.append({'g': v_metrech(pg, f), 'p': p, 'cls': cls})
    voda = [v_metrech(q, f) for q in voda_px]
    silnice = v_metrech(silnice_px, f)
    budovy_all = unary_union([b['g'] for b in st])
    cx, cy = f(OVAL[:2])
    el = lambda k: rotate(Polygon([(cx + k * OVAL[2] * s * math.cos(t), cy + k * OVAL[3] * s * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40, endpoint=False)]), NATOCENI, origin=(cx, cy))
    track, pitch = el(1.0), el(0.62)

    plochy, hriste, extra, parkoviste = [], [], [], []
    ll = lambda g: [[round(y / KY + LAT0, 7), round(x / KX + 15.85, 7)] for x, y in list(g.exterior.coords)[:-1]]
    rect = lambda x, y, a, b, ang: rotate(Polygon([(x - a / 2, y - b / 2), (x + a / 2, y - b / 2), (x + a / 2, y + b / 2), (x - a / 2, y + b / 2)]), ang, origin=(x, y))
    zona = unary_union([budovy_all.buffer(40), silnice.buffer(14), track.buffer(30)]).convex_hull.buffer(0)
    plochy.append({'k': 'grass', 'q': ll(zona)})
    for g in (silnice.geoms if silnice.geom_type == 'MultiPolygon' else [silnice]):
        g = g.buffer(1.5, join_style='mitre')                       # silnice tvoří uzavřené okruhy: vozovka = vnější obrys, dvory mezi nimi zpět na trávník
        for q in (g.geoms if g.geom_type == 'MultiPolygon' else [g]):
            plochy.append({'k': 'road', 'q': ll(q)})
            for h in q.interiors: plochy.append({'k': 'grass', 'q': ll(Polygon(h))})
    for vq in voda:
        for q in (vq.geoms if vq.geom_type == 'MultiPolygon' else [vq]):
            plochy.append({'k': 'water', 'q': ll(q.buffer(0.5))})
    plochy += [{'k': 'track', 'q': ll(track)}, {'k': 'pitch', 'q': ll(pitch)}]
    cm = lambda x, y: f(c2m(x, y))                            # pixel barevné makety -> metry
    for (x0, y0, x1, y1) in ((575, 622, 640, 646),):          # tenisové kurty vedle oválu
        plochy.append({'k': 'court_blue', 'q': ll(Polygon([cm(x0, y0), cm(x1, y0), cm(x1, y1), cm(x0, y1)]))})
    # pískoviště a dětské hřiště do dvora bloku tvaru C (největší dutina konvexního obalu domu), parkoviště směrem k nejbližší silnici
    for b in st:
        g = b['g']; c = g.centroid
        if b['cls'] != 'apartments' or g.area < 650: continue
        mr = list(g.minimum_rotated_rectangle.exterior.coords)
        ang = math.degrees(math.atan2(mr[1][1] - mr[0][1], mr[1][0] - mr[0][0]))
        cav = g.convex_hull.difference(g.buffer(2.0))
        if cav.geom_type == 'MultiPolygon': cav = max(cav.geoms, key=lambda q: q.area)
        if cav.area > 250:
            rp = cav.representative_point()
            plochy.append({'k': 'sand', 'q': ll(rect(rp.x, rp.y, 5.0, 5.0, ang))})
            hriste.append({'k': 'detske', 'q': ll(rect(rp.x + 9, rp.y + 1, 15.0, 11.0, ang))})
            for dx, dy in ((-9, 6), (-9, -6), (3, 9)): extra.append(Point(rp.x + dx, rp.y + dy))
        pt = silnice.boundary.interpolate(silnice.boundary.project(c))
        v = np.array([pt.x - c.x, pt.y - c.y]); dl = float(np.hypot(*v))
        if dl > 1:
            u = v / dl; q0 = np.array([c.x, c.y]) + u * min(dl * 0.55, 45)
            pk = rect(q0[0], q0[1], 24.0, 6.0, math.degrees(math.atan2(u[1], u[0])) + 90)
            if not pk.intersects(budovy_all.buffer(1.5)) and not pk.intersects(silnice):
                plochy.append({'k': 'parking', 'q': ll(pk)}); parkoviste.append((pk, math.degrees(math.atan2(u[1], u[0])) + 90))
    # parkovací domy kolem silnic (domysleno): 3 podlaží, 5 volných míst rovnoměrně podél vozovky
    sb = silnice.boundary
    for fr in (0.08, 0.27, 0.45, 0.63, 0.82):
        bnd = max(sb.geoms, key=lambda q: q.length) if sb.geom_type == 'MultiLineString' else sb
        pt0 = bnd.interpolate(fr, normalized=True); x0, y0 = pt0.x, pt0.y
        for r_ in (22, 34, 48):
            ok = False
            for a_ in range(0, 360, 45):
                x, y = x0 + r_ * math.cos(math.radians(a_)), y0 + r_ * math.sin(math.radians(a_))
                pd = rect(x, y, 38.0, 20.0, NATOCENI + 5)
                if pd.intersects(budovy_all.buffer(3)) or pd.intersects(silnice.buffer(1)) or pd.intersects(track.buffer(4)) or not zona.contains(pd): continue
                st.append({'g': pd, 'p': 3, 'cls': 'parking'}); budovy_all = unary_union([budovy_all, pd]); ok = True; break
            if ok: break
    # uliční stromořadí kolem silnic po ~24 m, mimo domy, parkoviště a ovál
    zakaz = unary_union([unary_union([b['g'] for b in st]).buffer(4), track.buffer(5)])
    stromy, k = [], 0
    for g in (silnice.geoms if silnice.geom_type == 'MultiPolygon' else [silnice]):
        bd = g.buffer(7).boundary
        for o in (bd.geoms if bd.geom_type == 'MultiLineString' else [bd]):
            for d in np.arange(0, o.length, 24.0):
                pt = o.interpolate(d)
                if zakaz.contains(pt): continue
                k += 1; stromy.append([round(pt.y / KY + LAT0, 7), round(pt.x / KX + 15.85, 7), round(8 + (k * 37 % 50) / 10.0, 1), 0])
    for pt in extra:
        k += 1; stromy.append([round(pt.y / KY + LAT0, 7), round(pt.x / KX + 15.85, 7), round(6 + (k * 29 % 40) / 10.0, 1), 0])

    # okolí: chodníky, značení, lampy, lavičky, koše, zastávky, značky, auta (plachta_okoli.py)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import plachta_okoli
    ll1 = lambda x, y: (round(y / KY + LAT0, 7), round(x / KX + 15.85, 7))
    props, cars, znac, chodniky = plachta_okoli.okoli(dict(f=f, s=s, blue=blue, silnice=silnice, st=st, track=track, voda=voda, hriste=hriste, parkoviste=parkoviste,
                                                           OVAL=OVAL, NATOCENI=NATOCENI, rect=rect, ll1=ll1, m_=m, oval_xy=(cx, cy)))
    i_tr = next(i for i, p_ in enumerate(plochy) if p_['k'] == 'track')
    plochy[i_tr:i_tr] = [{'k': 'footway', 'q': ll(c_)} for c_ in chodniky if c_.geom_type == 'Polygon' and not c_.is_empty]
    plochy += [{'k': 'marking', 'q': ll(z_)} for z_ in znac if z_.geom_type == 'Polygon']
    print('okolí: chodníků', len(chodniky), 'čar značení', len(znac), '| ' + ', '.join(f'{k} {len(v)}' for k, v in props.items()), '| aut', len(cars))

    PAN = [(232, 226, 208), (213, 217, 222), (236, 236, 230), (222, 224, 222), (226, 199, 154), (238, 232, 218)]
    zast = []
    for i, b in enumerate(st):
        p, cls, g = b['p'], b['cls'], b['g']
        if g.geom_type == 'MultiPolygon': g = max(g.geoms, key=lambda q: q.area)
        h = p * 2.9 + (1.0 if cls != 'apartments' else 0)
        wc = {'apartments': PAN[i % len(PAN)], 'office': (214, 208, 196), 'commercial': (226, 214, 190), 'parking': (176, 178, 182)}[cls]
        rc = (150, 90, 60) if cls == 'commercial' else (122, 122, 122)
        zast.append({'id': f'plachta-{i}', 'poly': ll(g), 'h': round(h, 1), 'p': p, 'cls': cls, 'wc': list(wc), 'rc': list(rc), 'plocha': round(g.area)})
    byty = sum(z['plocha'] * z['p'] for z in zast if z['cls'] == 'apartments')
    print(f'měřítko {s} m/px, natočení {NATOCENI}°; domů {len(zast)} (obytných {sum(z["cls"] == "apartments" for z in zast)}, parkovacích {sum(z["cls"] == "parking" for z in zast)}), '
          f'zastavěno {sum(z["plocha"] for z in zast) / 1e4:.1f} ha, obytná podlažní plocha {byty:,} m² (~{byty / 28:,.0f} obyvatel při 28 m²/os.)')
    print(f'zóna {zona.area / 1e4:.1f} ha, parkovišť {sum(1 for p in plochy if p["k"] == "parking")}, hřišť {len(hriste)}, stromů {len(stromy)}')
    json.dump({'zdroj': 'Urbanistická studie na Plachtě (maketa), obrysy domů a silnic ručně zakreslil uživatel, detaily domyšleny',
               'budovy': zast, 'zona': ll(zona), 'plochy': plochy, 'hriste': hriste, 'stromy': stromy, 'props': props, 'auta': cars, 'm_na_px': s},
              open('assets/plachta_studie.json', 'w'), ensure_ascii=False)
    if '--nahled' in sys.argv: nahled(sys.argv[sys.argv.index('--nahled') + 1], zast, plochy)


def nahled(out, zast, plochy):
    from PIL import ImageDraw
    la0, la1, lo0, lo1 = 50.178, 50.1985, 15.838, 15.8665
    W = 1400; H = int(W * ((la1 - la0) * KY) / ((lo1 - lo0) * KX))
    f = 'build/orto_plachta_nahled.jpg'                      # ortofoto se stáhne jednou a uloží
    if not os.path.exists(f):
        for _ in range(4):
            r = subprocess.run(['curl', '-s', '-m', '120', '-o', f, 'https://ags.cuzk.gov.cz/arcgis1/services/ORTOFOTO/MapServer/WMSServer?SERVICE=WMS&VERSION=1.3.0'
                                f'&REQUEST=GetMap&LAYERS=0&STYLES=&CRS=EPSG:4326&BBOX={la0},{lo0},{la1},{lo1}&WIDTH={W}&HEIGHT={H}&FORMAT=image/jpeg'])
            if r.returncode == 0 and os.path.getsize(f) > 10000: break
            time.sleep(4)
    im = Image.open(f).convert('RGBA'); ov = Image.new('RGBA', im.size); d = ImageDraw.Draw(ov)
    px = lambda la, lo: ((lo - lo0) / (lo1 - lo0) * W, (la1 - la) / (la1 - la0) * H)
    col = {'road': (60, 90, 255, 150), 'parking': (255, 255, 0, 150), 'sand': (255, 220, 120, 200), 'track': (200, 80, 60, 150)}
    for p in plochy:
        if p['k'] in col: d.polygon([px(la, lo) for la, lo in p['q']], fill=col[p['k']])
    for z in zast:
        c = {'apartments': (255, 40, 40, 190), 'parking': (255, 255, 0, 190), 'office': (255, 140, 0, 190), 'commercial': (255, 140, 0, 190)}[z['cls']]
        d.polygon([px(la, lo) for la, lo in z['poly']], fill=c, outline=(255, 255, 255, 220))
    Image.alpha_composite(im, ov).convert('RGB').save(out, quality=88)


if __name__ == '__main__':
    main()
