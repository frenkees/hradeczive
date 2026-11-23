"""Okolí sídliště Na Plachtě (domysleno): chodníky, čárkovaná osa a přechody, lampy, lavičky, koše, zastávky, značky, auta na parkovištích.
Volá se z plachta_studie.py; vrací vlastnosti (props), auta, polygony značení a chodníků v metrech."""
import math
import numpy as np
import scipy.ndimage as ndi
import shapely.ops
from shapely.affinity import rotate
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union


def kostra(m):
    """ztenčení masky (Zhang–Suen) na jednopixelovou osu"""
    m = m.astype(np.uint8).copy()

    def krok(m, it):
        P = np.pad(m, 1)
        p2, p3, p4, p5, p6, p7, p8, p9 = P[:-2, 1:-1], P[:-2, 2:], P[1:-1, 2:], P[2:, 2:], P[2:, 1:-1], P[2:, :-2], P[1:-1, :-2], P[:-2, :-2]
        n = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
        seq = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
        A = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(int) for i in range(8))
        c = ((p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)) if it == 0 else ((p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0))
        return (m == 1) & (n >= 2) & (n <= 6) & (A == 1) & c
    while True:
        r0 = krok(m, 0); m[r0] = 0; r1 = krok(m, 1); m[r1] = 0
        if not r0.any() and not r1.any(): break
    return m.astype(bool)


