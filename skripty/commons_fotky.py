"""Stáhne volně licencované fotky dominant z Wikimedia Commons do izomapa/landmarks_ref/<dominanta>/.

python skripty/commons_fotky.py   (z izohradec/; zdroje a licence zapíše do ZDROJE.md v každé složce)
Bere jen soubory přímo v kategorii (ne interiéry z podkategorií), náhled 960 px (Commons povoluje jen standardní velikosti náhledů).
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

UA = {'User-Agent': 'izomapa-landmarks/1.0 (local research script)'}
API = 'https://commons.wikimedia.org/w/api.php?'
OUT = os.path.join(os.path.dirname(__file__), '..', 'izomapa', 'landmarks_ref')
DOM = {
    'bila_vez': ['Category:White Tower (Hradec Králové)', 'Category:Bílá věž (Hradec Králové)'],
    'katedrala_sv_ducha': ['Category:Cathedral of the Holy Spirit (Hradec Králové)'],
    'gocarovo_gymnazium': ['Category:Gymnázium Josefa Kajetána Tyla'],
    'ulrichovo_namesti': ['Category:Ulrichovo náměstí', 'Category:Steinsky palace', 'Category:Bývalé ředitelství státních drah'],
    'hucak': ['Category:Hučák hydroelectric power plant', 'Category:Jez Hučák'],
    'malsovicky_stadion': ['Category:Malšovická aréna', 'Category:Všesportovní stadion'],
}
MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 12


def api(**p):
    p.update(format='json')
    for i in range(4):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(API + urllib.parse.urlencode(p), headers=UA), timeout=60).read())
        except Exception as e:
            time.sleep(3 * (i + 1)); err = e
    raise err


def strip(h):
    return re.sub(r'<[^>]+>', '', h or '').strip()


for key, cats in DOM.items():
    d = os.path.join(OUT, key); os.makedirs(d, exist_ok=True)
    rows, n = [], 0
    for cat in cats:
        r = api(action='query', generator='categorymembers', gcmtitle=cat, gcmtype='file', gcmlimit=50,
                prop='imageinfo', iiprop='url|extmetadata|mime', iiurlwidth=960)
        pages = sorted((r.get('query') or {}).get('pages', {}).values(), key=lambda p: p['title'])
        for p in pages:
            if n >= MAX: break
            ii = p['imageinfo'][0]
            if ii.get('mime') not in ('image/jpeg', 'image/png'): continue
            if re.search(r'interi|inside|organ|varhan|oltář|altar|plaque|deska|map|plán', p['title'], re.I): continue
            m = ii.get('extmetadata', {})
            lic = strip(m.get('LicenseShortName', {}).get('value'))
            if not re.search(r'CC|Public domain|PD', lic, re.I): continue
            name = re.sub(r'[^\w.-]+', '_', p['title'][5:])[:90]
            f = os.path.join(d, name.rsplit('.', 1)[0] + '.jpg')
            if not os.path.exists(f):
                for i in range(6):                      # Commons při rychlém stahování vrací 429: počkat a zkusit znovu
                    try:
                        data = urllib.request.urlopen(urllib.request.Request(ii['thumburl'], headers=UA), timeout=120).read(); break
                    except urllib.error.HTTPError as e:
                        if e.code != 429 or i == 5: raise
                        time.sleep(15 * (i + 1))
                open(f, 'wb').write(data)
                time.sleep(5)
            rows.append(f'| {os.path.basename(f)} | {strip(m.get("Artist", {}).get("value"))[:60]} | {lic} | {ii["descriptionurl"]} |')
            n += 1
    with open(os.path.join(d, 'ZDROJE.md'), 'w', encoding='utf-8') as o:
        o.write(f'# {key}\n\nWikimedia Commons ({", ".join(cats)}). Použito jen jako předloha pro model.\n\n| soubor | autor | licence | zdroj |\n|---|---|---|---|\n' + '\n'.join(rows) + '\n')
    print(key, n, 'fotek', flush=True)
