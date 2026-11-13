"""Nové stavby silnic, které pasport magistrátu ještě nemá: stáhne aktuální OSM (cesty a plochy silnic) do assets/prestavby.json.

python ../skripty/prestavby_osm.py          (z izomapa/, přepíše klíč "osm" u každé přestavby)

assets/prestavby.json: [{"nazev", "zona": [[lat, lon], ...], "pozn"}]. V zóně hook custom_prep.py nepoužije pasport komunikací,
značení, zeleně ani stání a vozovky, chodníky a přechody nakreslí podle OSM (pruhy, šířky, podchody vynechá).
Bere se přímo API OpenStreetMap (bbox zóny), ne Overpass – zóna je malá.
"""
import json, sys, time, urllib.request, xml.etree.ElementTree as ET

UA = {'User-Agent': 'izomapa-prestavby/1.0'}
F = 'assets/prestavby.json'
P = json.load(open(F, encoding='utf-8'))
KEEP = ('highway', 'lanes', 'lanes:forward', 'lanes:backward', 'oneway', 'width', 'tunnel', 'layer', 'bridge', 'covered',
        'area:highway', 'surface', 'footway', 'crossing', 'service', 'junction', 'name', 'description', 'turn:lanes',
        'cycleway', 'segregated', 'incline', 'ramp')


def get(url):
    for i in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
        except Exception as e:
            err = e; time.sleep(5 * (i + 1))
    raise err


for p in P:
    la = [q[0] for q in p['zona']]; lo = [q[1] for q in p['zona']]
    m = 0.0006
    bb = f'{min(lo) - m:.6f},{min(la) - m:.6f},{max(lo) + m:.6f},{max(la) + m:.6f}'
    r = ET.fromstring(get(f'https://api.openstreetmap.org/api/0.6/map?bbox={bb}'))
    N = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in r.iter('node')}
    NT = {n.get('id'): {t.get('k'): t.get('v') for t in n.iter('tag')} for n in r.iter('node')}
    ways, nodes = [], []
    for w in r.iter('way'):
        t = {x.get('k'): x.get('v') for x in w.iter('tag')}
        if 'highway' not in t and 'area:highway' not in t: continue
        q = [N[n.get('ref')] for n in w.iter('nd') if n.get('ref') in N]
        if len(q) < 2: continue
        ways.append({'id': int(w.get('id')), 't': {k: v for k, v in t.items() if k in KEEP}, 'q': [[round(a, 7), round(b, 7)] for a, b in q]})
    for i, t in NT.items():                      # přechody a semafory (pro zebry a stopčáry)
        if t.get('highway') in ('crossing', 'traffic_signals') or t.get('crossing'):
            nodes.append({'t': {k: v for k, v in t.items() if k in ('highway', 'crossing', 'crossing:markings')}, 'q': [round(N[i][0], 7), round(N[i][1], 7)]})
    p['osm'] = {'stazeno': time.strftime('%Y-%m-%d'), 'ways': ways, 'nodes': nodes}
    print(p['nazev'], 'cest', len(ways), 'uzlů', len(nodes))
json.dump(P, open(F, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