def okoli(C):
    f, s, blue, silnice, st, track, voda, hriste, parkoviste = (C[k] for k in ('f', 's', 'blue', 'silnice', 'st', 'track', 'voda', 'hriste', 'parkoviste'))
    OVAL, NAT, rect, ll1, m_ = C['OVAL'], C['NATOCENI'], C['rect'], C['ll1'], C['m_']
    ox, oy = C['oval_xy']
    props = {k: [] for k in ('lamp', 'bench', 'bin', 'shelter', 'sg_p', 'sg_a', 'sg_i')}
    cars, znac, peseky = [], [], []
    zabrano = unary_union([unary_union([b['g'] for b in st]).buffer(2.0), track.buffer(3.0)] + [v.buffer(3.0) for v in voda])

    def pridej(kind, x, y, ang):
        if not zabrano.contains(Point(x, y)): props[kind].append([*ll1(x, y), round(float(ang), 3)])

    sk = kostra(blue)
    sy_, sx_ = np.nonzero(sk)
    skset = set(zip(sx_.tolist(), sy_.tolist()))
    nb = lambda x, y: [(x + i, y + j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i or j) and (x + i, y + j) in skset]
    pts_all = np.array(sorted(skset), float)

    def smer(x, y, r=5):
        pts = pts_all[(abs(pts_all[:, 0] - x) <= r) & (abs(pts_all[:, 1] - y) <= r)]
        if len(pts) < 3: return None
        d = np.linalg.svd(pts - pts.mean(0), full_matrices=False)[2][0]
        v = np.array(f((x + d[0], y + d[1]))) - np.array(f((x, y)))
        return v / np.hypot(*v)

    def vzorky(krok_m):
        krok = krok_m / s; out, vis = [], set()
        for start in sorted(skset):
            if start in vis: continue
            zas = [(start, 0.0)]
            while zas:
                (x, y), dd = zas.pop()
                if (x, y) in vis: continue
                vis.add((x, y))
                if dd >= krok: out.append((x, y)); dd = 0.0
                for q in nb(x, y):
                    if q not in vis: zas.append((q, dd + math.hypot(q[0] - x, q[1] - y)))
        return out

    # čárkovaná osa
    for (x, y) in vzorky(9.0):
        v = smer(x, y)
        if v is None: continue
        mx_, my_ = f((x, y))
        if zabrano.contains(Point(mx_, my_)): continue
        znac.append(rect(mx_, my_, 3.0, 0.16, math.degrees(math.atan2(v[1], v[0]))))
    # lampy střídavě po stranách
    for i, (x, y) in enumerate(vzorky(34.0)):
        v = smer(x, y)
        if v is None: continue
        mx_, my_ = f((x, y)); n = np.array([-v[1], v[0]]) * (1 if i % 2 else -1)
        pridej('lamp', mx_ + n[0] * 5.9, my_ + n[1] * 5.9, math.atan2(-n[1], -n[0]))
    # křižovatky: přechody, Dej přednost
    jun = np.zeros(sk.shape, bool)
    for (x, y) in skset:
        if len(nb(x, y)) >= 3: jun[y, x] = True
    lj, nj = ndi.label(ndi.binary_dilation(jun, iterations=3))
    nz = 0; zeb = []
    for k in range(1, nj + 1):
        ys_, xs_ = np.nonzero(lj == k); jx, jy = xs_.mean(), ys_.mean()
        ring = [(a, b) for (a, b) in skset if 8 <= math.hypot(a - jx, b - jy) <= 11]
        if not ring: continue
        ang = sorted(math.atan2(b - jy, a - jx) for (a, b) in ring)
        grp, cur = [], [ang[0]]
        for a_ in ang[1:]:
            if a_ - cur[-1] > 0.6: grp.append(cur); cur = [a_]
            else: cur.append(a_)
        grp.append(cur)
        if len(grp) > 1 and grp[0][0] + 2 * math.pi - grp[-1][-1] <= 0.6: grp[0] = grp.pop() + grp[0]
        if len(grp) < 3: continue                              # jen skutečné křižovatky (3 a víc ramen), ne šum kostry
        jm = f((jx, jy))
        if any(math.hypot(jm[0] - a_[0], jm[1] - a_[1]) < 35 for a_ in zeb): continue
        zeb.append(jm)
        for gr in grp[:4]:
            am = float(np.mean(gr))
            c1 = np.array(f((jx + math.cos(am) * 9.5, jy + math.sin(am) * 9.5))); c0 = np.array(f((jx, jy)))
            v = c1 - c0; v /= np.hypot(*v); angd = math.degrees(math.atan2(v[1], v[0])); nv = np.array([-v[1], v[0]])
            if not silnice.contains(Point(*c1)): continue
            for q in np.arange(-3.0, 3.01, 1.0):
                cx_, cy_ = c1 + nv * q
                znac.append(rect(cx_, cy_, 3.4, 0.5, angd))
            if nz % 2 == 0:
                p_ = c1 + v * 3.5 + nv * 5.8; pridej('sg_p', p_[0], p_[1], math.atan2(v[1], v[0]) + math.pi)
            nz += 1
    # hřiště: lavičky, koš, značka Děti, chodníček k silnici
    for h in hriste:
        c = Polygon([m_(la, lo) for la, lo in h['q']]).centroid
        pridej('bench', c.x - 5.5, c.y + 2.0, 0.3); pridej('bench', c.x + 6.0, c.y - 3.0, 3.4); pridej('bin', c.x + 6.5, c.y + 3.5, 0.0)
        pt = silnice.boundary.interpolate(silnice.boundary.project(c)); v = np.array([pt.x - c.x, pt.y - c.y]); dl = float(np.hypot(*v))
        if dl > 8:
            peseky.append(LineString([(c.x, c.y), (pt.x, pt.y)]).buffer(1.1, cap_style='flat'))
            u = v / dl; pridej('sg_a', pt.x - u[0] * 4.5 + u[1] * 4.0, pt.y - u[1] * 4.5 - u[0] * 4.0, math.atan2(u[1], u[0]))
    # ovál: lavičky, koše a obvodová stezka
    for i, a_ in enumerate(np.linspace(0, 2 * math.pi, 8, endpoint=False)):
        p_ = rotate(Point(ox + 1.18 * OVAL[2] * s * math.cos(a_), oy + 1.18 * OVAL[3] * s * math.sin(a_)), NAT, origin=(ox, oy))
        pridej('bench', p_.x, p_.y, a_ + math.radians(NAT) + math.pi / 2)
        if i % 2 == 0: pridej('bin', p_.x + 1.2, p_.y + 0.8, 0.0)
    ring = rotate(Polygon([(ox + 1.3 * OVAL[2] * s * math.cos(t_), oy + 1.3 * OVAL[3] * s * math.sin(t_)) for t_ in np.linspace(0, 2 * math.pi, 49)]), NAT, origin=(ox, oy)).exterior
    for k in range(0, 48, 3): peseky.append(LineString(list(ring.coords)[k:k + 4]).buffer(1.2))
    # rybník: lavičky a obchůzka
    for q in voda:
        for pg in (q.geoms if q.geom_type == 'MultiPolygon' else [q]):
            bd = pg.buffer(4.0).exterior
            for i, d_ in enumerate(np.arange(8.0, bd.length, 30.0)):
                pt = bd.interpolate(d_); pridej('bench', pt.x, pt.y, i * 1.3)
            for k in range(0, len(bd.coords) - 3, 3): peseky.append(LineString(list(bd.coords)[k:k + 4]).buffer(1.1))
    # parkoviště: auta, čáry stání, značka
    for i, (pk, angd) in enumerate(parkoviste):
        c = pk.centroid; a = math.radians(angd); ux, uy = math.cos(a + math.pi / 2), math.sin(a + math.pi / 2)
        for j, q in enumerate(np.arange(-10.5, 10.6, 2.6)):
            x, y = c.x + ux * q, c.y + uy * q
            znac.append(rect(x - ux * 1.3, y - uy * 1.3, 0.14, 5.2, angd + 90))
            if (i * 7 + j * 3) % 5 not in (0, 3): cars.append([*ll1(x, y), round(a + math.pi / 2 + (0.0 if (i + j) % 2 else math.pi), 3), (i * 3 + j) % 8])
        pridej('sg_i', c.x + ux * 12.8, c.y + uy * 12.8, a)
    # lampy kolem obytných bloků (přístupové chodníky), po ~38 m
    for b in st:
        if b['cls'] not in ('apartments', 'office', 'commercial', 'parking'): continue
        g = b['g'] if b['g'].geom_type == 'Polygon' else max(b['g'].geoms, key=lambda q: q.area)
        o = g.buffer(6.5).exterior
        for d in np.arange(5.0, o.length, 38.0):
            pt = o.interpolate(d); pridej('lamp', pt.x, pt.y, 0.0)
    # chodníky podél silnic
    chodniky = []
    for g in (silnice.geoms if silnice.geom_type == 'MultiPolygon' else [silnice]):
        g = g.buffer(1.5, join_style='mitre')
        for q in (g.geoms if g.geom_type == 'MultiPolygon' else [g]):
            for rl in [q.exterior] + list(q.interiors):
                for k in np.arange(0, rl.length, 12.0):
                    seg = shapely.ops.substring(rl, k, min(k + 12.5, rl.length))
                    if seg.length > 1: chodniky.append(seg.buffer(1.15, cap_style='flat'))
    chodniky += peseky
    # zastávky MHD
    vz = vzorky(40.0)
    for fr in (0.18, 0.62):
        if len(vz) > 3:
            x, y = vz[int(len(vz) * fr)]; v = smer(x, y)
            if v is not None:
                mx_, my_ = f((x, y)); n = np.array([-v[1], v[0]])
                props['shelter'].append([*ll1(mx_ + n[0] * 6.3, my_ + n[1] * 6.3), round(math.atan2(v[1], v[0]), 3)])
    return props, cars, znac, chodniky
