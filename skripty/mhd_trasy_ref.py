"""Referenční trasy linek MHD pro mhd.py: relace linek z OSM a mapa linek MHD magistrátu -> assets/mhd_trasy_ref.json

python ../skripty/mhd_trasy_ref.py      (z izomapa/)

osm:   [{"ref", "name", "from", "to", "id", "ways": [[[lat, lon], ...], ...] (v pořadí jízdy), "stops": [[lat, lon], ...]}]
       PTv2 relace route=bus/trolleybus dopravce DPMHK (Overpass); každá relace = jeden směr jedné varianty linky.
zastavky: [[název, lat, lon], ...]  zastávky a stanoviště z OSM (highway=bus_stop, public_transport=stop_position/platform):
       jízdní řád CIS JŘ má jednu souřadnici na název, stejnojmenné zastávky bývají ale v několika ulicích – mhd.py vybere tu na trase.
mesto: {"číslo linky": [[[lat, lon], ...], ...]}  geoportal.mmhk.cz, ArcGIS thematic/mhd_linky (zjednodušená čára bez směru,
       body po ~60 m) – jen kontrola a rozhodčí mezi možnými cestami, ne tvar trasy.
mhd.py s tímhle souborem vede trasy přednostně po relaci z OSM (ve směru jízdy), pak podél městské čáry, jinak po silnicích;
kvalitu každého úseku mezi zastávkami zapíše do mhd.json (jistý / jen OSM / jen město / nejistý).
"""
import json, sys, time, urllib.parse, urllib.request

UA = {'User-Agent': 'izomapa-mhd/1.0'}
BB = '50.150,15.740,50.270,15.930'
Q = f'[out:json][timeout:120];rel({BB})["type"="route"]["route"~"^(bus|trolleybus)$"]["operator"~"Dopravní podnik města Hradce"];out geom;'
OVERPASS = ['https://overpass-api.de/api/interpreter', 'https://overpass.private.coffee/api/interpreter', 'https://overpass.kumi.systems/api/interpreter']
MESTO = ('https://geoportal.mmhk.cz/arcgis/rest/services/thematic/mhd_linky/MapServer/0/query?'
         'where=1%3D1&outFields=CISLO,DRUH&returnGeometry=true&outSR=4326&f=json')


def get(url, data=None):
    req = urllib.request.Request(url, data=data, headers=UA)
    return urllib.request.urlopen(req, timeout=180).read()


osm = None
for i in range(6):
    for u in OVERPASS:
        try:
            raw = get(u, urllib.parse.urlencode({'data': Q}).encode())
            if raw[:1] == b'{': osm = json.loads(raw); break
        except Exception as e:
            print('Overpass', u, e, file=sys.stderr)
    if osm: break
    time.sleep(20 * (i + 1))
if not osm: sys.exit('Overpass nedostupný')

rels = []
for r in osm['elements']:
    t = r.get('tags', {})
    ways, stops = [], []
    for m in r.get('members', []):
        if m['type'] == 'way' and m.get('role', '') in ('', 'forward', 'backward') and m.get('geometry'):
            ways.append([[round(p['lat'], 7), round(p['lon'], 7)] for p in m['geometry']])
        elif m['type'] == 'node' and m.get('role', '').startswith('stop') and 'lat' in m:
            stops.append([round(m['lat'], 7), round(m['lon'], 7)])
    # směr cest: navázat na předchozí (PTv2 má cesty v pořadí jízdy, ale každá může být kreslená opačně)
    for k in range(len(ways)):
        w = ways[k]
        if k == 0:
            if len(ways) > 1 and (w[0] == ways[1][0] or w[0] == ways[1][-1]): ways[0] = w[::-1]
            continue
        end = ways[k - 1][-1]
        if w[-1] == end and w[0] != end: ways[k] = w[::-1]
    rels.append({'id': r['id'], 'ref': t.get('ref', ''), 'name': t.get('name', ''), 'from': t.get('from', ''), 'to': t.get('to', ''),
                 'route': t.get('route'), 'ways': ways, 'stops': stops})
print('relací z OSM', len(rels), 'linky', sorted({r['ref'] for r in rels}, key=lambda x: (len(x), x)))

QZ = f'[out:json][timeout:120];(node({BB})["highway"="bus_stop"];node({BB})["public_transport"~"^(stop_position|platform)$"];);out;'
zast = None
for i in range(6):
    for u in OVERPASS:
        try:
            raw = get(u, urllib.parse.urlencode({'data': QZ}).encode())
            if raw[:1] == b'{': zast = json.loads(raw); break
        except Exception as e:
            print('Overpass', u, e, file=sys.stderr)
    if zast: break
    time.sleep(20 * (i + 1))
zastavky = sorted({(e['tags'].get('name', ''), round(e['lat'], 7), round(e['lon'], 7)) for e in (zast or {}).get('elements', []) if e.get('tags', {}).get('name')})
print('zastávek z OSM', len(zastavky))

m = json.loads(get(MESTO))
mesto = {}
for f in m.get('features', []):
    mesto.setdefault(str(f['attributes']['CISLO']), []).extend([[[round(lat, 7), round(lon, 7)] for lon, lat in p] for p in f['geometry']['paths']])
print('linek z mapy magistrátu', len(mesto), sorted(mesto, key=lambda x: (len(x), x)))
json.dump({'stazeno': time.strftime('%Y-%m-%d'), 'osm': rels, 'mesto': mesto, 'zastavky': [list(z) for z in zastavky]}, open('assets/mhd_trasy_ref.json', 'w', encoding='utf-8'),
          ensure_ascii=False, separators=(',', ':'))
